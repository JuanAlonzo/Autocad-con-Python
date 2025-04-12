from termcolor import colored
from utilities.acad_common import initialized_autocad, get_available_layers, get_valid_layer_input, delete_layer


def main():
    """Función principal para listar y eliminar capas en AutoCAD."""
    acad = initialized_autocad(
        colored("Programa para eliminar capas en AutoCAD", 'cyan', attrs=['bold']))
    if not acad:
        print(colored(
            "\nNo se puede continuar sin una conexión a AutoCAD.", 'red', attrs=['bold']))
        input(colored("Presione Enter para salir...", 'white', attrs=['bold']))
        return
    while True:
        try:
            layers_disponibles = get_available_layers(acad)
            layer_to_delete = get_valid_layer_input(
                "\nSelecciona la capa a eliminar", layers_disponibles)
            if layer_to_delete is None:
                print(colored("Saliendo del programa...",
                              'yellow', attrs=['bold']))
                break

            delete_layer(acad, layer_to_delete, layers_disponibles)
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
