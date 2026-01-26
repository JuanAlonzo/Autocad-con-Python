"""
Módulo de Capas: acad_layers.py
Responsabilidad: Contiene TODA la lógica relacionada con creación, eliminación y listado de capas.
Integra la validación lógica con la interfaz de usuario.
"""

from .config import SETTINGS


def get_layer_color_dict():
    """Devuelve un diccionario de colores de capa predefinidos."""
    return {
        "1": "Rojo",
        "2": "Amarillo",
        "3": "Verde",
        "4": "Cian",
        "5": "Azul",
        "6": "Magenta",
        "7": "Blanco",
        "8": "Gris Oscuro",
        "9": "Gris Claro",
        "256": "Negro",
        # Agregar más colores si es necesario
    }


def is_layer_used(acad, layer_name):
    """
    Verifica si una capa está en uso por algún objeto en el dibujo.
    """
    for obj in acad.iter_objects(limit=5000):
        if obj.Layer == layer_name:
            return True
    return False


def get_all_layer_names(acad):
    """
    Retorna una lista ordenada de nombres de capas.
    """
    return sorted([layer.Name for layer in acad.doc.Layers])


def create_layer_interactive(acad, ui):
    """
    Flujo completo para crear una capa: Pide nombre -> Pide color -> Crea.
    """
    ui.show_message("--- Crear Nueva Capa ---")

    # Pedir Nombre
    while True:
        name = ui.get_input("Nombre de la nueva capa (o 'salir')")
        if not name or name.lower() == "salir":
            return

        # Validación
        if name in get_all_layer_names(acad):
            ui.show_message(f"La capa '{name}' ya existe.", "error")
        else:
            break

    # Pedir Color
    colores = get_layer_color_dict()
    ui.show_message(
        "\nColores comunes: "
        + ", ".join(f"{code}: {color}" for code, color in colores.items())
    )
    # Alternativa: Solo sugerencias
    # ui.show_message("Colores comunes: 1=Rojo, 2=Amarillo, 3=Verde, 7=Blanco", "info")

    while True:
        color_code = ui.get_input("Código de color (1-255)")
        if not color_code:
            return
        if color_code.isdigit() and 1 <= int(color_code) <= 255:
            color_num = int(color_code)
            break
        ui.show_message("Debe ser un número entre 1 y 255.", "error")

    # Pedir Grosor de Línea
    ui.show_message("\n[bold]Grosores comunes:[/bold] 0, 9, 15, 20, 25, 30, 35, 50...")
    ui.show_message("Nota: Use -3 para el valor por Defecto.")

    lw_input = ui.get_input(
        f"Grosor de línea (por defecto {SETTINGS.DEFAULT_LINEWEIGHT})",
        default=str(SETTINGS.DEFAULT_LINEWEIGHT),
    )

    try:
        lineweight = int(lw_input)
    except Exception:
        lineweight = SETTINGS.DEFAULT_LINEWEIGHT

    # Ejecutar Acción
    try:
        new_layer = acad.doc.Layers.Add(name)
        new_layer.Color = color_num
        try:
            new_layer.Lineweight = lineweight
        except Exception:
            ui.show_message(f"Capa '{name}' creada.", "success")
    except Exception as e:
        ui.show_message(f"No se pudo crear la capa: {e}", "error")


def delete_layer_interactive(acad, ui):
    """
    Flujo completo para borrar capa: Muestra lista -> Selecciona -> Valida -> Borra.
    """
    ui.show_message("--- Eliminar Capa ---")

    # Seleccionar
    layers = get_all_layer_names(acad)
    target = ui.get_selection("Seleccione capa a eliminar", layers)
    if not target:
        return

    # Validaciones de Seguridad
    if target in ["0", "Defpoints"]:
        ui.show_message(
            "No se pueden eliminar las capas base del sistema (0/Defpoints).", "error"
        )
        return

    ui.show_message(f"Verificando uso de capa '{target}'...", "info")
    if is_layer_used(acad, target):
        ui.show_message(
            f"Imposible eliminar: La capa '{target}' contiene objetos.", "error"
        )
        return

    # Confirmación y Acción
    if ui.confirm(f"¿Eliminar '{target}' permanentemente?"):
        try:
            acad.doc.Layers.Item(target).Delete()
            ui.show_message(f"Capa '{target}' eliminada.", "success")
        except Exception as e:
            ui.show_message(f"Error de AutoCAD al eliminar: {e}", "error")


def list_layers_interactive(acad, ui):
    """
    Analiza y muestra una tabla comparativa de uso de capas.
    """
    ui.show_message("Analizando capas...", "info")

    layers = get_all_layer_names(acad)
    used = set()

    total = acad.doc.ModelSpace.Count

    ui.progress_start(total, "Escaneando objetos...")
    for i, obj in enumerate(acad.iter_objects()):
        if hasattr(obj, "Layer"):
            used.add(obj.Layer)
        if i % 50 == 0:
            ui.progress_update(50)
    ui.progress_stop()

    unused = [L for L in layers if L not in used]
    used_list = sorted(list(used))

    if used_list:
        # Preparamos datos para la tabla: Columna simple
        rows = [[L] for L in used_list]
        ui.show_message("--- Capas en Uso ---", "info")
        ui.show_table(["Nombre"], rows)

    if unused:
        rows = [[L] for L in unused]
        ui.show_message("--- Capas VACÍAS ---", "warning")
        ui.show_table(["Nombre"], rows)
