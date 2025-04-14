from utilities.acad_layers import delete_layer
from utilities.acad_common import initialized_autocad, get_available_layers, get_valid_layer_input, display_available_layers, display_message


def main():
    """Función principal para listar y eliminar capas en AutoCAD."""
    acad = initialized_autocad(
        display_message("Programa para eliminar capas en AutoCAD", style='error'))
    if not acad:
        display_message(
            "\nNo se puede continuar sin una conexión a AutoCAD.", style='error')
        display_message("Presione Enter para salir...",
                        style='input', use_rich=True)
        return

    try:
        layers_disponibles = get_available_layers(acad)
        display_available_layers(layers_disponibles)

        while True:
            try:
                layer_to_delete = get_valid_layer_input(
                    "\nSelecciona la capa, su numero asignado a eliminar", layers_disponibles)
                if layer_to_delete is None:
                    display_message(
                        "\nSaliendo del programa...", style='warning')
                    break

                if delete_layer(acad, layer_to_delete, layers_disponibles):
                    layers_disponibles = get_available_layers(acad)
                    display_message(
                        "\nLista de capas actualizada\n")
                    display_available_layers(layers_disponibles)
                else:
                    layers_disponibles = get_available_layers(acad)
                    display_message(
                        "No se pudo eliminar la capa seleccionada.", style='error')
            except KeyboardInterrupt:
                display_message(
                    "\nOperación cancelada por el usuario.", style='warning')
                break
            except Exception as e:
                display_message(f"Error inesperado: {e}", style='error')
                display_message(
                    "Presione Enter para continuar o Ctrl+C para salir...", style='input', use_rich=True)
                break
    except Exception as e:
        display_message(f"Error inesperado: {e}", style='error')


if __name__ == "__main__":
    main()
