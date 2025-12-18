from utilities.acad_common import require_autocad
from utilities.acad_layers import list_layers_interactive


def main():
    acad = require_autocad("Listado de capas")

    list_layers_interactive(acad)


if __name__ == "__main__":
    main()
