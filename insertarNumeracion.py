"""
Numeración con Bloques UTM (Estrategia Handle)
1. Inserta con pyautocad (APoint).
2. Edita con win32com (HandleToObject).
"""

import math
import win32com.client  # Necesario para la edición quirúrgica
from pyautocad import APoint
from utilities.acad_common import require_autocad
from utilities.acad_layers import get_all_layer_names
from utilities.acad_entities import extract_block_data
from utilities.acad_export import show_export_menu
from utilities.ui_console import ConsoleUI
from utilities.config import (
    LAYER_PREFIX_POSTES,
    DEFAULT_SEARCH_RADIUS
)

# --- CONFIGURACIÓN ---
BLOQUE_A_INSERTAR = "UBICACION POSTES UTM"
CAPA_DESTINO = "NUMERACION"
ATRIBUTO_ETIQUETA = "000"
ESCALA_BLOQUE = 2.0

ui = ConsoleUI()


def get_polyline_points(acad, layer_ruta, ui):
    """Extrae vértices de la polilínea guía."""
    path_points = []
    found = False
    ui.show_message(f"🔍 Analizando capa de ruta '{layer_ruta}'...", "info")

    for obj in acad.iter_objects():
        if obj.Layer == layer_ruta and obj.ObjectName == "AcDbPolyline":
            coords = obj.Coordinates
            # Convertir array plano [x1,y1, x2,y2] a lista de tuplas [(x,y), (x,y)]
            for i in range(0, len(coords), 2):
                path_points.append((coords[i], coords[i+1]))
            found = True
            break

    if not found:
        ui.show_message(
            f"❌ Error: No se encontró ninguna Polilínea en la capa '{layer_ruta}'.", "error")
        return []

    ui.show_message(
        f"✅ Ruta válida encontrada: {len(path_points)} vértices.", "success")
    return path_points


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
        f"⚙️ Procesando {total_inicial} postes (Radio: {search_radius}m | Modo: {'Estricto' if strict_mode else 'Normal'})...", "info")

    # Fase 1: Captura por cercanía a vértices
    for i, milestone in enumerate(path_points):
        mx, my = milestone
        close_ones = []

        # Buscamos candidatos en el pool
        for blk in pool:
            dist = math.hypot(blk['X'] - mx, blk['Y'] - my)
            if dist <= search_radius:
                close_ones.append(blk)

        if close_ones:
            # Ordenar sub-grupo por cercanía exacta al vértice
            close_ones.sort(key=lambda b: math.hypot(b['X'] - mx, b['Y'] - my))
            ordered_blocks.extend(close_ones)
            # Sacarlos del pool para no repetirlos
            for b in close_ones:
                if b in pool:
                    pool.remove(b)

    # Fase 2: Gestión de Sobrantes (Leftovers)
    sobrantes = len(pool)
    if sobrantes > 0:
        if strict_mode:
            ui.show_message(
                f"⚠️ Modo Estricto: Se han omitido {sobrantes} postes lejanos a la ruta.", "warning")
            # En modo estricto, 'pool' se ignora (se descartan)
        else:
            ui.show_message(
                f"ℹ️ Modo Normal: Se agregaron {sobrantes} postes dispersos al final de la secuencia.", "info")
            ordered_blocks.extend(pool)
    else:
        ui.show_message(
            "✨ Cobertura Perfecta: Todos los postes estaban dentro del radio de la ruta.", "success")

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
    except:
        return False


def insert_and_update(acad, x, y, z, number, is_first):
    """Coordinador de Inserción y Edición."""
    try:
        # 1. Insertar (pyautocad)
        point = APoint(float(x), float(y), float(z))
        block_ref = acad.model.InsertBlock(
            point, BLOQUE_A_INSERTAR, ESCALA_BLOQUE, ESCALA_BLOQUE, ESCALA_BLOQUE, 0)
        block_ref.Layer = CAPA_DESTINO

        # 2. Editar (win32com)
        handle = block_ref.Handle
        ok = update_attrib_via_handle(handle, ATRIBUTO_ETIQUETA, number)

        if not ok and is_first:
            print(
                f"DEBUG: No se encontró tag '{ATRIBUTO_ETIQUETA}'. Tags reales: {[att.TagString for att in block_ref.GetAttributes()]}")

        return True
    except Exception as e:
        if is_first:
            ui.show_message(f"Error insertando: {e}", "error")
        return False


