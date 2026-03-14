from typing import TYPE_CHECKING
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from PySide6.QtCore import Qt
from utilities.config import SETTINGS

if TYPE_CHECKING:
    from interface.controllers.capas_ctrl import CapasController


class TabCapas(QWidget):
    def __init__(self, controller: "CapasController"):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)

        # Panel Izquierdo: Controles
        left_layout = QVBoxLayout()

        group_create = QGroupBox("Crear / Actualizar Capa")
        form_create = QFormLayout(group_create)

        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre de la capa")

        self.combo_color = QComboBox()
        for code, color_name in SETTINGS.LAYER_COLORS.items():
            self.combo_color.addItem(f"{code} - {color_name}", userData=int(code))

        self.spin_grosor = QSpinBox()
        self.spin_grosor.setRange(-3, 211)
        self.spin_grosor.setValue(-3)

        form_create.addRow("Nombre:", self.input_nombre)
        form_create.addRow("Color:", self.combo_color)
        form_create.addRow("Grosor:", self.spin_grosor)

        self.btn_crear = QPushButton("Ejecutar Creación")
        self.btn_crear.clicked.connect(self.controller.crear_capa)

        left_layout.addWidget(group_create)
        left_layout.addWidget(self.btn_crear)

        group_acciones = QGroupBox("Gestión de Dibujo")
        vbox_acciones = QVBoxLayout(group_acciones)

        self.btn_actualizar = QPushButton("Escanear Capas del Dibujo")
        self.btn_actualizar.clicked.connect(self.controller.cargar_capas)

        self.btn_eliminar = QPushButton("Eliminar Capa Seleccionada")
        self.btn_eliminar.setStyleSheet(
            "color: white; background-color: #d9534f; font-weight: bold;"
        )
        self.btn_eliminar.clicked.connect(self.controller.eliminar_capa)

        vbox_acciones.addWidget(self.btn_actualizar)
        vbox_acciones.addWidget(self.btn_eliminar)

        left_layout.addWidget(group_acciones)
        left_layout.addStretch()

        layout.addLayout(left_layout, 1)

        # Panel Derecho: Tabla de Resultados
        self.table_capas = QTableWidget()
        self.table_capas.setColumnCount(2)
        self.table_capas.setHorizontalHeaderLabels(["Nombre de Capa", "Estado"])
        self.table_capas.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_capas.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_capas.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout.addWidget(self.table_capas, 2)

    def get_datos_creacion(self) -> dict:
        return {
            "nombre": self.input_nombre.text().strip().upper(),
            "color": self.combo_color.currentData(),
            "grosor": self.spin_grosor.value(),
        }

    def get_capa_seleccionada(self) -> str:
        filas = self.table_capas.selectedItems()
        if filas:
            return self.table_capas.item(filas[0].row(), 0).text()
        return ""

    def poblar_tabla(self, datos: list):
        self.table_capas.setRowCount(0)
        for i, fila in enumerate(datos):
            self.table_capas.insertRow(i)
            self.table_capas.setItem(i, 0, QTableWidgetItem(fila["Nombre"]))

            item_estado = QTableWidgetItem(fila["Estado"])
            if fila["Estado"] == "Vacía":
                item_estado.setForeground(Qt.green)
            else:
                item_estado.setForeground(Qt.yellow)

            self.table_capas.setItem(i, 1, item_estado)

    def set_ui_state(self, is_enabled: bool):
        self.btn_crear.setEnabled(is_enabled)
        self.btn_actualizar.setEnabled(is_enabled)
        self.btn_eliminar.setEnabled(is_enabled)
        self.table_capas.setEnabled(is_enabled)
