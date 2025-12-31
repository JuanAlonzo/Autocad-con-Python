"""
Módulo de Entidades: acad_entities.py
Responsabilidad: Extraer datos de objetos de AutoCAD (Bloques, Textos, Líneas).
Devuelve listas de diccionarios limpias, listas para ser exportadas o procesadas.
"""
import win32com.client
import pythoncom
from .acad_common import console, progress
from .acad_io import display_message, display_table


def get_model_space_safe():
    """
    Obtiene el espacio modelo de AutoCAD de manera segura.
    """
    try:
        acad_app = win32com.client.GetActiveObject("AutoCAD.Application")
    except:
        try:
            acad_app = win32com.client.Dispatch("AutoCAD.Application")
        except Exception as e:
            console.print(f"[red]Error al conectar con AutoCAD: {e}[/red]")
            return None

    return acad_app.ActiveDocument.ModelSpace


def extract_text_data(acad, layer_name, text_type="all"):
    """
    Extrae texto y coordenadas de una capa.
    text_type: 'all', 'text', 'mtext'
    Retorna: Lista de tuplas [(Texto, X, Y), ...]
    """
    data = []
    msp = get_model_space_safe()
    if not msp:
        return []

    console.print(
        f"[cyan]Analizando capa '{layer_name}' (Motor Nativo)...[/cyan]")

    # Definir filtros según tipo
    allowed_types = ["AcDbText", "AcDbMText"]
    if text_type == "text":
        allowed_types = ["AcDbText"]
    elif text_type == "mtext":
        allowed_types = ["AcDbMText"]

    console.print(f"[cyan]Analizando capa '{layer_name}'...[/cyan]")

    count = msp.Count

    # Extracción con barra de progreso
    with progress:
        task = progress.add_task(
            "[green]Extrayendo datos...[/green]", total=count)

        for i in range(count):
            try:
                obj = msp.Item(i)
                if obj.Layer == layer_name and obj.ObjectName in allowed_types:
                    txt = obj.TextString
                    coord = obj.InsertionPoint
                    data.append((txt, coord[0], coord[1]))
            except:
                pass
            progress.advance(task)

    display_message(
        f"Se extrajeron {len(data)} elementos de texto.", "success")
    return data


def extract_block_data(acad, layer_name=None):
    """
    Extrae propiedades avanzadas de bloques.
    Si layer_name es None, extrae de TODAS las capas.
    Retorna: Lista de diccionarios con propiedades y atributos.
    """
    blocks_data = []
    msp = get_model_space_safe()
    if not msp:
        return []

    msg = f"capa '{layer_name}'" if layer_name else "todas las capas"
    console.print(f"[cyan]Buscando bloques en {msg}...[/cyan]")

    count = msp.Count

    # Fase 2: Procesamiento detallado
    with progress:
        task = progress.add_task(
            "[green]Leyendo propiedades...[/green]", total=count)

        for i in range(count):
            try:
                obj = msp.Item(i)
                if obj.ObjectName != "AcDbBlockReference":
                    progress.advance(task)
                    continue

                if layer_name and obj.Layer != layer_name:
                    progress.advance(task)
                    continue

                # Propiedades base
                info = {}

                coords = obj.InsertionPoint
                info["X"] = round(coords[0], 4)
                info["Y"] = round(coords[1], 4)
                info["Z"] = round(coords[2], 4)

                try:
                    name = obj.EffectiveName if obj.EffectiveName else obj.Name
                except Exception:
                    name = obj.Name
                info["Nombre"] = name
                info["Capa"] = obj.Layer
                info["Rotacion"] = round(obj.Rotation, 4)

                if obj.HasAttributes:
                    attribs = obj.GetAttributes()
                    for att in attribs:
                        tag = att.TagString.upper()
                        val = att.TextString
                        info[f"Attr_{tag}"] = val

                blocks_data.append(info)
            except Exception:
                pass
            progress.advance(task)

    display_message(
        f"Procesados {len(blocks_data)} bloques correctamente.", "success")
    return blocks_data
