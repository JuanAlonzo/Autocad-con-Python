"""
Numeración con Bloques UTM (Estrategia Handle)
1. Inserta con pyautocad (APoint).
2. Edita con win32com (HandleToObject).
"""

import math
import win32com.client
from pyautocad import APoint
from utilities import (
    require_autocad,
    get_all_layer_names,
    extract_block_data,
    show_export_menu,
    get_polyline_points,
    ConsoleUI,
    SETTINGS,
)

ui = ConsoleUI()


def sort_blocks_unified(blocks_dicts, path_points, search_radius, ui, strict_mode):
    """
    Algoritmo de Ordenamiento Espacial.
    strict_mode = True: Descarta lo que no esté cerca de la ruta.
    strict_mode = False: Agrega los sobrantes al final.
    """
    ordered_blocks = []
    pool = blocks_dicts.copy()
    total_inicial = len(pool)

    ui.show_message(
        f"Procesando {total_inicial} postes (Radio: {search_radius}m | Modo: {'Estricto' if strict_mode else 'Normal'})...",
        "info",
    )

    # Captura por cercanía a vértices
    for i, milestone in enumerate(path_points):
        mx, my = milestone
        close_ones = []

        # Buscamos candidatos en el pool
        for blk in pool:
            dist = math.hypot(blk["X"] - mx, blk["Y"] - my)
            if dist <= search_radius:
                close_ones.append(blk)

        if close_ones:
            # Ordenar sub-grupo por cercanía exacta al vértice
            close_ones.sort(key=lambda b: math.hypot(b["X"] - mx, b["Y"] - my))
            ordered_blocks.extend(close_ones)
            # Sacarlos del pool para no repetirlos
            for b in close_ones:
                if b in pool:
                    pool.remove(b)

    # Gestión de Sobrantes
    sobrantes = len(pool)
    if sobrantes > 0:
        if strict_mode:
            ui.show_message(
                f"Modo Estricto: Se han omitido {sobrantes} postes lejanos a la ruta.",
                "warning",
            )
            # En modo estricto, 'pool' se ignora (se descartan)
        else:
            ui.show_message(
                f"Modo Normal: Se agregaron {sobrantes} postes dispersos al final de la secuencia.",
                "info",
            )
            ordered_blocks.extend(pool)
    else:
        ui.show_message(
            "Cobertura Perfecta: Todos los postes estaban dentro del radio de la ruta.",
            "success",
        )

    return ordered_blocks


def update_attrib_via_handle(handle, target_tag, new_value):
    """
    Edición Quirúrgica: Usa win32com para modificar atributos por Handle.
    """
    try:
        acad_app = win32com.client.GetActiveObject("AutoCAD.Application")
        doc = acad_app.ActiveDocument
        obj_native = doc.HandleToObject(handle)

        if obj_native.HasAttributes:
            for att in obj_native.GetAttributes():
                if att.TagString.upper() == target_tag.upper():
                    att.TextString = str(new_value)
                    att.Update()
                    return True
        return False
    except Exception:
        return False


def insert_and_update(acad, x, y, z, number, is_first):
    """Coordinador de Inserción y Edición."""
    try:
        # Insertar con pyautocad
        point = APoint(float(x), float(y), float(z))
        block_ref = acad.model.InsertBlock(
            point,
            SETTINGS.BLOQUE_A_INSERTAR,
            SETTINGS.ESCALA_BLOQUE,
            SETTINGS.ESCALA_BLOQUE,
            SETTINGS.ESCALA_BLOQUE,
            0,
        )
        block_ref.Layer = SETTINGS.CAPA_DESTINO

        # Editar con win32com
        handle = block_ref.Handle
        ok = update_attrib_via_handle(handle, SETTINGS.ATRIBUTO_ETIQUETA, number)

        if not ok and is_first:
            print(
                f"DEBUG: No se encontró tag '{SETTINGS.ATRIBUTO_ETIQUETA}'. Tags reales: {[att.TagString for att in block_ref.GetAttributes()]}"
            )

        return True
    except Exception as e:
        if is_first:
            ui.show_message(f"Error insertando: {e}", "error")
        return False


