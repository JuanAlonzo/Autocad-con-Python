"""
Gestor de Capas de AutoCAD
Herramienta unificada para crear, eliminar y listar capas
"""

from utilities import (
    require_autocad,
    create_layer_interactive,
    delete_layer_interactive,
    list_layers_interactive,
    ConsoleUI,
)


def main():
    ui = ConsoleUI()
    acad = require_autocad(ui)

    while True:
        ui.show_message("GESTOR DE CAPAS - AUTOCAD")

        opciones = [
            "Listar capas existentes",
            "Crear nueva capa",
            "Eliminar capa",
            "Salir",
        ]

        seleccion = ui.get_selection("Seleccione una opción", opciones)

        if not seleccion or "Salir" in seleccion:
            ui.show_message("Saliendo del gestor de capas...", "info")
            break

        if "Listar" in seleccion:
            list_layers_interactive(acad, ui)

        elif "Crear" in seleccion:
            while True:
                create_layer_interactive(acad, ui)
                if not ui.confirm("¿Desea crear otra capa?"):
                    break

        elif "Eliminar" in seleccion:
            while True:
                delete_layer_interactive(acad, ui)
                if not ui.confirm("¿Desea eliminar otra capa?"):
                    break

        # Pausa antes de volver al menú principal
        input("\nPresione Enter para continuar...")


if __name__ == "__main__":
    main()
