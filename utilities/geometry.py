import math
import logging
from .cad_manager import cad

logger = logging.getLogger(__name__)


def get_polyline_points(layer_name: str) -> list:
    """
    Extrae los vértices de una polilínea en una capa específica usando win32com puro.
    Devuelve una lista de tuplas (x, y).
    """
    if not cad.is_connected:
        logger.error("AutoCAD no está conectado.")
        return []

    path_points = []
    logger.info(f"Buscando polilínea de ruta en la capa '{layer_name}'...")

    try:
        found_valid = False
        total_objects = cad.msp.Count

        for i in range(total_objects):
            obj = cad.msp.Item(i)
            if (
                obj.EntityName in ["AcDbPolyline", "AcDb2dPolyline", "AcDb3dPolyline"]
                and obj.Layer.upper() == layer_name.upper()
            ):
                coords = obj.Coordinates

                # Identificamos el salto del array de coordenadas
                # LWPOLYLINE -> [x1, y1, x2, y2...]
                # 2d/3dPolyline -> [x1, y1, z1, x2, y2, z2...]
                step = 2 if obj.EntityName == "AcDbPolyline" else 3

                for j in range(0, len(coords), step):
                    # Extraemos solo X e Y para análisis 2D
                    path_points.append((round(coords[j], 4), round(coords[j + 1], 4)))

                found_valid = True
                logger.info(
                    f"Ruta detectada: {obj.EntityName} con {len(path_points)} vértices."
                )
                break

        if not found_valid:
            logger.warning(
                f"No se encontró ninguna polilínea en la capa '{layer_name}'."
            )

    except Exception as e:
        logger.error(f"Error extrayendo vértices de la polilínea: {e}")

    return path_points


def calculate_distance(p1: tuple, p2: tuple) -> float:
    """
    Calcula la distancia euclidiana 2D entre dos puntos.
    """
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def sort_blocks_by_path(
    blocks: list, path_points: list, search_radius: float, strict_mode: bool = False
) -> list:
    """
    Algoritmo de ordenamiento espacial de bloques a lo largo de una ruta.

    Args:
        blocks: Lista de diccionarios con los datos de los bloques (debe contener 'X' e 'Y').
        path_points: Lista de tuplas (x, y) que representan la ruta.
        search_radius: Radio de captura alrededor de cada vértice de la ruta.
        strict_mode: Si es True, ignora los bloques que no estén cerca de la ruta.
                     Si es False, los añade al final de la lista.
    """
    ordered_blocks = []
    pool = blocks.copy()

    logger.info(
        f"Ordenando {len(pool)} bloques (Radio: {search_radius}u | Estricto: {strict_mode})..."
    )

    # Se captura por cercanía a los vértices de la ruta
    for mx, my in path_points:
        close_ones = []

        # Buscamos candidatos en el pool restante
        for blk in pool:
            dist = calculate_distance((blk["X"], blk["Y"]), (mx, my))
            if dist <= search_radius:
                close_ones.append((dist, blk))

        if close_ones:
            # Ordenamos el sub-grupo por cercanía exacta al vértice (distancia)
            close_ones.sort(key=lambda item: item[0])

            for dist, blk in close_ones:
                ordered_blocks.append(blk)
                if blk in pool:
                    pool.remove(blk)

    # Gestión de bloques sobrantes
    sobrantes = len(pool)
    if sobrantes > 0:
        logger.warning(
            f"AUDITORÍA: Se detectaron {sobrantes} bloques fuera del radio de {search_radius}m."
        )
        # Iterar sobre los bloques no capturados para un loggeo exhaustivo
        for out_block in pool:
            coord_x = out_block.get("X")
            coord_y = out_block.get("Y")
            handle = out_block.get("Handle", "N/A")

            # Calcular a qué distancia exacta quedó del punto más cercano de la ruta
            if path_points:
                min_dist_to_path = min(
                    calculate_distance((coord_x, coord_y), pt) for pt in path_points
                )
                logger.warning(
                    f"[FUERA DE ALCANCE] Handle: {handle} en coordenadas (X: {coord_x}, Y: {coord_y}). "
                    f"Distancia a la ruta: {min_dist_to_path:.2f}m (Excede límite de {search_radius}m)"
                )
            else:
                logger.warning(
                    f"[FUERA DE ALCANCE] Handle: {handle} en coordenadas (X: {coord_x}, Y: {coord_y})."
                )

        if strict_mode:
            logger.warning(
                f"Modo Estricto activado: Los {sobrantes} bloques identificados arriba fueron omitidos de la numeración."
            )
        else:
            logger.info(
                f"Modo Normal activado: Se anexaron los {sobrantes} bloques dispersos al final de la secuencia."
            )
            ordered_blocks.extend(pool)
    else:
        logger.info(
            "Cobertura perfecta: 100% de los bloques se encontraban dentro de los parámetros de la ruta."
        )
    return ordered_blocks


