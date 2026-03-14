from PySide6.QtWidgets import QMessageBox
from utilities.cad_manager import cad
from interface.workers.capas_worker import CapasWorker


class CapasController:
    def __init__(self, main_controller):
        self.main = main_controller
        self.view = None
        self.worker = None

    def set_view(self, view):
        self.view = view

    def _check_connection(self) -> bool:
        cad.connect()
        if not cad.is_connected:
            self.main.log("ERROR: AutoCAD no está conectado.")
            return False
        return True

    def cargar_capas(self):
        if not self._check_connection():
            return

        self.view.set_ui_state(False)
        self.worker = CapasWorker("listar")
        self.worker.log_signal.connect(self.main.log)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def crear_capa(self):
        datos = self.view.get_datos_creacion()
        nombre = datos["nombre"]

        if not nombre:
            self.main.log("Aviso: Debes ingresar un nombre para la capa.")
            return

        if not self._check_connection():
            return

        self.view.set_ui_state(False)
        self.worker = CapasWorker("crear", datos)
        self.worker.log_signal.connect(self.main.log)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def eliminar_capa(self):
        nombre = self.view.get_capa_seleccionada()
        if not nombre:
            self.main.log("Aviso: Selecciona una capa de la tabla primero.")
            return

        reply = QMessageBox.question(
            self.view,
            "Confirmar Eliminación",
            f"¿Deseas eliminar permanentemente la capa '{nombre}'?\n\nSolo se procesará si está vacía.",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        if not self._check_connection():
            return

        self.view.set_ui_state(False)
        self.worker = CapasWorker("eliminar", {"nombre": nombre})
        self.worker.log_signal.connect(self.main.log)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def on_worker_finished(self, result: dict):
        self.view.set_ui_state(True)
        action = result.get("action")

        if action == "listar":
            self.view.poblar_tabla(result.get("data", []))
            self.main.log("Escaneo de capas finalizado exitosamente.")

        elif action == "crear":
            if result.get("success"):
                self.main.log(f"Operación exitosa en la capa '{result.get('nombre')}'.")
                self.cargar_capas()

        elif action == "eliminar":
            if result.get("success"):
                self.cargar_capas()
