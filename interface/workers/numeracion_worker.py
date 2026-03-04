import pythoncom
from PySide6.QtCore import QThread, Signal
from utilities.cad_manager import cad
from utilities import geometry, entities, drawing, layers
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
        pythoncom.CoInitialize()  # Inicializar COM para este hilo
        cad.connect()  # Asegurar conexión a AutoCAD en este hilo
        try:
            self.log_signal.emit(
                f"Paso 1: Extrayendo postes (Prefijo: '{SETTINGS.LAYER_PREFIX_POSTES}')..."
            )
            postes_crudos = entities.extract_blocks(
                layer_prefix=SETTINGS.LAYER_PREFIX_POSTES
            )

            if not postes_crudos:
                self.log_signal.emit("Operación cancelada: No se encontraron bloques.")
                self.finished_signal.emit(False)
                return

            self.progress_signal.emit(20)  # 20% - Extracción finalizada

            self.log_signal.emit("Paso 2: Leyendo polilínea de ruta...")
            puntos_ruta = geometry.get_polyline_points(self.cfg["capa_ruta"])
            if not puntos_ruta:
                self.log_signal.emit("Operación cancelada: Ruta no encontrada.")
                self.finished_signal.emit(False)
                return

            self.progress_signal.emit(40)  # 40% - Ruta procesada

            self.log_signal.emit("Paso 3: Ordenando bloques espacialmente...")
            postes_ordenados = geometry.sort_blocks_by_path(
                blocks=postes_crudos,
                path_points=puntos_ruta,
                search_radius=self.cfg["radio"],
                strict_mode=self.cfg["estricto"],
            )

            self.progress_signal.emit(60)  # 60% - Ordenamiento matemático finalizado

            if self.cfg["asociar"] and self.cfg["capa_datos"]:
                self.log_signal.emit(
                    f"Paso Opcional: Buscando datos en capa '{self.cfg['capa_datos']}'..."
                )
                datos_asociar = entities.extract_texts(
                    layer_name=self.cfg["capa_datos"]
                )
                if not datos_asociar:
                    datos_asociar = entities.extract_blocks(
                        layer_name=self.cfg["capa_datos"]
                    )

                if datos_asociar:
                    postes_ordenados = geometry.associate_data(
                        base_blocks=postes_ordenados,
                        data_entities=datos_asociar,
                        radius=SETTINGS.DEFAULT_ASSOCIATION_RADIUS,
                    )

            self.progress_signal.emit(70)  # 70% - Asociación de datos finalizada

            capa_destino = SETTINGS.CAPA_DESTINO
            color_capa = (
                SETTINGS.COLOR_NUMERACION_ESTRICTA
                if self.cfg["estricto"]
                else SETTINGS.COLOR_NUMERACION
            )
            layers.ensure_layer(capa_destino, color=color_capa)

            self.log_signal.emit(
                "Paso 4: Insertando bloques de numeración en AutoCAD..."
            )
            total = len(postes_ordenados)
            exitos = 0

            # Iteración con actualización dinámica de progreso (del 70% al 100%)
            for idx, poste in enumerate(postes_ordenados, start=1):
                etiqueta = str(idx)  # Corrección aplicada: sin zfill
                px = poste["X"] + SETTINGS.TEXT_OFFSET_X
                py = poste["Y"] + SETTINGS.TEXT_OFFSET_Y

                insercion_ok = drawing.insert_block_with_attributes(
                    x=px,
                    y=py,
                    block_name=SETTINGS.BLOQUE_A_INSERTAR,
                    layer=capa_destino,
                    scale=SETTINGS.ESCALA_BLOQUE,
                    attributes={SETTINGS.ATRIBUTO_ETIQUETA: etiqueta},
                )
                if insercion_ok:
                    exitos += 1

                # Calcular progreso fraccional
                current_progress = 70 + int((idx / total) * 30)
                self.progress_signal.emit(current_progress)

            self.log_signal.emit(f"--- FINALIZADO: {exitos} etiquetas insertadas. ---")
            self.progress_signal.emit(100)
            self.finished_signal.emit(True)

        except Exception as e:
            self.log_signal.emit(f"ERROR CRÍTICO durante la ejecución: {e}")
            self.finished_signal.emit(False)

        finally:
            pythoncom.CoUninitialize()  # Limpiar COM al finalizar el hilo
