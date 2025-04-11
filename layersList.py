from colorama import init, Fore, Style, just_fix_windows_console
from termcolor import colored
from utilities.acad_common import initialized_autocad
from utilities.acad_layers import list_layers

just_fix_windows_console()
init()


def main():
    acad = initialized_autocad(
        colored("Programa para listar capas en AutoCAD", 'cyan', attrs=['bold']))
    if not acad:
        return

    # Obtener información de las capas
    layers_info = list_layers(acad)

    # Mostrar resultados
    print(f"\n{Fore.BLUE}Capas utilizadas:")
    print("-" * 35)
    for layer_name in layers_info["used"]:
        print(f"- {layer_name}")

    print(f"\n{Fore.YELLOW}Capas sin utilizar:")
    print("-" * 35)
    for layer_name in layers_info["unused"]:
        print(f"- {layer_name}")

    print(colored(f"\nTotal de capas:", 'white', attrs=['bold']))
    print("*" * 35)
    print(f"- Capas en uso: {layers_info['counts']['used']}")
    print(f"- Capas sin uso: {layers_info['counts']['unused']}")
    print(f"- Total: {layers_info['counts']['total']}")


if __name__ == "__main__":
    main()
