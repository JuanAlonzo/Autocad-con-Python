from pyautocad import APoint
from utilities.acad_common import (
    initialized_autocad,
    display_message,
    get_available_layers
)
import math


def validate_and_select_layer(prompt, layers_disponibles):
    """Prompt user to select a valid layer."""
    while True:
        layer_name = input(prompt)
        if not layer_name.strip():
            print("Error: El nombre de la capa no puede estar vacío.")
        elif layer_name not in layers_disponibles:
            print(
                f"Error: La capa '{layer_name}' no existe en el documento actual.")
            print(f"Capas disponibles: {'\n'.join(layers_disponibles)}")
        else:
            return layer_name


def get_additional_layers(layers_disponibles, primary_layer):
    """Prompt user to add additional layers for block collection."""
    capas_adicionales = []

    while True:
        agregar_capa = input(
            "¿Deseas agregar otra capa adicional para buscar bloques? (si/no): ").lower()

        if agregar_capa in ["no", "n"]:
            break
        elif agregar_capa in ["si", "s", "sí"]:
            capa_adicional = input("Ingresa el nombre de la capa adicional: ")

            if not capa_adicional.strip():
                print("Error: El nombre de la capa no puede estar vacío.")
            elif capa_adicional not in layers_disponibles:
                print(
                    f"Error: La capa '{capa_adicional}' no existe en el documento actual.")
                print(f"Capas disponibles: {', '.join(layers_disponibles)}")
            elif capa_adicional == primary_layer or capa_adicional in capas_adicionales:
                print("Esta capa ya ha sido incluida.")
            else:
                capas_adicionales.append(capa_adicional)
                print(f"Capa '{capa_adicional}' agregada correctamente.")
        else:
            print("Por favor, responde 'si' o 'no'.")

    return capas_adicionales


def collect_blocks(acad, layer_name, additional_layers=None):
    """Collect all blocks from the specified layers."""
    blocks = []
    layers_to_check = [layer_name]

    if additional_layers:
        layers_to_check.extend(additional_layers)

    for obj in acad.model:
        try:
            if obj.Layer in layers_to_check and obj.ObjectName == "AcDbBlockReference":
                x, y = obj.InsertionPoint[:2]
                blocks.append((x, y))
        except Exception as e:
            print(f"Error al procesar el objeto: {e}")
    return blocks


def sort_by_x(blocks):
    """Sort blocks by X coordinate."""
    return sorted(blocks, key=lambda coord: coord[0])


def sort_by_y(blocks):
    """Sort blocks by Y coordinate."""
    return sorted(blocks, key=lambda coord: coord[1])


def sort_by_distance(blocks):
    """Sort blocks by distance from a reference point."""
    print("Ordenando por distancia desde un punto de referencia...")
    ref_x = float(input("Ingresa coordenada X de referencia: "))
    ref_y = float(input("Ingresa coordenada Y de referencia: "))

    def calculate_distance(point):
        return math.sqrt((point[0] - ref_x)**2 + (point[1] - ref_y)**2)

    return sorted(blocks, key=calculate_distance)


def sort_by_nearest_neighbor(blocks):
    """Sort blocks using nearest neighbor algorithm (optimal route)."""
    if not blocks:
        print("No se encontraron bloques para ordenar")
        return []

    route = [blocks[0]]
    remaining_blocks = blocks[1:]

    while remaining_blocks:
        last_point = route[-1]
        distances = [(math.dist(last_point, point), i)
                     for i, point in enumerate(remaining_blocks)]
        _, idx = min(distances)
        route.append(remaining_blocks[idx])
        remaining_blocks.pop(idx)

    return route


def collect_path_lines(acad, layer_name):
    """Collect all lines that form the path."""
    lines = []
    for obj in acad.model:
        try:
            if obj.Layer == layer_name and obj.ObjectName == "AcDbLine":
                x1, y1, _ = obj.StartPoint
                x2, y2, _ = obj.EndPoint
                lines.append(((x1, y1), (x2, y2)))
        except Exception as e:
            print(f"Error al procesar línea: {e}")
    return lines


def build_path_from_lines(lines):
    """Build a continuous path from a set of lines."""
    if not lines:
        return []

    path_points = []
    remaining_lines = lines.copy()

    # Start with first line
    start, end = remaining_lines.pop(0)
    path_points.append(start)
    path_points.append(end)
    last_point = end

    max_attempts = len(lines) * 2
    attempts = 0

    while remaining_lines and attempts < max_attempts:
        found = False
        tolerance = 0.1

        for i, (start, end) in enumerate(remaining_lines):
            if math.dist(last_point, start) < tolerance:
                path_points.append(end)
                last_point = end
                remaining_lines.pop(i)
                found = True
                break
            elif math.dist(last_point, end) < tolerance:
                path_points.append(start)
                last_point = start
                remaining_lines.pop(i)
                found = True
                break

        if not found:
            attempts += 1
            if attempts >= max_attempts:
                print(
                    "Advertencia: No se pudo formar un trayecto continuo con todas las líneas")
                break

    return path_points


