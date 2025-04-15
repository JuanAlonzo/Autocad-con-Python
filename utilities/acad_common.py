"""
Modulo de utilidades para interactuar con AutoCAD.
Este módulo proporciona funciones para inicializar la conexión con AutoCAD,
validar capas, mostrar mensajes y colores, y obtener entradas del usuario.
El módulo utiliza la biblioteca pyautocad para interactuar con AutoCAD y rich para mostrar mensajes en la consola.
"""

from pyautocad import Autocad
from colorama import init, just_fix_windows_console
from termcolor import colored
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

init()
just_fix_windows_console()
console = Console()
progress = Progress()


def initialized_autocad(message=None):
    """Inicializa la conexión con AutoCAD y devuelve el objeto Autocad.
    Si no se puede conectar, muestra un mensaje de error y posibles soluciones."""
    try:
        acad = Autocad()

        try:
            _ = acad.app.ActiveDocument
            acad.prompt(colored(f"AutoCAD iniciado satisfactoriamente.\nNombre del plano: {acad.doc.Name}\n",
                        'white', attrs=['bold']))
            if message:
                print(f"\n{message}\n")
            return acad
        except Exception:
            raise ConnectionError("No se pudo conectar a AutoCAD.")

    except Exception as e:
        print(colored("\n┌─────────────────────────────────────────┐",
              'red', attrs=['bold']))
        print(colored("│  ERROR AL CONECTAR CON AUTOCAD          │",
              'red', attrs=['bold']))
        print(colored("└─────────────────────────────────────────┘",
              'red', attrs=['bold']))
        print(colored("\nPosibles soluciones:", 'yellow', attrs=['bold']))
        print(colored("1. Asegúrate de que AutoCAD esté abierto", 'yellow'))
        print(colored("2. Abre un documento/dibujo en AutoCAD", 'yellow'))
        print(colored("3. Ejecuta este script como administrador", 'yellow'))
        print(colored("4. Reinicia AutoCAD y vuelve a intentarlo", 'yellow'))
        print(colored("\nDetalles técnicos del error:", 'red'))
        print(f"{str(e)}")
        return None


def get_available_layers(acad):
    """Devuelve una lista de capas disponibles en el documento actual."""
    return [layer.Name for layer in acad.doc.Layers]


def is_layer_used(acad, layer_name):
    """Chequea si el layer esta siendo usado por algun objeto en el dibujo."""
    return any(obj.Layer == layer_name for obj in acad.iter_objects(limit=1000))


def validate_layer_name(layer_name, layers=None, should_exist=True, cad_doc=None):
    """Valida nombre de capa según varios criterios.

    Args:
        layer_name: Nombre de la capa a validar
        layers: Lista de capas existentes
        should_exist: Si True, valida que la capa exista. Si False, que no exista.
        cad_doc: Documento de AutoCAD (alternativa a layers)

    Returns:
        (bool, str): Tupla con resultado de validación y mensaje de error
    """
    # Validar que no esté vacío
    if not layer_name or layer_name.isspace():
        return False, colored("El nombre de la capa no puede estar vacío.", 'red', attrs=['bold'])

    # Si proporcionan cad_doc, obtener las capas de ahí
    if layers is None and cad_doc is not None:
        layers = [layer.Name for layer in cad_doc.Layers]

    # Si tenemos lista de capas, validar existencia según corresponda
    if layers is not None:
        layer_exists = layer_name in layers

        if should_exist and not layer_exists:
            return False, colored(f"La capa '{layer_name}' no existe en el documento actual.", 'red', attrs=['bold'])
        elif not should_exist and layer_exists:
            return False, display_message(f'Error: La capa "{layer_name}" ya existe.', style='error')

    return True, ""


def validate_layer(layer_name, layers_disponibles):
    """Valida si la capa existe en el documento actual."""
    return validate_layer_name(layer_name, layers_disponibles, should_exist=True)


def validate_new_layer_name(cad_doc, layer_name):
    """Valida si un nombre de capa es válido para crear una nueva capa."""
    return validate_layer_name(layer_name, cad_doc=cad_doc, should_exist=False)


