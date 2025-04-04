from pyautocad import Autocad
import math

acad = Autocad()

welcome_message = f"""
Nombre del plano: {acad.doc.Name}
{'*' * 80}
Este programa extrae las coordenadas de los postes y los asocia 
a la capa de numeracion.
El uso de este programa se debe implementar cuando ya exista una 
capa de numeracion de la cual se pueda hacer el conteo.
Si no existe una capa de numeracion, el programa no podra asociar 
los postes a la capa de numeracion.
"""
print(f"{welcome_message}\n")

# Obtiene la lista de todas las capas disponibles
layers_disponibles = [layer.Name for layer in acad.doc.Layers]


def validate_layer(layer_name):
    if not layer_name.strip():
        return False, "El nombre de la capa no puede estar vacío."
    if layer_name not in layers_disponibles:
        return False, f"La capa '{layer_name}' no existe en el documento actual."
    return True, ""


# Solicitar y validar la capa de postes
while True:
    layer_poste = input("Ingresa el nombre de la capa a extraer: ")
    is_valid, error_message = validate_layer(layer_poste)

    if is_valid:
        break
    else:
        print(f"Error: {error_message}")
        print(f"Capas disponibles: {', '.join(layers_disponibles)}")

# Solicitar y validar la capa de numeración
while True:
    layer_numero = input("Ingresa el nombre de la capa de numeracion: ")
    is_valid, error_message = validate_layer(layer_numero)

    if is_valid:
        break
    else:
        print(f"Error: {error_message}")
        print(f"Capas disponibles: {', '.join(layers_disponibles)}")

postes = []
numeros = []

# Se extraen los bloques de la capa postes
for object in acad.model:
    if object.Layer == layer_poste and object.ObjectName == "AcDbBlockReference":
        x, y = object.InsertionPoint[0:2]
        postes.append((x, y))

# Se extraen los textos de la capa numeracion
for object in acad.model:
    if object.Layer == layer_numero and object.ObjectName == "AcDbText":
        try:
            numero = int(object.TextString)
            x, y = object.InsertionPoint[0:2]
            numeros.append((numero, x, y))
        except ValueError:
            print(
                f"Advertencia: No se pudo convertir '{object.TextString}' en número.")

# En esta seccion asociamos
asignaciones = []

# Recorremos cada poste y buscamos el número más cercano
for px, py in postes:
    num_mas_cercano = None
    distancia_minima = float('inf')

    for numero, nx, ny in numeros:
        distancia = math.sqrt((px - nx) ** 2 + (py - ny) ** 2)
        # Distancia euclidiana
        if distancia < distancia_minima:
            distancia_minima = distancia
            num_mas_cercano = numero
    # Si encontramos un número cercano, lo agregamos a la lista de asignaciones
    if num_mas_cercano is not None:
        asignaciones.append((num_mas_cercano, px, py))

asignaciones.sort(key=lambda x: x[0])  # Ordenar por número


# Mostrar las coordenadas obtenidas
print("Postes ordenados segun capa de numeracion mas cercana: ")
print("-" * 50)
for numero, x, y in asignaciones:
    print(f"Poste {numero} →\n   Coordenadas: X= {x:.4f}, Y= {y:.4f}")
print("-" * 50)
print(
    f'Conteo total de postes en la capa "{layer_poste}" encontrados: {len(numeros)}')