def sort_blocks_by_path(blocks, path_points):
    """Sort blocks by proximity to path points."""
    sorted_blocks = []
    blocks_to_sort = blocks.copy()

    for path_point in path_points:
        if not blocks_to_sort:
            break

        distances = [(math.dist(path_point, block), i)
                     for i, block in enumerate(blocks_to_sort)]
        min_dist, min_idx = min(distances)

        if min_dist < 20:
            sorted_blocks.append(blocks_to_sort.pop(min_idx))

    # Add any remaining blocks that weren't close to the path
    sorted_blocks.extend(blocks_to_sort)
    return sorted_blocks


def draw_numbering(acad, blocks):
    """Draw numbering on blocks and connecting lines."""
    coordinates = []
    count = 1

    for x, y in blocks:
        coordinates.append((x, y))

        # Text position with offset
        text_x = x - 3
        text_y = y - 2.5
        text_point = APoint(text_x, text_y)

        # Draw circle around block
        acad.model.AddCircle(APoint(x, y), 2)

        # Add incremental number
        acad.model.AddText(str(count), text_point, 1.0)
        count += 1

    return coordinates


def draw_connecting_lines(acad, coordinates, is_path_ordering=False):
    """Draw lines connecting the points to visualize the path."""
    if len(coordinates) <= 1 or is_path_ordering:
        return

    for i in range(len(coordinates) - 1):
        x1, y1 = coordinates[i]
        x2, y2 = coordinates[i+1]
        line = acad.model.AddLine(APoint(x1, y1), APoint(x2, y2))
        line.Color = 1  # Red


def print_results(coordinates, primary_layer, additional_layers=None):
    """Print the ordered coordinates of the blocks."""
    if additional_layers:
        print(
            f"\nCoordenadas ordenadas de los bloques en las capas {primary_layer} y {', '.join(additional_layers)}:")
    else:
        print(
            f"\nCoordenadas ordenadas de los bloques en la capa {primary_layer}:")
    print("-" * 50)
    for i, (x, y) in enumerate(coordinates, 1):
        print(f"{i}. X: {x:.4f}, Y: {y:.4f}")
    print("-" * 50)
    print(f"\nTotal de bloques procesados: {len(coordinates)}")


def main():
    acad = initialized_autocad("""
Bienvenido al programa de numeración de bloques en AutoCAD.
Este script permite numerar bloques en función de varias opciones de ordenamiento.
Puedes elegir entre ordenar por coordenadas, distancia desde un punto de referencia, 
o seguir un trayecto definido por líneas. 
Elige la opción que mejor se adapte a tusnecesidades.
Asegurate de definir una 'capa' para los bloques y otro para las líneas del trayecto.
Asegúrate de que los bloques estén en la capa correcta y que las líneas de trayecto esténdefinidas correctamente. Si no se encuentran líneas de trayecto, el script utilizará elmétodo de 'Ruta óptima' como alternativa.
Una vez completado, el script mostrará las coordenadas ordenadas de los bloques y losnumerará en el dibujo.
        """)
    if not acad:
        display_message(
            "\nNo se puede continuar sin una conexión a AutoCAD.", style='error')
        display_message("Presione Enter para salir...",
                        style='input', use_rich=True)
        return
    layers_disponibles = get_available_layers(acad)

    # Get layer names
    layer_name_bloques = validate_and_select_layer(
        "Ingresa el nombre de la capa 'postes' a enumerar: ",
        layers_disponibles
    )

    # Get additional layers
    capas_adicionales = get_additional_layers(
        layers_disponibles, layer_name_bloques)

    layer_name_lineas = validate_and_select_layer(
        "Ingresa el nombre de la capa con las líneas del trayecto: ",
        layers_disponibles
    )

    print(f"""\n
    Opciones de ordenamiento:
    1. Por coordenada X (Horizontal)
    2. Por coordenada Y (Vertical)
    3. Por distancia desde un punto de referencia
    4. Ruta óptima (vecino más cercano)
    5. Seguir trayecto definido por líneas
    6. Salir
    """)

    orden = input(
        "\nEscoge el tipo de ordenamiento o salir del programa (1-6): ")

    if orden == "6":
        print("Saliendo del programa...")
        return

    # Collect all blocks first
    bloques = collect_blocks(acad, layer_name_bloques, capas_adicionales)

    # Apply selected sorting method
    is_path_ordering = False

    if orden == "1":
        bloques = sort_by_x(bloques)
    elif orden == "2":
        bloques = sort_by_y(bloques)
    elif orden == "3":
        bloques = sort_by_distance(bloques)
    elif orden == "4":
        bloques = sort_by_nearest_neighbor(bloques)
    elif orden == "5":
        lineas = collect_path_lines(acad, layer_name_lineas)

        if not lineas:
            print(f"No se encontraron líneas en la capa {layer_name_lineas}")
            print("Usando método de vecino más cercano como alternativa...")
            bloques = sort_by_nearest_neighbor(bloques)
        else:
            print(
                f"Se encontraron {len(lineas)} líneas que definen el trayecto")
            puntos_trayecto = build_path_from_lines(lineas)
            bloques = sort_blocks_by_path(bloques, puntos_trayecto)
            is_path_ordering = True
    else:
        print("Opción no válida. Saliendo del programa...")
        return

    # Draw numbering and visualize results
    coordenadas = draw_numbering(acad, bloques)
    draw_connecting_lines(acad, coordenadas, is_path_ordering)
    print_results(coordenadas, layer_name_bloques, capas_adicionales)


if __name__ == "__main__":
    main()
