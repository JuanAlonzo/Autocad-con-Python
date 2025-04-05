from pyautocad import Autocad, APoint
import math

acad = Autocad()

welcome_message = f"""
Nombre del archivo: {acad.doc.Name}
{'*' * 80}
Bienvenido al programa de numeración de bloques en AutoCAD.
Este script permite numerar bloques en función de varias opciones de ordenamiento.
Puedes elegir entre ordenar por coordenadas, distancia desde un punto de referencia, 
o seguir un trayecto definido por líneas. Elige la opción que mejor se adapte a tus necesidades.
Asegurate de definir una "capa" para los bloques y otro para las líneas del trayecto.
Asegúrate de que los bloques estén en la capa correcta y que las líneas de trayecto estén definidas correctamente. Si no se encuentran líneas de trayecto, el script utilizará el método de "Ruta óptima" como alternativa.
Una vez completado, el script mostrará las coordenadas ordenadas de los bloques y los numerará en el dibujo.
"""

print(f"{welcome_message}\n")

# Obtiene la lista de todas las capas disponibles
layers_disponibles = [layer.Name for layer in acad.doc.Layers]


def validate_layer(layer_name):
    if not layer_name.strip():
        return False, "El nombre de la capa no puede estar vacío."
    if layer_name not in layers_disponibles:
        return False, f"La capa '{layer_name}' no existe en el documento actual."
    return True, ""


# Solicitar y validar la capa de postes
while True:
    layer_name_bloques = input(
        "Ingresa el nombre de la capa 'postes' a enumerar: ")
    is_valid, error_message = validate_layer(layer_name_bloques)

    if is_valid:
        break
    else:
        print(f"Error: {error_message}")
        print(f"Capas disponibles: {'\n'.join(layers_disponibles)}")

# Guardamos las capas adicionales solicitadas
capas_adicionales = []

# Solicitamos y validamos si desea agregar capas adicionales
while True:
    agregar_capa = input(
        "¿Deseas agregar otra capa adicional para buscar bloques? (si/no): ").lower()

    if agregar_capa in ["NO", "No", "no", "n"]:
        break
    elif agregar_capa in ["SI", "Si", "si", "s", "sí"]:
        capa_adicional = input("Ingresa el nombre de la capa adicional: ")
        is_valid, error_message = validate_layer(capa_adicional)

        if is_valid:
            if capa_adicional != layer_name_bloques and capa_adicional not in capas_adicionales:
                capas_adicionales.append(capa_adicional)
                print(f"Capa '{capa_adicional}' agregada correctamente.")
            else:
                print("Esta capa ya ha sido incluida.")
        else:
            print(f"Error: {error_message}")
            print(f"Capas disponibles: {'\n'.join(layers_disponibles)}")
    else:
        print("Por favor, responde 'si' o 'no'.")

while True:
    layer_name_lineas = input(
        "Ingresa el nombre de la capa con las líneas del trayecto: ")
    is_valid, error_message = validate_layer(layer_name_lineas)

    if is_valid:
        break
    else:
        print(f"Error: {error_message}")
        print(f"Capas disponibles: {'\n'.join(layers_disponibles)}")

print(f"""\n
Opciones de ordenamiento:
1. Por coordenada X (Horizontal)
2. Por coordenada Y (Vertical)
3. Por distancia desde un punto de referencia
4. Ruta óptima (vecino más cercano)
5. Seguir trayecto definido por líneas
6. Salir
""")

orden = input("\nEscoge el tipo de ordenamiento o salir del programa (1-6): ")

if orden == "6":
    print("Saliendo del programa...")
    exit()

# Recolectamos todos los bloques primero sin dibujar nada
bloques = []

for obj in acad.model:
    try:
        if (obj.Layer == layer_name_bloques or obj.Layer in capas_adicionales) and obj.ObjectName == "AcDbBlockReference":
            x, y = obj.InsertionPoint[:2]
            bloques.append((x, y))
    except Exception as e:
        print(f"Error al procesar el objeto: {e}")

if orden == "1":
    # Ordenar de izquierda a derecha (por X)
    bloques.sort(key=lambda coord: coord[0])
elif orden == "2":
    # Ordenar de abajo hacia arriba (por Y)
    bloques.sort(key=lambda coord: coord[1])
elif orden == "3":
    # Ordenar por distancia desde un punto de referencia
    print(
        "Ordenando por distancia desde un punto de referencia...")
    ref_x = float(input("Ingresa coordenada X de referencia: "))
    ref_y = float(input("Ingresa coordenada Y de referencia: "))

    # Función para calcular distancia
    def calcular_distancia(punto):
        return math.sqrt((punto[0] - ref_x)**2 + (punto[1] - ref_y)**2)

    bloques.sort(key=calcular_distancia)
