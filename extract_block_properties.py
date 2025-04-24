"""
"""

from utilities.acad_common import (
    initialized_autocad, display_message,
    get_available_layers,
    get_valid_layer_input,
    display_message,
    console
)
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
import pandas as pd
from datetime import datetime
import os
import csv


def extract_block_properties(acad, layer_name=None):
    """
    Extrae las propiedades de los bloques de una capa específica o de todas las capas.

    Args:
        acad: Objeto de AutoCAD inicializado
        layer_name: Nombre de la capa (opcional, si es None extrae de todas)

    Returns:
        list: Lista de diccionarios con las propiedades de cada bloque
    """
    blocks_data = []

    # Contar objetos para la barra de progreso
    console.print("[yellow]Contando bloques en el dibujo...[/yellow]")

    blocks_to_process = []
    for obj in acad.iter_objects():
        try:
            if obj.ObjectName == "AcDbBlockReference":
                if layer_name is None or obj.Layer == layer_name:
                    blocks_to_process.append(obj)
        except Exception as e:
            console.print(f"[red]Error al filtrar bloque: {str(e)}[/red]")

    total_blocks = len(blocks_to_process)
    console.print(
        f"[green]Se encontraron {total_blocks} bloques{' en la capa ' + layer_name if layer_name else ''}[/green]")

    if total_blocks == 0:
        return []

    # Procesar cada bloque con barra de progreso
    with console.status(f"[bold green]Procesando {total_blocks} bloques...") as status:
        for i, block in enumerate(blocks_to_process):
            try:
                block_data = {
                    "Layer": block.Layer,
                    "Name": getattr(block, "Name", "Unknown"),
                    "Position_X": block.InsertionPoint[0],
                    "Position_Y": block.InsertionPoint[1],
                    "Position_Z": block.InsertionPoint[2],
                    "Rotation": getattr(block, "Rotation", 0),
                    "Scale_X": getattr(block, "XScale", 1),
                    "Scale_Y": getattr(block, "YScale", 1),
                    "Scale_Z": getattr(block, "ZScale", 1),
                    "Color": getattr(block, "Color", 0),
                    "Linetype": getattr(block, "Linetype", ""),
                    "LinetypeScale": getattr(block, "LinetypeScale", 1),
                }

                # Extraer atributos si los tiene
                attributes = {}
                try:
                    if hasattr(block, "GetAttributes"):
                        for attrib in block.GetAttributes():
                            attributes[attrib.TagString] = attrib.TextString
                except Exception as e:
                    console.print(
                        f"[yellow]No se pudieron extraer atributos: {str(e)}[/yellow]")

                # Añadir atributos al diccionario principal
                block_data["Attributes"] = attributes

                # Añadir el bloque a la lista
                blocks_data.append(block_data)

                # Actualizar progreso
                if i % 10 == 0 or i == total_blocks - 1:
                    console.print(
                        f"[cyan]Procesados {i+1}/{total_blocks} bloques[/cyan]")

            except Exception as e:
                console.print(f"[red]Error al procesar bloque: {str(e)}[/red]")

    return blocks_data


def display_blocks_table(blocks_data, max_blocks=20):
    """
    Muestra una tabla formateada con la información de los bloques.

    Args:
        blocks_data: Lista de diccionarios con propiedades de bloques
        max_blocks: Máximo número de bloques a mostrar (por defecto 20)
    """
    if not blocks_data:
        console.print("[yellow]No hay bloques para mostrar.[/yellow]")
        return

    # Crear tabla principal
    table = Table(
        title=f"Propiedades de Bloques ({len(blocks_data)} bloques)",
        show_header=True,
        header_style="bold cyan",
        box=box.ROUNDED
    )

    # Añadir columnas
    table.add_column("#", style="dim", width=4)
    table.add_column("Nombre", style="green")
    table.add_column("Capa", style="blue")
    table.add_column("Posición X", style="magenta", justify="right")
    table.add_column("Posición Y", style="magenta", justify="right")
    table.add_column("Escala", style="yellow", justify="right")
    table.add_column("Atributos", style="cyan")

    # Limitar la cantidad de bloques a mostrar
    display_blocks = blocks_data[:max_blocks]

    for i, block in enumerate(display_blocks, 1):
        # Convertir atributos a texto
        attrs_text = ""
        if block["Attributes"]:
            attrs_list = [f"{k}: {v}" for k, v in block["Attributes"].items()]
            # Mostrar solo los primeros 2 atributos
            attrs_text = ", ".join(attrs_list[:2])
            if len(block["Attributes"]) > 2:
                attrs_text += f"... (+{len(block["Attributes"])-2})"
        else:
            attrs_text = "[dim]Sin atributos[/dim]"

        # Añadir fila a la tabla
        table.add_row(
            str(i),
            str(block["Name"]),
            block["Layer"],
            f"{block['Position_X']:.4f}",
            f"{block['Position_Y']:.4f}",
            f"{block['Scale_X']:.4f}",
            attrs_text
        )

    if len(blocks_data) > max_blocks:
        console.print(
            f"[italic]Mostrando {max_blocks} de {len(blocks_data)} bloques. Exporta los resultados para ver todos.[/italic]")

    console.print(table)


