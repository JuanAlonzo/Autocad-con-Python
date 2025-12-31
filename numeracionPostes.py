"""
Numeración de Postes Unificada
Propósito:
1. Detectar capas 'POSTE*'.
2. Seleccionar ruta (Polilínea).
3. Solicitar modo de operación (Normal vs Estricto).
4. Numerar, dibujar y exportar reporte.
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
from utilities.config import (
    LAYER_PREFIX_POSTES,
    LAYER_NUMERACION,
    COLOR_NUMERACION,
    COLOR_NUMERACION_ESTRICTA,
    TEXT_HEIGHT,
    CIRCLE_RADIUS,
    TEXT_OFFSET_X,
    TEXT_OFFSET_Y,
    DEFAULT_SEARCH_RADIUS
)


def get_polyline_points(acad, layer_ruta):
    """Extrae vértices de la polilínea guía."""
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


def sort_blocks_unified(blocks_dicts, path_points, search_radius, strict_mode=False):
    """
    Algoritmo de ordenamiento híbrido.
    - strict_mode = True: Ignora postes fuera del radio.
    - strict_mode = False: Agrega postes fuera del radio al final de la lista.
    """
    ordered_blocks = []
    pool = blocks_dicts.copy()

    display_message(
        f"Procesando con radio {search_radius}u (Modo Estricto: {strict_mode})...", "info")

    for milestone in path_points:
        mx, my = milestone

        # Buscar cercanos al vértice actual
        close_ones = []
        for blk in pool:
            dist = math.hypot(blk['X'] - mx, blk['Y'] - my)
            if dist <= search_radius:
                close_ones.append(blk)

        # Ordenar locales y mover a lista final
        if close_ones:
            close_ones.sort(key=lambda b: math.hypot(b['X'] - mx, b['Y'] - my))
            ordered_blocks.extend(close_ones)
            for b in close_ones:
                pool.remove(b)

    # Tratamiento de remanentes (Postes lejanos)
    if pool:
        count = len(pool)
        if strict_mode:
            display_message(
                f"Se omitieron {count} postes fuera de rango (Estricto).", "warning")
        else:
            display_message(
                f"Se agregaron {count} postes lejanos al final de la lista (Normal).", "warning")
            ordered_blocks.extend(pool)
    else:
        display_message(
            "Todos los postes fueron cubiertos por la ruta.", "success")

    return ordered_blocks


def associate_data_layers(main_blocks, data_blocks, max_radius):
    """
    Busca el bloque de datos más cercano para cada poste y fusiona sus atributos.
    """
    count = 0
    display_message(f"Asociando datos (Radio: {max_radius}m)...", "info")

    for pole in main_blocks:
        px, py = pole['X'], pole['Y']

        # Buscar candidatos cercanos
        candidates = []
        for info in data_blocks:
            # Calculamos distancia euclidiana
            dist = math.hypot(px - info['X'], py - info['Y'])
            if dist <= max_radius:
                candidates.append((dist, info))

        # Si encontramos alguno, tomamos el más cercano
        if candidates:
            candidates.sort(key=lambda x: x[0])  # Ordenar por distancia
            best_match = candidates[0][1]  # El objeto más cercano

            # COPIAR SOLO ATRIBUTOS (Ignoramos X, Y del texto para no mover el poste)
            for key, val in best_match.items():
                if key.startswith("Attr_"):
                    pole[key] = val

            count += 1

    display_message(f"Se asociaron datos a {count} postes.", "success")
    return main_blocks


def ensure_layer(acad, layer_name, color_code):
    try:
        acad.doc.Layers.Add(layer_name)
        acad.doc.Layers.Item(layer_name).Color = color_code
    except Exception:
        pass


def main():
    acad = require_autocad("Numeración de Postes (Global)")

    # CAPAS
    all_layers = get_all_layer_names(acad)
    postes_layers = [
        L for L in all_layers if L.upper().startswith(LAYER_PREFIX_POSTES)]

    if not postes_layers:
        display_message("No se encontraron capas 'POSTE*'.", "error")
        return

    # Extraemos data
    raw_data = []
    for layer in postes_layers:
        raw_data.extend(extract_block_data(acad, layer))
    if not raw_data:
        return

    # RUTA
    route_layers = [L for L in all_layers if L not in postes_layers]
    layer_ruta = get_selection_from_list(
        "Seleccione capa de RUTA:", route_layers)
    if not layer_ruta:
        return

    path_points = get_polyline_points(acad, layer_ruta)
    if not path_points:
        return

    # CONFIGURACIÓN DEL PROCESO
    modes = ["Modo Normal (Incluir todos)", "Modo Estricto (Solo cercanos)"]
    mode_sel = get_selection_from_list("Seleccione Modo de Numeración", modes)
    if not mode_sel:
        return

    strict_mode = "Estricto" in mode_sel

    # Pedir radio (Usando valor por defecto del config)
    r_input = get_user_input(
        f"Radio de búsqueda (Enter = {DEFAULT_SEARCH_RADIUS})", default=str(DEFAULT_SEARCH_RADIUS))
    try:
        search_radius = float(r_input)
    except ValueError:
        search_radius = DEFAULT_SEARCH_RADIUS

    # EJECUTAR ORDENAMIENTO
    sorted_data = sort_blocks_unified(
        raw_data, path_points, search_radius, strict_mode)

    if not sorted_data:
        display_message("No hay postes para numerar.", "error")
        return

    # 4.5 ASOCIACIÓN DE DATOS (NUEVO)
    if get_confirmation("¿Asociar datos de otra capa (ej: CAT_COD_POSTE)?"):
        # 1. Pedir capa de datos
        # Obtenemos lista de capas para que el usuario elija, excluyendo la actual
        other_layers = [L for L in all_layers if L not in postes_layers]
        layer_data_name = get_selection_from_list(
            "Seleccione capa de DATOS:", other_layers)

        if layer_data_name:
            # 2. Extraer los bloques de datos (Usa el nuevo motor win32com)
            data_blocks = extract_block_data(acad, layer_data_name)

            if data_blocks:
                # 3. Pedir radio de asociación (distancia máxima entre poste y texto)
                try:
                    r_assoc_str = get_user_input(
                        f"Radio de asociación (Enter=2.0): ", default="2.0")
                    r_assoc = float(r_assoc_str)
                except:
                    r_assoc = 2.0

                # 4. Ejecutar la magia
                sorted_data = associate_data_layers(
                    sorted_data, data_blocks, r_assoc)

    # DIBUJO
    # Elegimos color según el modo para diferenciarlos visualmente
    target_color = COLOR_NUMERACION_ESTRICTA if strict_mode else COLOR_NUMERACION

    ensure_layer(acad, LAYER_NUMERACION, target_color)

    display_message(f"Dibujando en capa '{LAYER_NUMERACION}'...", "info")

    for i, blk in enumerate(sorted_data, 1):
        blk['N'] = i  # Columna prioritaria

        # Geometría
        center = APoint(blk['X'], blk['Y'])
        text_pos = APoint(blk['X'] + TEXT_OFFSET_X, blk['Y'] + TEXT_OFFSET_Y)

        # Dibujar Círculo
        c = acad.model.AddCircle(center, CIRCLE_RADIUS)
        c.Layer = LAYER_NUMERACION

        # Dibujar Texto
        t = acad.model.AddText(str(i), text_pos, TEXT_HEIGHT)
        t.Layer = LAYER_NUMERACION

    # 6. EXPORTACIÓN (Con lógica de lista de listas corregida)
    if get_confirmation("¿Generar reporte Excel/CSV?"):
        all_keys = list(sorted_data[0].keys())

        # Orden de columnas deseado
        priority = ["N", "Nuevo_Numero", "Nombre", "Capa", "X", "Y"]
        final_columns = [col for col in priority if col in all_keys]

        # Agregar columnas restantes (Z, Atributos...)
        final_columns.extend([k for k in all_keys if k not in final_columns])

        # Crear Matriz (Lista de Listas)
        data_to_export = []
        for item in sorted_data:
            row = [item.get(col, "") for col in final_columns]
            data_to_export.append(row)

        suffix = "Estricto" if strict_mode else "Normal"
        show_export_menu(
            data_to_export, f"Reporte_Postes_{suffix}", columns=final_columns)


if __name__ == "__main__":
    main()
