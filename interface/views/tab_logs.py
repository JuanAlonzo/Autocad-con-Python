from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit


class TabLogs(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet(
            "background-color: #1e1e1e; color: #00ff00; font-family: Consolas;"
        )
        layout.addWidget(self.log_viewer)

    def append_log(self, message: str):
        self.log_viewer.append(message)
