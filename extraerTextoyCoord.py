from utilities.acad_common import require_autocad
from utilities.acad_entities import extract_text_data
from utilities.acad_export import show_export_menu
from utilities.acad_layers import get_all_layer_names
from utilities.ui_console import ConsoleUI


def main():
    ui = ConsoleUI()
    acad = require_autocad(ui)

    layers = get_all_layer_names(acad)
    layer = ui.get_selection(
        "Seleccionar la capa de Texto", layers)
    if not layer:
        return

    tipos = ["Todos (Text + MText)", "Solo Texto Simple (Text)",
             "Solo Texto Múltiple (MText)"]
    sel_tipo = ui.get_selection("Filtrar por Tipo de Objeto", tipos)

    if not sel_tipo:
        return

    # Mapeo simple para la función interna
    type_code = "all"
    if "Simple" in sel_tipo:
        type_code = "text"
    elif "Múltiple" in sel_tipo:
        type_code = "mtext"

    # 3. Extracción
    # extract_text_data devuelve tuplas: (Texto, X, Y)
    data_tuples = extract_text_data(acad, ui, layer, type_code)

    if not data_tuples:
        ui.show_message("No se encontraron textos.", "warning")
        return

    # 4. Visualización
    # Convertimos tuplas a listas de strings para la tabla
    headers = ["Contenido", "Coord X", "Coord Y"]
    rows = [[str(t), str(x), str(y)] for t, x, y in data_tuples[:15]]

    ui.show_message(f"Se encontraron ({len(data_tuples)}) Textos ")
    ui.show_table(headers, rows)

    # 5. Exportación
    if ui.confirm("¿Exportar reporte a archivo?"):
        # Como data_tuples es una lista de listas (no diccionarios), pasamos los headers explícitamente
        show_export_menu(data_tuples, f"textos_{layer}", ui, columns=headers)


if __name__ == "__main__":
    main()
