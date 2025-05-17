from utilities.acad_common import console, display_message
from enum import IntEnum
from typing import Optional, List, Dict


class OsnapMode(IntEnum):
    """Enum for Object Snap Modes."""
    NONE = 0
    ENDPOINT = 1
    MIDPOINT = 2
    CENTER = 4
    NODE = 8
    QUADRANT = 16
    INTERSECTION = 32
    INSERTION = 64
    PERPENDICULAR = 128
    TANGENT = 256
    NEAREST = 512
    APPARENT_INTERSECTION = 2048
    GEOMETRIC_CENTER = 1024
    EXTENSION = 4096
    PARALLEL = 8192
    ALL = 16383


class AutosnapMode(IntEnum):
    """Enum para los diferentes modos de AUTOSNAP en AutoCAD."""
    NONE = 0
    MARKER = 1
    MAGNET = 2
    TOOLTIP = 4
    APERTURE = 8
    HIGHLIGHT = 16
    POLAR = 32
    ALL = 63


class OsnapManager:
    """Clase para gestionar los OSNAP de AutoCAD."""

    def __init__(self, acad):
        self.acad = acad
        self.osnap_descriptions = {
            OsnapMode.ENDPOINT: "ENDpoint",
            OsnapMode.MIDPOINT: "MIDpoint",
            OsnapMode.CENTER: "CENter",
            OsnapMode.GEOMETRIC_CENTER: "GEometric Center",
            OsnapMode.NODE: "Node",
            OsnapMode.QUADRANT: "QUAdrant",
            OsnapMode.INTERSECTION: "INTersection",
            OsnapMode.EXTENSION: "EXTension",
            OsnapMode.INSERTION: "INSertion",
            OsnapMode.PERPENDICULAR: "PERpendicular",
            OsnapMode.TANGENT: "TANgent",
            OsnapMode.NEAREST: "NEArest",
            OsnapMode.APPARENT_INTERSECTION: "AParent Intersection",
            OsnapMode.PARALLEL: "PARallel",
        }

    def get_current_osnap(self) -> int:
        """Obtiene el valor actual de OSNAP."""
        return self.acad.doc.GetVariable("OSMODE")

    def get_current_autosnap(self) -> int:
        """Obtiene el valor actual de AUTOSNAP."""
        return self.acad.doc.GetVariable("AUTOSNAP")

    def set_osnap(self, mode: int) -> None:
        """Establece el valor de OSNAP."""
        self.acad.doc.SetVariable("OSMODE", mode)

    def set_autosnap(self, mode: int) -> None:
        """Establece el valor de AUTOSNAP."""
        self.acad.doc.SetVariable("AUTOSNAP", mode)

    def toggle_all_osnaps(self, enable: bool = True) -> None:
        """Activa o desactiva todos los OSNAP."""
        if enable:
            self.set_osnap(OsnapMode.ALL)
            self.set_autosnap(AutosnapMode.ALL)
            self.acad.prompt("All object snaps are enabled.")
            display_message(
                "\nTodos los OSNAP han sido activados.", style='success')
        else:
            self.set_osnap(OsnapMode.NONE)
            self.set_autosnap(AutosnapMode.NONE)
            self.acad.prompt("All object snaps are disabled.")
            display_message(
                "\nTodos los OSNAP han sido desactivados.", style='success')

    def toggle_osnap_f3(self, enable: bool = True) -> None:
        """Simula presionar F3 para activar/desactivar OSNAP temporalmente."""
        current_osnap = self.get_current_osnap()

        if enable and current_osnap == 0:
            # Si estaba desactivado, activamos el último valor o todos si no hay valor previo
            last_osnap = getattr(self, '_last_osnap', OsnapMode.ALL)
            self.set_osnap(last_osnap)
            self.set_autosnap(AutosnapMode.ALL)
            display_message(
                "OSNAP activado temporalmente (F3).", style='success')
        elif not enable and current_osnap != 0:
            # Guardamos el valor actual antes de desactivar
            self._last_osnap = current_osnap
            self.set_osnap(OsnapMode.NONE)
            display_message(
                "OSNAP desactivado temporalmente (F3).", style='success')

    def set_custom_osnaps(self, osnap_modes: List[OsnapMode]) -> int:
        """Establece una combinación personalizada de OSNAP.

        Args:
            osnap_modes: Lista de modos OsnapMode a activar

        Returns:
            El valor total configurado para OSNAP
        """
        total = sum(osnap_modes)
        self.set_osnap(total)
        self.set_autosnap(AutosnapMode.ALL)
        self.acad.prompt(f"Object snaps set to {total}\n.")
        return total

    def get_active_osnaps(self) -> Dict[OsnapMode, bool]:
        """Retorna un diccionario con los OSNAP activos.

        Returns:
            Diccionario donde las claves son los modos de OSNAP y los valores son booleanos
            que indican si están activos.
        """
        current = self.get_current_osnap()
        result = {}

        for osnap in OsnapMode:
            if osnap == OsnapMode.NONE or osnap == OsnapMode.ALL:
                continue
            result[osnap] = (current & osnap) == osnap

        return result

    def display_osnap_status(self) -> None:
        """Muestra el estado actual de los OSNAP en una tabla formateada."""
        from rich.table import Table

        active_osnaps = self.get_active_osnaps()
        current_value = self.get_current_osnap()

        table = Table(title=f"Estado OSNAP (Valor actual: {current_value})")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Modo", style="blue")
        table.add_column("Valor", style="magenta", justify="right")
        table.add_column("Estado", style="green")

        for osnap, active in active_osnaps.items():
            table.add_row(
                str(int(osnap.value)),
                self.osnap_descriptions.get(osnap, str(osnap)),
                str(osnap.value),
                "✓ Activo" if active else "✗ Inactivo"
            )

        console.print(table)


