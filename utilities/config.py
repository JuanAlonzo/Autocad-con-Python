"""
Configuraciones globales
"""

import json
import os
import logging

logger = logging.getLogger(__name__)


class AppSettings:
    def __init__(self):
        # Valores por defecto (Fallback)
        self.LAYER_PREFIX_POSTES = "POSTE"
        self.LAYER_NUMERACION = "NUMERACION_POSTES"
        self.COLOR_NUMERACION = 6
        self.COLOR_NUMERACION_ESTRICTA = 5
        self.COLOR_DEFAULT_LAYER = 7
        self.DEFAULT_LINEWEIGHT = -3

        self.TEXT_HEIGHT = 1.5
        self.CIRCLE_RADIUS = 2.0
        self.TEXT_OFFSET_X = 0.0
        self.TEXT_OFFSET_Y = 0.0

        self.DEFAULT_SEARCH_RADIUS = 5.0
        self.DEFAULT_ASSOCIATION_RADIUS = 5.0

        self.BLOQUE_A_INSERTAR = "UBICACION POSTES UTM"
        self.CAPA_DESTINO = "NUMERACION"
        self.ATRIBUTO_ETIQUETA = "000"
        self.ESCALA_BLOQUE = 2.0

    def load_from_file(self, filepath="settings.json"):
        """Carga las configuraciones desde un archivo JSON si existe."""
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Sobrescribir los atributos existentes con los del JSON
                    for key, value in data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
                logger.info(f"Configuraciones cargadas desde {filepath}")
            except Exception as e:
                logger.error(
                    f"Error al cargar config: {e}. Usando valores por defecto."
                )
        else:
            logger.info(
                f"Archivo {filepath} no encontrado. Creando con valores por defecto."
            )
            self.save_to_file(filepath)

    def save_to_file(self, filepath="settings.json"):
        """Guarda las configuraciones actuales en un archivo JSON."""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.__dict__, f, indent=4, ensure_ascii=False)
            logger.info(f"Configuraciones guardadas en {filepath}")
        except Exception as e:
            logger.error(f"Error al guardar config: {e}")


SETTINGS = AppSettings()
