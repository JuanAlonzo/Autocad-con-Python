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


def _get_selection_set(
    acad, filter_dxf_codes, filter_dxf_values, name="MySelectionSet"
):
    """
    Helper privado para crear y filtrar SelectionSets de forma segura.
    Args:
        acad: Objeto Autocad (pyautocad o win32com wrapper).
        filter_dxf_codes (list): Lista de códigos DXF (ej. [0, 8] para Tipo y Capa).
        filter_dxf_values (list): Lista de valores (ej. ["INSERT", "MiCapa"]).
    """
    doc = acad.doc
    try:
        try:
            doc.SelectionSets.Item(name).Delete()
        except Exception:
            pass
        sset = doc.SelectionSets.Add(name)

        sset.Select(5, filter_dxf_codes, filter_dxf_values)
        return sset
    except Exception as e:
        print(f"Error creando SelectionSet: {e}")
        return []


def extract_text_data(acad, ui, layer_name, text_type="all"):
    """
    Extrae texto y coordenadas con SelectionSet.
    """
    if ui:
        ui.show_message(f"Analizando capa '{layer_name}' (Optimizado)...", "info")

    # Definir filtro
    dxf_codes = [8]  # Código 8 = Capa
    dxf_values = [layer_name]

    # Filtro de tipo
    if text_type == "text":
        dxf_codes.append(0)
        dxf_values.append("TEXT")
    elif text_type == "mtext":
        dxf_codes.append(0)
        dxf_values.append("MTEXT")
    else:  # all
        dxf_codes.append(0)
        dxf_values.append("TEXT,MTEXT")

    data = []

    try:
        # USANDO SELECTION SET
        sset = _get_selection_set(acad, dxf_codes, dxf_values, "SS_TEXTOS")
        count = sset.Count

        if ui:
            ui.progress_start(count, "Extrayendo textos...")

        for i in range(count):
            obj = sset.Item(i)
            try:
                # Nota: obj es un objeto COM nativo ahora
                coords = obj.InsertionPoint
                data.append((obj.TextString, coords[0], coords[1]))
            except Exception:
                pass

            if ui and i % 100 == 0:  # Actualizar UI cada 100 para no frenar
                ui.progress_update(100)

        sset.Delete()  # Limpieza importante

    except Exception as e:
        if ui:
            ui.show_message(f"Error extrayendo textos: {e}", "error")

    if ui:
        ui.progress_stop()
        ui.show_message(f"Se extrajeron {len(data)} textos.", "success")

    return data


def extract_block_data(acad, ui, layer_name=None):
    """
    Extrae propiedades utilizando SelectionSet.
    """
    blocks_data = []
    msg = f"capa '{layer_name}'" if layer_name else "todas las capas"
    if ui:
        ui.show_message(f"Buscando bloques en {msg}...", "info")

    # Filtros
    dxf_codes = [0]
    dxf_values = ["INSERT"]  # INSERT es el nombre interno de BlockReference

    if layer_name:
        dxf_codes.append(8)
        dxf_values.append(layer_name)

    try:
        sset = _get_selection_set(acad, dxf_codes, dxf_values, "SS_BLOQUES")
        count = sset.Count

        if ui:
            ui.progress_start(count, "Procesando atributos de bloques...")

        for i in range(count):
            try:
                obj = sset.Item(i)

                info = {}
                info["Handle"] = obj.Handle
                coords = obj.InsertionPoint
                info["X"] = round(coords[0], 4)
                info["Y"] = round(coords[1], 4)
                info["Z"] = round(coords[2], 4)

                try:
                    name = obj.EffectiveName
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

            if ui and i % 50 == 0:
                ui.progress_update(50)

        sset.Delete()

    except Exception as e:
        if ui:
            ui.show_message(f"Error procesando bloques: {e}", "error")

    if ui:
        ui.progress_stop()
        ui.show_message(f"Procesados {len(blocks_data)} bloques.", "success")

    return blocks_data


def get_polyline_points(acad, layer_name, ui=None):
    """
    Funcion Optimizada para encontrar puntos de polilineas.
    """
    path_points = []
    if ui:
        ui.show_message(f"Buscando ruta en '{layer_name}'...", "info")

    # Filtro: Pedimos todo lo que parezca una polilínea
    dxf_codes = [0, 8]
    dxf_values = ["LWPOLYLINE,POLYLINE", layer_name]

    try:
        sset = _get_selection_set(acad, dxf_codes, dxf_values, "SS_RUTA")

        if sset.Count == 0:
            if ui:
                ui.show_message("No se encontraron objetos de ruta.", "warning")
            sset.Delete()
            return []

        found_valid = False

        for i in range(sset.Count):
            obj = sset.Item(i)
            obj_type = obj.ObjectName

            # Lista blanca de objetos que SÍ tienen .Coordinates
            valid_types = ["AcDbPolyline", "AcDb2dPolyline", "AcDb3dPolyline"]

            if obj_type not in valid_types:
                ConnectionRefusedError

            try:
                coords = obj.Coordinates

                # Detectar tipo para saber el "step" (salto) de coordenadas
                # AcDbPolyline (LW) es 2D flat [x,y, x,y...] -> step 2
                # Heavy/3D Polyline es 3D flat [x,y,z, x,y,z...] -> step 3
                is_lw = obj_type == "AcDbPolyline"
                step = 2 if is_lw else 3

                for j in range(0, len(coords), step):
                    path_points.append((coords[j], coords[j + 1]))

                found_valid = True
                if ui:
                    ui.show_message(
                        f"Ruta válida: {obj_type} ({len(path_points)} pts)", "success"
                    )
                break  # Salimos del bucle.

            except Exception as e:
                print(f"Error leyendo coordenadas: {e}")
                continue

        sset.Delete()

        if not found_valid:
            if ui:
                ui.show_message(
                    "Se encontraron objetos, pero ninguno era una Polilínea válida.",
                    "error",
                )

    except Exception as e:
        if ui:
            ui.show_message(f"Error crítico al leer ruta: {e}", "error")

    return path_points
