import logging
from .cad_manager import cad

logger = logging.getLogger(__name__)


def extract_blocks(layer_name: str = None, layer_prefix: str = None) -> list:
    """
    Extrae datos de bloques (INSERT) iterando sobre el ModelSpace con win32com.
    Opcionalmente filtra por capa.
    Devuelve una lista de diccionarios con la información y atributos.
    Permite filtrar por capa exacta (layer_name) o por prefijo (layer_prefix).
    """
    if not cad.is_connected:
        logger.error("AutoCAD no está conectado.")
        return []

    blocks_data = []

    if layer_prefix:
        logger.info(f"Escaneando bloques en capas que inicien con '{layer_prefix}'...")
    elif layer_name:
        logger.info(f"Escaneando bloques en la capa '{layer_name}'...")
    else:
        logger.info("Escaneando bloques en todas las capas...")

    try:
        for obj in cad.msp:
            if obj.EntityName == "AcDbBlockReference":
                if layer_name and obj.Layer.upper() != layer_name.upper():
                    continue
                if layer_prefix and not obj.Layer.upper().startswith(
                    layer_prefix.upper()
                ):
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

        logger.info(f"Se extrajeron {len(blocks_data)} bloques exitosamente.")

    except Exception as e:
        logger.error(f"Error crítico extrayendo bloques: {e}")

    return blocks_data


def extract_texts(layer_name: str = None, text_type: str = "all") -> list:
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
        for obj in cad.msp:
            if obj.EntityName in valid_types:
                if layer_name and obj.Layer != layer_name:
                    continue

                data = {
                    "Handle": obj.Handle,
                    "Texto": obj.TextString,
                    "Capa": obj.Layer,
                    "X": round(obj.InsertionPoint[0], 4),
                    "Y": round(obj.InsertionPoint[1], 4),
                    "Z": round(obj.InsertionPoint[2], 4),
                    "Tipo": obj.EntityName,
                }
                texts_data.append(data)

        logger.info(f"Se extrajeron {len(texts_data)} textos exitosamente.")

    except Exception as e:
        logger.error(f"Error crítico extrayendo textos: {e}")

    return texts_data
