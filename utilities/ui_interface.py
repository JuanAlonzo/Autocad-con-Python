from abc import ABC, abstractmethod


class UserInterface(ABC):
    """
    Contrato que debe cumplir cualquier interfaz (Consola o GUI).
    El script principal solo llamará a estos métodos.
    """
    @abstractmethod
    def show_message(self, message: str, level: str = None) -> str:
        """
        Muestra un mensaje (info, success, warning, error).
        """
        pass

    @abstractmethod
    def get_input(self, prompt: str, default: str = None) -> str:
        """
        Solicita una entrada al usuario.
        """
        pass

    @abstractmethod
    def get_selection(self, prompt: str, options: list) -> str:
        """Muestra una lista y devuelve la opción elegida."""
        pass

    @abstractmethod
    def confirm(self, prompt: str) -> bool:
        """Pregunta Sí/No."""
        pass

    @abstractmethod
    def show_table(self, headers: list, data: list):
        """Muestra una tabla de datos."""
        pass

    @abstractmethod
    def progress_start(self, total: int, description: str):
        """Inicia una barra de progreso."""
        pass

    @abstractmethod
    def progress_update(self, step: int = 1):
        """Avanza la barra de progreso."""
        pass

    @abstractmethod
    def progress_stop(self):
        """Cierra/Limpia la barra de progreso."""
        pass
