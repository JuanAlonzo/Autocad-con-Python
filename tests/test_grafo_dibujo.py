import sys
import os

# Ajuste de ruta para importar módulos del proyecto principal
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utilities.cad_manager import cad
from utilities.entities import extract_network_lines, extract_blocks
from utilities.graph import NetworkGraph
from utilities.drawing import insert_block_with_attributes
from utilities.config import SETTINGS
from utilities.geometry import calculate_distance
from utilities.layers import ensure_layer


def main():
    print("========================================")
    print("   TEST VISUAL: NUMERACIÓN CON GRAFO")
    print("========================================\n")

    if not cad.connect():
        print("❌ ERROR: Debes abrir AutoCAD y cargar tu plano de prueba primero.")
        return

    # 1. Definición del Diccionario de Capas
    diccionario_red = {
        "red_existente": "CAT_LINEA DE RED EXISTENTE",
        # "red_proyectada": "CAT_LINEA DE RED PROYECTADA",
    }

    # 2. Definición del Diccionario de Postes
    diccionario_postes = {
        "POSTE_C_9": "Postes de Concreto de 9m",
        # "POSTE_C_8": "Postes de Concreto de 8m",
        # "POSTE_C_11.5": "Postes de Concreto de 11.5m",
        "POSTE_W_8": "Poste de madera de 8m",
    }

    print(f"📡 1. Extrayendo red de las capas: {list(diccionario_red.values())}")
    segmentos = extract_network_lines(diccionario_red)

    if not segmentos:
        print("⚠️ No se encontraron cables. Revisa los nombres de las capas.")
        return

    print("\n 2.  Extrayendo postes fisicos del dibujo...")
    todos_los_bloques = extract_blocks()

    # Filtramos la lista para quedarnos SOLO con los que coinciden con el diccionario
    postes_validos = [
        b for b in todos_los_bloques if b["Nombre"].upper() in diccionario_postes
    ]
    print(f"✅ Se encontraron {len(postes_validos)} postes válidos para numerar.")

    # 2. Construcción de la Topología
    print("🧠 3. Construyendo el grafo matemático (Tolerancia: 0.1m)...")
    grafo = NetworkGraph(tolerance=0.1)
    for p1, p2 in segmentos:
        grafo.add_line(p1, p2)

    # 3. Interacción con AutoCAD (Selección de Punto)
    print("\n🖱️ 4. Ve a AutoCAD y haz CLIC en el punto de inicio de la red...")
    try:
        cad.app.Visible = True
        # Esto pausa la consola y te pide un clic en el ModelSpace
        punto_com = cad.doc.Utility.GetPoint(
            Prompt="\nSeleccione el poste/punto de inicio para la numeración: "
        )
        punto_clic = (round(punto_com[0], 4), round(punto_com[1], 4))
        print(f"✅ Clic capturado en coordenadas: {punto_clic}")
    except Exception as e:
        print(f"❌ Fallo al capturar el clic. Detalle técnico: {e}")
        print(
            "💡 CONSEJO: Ve a AutoCAD, presiona ESC dos veces y vuelve a correr el script."
        )
        return

    # 5. Ajuste del Clic a la Red (Snap)
    # Como es imposible hacer clic en el milímetro exacto de la línea, buscamos el nodo más cercano
    nodo_raiz, dist = grafo.find_nearest_node(punto_clic, max_radius=5.0)

    if not nodo_raiz:
        print(
            "❌ El clic está a más de 5 metros de cualquier cable de la red. Intenta de nuevo."
        )
        return

    print(f"✅ Nodo de red enganchado con éxito (Distancia del clic: {dist:.2f}m)")

    # 5. Ejecutar Búsqueda en Profundidad (DFS)
    print("\n🚀 6. Ejecutando Algoritmo DFS...")
    ruta_numeracion = grafo.dfs_traversal(nodo_raiz)
    print(f"✅ Se trazó un recorrido lógico por {len(ruta_numeracion)} nodos.")

    # 6. Dibujo en AutoCAD
    print("✏️ 6. Dibujando la numeración en AutoCAD...")
    capa_destino = "TEST_NUMERACION_DFS"
    ensure_layer(capa_destino, color=3)  # Color Verde

    exitos = 0
    numero_actual = 1
    radio_busqueda = 1.0  # Tolerancia para encontrar el bloque cerca del nodo

    # Recorremos el camino trazado por el Grafo
    for pt_grafo in ruta_numeracion:
        poste_encontrado = None

        # Cruzamos el punto del cable con nuestra lista de postes filtrados
        for poste in postes_validos:
            dist = calculate_distance(pt_grafo, (poste["X"], poste["Y"]))
            if dist <= radio_busqueda:
                poste_encontrado = poste
                break  # Encontramos el poste, no necesitamos seguir buscando en este nodo

        # Si hay un poste real en esta coordenada, lo numeramos
        if poste_encontrado:
            insercion_ok = insert_block_with_attributes(
                x=poste_encontrado["X"] + SETTINGS.TEXT_OFFSET_X,
                y=poste_encontrado["Y"] + SETTINGS.TEXT_OFFSET_Y,
                block_name=SETTINGS.BLOQUE_A_INSERTAR,
                layer=capa_destino,
                scale=SETTINGS.ESCALA_BLOQUE,
                attributes={SETTINGS.ATRIBUTO_ETIQUETA: str(numero_actual)},
            )
            if insercion_ok:
                exitos += 1
                numero_actual += 1  # Solo aumenta si realmente numeramos un poste

            # Lo quitamos de la lista para no numerarlo dos veces si el grafo pasa cerca de nuevo
            postes_validos.remove(poste_encontrado)

    print(f"\n🎉 ¡TEST COMPLETADO! Se dibujaron {exitos} bloques de numeración.")
    print("👉 Abre AutoCAD y mira cómo el algoritmo decidió viajar por tu red.")


if __name__ == "__main__":
    main()
