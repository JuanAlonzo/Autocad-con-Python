from utilities.cad_manager import cad
from utilities import entities
import logging


class Controller:
    def __init__(self):
        self.view = None  # Se asigna después
        self.logger = logging.getLogger("Controller")

    def set_view(self, view):
        self.view = view

    def connect_to_cad(self):
        if cad.connect():
            self.view.update_status(True, cad.doc.Name)
            self.view.append_log(f"Conexión exitosa: {cad.doc.Name}")
        else:
            self.view.update_status(False, "")
            self.view.append_log("Error: No se encontró AutoCAD abierto.")

    def scan_blocks(self):
        # Ejemplo de uso de utilities
        if not cad.is_connected:
            self.view.append_log("Error: Conéctate primero a AutoCAD.")
            return

        # Aquí podrías lanzar un InputDialog para pedir la capa
        layer = "POSTES_PROYECTO"  # Hardcoded por ahora para ejemplo
        self.view.append_log(f"Escaneando capa {layer}...")

        blocks = entities.get_blocks_by_layer(layer)
        self.view.append_log(f"Encontrados {len(blocks)} bloques.")
