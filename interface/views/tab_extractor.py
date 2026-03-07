from typing import TYPE_CHECKING
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFileDialog,
    QProgressBar,
)

if TYPE_CHECKING:
    from interface.controllers.extractor_ctrl import ExtractorController


class TabExtractor(QWidget):
    def __init__(self, controller: "ExtractorController"):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Nombre de la Capa (vacío = todas):"))

        self.input_layer = QLineEdit()
        self.input_layer.setPlaceholderText("Ej: POSTE_C_9")
        controls_layout.addWidget(self.input_layer)

        self.btn_extract_blocks = QPushButton("Extraer Bloques")
        self.btn_extract_blocks.clicked.connect(
            lambda: self.controller.extract_data("bloques")
        )

        self.btn_extract_texts = QPushButton("Extraer Textos")
        self.btn_extract_texts.clicked.connect(
            lambda: self.controller.extract_data("textos")
        )

        controls_layout.addWidget(self.btn_extract_blocks)
        controls_layout.addWidget(self.btn_extract_texts)
        layout.addLayout(controls_layout)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.btn_export = QPushButton("Exportar a CSV")
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self.controller.export_to_csv)
        layout.addWidget(self.btn_export)

        self.ext_progress = QProgressBar()
        self.ext_progress.setRange(0, 100)
        self.ext_progress.setValue(0)
        self.ext_progress.setVisible(False)
        layout.addWidget(self.ext_progress)

    def set_extraction_state(self, is_running: bool):
        self.ext_progress.setVisible(is_running)
        self.btn_extract_blocks.setEnabled(not is_running)
        self.btn_extract_texts.setEnabled(not is_running)
        if not is_running:
            self.ext_progress.setValue(0)

    def update_progress(self, value: int):
        self.ext_progress.setValue(value)

    def get_layer_input(self) -> str:
        return self.input_layer.text().strip()

    def populate_table(self, data: list):
        self.table.clear()
        if not data:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self.btn_export.setEnabled(False)
            return

        headers = []
        for row in data:
            for key in row.keys():
                if key not in headers:
                    headers.append(key)

        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(data))

        for row_idx, row_data in enumerate(data):
            for col_idx, key in enumerate(headers):
                val = str(row_data.get(key, ""))
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(val))

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.btn_export.setEnabled(True)

    def show_save_dialog(self) -> str:
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar CSV", "", "CSV Files (*.csv)"
        )
        return file_path
