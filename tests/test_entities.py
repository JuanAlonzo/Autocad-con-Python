# import pytest
from unittest.mock import MagicMock, patch
from utilities.entities import extract_blocks


@patch("utilities.entities.cad")  # Interceptamos el cad_manager
def test_extract_blocks_with_prefix(mock_cad):
    # 1. PREPARAR EL ENGAÑO (MOCK)
    mock_cad.is_connected = True

    # Crear un objeto COM falso que simule ser un bloque válido
    fake_block = MagicMock()
    fake_block.EntityName = "AcDbBlockReference"
    fake_block.Layer = "POSTE_NUEVO"
    fake_block.Name = "UBICACION"
    fake_block.Handle = "A1F"
    fake_block.InsertionPoint = (15.0, 20.0, 0.0)
    fake_block.Rotation = 0.0
    fake_block.HasAttributes = False  # Sin atributos para simplificar

    # Crear un objeto falso que simule una línea (debería ser ignorado)
    fake_line = MagicMock()
    fake_line.EntityName = "AcDbLine"

    # Le decimos a mock_cad.msp (ModelSpace) que contenga estos dos objetos
    mock_cad.msp = [fake_block, fake_line]

    # 2. EJECUTAR LA FUNCIÓN
    # Buscamos bloques que empiecen con "POSTE_"
    result = extract_blocks(layer_prefix="POSTE_")

    # 3. COMPROBAR RESULTADOS
    assert len(result) == 1  # Solo debió capturar el fake_block
    assert result[0]["Capa"] == "POSTE_NUEVO"
    assert result[0]["X"] == 15.0
    assert result[0]["Handle"] == "A1F"
