import pandas as pd
from utilities.cad_manager import cad
from interface.workers.extractor_worker import ExtractorWorker


class ExtractorController:
    def __init__(self, main_controller):
        self.main = main_controller
        self.view = None
        self.current_data = []
        self.worker = None

    def set_view(self, view):
        self.view = view

    def extract_data(self, entity_type: str):
        if not cad.is_connected:
            self.main.log("Error: Debes conectar a AutoCAD primero.")
            return

        layer = self.view.get_layer_input()
        layer_arg = layer if layer else None
        msg_capa = f"la capa '{layer}'" if layer else "todas las capas"

        self.main.log(f"Iniciando extracción de {entity_type} en {msg_capa}...")
        self.view.set_extraction_state(True)

        self.worker = ExtractorWorker(entity_type, layer_arg)
        self.worker.progress_signal.connect(self.view.update_progress)
        self.worker.log_signal.connect(self.main.log)
        self.worker.finished_signal.connect(self.on_extraction_finished)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def on_extraction_finished(self, data):
        self.current_data = data
        self.main.log(
            f"Extracción completada: {len(self.current_data)} elementos encontrados."
        )
        self.view.populate_table(self.current_data)
        self.view.set_extraction_state(False)

    def export_to_excel(self):
        if not self.current_data:
            self.main.log("No hay datos para exportar.")
            return

        file_path = self.view.show_save_dialog()
        if not file_path:
            return

        try:
            self.main.log(f"Exportando {len(self.current_data)} filas a Excel...")
            df = pd.DataFrame(self.current_data)
            df.to_excel(file_path, index=False)
            self.main.log(f"Excel guardado exitosamente en: {file_path}")
        except Exception as e:
            self.main.log(f"Error al guardar Excel: {e}")
