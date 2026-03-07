from typing import TYPE_CHECKING
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QGroupBox,
    QComboBox,
    QLabel,
    QFormLayout,
    QProgressBar,
)
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

        # Selector de Perfil Estándar
        group_perfil = QGroupBox("1. Estandarización de Numeración")
        form_perfil = QFormLayout(group_perfil)

        self.combo_perfiles = QComboBox()
        # Cargar perfiles desde config
        for key, config in SETTINGS.PERFILES_NUMERACION.items():
            self.combo_perfiles.addItem(config["descripcion"], userData=key)

        form_perfil.addRow(QLabel("Caso de Uso:"), self.combo_perfiles)
        layout.addWidget(group_perfil)

        layout.addStretch()

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.btn_ejecutar_num = QPushButton("SELECCIONAR PUNTO DE INICIO Y NUMERAR")
        self.btn_ejecutar_num.setMinimumHeight(50)
        self.btn_ejecutar_num.setStyleSheet(
            "font-weight: bold; background-color: #2b579a; color: white;"
        )
        self.btn_ejecutar_num.clicked.connect(self.controller.ejecutar_numeracion)
        layout.addWidget(self.btn_ejecutar_num)

    def set_execution_state(self, is_running: bool):
        self.btn_ejecutar_num.setEnabled(not is_running)
        self.progress_bar.setVisible(is_running)
        if not is_running:
            self.progress_bar.setValue(0)

    def update_progress(self, value: int):
        self.progress_bar.setValue(value)

    def get_numeracion_config(self):
        # Recuperar la clave del perfil seleccionado (EXISTENTES, PROYECTADOS o APOYO)
        perfil_key = self.combo_perfiles.currentData()
        perfil_data = SETTINGS.PERFILES_NUMERACION.get(perfil_key, {})

        return {
            "perfil_id": perfil_key,
            "estrategia": perfil_data.get("estrategia"),
            "dict_red": perfil_data.get("dict_red", {}),
            "dict_postes": perfil_data.get("dict_postes", {}),
            "filtro_capa": perfil_data.get("filtro_capa"),
            "tolerancia_grafo": 0.1,
            "radio_snap": 5.0,
        }
