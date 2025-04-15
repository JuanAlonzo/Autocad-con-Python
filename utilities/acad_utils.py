"""
Módulo para extraer texto y coordenadas de objetos de AutoCAD en una capa específica.
Este módulo permite extraer texto y coordenadas de objetos de texto en AutoCAD, mostrando los resultados en una tabla.
También permite exportar los datos a archivos CSV o Excel.
"""

from rich.table import Table
from rich import box
from utilities.acad_common import console, progress, display_message
import pandas as pd
from datetime import datetime
import os
import csv


def extract_text_and_coordinates(acad, layer_name, text_type="all", case_sensitive=False):
    """
    Extrae texto y coordenadas de los objetos de texto en la capa especificada.

    Args:
        acad: Objeto AutoCAD inicializado
        layer_name: Nombre de la capa a procesar
        text_type: Tipo de texto a extraer ("all", "text", "mtext")
        case_sensitive: Si es True, la comparación de capas será sensible a mayúsculas/minúsculas

    Returns:
        list: Lista de tuplas (contenido, x, y) con el texto y coordenadas
    """
    data = []
    object_types = []

    if text_type == "all":
        object_types = ["AcDbText", "AcDbMText"]
    elif text_type == "text":
        object_types = ["AcDbText"]
    elif text_type == "mtext":
        object_types = ["AcDbMText"]
    else:
        display_message(
            f"Tipo de texto '{text_type}' no válido. Usando 'all'.", style='warning')
        object_types = ["AcDbText", "AcDbMText"]

    # Contar objetos primero para mostrar progreso
    console.print("[yellow]Contando objetos del dibujo...[/yellow]")
    all_objects = list(acad.iter_objects())
    matching_objects = []

    for obj in all_objects:
        try:
            if hasattr(obj, "Layer") and hasattr(obj, "ObjectName"):
                layer_matches = obj.Layer == layer_name if case_sensitive else obj.Layer.lower(
                ) == layer_name.lower()
                if layer_matches and obj.ObjectName in object_types:
                    matching_objects.append(obj)
        except Exception:
            pass

    total_objects = len(matching_objects)
    console.print(
        f"[green]Se encontraron {total_objects} objetos de texto en la capa '{layer_name}'[/green]")

    if total_objects == 0:
        return data

    # Usar barra de progreso de rich para la extracción
    with console.status(f"[bold green]Procesando {total_objects} textos...") as status:
        with progress:
            task = progress.add_task(
                "[cyan]Extrayendo texto...", total=total_objects)

            for i, obj in enumerate(matching_objects):
                try:
                    content = obj.TextString
                    x, y = obj.InsertionPoint[0:2]
                    data.append((content, x, y))
                except Exception as e:
                    console.print(
                        f"[red]Error al procesar objeto: {str(e)}[/red]")

                progress.update(task, completed=i+1)

    return data


def display_text_coordinates(data, layer_name):
    """
    Muestra las coordenadas de los textos extraídos en una tabla formateada.

    Args:
        data: Lista de tuplas (contenido, x, y)
        layer_name: Nombre de la capa procesada
    """
    if not data:
        console.print(
            "[yellow]No se encontraron textos para mostrar.[/yellow]")
        return

    table = Table(
        title=f"Coordenadas obtenidas en la capa '{layer_name}'",
        show_header=True,
        header_style="bold cyan",
        box=box.ROUNDED
    )

    table.add_column("#", style="dim", width=4)
    table.add_column("Texto", style="green")
    table.add_column("Coordenada X", style="blue", justify="right")
    table.add_column("Coordenada Y", style="blue", justify="right")

    for i, (content, x, y) in enumerate(data, 1):
        table.add_row(
            str(i),
            content,
            f"{x:.4f}",
            f"{y:.4f}"
        )
    console.print(table)
    console.print(
        f"[bold green]Total de objetos encontrados: {len(data)}[/bold green]")


def export_data_to_csv(data, layer_name, file_path=None):
    """
    Exporta los datos extraídos a un archivo CSV.

    Args:
        data: Lista de tuplas (contenido, x, y)
        layer_name: Nombre de la capa procesada
        file_path: Ruta del archivo CSV (opcional)

    Returns:
        str: Ruta del archivo creado
    """
    if not data:
        display_message("No hay datos para exportar.", style='warning')
        return None

    # Generar nombre de archivo por defecto si no se proporciona
    if file_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"texto_{layer_name}_{timestamp}.csv"

    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Texto', 'Coordenada X', 'Coordenada Y'])
            for content, x, y in data:
                writer.writerow([content, f"{x:.4f}", f"{y:.4f}"])

        display_message(
            f"Datos exportados exitosamente a {file_path}", style='success')
        return file_path

    except Exception as e:
        display_message(f"Error al exportar datos: {e}", style='error')
        return None


def export_data_to_excel(data, layer_name, file_path=None):
    """
    Exporta los datos extraídos a un archivo Excel.

    Args:
        data: Lista de tuplas (contenido, x, y)
        layer_name: Nombre de la capa procesada
        file_path: Ruta del archivo Excel (opcional)

    Returns:
        str: Ruta del archivo creado
    """
    try:
        import pandas as pd
    except ImportError:
        display_message(
            "Pandas no está instalado. No se puede exportar a Excel.", style='error')
        display_message(
            "Instálalo con: pip install pandas openpyxl", style='info')
        return None

    if not data:
        display_message("No hay datos para exportar.", style='warning')
        return None

    # Generar nombre de archivo por defecto si no se proporciona
    if file_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"texto_{layer_name}_{timestamp}.xlsx"

    try:
        df = pd.DataFrame(
            data, columns=['Texto', 'Coordenada X', 'Coordenada Y'])
        df.to_excel(file_path, index=False)

        display_message(
            f"Datos exportados exitosamente a {file_path}", style='success')
        return file_path

    except Exception as e:
        display_message(f"Error al exportar datos: {e}", style='error')
        return None

# Others


def display_postes_with_numbers(asignaciones, capa_poste, numeros):
    """Muestra los postes ordenados según la capa de numeración más cercana."""
    print("Postes ordenados segun capa de numeracion más cercana:")
    print("-" * 50)
    for numero, x, y in asignaciones:
        print(f"Poste {numero} →\n   Coordenadas: X= {x:.4f}, Y= {y:.4f}")
    print("-" * 50)
    print(
        f'Conteo total de postes en la capa "{capa_poste}" encontrados: {len(numeros)}')
