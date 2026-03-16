import os
import sys
import socket
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DOMAINS_ALLOWED = [
    "HFC-01",
    "HFC-02",
    "HFC-03",
    "HFC-04",
    "HFC-05",
    "HFC-06",
    "HFC-07",
    "HFC-08",
    "HFC-09",
]

FECHA_EXPIRACION = datetime(2026, 12, 31)


def verificar_entorno() -> None:
    """
    Verifica si el entorno de ejecución es seguro y autorizado.
    Si falla, interrumpe el arranque y cierra el programa.
    """
    if datetime.now() > FECHA_EXPIRACION:
        msg = "NO DISPONIBLE.\nEsta versión del software ha caducado.\nPor favor contacte al administrador para renovar."
        logger.critical("Bloqueo de seguridad: Licencia expirada.")
        _bloquear_y_salir("Software Expirado", msg)

    dominio_actual = os.environ.get("USERDOMAIN", "").upper()
    pc_name = socket.gethostname().upper()

    logger.debug(f"Nombre del PC: {pc_name} | Dominio actual: {dominio_actual}")

    # Validación flexible (permite coincidencia por dominio de red o nombre de equipo)
    if dominio_actual not in DOMAINS_ALLOWED and pc_name not in DOMAINS_ALLOWED:
        msg = (
            f"⛔ ACCESO DENEGADO.\n\n"
            f"Este software tiene licencia exclusiva para uso corporativo interno.\n"
            f"Dominio detectado: {dominio_actual}\n"
            f"Equipo: {pc_name}"
        )
        logger.critical(
            f"Bloqueo de seguridad: Dominio/Equipo no autorizado ({dominio_actual} / {pc_name})."
        )
        _bloquear_y_salir("Acceso Denegado", msg)

    logger.info("Entorno de seguridad verificado: Autorizado.")


def _bloquear_y_salir(titulo: str, mensaje: str) -> None:
    """
    Muestra un mensaje crítico utilizando PySide6 y fuerza el cierre del sistema.
    """
    from PySide6.QtWidgets import QApplication, QMessageBox

    # Crear una instancia de QApplication temporal si aún no existe en el Hilo Principal
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle(titulo)
    msg_box.setText(mensaje)
    msg_box.exec()

    sys.exit(1)
