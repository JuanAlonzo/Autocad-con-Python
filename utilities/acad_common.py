"""
Modulo core.
Configuracion global y conexion critica con Autocad.
"""

import sys
from pyautocad import Autocad
from colorama import init, just_fix_windows_console
from rich.console import Console
from rich.progress import Progress

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
        if welcome_message:
            console.rule("[bold cyan]PYAUTOCAD[/bold cyan]")
            console.print(
                f"[bold cyan]{welcome_message}[/bold cyan]", justify="center")
            console.print(
                f"✓ Conectado a: [green]{doc_name}[/green]\n", justify="center")
        return acad
    except Exception as e:
        # Manejo de error fatal centralizado
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
