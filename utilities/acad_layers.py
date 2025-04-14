from termcolor import colored
from rich import print
from utilities.acad_common import console, progress, is_layer_used, get_layer_color_dict, validate_layer_name, display_message


def get_valid_layer_name(cad_doc):
    """Solicita un nombre de capa al usuario y validar si ya existe."""
    while True:
        layer_name = input(colored(
            "\nIntroduce el nombre de la capa a crear (o 'salir' para terminar): ", 'white', attrs=['bold'])).strip()

        if layer_name.lower() == 'salir':
            display_message("\nSaliendo del programa...", style='warning')
            return None

        is_valid, error = validate_layer_name(
            layer_name, cad_doc=cad_doc, should_exist=False)

        if is_valid:
            return layer_name
        print(error)


def get_valid_color():
    """Solicita y valida un código de color entre 1 y 255."""
    while True:
        color = input(
            colored("Introduce el color de la capa (1-255): ", 'white', attrs=['bold'])).strip()
        try:
            color_num = int(color)
            if 1 <= color_num <= 255:
                return color_num
            else:
                display_message(
                    "El número de color debe estar entre 1 y 255.", style='error')
        except ValueError:
            display_message(
                "Por favor, introduce un número válido para el color.", style='error')


def create_layer(cad_doc, layer_name, color_num, color_dict=None):
    """Crea una nueva capa con el nombre y color especificados."""
    if color_dict is None:
        color_dict = get_layer_color_dict()

    try:
        new_layer = cad_doc.Layers.Add(layer_name)
        new_layer.Color = color_num
        color_name = color_dict.get(str(color_num), "Color no definido")
        display_message(
            f'La capa "{layer_name}" ha sido creada con el color {color_num} ({color_name}).', style='success')
        return new_layer
    except Exception as e:
        console.error(
            f"❌ Error al crear capa {layer_name}: {str(e)}")
        raise


def delete_layer(acad, layer_name, layers_disponibles):
    """Elimina una capa de AutoCAD si no está en uso.
    Solicita confirmación al usuario antes de eliminarla."""
    is_valid, error = validate_layer_name(layer_name, layers_disponibles)
    if not is_valid:
        print(error)
        return False

    try:
        if is_layer_used(acad, layer_name):
            display_message(
                f"La capa '{layer_name}' está en uso y no puede ser eliminada.", style='error')
            return False

        confirm = input(colored(
            f"¿Estás seguro de eliminar la capa '{layer_name}'? (s/n): ",
            'yellow', attrs=['bold'])).lower().strip() == 's'

        if not confirm:
            display_message(
                "Operación cancelada por el usuario.", style='warning')
            return False

        acad.doc.Layers.Item(layer_name).Delete()
        display_message(
            f"La capa '{layer_name}' se eliminó satisfactoriamente.", style='success')
        return True
    except Exception as e:
        display_message(
            f"No se puede eliminar la capa '{layer_name}': {e}", style='error')
        return False


def list_layers(acad, show_unused=True, show_used=True):
    """Lista las capas disponibles del dibujo, con opción de mostrar usadas o no usadas."""
    # Obtener todas las capas
    layers = acad.doc.Layers
    layer_names = [layer.Name for layer in layers]

    # Verificar qué capas están en uso
    used_layers = set()

    # Primero contar los objetos totales para la barra de progreso
    console.print("[yellow]Contando objetos del dibujo...[/yellow]")
    all_objects = list(acad.iter_objects())
    total_objects = len(all_objects)

    # Usar barra de progreso de rich
    with console.status(f"[bold green]Procesando {total_objects} objetos...") as status:
        with progress:
            task = progress.add_task(
                "[cyan]Analizando capas...", total=total_objects)

            for i, obj in enumerate(all_objects):
                try:
                    if hasattr(obj, "Layer"):
                        used_layers.add(obj.Layer)
                except Exception as e:
                    console.print(
                        f"[red]Error al procesar objeto: {str(e)}[/red]")

                progress.update(task, completed=i+1)

    results = {
        "used": sorted(used_layers) if show_used else [],
        "unused": sorted(set(layer_names) - used_layers) if show_unused else [],
        "all": layer_names,
        "counts": {
            "used": len(used_layers),
            "unused": len(set(layer_names) - used_layers),
            "total": len(layer_names)
        }
    }

    console.print(
        f"[green]✓ Análisis completado: {results['counts']['used']} capas usadas, {results['counts']['unused']} sin usar[/green]")

    return results
