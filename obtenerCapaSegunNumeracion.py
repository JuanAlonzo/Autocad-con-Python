from utilities.acad_common import (
    initialized_autocad,
    get_available_layers,
    get_valid_layer_input,
    display_message,
    console
)
from utilities.acad_association import (
    EnhancedElementAssociator,
    show_enhanced_export_menu,
    select_additional_layers
)
from rich.panel import Panel
from rich.text import Text


def show_distance_menu():
    """Muestra un menú para configurar la distancia máxima de asociación.

    Returns:
        float: Distancia máxima configurada
    """
    console.print(Panel(
        Text("CONFIGURAR DISTANCIA MÁXIMA", style="bold white"),
        subtitle="Selecciona una opción",
        border_style="cyan"
    ))

    console.print("[1] Sin límite de distancia")
    console.print("[2] Establecer distancia máxima personalizada")

    option = display_message(
        "\nElige una opción (1-2): ",
        style='input',
        use_rich=True
    ).strip()

    if option == "1":
        return float('inf')
    elif option == "2":
        while True:
            try:
                distance = float(display_message(
                    "Introduce la distancia máxima: ",
                    style='input',
                    use_rich=True
                ).strip())

                if distance > 0:
                    return distance
                else:
                    display_message(
                        "La distancia debe ser mayor que cero.", style='error')
            except ValueError:
                display_message(
                    "Por favor, introduce un número válido.", style='error')
    else:
        display_message("Opción no válida. Usando sin límite.",
                        style='warning')
        return float('inf')


def main():
    """Función principal del programa."""
    acad = initialized_autocad(
        display_message("Programa para asociar Elementos con Numeración y Texto", style='info', bold=True))
    if not acad:
        display_message(
            "\nNo se puede continuar sin una conexión a AutoCAD.", style='error')
        display_message("Presione Enter para salir...",
                        style='input', use_rich=True)
        return

    try:
        # Mostrar panel informativo
        console.print(Panel(
            Text("""
Este programa extrae las coordenadas de los elementos (como postes) y los asocia 
a una capa de numeración y a capas adicionales de texto.

El uso de este programa se debe implementar cuando ya exista una capa de numeración
de la cual se pueda hacer el conteo. También permite asociar textos adicionales
de otras capas manteniendo la relación con la numeración.

Si no existe una capa de numeración, el programa no podrá asociar los elementos
correctamente.                 
                 
""", style="white"),
            title="INFORMACIÓN DEL PROGRAMA",
            border_style="blue"))

        # Obtener capas disponibles
        layers_disponibles = get_available_layers(acad)

        # Crear instancia del asociador mejorado
        associator = EnhancedElementAssociator(acad)

        # Obtener capas válidas usando la función mejorada de acad_common
        layer_source = get_valid_layer_input(
            "Escribe el número o nombre de la capa con elementos a asociar",
            layers_disponibles,
            show_table=True
        )
        if layer_source is None:
            display_message("Operación cancelada.", style='warning')
            return
        associator.set_source_layer(layer_source)

        layer_target = get_valid_layer_input(
            "Escribe el número o nombre de la capa de numeración",
            layers_disponibles,
            show_table=True
        )
        if layer_target is None:
            display_message("Operación cancelada.", style='warning')
            return
        associator.set_target_layer(layer_target)

        # Seleccionar capas adicionales de texto
        primary_layers = [layer_source, layer_target]
        additional_layers = select_additional_layers(
            acad, layers_disponibles, primary_layers)

        # Agregar las capas adicionales al asociador
        for layer in additional_layers:
            associator.add_additional_layer(layer)

        # Configurar distancia máxima
        max_distance = show_distance_menu()
        associator.set_max_distance(max_distance)

        # Extraer elementos de la capa fuente
        associator.extract_source_elements()
        associator.extract_target_elements()

        # Extraer elementos de las capas adicionales
        if additional_layers:
            associator.extract_additional_elements()

        # Asociar elementos por proximidad y mostrar resultados
        associations = associator.associate_by_proximity()

        if associations:
            # Mostrar tabla mejorada con asociaciones y textos adicionales
            associator.display_enhanced_associations()

            # Preguntar si se quieren exportar los datos
            exportar = display_message(
                "\n¿Deseas exportar los resultados? (s/n): ",
                style='input',
                use_rich=True
            ).lower().strip()

            if exportar == 's':
                show_enhanced_export_menu(associator)
        else:
            display_message(
                f"No se pudieron asociar elementos entre las capas '{layer_source}' y '{layer_target}'",
                style='warning'
            )

        # Preguntar si desea procesar otras capas
        continuar = display_message(
            "\n¿Deseas procesar otra capa? (s/n): ",
            style='input',
            use_rich=True
        ).lower().strip()

        if continuar == 's':
            main()  # Reiniciar el programa
        else:
            display_message(
                "Programa finalizado. ¡Hasta luego!", style='success')
    except KeyboardInterrupt:
        display_message(
            "\nOperación cancelada por el usuario.", style='warning')
    except Exception as e:
        display_message(f"Error inesperado: {e}", style='error')
        # Para depuración, mostrar el traceback completo
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
