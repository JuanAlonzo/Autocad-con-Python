from pyautocad import Autocad

acad = Autocad()

print(f"Nombre del plano: {acad.doc.Name}")
