from pyautocad import Autocad
from colorama import init, Fore, Style, just_fix_windows_console
from termcolor import colored

just_fix_windows_console()
init()


def is_layer_used(acad, layer_name):
    """Chequea si el layer esta siendo usado por algun objeto en el dibujo."""
    return any(obj.Layer == layer_name for obj in acad.iter_objects(limit=1000))


def list_and_delete_layers():
    acad = Autocad(create_if_not_exists=True)
    print("Conectado a AutoCAD")

    # Lista las capas existentes
    layers = acad.doc.Layers
    print("CAPAS EXISTENTES:")
    for layer in layers:
        print(f"- {layer.Name}")

    layer_to_delete = input(
        "Selecciona la capa a eliminar (escribe 'salir' para finalizar): ")

    # Opción para salir del programa
    if layer_to_delete.lower() == "salir":
        print("Finalizando el programa...")
        return

    layer_found = False
    for layer in layers:
        if layer.Name == layer_to_delete:
            layer_found = True
            try:
                if is_layer_used(acad, layer.Name):
                    print(
                        f"La capa '{layer.Name}' esta en uso y no puede ser eliminada.")
                else:
                    layer_name = layer.Name
                    layers.Item(layer_name).Delete()
                    print(
                        f"La capa '{layer_name}' se elimino satisfactoriamente.")
            except Exception as e:
                print(f"No se puede eliminar la capa '{layer_to_delete}': {e}")
            break

    if not layer_found:
        print(f"Capa '{layer_to_delete}' no encontrada.")


if __name__ == "__main__":
    list_and_delete_layers()
