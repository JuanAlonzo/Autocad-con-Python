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
from utilities import (
    require_autocad,
    get_all_layer_names,
    extract_block_data,
    show_export_menu,
    ConsoleUI,
    SETTINGS,
)

ui = ConsoleUI()


def get_polyline_points(acad, layer_ruta, ui):
    """Extrae vértices de la polilínea guía."""
    path_points = []
    found = False
    ui.show_message(f"Buscando polilínea en capa '{layer_ruta}'...", "info")

    for obj in acad.iter_objects():
        if obj.Layer == layer_ruta and obj.ObjectName == "AcDbPolyline":
            coords = obj.Coordinates
            for i in range(0, len(coords), 2):
                path_points.append((coords[i], coords[i + 1]))
            found = True
            break

    if not found:
        ui.show_message(f"No se encontró Polilínea en {layer_ruta}.", "error")
        return []

    ui.show_message(f"Ruta detectada con {len(path_points)} vértices.", "success")
    return path_points


def sort_blocks_unified(
    blocks_dicts, path_points, ui, search_radius, strict_mode=False
):
    """
    Algoritmo de ordenamiento híbrido.
    - strict_mode = True: Ignora postes fuera del radio.
    - strict_mode = False: Agrega postes fuera del radio al final de la lista.
    """
    ordered_blocks = []
    pool = blocks_dicts.copy()

    ui.show_message(
        f"Procesando con radio {search_radius}u (Modo Estricto: {strict_mode})...",
        "info",
    )

    for milestone in path_points:
        mx, my = milestone

        # Buscar cercanos al vértice actual
        close_ones = []
        for blk in pool:
            dist = math.hypot(blk["X"] - mx, blk["Y"] - my)
            if dist <= search_radius:
                close_ones.append(blk)

        # Ordenar locales y mover a lista final
        if close_ones:
            close_ones.sort(key=lambda b: math.hypot(b["X"] - mx, b["Y"] - my))
            ordered_blocks.extend(close_ones)
            for b in close_ones:
                pool.remove(b)

    # Tratamiento de remanentes (Postes lejanos)
    if pool:
        count = len(pool)
        if strict_mode:
            ui.show_message(
                f"Se omitieron {count} postes fuera de rango (Estricto).", "warning"
            )
        else:
            ui.show_message(
                f"Se agregaron {count} postes lejanos al final de la lista (Normal).",
                "warning",
            )
            ordered_blocks.extend(pool)
    else:
        ui.show_message("Todos los postes fueron cubiertos por la ruta.", "success")

    return ordered_blocks


def associate_data_layers(main_blocks, data_blocks, max_radius, ui):
    """
    Busca el bloque de datos más cercano para cada poste y fusiona sus atributos.
    """
    count = 0
    ui.show_message(f"Asociando datos (Radio: {max_radius}m)...", "info")

    for pole in main_blocks:
        px, py = pole["X"], pole["Y"]

        # Buscar candidatos cercanos
        candidates = []
        for info in data_blocks:
            # Calculamos distancia euclidiana
            dist = math.hypot(px - info["X"], py - info["Y"])
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

    ui.show_message(f"Se asociaron datos a {count} postes.", "success")
    return main_blocks


def ensure_layer(acad, layer_name, color_code):
    try:
        acad.doc.Layers.Add(layer_name)
        acad.doc.Layers.Item(layer_name).Color = color_code
    except Exception:
        pass


