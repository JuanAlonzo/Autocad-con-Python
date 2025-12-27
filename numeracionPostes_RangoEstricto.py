"""
Script: Numeración de Postes (Rango Estricto)
Propósito: 
1. Buscar bloques en capas 'POSTES*'.
2. Ordenarlos siguiendo una Polilínea guía.
3. IMPORTANTE: Omitir/Ignorar los postes que estén fuera del rango de la ruta.
4. Exportar reporte limpio con columna 'N' al inicio.
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
    get_confirmation,
    get_user_input
)


def get_polyline_points(acad, layer_ruta):
    """Extrae los vértices de la Polilínea (ruta)."""
    path_points = []
    found = False
    display_message(f"Buscando polilínea en capa '{layer_ruta}'...", "info")

    for obj in acad.iter_objects():
        if obj.Layer == layer_ruta and obj.ObjectName == "AcDbPolyline":
            coords = obj.Coordinates
            for i in range(0, len(coords), 2):
                path_points.append((coords[i], coords[i+1]))
            found = True
            break

    if not found:
        display_message(f"No se encontró Polilínea en {layer_ruta}.", "error")
        return []

    display_message(
        f"Ruta detectada con {len(path_points)} vértices.", "success")
    return path_points


def sort_blocks_strict(blocks_dicts, path_points, search_radius):
    """
    Ordena bloques por ruta y DESCARTA los que estén lejos.
    """
    ordered_blocks = []
    pool = blocks_dicts.copy()
    ignored_count = 0

    display_message(
        f"Filtrando postes a {search_radius}u de la ruta...", "info")

    for milestone in path_points:
        mx, my = milestone

        # Buscar bloques cercanos a este vértice
        close_ones = []
        for blk in pool:
            dist = math.hypot(blk['X'] - mx, blk['Y'] - my)
            if dist <= search_radius:
                close_ones.append(blk)

        # Ordenarlos por cercanía exacta al vértice y agregarlos
        if close_ones:
            close_ones.sort(key=lambda b: math.hypot(b['X'] - mx, b['Y'] - my))
            ordered_blocks.extend(close_ones)

            # Quitarlos del pool para no repetirlos
            for b in close_ones:
                pool.remove(b)

    # Lo que quedó en 'pool' se ignora.
    ignored_count = len(pool)

    if ignored_count > 0:
        display_message(
            f"Se omitieron {ignored_count} postes por estar fuera de rango.", "warning")
    else:
        display_message("Todos los postes entraron en el rango.", "success")

    return ordered_blocks


def ensure_layer(acad, layer_name, color_code=2):
    try:
        acad.doc.Layers.Add(layer_name)
        acad.doc.Layers.Item(layer_name).Color = color_code
    except Exception:
        pass


def main():
    acad = require_autocad("Numeración Estricta por Ruta")

    # CAPAS POSTE
    all_layers = get_all_layer_names(acad)
    postes_layers = [L for L in all_layers if L.upper().startswith("POSTE")]

    if not postes_layers:
        display_message("No se encontraron capas 'POSTE*'.", "error")
        return

    raw_data = []
    for layer in postes_layers:
        raw_data.extend(extract_block_data(acad, layer))

    if not raw_data:
        return

    # CAPA RUTA
    route_layers = [L for L in all_layers if L not in postes_layers]
    layer_ruta = get_selection_from_list(
        "Seleccione capa de RUTA (Polilínea):", route_layers)
    if not layer_ruta:
        return

    path_points = get_polyline_points(acad, layer_ruta)
    if not path_points:
        return

    # DEFINIR RANGO (Radio de búsqueda)
    # Pedimos al usuario la tolerancia. Si da Enter, usa 5 por defecto.
    radius_input = get_user_input(
        "Ingrese radio máximo de búsqueda (Enter = 5)", default="5")
    try:
        search_radius = float(radius_input)
    except ValueError:
        search_radius = 5.0

    # ORDENAMIENTO ESTRICTO
    sorted_data = sort_blocks_strict(raw_data, path_points, search_radius)

    if not sorted_data:
        display_message(
            "Ningún poste cumple con el rango especificado.", "error")
        return

    # DIBUJO
    target_layer = "NUMERACION_POSTES"
    ensure_layer(acad, target_layer, 5)

    for i, blk in enumerate(sorted_data, 1):
        blk['Nuevo_Numero'] = i  # Creamos la columna prioritaria

        # Dibujo
        center = APoint(blk['X'], blk['Y'])
        circle = acad.model.AddCircle(center, 2.0)
        circle.Layer = target_layer
        text_pos = APoint(blk['X'] - 3, blk['Y'] - 2.5)
        text = acad.model.AddText(str(i), text_pos, 1.5)
        text.Layer = target_layer

    display_message("Numeración completada en AutoCAD.", "success")

    # EXPORTACIÓN
    if get_confirmation("¿Exportar reporte filtrado?"):
        if not sorted_data:
            return

        all_keys = list(sorted_data[0].keys())

        # Orden prioritario: N primero
        priority_order = ["Nuevo_Numero", "Nombre",
                          "Capa", "X", "Y", "Z", "Rotacion", "EscalaX"]

        final_columns = []
        # Prioritarias
        for col in priority_order:
            if col in all_keys:
                final_columns.append(col)
                all_keys.remove(col)

        # Resto (Atributos, Z, etc.)
        final_columns.extend(all_keys)

        # Crear matriz de datos limpia
        data_to_export = []
        for item in sorted_data:
            row = [item.get(col, "") for col in final_columns]
            data_to_export.append(row)

        show_export_menu(
            data_to_export, "Reporte_Postes_RutaEstricta", columns=final_columns)


if __name__ == "__main__":
    main()
