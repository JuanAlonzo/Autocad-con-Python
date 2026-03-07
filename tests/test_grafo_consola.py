import sys
import os

# Agregamos la ruta raíz del proyecto para que Python encuentre 'utilities'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utilities.cad_manager import cad
from utilities.entities import extract_network_lines
from utilities.graph import NetworkGraph


def main():
    print("   PRUEBA DE FUEGO: MOTOR DE GRAFOS")

    if not cad.connect():
        print("ERROR: Debes abrir AutoCAD y cargar tu plano de prueba primero.")
        return

    # 1. Definición de la Topología (Diccionario de Capas)
    diccionario_capas = {
        "red_principal": "CAT_LINEA DE RED EXISTENTE",
        "red_secundaria": "CAT_LINEA DE RED PROYECTADA",
    }

    print(f"1. Escaneando plano en busca de capas: {list(diccionario_capas.values())}")
    segmentos = extract_network_lines(diccionario_capas)

    if not segmentos:
        print("No se encontró ningún cable en las capas indicadas.")
        return

    print(f"✅ Se encontraron {len(segmentos)} segmentos físicos de cable.\n")

    # 2. Construcción del Grafo
    print("2. Construyendo topología matemática...")
    # Tolerancia de 0.1m (10cm). Si el dibujante dejó un hueco menor a 10cm entre dos cables, el grafo los unirá.
    grafo = NetworkGraph(tolerance=0.1)

    for p1, p2 in segmentos:
        grafo.add_line(p1, p2)

    total_nodos = len(grafo.nodes)
    total_conexiones = sum(len(vecinos) for vecinos in grafo.adj.values()) // 2

    print("Grafo construido:")
    print(f"   - Nodos únicos (Postes/Intersecciones): {total_nodos}")
    print(f"   - Aristas conectadas: {total_conexiones}\n")

    # 3. Prueba de Búsqueda en Profundidad (DFS)
    if total_nodos > 0:
        print("3. Iniciando simulacro de recorrido (DFS)...")
        # Tomamos el primer nodo que encuentre el diccionario como "Punto de Inicio"
        nodo_inicial = list(grafo.nodes.values())[0]
        print(f"   -> Empezando recorrido desde el nodo: {nodo_inicial}")

        ruta_numeracion = grafo.dfs_traversal(nodo_inicial)

        print(
            f"✅ El algoritmo DFS logró recorrer {len(ruta_numeracion)} nodos interconectados en esta rama."
        )

        # Opcional: Imprimir los primeros 5 puntos por los que pasaría
        print("   -> Primeros 5 saltos calculados:")
        for i, pt in enumerate(ruta_numeracion[:5]):
            print(f"      Salto {i + 1}: {pt}")


if __name__ == "__main__":
    main()
