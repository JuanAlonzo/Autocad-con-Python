"""
Configuraciones para la numeración de postes en AutoCAD.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AppSettings:
    # --- Prefijos ---
    LAYER_PREFIX_POSTES: str = "POSTE"

    # --- Configuración de Capas y Colores ---
    LAYER_NUMERACION: str = "NUMERACION_POSTES"
    COLOR_NUMERACION: int = 6  # Magenta
    COLOR_NUMERACION_ESTRICTA: int = 5  # Azul
    COLOR_DEFAULT_LAYER: int = 7  # Blanco
    DEFAULT_LINEWEIGHT: int = -3

    # --- Configuración de Dibujo ---
    TEXT_HEIGHT: float = 1.5
    CIRCLE_RADIUS: float = 2.0
    TEXT_OFFSET_X: float = -3.0
    TEXT_OFFSET_Y: float = -2.5

    # --- Configuración de Algoritmo ---
    DEFAULT_SEARCH_RADIUS: float = 5.0
    DEFAULT_ASSOCIATION_RADIUS: float = 5.0

    # --- Configuración de Bloques ---
    BLOQUE_A_INSERTAR: str = "UBICACION POSTES UTM"
    CAPA_DESTINO: str = "NUMERACION"
    ATRIBUTO_ETIQUETA: str = "000"
    ESCALA_BLOQUE: float = 2.0


SETTINGS = AppSettings()
