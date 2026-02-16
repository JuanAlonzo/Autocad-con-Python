from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTabWidget,
    QTextEdit,
    QStatusBar,
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("AutoCAD Python Optimizer")
        self.resize(900, 600)

        # Widget Central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # 1. Header (Conexión)
        self.setup_header()

        # 2. Pestañas
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Tab 1: Home / Logs
        self.tab_home = QWidget()
        self.setup_tab_home()
        self.tabs.addTab(self.tab_home, "Inicio & Logs")

        # Tab 2: Herramientas (Aquí irán tus macros migradas)
        self.tab_tools = QWidget()
        self.setup_tab_tools()
        self.tabs.addTab(self.tab_tools, "Herramientas Fibra")

        # Barra de Estado
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def setup_header(self):
        header = QHBoxLayout()

        self.lbl_status = QLabel("Estado: Desconectado")
        self.lbl_status.setStyleSheet("color: red; font-weight: bold;")

        btn_connect = QPushButton("Conectar AutoCAD")
        btn_connect.clicked.connect(self.controller.connect_to_cad)

        header.addWidget(self.lbl_status)
        header.addStretch()
        header.addWidget(btn_connect)

        self.main_layout.addLayout(header)

    def setup_tab_home(self):
        layout = QVBoxLayout(self.tab_home)
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet(
            "background-color: #1e1e1e; color: #00ff00; font-family: Consolas;"
        )
        layout.addWidget(QLabel("Registro de Actividad (Logs):"))
        layout.addWidget(self.log_viewer)

    def setup_tab_tools(self):
        layout = QVBoxLayout(self.tab_tools)
        layout.addWidget(QLabel("Herramientas de Optimización"))

        # Ejemplo: Botón para ejecutar la lógica de numeración
        btn_scan = QPushButton("Escanear Bloques en Capa")
        btn_scan.clicked.connect(self.controller.scan_blocks)
        layout.addWidget(btn_scan)

        layout.addStretch()

    def update_status(self, connected: bool, msg: str):
        if connected:
            self.lbl_status.setText(f"Conectado: {msg}")
            self.lbl_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.lbl_status.setText("Desconectado")
            self.lbl_status.setStyleSheet("color: red; font-weight: bold;")

    def append_log(self, message):
        self.log_viewer.append(message)
