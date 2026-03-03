import sys
import logging
from PySide6.QtWidgets import QApplication
from interface.view import MainWindow
from interface.controller import Controller

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    app = QApplication(sys.argv)

    # Inyección de dependencias (MVC)
    controller = Controller()
    window = MainWindow(controller)
    controller.set_view(window)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
