from PySide6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout,
    QHBoxLayout, QPushButton
)
from PySide6 import QtCore
from project.interface.utils.text import MainText


class InfoPopup(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.message_label = QLabel()
        self.layout.addWidget(self.message_label)

        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)

    def set_text(self, text: str) -> None:
        self.message_label.setText(text)


class ConfirmationPopup(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.message = message

        self._init_ui_()
        self._connect_buttons()

    def _init_ui_(self):
        self.setWindowTitle(MainText.confirm_action)
        self.setModal(True)

        layout = QVBoxLayout()

        self.label = QLabel(self.message)
        layout.addWidget(self.label)

        button_layout = QHBoxLayout()

        self.confirm_button = QPushButton(MainText.continue_action)
        button_layout.addWidget(self.confirm_button)

        self.cancel_button = QPushButton(MainText.discard_action)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _connect_buttons(self):
        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)