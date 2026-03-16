import sys
import logging
from PySide6.QtWidgets import QApplication
from utilities.logger import setup_logger
from utilities.config import SETTINGS
from utilities.security import verificar_entorno
from interface.views.main_window import MainWindow
from interface.controllers.main_controller import MainController


def main():
    """Inicializacion principal del programa."""
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("Iniciando AutoCAD Tools")

    verificar_entorno()
    SETTINGS.load_from_file()

    app = QApplication(sys.argv)

    # Inyección de dependencias (MVC)
    controller = MainController()
    window = MainWindow(controller)
    controller.set_view(window)

    window.show()
    logger.info("Aplicación lista para usar.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
