# import pytest
from utilities.geometry import associate_data


def test_heterogeneous_data_association():
    # 1. Definición del objeto base (El poste a numerar)
    base_blocks = [{"Handle": "A1", "Nombre": "POSTE_PROY", "X": 100.0, "Y": 200.0}]

    # 2. Definición del pool heterogéneo
    data_entities = [
        # Un MText muy alejado
        {"Tipo": "AcDbMText", "Texto": "COD-INVALIDO", "X": 999.0, "Y": 999.0},
        # Un Texto simple a 2 unidades de distancia
        {"Tipo": "AcDbText", "Texto": "COD-TXT-123", "X": 102.0, "Y": 200.0},
        # Un Bloque con atributos a 0.5 unidades de distancia (El más cercano)
        {
            "Tipo": "AcDbBlockReference",
            "Attr_CODIGO": "COD-BLK-456",
            "X": 100.5,
            "Y": 200.0,
        },
    ]

    # 3. Ejecución con Radio de búsqueda: 5.0m
    result = associate_data(base_blocks, data_entities, radius=5.0)

    # 4. Verificación de Lógica
    assert len(result) == 1
    poste = result[0]

    # El algoritmo debe haber preferido "COD-BLK-456" porque está a 0.5m,
    # ignorando "COD-TXT-123" que está a 2.0m, y descartando el MText por exceder el radio.
    assert "Data_Attr_CODIGO" in poste
    assert poste["Data_Attr_CODIGO"] == "COD-BLK-456"
    assert "Data_Texto" not in poste
