from pyautocad import Autocad, APoint
from colorama import Fore, Style
from termcolor import colored
from .acad_common import initialized_autocad, get_available_layers


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


def print_color_options(color_dict=None):
    """Muestra los colores disponibles con sus códigos."""
    if color_dict is None:
        color_dict = get_layer_color_dict()

    print("\nColores disponibles:")
    print("-"*20)
    for code, color in color_dict.items():
        print(f"{code}: {color}")


def get_valid_layer_name(cad_doc):
    """Solicita un nombre y valida si la capa ya existe."""
    while True:
        layer_name = input(colored(
            "\nIntroduce el nombre de la capa a crear (o 'salir' para terminar): ", 'white', attrs=['bold']))

        if layer_name.lower() == 'salir':
            print(colored("\nSaliendo del programa...", 'yellow'))
            return None

        if not layer_name or layer_name.isspace():
            print(colored("El nombre de la capa no puede estar vacío.", 'red'))
            continue

        for layer in cad_doc.Layers:
            if layer.Name == layer_name:
                print(
                    colored(f'Error: La capa "{layer_name}" ya existe.', 'white', 'on_red'))
                break
        else:
            return layer_name


def get_valid_color():
    """Solicita y valida un código de color entre 1 y 255."""
    while True:
        color = input(
            colored("Introduce el color de la capa (1-255): ", 'white', attrs=['bold']))
        try:
            color_num = int(color)
            if 1 <= color_num <= 255:
                return color_num
            else:
                print(colored("El número de color debe estar entre 1 y 255.", 'red'))
        except ValueError:
            print(colored("Por favor, introduce un número válido para el color.", 'red'))


def create_layer(cad_doc, layer_name, color_num, color_dict=None):
    """Crea una nueva capa con el nombre y color especificados."""
    if color_dict is None:
        color_dict = get_layer_color_dict()

    new_layer = cad_doc.Layers.Add(layer_name)
    new_layer.Color = color_num
    color_name = color_dict.get(str(color_num), "Color no definido")
    print(colored(
        f'La capa "{layer_name}" ha sido creada con el color {color_num} ({color_name}).', 'green'))
    return new_layer


def is_layer_used(acad, layer_name):
    """Chequea si el layer esta siendo usado por algun objeto en el dibujo."""
    return any(obj.Layer == layer_name for obj in acad.iter_objects(limit=1000))


def list_layers(acad, show_unused=True, show_used=True):
    """Lista las capas disponibles del dibujo, con opción de mostrar usadas o no usadas."""
    # Obtener todas las capas
    layers = acad.doc.Layers
    layer_names = [layer.Name for layer in layers]

    # Verificar qué capas están en uso
    used_layers = set()
    all_objects = acad.iter_objects()

    for obj in all_objects:
        try:
            if hasattr(obj, "Layer"):
                used_layers.add(obj.Layer)
        except:
            pass

    results = {
        "used": sorted(used_layers) if show_used else [],
        "unused": sorted(set(layer_names) - used_layers) if show_unused else [],
        "all": layer_names,
        "counts": {
            "used": len(used_layers),
            "unused": len(set(layer_names) - used_layers),
            "total": len(layer_names)
        }
    }

    return results
