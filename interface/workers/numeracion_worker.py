import pythoncom
from PySide6.QtCore import QThread, Signal
from utilities.cad_manager import cad
from utilities import geometry, entities, drawing, layers
from utilities.graph import NetworkGraph
from utilities.geometry import calculate_distance
from utilities.config import SETTINGS


class NumeracionWorker(QThread):
    """
    Hilo de trabajo secundario para ejecutar la numeración sin bloquear la UI.
    """

    progress_signal = Signal(int)
    log_signal = Signal(str)
    finished_signal = Signal(bool)

    def __init__(self, config_ui):
        super().__init__()
        self.cfg = config_ui

    def run(self):
        pythoncom.CoInitialize()
        cad.connect()
        try:
            estrategia = self.cfg.get("estrategia", "DFS")

            capa_destino = self.cfg.get("capa_destino")
            color_destino = self.cfg.get("color_destino")

            self.log_signal.emit(
                f"Preparando capa de destino '{capa_destino}' con color {color_destino}..."
            )

            layers.ensure_layer(capa_destino, color=color_destino)

            # TOPOLOGÍA (DFS)
            if estrategia == "DFS":
                self.log_signal.emit("Modo DFS Iniciado. Extrayendo red y postes...")
                segmentos = entities.extract_network_lines(self.cfg["dict_red"])
                todos_los_bloques = entities.extract_blocks()
                nombres_esperados = [
                    k.upper() for k in self.cfg.get("dict_postes", {}).keys()
                ]
                filtro_capa = self.cfg.get("filtro_capa")

                postes_validos = []
                for b in todos_los_bloques:
                    # nombre de bloque coincide?
                    nombre_match = b["Nombre"].upper() in nombres_esperados

                    # perfil exige una capa específica, coincide?
                    capa_match = True
                    if filtro_capa:
                        capa_match = b["Capa"].upper() == filtro_capa.upper()

                    # agregamos solo si pasa ambas pruebas
                    if nombre_match and capa_match:
                        postes_validos.append(b)

                if not segmentos or not postes_validos:
                    raise ValueError("Faltan datos de red o postes para ejecutar DFS.")

                self.log_signal.emit(
                    "Aplicando División de Aristas (Split) para postes intermedios..."
                )
                # Modificamos la topología antes de crear el grafo
                segmentos = geometry.split_segments_with_poles(
                    segmentos, postes_validos, tolerancia=1.5
                )

                self.progress_signal.emit(30)

                grafo = NetworkGraph(tolerance=self.cfg["tolerancia_grafo"])
                for p1, p2 in segmentos:
                    grafo.add_line(p1, p2)

                nodo_raiz, dist = grafo.find_nearest_node(
                    self.cfg["punto_inicio"], max_radius=self.cfg["radio_snap"]
                )
                if not nodo_raiz:
                    raise ValueError("Punto de inicio muy alejado de la red.")

                ruta_logica = grafo.dfs_traversal(nodo_raiz)
                self.progress_signal.emit(60)

                exitos = self._ejecutar_insercion_dfs(
                    ruta_logica, postes_validos, capa_destino
                )

            # BÚSQUEDA SIMPLE GEOMÉTRICA
            elif estrategia == "SIMPLE":
                self.log_signal.emit(
                    "Modo Simple Iniciado. Buscando bloques específicos..."
                )
                todos_los_bloques = entities.extract_blocks()
                nombres_esperados = [
                    k.upper() for k in self.cfg.get("dict_postes", {}).keys()
                ]
                filtro_capa = self.cfg.get("filtro_capa")

                postes_validos = []
                for b in todos_los_bloques:
                    # nombre del bloque coincide?
                    nombre_match = b["Nombre"].upper() in nombres_esperados

                    # perfil exige una capa específica, coincide?
                    capa_match = True
                    if filtro_capa:
                        capa_match = b["Capa"].upper() == filtro_capa.upper()

                    # agregamos si pasa ambas pruebas
                    if nombre_match and capa_match:
                        postes_validos.append(b)

                if not postes_validos:
                    raise ValueError(
                        "No se encontraron postes válidos para la numeración simple."
                    )

                self.progress_signal.emit(50)

                # Ord por prox euclidiana desde punto de inicio
                punto_inicio = self.cfg["punto_inicio"]
                postes_ordenados = sorted(
                    postes_validos,
                    key=lambda p: calculate_distance((p["X"], p["Y"]), punto_inicio),
                )

                exitos = self._ejecutar_insercion_secuencial(
                    postes_ordenados, capa_destino
                )

            self.log_signal.emit(f"Inserción completa: {exitos} postes numerados.")
            self.progress_signal.emit(100)
            self.finished_signal.emit(True)

        except Exception as e:
            self.log_signal.emit(f"ERROR: {e}")
            self.finished_signal.emit(False)

        finally:
            pythoncom.CoUninitialize()

    # MÉTODOS AUXILIARES DE INSERCIÓN

    def _ejecutar_insercion_dfs(self, ruta_logica, postes_validos, capa_destino) -> int:
        exitos = 0
        numero_actual = 1
        radio_asociacion = (
            1.5  # Margen de captura desde el vértice de la línea al bloque
        )

        total_nodos = len(ruta_logica)

        # ETAPA 1: RECORRIDO TOPOLÓGICO (NODOS MÚLTIPLES)
        for idx, pt_grafo in enumerate(ruta_logica):
            postes_en_este_nodo = []

            # En lugar de 'break', recopilamos TODOS los postes en este radio
            for poste in postes_validos:
                dist_poste = calculate_distance(pt_grafo, (poste["X"], poste["Y"]))
                if dist_poste <= radio_asociacion:
                    postes_en_este_nodo.append((dist_poste, poste))

            if postes_en_este_nodo:
                # Los ordenamos por cercanía exacta al vértice de la red
                postes_en_este_nodo.sort(key=lambda item: item[0])

                for _, poste_encontrado in postes_en_este_nodo:
                    if self._insertar_bloque(
                        poste_encontrado, numero_actual, capa_destino
                    ):
                        exitos += 1
                        numero_actual += 1
                    # Retiramos para no contarlo dos veces
                    postes_validos.remove(poste_encontrado)

            # Progreso del 60% al 90%
            self.progress_signal.emit(60 + int((idx / total_nodos) * 30))

        # ETAPA 2: BARRIDO DE POSTES REZAGADOS
        # Si la lista no quedó vacía, es porque hay postes fuera de los ramales principales
        if len(postes_validos) > 0:
            self.log_signal.emit(
                f"Barrido final: Numerando {len(postes_validos)} postes rezagados fuera de la red..."
            )

            # Tomamos el último punto del grafo como referencia, o el punto de inicio si algo falló
            punto_ref = ruta_logica[-1] if ruta_logica else self.cfg["punto_inicio"]

            # Ordenamos los rezagados por proximidad al final de la red
            postes_rezagados = sorted(
                postes_validos,
                key=lambda p: calculate_distance((p["X"], p["Y"]), punto_ref),
            )

            for poste in postes_rezagados:
                if self._insertar_bloque(poste, numero_actual, capa_destino):
                    exitos += 1
                    numero_actual += 1

        return exitos

    def _ejecutar_insercion_secuencial(self, postes_ordenados, capa_destino) -> int:
        exitos = 0
        numero_actual = 1
        total_postes = len(postes_ordenados)

        for idx, poste in enumerate(postes_ordenados):
            if self._insertar_bloque(poste, numero_actual, capa_destino):
                exitos += 1
                numero_actual += 1
            self.progress_signal.emit(50 + int((idx / total_postes) * 50))
        return exitos

    def _insertar_bloque(
        self, poste_datos: dict, numero: int, capa_destino: str
    ) -> bool:
        return drawing.insert_block_with_attributes(
            x=poste_datos["X"] + SETTINGS.TEXT_OFFSET_X,
            y=poste_datos["Y"] + SETTINGS.TEXT_OFFSET_Y,
            block_name=SETTINGS.BLOQUE_A_INSERTAR,
            layer=capa_destino,
            scale=SETTINGS.ESCALA_BLOQUE,
            attributes={SETTINGS.ATRIBUTO_ETIQUETA: str(numero)},
        )
