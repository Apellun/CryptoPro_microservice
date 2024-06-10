from PySide6.QtWidgets import (
    QWidget, QLineEdit, QVBoxLayout,
    QLabel, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QThreadPool
from project.interface.core.threads.thread_manager import thread_manager
from project.interface.utils.text import ConfigureServerText as Text, MainText


class ConfigureServerTab(QWidget):
    def __init__(self, parent: QWidget):
        self.parent = parent
        super().__init__(parent=parent)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.host_label = QLabel(Text.host_label)
        self.host_edit = QLineEdit()
        self.layout.addWidget(self.host_label)
        self.layout.addWidget(self.host_edit)

        self.port_label = QLabel(Text.port_label)
        self.port_edit = QLineEdit()
        self.layout.addWidget(self.port_label)
        self.layout.addWidget(self.port_edit)

        self.saveButton = QPushButton(Text.save_button)
        self.layout.addWidget(self.saveButton)
        self.saveButton.clicked.connect(self.update_server_settings)

        self.threadpool = QThreadPool()

    def update_server_settings(self) -> None:
        host = self.host_edit.text()
        port = self.port_edit.text()

        if not host or not port:
            QMessageBox.warning(self, MainText.error_title, Text.empty_field_error)
            return
        if not port.isnumeric():
            QMessageBox.warning(self, MainText.error_title, Text.port_validation_error)
            return

        thread_manager.run_update_server_settings_thread(host=host, port=port)