def associate_data(base_blocks: list, data_entities: list, radius: float) -> list:
    """
    Asocia atributos de 'data_entities' (textos o bloques) a 'base_blocks'
    basándose en la cercanía espacial (dentro de un radio).
    """
    logger.info(f"Iniciando asociación de datos (Radio de búsqueda: {radius}m)...")
    associated_count = 0
    pool_datos = data_entities.copy()

    for base in base_blocks:
        bx, by = base["X"], base["Y"]
        closest_data = None
        min_dist = radius

        for entity in pool_datos:
            ex, ey = entity["X"], entity["Y"]
            dist = calculate_distance((bx, by), (ex, ey))

            # Buscamos la entidad más cercana dentro del radio permitido
            if dist <= min_dist:
                min_dist = dist
                closest_data = entity

        if closest_data:
            # Si encontramos algo, le pasamos los datos relevantes al bloque base
            # Agregamos un prefijo 'Data_' para no chocar con atributos propios del poste
            for key, val in closest_data.items():
                if key.startswith("Attr_") or key == "Texto":
                    base[f"Data_{key}"] = val

            associated_count += 1
            # Retiramos el dato del pool para no asignarlo a dos postes distintos
            pool_datos.remove(closest_data)

    logger.info(
        f"Asociación exitosa: Se cruzó información en {associated_count} bloques."
    )
    return base_blocks


def point_to_segment_projection(p: tuple, a: tuple, b: tuple) -> tuple:
    """
    Proyecta un punto p sobre el vector ab.
    Retorna: ((proj_x, proj_y), distancia_perpendicular)
    """
    ax, ay = a
    bx, by = b
    px, py = p

    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay

    ab_len_sq = abx**2 + aby**2
    if ab_len_sq == 0:
        return a, calculate_distance(p, a)

    # t representa el punto en el vector (0 es A, 1 es B)
    t = (apx * abx + apy * aby) / ab_len_sq
    t = max(0.0, min(1.0, t))  # Forzamos a que no se salga del segmento de recta

    proj_x = ax + t * abx
    proj_y = ay + t * aby

    dist = calculate_distance(p, (proj_x, proj_y))
    return (proj_x, proj_y), dist


def split_segments_with_poles(
    segmentos: list, postes: list, tolerancia: float = 1.0
) -> list:
    """
    Cruza líneas con postes. Si un poste está sobre la línea, divide la arista $A \to B$
    en $A \to Poste \to B$.
    """
    nuevos_segmentos = []

    for p1, p2 in segmentos:
        postes_en_segmento = []
        for poste in postes:
            coords_poste = (poste["X"], poste["Y"])
            proj, dist = point_to_segment_projection(coords_poste, p1, p2)

            # Si el poste pertenece a esta línea
            if dist <= tolerancia:
                dist_from_p1 = calculate_distance(p1, proj)
                postes_en_segmento.append((dist_from_p1, proj))

        if not postes_en_segmento:
            nuevos_segmentos.append((p1, p2))
        else:
            # Ordenar las proyecciones para no cruzar los segmentos resultantes
            postes_en_segmento.sort(key=lambda item: item[0])
            punto_actual = p1
            for _, proj in postes_en_segmento:
                if (
                    calculate_distance(punto_actual, proj) > 0.1
                ):  # Evitar segmentos nulos
                    nuevos_segmentos.append((punto_actual, proj))
                punto_actual = proj
            if calculate_distance(punto_actual, p2) > 0.1:
                nuevos_segmentos.append((punto_actual, p2))

    return nuevos_segmentos
