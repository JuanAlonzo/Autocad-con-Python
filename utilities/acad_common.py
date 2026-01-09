"""
Modulo core.
Configuracion global y conexion critica con Autocad.
"""

import sys
import os
import logging
from datetime import datetime
from pyautocad import Autocad

log_dir = "logs"

if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir)
    except Exception:
        pass

log_filename = os.path.join(
    log_dir, f"registro_autocad_{datetime.now().strftime('%Y-%m')}.log")

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)


def require_autocad(ui=None):
    """
    Intenta conectar a AutoCAD. 
    Si recibe ui, usa esa interfaz para mostrar mensajes.
    Devuelve el objeto acad listo para usar.
    """
    try:
        acad = Autocad(create_if_not_exists=True)
        doc_name = acad.doc.Name
        logging.info(f"Conectado a AutoCAD: {doc_name}")
        if ui:
            ui.show_message(f"Conectado a: {doc_name}", "success")
        return acad

    except Exception as e:
        error_msg = f"ERROR FATAL: No hay conexión a AutoCAD. Detalles: {e}"
        logging.critical(error_msg)
        if ui:
            ui.show_message("ERROR FATAL: No hay conexión a AutoCAD.", "error")
            ui.show_message("Soluciones: ", "warning")
            ui.show_message("1. Abre un dibujo en AutoCAD.", "warning")
            ui.show_message(
                "2. Sal de cualquier comando activo (Esc, Esc).", "warning")
            ui.show_message(
                "3. Si el error persiste, reinicia AutoCAD.", "warning")
        else:
            print(error_msg)
        sys.exit(1)
