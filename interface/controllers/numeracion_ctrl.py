from utilities.cad_manager import cad
from interface.workers.numeracion_worker import NumeracionWorker


class NumeracionController:
    def __init__(self, main_controller):
        self.main = main_controller
        self.view = None
        self.worker = None

    def set_view(self, view):
        self.view = view

    def ejecutar_numeracion(self):
        if not cad.is_connected:
            self.main.log("ERROR: AutoCAD no está conectado.")
            return

        cfg = self.view.get_numeracion_config()
        self.main.log("--- INICIANDO PROCESO DE NUMERACIÓN ---")

        self.view.set_execution_state(is_running=True)
        self.worker = NumeracionWorker(cfg)

        self.worker.progress_signal.connect(self.view.update_progress)
        self.worker.log_signal.connect(self.main.log)
        self.worker.finished_signal.connect(self.on_numeracion_finished)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def on_numeracion_finished(self, success: bool):
        self.view.set_execution_state(is_running=False)
