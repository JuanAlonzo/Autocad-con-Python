"""
Módulo IO: acad_io.py
Responsabilidad: Manejar TODA la entrada y salida de datos con el usuario.
Aquí viven los inputs, prints, tablas y validaciones visuales.
"""
import logging
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from .acad_common import console


def display_message(message, style='info'):
    """
    Muestra mensajes formateados en la consola.
    Styles: 'info', 'warning', 'error', 'success'.
    """
    clean_msg = message.replace("[bold]", "").replace("[/bold]", "")
    if style == 'error':
        logging.error(clean_msg)
    elif style == 'warning':
        logging.warning(clean_msg)
    elif style == 'success':
        logging.info(f"[EXITO] {clean_msg}")
    else:
        logging.info(clean_msg)

    styles = {
        'info': 'bold cyan',
        'warning': 'bold yellow',
        'error': 'bold red',
        'success': 'bold green',
        "title": "bold white on blue"
    }

    tag = styles.get(style, 'white')

    if style == 'error':
        console.print(f"❌[{tag}]{message}[/{tag}]")
    elif style == "success":
        console.print(f"✅ [{tag}]{message}[/{tag}]")
    elif style == "warning":
        console.print(f"⚠️  [{tag}]{message}[/{tag}]")
    else:
        console.print(f"[{tag}]{message}[/{tag}]")


def display_table(title, columns, rows):
    """
    Muestra una tabla formateada en la consola.

    Args:
        title: Título de la tabla.
        columns: Lista de nombres de columnas.
        rows: Lista de filas (cada fila es una lista de valores).
    """
    table = Table(title=title, style="cyan", header_style="bold magenta")

    for col in columns:
        table.add_column(col)

    for row in rows:
        table.add_row(*[str(item) for item in row])

    console.print(table)


def get_user_input(prompt_text, default=None):
    """Pide un texto simple al usuario."""
    return Prompt.ask(f"[cyan]{prompt_text}[/cyan]", default=default)


def get_confirmation(prompt_text="¿Desea continuar?"):
    """Devuelve True si el usuario dice 'y' o 's', False si dice 'n'."""
    return Confirm.ask(f"[yellow]{prompt_text}[/yellow]")


def get_selection_from_list(title, options_list, prompt_text="Seleccione una opción"):
    """
    Muestra una lista numerada y obliga al usuario a elegir un número válido.
    Retorna el valor seleccionado (string).
    """
    if not options_list:
        display_message("La lista está vacía.", "warning")
        return None

    console.print(f"\n[bold]{title}[/bold]")
    for i, option in enumerate(options_list, 1):
        console.print(f"  [green]{i}.[/green] {option}")

    # 2. Bucle de validación
    while True:
        choice = Prompt.ask(
            f"\n[cyan]{prompt_text} (1-{len(options_list)})[/cyan]")

        # Permitir salir
        if choice.lower() == 'salir':
            return None

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(options_list):
                return options_list[idx]

        display_message("Número inválido. Intente de nuevo.", "error")
