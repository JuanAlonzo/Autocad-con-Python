from pyautocad import Autocad

acad = Autocad(create_if_not_exists=True)


def toggle_all_osnaps(acad, enable=True):
    """
    Enable or disable all object snaps in AutoCAD.

    :param acad: The AutoCAD application object.
    :param enable: Boolean to enable or disable object snaps.
    """
    if enable:
        acad.doc.SetVariable("OSMODE", 32767)
        acad.doc.SetVariable("AUTOSNAP", 63)
        acad.prompt("All object snaps are enabled.")
    else:
        acad.doc.SetVariable("OSMODE", 0)
        acad.doc.SetVariable("AUTOSNAP", 0)
        acad.prompt("All object snaps are disabled.")

# Alternativa para activar/desactivar el interruptor principal de OSNAP (F3)


def toggle_osnap_f3(acad, enable=True):
    """Activa o desactiva el interruptor principal de OSNAP (F3)."""
    if enable:
        acad.doc.SendCommand("_OSNAP ON\n")
        acad.prompt("Object Snap turned ON (F3).\n")
    else:
        acad.doc.SendCommand("_OSNAP OFF\n")
        acad.prompt("Object Snap turned OFF (F3).\n")


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
        # toggle_all_osnaps(acad, True)
        toggle_osnap_f3(acad, True)
    elif choice == "2":
        # toggle_all_osnaps(acad, False)
        toggle_osnap_f3(acad, False)
    elif choice == "3":
        print("\nSelecciona los OSNAP que deseas activar:")
        print("1. ENDpoint (1)")
        print("2. MIDpoint (2)")
        print("3. CENter (4)")
        print("4. INTersection (32)")
        print("5. PERpendicular (128)")
        print("6. NEArest (512)")

        selections = input("Ingresa los números separados por comas: ")
        osnap_values = {
            "1": 1, "2": 2, "3": 4, "4": 32, "5": 128, "6": 512
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
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")


if __name__ == "__main__":
    main()
