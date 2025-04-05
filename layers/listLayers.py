from pyautocad import Autocad
import win32com.client  # pip install pywin32

# Inicializar AutoCAD
cad = Autocad()
cad.prompt("Conectado a AutoCAD\n")

# Obtener todas las capas
layers = cad.doc.Layers
layer_names = [layer.Name for layer in layers]

# Verificar qué capas están en uso
used_layers = set()
all_objects = cad.iter_objects()

# Recorrer todos los objetos para verificar a qué capa pertenecen
for obj in all_objects:
    try:
        if hasattr(obj, "Layer"):
            used_layers.add(obj.Layer)
    except:
        pass

# Mostrar resultados
print("\nCapas utilizadas:")
print("-" * 35)
for layer_name in sorted(used_layers):
    print(f"- {layer_name}")

print("\nCapas sin utilizar:")
print("-" * 35)
for layer_name in sorted(set(layer_names) - used_layers):
    print(f"- {layer_name}")

print("\nTotal de capas:")
print("*" * 35)
print(f"- Capas en uso: {len(used_layers)}")
print(f"- Capas sin uso: {len(set(layer_names) - used_layers)}")
print(f"- Total: {len(layer_names)}")
