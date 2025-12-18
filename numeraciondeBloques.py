"""
Script: Numeración de Bloques
Propósito: Ordenar bloques espacialmente (X, Y, Ruta, etc.) y dibujar numeración en AutoCAD.
"""
import math
from pyautocad import APoint
from utilities.acad_common import require_autocad
from utilities.acad_layers import get_all_layer_names
from utilities.acad_entities import extract_block_data
from utilities.acad_io import (
    get_selection_from_list,
    get_user_input,
    display_message,
    get_confirmation
)


def sort_by_distance(blocks):
    """Ordena bloques por distancia a un punto de referencia dado por el usuario."""
    try:
        display_message("Ingrese coordenadas del punto de referencia:", "info")
        ref_x = float(get_user_input("Coordenada X"))
        ref_y = float(get_user_input("Coordenada Y"))
    except ValueError:
        display_message("Coordenadas inválidas. Se usará (0,0).", "warning")
        ref_x, ref_y = 0.0, 0.0

    return sorted(blocks, key=lambda p: math.hypot(p[0] - ref_x, p[1] - ref_y))


def sort_by_nearest_neighbor(blocks):
    """Algoritmo de la Ruta Óptima (Vecino más cercano)."""
    if not blocks:
        return []

    route = [blocks[0]]
    remaining = blocks[1:]

    while remaining:
        last = route[-1]
        # Buscamos el más cercano al último punto añadido
        # min() con key calcula la distancia de todos contra 'last'
        next_block = min(remaining, key=lambda p: math.hypot(
            p[0] - last[0], p[1] - last[1]))
        route.append(next_block)
        remaining.remove(next_block)

    return route


def sort_by_path_lines(acad, blocks, layer_lines):
    """Ordena proyectando los bloques sobre un trayecto dibujado con líneas."""
    # 1. Obtener líneas del trayecto
    lines = []
    for obj in acad.iter_objects():
        if obj.Layer == layer_lines and obj.ObjectName == "AcDbLine":
            lines.append((obj.StartPoint[:2], obj.EndPoint[:2]))

    if not lines:
        display_message(
            f"No hay líneas en la capa '{layer_lines}'. Usando vecino cercano.", "warning")
        return sort_by_nearest_neighbor(blocks)

    display_message(f"Procesando trayecto con {len(lines)} líneas...", "info")

    # 2. Construir puntos ordenados del trayecto (lógica simplificada)
    # Nota: Para un script de producción, aquí idealmente unirías las líneas geométricamente.
    # Por simplicidad, usamos los puntos medios de las líneas como "hitos" del trayecto.
    path_points = []
    for start, end in lines:
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        path_points.append((mid_x, mid_y))

    # 3. Ordenar bloques según su cercanía secuencial a los hitos del trayecto
    ordered_blocks = []
    pool = blocks.copy()

    for milestone in path_points:
        # Encontrar bloques cercanos a este hito (radio 20u)
        close_ones = [b for b in pool if math.hypot(
            b[0]-milestone[0], b[1]-milestone[1]) < 20]
        # Ordenarlos por distancia al hito
        close_ones.sort(key=lambda b: math.hypot(
            b[0]-milestone[0], b[1]-milestone[1]))

        ordered_blocks.extend(close_ones)
        for b in close_ones:
            pool.remove(b)

    # Añadir los sobrantes al final
    ordered_blocks.extend(pool)
    return ordered_blocks

# LOGICA DE DIBUJO


def draw_numbering(acad, sorted_blocks):
    """Dibuja círculos y números en AutoCAD."""
    display_message(
        f"Dibujando numeración en {len(sorted_blocks)} bloques...", "info")

    for i, (x, y) in enumerate(sorted_blocks, 1):
        # Insertar Círculo
        center = APoint(x, y)
        acad.model.AddCircle(center, 2.0)

        # Insertar Texto (desplazado ligeramente)
        text_pos = APoint(x - 3, y - 2.5)
        acad.model.AddText(str(i), text_pos, 1.0)

    display_message("Numeración completada exitosamente.", "success")


def draw_route_lines(acad, sorted_blocks):
    """Dibuja líneas conectando la secuencia (Visualizar ruta)."""
    if len(sorted_blocks) < 2:
        return

    for i in range(len(sorted_blocks) - 1):
        p1 = APoint(*sorted_blocks[i])
        p2 = APoint(*sorted_blocks[i+1])
        line = acad.model.AddLine(p1, p2)
        line.Color = 1  # Rojo


def main():
    acad = require_autocad("Numeracion Automatica de Bloques")

    # Selección de Capas
    all_layers = get_all_layer_names(acad)
    layer_bloques = get_selection_from_list(
        "Seleccione la capa de bloques (Postes):", all_layers)
    if not layer_bloques:
        return

    # Capas Adicionales
    extra_layers = []
    if get_confirmation("¿Hay bloques en otras capas adicionales?"):
        while True:
            layer = get_selection_from_list(
                "Añadir capa extra (o salir):", all_layers + ["(Terminar)"])
            if not layer or layer == "(Terminar)":
                break
            extra_layers.append(layer)

    # Extracción de Datos
    raw_data = extract_block_data(acad, layer_bloques)
    for layer in extra_layers:
        raw_data.extend(extract_block_data(acad, layer))

    if not raw_data:
        return

    blocks = [(d['X'], d['Y']) for d in raw_data]

    # Menú de Ordenamiento
    menu_opts = [
        "Horizontal (X)",
        "Vertical (Y)",
        "Distancia a Punto Ref.",
        "Ruta Óptima (Vecino más cercano)",
        "Seguir Trayecto (Capa Líneas)"
    ]
    metodo = get_selection_from_list("Método de Ordenamiento", menu_opts)
    if not metodo:
        return

    # Procesamiento
    if "Horizontal" in metodo:
        blocks.sort(key=lambda p: p[0])
    elif "Vertical" in metodo:
        blocks.sort(key=lambda p: p[1])
    elif "Distancia" in metodo:
        blocks = sort_by_distance(blocks)
    elif "Ruta Óptima" in metodo:
        blocks = sort_by_nearest_neighbor(blocks)
    elif "Trayecto" in metodo:
        layer_lines = get_selection_from_list(
            "Seleccione capa del trayecto (Líneas)", all_layers)
        if layer_lines:
            blocks = sort_by_path_lines(acad, blocks, layer_lines)
        else:
            return

    # Dibujo
    draw_numbering(acad, blocks)

    if get_confirmation("¿Dibujar líneas conectando la ruta?"):
        draw_route_lines(acad, blocks)


if __name__ == "__main__":
    main()
