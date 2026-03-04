# import pytest
from utilities.geometry import calculate_distance, sort_blocks_by_path, associate_data


def test_calculate_distance():
    # Triángulo rectángulo clásico 3, 4, 5
    dist = calculate_distance((0, 0), (3, 4))
    assert dist == 5.0


def test_sort_blocks_by_path_strict_mode():
    # Ruta de dos puntos: (0,0) y (10,0)
    path = [(0, 0), (10, 0)]

    # Bloques desordenados. Uno está fuera del radio.
    blocks = [
        {"Nombre": "B2", "X": 10.0, "Y": 0.1},  # Cerca del segundo punto
        {"Nombre": "B_OUT", "X": 50.0, "Y": 50.0},  # Muy lejos
        {"Nombre": "B1", "X": 0.0, "Y": 0.5},  # Cerca del primer punto
    ]

    # Modo Estricto: Debería ignorar B_OUT
    ordered = sort_blocks_by_path(blocks, path, search_radius=2.0, strict_mode=True)

    assert len(ordered) == 2
    assert ordered[0]["Nombre"] == "B1"  # El más cercano a (0,0)
    assert ordered[1]["Nombre"] == "B2"  # El más cercano a (10,0)


def test_associate_data():
    base_blocks = [{"Nombre": "POSTE_1", "X": 10.0, "Y": 10.0}]

    # Datos a cruzar (uno cerca, uno lejos)
    data_entities = [
        {"Texto": "COD-999", "X": 100.0, "Y": 100.0},  # Lejos
        {"Texto": "COD-123", "X": 10.5, "Y": 10.5},  # Cerca (dentro de radio 1.0)
    ]

    result = associate_data(base_blocks, data_entities, radius=1.0)

    # Verificamos que el dato cercano se heredó al bloque base
    assert "Data_Texto" in result[0]
    assert result[0]["Data_Texto"] == "COD-123"
