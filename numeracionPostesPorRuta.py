"""
Script: Numeración de Postes por Ruta (Polilínea)
Propósito: 
1. Buscar bloques en capas 'POSTE*'.
2. Ordenarlos siguiendo una Polilínea guía.
3. Numerar en una capa nueva.
4. Exportar reporte.
"""
import math
from pyautocad import APoint
from utilities.acad_common import require_autocad
from utilities.acad_layers import get_all_layer_names
from utilities.acad_entities import extract_block_data
from utilities.acad_export import show_export_menu
from utilities.acad_io import (
    get_selection_from_list,
    display_message,
    get_confirmation
)


def get_polyline_points(acad, layer_ruta):
    """
    Busca una Polilínea en la capa especificada y extrae sus vértices en orden.
    Soporta LWPolyline (AcDbPolyline), que es la más común.
    """
    path_points = []
    found = False

    display_message(f"Buscando polilínea en capa '{layer_ruta}'...", "info")

    for obj in acad.iter_objects():
        if obj.Layer == layer_ruta and obj.ObjectName == "AcDbPolyline":
            # Coordinates devuelve una tupla plana
            coords = obj.Coordinates
            # Agrupamos en pares (X, Y)
            for i in range(0, len(coords), 2):
                path_points.append((coords[i], coords[i+1]))
            found = True
            break

    if not found:
        display_message(
            f"No se encontró ninguna Polilínea (AcDbPolyline) en {layer_ruta}.", "error")
        return []

    display_message(
        f"Ruta detectada con {len(path_points)} vértices.", "success")
    return path_points


def sort_blocks_by_path(blocks_dicts, path_points):
    """
    Ordena la lista de diccionarios de bloques basándose en los puntos de la ruta.
    """
    ordered_blocks = []
    pool = blocks_dicts.copy()

    # Radio de búsqueda (ajustable)
    SEARCH_RADIUS = 5.0

    for milestone in path_points:
        mx, my = milestone

        # Encontrar bloques cercanos a este vértice
        close_ones = []
        for blk in pool:
            dist = math.hypot(blk['X'] - mx, blk['Y'] - my)
            if dist < SEARCH_RADIUS:
                close_ones.append(blk)

        # Ordenar esos bloques locales por cercanía exacta al vértice
        close_ones.sort(key=lambda b: math.hypot(b['X'] - mx, b['Y'] - my))

        # Agregarlos a la lista final y sacarlos del pool
        ordered_blocks.extend(close_ones)
        for b in close_ones:
            pool.remove(b)

    # Añadir los sobrantes al final
    if pool:
        display_message(
            f"{len(pool)} bloques estaban muy lejos de la ruta, se agregan al final.", "warning")
        ordered_blocks.extend(pool)

    return ordered_blocks


def ensure_layer(acad, layer_name, color_code=2):
    """Crea la capa si no existe."""
    try:
        acad.doc.Layers.Add(layer_name)
        acad.doc.Layers.Item(layer_name).Color = color_code
    except Exception:
        pass


def main():
    acad = require_autocad("Numeración de Postes por Ruta")

    # AUTODETECCIÓN DE CAPAS 'POSTE_*'
    all_layers = get_all_layer_names(acad)
    postes_layers = [L for L in all_layers if L.upper().startswith("POSTE")]

    if not postes_layers:
        display_message(
            "No se encontraron capas que inicien con 'POSTE'.", "error")
        return

    display_message(f"Capas encontradas: {', '.join(postes_layers)}", "info")

    # Extraer data de TODAS las capas de postes encontradas
    raw_data = []
    for layer in postes_layers:
        raw_data.extend(extract_block_data(acad, layer))

    if not raw_data:
        return

    # SELECCIÓN DE RUTA
    # Filtramos capas para no mostrar las mismas de los postes
    route_layers = [L for L in all_layers if L not in postes_layers]
    layer_ruta = get_selection_from_list(
        "Seleccione la capa de la POLILÍNEA de ruta:", route_layers)

    if not layer_ruta:
        return

    # Obtener vértices de la polilínea
    path_points = get_polyline_points(acad, layer_ruta)
    if not path_points:
        return

    # ORDENAMIENTO
    sorted_data = sort_blocks_by_path(raw_data, path_points)

    # NUMERACIÓN Y DIBUJO
    target_layer = "NUMERACION_POSTES"
    ensure_layer(acad, target_layer, 5)

    display_message(
        f"Dibujando numeración en capa '{target_layer}'...", "info")

    for i, blk in enumerate(sorted_data, 1):
        blk['Nuevo_Numero'] = i

        # Dibujo
        center = APoint(blk['X'], blk['Y'])
        circle = acad.model.AddCircle(center, 2.0)
        circle.Layer = target_layer
        text_pos = APoint(blk['X'] - 3, blk['Y'] -
                          2.5)
        text = acad.model.AddText(str(i), text_pos, 1.5)
        text.Layer = target_layer

    display_message("Numeración completada en AutoCAD.", "success")

    # EXPORTACIÓN
    if get_confirmation("¿Desea exportar el reporte de numeración?"):
        if not sorted_data:
            return

        all_keys = list(sorted_data[0].keys())

        priority_order = ["Nuevo_Numero", "Nombre",
                          "Capa", "X", "Y", "Z", "Rotacion", "EscalaX"]

        final_columns = []
        for col in priority_order:
            if col in all_keys:
                final_columns.append(col)
                all_keys.remove(col)

        final_columns.extend(all_keys)
        data_to_export = []
        for item in sorted_data:
            row = [item.get(col, "") for col in final_columns]
            data_to_export.append(row)

        show_export_menu(
            data_to_export, "Reporte_Postes_Ordenados", columns=final_columns)


if __name__ == "__main__":
    main()
