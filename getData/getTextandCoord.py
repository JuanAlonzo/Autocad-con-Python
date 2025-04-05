from pyautocad import Autocad

acad = Autocad()
acad.prompt("Iniciando script...\n")

print(f"""
Nombre del archivo: {acad.doc.Name}
{'*' * 80}
Bienvenido al programa de extracción de texto y coordenadas.
Este programa extrae el texto y las coordenadas "X, Y" de 
objetos en AutoCAD. Asegúrate de tener la capa correcta seleccionada 
y de que los objetos sean de tipo texto.
Recuerda que el programa no dibuja nada, solo extrae información.
"""
)

# Obtiene la lista de todas las capas disponibles
available_layers = [layer.Name for layer in acad.doc.Layers]


def validate_layer(layer_name):
    if not layer_name.strip():
        return False, "El nombre de la capa no puede estar vacío."
    if layer_name not in available_layers:
        return False, f"La capa '{layer_name}' no existe en el documento actual."
    return True, ""


# Solicitar y validar la capa de postes
while True:
    layer_name = input(
        "Escribe el nombre de la capa de la cual\nextraer texto y coordenadas: ")
    is_valid, error_message = validate_layer(layer_name)

    if is_valid:
        break
    else:
        print(f"Error: {error_message}")
        print(f"Capas disponibles: \n{', \n'.join(available_layers)}")


# Lista para almacenar los números y sus coordenadas
data = []

for object in acad.model:
    try:
        if object.Layer == layer_name and object.ObjectName in ["AcDbText", "AcDbMText"]:
            content = object.TextString
            x, y = object.InsertionPoint[0:2]
            data.append((content, x, y))
    except Exception as e:
        print(f"Error al procesar el objeto: {e}")

print("Coordenadas obtenidas en la capa:", layer_name)
print("-" * 50)
for i, (content, x, y) in enumerate(data, 1):
    print(f"{i}. Texto: '{content}'\n   Coordenadas: X= {x:.4f}, Y= {y:.4f}")
print("-" * 50)
print(f"Total de objetos encontrados: {len(data)}")
