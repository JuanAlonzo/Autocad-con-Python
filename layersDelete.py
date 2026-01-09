from utilities.ui_console import ConsoleUI
from utilities.acad_common import require_autocad
from utilities.acad_layers import delete_layer_interactive


def main():
    ui = ConsoleUI()
    acad = require_autocad(ui)

    while True:
        delete_layer_interactive(acad, ui)

        if not ui.confirm("¿Desea eliminar otra capa?"):
            break


if __name__ == "__main__":
    main()
