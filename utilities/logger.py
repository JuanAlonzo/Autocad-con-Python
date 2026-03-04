import logging
import os
from datetime import datetime


def setup_logger():
    """
    Configura el sistema de logging global de la aplicación.
    Debe llamarse una sola vez al inicio del programa (en main.py).
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_filename = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y-%m')}.log")

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler para escribir en el archivo
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Handler para la consola (útil para ti mientras programas)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    # Configurar el logger raíz (root)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Evitar duplicar handlers si la función se llama accidentalmente más de una vez
    if not root_logger.handlers:
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    return root_logger
