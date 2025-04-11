# from pyautocad import Autocad
from colorama import init, just_fix_windows_console
from termcolor import colored
from utilities.acad_common import initialized_autocad
from utilities.acad_layers import (
    print_color_options, get_valid_layer_name,
    get_valid_color, create_layer, get_layer_color_dict
)

just_fix_windows_console()
init()


def main():
    """Función principal del programa."""
    cad = initialized_autocad(
        colored("Programa para crear nuevas capas en AutoCAD", 'cyan'))
    if not cad:
        return

    color_dict = get_layer_color_dict()
    print(
        colored(f"\nNombre del plano: {cad.doc.Name}", 'cyan', attrs=['bold']))
    print_color_options(color_dict)

    layer_name = get_valid_layer_name(cad.doc)
    if layer_name:
        color_num = get_valid_color()
        create_layer(cad.doc, layer_name, color_num, color_dict)


if __name__ == "__main__":
    main()
