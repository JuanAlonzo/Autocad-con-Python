from colorama import Fore
from termcolor import colored
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from utilities.acad_common import initialized_autocad
from utilities.acad_layers import list_layers

console = Console()


def main():
    acad = initialized_autocad(
        colored("Programa para listar capas en AutoCAD", 'cyan', attrs=['bold']))
    if not acad:
        print(colored(
            "\nNo se puede continuar sin una conexión a AutoCAD.", 'red', attrs=['bold']))
        input(colored("Presione Enter para salir...", 'white', attrs=['bold']))
        return

    while True:
        try:
            # Obtener información de las capas
            layers_info = list_layers(acad)
            console.print(Panel(
                Text("LISTADO DE CAPAS EN AUTOCAD", style="bold white"),
                border_style="cyan"
            ))

            used_table = Table(title="Capas en Uso",
                               show_header=True,
                               header_style="bold blue",
                               border_style="blue")
            used_table.add_column("#", style="dim", width=4)
            used_table.add_column("Nombre de Capa", style="blue")
            unused_table = Table(title="Capas sin Usar",
                                 show_header=True,
                                 header_style="bold yellow",
                                 border_style="yellow")
            unused_table.add_column("#", style="dim", width=4)
            unused_table.add_column("Nombre de Capa", style="yellow")

            for i, layer_name in enumerate(sorted(layers_info["used"]), 1):
                used_table.addrow(str(i), layer_name)

            for i, layer_name in enumerate(sorted(layers_info["unused"]), 1):
                unused_table.addrow(str(i), layer_name)

            console.print(used_table)
            console.print(unused_table)

            summary_table = Table(show_header=False, box=None)
            summary_table.add_column(style="bold white")
            summary_table.add_column(style="cyan")

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

            # print(colored(f"\nTotal de capas:", 'white', attrs=['bold']))
            # print("*" * 35)
            # print(f"- Capas en uso: {layers_info['counts']['used']}")
            # print(f"- Capas sin uso: {layers_info['counts']['unused']}")
            # print(f"- Total: {layers_info['counts']['total']}")
            break
        except KeyboardInterrupt:
            print(colored("\nOperación cancelada por el usuario.",
                          'yellow', attrs=['bold']))
            break
        except Exception as e:
            print(colored(f"Error inesperado: {e}", 'red'))
            input(colored(
                "Presione Enter para continuar o Ctrl+C para salir...", 'white', attrs=['bold']))
            break


if __name__ == "__main__":
    main()