def display_available_layers(layers):
    """Muestra una tabla con las capas disponibles numeradas."""
    # Mostrar lista de capas numeradas
    sorted_layers = sorted(layers)
    # Crear tabla Rich para mostrar las capas disponibles
    table = Table(title="Capas Disponibles",
                  show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Nombre de Capa", style="cyan")

    for i, layer in enumerate(sorted_layers, 1):
        table.add_row(str(i), layer)
    console.print(table)
    print()
    return sorted_layers


def get_valid_layer_input(prompt, layers, exit_keyword="salir", show_table=False):
    """Solicita al usuario un nombre de capa y valida su existencia."""
    sorted_layers = sorted(layers)

    if show_table:
        display_available_layers(sorted_layers)

    while True:
        # Solicitar entrada al usuario
        layer_name = input(colored(
            f"{prompt} o escriba '{exit_keyword}' para salir: ", 'white', attrs=['bold'])).strip()
        # Verificar si quiere salir
        if layer_name.lower() == exit_keyword.lower():
            display_message(
                "Operación cancelada por el usuario.", style="warning")
            return None

        # Verificar si ingresó un número
        if layer_name.isdigit():
            idx = int(layer_name) - 1
            if 0 <= idx < len(sorted_layers):
                return sorted_layers[idx]
            else:
                display_message(
                    f"Error: Número fuera de rango. Ingrese un número entre 1 y {len(sorted_layers)}.", style='error')
                continue

        # Validar la capa
        is_valid, error = validate_layer(layer_name, layers)
        if is_valid:
            return layer_name
        print(f"Error: {error}")


def display_message(message, style='info', use_rich=False, bold=True):
    """
    Muestra un mensaje en la consola con un estilo específico.
    Nota: Si el estilo es 'input', se solicita entrada al usuario. Para que se cumpla la condicion de input use_rich debe ser True.

    Args:
        message (str): El mensaje a mostrar
        style (str): Estilo del mensaje ('info', 'success', 'warning', 'error', 'input')
        use_rich (bool): Si es True, usa rich para mostrar el mensaje; si es input, solicita entrada
        bold (bool): Si es True, muestra el mensaje en negrita (Por defecto es True)

    Returns:
        str or None: Si use_rich es True y style es 'input', devuelve la entrada del usuario
    """
    style_colors = {
        'info': 'blue',
        'success': 'green',
        'warning': 'yellow',
        'init': 'cyan',
        'error': 'red',
        'input': 'white'
    }

    color = style_colors.get(style, 'white')
    attrs = ['bold'] if bold or style == 'input' else []

    if use_rich and style == 'input':
        user_input = input(colored(message, color, attrs=attrs))
        return "" if user_input is None else user_input
    elif use_rich:
        from rich.console import Console
        console = Console()
        if bold:
            console.print(message, style=f"bold {color}")
        else:
            console.print(message, style=color)
        return ""
    else:
        print(colored(message, color, attrs=attrs))
        return ""


def get_layer_color_dict():
    """Retorna un diccionario con los colores estándar de AutoCAD."""
    return {
        "1": "Rojo",
        "2": "Amarillo",
        "3": "Verde",
        "4": "Cian",
        "5": "Azul",
        "6": "Magenta",
        "7": "Blanco",
        "8": "Gris",
        "256": "Negro"
    }


def print_color_options(use_colors=True):
    """Muestra los colores disponibles con sus códigos."""

    color_dict = {
        "1": "Rojo",
        "2": "Amarillo",
        "3": "Verde",
        "4": "Cian",
        "5": "Azul",
        "6": "Magenta",
        "7": "Blanco",
        "8": "Gris",
        "256": "Negro"
    }

    color_map = {
        "Rojo": "red",
        "Amarillo": "yellow",
        "Verde": "green",
        "Cian": "cyan",
        "Azul": "blue",
        "Magenta": "magenta",
        "Blanco": "white",
        "Gris": "grey",
        "Negro": "grey"
    }

    print("\nColores disponibles:")
    print("-"*20)
    for code, color_name in color_dict.items():
        if use_colors and color_name in color_map:
            color = color_map[color_name]
            code_colored = colored(code, color, attrs=["bold"])
            separator_colored = colored(":", color, attrs=["bold"])
            name_colored = colored(color_name, color, attrs=["bold"])
        else:
            code_colored = code
            separator_colored = colored(":", 'white', attrs=['bold'])
            name_colored = color_name
        print(f"{code_colored}{separator_colored}{name_colored}")
    return color_dict
