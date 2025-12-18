"""
Módulo de Entidades: acad_entities.py
Responsabilidad: Extraer datos de objetos de AutoCAD (Bloques, Textos, Líneas).
Devuelve listas de diccionarios limpias, listas para ser exportadas o procesadas.
"""
from .acad_common import console, progress
from .acad_io import display_message, display_table


def extract_text_data(acad, layer_name, text_type="all"):
    """
    Extrae texto y coordenadas de una capa.
    text_type: 'all', 'text', 'mtext'
    Retorna: Lista de tuplas [(Texto, X, Y), ...]
    """
    data = []

    # Definir filtros según tipo
    allowed_types = ["AcDbText", "AcDbMText"]
    if text_type == "text":
        allowed_types = ["AcDbText"]
    elif text_type == "mtext":
        allowed_types = ["AcDbMText"]

    console.print(f"[cyan]Analizando capa '{layer_name}'...[/cyan]")

    # Barrido optimizado
    found_objs = []
    for obj in acad.iter_objects():
        # Verificación rápida de capa y tipo antes de acceder a propiedades lentas
        if obj.Layer == layer_name and obj.ObjectName in allowed_types:
            found_objs.append(obj)

    total = len(found_objs)
    if total == 0:
        display_message(
            f"No se encontraron textos en la capa '{layer_name}'.", "warning")
        return []

    # Extracción con barra de progreso
    with progress:
        task = progress.add_task(
            "[green]Extrayendo datos...[/green]", total=total)

        for obj in found_objs:
            try:
                # Normalizamos coordenadas a X, Y (ignoramos Z para textos 2D)
                # TextString puede fallar en caracteres raros, por eso el try
                txt = obj.TextString
                x, y = obj.InsertionPoint[:2]
                data.append((txt, x, y))
            except Exception:
                pass  # Ignoramos objetos corruptos
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

    msg = f"capa '{layer_name}'" if layer_name else "todas las capas"
    console.print(f"[cyan]Buscando bloques en {msg}...[/cyan]")

    # Fase 1: Recolección
    target_blocks = []
    for obj in acad.iter_objects():
        if obj.ObjectName == "AcDbBlockReference":
            if layer_name is None or obj.Layer == layer_name:
                target_blocks.append(obj)

    total = len(target_blocks)
    if total == 0:
        display_message("No se encontraron bloques.", "warning")
        return []

    # Fase 2: Procesamiento detallado
    with progress:
        task = progress.add_task(
            "[green]Leyendo propiedades...[/green]", total=total)

        for blk in target_blocks:
            try:
                # Propiedades base
                info = {
                    "Nombre": blk.Name,
                    "Capa": blk.Layer,
                    "X": round(blk.InsertionPoint[0], 4),
                    "Y": round(blk.InsertionPoint[1], 4),
                    "Z": round(blk.InsertionPoint[2], 4),
                    "Rotacion": round(blk.Rotation, 2),
                    "Escala X": round(blk.XScaleFactor, 4)
                }

                # Extracción de Atributos (Si tiene)
                # GetAttributes devuelve una tupla de objetos, iteramos para sacar Tag y Text
                if blk.HasAttributes:
                    for attrib in blk.GetAttributes():
                        # Agregamos prefijo 'Attr_' para diferenciar de propiedades
                        info[f"Attr_{attrib.TagString}"] = attrib.TextString

                blocks_data.append(info)
            except Exception:
                pass
            progress.advance(task)

    display_message(
        f"Procesados {len(blocks_data)} bloques correctamente.", "success")
    return blocks_data
