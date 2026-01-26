from utilities import (
    require_autocad,
    extract_text_data,
    show_export_menu,
    get_all_layer_names,
    ConsoleUI,
)


def main():
    ui = ConsoleUI()
    acad = require_autocad(ui)

    layers = get_all_layer_names(acad)
    layer = ui.get_selection("Seleccionar la capa de Texto", layers)
    if not layer:
        return

    tipos = [
        "Todos (Text + MText)",
        "Solo Texto Simple (Text)",
        "Solo Texto Múltiple (MText)",
    ]
    sel_tipo = ui.get_selection("Filtrar por Tipo de Objeto", tipos)

    if not sel_tipo:
        return

    # Mapeo simple para la función interna
    type_code = "all"
    if "Simple" in sel_tipo:
        type_code = "text"
    elif "Múltiple" in sel_tipo:
        type_code = "mtext"

    # Extracción
    data_tuples = extract_text_data(acad, ui, layer, type_code)

    if not data_tuples:
        ui.show_message("No se encontraron textos.", "warning")
        return

    # Visualización -> Convertimos tuplas a listas de strings para la tabla
    headers = ["Contenido", "Coord X", "Coord Y"]
    rows = [[str(t), str(x), str(y)] for t, x, y in data_tuples[:15]]

    ui.show_message(f"Se encontraron ({len(data_tuples)}) Textos ")
    ui.show_table(headers, rows)

    # Exportación
    if ui.confirm("¿Exportar reporte a archivo?"):
        show_export_menu(data_tuples, f"textos_{layer}", ui, columns=headers)


if __name__ == "__main__":
    main()
