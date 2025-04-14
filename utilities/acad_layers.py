from termcolor import colored
from rich import print as rprint
from utilities.acad_common import console, progress, validate_new_layer_name, is_layer_used, get_layer_color_dict


def get_valid_layer_name(cad_doc):
    """Solicita un nombre y valida si la capa ya existe."""
    while True:
        layer_name = input(colored(
            "\nIntroduce el nombre de la capa a crear (o 'salir' para terminar): ", 'white', attrs=['bold'])).strip()

        if layer_name.lower() == 'salir':
            print(colored("\nSaliendo del programa...",
                  'yellow', attrs=['bold']))
            return None

        if not layer_name or layer_name.isspace():
            print(colored("El nombre de la capa no puede estar vacío.", 'red'))
            continue

        for layer in cad_doc.Layers:
            if layer.Name == layer_name:
                print(
                    colored(f'Error: La capa "{layer_name}" ya existe.', 'white', 'on_red'))
                break
        else:
            return layer_name


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
                print(colored("El número de color debe estar entre 1 y 255.", 'red'))
        except ValueError:
            print(colored("Por favor, introduce un número válido para el color.", 'red'))


def create_layer(cad_doc, layer_name, color_num, color_dict=None):
    """Crea una nueva capa con el nombre y color especificados."""
    if color_dict is None:
        color_dict = get_layer_color_dict()

    try:
        new_layer = cad_doc.Layers.Add(layer_name)
        new_layer.Color = color_num
        color_name = color_dict.get(str(color_num), "Color no definido")
        print(colored(
            f'La capa "{layer_name}" ha sido creada con el color {color_num} ({color_name}).', 'green', attrs=['bold']))
        return new_layer
    except Exception as e:
        console.error(
            f"❌ Error al crear capa {layer_name}: {str(e)}")
        raise


def delete_layer(acad, layer_name, layers_disponibles):
    """Elimina una capa de AutoCAD si no está en uso.
    Solicita confirmación al usuario antes de eliminarla."""
    if layer_name not in layers_disponibles:
        print(colored(f"Error: La capa '{layer_name}' no existe.", 'red'))
        return False

    try:
        if is_layer_used(acad, layer_name):
            print(colored(
                f"La capa '{layer_name}' está en uso y no puede ser eliminada.", 'red'))
            return False

        confirm = input(colored(
            f"¿Estás seguro de eliminar la capa '{layer_name}'? (s/n): ",
            'yellow', attrs=['bold'])).lower().strip() == 's'

        if not confirm:
            print(colored("Operación cancelada por el usuario.", 'yellow'))
            return False

        acad.doc.Layers.Item(layer_name).Delete()
        print(colored(
            f"La capa '{layer_name}' se eliminó satisfactoriamente.", 'green'))
        return True
    except Exception as e:
        print(
            colored(f"No se puede eliminar la capa '{layer_name}': {e}", 'red'))
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