def main():
    acad = require_autocad(ui)

    all_layers = get_all_layer_names(acad)
    postes_layers = [
        L for L in all_layers if L.upper().startswith(SETTINGS.LAYER_PREFIX_POSTES)
    ]

    if not postes_layers:
        ui.show_message(
            f"No se encontraron capas que empiecen con '{SETTINGS.LAYER_PREFIX_POSTES}'.",
            "error",
        )
        return

    # Extracción
    raw_data = []
    for layer in postes_layers:
        layer_data = extract_block_data(acad, ui, layer)
        raw_data.extend(layer_data)

    total_original = len(raw_data)

    # Usamos un diccionario para eliminar duplicados basados en el 'Handle'
    unique_map = {blk["Handle"]: blk for blk in raw_data}
    raw_data = list(unique_map.values())

    diff = total_original - len(raw_data)

    if diff > 0:
        ui.show_message(
            f"Se eliminaron {diff} bloques duplicados.",
            "info",
        )
    ui.show_message(f"Total de bloques únicos detectados: {len(raw_data)}", "info")
    # -------------------------------------------

    if not raw_data:
        ui.show_message("No se encontraron bloques de postes.", "error")
        return

    # Selección de Ruta
    route_layers = [L for L in all_layers if L not in postes_layers]
    layer_ruta = ui.get_selection(
        "Seleccione la capa de la RUTA (Polilínea):", route_layers
    )
    if not layer_ruta:
        return

    path_points = get_polyline_points(acad, layer_ruta, ui)
    if not path_points:
        return

    # Configuración de Usuario
    modes = ["Modo Normal (Incluir Todo)", "Modo Estricto (Solo Ruta)"]
    mode_sel = ui.get_selection("Seleccione Modo de Numeración:", modes)
    if not mode_sel:
        return
    strict_mode = "Estricto" in mode_sel

    try:
        r_str = ui.get_input(
            f"Radio de búsqueda (mts) [Default={SETTINGS.DEFAULT_SEARCH_RADIUS}]:",
            default=str(SETTINGS.DEFAULT_SEARCH_RADIUS),
        )
        radius = float(r_str)
    except Exception:
        radius = SETTINGS.DEFAULT_SEARCH_RADIUS
    # Procesamiento
    sorted_data = sort_blocks_unified(raw_data, path_points, radius, ui, strict_mode)

    if not sorted_data:
        ui.show_message("Ningún poste cumple con los criterios de la ruta.", "warning")
        return

    # Inserción Masiva
    try:
        acad.doc.Layers.Add(SETTINGS.CAPA_DESTINO)
    except Exception:
        pass

    msg_confirm = (
        f"RESUMEN DE OPERACIÓN:\n"
        f"---------------------\n"
        f"• Total a insertar: {len(sorted_data)} bloques\n"
        f"• Bloque Base: '{SETTINGS.BLOQUE_A_INSERTAR}'\n"
        f"• Capa Destino: '{SETTINGS.CAPA_DESTINO}'\n"
        f"• Escala: {SETTINGS.ESCALA_BLOQUE}\n\n"
        f"¿Proceder con la inserción?"
    )

    if ui.confirm(msg_confirm):
        ui.progress_start(len(sorted_data), "Insertando y Numerando...")

        success_count = 0
        for i, blk in enumerate(sorted_data, 1):
            # Insertar
            ok = insert_and_update(
                acad, blk["X"], blk["Y"], blk.get("Z", 0.0), i, (i == 1)
            )

            if ok:
                success_count += 1

            # Enriquecer datos para el reporte
            blk["Nuevo_Numero"] = i
            blk["Estado_Insercion"] = "OK" if ok else "ERROR"

            ui.progress_update(1)

        ui.progress_stop()
        acad.doc.Regen(1)
        ui.show_message(
            f"Terminado. Se insertaron {success_count} de {len(sorted_data)} bloques.",
            "success",
        )

    # Exportación
    if ui.confirm("¿Generar Reporte Excel Detallado?"):
        if not sorted_data:
            return

        # Obtener TODAS las columnas posibles de todos los diccionarios
        all_keys = set()
        for item in sorted_data:
            all_keys.update(item.keys())
        all_keys = list(all_keys)

        # Definir orden prioritario para que se vea bonito
        priority_cols = [
            "Nuevo_Numero",
            "Nombre",
            "Capa",
            "X",
            "Y",
            "Z",
            "Estado_Insercion",
        ]

        # Columnas de atributos (las que empiezan con Attr_)
        attr_cols = sorted([k for k in all_keys if k.startswith("Attr_")])

        # Columnas restantes (cualquier otra cosa)
        other_cols = sorted(
            [k for k in all_keys if k not in priority_cols and k not in attr_cols]
        )

        # Lista final ordenada
        final_columns = priority_cols + attr_cols + other_cols

        # Preparar datos
        export_data = []
        for item in sorted_data:
            row = [str(item.get(col, "")) for col in final_columns]
            export_data.append(row)

        show_export_menu(
            export_data, "Reporte_Numeracion_UTM", ui, columns=final_columns
        )


if __name__ == "__main__":
    main()
