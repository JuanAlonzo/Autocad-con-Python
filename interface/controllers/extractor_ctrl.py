import csv
from typing import TYPE_CHECKING
from utilities.cad_manager import cad
from interface.workers.extractor_worker import ExtractorWorker

if TYPE_CHECKING:
    from interface.controllers.main_controller import MainController


class ExtractorController:
    def __init__(self, main_controller: "MainController"):
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

    def export_to_csv(self):
        if not self.current_data:
            self.main.log("No hay datos para exportar.")
            return

        file_path = self.view.show_save_dialog()
        if not file_path:
            return

        try:
            self.main.log(f"Exportando {len(self.current_data)} filas a CSV...")

            primer_elemento = self.current_data[0]

            if isinstance(primer_elemento, dict):
                headers = []
                for row in self.current_data:
                    if isinstance(row, dict):
                        for key in row.keys():
                            if key not in headers:
                                headers.append(key)

                with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=headers)
                    writer.writeheader()
                    for row in self.current_data:
                        if isinstance(row, dict):
                            writer.writerow(row)
            else:
                # Flujo para listas o tuplas simples (Ej: Coordenadas de red)
                with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    for row in self.current_data:
                        # Si es una tupla anidada ej: ((x1,y1), (x2,y2)), la aplanamos
                        if isinstance(row, (list, tuple)):
                            # Aplanar un nivel si es necesario, o guardarla cruda
                            fila_plana = []
                            for item in row:
                                if isinstance(item, (list, tuple)):
                                    fila_plana.extend(item)
                                else:
                                    fila_plana.append(item)
                            writer.writerow(fila_plana)
                        else:
                            writer.writerow([row])

            self.main.log(f"CSV guardado exitosamente en: {file_path}")
        except Exception as e:
            self.main.log(f"Error al guardar CSV: {str(e)}")
