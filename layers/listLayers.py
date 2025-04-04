from pyautocad import Autocad

cad = Autocad()
cad.prompt("Conectado a AutoCAD\n")

layers = cad.doc.Layers

print("CAPAS EXISTENTES:")
for layer in layers:
    print(f"- {layer.Name}")
