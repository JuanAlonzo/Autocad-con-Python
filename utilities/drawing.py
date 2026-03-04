import logging
from .cad_manager import cad

logger = logging.getLogger(__name__)


def insert_block_with_attributes(
    x: float,
    y: float,
    block_name: str,
    layer: str,
    scale: float = 1.0,
    rotation: float = 0.0,
    attributes: dict = None,
) -> bool:
    """
    Inserta un bloque en AutoCAD y actualiza sus atributos si se proporcionan.

    Args:
        x, y: Coordenadas de inserción.
        block_name: Nombre del bloque en la biblioteca del dibujo.
        layer: Capa de destino para el bloque.
        scale: Factor de escala uniforme (X, Y, Z).
        rotation: Rotación en radianes.
        attributes: Diccionario con Tags y Valores (ej: {"000": "15"}).
    """
    if not cad.is_connected:
        logger.error("AutoCAD no está conectado.")
        return False

    try:
        # Convertir punto a variante COM
        insertion_point = cad.variant_point(x, y, 0.0)

        # Insertar el bloque
        block_ref = cad.msp.InsertBlock(
            insertion_point, block_name, scale, scale, scale, rotation
        )
        block_ref.Layer = layer

        # Actualizar atributos si el bloque los tiene
        if attributes and block_ref.HasAttributes:
            for att in block_ref.GetAttributes():
                tag = att.TagString.upper()
                # Buscar coincidencia ignorando mayúsculas/minúsculas
                for k, v in attributes.items():
                    if k.upper() == tag:
                        att.TextString = str(v)
                        att.Update()
                        break

        return True

    except Exception as e:
        logger.error(f"Error insertando bloque '{block_name}' en ({x}, {y}): {e}")
        return False
