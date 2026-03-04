import logging
from .cad_manager import cad

logger = logging.getLogger(__name__)


def ensure_layer(layer_name: str, color: int = 7, lineweight: int = -3) -> bool:
    """
    Verifica si una capa existe. Si no existe, la crea con el color especificado.
    Si ya existe, opcionalmente actualiza su color.
    """
    if not cad.is_connected:
        return False

    try:
        # Intenta acceder a la capa existente
        layer = cad.doc.Layers.Item(layer_name)
        layer.Color = color
        return True
    except Exception:
        # Si lanza excepción, y la capa no existe; la creamos
        try:
            new_layer = cad.doc.Layers.Add(layer_name)
            new_layer.Color = color
            try:
                new_layer.Lineweight = lineweight
            except Exception:
                pass

            logger.info(f"Capa '{layer_name}' creada (Color: {color}).")
            return True
        except Exception as e:
            logger.error(f"Error crítico creando la capa '{layer_name}': {e}")
            return False


def get_all_layers() -> list:
    """Devuelve una lista ordenada alfabéticamente de todas las capas del dibujo."""
    if not cad.is_connected:
        return []
    try:
        return sorted([layer.Name for layer in cad.doc.Layers])
    except Exception as e:
        logger.error(f"Error obteniendo lista de capas: {e}")
        return []
