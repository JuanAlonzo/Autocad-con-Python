"""
Módulo de Exportación: acad_export.py
Responsabilidad: Convertir listas de datos a archivos (CSV, Excel, JSON).
Centraliza la lógica de Pandas, manejo de rutas y nombres de archivo con fecha.
"""
import pandas as pd
from datetime import datetime
import os
from .acad_common import console
from .acad_io import display_message, get_user_input


def generate_filename(prefix, extension):
    """
    Genera un nombre único con fecha y hora: 'prefix_YYYYMMDD_HHMMSS.ext'
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def export_to_file(data, filename_prefix, columns=None, format='csv'):
    """
    Función Universal de Exportación.

    Args:
        data (list): Lista de diccionarios O lista de listas.
        filename_prefix (str): Nombre base del archivo (ej. 'mis_bloques').
        columns (list, opcional): Nombres de columnas (obligatorio si data es lista de listas).
        format (str): 'csv' o 'excel'.

    Returns:
        bool: True si tuvo éxito, False si falló.
    """
    if not data:
        display_message("No hay datos para exportar.", 'warning')
        return False

    try:
        df = pd.DataFrame(data)

        if columns:
            if len(columns) != len(df.columns):
                display_message(
                    f"Error al procesar datos para exportacion: {e}.", 'error')
                return False
            df.columns = columns
    except Exception as e:
        display_message(f"Error al crear DataFrame: {e}", 'error')
        return False
    ext = 'xlsx' if format.lower() == 'excel' else 'csv'
    filename = generate_filename(filename_prefix, ext)

    try:
        console.print(f"[cyan]Exportando {filename}...[/cyan]")

        if format.lower() == 'csv':
            df.to_csv(filename, index=False)
        else:
            df.to_excel(filename, index=False)
        display_message(
            f"Archivo exportado exitosamente: {os.path.abspath(filename)}", 'success')
        return True
    except PermissionError:
        display_message(
            f"Error: El archivo '{filename}' está abierto. Ciérralo e intenta de nuevo.", "error")
        return False
    except Exception as e:
        display_message(f"Error fatal exportando: {e}", "error")
        return False


def show_export_menu(data, filename_prefix, columns=None):
    """
    Flujo interactivo completo: Pregunta al usuario formato y exporta.
    Úsalo al final de tus scripts principales.
    """
    from .acad_io import get_selection_from_list  # Importación local para evitar ciclos

    options = ["Exportar a CSV", "Exportar a Excel", "Salir"]
    selection = get_selection_from_list("Opciones de Exportación", options)

    if not selection or selection == "Salir":
        return

    fmt = 'csv' if "CSV" in selection else 'excel'
    export_to_file(data, filename_prefix, columns, format=fmt)
