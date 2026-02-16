import win32com.client
import pythoncom
import logging


class CADManager:
    """
    Gestor Singleton para la conexión COM con AutoCAD.
    Reemplaza totalmente a pyautocad eliminando dependencias externas.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CADManager, cls).__new__(cls)
            cls._instance.app = None
            cls._instance.doc = None
            cls._instance.msp = None  # ModelSpace
            cls._instance.logger = logging.getLogger("CADManager")
        return cls._instance

    def connect(self) -> bool:
        """Intenta conectar a una instancia activa de AutoCAD."""
        try:
            # GetActiveObject lanza error si AutoCAD no está abierto
            self.app = win32com.client.GetActiveObject("AutoCAD.Application")
            self.doc = self.app.ActiveDocument
            self.msp = self.doc.ModelSpace
            self.logger.info(f"Conectado exitosamente a: {self.doc.Name}")
            return True
        except Exception as e:
            self.logger.error(f"No se pudo conectar a AutoCAD: {e}")
            self.app = None
            self.doc = None
            return False

    @property
    def is_connected(self) -> bool:
        return self.doc is not None

    def variant_point(self, x: float, y: float, z: float = 0.0):
        """Convierte coordenadas Python a VARIANT (array de doubles) para AutoCAD."""
        return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y, z))


# Instancia global lista para importar
cad = CADManager()
