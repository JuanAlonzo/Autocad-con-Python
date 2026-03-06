from typing import TYPE_CHECKING
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QGroupBox,
    QDoubleSpinBox,
    QRadioButton,
    QCheckBox,
    QFormLayout,
    QProgressBar,
)
from PySide6.QtCore import Qt
from utilities.config import SETTINGS

if TYPE_CHECKING:
    from interface.controllers.numeracion_ctrl import NumeracionController


class TabNumeracion(QWidget):
    def __init__(self, controller: "NumeracionController"):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        group_ruta = QGroupBox("1. Configuración de la Ruta y Búsqueda")
        form_ruta = QFormLayout(group_ruta)

        self.input_ruta = QLineEdit()
        self.input_ruta.setPlaceholderText(
            f"Por defecto: {SETTINGS.LAYER_PREFIX_POSTES}"
        )
        form_ruta.addRow("Capa de la Ruta:", self.input_ruta)

        self.spin_radio = QDoubleSpinBox()
        self.spin_radio.setRange(0.1, 100.0)
        self.spin_radio.setValue(SETTINGS.DEFAULT_SEARCH_RADIUS)
        form_ruta.addRow("Radio de Búsqueda (m):", self.spin_radio)

        layout.addWidget(group_ruta)

        group_modo = QGroupBox("2. Modo de Ordenamiento Espacial")
        vbox_modo = QVBoxLayout(group_modo)

        self.radio_normal = QRadioButton("Modo Normal (Agrega dispersos al final)")
        self.radio_normal.setChecked(True)
        self.radio_estricto = QRadioButton("Modo Estricto (Ignora fuera del radio)")

        vbox_modo.addWidget(self.radio_normal)
        vbox_modo.addWidget(self.radio_estricto)
        layout.addWidget(group_modo)

        group_datos = QGroupBox("3. Asociación de Datos")
        form_datos = QFormLayout(group_datos)

        self.check_asociar = QCheckBox("Cruzar con datos de otra capa")
        self.check_asociar.stateChanged.connect(self.toggle_asociacion)
        form_datos.addRow(self.check_asociar)

        self.input_datos = QLineEdit()
        self.input_datos.setEnabled(False)
        form_datos.addRow("Capa de Datos:", self.input_datos)

        layout.addWidget(group_datos)

        layout.addStretch()

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.btn_ejecutar_num = QPushButton("EJECUTAR NUMERACIÓN")
        self.btn_ejecutar_num.setMinimumHeight(50)
        self.btn_ejecutar_num.setStyleSheet(
            "font-weight: bold; font-size: 14px; background-color: #2b579a; color: white;"
        )
        self.btn_ejecutar_num.clicked.connect(self.controller.ejecutar_numeracion)
        layout.addWidget(self.btn_ejecutar_num)

    def toggle_asociacion(self, state):
        self.input_datos.setEnabled(state == Qt.Checked.value)

    def set_execution_state(self, is_running: bool):
        self.btn_ejecutar_num.setEnabled(not is_running)
        self.progress_bar.setVisible(is_running)
        if not is_running:
            self.progress_bar.setValue(0)

    def update_progress(self, value: int):
        self.progress_bar.setValue(value)

    def get_numeracion_config(self):
        return {
            "capa_ruta": self.input_ruta.text().strip() or SETTINGS.LAYER_PREFIX_POSTES,
            "radio": self.spin_radio.value(),
            "estricto": self.radio_estricto.isChecked(),
            "asociar": self.check_asociar.isChecked(),
            "capa_datos": self.input_datos.text().strip(),
        }
