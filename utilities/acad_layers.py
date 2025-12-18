"""
Módulo de Capas: acad_layers.py
Responsabilidad: Contiene TODA la lógica relacionada con creación, eliminación y listado de capas.
Integra la validación lógica con la interfaz de usuario.
"""

from .acad_common import console, progress
# from rich import print
from .acad_io import (
    display_message,
    display_table,
    get_user_input,
    get_selection_from_list,
    get_confirmation
)


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

    # C. Ejecutar Acción
    try:
        new_layer = acad.doc.Layers.Add(name)
        new_layer.Color = color_num
        display_message(
            f"Capa '{name}' creada con color {color_num}.", "success")
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


# def get_valid_layer_name(cad_doc):
#     """Solicita un nombre de capa al usuario y validar si ya existe."""
#     while True:
#         layer_name = display_message(
#             "\nIntroduce el nombre de la capa a crear (o 'salir' para terminar): ", style='input', use_rich=True).strip()

#         if layer_name.lower() == 'salir':
#             display_message("\nSaliendo del programa...", style='warning')
#             return None

#         is_valid, error = validate_layer_name(
#             layer_name, cad_doc=cad_doc, should_exist=False)

#         if is_valid:
#             return layer_name
#         print(error)


# def get_valid_color():
#     """Solicita y valida un código de color entre 1 y 255."""
#     while True:
#         color = display_message(
#             "Introduce el color de la capa (1-255): ", style='input', use_rich=True).strip()
#         try:
#             color_num = int(color)
#             if 1 <= color_num <= 255:
#                 return color_num
#             else:
#                 display_message(
#                     "El número de color debe estar entre 1 y 255.", style='error')
#         except ValueError:
#             display_message(
#                 "Por favor, introduce un número válido para el color.", style='error')


# def create_layer(cad_doc, layer_name, color_num, color_dict=None):
#     """Crea una nueva capa con el nombre y color especificados."""
#     if color_dict is None:
#         color_dict = get_layer_color_dict()

#     try:
#         new_layer = cad_doc.Layers.Add(layer_name)
#         new_layer.Color = color_num
#         color_name = color_dict.get(str(color_num), "Color no definido")
#         display_message(
#             f'La capa "{layer_name}" ha sido creada con el color {color_num} ({color_name}).', style='success')
#         return new_layer
#     except Exception as e:
#         console.error(
#             f"❌ Error al crear capa {layer_name}: {str(e)}")
#         raise


# def delete_layer(acad, layer_name, layers_disponibles):
#     """Elimina una capa de AutoCAD si no está en uso.
#     Solicita confirmación al usuario antes de eliminarla."""
#     is_valid, error = validate_layer_name(layer_name, layers_disponibles)
#     if not is_valid:
#         print(error)
#         return False

#     try:
#         if is_layer_used(acad, layer_name):
#             display_message(
#                 f"La capa '{layer_name}' está en uso y no puede ser eliminada.", style='error')
#             return False

#         confirm = input(display_message(
#             f"¿Estás seguro de eliminar la capa '{layer_name}'? (s/n): ",
#             style='warning')).lower().strip() == 's'

#         if not confirm:
#             display_message(
#                 "Operación cancelada por el usuario.", style='warning')
#             return False

#         acad.doc.Layers.Item(layer_name).Delete()
#         display_message(
#             f"La capa '{layer_name}' se eliminó satisfactoriamente.", style='success')
#         return True
#     except Exception as e:
#         display_message(
#             f"No se puede eliminar la capa '{layer_name}': {e}", style='error')
#         return False


# def list_layers(acad, show_unused=True, show_used=True):
#     """Lista las capas disponibles del dibujo, con opción de mostrar usadas o no usadas."""
#     # Obtener todas las capas
#     layers = acad.doc.Layers
#     layer_names = [layer.Name for layer in layers]

#     # Verificar qué capas están en uso
#     used_layers = set()

#     # Primero contar los objetos totales para la barra de progreso
#     console.print("[yellow]Contando objetos del dibujo...[/yellow]")
#     all_objects = list(acad.iter_objects())
#     total_objects = len(all_objects)

#     # Usar barra de progreso de rich
#     with console.status(f"[bold green]Procesando {total_objects} objetos...") as status:
#         with progress:
#             task = progress.add_task(
#                 "[cyan]Analizando capas...", total=total_objects)

#             for i, obj in enumerate(all_objects):
#                 try:
#                     if hasattr(obj, "Layer"):
#                         used_layers.add(obj.Layer)
#                 except Exception as e:
#                     console.print(
#                         f"[red]Error al procesar objeto: {str(e)}[/red]")

#                 progress.update(task, completed=i+1)

#     results = {
#         "used": sorted(used_layers) if show_used else [],
#         "unused": sorted(set(layer_names) - used_layers) if show_unused else [],
#         "all": layer_names,
#         "counts": {
#             "used": len(used_layers),
#             "unused": len(set(layer_names) - used_layers),
#             "total": len(layer_names)
#         }
#     }

#     console.print(
#         f"[green]✓ Análisis completado: {results['counts']['used']} capas usadas, {results['counts']['unused']} sin usar[/green]")

#     return results
