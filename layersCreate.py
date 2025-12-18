from utilities.acad_common import require_autocad
from utilities.acad_layers import create_layer_interactive
from utilities.acad_io import get_confirmation


def main():
    acad = require_autocad("Creación de capas")

    while True:
        create_layer_interactive(acad)

        if not get_confirmation("¿Desea crear otra capa?"):
            break


if __name__ == "__main__":
    main()
