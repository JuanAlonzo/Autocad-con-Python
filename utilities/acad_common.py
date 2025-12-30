"""
Modulo core.
Configuracion global y conexion critica con Autocad.
"""

import sys
import os
import logging
from datetime import datetime
from pyautocad import Autocad
from colorama import init, just_fix_windows_console
from rich.console import Console
from rich.progress import Progress

log_dir = "logs"

if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir)
    except Exception as e:
        print(f"Error al crear carpeta de logs: {e}")

log_filename = os.path.join(
    log_dir, f"registro_autocad_{datetime.now().strftime('%Y-%m')}.log")

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

init()
just_fix_windows_console()
console = Console()
progress = Progress()


def require_autocad(welcome_message=None):
    """
    Intenta conectar a AutoCAD. 
    Si falla, muestra error y CIERRA el programa.
    Devuelve el objeto acad listo para usar.
    """
    try:
        acad = Autocad(create_if_not_exists=True)
        doc_name = acad.doc.Name  # Forzar acceso para verificar conexión
        logging.info(f"Inicio de sesión: {welcome_message}")
        logging.info(f"Conectado a AutoCAD: {doc_name}")
        if welcome_message:
            console.rule("[bold cyan]PYAUTOCAD[/bold cyan]")
            console.print(
                f"[bold cyan]{welcome_message}[/bold cyan]", justify="center")
            console.print(
                f"✓ Conectado a: [green]{doc_name}[/green]\n", justify="center")
        return acad
    except Exception as e:
        error_msg = f"ERROR FATAL: No hay conexión a AutoCAD. Detalles: {e}"
        logging.critical(error_msg)
        console.print(
            "\n[bold red]┌─────────────────────────────────────────┐[/bold red]")
        console.print(
            "[bold red]│  ERROR FATAL: No hay conexión a AutoCAD │[/bold red]")
        console.print(
            "[bold red]└─────────────────────────────────────────┘[/bold red]")
        console.print(f"[yellow]Error técnico: {e}[/yellow]")
        console.print("\n[bold white]Posibles soluciones:[/bold white]")
        console.print("1. Abre un dibujo en AutoCAD.")
        console.print("2. Sal de cualquier comando activo (Esc, Esc).")
        console.print("3. Si el error persiste, reinicia AutoCAD.")
        sys.exit(1)
