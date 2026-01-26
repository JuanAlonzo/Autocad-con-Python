"""
Módulo de Exportación: acad_export.py
Responsabilidad: Convertir listas de datos a archivos (CSV, Excel, JSON).
Centraliza la lógica de Pandas, manejo de rutas y nombres de archivo con fecha.
"""

import pandas as pd
from datetime import datetime
import os


def generate_filename(prefix, extension):
    """
    Genera un nombre único con fecha y hora: 'prefix_YYYYMMDD_HHMMSS.ext'
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def export_to_file(data, filename_prefix, ui, columns=None, format="csv"):
    """
    Función Universal de Exportación.

    Args:
        data (list): Lista de diccionarios O lista de listas.
        filename_prefix (str): Nombre base del archivo (ej. 'mis_bloques').
        ui: Interfaz de usuario para mostrar mensajes.
        columns (list, opcional): Nombres de columnas (obligatorio si data es lista de listas).
        format (str): 'csv' o 'excel'.

    Returns:
        bool: True si tuvo éxito, False si falló.
    """
    if not data:
        ui.show_message("No hay datos para exportar.", "warning")
        return False

    try:
        df = pd.DataFrame(data)

        if columns:
            if len(columns) != len(df.columns):
                ui.show_message(
                    f"Error: Columnas no coinciden: {len(df.columns)} vs {len(columns)}.",
                    "error",
                )
                return False
            df.columns = columns
    except Exception as e:
        ui.show_message(f"Error al crear DataFrame: {e}", "error")
        return False

    ext = "xlsx" if format.lower() == "excel" else "csv"
    filename = generate_filename(filename_prefix, ext)

    try:
        ui.show_message(f"Exportando {filename}...", "info")

        if format.lower() == "csv":
            df.to_csv(filename, index=False)
        else:
            df.to_excel(filename, index=False)
        ui.show_message(
            f"Archivo exportado exitosamente: {os.path.abspath(filename)}", "success"
        )
        return True
    except PermissionError:
        ui.show_message(
            f"Error: El archivo '{filename}' está abierto. Ciérralo e intenta de nuevo.",
            "error",
        )
        return False
    except Exception as e:
        ui.show_message(f"Error fatal exportando: {e}", "error")
        return False


def show_export_menu(data, filename_prefix, ui, columns=None):
    """
    Flujo interactivo completo: Pregunta al usuario formato y exporta.
    Úsalo al final de tus scripts principales.
    """

    options = ["Exportar a CSV", "Exportar a Excel", "Salir"]
    selection = ui.get_selection("Opciones de Exportación", options)

    if not selection or selection == "Salir":
        return

    fmt = "csv" if "CSV" in selection else "excel"
    export_to_file(data, filename_prefix, ui, columns, format=fmt)
