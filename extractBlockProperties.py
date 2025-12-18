from utilities.acad_common import require_autocad
from utilities.acad_entities import extract_block_data
from utilities.acad_export import show_export_menu
from utilities.acad_layers import get_all_layer_names
from utilities.acad_io import (
    get_selection_from_list,
    display_table,
    display_message,
    get_confirmation
)


def main():
    acad = require_autocad("Extractor de Propiedades de Bloques")

    opciones = [
        "Extraer de UNA capa específica",
        "Extraer de TODAS las capas"
    ]
    seleccion = get_selection_from_list(
        "Configuracion de Extraccion", opciones)

    if not seleccion:
        return

    layer_name = None
    if "UNA capa" in seleccion:
        layers = get_all_layer_names(acad)
        layer_name = get_selection_from_list(
            "Seleccionar la capa de Bloques", layers)
        if not layer_name:
            return

    data = extract_block_data(acad, layer_name)

    if not data:
        return

    headers = list(data[0].keys())
    preview_rows = [[str(row.get(col, '')) for col in headers]
                    for row in data[:10]]

    display_table(
        f"Vista Previa ({len(data)} bloques encontrados)", headers, preview_rows)

    if len(data) > 10:
        display_message(f"... y {len(data) - 10} filas más...", "info")

    if get_confirmation("¿Desea exportar los datos extraídos?"):
        prefix = f"bloques_{layer_name}_" if layer_name else "reporte_bloques_global"
        show_export_menu(data, prefix)


if __name__ == "__main__":
    main()