def show_osnap_menu(acad):
    """Muestra el menú de gestión de OSNAP y maneja las opciones del usuario."""
    manager = OsnapManager(acad)
    current_osnap = manager.get_current_osnap()

    display_message("\nGestor de OSNAP", style='info', bold=True)
    print("-" * 30)
    print(f"Configuración actual de OSNAP: {current_osnap}")

    # Mostrar estado actual detallado
    manager.display_osnap_status()

    display_message("\nOpciones disponibles:", style='info')
    print("1. Activar todos los OSNAP")
    print("2. Desactivar todos los OSNAP")
    print("3. Configuración personalizada")
    print("4. Simular F3 (activar/desactivar temporalmente)")
    print("5. Volver al menú principal")

    choice = display_message("\nSelecciona una opción: ",
                             style='input', use_rich=True)

    try:
        if choice == "1":
            manager.toggle_all_osnaps(True)
        elif choice == "2":
            manager.toggle_all_osnaps(False)
        elif choice == "3":
            show_custom_osnap_menu(acad, manager)
        elif choice == "4":
            # Detectar si OSNAP está activo o no para decidir qué hacer
            if manager.get_current_osnap() == 0:
                manager.toggle_osnap_f3(True)
            else:
                manager.toggle_osnap_f3(False)
        elif choice == "5":
            return
        else:
            display_message("Opción no válida", style='error')
    except Exception as e:
        display_message(f"\nOcurrió un error: {str(e)}", style='error')
        display_message("Volviendo al menú principal...", style='warning')
        return

    # Mostrar el menú de nuevo para permitir múltiples operaciones
    show_osnap_menu(acad)


def show_custom_osnap_menu(acad, manager):
    """Muestra el menú para configuración personalizada de OSNAP."""
    display_message("\nSelecciona los OSNAP que deseas activar:", style='info')

    # Crear una lista ordenada de opciones
    options = []
    for osnap, description in manager.osnap_descriptions.items():
        options.append((int(osnap), osnap, description))

    # Ordenar por ID
    options.sort(key=lambda x: x[0])

    # Mostrar opciones
    for i, (value, osnap, description) in enumerate(options, 1):
        print(f"{i:02d}. {description} ({value})")

    selections = display_message("\nIngresa los números separados por comas: ",
                                 style='input', use_rich=True)

    # Procesar selecciones
    selected_modes = []
    for sel in selections.split(","):
        sel = sel.strip()
        try:
            # Convertir a índice basado en 1 (como se muestra en el menú)
            idx = int(sel) - 1
            if 0 <= idx < len(options):
                selected_modes.append(options[idx][1])
        except ValueError:
            # Ignorar entradas no válidas
            pass

    # Aplicar configuración
    if selected_modes:
        total = manager.set_custom_osnaps(selected_modes)
        display_message(
            f"OSNAP configurado con valor: {total}", style='success')
    else:
        display_message("No se seleccionaron OSNAP válidos", style='warning')
