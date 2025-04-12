from termcolor import colored
from utilities.acad_common import initialized_autocad
from utilities.acad_layers import print_color_options, get_valid_layer_name, get_valid_color, create_layer, get_layer_color_dict


def main():
    """Función principal del programa."""
    cad = initialized_autocad(
        colored("Programa para crear nuevas capas en AutoCAD", 'cyan'))
    if not cad:
        print(colored(
            "\nNo se puede continuar sin una conexión a AutoCAD.", 'red', attrs=['bold']))
        input(colored("Presione Enter para salir...", 'white', attrs=['bold']))
        return
    while True:
        try:
            color_dict = get_layer_color_dict()
            print_color_options(color_dict)

            layer_name = get_valid_layer_name(cad.doc)
            if layer_name is None:
                print(colored("Operación cancelada.",
                      'yellow', attrs=['bold']))
                break

            color_num = get_valid_color()
            if color_num is None:
                print(colored("Operación cancelada.",
                      'yellow', attrs=['bold']))
                break
            create_layer(cad.doc, layer_name, color_num, color_dict)

            continuar = input(
                colored("\n¿Desea crear otra capa? (s/n): ", 'cyan')).strip().lower()
            if continuar != 's':
                print(colored("Saliendo del programa...",
                      'yellow', attrs=['bold']))
                break
        except KeyboardInterrupt:
            print(colored("\nOperación cancelada por el usuario.",
                          'yellow', attrs=['bold']))
            break
        except Exception as e:
            print(colored(f"Error inesperado: {e}", 'red'))
            input(colored(
                "Presione Enter para continuar o Ctrl+C para salir...", 'white', attrs=['bold']))
            break


if __name__ == "__main__":
    main()