def main():
    # 1. Inicio
    acad = require_autocad(ui)

    # 2. Selección de Capas de Origen
    all_layers = get_all_layer_names(acad)
    postes_layers = [
        L for L in all_layers if L.upper().startswith(LAYER_PREFIX_POSTES)]

    if not postes_layers:
        ui.show_message(
            f"No se encontraron capas que empiecen con '{LAYER_PREFIX_POSTES}'.", "error")
        return

    # Extracción
    ui.progress_start(len(postes_layers), "Extrayendo datos de postes...")
    raw_data = []
    for layer in postes_layers:
        # Ui=None para no spammear mensajes internos
        raw_data.extend(extract_block_data(acad, None, layer))
        ui.progress_update(1)
    ui.progress_stop()

    if not raw_data:
        ui.show_message("No se encontraron bloques de postes.", "error")
        return

    # 3. Selección de Ruta
    route_layers = [L for L in all_layers if L not in postes_layers]
    layer_ruta = ui.get_selection(
        "Seleccione la capa de la RUTA (Polilínea):", route_layers)
    if not layer_ruta:
        return

    path_points = get_polyline_points(acad, layer_ruta, ui)
    if not path_points:
        return

    # 4. Configuración de Usuario
    modes = ["Modo Normal (Incluir Todo)", "Modo Estricto (Solo Ruta)"]
    mode_sel = ui.get_selection("Seleccione Modo de Numeración:", modes)
    if not mode_sel:
        return
    strict_mode = "Estricto" in mode_sel

    try:
        r_str = ui.get_input(
            f"Radio de búsqueda (mts) [Default={DEFAULT_SEARCH_RADIUS}]:", default=str(DEFAULT_SEARCH_RADIUS))
        radius = float(r_str)
    except:
        radius = DEFAULT_SEARCH_RADIUS

    # 5. Procesamiento
    sorted_data = sort_blocks_unified(
        raw_data, path_points, radius, ui, strict_mode)

    if not sorted_data:
        ui.show_message(
            "Ningún poste cumple con los criterios de la ruta.", "warning")
        return

    # 6. Inserción Masiva
    try:
        acad.doc.Layers.Add(CAPA_DESTINO)
    except:
        pass

    msg_confirm = (
        f"RESUMEN DE OPERACIÓN:\n"
        f"---------------------\n"
        f"• Total a insertar: {len(sorted_data)} bloques\n"
        f"• Bloque Base: '{BLOQUE_A_INSERTAR}'\n"
        f"• Capa Destino: '{CAPA_DESTINO}'\n"
        f"• Escala: {ESCALA_BLOQUE}\n\n"
        f"¿Proceder con la inserción?"
    )

    if ui.confirm(msg_confirm):
        ui.progress_start(len(sorted_data), "Insertando y Numerando...")

        success_count = 0
        for i, blk in enumerate(sorted_data, 1):

            # Insertar
            ok = insert_and_update(
                acad, blk['X'], blk['Y'], blk.get('Z', 0.0), i, (i == 1))

            if ok:
                success_count += 1

            # Enriquecer datos para el reporte
            blk['Nuevo_Numero'] = i
            blk['Estado_Insercion'] = "OK" if ok else "ERROR"

            ui.progress_update(1)

        ui.progress_stop()
        acad.doc.Regen(1)
        ui.show_message(
            f"Terminado. Se insertaron {success_count} de {len(sorted_data)} bloques.", "success")

    # 7. Exportación "Nutrida"
    if ui.confirm("¿Generar Reporte Excel Detallado?"):
        if not sorted_data:
            return

        # Obtener TODAS las columnas posibles de todos los diccionarios
        all_keys = set()
        for item in sorted_data:
            all_keys.update(item.keys())
        all_keys = list(all_keys)

        # Definir orden prioritario para que se vea bonito
        priority_cols = ["Nuevo_Numero", "Nombre",
                         "Capa", "X", "Y", "Z", "Estado_Insercion"]

        # Columnas de atributos (las que empiezan con Attr_)
        attr_cols = sorted([k for k in all_keys if k.startswith("Attr_")])

        # Columnas restantes (cualquier otra cosa)
        other_cols = sorted(
            [k for k in all_keys if k not in priority_cols and k not in attr_cols])

        # Lista final ordenada
        final_columns = priority_cols + attr_cols + other_cols

        # Preparar datos
        export_data = []
        for item in sorted_data:
            row = [str(item.get(col, "")) for col in final_columns]
            export_data.append(row)

        show_export_menu(export_data, "Reporte_Numeracion_UTM",
                         ui, columns=final_columns)


if __name__ == "__main__":
    main()
