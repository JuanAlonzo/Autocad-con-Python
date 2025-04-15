"""
Módulo para asociar elementos en AutoCAD según diferentes criterios.
Contiene clases y funciones para relacionar elementos entre diferentes capas.
"""
import math
from rich.table import Table
from rich.console import Console
from rich import box
from rich.panel import Panel
from rich.text import Text
import pandas as pd
from datetime import datetime
import os
import csv
from utilities.acad_common import console, progress, display_message
from utilities.acad_utils import extract_text_and_coordinates


class ElementAssociator:
    """Clase para asociar elementos entre capas en AutoCAD."""

    def __init__(self, acad):
        """Inicializa el asociador de elementos con una instancia de AutoCAD.

        Args:
            acad: Instancia de AutoCAD inicializada
        """
        self.acad = acad
        self.source_elements = []
        self.target_elements = []
        self.associations = []
        self.source_layer = None
        self.target_layer = None
        # Distancia máxima permitida para asociar elementos
        self.max_distance = float('inf')

    def set_source_layer(self, layer_name):
        """Establece la capa de elementos fuente.

        Args:
            layer_name (str): Nombre de la capa de origen
        """
        self.source_layer = layer_name
        display_message(f"Capa fuente establecida: {layer_name}", style='info')

    def set_target_layer(self, layer_name):
        """Establece la capa de elementos destino (con numeración).

        Args:
            layer_name (str): Nombre de la capa destino
        """
        self.target_layer = layer_name
        display_message(
            f"Capa destino establecida: {layer_name}", style='info')

    def set_max_distance(self, distance):
        """Establece la distancia máxima para la asociación.

        Args:
            distance (float): Distancia máxima permitida
        """
        self.max_distance = distance
        display_message(
            f"Distancia máxima establecida: {distance}", style='info')

    def extract_source_elements(self, object_type="AcDbBlockReference"):
        """Extrae elementos de la capa fuente.

        Args:
            object_type (str): Tipo de objeto a extraer

        Returns:
            list: Lista de elementos extraídos
        """
        if not self.source_layer:
            display_message(
                "No se ha establecido una capa fuente", style='error')
            return []

        elements = []
        console.print(
            "[yellow]Extrayendo elementos de la capa fuente...[/yellow]")

        # Contar objetos para la barra de progreso
        all_objects = list(self.acad.iter_objects())
        matching_objects = []

        # Filtrar objetos que coinciden con los criterios
        for obj in all_objects:
            try:
                if hasattr(obj, "Layer") and obj.Layer == self.source_layer and obj.ObjectName == object_type:
                    matching_objects.append(obj)
            except Exception as e:
                console.print(f"[red]Error al filtrar objeto: {e}[/red]")

        total_objects = len(matching_objects)

        if total_objects == 0:
            display_message(
                f"No se encontraron elementos en la capa {self.source_layer}", style='warning')
            return []

        # Procesar objetos con barra de progreso
        with console.status(f"[bold green]Procesando {total_objects} elementos...") as status:
            with progress:
                task = progress.add_task(
                    "[cyan]Extrayendo elementos...", total=total_objects)

                for i, obj in enumerate(matching_objects):
                    try:
                        x, y = obj.InsertionPoint[0:2]
                        elements.append((x, y))
                        progress.update(task, completed=i+1)
                    except Exception as e:
                        console.print(
                            f"[red]Error al procesar elemento: {e}[/red]")

        self.source_elements = elements
        console.print(
            f"[green]Se extrajeron {len(elements)} elementos de la capa {self.source_layer}[/green]")
        return elements

    def extract_target_elements(self, object_type="AcDbText"):
        """Extrae elementos de la capa destino (números).

        Args:
            object_type (str): Tipo de objeto a extraer

        Returns:
            list: Lista de elementos extraídos con su numeración
        """
        if not self.target_layer:
            display_message(
                "No se ha establecido una capa destino", style='error')
            return []

        elements = []
        console.print("[yellow]Extrayendo elementos de numeración...[/yellow]")

        # Contar objetos para la barra de progreso
        all_objects = list(self.acad.iter_objects())
        matching_objects = []

        # Filtrar objetos que coinciden con los criterios
        for obj in all_objects:
            try:
                if hasattr(obj, "Layer") and obj.Layer == self.target_layer and obj.ObjectName == object_type:
                    matching_objects.append(obj)
            except Exception as e:
                console.print(f"[red]Error al filtrar objeto: {e}[/red]")

        total_objects = len(matching_objects)

        if total_objects == 0:
            display_message(
                f"No se encontraron elementos en la capa {self.target_layer}", style='warning')
            return []

        # Procesar objetos con barra de progreso
        with console.status(f"[bold green]Procesando {total_objects} elementos...") as status:
            with progress:
                task = progress.add_task(
                    "[cyan]Extrayendo numeración...", total=total_objects)

                for i, obj in enumerate(matching_objects):
                    try:
                        content = obj.TextString
                        x, y = obj.InsertionPoint[0:2]

                        try:
                            number = int(content)
                            elements.append((number, x, y))
                        except ValueError:
                            console.print(
                                f"[yellow]Advertencia: '{content}' no es un número entero válido[/yellow]")

                        progress.update(task, completed=i+1)
                    except Exception as e:
                        console.print(
                            f"[red]Error al procesar elemento: {e}[/red]")

        self.target_elements = elements
        console.print(
            f"[green]Se extrajeron {len(elements)} elementos de numeración de la capa {self.target_layer}[/green]")
        return elements

    def associate_by_proximity(self):
        """Asocia elementos por proximidad.

        Returns:
            list: Lista de asociaciones (número, x, y)
        """
        if not self.source_elements:
            display_message(
                "No hay elementos fuente para asociar", style='error')
            return []

        if not self.target_elements:
            display_message(
                "No hay elementos destino para asociar", style='error')
            return []

        associations = []
        console.print("[yellow]Asociando elementos por proximidad...[/yellow]")

        with console.status("[bold green]Calculando asociaciones...") as status:
            with progress:
                task = progress.add_task(
                    "[cyan]Procesando...", total=len(self.source_elements))

                for i, (px, py) in enumerate(self.source_elements):
                    closest_number = None
                    min_distance = float('inf')

                    for number, nx, ny in self.target_elements:
                        distance = math.sqrt((px - nx) ** 2 + (py - ny) ** 2)
                        if distance < min_distance:
                            min_distance = distance
                            closest_number = number

                    # Solo asociar si la distancia está dentro del límite establecido
                    if closest_number is not None and min_distance <= self.max_distance:
                        associations.append((closest_number, px, py))

                    progress.update(task, completed=i+1)

        self.associations = sorted(associations, key=lambda x: x[0])
        console.print(
            f"[green]Se crearon {len(associations)} asociaciones[/green]")
        return self.associations

    def display_associations(self):
        """Muestra las asociaciones en una tabla formateada."""
        if not self.associations:
            display_message("No hay asociaciones para mostrar",
                            style='warning')
            return

        table = Table(
            title=f"Elementos de {self.source_layer} ordenados según {self.target_layer}",
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED
        )

        table.add_column("Número", style="cyan", justify="right")
        table.add_column("Coordenada X", style="green", justify="right")
        table.add_column("Coordenada Y", style="green", justify="right")

        for number, x, y in self.associations:
            table.add_row(
                str(number),
                f"{x:.4f}",
                f"{y:.4f}"
            )

        console.print(table)
        console.print(
            f"[bold green]Total de elementos asociados: {len(self.associations)}[/bold green]")

    def export_to_csv(self, file_path=None):
        """Exporta las asociaciones a un archivo CSV.

        Args:
            file_path (str, optional): Ruta del archivo CSV

        Returns:
            str: Ruta del archivo creado
        """
        if not self.associations:
            display_message(
                "No hay asociaciones para exportar", style='warning')
            return None

        # Generar nombre de archivo por defecto si no se proporciona
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"asociaciones_{self.source_layer}_{self.target_layer}_{timestamp}.csv"

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Número', 'Coordenada X', 'Coordenada Y'])
                for number, x, y in self.associations:
                    writer.writerow([number, f"{x:.4f}", f"{y:.4f}"])

            display_message(
                f"Datos exportados exitosamente a {file_path}", style='success')
            return file_path
        except Exception as e:
            display_message(f"Error al exportar datos: {e}", style='error')
            return None

    def export_to_excel(self, file_path=None):
        """Exporta las asociaciones a un archivo Excel.

        Args:
            file_path (str, optional): Ruta del archivo Excel

        Returns:
            str: Ruta del archivo creado
        """
        if not self.associations:
            display_message(
                "No hay asociaciones para exportar", style='warning')
            return None

        try:
            import pandas as pd
        except ImportError:
            display_message(
                "Pandas no está instalado. No se puede exportar a Excel.", style='error')
            display_message(
                "Instálalo con: pip install pandas openpyxl", style='info')
            return None

        # Generar nombre de archivo por defecto si no se proporciona
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"asociaciones_{self.source_layer}_{self.target_layer}_{timestamp}.xlsx"

        try:
            df = pd.DataFrame(self.associations, columns=[
                              'Número', 'Coordenada X', 'Coordenada Y'])
            df.to_excel(file_path, index=False)

            display_message(
                f"Datos exportados exitosamente a {file_path}", style='success')
            return file_path
        except Exception as e:
            display_message(f"Error al exportar datos: {e}", style='error')
            return None


