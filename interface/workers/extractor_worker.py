import pythoncom
from PySide6.QtCore import QThread, Signal
from utilities.cad_manager import cad
from utilities import entities


class ExtractorWorker(QThread):
    progress_signal = Signal(int)
    log_signal = Signal(str)
    finished_signal = Signal(list)

    def __init__(self, entity_type, layer_arg):
        super().__init__()
        self.entity_type = entity_type
        self.layer_arg = layer_arg

    def run(self):
        pythoncom.CoInitialize()  # Inicializar COM para este hilo
        cad.connect()  # Asegurar conexión a AutoCAD en este hilo
        try:
            # Creamos una función anidada (callback) para despachar la señal de la GUI
            def emit_progress(pct):
                self.progress_signal.emit(pct)

            if self.entity_type == "bloques":
                data = entities.extract_blocks(
                    layer_name=self.layer_arg, progress_callback=emit_progress
                )
            elif self.entity_type == "textos":
                data = entities.extract_texts(
                    layer_name=self.layer_arg,
                    text_type="all",
                    progress_callback=emit_progress,
                )
            else:
                data = []

            self.finished_signal.emit(data)
        except Exception as e:
            self.log_signal.emit(f"Error crítico en hilo de extracción: {e}")
            self.finished_signal.emit([])
        finally:
            pythoncom.CoUninitialize()  # Limpiar COM al finalizar el hilo
