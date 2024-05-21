from PySide6.QtWidgets import (
    QWidget, QLineEdit, QVBoxLayout,
    QLabel, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QThreadPool
from project.interface.utils.threads import UpdateServerSettingsThread


class ConfigureServerTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.host_label = QLabel("Адрес:")
        self.host_edit = QLineEdit()
        self.layout.addWidget(self.host_label)
        self.layout.addWidget(self.host_edit)

        self.port_label = QLabel("Порт:")
        self.port_edit = QLineEdit()
        self.layout.addWidget(self.port_label)
        self.layout.addWidget(self.port_edit)

        self.saveButton = QPushButton("Сохранить")
        self.layout.addWidget(self.saveButton)
        self.saveButton.clicked.connect(self.update_server_settings)

        self.threadpool = QThreadPool()

    def update_server_settings(self) -> None:
        host = self.host_edit.text()
        port = self.port_edit.text()

        if not host or not port:
            QMessageBox.warning(self, "Ошибка","Значения полей не могут быть пустыми.")
            return
        if not port.isnumeric():
            QMessageBox.warning(self, "Ошибка",'Убедитесь, что в поле "порт" только цифры')
            return

        thread = UpdateServerSettingsThread(host, port)
        thread.signals.finished.connect(self.on_update_finished)
        thread.signals.error.connect(self.on_update_error)
        self.threadpool.start(thread)

    def on_update_finished(self) -> None:
        QMessageBox.information(self, "Успешно", "Настройки успешно изменены.")

    def on_update_error(self, message: str) -> None:
        QMessageBox.warning(self, "Ошибка", message)
