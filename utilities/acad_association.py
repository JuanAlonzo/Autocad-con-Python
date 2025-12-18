"""
Módulo de Asociación: acad_association.py
Responsabilidad: Asociar elementos (bloques) con textos (numeración) por proximidad.
Usa las nuevas herramientas de Entidades y Exportación.
"""
import math
from .acad_common import console, progress
from .acad_io import display_message, display_table, get_selection_from_list
from .acad_entities import extract_text_data, extract_block_data
from .acad_export import show_export_menu


class ElementAssociator:
    def __init__(self, acad):
        self.acad = acad
        self.source_elements = []  # Lista de (x, y)
        self.target_elements = []  # Lista de (número, x, y)
        self.associations = []    # Lista de (número, x, y)
        self.source_layer = None
        self.target_layer = None
        self.max_distance = float('inf')

    def set_source_layer(self, layer_name):
        self.source_layer = layer_name
        display_message(f"Capa fuente establecida: {layer_name}", 'info')

    def set_target_layer(self, layer_name):
        self.target_layer = layer_name
        display_message(f"Capa destino establecida: {layer_name}", 'info')

    def set_max_distance(self, distance):
        self.max_distance = distance
        msg = str(distance) if distance != float('inf') else "Sin limite"
        display_message(
            f"Distancia máxima: {msg}", 'info')

    def extract_source_elements(self):
        if not self.source_layer:
            return []

        # Usamos la nueva función centralizada.
        # extract_block_data devuelve diccionarios completos, aquí solo necesitamos X e Y.
        raw_data = extract_block_data(self.acad, self.source_layer)

        self.source_elements = [(d['X'], d['Y']) for d in raw_data]
        return self.source_elements

    def extract_target_elements(self):
        """Extrae números de textos."""
        if not self.target_layer:
            return []

        raw_texts = extract_text_data(self.acad, self.target_layer)

        elements = []
        with progress:
            task = progress.add_task(
                "[cyan]Validando números...[/cyan]", total=len(raw_texts))
            for content, x, y in raw_texts:
                try:
                    num = int(content)  # Intentamos convertir a entero
                    elements.append((num, x, y))
                except ValueError:
                    pass  # Ignoramos textos que no sean números (ej. "POSTE")
                progress.advance(task)

        self.target_elements = elements
        display_message(
            f"Se validaron {len(elements)} números correctos.", 'success')
        return elements

    def associate_by_proximity(self):
        """
        Core del algoritmo: Busca el número más cercano a cada bloque.
        """
        if not self.source_elements or not self.target_elements:
            display_message(
                "Faltan datos para realizar la asociacion", 'error')
            return []

        associations = []

        with progress:
            task = progress.add_task(
                "[magenta]Calculando distancias...[/magenta]", total=len(self.source_elements))

            for px, py in self.source_elements:
                closest_num = None
                min_dist = float('inf')

                # Buscamos el número más cercano (Fuerza bruta optimizada)
                for num, nx, ny in self.target_elements:
                    # Distancia euclidiana
                    dist = math.hypot(px - nx, py - ny)
                    if dist < min_dist:
                        min_dist = dist
                        closest_num = num

                # Solo guardamos si cumple la distancia máxima
                if closest_num is not None and min_dist <= self.max_distance:
                    associations.append((closest_num, px, py))

                progress.advance(task)

        self.associations = sorted(associations, key=lambda x: x[0])
        display_message(
            f"Asociaciones creadas con exito: {len(associations)}", 'success')
        return self.associations

    def display_associations(self):
        """Muestra tabla de resultados."""
        if not self.associations:
            return

        # Formateamos los datos para la tabla de acad_io
        rows = [[str(num), f"{x:.4f}", f"{y:.4f}"]
                for num, x, y in self.associations]
        display_table("Resultados de Asociación", [
                      "Número", "Coord X", "Coord Y"], rows)

    def export_data(self):
        """Usa el nuevo módulo de exportación."""
        if not self.associations:
            return

        data_to_export = [
            {'Número': n, 'Coordenada X': x, 'Coordenada Y': y}
            for n, x, y in self.associations
        ]

        show_export_menu(data_to_export, f"asociacion_{self.source_layer}")


class EnhancedElementAssociator(ElementAssociator):
    """
    Extensión para agregar capas de texto adicionales (ej. Material, Altura)
    a la asociación principal.
    """

    def __init__(self, acad):
        super().__init__(acad)
        self.additional_layers = []
        self.additional_data = {}  # {layer_name: [(txt, x, y), ...]}
        self._last_enhanced_data = []  # Caché para exportación

    def add_additional_layer(self, layer_name):
        self.additional_layers.append(layer_name)

    def extract_additional_elements(self):
        """Extrae elementos adicionales (textos) de las capas adicionales.
        """
        for layer in self.additional_layers:
            self.additional_data[layer] = extract_text_data(self.acad, layer)

    def display_enhanced_associations(self):
        """Genera y muestra una tabla cruzando Bloque -> Número -> Textos Extra."""
        if not self.associations:
            return

        display_message("Generando matriz de datos cruzada...", "info")

        rows = []
        # Iteramos sobre los bloques ya asociados
        for num, bx, by in self.associations:
            row_visual = [str(num), f"{bx:.2f}", f"{by:.2f}"]

            # Para este bloque, buscamos el texto más cercano en cada capa adicional
            row_data = {"Número": num, "X": bx, "Y": by}

            for layer in self.additional_layers:
                texts = self.additional_data.get(layer, [])
                best_txt = "-"
                best_dist = self.max_distance

                for txt, tx, ty in texts:
                    dist = math.hypot(bx-tx, by-ty)
                    if dist < best_dist:
                        best_dist = dist
                        best_txt = txt

                row_visual.append(best_txt)
                row_data[layer] = best_txt

            rows.append(row_visual)
            self._last_enhanced_data.append(row_data)

        # Headers dinámicos para la tabla
        headers = ["Num", "X", "Y"] + self.additional_layers
        display_table("Asociación Avanzada (Datos Cruzados)", headers, rows)

    def export_enhanced_data(self):
        """Exporta la tabla completa con columnas extras."""
        if self._last_enhanced_data:
            show_export_menu(self._last_enhanced_data, "asociacion_completa")
        else:
            super().export_data()


def select_additional_layers_interactive(acad, layers_disponibles, exclude_layers):
    """
    Bucle interactivo para seleccionar múltiples capas extras.
    Reemplaza la lógica antigua de 'while True: input...'
    """
    seleccionadas = []
    while True:
        # Filtramos las capas que ya no se pueden elegir
        prohibidas = exclude_layers + seleccionadas
        disponibles = [l for l in layers_disponibles if l not in prohibidas]

        if not disponibles:
            break

        # Opción especial para salir
        opciones = ["(TERMINAR SELECCIÓN)"] + disponibles

        choice = get_selection_from_list(
            "Seleccione Capa Adicional de Texto",
            opciones
        )

        if not choice or choice == "(TERMINAR SELECCIÓN)":
            break

        seleccionadas.append(choice)
        display_message(f"Capa '{choice}' agregada.", "success")

    return seleccionadas
