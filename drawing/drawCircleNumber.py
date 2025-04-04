from pyautocad import Autocad, APoint

acad = Autocad()
acad.prompt("DRAW A CIRCLE AND TEXT\n")

p1 = APoint(288991.3015, 8646797.0459)  # Coordenadas del punto
radius = 2

circle = acad.model.AddCircle(p1, radius)

# Desplaza el texto hacia abajo y a la izquierda del círculo
text_x = p1.x - 2.5
text_y = p1.y - 2.2
text_point = APoint(text_x, text_y)

text_string = "1"  # Número del texto
text_height = 1  # Tamaño del texto
text = acad.model.AddText(text_string, text_point, text_height)

# Cambia el color del texto y el circulo a amarillo (color 2 en AutoCAD)
text.Color = 2
circle.Color = 2

print("Círculo y texto dibujados correctamente.")
