import pythoncom
from PySide6.QtCore import QThread, Signal
from utilities.cad_manager import cad
from utilities import layers


class CapasWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal(dict)

    def __init__(self, action: str, params: dict = None):
        super().__init__()
        self.action = action
        self.params = params or {}

    def run(self):
        pythoncom.CoInitialize()
        cad.connect()
        try:
            if self.action == "listar":
                self.log_signal.emit("Escaneando el estado de uso de las capas...")
                data = layers.get_layers_status()
                self.finished_signal.emit({"action": "listar", "data": data})

            elif self.action == "crear":
                nombre = self.params.get("nombre")
                color = self.params.get("color")
                grosor = self.params.get("grosor")
                success = layers.ensure_layer(nombre, color, grosor)
                self.finished_signal.emit(
                    {"action": "crear", "success": success, "nombre": nombre}
                )

            elif self.action == "eliminar":
                nombre = self.params.get("nombre")
                success, msg = layers.delete_layer(nombre)
                if not success:
                    self.log_signal.emit(f"Fallo al eliminar: {msg}")
                self.finished_signal.emit(
                    {"action": "eliminar", "success": success, "nombre": nombre}
                )

        except Exception as e:
            self.log_signal.emit(f"Error crítico en CapasWorker ({self.action}): {e}")
            self.finished_signal.emit({"action": "error"})

        finally:
            pythoncom.CoUninitialize()
