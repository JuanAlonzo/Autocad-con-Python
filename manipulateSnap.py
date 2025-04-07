from pyautocad import Autocad

acad = Autocad(create_if_not_exists=True)


def toggle_all_osnaps(acad, enable=True):
    """
    Enable or disable all object snaps in AutoCAD.

    :param acad: The AutoCAD application object.
    :param enable: Boolean to enable or disable object snaps.
    """
    if enable:
        acad.doc.SetVariable("OSMODE", 16383)
        acad.doc.SetVariable("AUTOSNAP", 63)
        acad.prompt("All object snaps are enabled.")
    else:
        acad.doc.SetVariable("OSMODE", 0)
        acad.doc.SetVariable("AUTOSNAP", 0)
        acad.prompt("All object snaps are disabled.")


def set_custom_osnaps(acad, osnap_sum):
    """
    Set a custom object snap mode in AutoCAD.

    :param acad: The AutoCAD application object.
    :param osnap_sum: The sum of the object snap modes to set.
    """
    acad.doc.SetVariable("OSMODE", osnap_sum)
    acad.doc.SetVariable("AUTOSNAP", 63)
    acad.prompt(f"Object snaps set to {osnap_sum}\n.")


def get_current_osnap(acad):
    """
    Get the current object snap mode in AutoCAD.

    :param acad: The AutoCAD application object.
    :return: The current object snap mode as an integer.
    """
    return acad.doc.GetVariable("OSMODE")


def osnap_manager(acad):
    """Gestiona la configuración de OSNAP."""
    current_osnap = get_current_osnap(acad)

    print("\nGestor de OSNAP")
    print("-" * 30)
    print(f"Configuración actual de OSNAP: {current_osnap}")
    print("1. Activar todos los OSNAP")
    print("2. Desactivar todos los OSNAP")
    print("3. Configuración personalizada")
    print("4. Volver al menú principal")

    choice = input("Selecciona una opción: ")

    if choice == "1":
        toggle_all_osnaps(acad, True)
        # toggle_osnap_f3(acad, True)
    elif choice == "2":
        toggle_all_osnaps(acad, False)
        # toggle_osnap_f3(acad, False)
    elif choice == "3":
        print("\nSelecciona los OSNAP que deseas activar:")
        print("01. ENDpoint (1)")
        print("02. MIDpoint (2)")
        print("03. CENter (4)")
        print("04. GEometric Center(1024)")
        print("05. Node(8)")
        print("06. QUAdrant(16)")
        print("07. INTersection (32)")
        print("08. EXTension (4096)")
        print("09. INSertion (64)")
        print("10. PERpendicular (128)")
        print("11. TANgent (256)")
        print("12. NEArest (512)")
        print("13. AParent Intersection (2048)")
        print("14. PARallel (8192)")
        # print("15. All sellected (16383)")

        selections = input("Ingresa los números separados por comas: ")
        osnap_values = {
            "1": 1, "2": 2, "3": 4, "4": 1024, "5": 8, "6": 16, "7": 32, "8": 4096,
            "9": 64, "10": 128, "11": 256, "12": 512, "13": 2048, "14": 8192
        }

        total = 0
        for sel in selections.split(","):
            sel = sel.strip()
            if sel in osnap_values:
                total += osnap_values[sel]

        set_custom_osnaps(acad, total)
        print(f"OSNAP configurado con valor: {total}")

    return


def main():
    """Función principal del programa."""
    # Inicializa AutoCAD (esto ya lo tienes en el nivel superior, pero es mejor moverlo aquí)
    try:
        acad = Autocad(create_if_not_exists=True)
        print(f"AutoCAD conectado correctamente: {acad.doc.Name}")
    except Exception as e:
        print(f"Error al conectar con AutoCAD: {e}")
        return

    # Menú principal
    while True:
        print("\n" + "=" * 40)
        print("MENÚ PRINCIPAL - MANIPULACIÓN DE AUTOCAD")
        print("=" * 40)
        print("1. Gestionar configuración de OSNAP")
        print("2. Salir")

        option = input("\nSelecciona una opción: ")

        if option == "1":
            osnap_manager(acad)
        elif option == "2":
            print("\nSaliendo del programa...")
            break
        else:
            print("\nOpción no válida. Inténtalo de nuevo.")


if __name__ == "__main__":
    main()
