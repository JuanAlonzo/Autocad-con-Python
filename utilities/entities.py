import logging
from .cad_manager import cad

logger = logging.getLogger(__name__)


def get_blocks_by_layer(layer_name: str) -> list:
    """
    Extrae datos de bloques de una capa específica usando win32com puro.
    Devuelve una lista de diccionarios limpios.
    """
    if not cad.is_connected:
        logger.error("AutoCAD no está conectado.")
        return []

    blocks_data = []

    # Optimizamos usando un SelectionSet
    sset_name = "PythonBlockSelection"
    try:
        try:
            cad.doc.SelectionSets.Item(sset_name).Delete()
        except Exception:
            pass

        sset = cad.doc.SelectionSets.Add(sset_name)

        # Filtros DXF: Código 0 (Tipo) = INSERT, Código 8 (Capa) = layer_name
        dxf_codes = [0, 8]
        dxf_values = ["INSERT", layer_name]

        # Convertir a VARIANT para win32com
        filter_type = cad.variant_point(
            *dxf_codes
        )  # Reusamos para array de enteros (short)
        # Nota: Para filtros SelectionSet en win32com a veces se requiere un manejo específico de tipos,
        # por simplicidad aquí iteramos si el filtro falla, o usamos iteración directa si son pocos objetos.
        # Implementación robusta de iteración directa (más lento pero seguro):

        logger.info(f"Escaneando bloques en capa '{layer_name}'...")

        # Iteración directa sobre ModelSpace (Seguro y fácil de depurar)
        for obj in cad.msp:
            if obj.EntityName == "AcDbBlockReference" and obj.Layer == layer_name:
                data = {
                    "Handle": obj.Handle,
                    "Nombre": obj.Name,  # O EffectiveName si es dinámico
                    "Capa": obj.Layer,
                    "X": round(obj.InsertionPoint[0], 4),
                    "Y": round(obj.InsertionPoint[1], 4),
                    "Z": round(obj.InsertionPoint[2], 4),
                    "Rotacion": obj.Rotation,
                }

                # Manejo de Bloques Dinámicos
                try:
                    data["Nombre"] = obj.EffectiveName
                except Exception:
                    pass

                # Atributos
                if obj.HasAttributes:
                    for attrib in obj.GetAttributes():
                        tag = attrib.TagString
                        val = attrib.TextString
                        data[f"ATTR_{tag}"] = val

                blocks_data.append(data)

    except Exception as e:
        logger.error(f"Error extrayendo bloques: {e}")

    return blocks_data
