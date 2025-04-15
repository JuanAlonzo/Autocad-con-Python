from utilities.acad_common import (
    initialized_autocad,
    get_available_layers,
    get_valid_layer_input,
    display_message,
    console
)
from utilities.acad_utils import (
    extract_text_and_coordinates,
    display_text_coordinates,
    export_data_to_csv,
    export_data_to_excel
)
from rich.panel import Panel
from rich.text import Text


def show_export_menu(data, layer_name):
    """Muestra un menú para exportar los datos extraídos."""
    while True:
        console.print(Panel(
            Text("OPCIONES DE EXPORTACIÓN", style="bold white"),
            subtitle="Selecciona una opción",
            border_style="cyan"
        ))

        console.print("[1] Exportar a CSV")
        console.print("[2] Exportar a Excel")
        console.print("[3] Volver sin exportar")

        option = display_message(
            "\nElige una opción (1-3): ",
            style='input',
            use_rich=True
        ).strip()

        if option == "1":
            export_data_to_csv(data, layer_name)
            break
        elif option == "2":
            export_data_to_excel(data, layer_name)
            break
        elif option == "3":
            display_message("No se exportaron datos.", style='info')
            break
        else:
            display_message(
                "Opción no válida. Intenta de nuevo.", style='error')


def show_filter_menu(acad, layer_name):
    """Muestra un menú para filtrar los datos extraídos."""
    console.print(Panel(
        Text("FILTRAR POR TIPO DE TEXTO", style="bold white"),
        subtitle="Selecciona una opción",
        border_style="cyan"
    ))

    console.print("[1] Todos los Textos")
    console.print("[2] Solo Texto Simple (Text)")
    console.print("[3] Solo Texto Multiple (MText)")

    option = display_message(
        "\nElige una opción (1-3): ",
        style='input',
        use_rich=True
    ).strip()

    text_type = "all"
    if option == "2":
        text_type = "text"
    elif option == "3":
        text_type = "mtext"

    return extract_text_and_coordinates(acad, layer_name, text_type)


def main():
    """Función principal del programa."""
    acad = initialized_autocad(display_message(
        "Programa para Extraer Texto y Coordenadas", style='info', bold=True))
    if not acad:
        display_message(
            "\nNo se puede continuar sin una conexión a AutoCAD.", style='error')
        display_message("Presione Enter para salir...",
                        style='input', use_rich=True)
        return

    try:
        layers_disponibles = get_available_layers(acad)
        layer_name = get_valid_layer_input(
            "Escribe el nombre de la capa de la cual extraer texto y coordenadas", layers_disponibles, show_table=True)

        if layer_name is None:
            display_message("Saliendo del programa...", style='warning')
            return
        display_message(f"Procesando capa: {layer_name}", style='info')

        data = show_filter_menu(acad, layer_name)

        if data:
            display_text_coordinates(data, layer_name)

            # Preguntar si se quieren exportar los datos
            exportar = display_message(
                "\n¿Deseas exportar los resultados? (s/n): ",
                style='input',
                use_rich=True
            ).lower().strip()

            if exportar == 's':
                show_export_menu(data, layer_name)
        else:
            display_message(
                f"No se encontraron textos en la capa '{layer_name}'",
                style='warning'
            )
        continuar = display_message(
            "\n¿Desea procesar otra capa? (s/n): ",
            style='input',
            use_rich=True
        ).lower().strip()

        if continuar == 's':
            main()  # Reiniciar el programa
        else:
            display_message(
                "Programa finalizado. ¡Hasta luego!", style='success')
    except KeyboardInterrupt:
        display_message(
            "\nOperación cancelada por el usuario.", style='warning')
    except Exception as e:
        display_message(f"Error inesperado: {e}", style='error')


if __name__ == "__main__":
    main()
