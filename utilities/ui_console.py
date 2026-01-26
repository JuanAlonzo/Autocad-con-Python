from .ui_interface import UserInterface
from rich.console import Console
from rich.progress import Progress
from rich.prompt import Prompt, Confirm
from rich.table import Table

_console = Console()


class ConsoleUI(UserInterface):
    def __init__(self):
        self.progress = Progress(console=_console)
        self.current_task = None

    def show_message(self, message: str, level: str = "info"):
        styles = {
            "info": "cyan",
            "success": "bold green",
            "warning": "bold yellow",
            "error": "bold red",
        }
        style = styles.get(level, "white")
        prefix = {"info": "ℹ", "success": "✅", "warning": "⚠️", "error": "❌"}
        _console.print(f"[{style}]{prefix.get(level, '')} {message}[/]")

    def show_table(self, headers: list, data: list):
        table = Table(show_header=True, header_style="bold magenta")
        for header in headers:
            table.add_column(header)
        for row in data:
            table.add_row(*[str(item) for item in row])
        _console.print(table)

    def get_input(self, prompt: str, default: str = None) -> str:
        p_text = f"[cyan]{prompt}[/]"
        if default:
            p_text += f" (Enter = {default})"
        return Prompt.ask(p_text, default=default)

    def get_selection(self, prompt: str, options: list) -> str:
        _console.print(f"\n[bold]{prompt}[/]")
        for i, opt in enumerate(options, 1):
            _console.print(f"  {i}. {opt}")

        while True:
            choice = Prompt.ask("Seleccione una opción", default="1")
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
            _console.print("[red]Opción inválida.[/]")

    def confirm(self, prompt: str) -> bool:
        return Confirm.ask(f"[bold yellow]{prompt}[/]")

    def progress_start(self, total: int, description: str):
        self.progress = Progress(console=_console)
        self.progress.start()
        self.current_task = self.progress.add_task(f"[green]{description}", total=total)

    def progress_update(self, step: int = 1):
        if self.current_task is not None:
            self.progress.advance(self.current_task, advance=step)

    def progress_stop(self):
        self.progress.stop()
        self.current_task = None
