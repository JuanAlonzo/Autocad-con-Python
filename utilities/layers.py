import logging
from .cad_manager import cad

logger = logging.getLogger(__name__)


def get_all_layers() -> list:
    """Devuelve una lista ordenada alfabéticamente de todas las capas del dibujo."""
    if not cad.is_connected:
        return []
    try:
        return sorted([layer.Name for layer in cad.doc.Layers])
    except Exception as e:
        logger.error(f"Error obteniendo lista de capas: {e}")
        return []


def is_layer_used(layer_name: str) -> bool:
    """Verifica si una capa está siendo utilizada por alguna entidad en el dibujo."""
    if not cad.is_connected:
        return False
    try:
        total_objects = cad.msp.Count
        for i in range(total_objects):
            obj = cad.msp.Item(i)
            if hasattr(obj, "Layer") and obj.Layer.upper() == layer_name.upper():
                return True
        return False
    except Exception as e:
        logger.error(f"Error verificando uso de capa '{layer_name}': {e}")
        return True  # Asumimos que está en uso para evitar eliminarla por error


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


def delete_layer(layer_name: str) -> tuple:
    """
    Intenta eliminar una capa de AutoCAD.
    Retorna una tupla: (bool_exito, str_mensaje_error)
    """
    if not cad.is_connected:
        return False, "AutoCAD no está conectado."

    if layer_name in ["0", "Defpoints"]:
        return (
            False,
            "No se pueden eliminar las capas base del sistema (0 o Defpoints).",
        )

    if is_layer_used(layer_name):
        return (
            False,
            f"La capa '{layer_name}' contiene objetos y no puede ser eliminada.",
        )

    try:
        cad.doc.Layers.Item(layer_name).Delete()
        logger.info(f"Capa '{layer_name}' eliminada exitosamente.")
        return True, ""
    except Exception as e:
        error_msg = f"Error de AutoCAD al eliminar '{layer_name}': {e}"
        logger.error(error_msg)
        return False, error_msg


def get_layers_status() -> list:
    """
    Realiza un escaneo completo y devuelve una lista de diccionarios con el estado de cada capa.
    Útil para poblar tablas en la interfaz gráfica.
    """
    if not cad.is_connected:
        return []

    all_layers = get_all_layers()
    used_layers = set()

    try:
        total_objects = cad.msp.Count
        for i in range(total_objects):
            obj = cad.msp.Item(i)
            if hasattr(obj, "Layer"):
                used_layers.add(obj.Layer.upper())

        status_list = []
        for layer in all_layers:
            en_uso = layer.upper() in used_layers
            status_list.append(
                {"Nombre": layer, "Estado": "En Uso" if en_uso else "Vacía"}
            )
        return status_list
    except Exception as e:
        logger.error(f"Error escaneando estado de capas: {e}")
        return []
