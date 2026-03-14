import logging
from utilities.cad_manager import cad
from .extractor_ctrl import ExtractorController
from .numeracion_ctrl import NumeracionController
from .capas_ctrl import CapasController


class MainController:
    def __init__(self):
        self.logger = logging.getLogger("MainController")
        self.view = None

        # Instanciación de módulos desacoplados
        self.extractor = ExtractorController(self)
        self.numeracion = NumeracionController(self)
        self.capas = CapasController(self)

    def set_view(self, view):
        self.view = view
        # Inyección de las sub-vistas específicas a cada controlador
        self.extractor.set_view(view.tab_extractor)
        self.numeracion.set_view(view.tab_numeracion)
        self.capas.set_view(view.tab_capas)

    def log(self, msg: str):
        self.logger.info(msg)
        if self.view:
            self.view.append_log(msg)

    def connect_to_cad(self):
        self.log("Intentando conectar a AutoCAD...")
        if cad.connect():
            self.view.update_connection_status(True, cad.doc.Name)
            self.log(f"Conexión exitosa con el documento: {cad.doc.Name}")
        else:
            self.view.update_connection_status(False, "")
            self.log("Error: No se detectó ninguna instancia de AutoCAD abierta.")