def export_blocks_to_csv(blocks_data, file_path=None):
    """
    Exporta las propiedades de los bloques a un archivo CSV.

    Args:
        blocks_data: Lista de diccionarios con propiedades de bloques
        file_path: Ruta del archivo CSV (opcional)

    Returns:
        str: Ruta del archivo creado
    """
    if not blocks_data:
        display_message("No hay datos para exportar.", style='warning')
        return None

    # Generar nombre de archivo por defecto si no se proporciona
    if file_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"bloques_{timestamp}.csv"

    try:
        # Preparar datos para exportación
        export_rows = []
        all_attribute_keys = set()

        # Recopilar todos los nombres de atributos
        for block in blocks_data:
            if block["Attributes"]:
                all_attribute_keys.update(block["Attributes"].keys())

        attribute_keys = sorted(list(all_attribute_keys))

        # Crear encabezados
        headers = ["Nombre", "Capa", "Posición_X", "Posición_Y", "Posición_Z",
                   "Rotación", "Escala_X", "Escala_Y", "Escala_Z", "Color",
                   "Tipo_Línea", "Escala_Línea"]

        # Añadir encabezados de atributos
        for key in attribute_keys:
            headers.append(f"Atrib_{key}")

        # Crear filas de datos
        for block in blocks_data:
            row = [
                block["Name"],
                block["Layer"],
                block["Position_X"],
                block["Position_Y"],
                block["Position_Z"],
                block["Rotation"],
                block["Scale_X"],
                block["Scale_Y"],
                block["Scale_Z"],
                block["Color"],
                block["Linetype"],
                block["LinetypeScale"]
            ]

            # Añadir valores de atributos
            for key in attribute_keys:
                if block["Attributes"] and key in block["Attributes"]:
                    row.append(block["Attributes"][key])
                else:
                    row.append("")

            export_rows.append(row)

        # Escribir archivo CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(export_rows)

        display_message(
            f"Datos exportados exitosamente a {file_path}", style='success')
        return file_path

    except Exception as e:
        display_message(f"Error al exportar datos: {e}", style='error')
        return None


