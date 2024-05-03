from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PySide6 import QtCore


class InfoPopup(QDialog):
    def __init__(self, text, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        message_label = QLabel(text)
        layout.addWidget(message_label)

        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)