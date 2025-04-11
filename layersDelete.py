# from pyautocad import Autocad
from colorama import init, Fore, Style, just_fix_windows_console
from termcolor import colored
from utilities.acad_common import initialized_autocad, get_available_layers, get_valid_layer_input
from utilities.acad_layers import is_layer_used

just_fix_windows_console()

init()


def delete_layer(acad, layer_name, layers_disponibles):
    if layer_name.lower() == "salir":
        print(colored("Finalizando el programa...", 'yellow', attrs=['bold']))
        return True

    if layer_name not in layers_disponibles:
        print(colored(f"Error: La capa '{layer_name}' no existe.", 'red'))
        return False

    try:
        if is_layer_used(acad, layer_name):
            print(colored(
                f"La capa '{layer_name}' está en uso y no puede ser eliminada.", 'red'))
            return False
        else:
            acad.doc.Layers.Item(layer_name).Delete()
            print(colored(
                f"La capa '{layer_name}' se eliminó satisfactoriamente.", 'green'))
            return True
    except Exception as e:
        print(
            colored(f"No se puede eliminar la capa '{layer_name}': {e}", 'red'))
        return False


def list_and_delete_layers():
    acad = initialized_autocad(
        colored("Programa para eliminar capas en AutoCAD", 'cyan', attrs=['bold']))
    if not acad:
        return

        # Lista las capas existentes
    layers_disponibles = get_available_layers(acad)
    print(colored("CAPAS EXISTENTES:", 'blue', attrs=['bold']))
    for layer in layers_disponibles:
        print(colored(f"- {layer}", 'blue'))

    while True:
        layer_to_delete = input(
            "\nSelecciona la capa a eliminar (escribe 'salir' para finalizar): ")

        delete_layer(acad, layer_to_delete, layers_disponibles)

        if layer_to_delete.lower() == "salir":
            break


if __name__ == "__main__":
    list_and_delete_layers()
