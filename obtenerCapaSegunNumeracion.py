from pyautocad import Autocad
import math


def initialize_autocad():
    acad = Autocad()
    print(f"""
Nombre del plano: {acad.doc.Name}
{'*' * 80}
Este programa extrae las coordenadas de los postes y los asocia 
a la capa de numeracion.
El uso de este programa se debe implementar cuando ya exista una 
capa de numeracion de la cual se pueda hacer el conteo.
Si no existe una capa de numeracion, el programa no podra asociar 
los postes a la capa de numeracion.
""")
    return acad


def get_available_layers(acad):
    return [layer.Name for layer in acad.doc.Layers]


def validate_layer(layer_name, layers_disponibles):
    if not layer_name.strip():
        return False, "El nombre de la capa no puede estar vacío."
    if layer_name not in layers_disponibles:
        return False, f"La capa '{layer_name}' no existe en el documento actual."
    return True, ""


def get_valid_layer_input(prompt, layers_disponibles):
    while True:
        layer_name = input(prompt)
        is_valid, error_message = validate_layer(
            layer_name, layers_disponibles)

        if is_valid:
            return layer_name
        else:
            print(f"Error: {error_message}")
            print(f"Capas disponibles: {', '.join(layers_disponibles)}")


def extract_postes(acad, layer_name):
    postes = []
    for obj in acad.model:
        if obj.Layer == layer_name and obj.ObjectName == "AcDbBlockReference":
            x, y = obj.InsertionPoint[0:2]
            postes.append((x, y))
    return postes


def extract_numeros(acad, layer_name):
    numeros = []
    for obj in acad.model:
        if obj.Layer == layer_name and obj.ObjectName == "AcDbText":
            try:
                numero = int(obj.TextString)
                x, y = obj.InsertionPoint[0:2]
                numeros.append((numero, x, y))
            except ValueError:
                print(
                    f"Advertencia: No se pudo convertir '{obj.TextString}' en número.")
    return numeros


def associate_postes_with_numbers(postes, numeros):
    asignaciones = []
    for px, py in postes:
        num_mas_cercano = None
        distancia_minima = float('inf')

        for numero, nx, ny in numeros:
            distancia = math.sqrt((px - nx) ** 2 + (py - ny) ** 2)
            if distancia < distancia_minima:
                distancia_minima = distancia
                num_mas_cercano = numero

        if num_mas_cercano is not None:
            asignaciones.append((num_mas_cercano, px, py))

    return sorted(asignaciones, key=lambda x: x[0])


def display_results(asignaciones, layer_poste, numeros):
    print("Postes ordenados segun capa de numeracion mas cercana: ")
    print("-" * 50)
    for numero, x, y in asignaciones:
        print(f"Poste {numero} →\n   Coordenadas: X= {x:.4f}, Y= {y:.4f}")
    print("-" * 50)
    print(
        f'Conteo total de postes en la capa "{layer_poste}" encontrados: {len(numeros)}')


def main():
    acad = initialize_autocad()
    layers_disponibles = get_available_layers(acad)

    # Obtener capas válidas
    layer_poste = get_valid_layer_input(
        "Ingresa el nombre de la capa a extraer: ", layers_disponibles)
    layer_numero = get_valid_layer_input(
        "Ingresa el nombre de la capa de numeracion: ", layers_disponibles)

    # Extraer datos
    postes = extract_postes(acad, layer_poste)
    numeros = extract_numeros(acad, layer_numero)

    # Asociar postes con números
    asignaciones = associate_postes_with_numbers(postes, numeros)

    # Mostrar resultados
    display_results(asignaciones, layer_poste, numeros)


if __name__ == "__main__":
    main()
