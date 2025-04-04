from pyautocad import Autocad

cad = Autocad()
cad.prompt("Hola desde Python\n")

color_dicc = {
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

print("Colores disponibles:")
for code, color in color_dicc.items():
    print(f"{code}: {color}")

while True:
    layer_name = input("Introduce el nombre de la capa a crear: ")

    if not layer_name or layer_name.isspace():
        print("El nombre de la capa no puede estar vacío.")
        continue

    layer_exist = False
    for layer in cad.doc.Layers:
        if layer.Name == layer_name:
            layer_exist = True
            print(f"Error: La capa {layer_name} ya existe.")
            break

    if not layer_exist:
        break

if not layer_exist:
    while True:
        color = input("Introduce el color de la capa (1-255): ")
        try:
            color_num = int(color)
            if 1 <= color_num <= 255:
                color_name = color_dicc.get(color, "Color no definido")

                new_layer = cad.doc.Layers.Add(layer_name)
                new_layer.Color = color_num
                print(
                    f'La capa "{layer_name}" ha sido creada con el color {color_num} ({color_name}).')
                break
            else:
                print("El número de color debe estar entre 1 y 255.")
        except ValueError:
            print("Por favor, introduce un número válido para el color.")
            continue
