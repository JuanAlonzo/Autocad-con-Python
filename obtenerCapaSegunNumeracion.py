"""
Script: Asociación Inteligente
Propósito: Vincular bloques físicos con textos de numeración cercanos.
Soporta capas adicionales de información (ej. Material, Altura).
"""
from utilities.acad_common import require_autocad
from utilities.acad_layers import get_all_layer_names
from utilities.acad_io import (
    get_selection_from_list,
    get_user_input,
    display_message,
    get_confirmation
)
from utilities.acad_association import (
    EnhancedElementAssociator, select_additional_layers_interactive
)


def main():
    """Función principal del programa."""
    acad = require_autocad("Asociación Inteligente de Elementos")
    # Configuración del Asociador
    associator = EnhancedElementAssociator(acad)
    all_layers = get_all_layer_names(acad)

    # A. Capa Fuente (Bloques)
    source = get_selection_from_list(
        "Paso 1: Capa de Elementos Físicos (Bloques)", all_layers)
    if not source:
        return
    associator.set_source_layer(source)

    # B. Capa Destino (Números)
    target = get_selection_from_list(
        "Paso 2: Capa de Numeración (Texto)", all_layers)
    if not target:
        return
    associator.set_target_layer(target)

    # C. Capas Adicionales (Info extra)
    if get_confirmation("¿Desea extraer texto de capas adicionales (ej. Material)?"):
        extras = select_additional_layers_interactive(
            acad, all_layers, exclude_layers=[source, target])
        for layer in extras:
            associator.add_additional_layer(layer)

    # D. Configuración de Distancia
    try:
        dist_input = get_user_input(
            "Distancia máxima de búsqueda (Enter para infinito)", default="inf")
        if dist_input.lower() != "inf":
            associator.set_max_distance(float(dist_input))
    except ValueError:
        display_message(
            "Valor inválido, usando distancia infinita.", "warning")

    # Ejecución (El trabajo pesado lo hace utilities)
    display_message("\nIniciando análisis...", "info")

    # Extracción
    if not associator.extract_source_elements():
        return
    if not associator.extract_target_elements():
        return
    if associator.additional_layers:
        associator.extract_additional_elements()

    # Cálculo
    associations = associator.associate_by_proximity()

    if not associations:
        display_message("No se encontraron asociaciones válidas.", "warning")
        return

    # Resultados y Exportación
    if associator.additional_layers:
        associator.display_enhanced_associations()
        if get_confirmation("¿Exportar matriz de datos completa?"):
            associator.export_enhanced_data()
    else:
        associator.display_associations()
        if get_confirmation("¿Exportar resultados simples?"):
            associator.export_data()

    display_message("Proceso finalizado.", "success")


if __name__ == "__main__":
    main()
