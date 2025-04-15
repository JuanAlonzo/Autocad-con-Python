from utilities.acad_common import initialized_autocad, display_message
from utilities.acad_snap import show_osnap_menu


def main():
    """Función principal del programa."""
    acad = initialized_autocad(
        display_message("Programa para manipular en OSNAP en AutoCAD", style='init'))
    if not acad:
        display_message(
            "\nNo se puede continuar sin una conexión a AutoCAD.", style='error')
        display_message("Presione Enter para salir...",
                        style='input', use_rich=True)
        return

    # Menú principal
    while True:
        display_message("\nMENÚ PRINCIPAL - OSNAP MANAGER",
                        style='info', bold=True)
        print("=" * 40)
        print("1. Gestionar configuración de OSNAP")
        print("2. Salir")

        option = display_message(
            "\nSelecciona una opción: ", style='input', use_rich=True)

        if option == "1":
            show_osnap_menu(acad)
        elif option == "2":
            display_message("\nSaliendo del programa...", style='warning')
            break
        else:
            display_message(
                "\nOpción no válida. Inténtalo de nuevo.", style='error')


if __name__ == "__main__":
    main()
