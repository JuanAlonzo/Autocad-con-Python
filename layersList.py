from utilities.ui_console import ConsoleUI
from utilities.acad_common import require_autocad
from utilities.acad_layers import list_layers_interactive


def main():
    ui = ConsoleUI()
    acad = require_autocad(ui)

    list_layers_interactive(acad, ui)


if __name__ == "__main__":
    main()
