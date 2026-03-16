import logging
from .cad_manager import cad

logger = logging.getLogger(__name__)


def extract_blocks(layer_name: str = None, progress_callback=None) -> list:
    """
    Extrae datos de bloques (INSERT) iterando sobre el ModelSpace con win32com.
    Opcionalmente filtra por capa.
    Devuelve una lista de diccionarios con la información y atributos.
    """
    if not cad.is_connected:
        logger.error("AutoCAD no está conectado.")
        return []

    blocks_data = []

    if layer_name:
        logger.info(f"Escaneando bloques en la capa '{layer_name}'...")
    else:
        logger.info("Escaneando bloques en todas las capas...")

    try:
        total_objects = cad.msp.Count
        for i in range(total_objects):
            if progress_callback and i % 100 == 0:
                progress_callback(int((i / total_objects) * 100))

            try:
                obj = cad.msp.Item(i)
                entity_name = obj.EntityName
            except Exception:
                continue

            if entity_name == "AcDbBlockReference":
                try:
                    if layer_name and obj.Layer.upper() != layer_name.upper():
                        continue

                    # Extraer propiedades base
                    data = {
                        "Handle": obj.Handle,
                        "Nombre": obj.Name,
                        "Capa": obj.Layer,
                        "X": round(obj.InsertionPoint[0], 4),
                        "Y": round(obj.InsertionPoint[1], 4),
                        "Z": round(obj.InsertionPoint[2], 4),
                        "Rotacion": round(obj.Rotation, 4),
                    }

                    # Manejo de Bloques Dinámicos (en EffectiveName)
                    try:
                        data["Nombre"] = obj.EffectiveName
                    except AttributeError:
                        pass  # Si no tiene la propiedad exacta, se queda con obj.Name

                    # Extracción de Atributos
                    if obj.HasAttributes:
                        for attrib in obj.GetAttributes():
                            tag = attrib.TagString
                            val = attrib.TextString
                            data[f"Attr_{tag}"] = val

                    blocks_data.append(data)
                except Exception:
                    continue

        if progress_callback:
            progress_callback = 100

        logger.info(f"Se extrajeron {len(blocks_data)} bloques exitosamente.")

    except Exception as e:
        logger.error(f"Error crítico extrayendo bloques: {e}")

    return blocks_data


def extract_texts(
    layer_name: str = None, text_type: str = "all", progress_callback=None
) -> list:
    """
    Extrae textos simples (TEXT) y/o múltiples (MTEXT).
    Devuelve una lista de diccionarios listos para Pandas/Excel o para cálculos lógicos.
    """
    if not cad.is_connected:
        logger.error("AutoCAD no está conectado.")
        return []

    texts_data = []
    logger.info(f"Escaneando textos (tipo: {text_type}) en la capa '{layer_name}'...")

    # Definir qué entidades vamos a buscar
    valid_types = []
    if text_type in ["text", "all"]:
        valid_types.append("AcDbText")
    if text_type in ["mtext", "all"]:
        valid_types.append("AcDbMText")

    try:
        total_objects = cad.msp.Count
        for i in range(total_objects):
            if progress_callback and i % 100 == 0:
                progress_callback(int((i / total_objects) * 100))

            try:
                obj = cad.msp.Item(i)
                entity_name = obj.EntityName
            except Exception:
                continue

            if entity_name in valid_types:
                try:
                    if layer_name and obj.Layer.upper() != layer_name.upper():
                        continue

                    data = {
                        "Handle": obj.Handle,
                        "Texto": obj.TextString,
                        "Capa": obj.Layer,
                        "X": round(obj.InsertionPoint[0], 4),
                        "Y": round(obj.InsertionPoint[1], 4),
                        "Z": round(obj.InsertionPoint[2], 4),
                        "Tipo": entity_name,
                    }
                    texts_data.append(data)
                except Exception:
                    continue

        if progress_callback:
            progress_callback(100)

        logger.info(f"Se extrajeron {len(texts_data)} textos exitosamente.")

    except Exception as e:
        logger.error(f"Error crítico extrayendo textos: {e}")

    return texts_data


def extract_network_lines(layers_dict: dict):
    """
    Extrae segmentos de red (AcDbLine y AcDbPolyline) basándose en un diccionario de capas.
    Devuelve una lista de tuplas con los puntos de inicio y fin: [((x1, y1), (x2, y2)), ...]
    """
    if not cad.is_connected:
        logger.error("AutoCAD no está conectado.")
        return []

    segments = []
    # Convertimos los valores del diccionario a mayúsculas para evitar errores de tipeo
    valid_layers = [layer_name.upper() for layer_name in layers_dict.values()]
    logger.info(f"Escaneando red física en las capas: {valid_layers}")

    try:
        total_objects = cad.msp.Count
        for i in range(total_objects):
            try:
                obj = cad.msp.Item(i)
                entity_name = obj.EntityName
                layer_name = obj.Layer
            except Exception:
                continue

            if layer_name.upper() in valid_layers:
                continue

            try:
                # Si es una línea simple
                if entity_name == "AcDbLine":
                    p1 = (round(obj.StartPoint[0], 4), round(obj.StartPoint[1], 4))
                    p2 = (round(obj.EndPoint[0], 4), round(obj.EndPoint[1], 4))
                    segments.append((p1, p2))

                # Si es una polilínea (Cable continuo)
                elif entity_name in ["AcDbPolyline", "AcDb2dPolyline"]:
                    coords = obj.Coordinates
                    step = 2 if entity_name == "AcDbPolyline" else 3

                    # Iterar por los vértices para crear segmentos individuales
                    for j in range(0, len(coords) - step, step):
                        p1 = (round(coords[j], 4), round(coords[j + 1], 4))
                        p2 = (
                            round(coords[j + step], 4),
                            round(coords[j + step + 1], 4),
                        )
                        segments.append((p1, p2))
            except Exception:
                continue

        logger.info(f"Se extrajeron {len(segments)} segmentos de red.")
    except Exception as e:
        logger.error(f"Error crítico extrayendo red: {e}")

    return segments