def show_export_menu(associations, source_layer, target_layer):
    """Muestra un menú para exportar los datos asociados.

    Args:
        associations: Lista de asociaciones (número, x, y)
        source_layer: Nombre de la capa fuente
        target_layer: Nombre de la capa destino

    Returns:
        str: Ruta del archivo exportado o None
    """
    if not associations:
        display_message("No hay datos para exportar", style='warning')
        return None

    associator = ElementAssociator(None)
    associator.associations = associations
    associator.source_layer = source_layer
    associator.target_layer = target_layer

    while True:
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
            return associator.export_to_csv()
        elif option == "2":
            return associator.export_to_excel()
        elif option == "3":
            display_message("No se exportaron datos.", style='info')
            return None
        else:
            display_message(
                "Opción no válida. Intenta de nuevo.", style='error')


class EnhancedElementAssociator(ElementAssociator):
    """Clase mejorada para asociar elementos con soporte para capas adicionales de texto.

    Esta clase extiende la funcionalidad básica de ElementAssociator añadiendo
    capacidades para gestionar capas adicionales de texto, vincularlas a elementos
    numerados y exportar los datos enriquecidos.

    Atributos:
        additional_layers (list): Lista de capas adicionales para extraer texto
        additional_elements (dict): Diccionario que almacena los textos extraídos por capa
    """

    def __init__(self, acad):
        """Inicializa el asociador de elementos mejorado."""
        super().__init__(acad)
        self.additional_layers = []
        self.additional_elements = {}

    def add_additional_layer(self, layer_name):
        """Agrega una capa adicional para extraer textos.

        Args:
            layer_name (str): Nombre de la capa adicional
        """
        self.additional_layers.append(layer_name)
        display_message(
            f"Capa adicional agregada: {layer_name}", style='info')

    def extract_additional_elements(self, text_type="all"):
        """Extrae elementos adicionales (textos) de las capas adicionales.

        Args:
            text_type (str): Tipo de texto a extraer ("all", "text", "mtext")

        Returns:
            dict: Diccionario con los elementos extraídos por capa
        """
        for layer in self.additional_layers:
            display_message(
                f"Extrayendo textos de capa: {layer}", style='info')
            texts = extract_text_and_coordinates(self.acad, layer, text_type)
            self.additional_elements[layer] = texts
            console.print(
                f"[green]Se extrajeron {len(texts)} textos de la capa {layer}[/green]")

        return self.additional_elements

    def display_enhanced_associations(self):
        """
        Muestra una tabla mejorada con las asociaciones y solo el texto más cercano.
        Si se desea adaptar a mostrar todos los textos asociados, se puede modificar el método (Actualmente ###).

        Args:
            decimal_places (int): Número de decimales para mostrar en las coordenadas y distancias
            highlight_color (str): Color para resaltar elementos sin texto asociado
            show_empty (bool): Si es True, muestra filas para elementos sin texto asociado
        """
        if not self.associations:
            display_message("No hay asociaciones para mostrar",
                            style='warning')
            return

        # Crear primero la tabla básica
        super().display_associations()

        # Si hay elementos adicionales, mostrarlos
        for layer_name, texts in self.additional_elements.items():
            if not texts:
                continue

            # Crear un diccionario para rápido acceso por coordenadas aproximadas
            closest_texts = {}

            for content, tx, ty in texts:
                # Usamos un sistema de coordenadas aproximadas para la asociación
                for number, x, y in self.associations:
                    distance = ((tx - x) ** 2 + (ty - y) ** 2) ** 0.5
                    if distance <= self.max_distance:
                        if number not in closest_texts or distance < closest_texts[number][1]:
                            closest_texts[number] = (content, distance)
                    # if distance <= self.max_distance:
                    #     if number not in closest_texts:
                    #         closest_texts[number] = []
                    #     closest_texts[number].append((content, tx, ty, distance))

            # Ahora mostramos la tabla de textos asociados
            table = Table(
                title=f"Textos de {layer_name} asociados a {self.target_layer}",
                show_header=True,
                header_style="bold cyan",
                box=box.ROUNDED
            )

            table.add_column("Número", style="cyan", justify="right")
            table.add_column("Texto Más Cercano", style="green")
            table.add_column("Distancia", style="blue", justify="right")

            for number, x, y in sorted(self.associations, key=lambda a: a[0]):
                if number in closest_texts:
                    content, distance = closest_texts[number]
                    # texts_sorted = sorted(
                    #     closest_texts[number], key=lambda t: t[3])
                    # for content, tx, ty, distance in texts_sorted:
                    table.add_row(
                        str(number),
                        content,
                        f"{distance:.4f}"
                    )
                else:
                    table.add_row(
                        str(number), "[red]Sin texto asociado[/red]", "-")

            console.print(table)

    def export_enhanced_data(self, file_path=None, format='csv'):
        """Exporta los datos mejorados incluyendo textos adicionales.

        Args:
            file_path (str, optional): Ruta del archivo a exportar
            format (str): Formato ('csv' o 'excel')

        Returns:
            str: Ruta del archivo creado
        """
        if not self.associations:
            display_message("No hay datos para exportar", style='warning')
            return None

        # Preparar datos para exportación
        export_data = []
        headers = ['Número', 'Coordenada X', 'Coordenada Y']

        # Agregar encabezados para cada capa adicional
        for layer in self.additional_layers:
            if layer in self.additional_elements and self.additional_elements[layer]:
                headers.append(f'Texto ({layer})')

        # Crear diccionarios de búsqueda rápida para cada capa
        layer_text_dicts = {}
        for layer, texts in self.additional_elements.items():
            text_dict = {}
            for content, tx, ty in texts:
                # Asociar cada texto con el número más cercano
                for number, x, y in self.associations:
                    distance = ((tx - x) ** 2 + (ty - y) ** 2) ** 0.5
                    if distance <= self.max_distance:
                        if number not in text_dict or distance < text_dict[number][1]:
                            text_dict[number] = (content, distance)
            layer_text_dicts[layer] = text_dict

        # Crear filas de datos para exportación
        for number, x, y in sorted(self.associations, key=lambda a: a[0]):
            row = [number, f"{x:.4f}", f"{y:.4f}"]

            # Agregar texto de cada capa adicional si está disponible
            for layer in self.additional_layers:
                if layer in layer_text_dicts and number in layer_text_dicts[layer]:
                    row.append(layer_text_dicts[layer][number][0])
                else:
                    row.append("")

            export_data.append(row)

        # Exportar según formato
        timestamp = self._get_timestamp()

        if format.lower() == 'csv':
            if file_path is None:
                file_path = f"asociaciones_mejoradas_{self.source_layer}_{timestamp}.csv"
            return self._export_to_csv(export_data, headers, file_path)
        else:
            if file_path is None:
                file_path = f"asociaciones_mejoradas_{self.source_layer}_{timestamp}.xlsx"
            return self._export_to_excel(export_data, headers, file_path)

    def _get_timestamp(self):
        """Obtiene una marca de tiempo para el nombre del archivo."""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _export_to_csv(self, data, headers, file_path):
        """Exporta los datos a CSV."""
        import csv

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                for row in data:
                    writer.writerow(row)

            display_message(
                f"Datos exportados exitosamente a {file_path}", style='success')
            return file_path
        except Exception as e:
            display_message(f"Error al exportar datos: {e}", style='error')
            return None

    def _export_to_excel(self, data, headers, file_path):
        """Exporta los datos a Excel."""
        try:
            import pandas as pd
        except ImportError:
            display_message(
                "Pandas no está instalado. No se puede exportar a Excel.", style='error')
            display_message(
                "Instálalo con: pip install pandas openpyxl", style='info')
            return None

        try:
            df = pd.DataFrame(data, columns=headers)
            df.to_excel(file_path, index=False)

            display_message(
                f"Datos exportados exitosamente a {file_path}", style='success')
            return file_path
        except Exception as e:
            display_message(f"Error al exportar datos: {e}", style='error')
            return None


