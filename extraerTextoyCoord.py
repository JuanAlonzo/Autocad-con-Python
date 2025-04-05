from pyautocad import Autocad


def initialize_autocad():
    """Inicializa la conexión con AutoCAD y muestra un mensaje de bienvenida."""
    acad = Autocad()
    acad.prompt("Iniciando script...\n")

    welcome_message = f"""
    Nombre del archivo: {acad.doc.Name}
    {'*' * 80}
    Bienvenido al programa de extracción de texto y coordenadas.
    Este programa extrae el texto y las coordenadas "X, Y" de 
    objetos en AutoCAD. Asegúrate de tener la capa correcta seleccionada 
    y de que los objetos sean de tipo texto.
    Recuerda que el programa no dibuja nada, solo extrae información.
    """

    print(f"{welcome_message}\n")
    return acad


def get_available_layers(acad):
    """Obtiene la lista de todas las capas disponibles en el documento actual."""
    return [layer.Name for layer in acad.doc.Layers]


def validate_layer(layer_name, available_layers):
    """Valida si la capa existe en el documento actual."""
    if not layer_name.strip():
        return False, "El nombre de la capa no puede estar vacío."
    if layer_name not in available_layers:
        return False, f"La capa '{layer_name}' no existe en el documento actual."
    return True, ""


def get_valid_layer(available_layers):
    """Solicita y valida la capa hasta que se proporcione una válida."""
    while True:
        layer_name = input(
            "Escribe el nombre de la capa de la cual\nextraer texto y coordenadas: ")
        is_valid, error_message = validate_layer(layer_name, available_layers)

        if is_valid:
            return layer_name
        else:
            print(f"Error: {error_message}")
            print(f"Capas disponibles: \n{', \n'.join(available_layers)}")


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


def display_results(data, layer_name):
    """Muestra los resultados de la extracción."""
    print("Coordenadas obtenidas en la capa:", layer_name)
    print("-" * 50)
    for i, (content, x, y) in enumerate(data, 1):
        print(f"{i}. Texto: '{content}'\n   Coordenadas: X= {x:.4f}, Y= {y:.4f}")
    print("-" * 50)
    print(f"Total de objetos encontrados: {len(data)}")


def main():
    """Función principal del programa."""
    acad = initialize_autocad()
    available_layers = get_available_layers(acad)
    layer_name = get_valid_layer(available_layers)
    data = extract_text_and_coordinates(acad, layer_name)
    display_results(data, layer_name)


if __name__ == "__main__":
    main()
