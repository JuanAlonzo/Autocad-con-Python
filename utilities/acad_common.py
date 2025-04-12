from pyautocad import Autocad
from colorama import init, just_fix_windows_console
from termcolor import colored
from rich.console import Console
from rich.table import Table
from utilities.acad_layers import is_layer_used

init()
just_fix_windows_console()
console = Console()


def initialized_autocad(message=None):
    """Inicializa la conexión con AutoCAD y devuelve el objeto Autocad."""
    try:
        acad = Autocad()

        try:
            _ = acad.app.ActiveDocument
            acad.prompt(colored(f"AutoCAD iniciado satisfactoriamente.\nNombre del plano: {acad.doc.Name}\n",
                        'cyan', attrs=['bold']))
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


def validate_layer(layer_name, layers_disponibles):
    """Valida si la capa existe en el documento actual."""
    if not layer_name.strip():
        return False, colored("El nombre de la capa no puede estar vacío.", 'red', attrs=['bold'])
    if layer_name not in layers_disponibles:
        return False, colored(f"La capa '{layer_name}' no existe en el documento actual.", 'red', attrs=['bold'])
    return True, ""


def get_valid_layer_input(prompt, layers, exit_keyword="salir"):
    """Solicita al usuario un nombre de capa y valida su existencia."""
    while True:
        # Mostrar lista de capas numeradas
        sorted_layers = sorted(layers)
        # Crear tabla Rich para mostrar las capas disponibles
        table = Table(title="Capas Disponibles",
                      show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Nombre de Capa", style="cyan")

        for i, layer in enumerate(sorted(layers), 1):
            table.add_row(str(i), layer)
        console.print(table)
        print()

        # Solicitar entrada al usuario
        layer_name = input(colored(
            f"{prompt} o escriba '{exit_keyword}' para salir: ", 'white', attrs=['bold'])).strip()
        # Verificar si quiere salir
        if layer_name.lower() == exit_keyword.lower():
            print(colored("Operación cancelada por el usuario.",
                  "yellow", attrs=["bold"]))
            return None

        # Verificar si ingresó un número
        if layer_name.isdigit():
            idx = int(layer_name) - 1
            if 0 <= idx < len(sorted_layers):
                return sorted_layers[idx]
            else:
                print(colored(f"Error: Número fuera de rango. Ingrese un número entre 1 y {len(sorted_layers)}.",
                              'red', attrs=['bold']))
                continue

        # Validar la capa
        is_valid, error = validate_layer(layer_name, layers)
        if is_valid:
            return layer_name
        print(f"Error: {error}")


def delete_layer(acad, layer_name, layers_disponibles):
    """Elimina una capa de AutoCAD si no está en uso.
    Solicita confirmación al usuario antes de eliminarla."""
    if layer_name not in layers_disponibles:
        print(colored(f"Error: La capa '{layer_name}' no existe.", 'red'))
        return False

    try:
        if is_layer_used(acad, layer_name):
            print(colored(
                f"La capa '{layer_name}' está en uso y no puede ser eliminada.", 'red'))
            return False

        confirm = input(colored(
            f"¿Estás seguro de eliminar la capa '{layer_name}'? (s/n): ",
            'yellow', attrs=['bold'])).lower().strip() == 's'

        if not confirm:
            print(colored("Operación cancelada por el usuario.", 'yellow'))
            return False

        acad.doc.Layers.Item(layer_name).Delete()
        print(colored(
            f"La capa '{layer_name}' se eliminó satisfactoriamente.", 'green'))
        return True
    except Exception as e:
        print(
            colored(f"No se puede eliminar la capa '{layer_name}': {e}", 'red'))
        return False


def display_text_coordinates(data, layer_name):
    """Muestra las coordenadas de los textos extraídos de la capa especificada."""
    print("Coordenadas obtenidas en la capa:", layer_name)
    print("-" * 50)
    for i, (content, x, y) in enumerate(data, 1):
        print(f"{i}. Texto: '{content}'\n   Coordenadas: X= {x:.4f}, Y= {y:.4f}")
    print("-" * 50)
    print(f"Total de objetos encontrados: {len(data)}")


def display_postes_with_numbers(asignaciones, capa_poste, numeros):
    """Muestra los postes ordenados según la capa de numeración más cercana."""
    print("Postes ordenados segun capa de numeracion más cercana:")
    print("-" * 50)
    for numero, x, y in asignaciones:
        print(f"Poste {numero} →\n   Coordenadas: X= {x:.4f}, Y= {y:.4f}")
    print("-" * 50)
    print(
        f'Conteo total de postes en la capa "{capa_poste}" encontrados: {len(numeros)}')