def show_enhanced_export_menu(associator):
    """Muestra un menú mejorado para exportar los datos asociados.

    Args:
        associator: Instancia de EnhancedElementAssociator

    Returns:
        str: Ruta del archivo exportado o None
    """
    if not associator.associations:
        display_message("No hay datos para exportar", style='warning')
        return None

    while True:
        console.print(Panel(
            Text("OPCIONES DE EXPORTACIÓN MEJORADA", style="bold white"),
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
            return associator.export_enhanced_data(format='csv')
        elif option == "2":
            return associator.export_enhanced_data(format='excel')
        elif option == "3":
            display_message("No se exportaron datos.", style='info')
            return None
        else:
            display_message(
                "Opción no válida. Intenta de nuevo.", style='error')


def select_additional_layers(acad, layers_disponibles, primary_layers):
    """Permite seleccionar capas adicionales de texto para extraer información.

    Args:
        acad: Instancia de AutoCAD
        layers_disponibles: Lista de capas disponibles
        primary_layers: Lista de capas ya seleccionadas que se deben excluir

    Returns:
        list: Lista de capas adicionales seleccionadas
    """
    additional_layers = []

    console.print(Panel(
        Text("SELECCIÓN DE CAPAS ADICIONALES DE TEXTO", style="bold white"),
        subtitle="Selecciona capas con textos complementarios",
        border_style="green"
    ))

    while True:
        # Mostrar capas disponibles excluyendo las ya seleccionadas
        available = [
            l for l in layers_disponibles if l not in primary_layers and l not in additional_layers]

        if not available:
            display_message(
                "No hay más capas disponibles para seleccionar", style='warning')
            break

        display_message("\nCapas disponibles:", style='info')
        # Crear tabla Rich para mostrar las capas disponibles
        table = Table(title="Capas Disponibles",
                      show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Nombre de Capa", style="cyan")

        for i, layer in enumerate(available, 1):
            table.add_row(str(i), layer)
        console.print(table)

        # Solicitar selección o terminar
        input_prompt = "\nEscribe el número o nombre de la capa adicional (o 'listo' para terminar): "
        layer_input = display_message(
            input_prompt, style='input', use_rich=True).strip()

        if layer_input.lower() == 'listo':
            break

        # Verificar si ingresó un número
        if layer_input.isdigit():
            idx = int(layer_input) - 1
            if 0 <= idx < len(available):
                selected = available[idx]
                additional_layers.append(selected)
                display_message(f"Capa '{selected}' agregada", style='success')
            else:
                display_message("Número fuera de rango", style='error')
        else:
            # Verificar por nombre
            if layer_input in available:
                additional_layers.append(layer_input)
                display_message(
                    f"Capa '{layer_input}' agregada", style='success')
            else:
                display_message(
                    f"La capa '{layer_input}' no existe o ya fue seleccionada", style='error')

    return additional_layers
