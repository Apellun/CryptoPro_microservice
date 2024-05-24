from PySide6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout,
    QHBoxLayout, QPushButton
)
from PySide6 import QtCore


class InfoPopup(QDialog):
    def __init__(self, text=None, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.message_label = QLabel(text)
        self.layout.addWidget(self.message_label)

        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)

    def set_text(self, text: str) -> None:
        self.message_label.setText(text)


class ConfirmationPopup(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Подтвердите действие")
        self.setModal(True)

        layout = QVBoxLayout()

        self.label = QLabel(message)
        layout.addWidget(self.label)

        button_layout = QHBoxLayout()

        self.confirm_button = QPushButton("Продолжить")
        self.confirm_button.clicked.connect(self.accept)
        button_layout.addWidget(self.confirm_button)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)