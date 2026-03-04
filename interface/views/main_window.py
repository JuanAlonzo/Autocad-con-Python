from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTabWidget,
    QStatusBar,
)

from .tab_extractor import TabExtractor
from .tab_numeracion import TabNumeracion
from .tab_logs import TabLogs


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("AutoCAD Tools v2.0")
        self.resize(500, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        self.setup_header()

        self.tabs = QTabWidget()
        self.tabs.setEnabled(False)
        self.main_layout.addWidget(self.tabs)

        # Inyección de las vistas modulares
        self.tab_extractor = TabExtractor(self.controller.extractor)
        self.tabs.addTab(self.tab_extractor, "Extractor de Entidades")

        self.tab_numeracion = TabNumeracion(self.controller.numeracion)
        self.tabs.addTab(self.tab_numeracion, "Numeración de Postes")

        self.tab_logs = TabLogs()
        self.tabs.addTab(self.tab_logs, "Registro (Logs)")

        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def setup_header(self):
        header = QHBoxLayout()
        self.lbl_status = QLabel("Estado: Desconectado")
        self.lbl_status.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")

        self.btn_connect = QPushButton("Conectar a AutoCAD")
        self.btn_connect.clicked.connect(self.controller.connect_to_cad)

        header.addWidget(self.lbl_status)
        header.addStretch()
        header.addWidget(self.btn_connect)
        self.main_layout.addLayout(header)

    def update_connection_status(self, connected: bool, msg: str):
        if connected:
            self.lbl_status.setText(f"Conectado: {msg}")
            self.lbl_status.setStyleSheet(
                "color: green; font-weight: bold; font-size: 14px;"
            )
            self.btn_connect.setEnabled(False)
            self.tabs.setEnabled(True)
        else:
            self.lbl_status.setText("Desconectado")
            self.lbl_status.setStyleSheet(
                "color: red; font-weight: bold; font-size: 14px;"
            )

    # --- WRAPPERS: Redirigen los métodos del controlador a la pestaña correcta ---

    def append_log(self, message: str):
        self.tab_logs.append_log(message)

    def get_layer_input(self) -> str:
        return self.tab_extractor.get_layer_input()

    def set_extraction_state(self, is_running: bool):
        self.tab_extractor.set_extraction_state(is_running)

    def update_ext_progress(self, value: int):
        self.tab_extractor.update_progress(value)

    def populate_table(self, data: list):
        self.tab_extractor.populate_table(data)

    def show_save_dialog(self) -> str:
        return self.tab_extractor.show_save_dialog()

    def get_numeracion_config(self):
        return self.tab_numeracion.get_numeracion_config()

    def set_execution_state(self, is_running: bool):
        self.tab_numeracion.set_execution_state(is_running)

    def update_progress(self, value: int):
        self.tab_numeracion.update_progress(value)
