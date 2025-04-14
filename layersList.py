from termcolor import colored
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from utilities.acad_common import console, initialized_autocad, display_message
from utilities.acad_layers import list_layers


def main():
    acad = initialized_autocad(
        colored("Programa para listar capas en AutoCAD", 'cyan', attrs=['bold']))
    if not acad:
        display_message(
            "\nNo se puede continuar sin una conexión a AutoCAD.", style='error')
        display_message("Presione Enter para salir...",
                        style='input', use_rich=True)
        return

    while True:
        try:
            # Obtener información de las capas
            layers_info = list_layers(acad)
            console.print(Panel(
                Text("LISTADO DE CAPAS EN AUTOCAD", style="bold white"),
                border_style="white"
            ))

            used_table = Table(title="Capas en Uso",
                               show_header=True,
                               header_style="bold blue",
                               border_style="blue")
            used_table.add_column("#", style="blue", width=4)
            used_table.add_column("Nombre de Capa", style="blue")

            unused_table = Table(title="Capas sin Usar",
                                 show_header=True,
                                 header_style="bold yellow",
                                 border_style="yellow")
            unused_table.add_column("#", style="yellow", width=4)
            unused_table.add_column("Nombre de Capa", style="yellow")

            for i, layer_name in enumerate(sorted(layers_info["used"]), 1):
                used_table.add_row(str(i), layer_name)

            for i, layer_name in enumerate(sorted(layers_info["unused"]), 1):
                unused_table.add_row(str(i), layer_name)

            # Mostrar las tablas en la consola
            console.print(used_table)
            console.print(unused_table)

            summary_table = Table(show_header=False, box=None)
            summary_table.add_column(style="bold white")
            summary_table.add_column(style="bold white")

            summary_table.add_row("Total de capas en uso:", str(
                layers_info['counts']['used']))
            summary_table.add_row("Total de capas sin uso:", str(
                layers_info['counts']['unused']))
            summary_table.add_row("Total de capas:", str(
                layers_info['counts']['total']))

            # Mostrar el resumen dentro de un panel
            console.print(Panel(
                summary_table,
                title="Resumen",
                border_style="white"
            ))
            break
        except KeyboardInterrupt:
            display_message(
                "\nOperación cancelada por el usuario.", style='warning')
            break
        except Exception as e:
            display_message(f"Error inesperado: {e}", style='error')
            display_message(
                "Presione Enter para continuar o Ctrl+C para salir...", style='input', use_rich=True)
            break


if __name__ == "__main__":
    main()
