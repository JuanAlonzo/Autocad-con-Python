import logging
from typing import Tuple, List, Dict, Optional, Any
from .geometry import calculate_distance

logger = logging.getLogger(__name__)
Point2D = Tuple[float, float]


def point_to_key(point: Point2D, tolerance: float) -> Tuple[float, float]:
    """
    Normaliza una coordenada aplicando un redondeo (snap) basado en tolerancia.
    """
    if tolerance == 0:
        return point
    x = round(point[0] / tolerance) * tolerance
    y = round(point[1] / tolerance) * tolerance
    return (x, y)


class NetworkGraph:
    """
    Grafo no dirigido que representa la linea de red existente.
    Usa listas de adyacencia para almacenar conexiones y pesos (distancias).
    """

    def __init__(self, tolerance: float = 0.1):
        self.adj: Dict[
            Tuple[float, float], List[Tuple[Tuple[float, float], float]]
        ] = {}
        self.nodes: Dict[Tuple[float, float], Point2D] = {}
        self.tolerance = tolerance
        logger.debug(f"Inicializando Grafo con tolerancia: {tolerance}m")

    def add_line(self, p1: Point2D, p2: Point2D) -> None:
        """
        Agrega una conexión (arista) entre dos puntos (nodos).
        """
        # Obtener claves únicas (con Snap)
        key1 = point_to_key(p1, self.tolerance)
        key2 = point_to_key(p2, self.tolerance)

        self.nodes[key1] = p1
        self.nodes[key2] = p2

        if key1 == key2:
            logger.debug(f"Saltando línea de longitud 0 entre {p1} y {p2}")
            return  # Ignorar líneas de longitud 0

        dist = calculate_distance(p1, p2)

        # Inicializar listas
        if key1 not in self.adj:
            self.adj[key1] = []
        if key2 not in self.adj:
            self.adj[key2] = []

        if not any(neighbor == key2 for neighbor, _ in self.adj[key1]):
            self.adj[key1].append((key2, dist))
            self.adj[key2].append((key1, dist))

    def dfs_traversal(self, start_node: Point2D) -> List[Point2D]:
        """
        Recorrido en profundidad (DFS) adaptado para topología de red.
        Útil para enumerar postes secuencialmente a lo largo de ramas conectadas.
        """
        start_key = point_to_key(start_node, self.tolerance)
        if start_key not in self.adj:
            logger.warning("El nodo de inicio no pertenece a la red.")
            return []

        visited = set()
        path = []

        def dfs(current_key):
            visited.add(current_key)
            path.append(self.nodes[current_key])
            for neighbor_key, _ in self.adj.get(current_key):
                if neighbor_key not in visited:
                    dfs(neighbor_key)

        dfs(start_key)
        return path

    def find_nearest_node(
        self, point: Point2D, max_radius: float = 5.0
    ) -> Tuple[Optional[Tuple[float, float]], Optional[float]]:
        """
        Encuentra el nodo del grafo más cercano a un punto dado (ej. un Equipo).

        Returns:
            Tuple(NodeKey, Distancia): Retorna None, None si no encuentra nada en el radio.
        """
        best_node = None
        min_dist = float("inf")

        # Búsqueda lineal optimizada con caja delimitadora simple
        for key, coords in self.nodes.items():
            if abs(point[0] - coords[0]) > max_radius:
                continue
            if abs(point[1] - coords[1]) > max_radius:
                continue

            d = calculate_distance(point, coords)
            if d < min_dist:
                min_dist = d
                best_node = key

        # Solo logueamos si NO encuentra nada, para depurar
        if best_node is None and min_dist > max_radius:
            logger.debug(f"No se encontró nodo cercano a {point} en radio {max_radius}")
            pass

        if min_dist <= max_radius:
            return best_node, min_dist
        return None, None

    def get_path_length(
        self, start_node: Any, end_node: Any
    ) -> Tuple[Optional[float], List[Point2D]]:
        """
        Ejecuta el algoritmo de Dijkstra para encontrar la ruta más corta.

        Returns:
            Tuple(DistanciaTotal, ListaDePuntos): (None, []) si no hay camino.
        """
        import heapq

        # Cola de prioridad: (distancia_acumulada, nodo_actual)
        queue = [(0, start_node)]
        visited = {}  # Diccionario: nodo -> (distancia, nodo_padre)

        visited[start_node] = (0, None)  # distancia, nodo_previo

        while queue:
            current_dist, current_node = heapq.heappop(queue)

            if current_node == end_node:
                # Reconstruir camino hacia atrás
                path = []
                curr = end_node
                while curr is not None:
                    path.append(self.nodes[curr])
                    _, parent = visited[curr]
                    curr = parent
                return current_dist, path[
                    ::-1
                ]  # Se invierte para tener orden Inicio->Fin

            # Si encontramos un camino más largo al que ya conocemos, ignorar
            if current_dist > visited[current_node][0]:
                continue

            if current_node in self.adj:
                for neighbor, weight in self.adj[current_node]:
                    new_dist = current_dist + weight

                    if neighbor not in visited or new_dist < visited[neighbor][0]:
                        visited[neighbor] = (new_dist, current_node)
                        heapq.heappush(queue, (new_dist, neighbor))

        return None  # No hay camino (islas separadas)