def export_blocks_to_excel(blocks_data, file_path=None):
    """
    Exporta las propiedades de los bloques a un archivo Excel.

    Args:
        blocks_data: Lista de diccionarios con propiedades de bloques
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

    if not blocks_data:
        display_message("No hay datos para exportar.", style='warning')
        return None

    # Generar nombre de archivo por defecto si no se proporciona
    if file_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"bloques_{timestamp}.xlsx"

    try:
        # Preparar datos para exportación
        export_data = []
        all_attribute_keys = set()

        # Recopilar todos los nombres de atributos
        for block in blocks_data:
            if block["Attributes"]:
                all_attribute_keys.update(block["Attributes"].keys())

        attribute_keys = sorted(list(all_attribute_keys))

        # Crear filas de datos
        for block in blocks_data:
            row_data = {
                "Nombre": block["Name"],
                "Capa": block["Layer"],
                "Posición_X": block["Position_X"],
                "Posición_Y": block["Position_Y"],
                "Posición_Z": block["Position_Z"],
                "Rotación": block["Rotation"],
                "Escala_X": block["Scale_X"],
                "Escala_Y": block["Scale_Y"],
                "Escala_Z": block["Scale_Z"],
                "Color": block["Color"],
                "Tipo_Línea": block["Linetype"],
                "Escala_Línea": block["LinetypeScale"],
            }

            # Añadir valores de atributos
            for key in attribute_keys:
                if block["Attributes"] and key in block["Attributes"]:
                    row_data[f"Atrib_{key}"] = block["Attributes"][key]
                else:
                    row_data[f"Atrib_{key}"] = ""

            export_data.append(row_data)

        # Crear DataFrame y exportar a Excel
        df = pd.DataFrame(export_data)
        df.to_excel(file_path, index=False)

        display_message(
            f"Datos exportados exitosamente a {file_path}", style='success')
        return file_path

    except Exception as e:
        display_message(f"Error al exportar datos: {e}", style='error')
        return None


def show_export_menu(blocks_data):
    """Muestra un menú para exportar los datos de los bloques."""
    console.print(Panel(
        Text("OPCIONES DE EXPORTACIÓN", style="bold white"),
        subtitle="Selecciona una opción",
        border_style="cyan"
    ))

    console.print("[1] Exportar a CSV")
    console.print("[2] Exportar a Excel")
    console.print("[3] Volver sin exportar")

    option = display_message(
        "\nElige una opción (1-3): ",
        style='input',
        use_rich=True
    ).strip()

    if option == "1":
        return export_blocks_to_csv(blocks_data)
    elif option == "2":
        return export_blocks_to_excel(blocks_data)
    elif option == "3":
        display_message("No se exportaron datos.", style='info')
        return None
    else:
        display_message("Opción no válida. Intenta de nuevo.", style='error')
        return show_export_menu(blocks_data)


def main():
    """Función principal del programa."""
    acad = initialized_autocad(display_message(
        "Programa para Extraer Propiedades de Bloques", style='info', bold=True))
    if not acad:
        display_message(
            "\nNo se puede continuar sin una conexión a AutoCAD.", style='error')
        display_message("Presione Enter para salir...",
                        style='input', use_rich=True)
        return

    try:
        # Mostrar panel informativo
        console.print(Panel(
            Text("""
Este programa extrae las propiedades de los bloques en AutoCAD, incluyendo:
- Información de posición y geometría (coordenadas, escala, rotación)
- Capa y propiedades visuales
- Atributos asociados al bloque
- Nombre del bloque y otras propiedades

Puedes extraer bloques de una capa específica o de todas las capas.
Los resultados pueden exportarse a CSV o Excel para análisis posterior.
            """, style="white"),
            title="EXTRACTOR DE PROPIEDADES DE BLOQUES",
            border_style="blue"))

        # Opciones de selección
        console.print(Panel(
            Text("OPCIONES DE SELECCIÓN", style="bold white"),
            subtitle="Selecciona una opción",
            border_style="green"
        ))

        console.print("[1] Extraer bloques de una capa específica")
        console.print("[2] Extraer bloques de todas las capas")

        option = display_message(
            "\nElige una opción (1-2): ",
            style='input',
            use_rich=True
        ).strip()

        layer_name = None
        if option == "1":
            layers_disponibles = get_available_layers(acad)
            layer_name = get_valid_layer_input(
                "Selecciona la capa que contiene los bloques a extraer",
                layers_disponibles,
                show_table=True
            )
            if layer_name is None:
                display_message("Operación cancelada.", style='warning')
                return
        elif option == "2":
            display_message(
                "Se extraerán bloques de todas las capas.", style='info')
        else:
            display_message(
                "Opción no válida. Se extraerán bloques de todas las capas.", style='warning')

        # Extraer propiedades de bloques
        blocks_data = extract_block_properties(acad, layer_name)

        if blocks_data:
            # Mostrar resultados en tabla
            display_blocks_table(blocks_data)

            # Preguntar si se quieren exportar los datos
            exportar = display_message(
                "\n¿Deseas exportar los resultados? (s/n): ",
                style='input',
                use_rich=True
            ).lower().strip()

            if exportar == 's':
                show_export_menu(blocks_data)
        else:
            if layer_name:
                display_message(
                    f"No se encontraron bloques en la capa '{layer_name}'", style='warning')
            else:
                display_message(
                    "No se encontraron bloques en el dibujo", style='warning')

        # Preguntar si desea continuar
        continuar = display_message(
            "\n¿Desea extraer más bloques? (s/n): ",
            style='input',
            use_rich=True
        ).lower().strip()

        if continuar == 's':
            main()  # Reiniciar el programa
        else:
            display_message(
                "Programa finalizado. ¡Hasta luego!", style='success')

    except KeyboardInterrupt:
        display_message(
            "\nOperación cancelada por el usuario.", style='warning')
    except Exception as e:
        display_message(f"Error inesperado: {e}", style='error')
        # Para depuración, mostrar el traceback completo
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
