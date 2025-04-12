from utilities.acad_common import initialized_autocad, get_available_layers, get_valid_layer_input,  display_text_coordinates
from termcolor import colored


def extract_text_and_coordinates(acad, layer_name):
    """Extrae texto y coordenadas de los objetos de texto en la capa especificada."""
    data = []

    for obj in acad.model:
        try:
            if obj.Layer == layer_name and obj.ObjectName in ["AcDbText", "AcDbMText"]:
                content = obj.TextString
                x, y = obj.InsertionPoint[0:2]
                data.append((content, x, y))
        except Exception as e:
            print(f"Error al procesar el objeto: {e}")

    return data


def main():
    """Función principal del programa."""
    acad = initialized_autocad()
    available_layers = get_available_layers(acad)
    layer_name = get_valid_layer_input(
        "Escribe el nombre de la capa de la cual extraer texto y coordenadas", available_layers)
    if layer_name is None:
        print("Saliendo del programa...")
        return
    else:
        print(f"Procesando capa: {layer_name}")
    data = extract_text_and_coordinates(acad, layer_name)
    display_text_coordinates(data, layer_name)


if __name__ == "__main__":
    main()
