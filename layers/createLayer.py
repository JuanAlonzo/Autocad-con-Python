from pyautocad import Autocad


def print_color_options(color_dict):
    """Muestra los colores disponibles con sus códigos."""
    print("\nColores disponibles:")
    print("-"*20)
    for code, color in color_dict.items():
        print(f"{code}: {color}")


def get_valid_layer_name(cad_doc):
    """Solicita un nombre y valida si la capa ya existe."""
    while True:
        layer_name = input(
            "Introduce el nombre de la capa a crear (o 'salir' para terminar): ")

        if layer_name.lower() == 'salir':
            print("Saliendo del programa.")
            return None

        if not layer_name or layer_name.isspace():
            print("El nombre de la capa no puede estar vacío.")
            continue

        for layer in cad_doc.Layers:
            if layer.Name == layer_name:
                print(f'Error: La capa "{layer_name}" ya existe.')
                break
        else:
            return layer_name


def get_valid_color():
    """Solicita y valida un código de color entre 1 y 255."""
    while True:
        color = input("Introduce el color de la capa (1-255): ")
        try:
            color_num = int(color)
            if 1 <= color_num <= 255:
                return color_num
            else:
                print("El número de color debe estar entre 1 y 255.")
        except ValueError:
            print("Por favor, introduce un número válido para el color.")


def create_layer(cad_doc, layer_name, color_num, color_dict):
    """Crea una nueva capa con el nombre y color especificados."""
    new_layer = cad_doc.Layers.Add(layer_name)
    new_layer.Color = color_num
    color_name = color_dict.get(str(color_num), "Color no definido")
    print(
        f'La capa "{layer_name}" ha sido creada con el color {color_num} ({color_name}).')


def main():
    """Función principal del programa."""
    cad = Autocad()
    cad.prompt("Hola desde Python!\n")

    color_dict = {
        "1": "Rojo",
        "2": "Amarillo",
        "3": "Verde",
        "4": "Cian",
        "5": "Azul",
        "6": "Magenta",
        "7": "Blanco",
        "8": "Gris",
        "256": "Negro"
    }

    print(f"\nNombre del plano: {cad.doc.Name}")
    print_color_options(color_dict)

    layer_name = get_valid_layer_name(cad.doc)
    if layer_name:
        color_num = get_valid_color()
        create_layer(cad.doc, layer_name, color_num, color_dict)


if __name__ == "__main__":
    main()
