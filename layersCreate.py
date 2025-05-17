from termcolor import colored
from utilities.acad_common import initialized_autocad, print_color_options
from utilities.acad_layers import get_valid_layer_name, get_valid_color, create_layer, display_message


def main():
    """Función principal del programa."""
    cad = initialized_autocad(
        display_message("Programa para crear nuevas capas en AutoCAD", style='init'))
    if not cad:
        display_message(
            "\nNo se puede continuar sin una conexión a AutoCAD.", style='error')
        display_message("Presione Enter para salir...",
                        style='input', use_rich=True)
        return
    while True:
        try:
            color_dict = print_color_options()

            layer_name = get_valid_layer_name(cad.doc)
            if layer_name is None:
                display_message("Operación cancelada.", style='warning')
                break

            color_num = get_valid_color()
            if color_num is None:
                display_message("Operación cancelada.", style='warning')
                break
            create_layer(cad.doc, layer_name, color_num, color_dict)

            continuar = input(colored(
                "\n¿Desea crear otra capa? (s/n): ", 'cyan', attrs=['bold'])).strip().lower()
            if continuar not in ['s', 'si', 'yes', 'y']:
                display_message("Saliendo del programa...", style='warning')
                break
        except KeyboardInterrupt:
            display_message(
                "\nOperación cancelada por el usuario.", style='warning')
            break
        except Exception as e:
            display_message(f"Error inesperado: {e}", style='error')
            display_message(
                "Presione Enter para continuar o Ctrl+C para salir...", style='input', use_rich=True)
            break


if __name__ == "__main__":
    main()
