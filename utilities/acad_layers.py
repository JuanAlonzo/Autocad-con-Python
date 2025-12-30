"""
Módulo de Capas: acad_layers.py
Responsabilidad: Contiene TODA la lógica relacionada con creación, eliminación y listado de capas.
Integra la validación lógica con la interfaz de usuario.
"""

from .acad_common import console, progress
from .acad_io import (
    display_message,
    display_table,
    get_user_input,
    get_selection_from_list,
    get_confirmation
)
from .config import DEFAULT_LINEWEIGHT


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
        "256": "Negro"
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


def create_layer_interactive(acad):
    """
    Flujo completo para crear una capa: Pide nombre -> Pide color -> Crea.
    """
    console.print("\n[bold magenta]--- Crear Nueva Capa ---[/bold magenta]")

    # A. Pedir Nombre
    while True:
        name = get_user_input("Nombre de la nueva capa (o 'salir')")
        if not name or name.lower() == 'salir':
            return

        # Validación: ¿Ya existe?
        existentes = get_all_layer_names(acad)
        if name in existentes:
            display_message(f"La capa '{name}' ya existe.", "error")
        else:
            break

    # B. Pedir Color
    colores = get_layer_color_dict()
    console.print("\n[bold]Colores sugeridos:[/bold]")
    for code, color in colores.items():
        console.print(f"  [cyan]{code}[/cyan]: {color}")

    while True:
        color_code = get_user_input("Código de color (1-255)")
        if not color_code:
            return
        if color_code.isdigit() and 1 <= int(color_code) <= 255:
            color_num = int(color_code)
            break
        display_message("Debe ser un número entre 1 y 255.", "error")

    # C. Pedir Grosor de Línea
    console.print(
        "\n[bold]Grosores comunes:[/bold] 0, 9, 15, 20, 25, 30, 35, 50...")
    console.print("Nota: Use -3 para el valor por Defecto.")

    lw_input = get_user_input(
        f"Grosor de línea (por defecto {DEFAULT_LINEWEIGHT})", default=str(DEFAULT_LINEWEIGHT))

    try:
        lineweight = int(lw_input)
    except ValueError:
        display_message(
            "Valor inválido para grosor de línea. Usando valor por defecto.", "warning")
        lineweight = DEFAULT_LINEWEIGHT

    # D. Ejecutar Acción
    try:
        new_layer = acad.doc.Layers.Add(name)
        new_layer.Color = color_num
        try:
            new_layer.Lineweight = lineweight
        except Exception:
            display_message(
                f"El grosor {lineweight} no es válido. Usando valor por defecto.", "warning")
            new_layer.Lineweight = lineweight
        except Exception:
            display_message(
                f"El grosor {lineweight} no es válido. Usando valor por defecto.", "warning")
            new_layer.Lineweight = DEFAULT_LINEWEIGHT
        display_message(
            f"Capa '{name}' creada con color {color_num} y grosor de línea {lineweight}.", "success")
    except Exception as e:
        display_message(f"No se pudo crear la capa: {e}", "error")


def delete_layer_interactive(acad):
    """
    Flujo completo para borrar capa: Muestra lista -> Selecciona -> Valida -> Borra.
    """
    console.print("\n[bold magenta]--- Eliminar Capa ---[/bold magenta]")

    # A. Seleccionar
    layers = get_all_layer_names(acad)
    target = get_selection_from_list(
        "Capas Disponibles", layers, "Seleccione capa a eliminar")
    if not target:
        return

    # B. Validaciones de Seguridad
    if target == "0" or target == "Defpoints":
        display_message(
            "No se pueden eliminar las capas base del sistema (0/Defpoints).", "error")
        return

    display_message(f"Verificando uso de capa '{target}'...", "info")
    if is_layer_used(acad, target):
        display_message(
            f"Imposible eliminar: La capa '{target}' contiene objetos.", "error")
        return

    # C. Confirmación y Acción
    if get_confirmation(f"¿Seguro que desea eliminar '{target}' permanentemente?"):
        try:
            acad.doc.Layers.Item(target).Delete()
            display_message(f"Capa '{target}' eliminada.", "success")
        except Exception as e:
            display_message(f"Error de AutoCAD al eliminar: {e}", "error")


def list_layers_interactive(acad):
    """
    Analiza y muestra una tabla comparativa de uso de capas.
    """
    display_message(
        "Analizando capas... (esto puede tardar en dibujos grandes)", "info")

    layers = get_all_layer_names(acad)
    used = set()

    # Usamos la barra de progreso de 'common'
    total_objs = acad.doc.ModelSpace.Count  # Estimación rápida
    with progress:
        task = progress.add_task(
            "[green]Escaneando objetos...", total=total_objs if total_objs > 0 else 100)

        # Barrido optimizado
        for i, obj in enumerate(acad.iter_objects()):
            if hasattr(obj, 'Layer'):
                used.add(obj.Layer)
            if i % 100 == 0:
                progress.update(task, advance=100)

    unused = [l for l in layers if l not in used]
    used_list = sorted(list(used))

    # Mostrar resultados usando acad_io
    console.print("\n")
    if used_list:
        # Preparamos datos para la tabla: Columna simple
        rows = [[l] for l in used_list]
        display_table(f"Capas EN USO ({len(used_list)})", ["Nombre"], rows)

    if unused:
        rows = [[l] for l in unused]
        display_table(f"Capas VACÍAS ({len(unused)})", ["Nombre"], rows)

    display_message(f"Total: {len(layers)} capas.", "info")
