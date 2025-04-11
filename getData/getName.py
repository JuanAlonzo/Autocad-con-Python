from pyautocad import Autocad
from colorama import init, Fore, Style, just_fix_windows_console
from termcolor import colored

just_fix_windows_console()
init(autoreset=True)

try:
    acad = Autocad()

    if acad.doc:
        print(f"{Fore.GREEN}Nombre del plano: {acad.doc.Name}")
    else:
        print(f"{Fore.YELLOW}No hay un documento activo en AutoCAD.")

except Exception as e:
    print(f"{Fore.RED}Error al conectar con AutoCAD: {e}")
    acad = None
    print(colored("No se pudo conectar a AutoCAD.", 'green', 'on_red'))
