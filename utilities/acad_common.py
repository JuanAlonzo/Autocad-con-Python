from pyautocad import Autocad
from colorama import init
from termcolor import colored

init()


def initialized_autocad(message=None):
    try:
        acad = Autocad()
        acad.prompt(colored("AutoCAD initialized successfully.\n",
                    'cyan', attrs=['bold']))
        if message:
            print(f"\n{message}\n")
        return acad

    except Exception as e:
        print(f"Error initializing AutoCAD: {e}")
        return None


def get_available_layers(acad):
    return [layer.Name for layer in acad.doc.Layers]


def validate_layer(layer_name, layers_disponibles):
    if not layer_name.strip():
        return False, "El nombre de la capa no puede estar vacío."
    if layer_name not in layers_disponibles:
        return False, f"La capa '{layer_name}' no existe en el documento actual."
    return True, ""


def get_valid_layer_input(prompt, layers):
    while True:
        layer_name = input(prompt)
        is_valid, error = validate_layer(layer_name, layers)
        if is_valid:
            return layer_name
        print(f"Error: {error}")
        print(f"Capas disponibles: {', '.join(layers)}")


def display_text_coordinates(data, layer_name):
    print("Coordenadas obtenidas en la capa:", layer_name)
    print("-" * 50)
    for i, (content, x, y) in enumerate(data, 1):
        print(f"{i}. Texto: '{content}'\n   Coordenadas: X= {x:.4f}, Y= {y:.4f}")
    print("-" * 50)
    print(f"Total de objetos encontrados: {len(data)}")


def display_postes_with_numbers(asignaciones, capa_poste, numeros):
    print("Postes ordenados segun capa de numeracion más cercana:")
    print("-" * 50)
    for numero, x, y in asignaciones:
        print(f"Poste {numero} →\n   Coordenadas: X= {x:.4f}, Y= {y:.4f}")
    print("-" * 50)
    print(
        f'Conteo total de postes en la capa "{capa_poste}" encontrados: {len(numeros)}')