def main():
    acad = require_autocad(ui)

    # CAPAS
    all_layers = get_all_layer_names(acad)
    postes_layers = [
        L for L in all_layers if L.upper().startswith(SETTINGS.LAYER_PREFIX_POSTES)
    ]

    if not postes_layers:
        ui.show_message("No se encontraron capas 'POSTE*'.", "error")
        return

    # Extraemos data de todas las capas de postes
    raw_data = []
    for layer in postes_layers:
        raw_data.extend(extract_block_data(acad, ui, layer))
    if not raw_data:
        return

    # RUTA
    route_layers = [L for L in all_layers if L not in postes_layers]
    layer_ruta = ui.get_selection("Seleccione capa de RUTA:", route_layers)
    if not layer_ruta:
        return

    path_points = get_polyline_points(acad, layer_ruta, ui)
    if not path_points:
        return

    # CONFIGURACIÓN DEL PROCESO
    modes = ["Modo Normal (Incluir todos)", "Modo Estricto (Solo cercanos)"]
    mode_sel = ui.get_selection("Seleccione Modo de Numeración", modes)
    if not mode_sel:
        return

    strict_mode = "Estricto" in mode_sel

    # Pedir radio (Usando valor por defecto del config)
    try:
        r_val = ui.get_input(
            f"Radio de búsqueda (Enter = {SETTINGS.DEFAULT_SEARCH_RADIUS})",
            default=str(SETTINGS.DEFAULT_SEARCH_RADIUS),
        )
        search_radius = float(r_val)
    except ValueError:
        search_radius = SETTINGS.DEFAULT_SEARCH_RADIUS

    # EJECUTAR ORDENAMIENTO
    sorted_data = sort_blocks_unified(
        raw_data, path_points, ui, search_radius, strict_mode
    )

    if not sorted_data:
        ui.show_message("No hay postes para numerar.", "error")
        return

    # 4.5 ASOCIACIÓN DE DATOS (NUEVO)
    if ui.confirm("¿Asociar datos de otra capa (ej: CAT_COD_POSTE)?"):
        # 1. Pedir capa de datos
        # Obtenemos lista de capas para que el usuario elija, excluyendo la actual
        other_layers = [L for L in all_layers if L not in postes_layers]
        layer_data_name = ui.get_selection("Seleccione capa de DATOS:", other_layers)

        if layer_data_name:
            # 2. Extraer los bloques de datos (Usa el nuevo motor win32com)
            data_blocks = extract_block_data(acad, layer_data_name)

            if data_blocks:
                # 3. Pedir radio de asociación (distancia máxima entre poste y texto)
                try:
                    r_assoc_str = ui.get_input(
                        "Radio de asociación (Enter=2.0): ", default="2.0"
                    )
                    r_assoc = float(r_assoc_str)
                except Exception:
                    r_assoc = 2.0

                # 4. Ejecutar la magia
                sorted_data = associate_data_layers(
                    sorted_data, data_blocks, r_assoc, ui
                )

    # DIBUJO
    # Elegimos color según el modo para diferenciarlos visualmente
    target_color = (
        SETTINGS.COLOR_NUMERACION_ESTRICTA if strict_mode else SETTINGS.COLOR_NUMERACION
    )

    ensure_layer(acad, SETTINGS.LAYER_NUMERACION, target_color)

    ui.show_message(f"Dibujando en capa '{SETTINGS.LAYER_NUMERACION}'...", "info")
    for i, blk in enumerate(sorted_data, 1):
        blk["N"] = i  # Columna prioritaria

        # Geometría
        center = APoint(blk["X"], blk["Y"])
        text_pos = APoint(
            blk["X"] + SETTINGS.TEXT_OFFSET_X, blk["Y"] + SETTINGS.TEXT_OFFSET_Y
        )

        # Dibujar Círculo
        c = acad.model.AddCircle(center, SETTINGS.CIRCLE_RADIUS)
        c.Layer = SETTINGS.LAYER_NUMERACION
        # Dibujar Texto
        t = acad.model.AddText(str(i), text_pos, SETTINGS.TEXT_HEIGHT)
        t.Layer = SETTINGS.LAYER_NUMERACION

    # 6. EXPORTACIÓN (Con lógica de lista de listas corregida)
    if ui.confirm("¿Generar reporte Excel/CSV?"):
        all_keys = set()
        for item in sorted_data:
            all_keys.update(item.keys())
        all_keys = list(all_keys)

        # Orden de columnas deseado
        priority = ["N", "Nuevo_Numero", "Nombre", "Capa", "X", "Y"]
        remaining = [col for col in all_keys if col not in priority]
        remaining.sort()
        # Agregar columnas restantes (Z, Atributos...)
        final_cols = priority + remaining

        # Crear Matriz (Lista de Listas)
        data_to_export = []
        for item in sorted_data:
            row = [str(item.get(col, "")) for col in final_cols]
            data_to_export.append(row)

        name = f"Reporte{'Estricto' if strict_mode else 'Normal'}"
        show_export_menu(data_to_export, name, ui, columns=final_cols)


if __name__ == "__main__":
    main()
