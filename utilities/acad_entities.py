"""
Módulo de Entidades: acad_entities.py
Responsabilidad: Extraer datos de objetos de AutoCAD (Bloques, Textos, Líneas).
Devuelve listas de diccionarios limpias, listas para ser exportadas o procesadas.
"""

import win32com.client


def get_model_space_safe(ui=None):
    """
    Obtiene el espacio modelo de AutoCAD de manera segura.
    """
    try:
        return win32com.client.GetActiveObject(
            "AutoCAD.Application"
        ).ActiveDocument.ModelSpace
    except Exception:
        try:
            return win32com.client.Dispatch(
                "AutoCAD.Application"
            ).ActiveDocument.ModelSpace
        except Exception as e:
            if ui:
                ui.show_message(f"Error al conectar con AutoCAD: {e}", "error")
            return None


def extract_text_data(acad, ui, layer_name, text_type="all"):
    """
    Extrae texto y coordenadas de una capa.
    text_type: 'all', 'text', 'mtext'
    Retorna: Lista de tuplas [(Texto, X, Y), ...]
    """
    msp = get_model_space_safe(ui)
    if not msp:
        return []

    if ui:
        ui.show_message(f"Analizando '{layer_name}' ...", "info")

    allowed_types = ["AcDbText", "AcDbMText"]

    data = []
    count = msp.Count

    if ui:
        ui.progress_start(count, "Extrayendo textos...")

    for i in range(count):
        try:
            obj = msp.Item(i)
            if obj.Layer == layer_name and obj.ObjectName in allowed_types:
                data.append(
                    (obj.TextString, obj.InsertionPoint[0], obj.InsertionPoint[1])
                )
        except Exception:
            pass
        if ui:
            ui.progress_update(1)

    if ui:
        ui.progress_stop()

    if ui:
        ui.show_message(f"Se extrajeron {len(data)} textos.", "success")
    return data


def extract_block_data(acad, ui, layer_name=None):
    """
    Extrae propiedades avanzadas de bloques.
    Si layer_name es None, extrae de TODAS las capas.
    Retorna: Lista de diccionarios con propiedades y atributos.
    """
    blocks_data = []
    msp = get_model_space_safe(ui)
    if not msp:
        return []

    msg = f"capa '{layer_name}'" if layer_name else "todas las capas"
    if ui:
        ui.show_message(f"Buscando bloques en {msg}...", "info")

    count = msp.Count

    # Procesamiento detallado
    if ui:
        ui.progress_start(count, "Procesando bloques...")

    for i in range(count):
        try:
            obj = msp.Item(i)
            if obj.ObjectName != "AcDbBlockReference":
                if ui:
                    ui.progress_update(1)
                continue

            if layer_name and obj.Layer != layer_name:
                if ui:
                    ui.progress_update(1)
                continue

            # Propiedades base
            info = {}

            info["Handle"] = obj.Handle
            coords = obj.InsertionPoint
            info["X"] = round(coords[0], 4)
            info["Y"] = round(coords[1], 4)
            info["Z"] = round(coords[2], 4)

            try:
                name = obj.EffectiveName if hasattr(obj, "EffectiveName") else obj.Name
            except Exception:
                name = obj.Name

            info["Nombre"] = name
            info["Capa"] = obj.Layer
            info["Rotacion"] = round(obj.Rotation, 4)

            if obj.HasAttributes:
                attribs = obj.GetAttributes()
                for att in attribs:
                    tag = att.TagString.upper()
                    val = att.TextString
                    info[f"Attr_{tag}"] = val

            blocks_data.append(info)
        except Exception:
            pass

        if ui:
            ui.progress_update(1)

    if ui:
        ui.progress_stop()

    if ui:
        ui.show_message(
            f"Procesados {len(blocks_data)} bloques correctamente.", "success"
        )
    return blocks_data
