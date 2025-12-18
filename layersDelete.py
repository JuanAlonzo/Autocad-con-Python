from utilities.acad_common import require_autocad
from utilities.acad_layers import delete_layer_interactive
from utilities.acad_io import get_confirmation


def main():
    acad = require_autocad("Eliminación de capas")
    while True:
        delete_layer_interactive(acad)

        if not get_confirmation("¿Desea eliminar otra capa?"):
            break


if __name__ == "__main__":
    main()