elif orden == "4":
    # Ordenamiento por vecino más cercano (ruta óptima)
    if not bloques:
        print("No se encontraron bloques para ordenar")
    else:
        ruta = [bloques[0]]  # Empezamos con el primer punto
        bloques_restantes = bloques[1:]

        while bloques_restantes:
            ultimo = ruta[-1]
            # Encontrar el vecino más cercano
            distancias = [(math.sqrt((x - ultimo[0])**2 + (y - ultimo[1])**2), i)
                          for i, (x, y) in enumerate(bloques_restantes)]
            _, idx = min(distancias)
            ruta.append(bloques_restantes[idx])
            bloques_restantes.pop(idx)

        bloques = ruta

elif orden == "5":
    # Recopilamos las líneas que forman el trayecto
    lineas = []
    for obj in acad.model:
        try:
            if obj.Layer == layer_name_lineas and obj.ObjectName == "AcDbLine":
                # Obtenemos los puntos inicial y final de cada línea
                x1, y1, _ = obj.StartPoint
                x2, y2, _ = obj.EndPoint
                lineas.append(((x1, y1), (x2, y2)))
        except Exception as e:
            print(f"Error al procesar línea: {e}")

    if not lineas:
        print(f"No se encontraron líneas en la capa {layer_name_lineas}")
        print("Usando método de vecino más cercano como alternativa...")
        orden = "4"  # Fallback a vecino más cercano
    else:
        print(f"Se encontraron {len(lineas)} líneas que definen el trayecto")

        # Construimos la secuencia ordenada de puntos del trayecto
        puntos_trayecto = []
        lineas_restantes = lineas.copy()

        # Empezamos con la primera línea
        inicio, fin = lineas_restantes.pop(0)
        puntos_trayecto.append(inicio)
        puntos_trayecto.append(fin)
        ultimo_punto = fin

        # Procesamos líneas restantes para construir un trayecto continuo
        max_intentos = len(lineas) * 2  # Para evitar bucles infinitos
        intentos = 0

        while lineas_restantes and intentos < max_intentos:
            encontrada = False
            for i, (inicio, fin) in enumerate(lineas_restantes):
                # Comprobamos si esta línea conecta con el último punto (con tolerancia)
                tolerancia = 0.1
                if (math.dist(ultimo_punto, inicio) < tolerancia):
                    puntos_trayecto.append(fin)
                    ultimo_punto = fin
                    lineas_restantes.pop(i)
                    encontrada = True
                    break
                elif (math.dist(ultimo_punto, fin) < tolerancia):
                    puntos_trayecto.append(inicio)
                    ultimo_punto = inicio
                    lineas_restantes.pop(i)
                    encontrada = True
                    break

            if not encontrada:
                intentos += 1
                if intentos >= max_intentos:
                    print(
                        "Advertencia: No se pudo formar un trayecto continuo con todas las líneas")
                    break

        # Asignamos cada bloque al punto más cercano del trayecto
        bloques_ordenados = []
        for punto_trayecto in puntos_trayecto:
            if not bloques:  # Si ya no quedan bloques por asignar
                break

            # Encontrar el bloque más cercano a este punto del trayecto
            distancias = [(math.dist(punto_trayecto, bloque), i)
                          for i, bloque in enumerate(bloques)]
            dist_min, idx_min = min(distancias)

            # Si la distancia es razonable (menos de 20 unidades), asignar este bloque al trayecto
            if dist_min < 20:
                bloques_ordenados.append(bloques.pop(idx_min))

        # Agregar bloques restantes que no estén cerca del trayecto
        bloques_ordenados.extend(bloques)
        bloques = bloques_ordenados

# Ahora dibujamos numeración en los bloques ya ordenados
coordenadas = []
count = 1

for x, y in bloques:
    coordenadas.append((x, y))

    # Aplicando desplazamiento para el texto
    text_x = x - 3
    text_y = y - 2.5
    text_point = APoint(text_x, text_y)

    # Dibujar un círculo alrededor del bloque
    acad.model.AddCircle(APoint(x, y), 2)
    # circle.Color = 2  # Amarillo

    # Agregar texto con número incremental
    acad.model.AddText(str(count), text_point, 1.0)
    # texto.Color = 2  # Amarillo
    count += 1

# Dibujamos líneas conectando los puntos para visualizar el recorrido
# No dibujamos líneas adicionales si ya usamos trayecto existente
if len(coordenadas) > 1 and orden != "5":
    for i in range(len(coordenadas) - 1):
        x1, y1 = coordenadas[i]
        x2, y2 = coordenadas[i+1]
        linea = acad.model.AddLine(APoint(x1, y1), APoint(x2, y2))
        linea.Color = 1  # Rojo

# Se muestran las coordenadas ordenadas
if capas_adicionales:
    print(
        f"\nCoordenadas ordenadas de los bloques en las capas {layer_name_bloques} y {', '.join(capas_adicionales)}:")
else:
    print(
        f"\nCoordenadas ordenadas de los bloques en la capa {layer_name_bloques}:")
for i, (x, y) in enumerate(coordenadas, 1):
    print(f"{i}. X: {x:.2f}, Y: {y:.2f}")
print(f"\nTotal de bloques procesados: {len(coordenadas)}")
