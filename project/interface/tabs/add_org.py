import re
from PySide6.QtWidgets import (
    QWidget, QLineEdit, QVBoxLayout,
    QLabel, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QThreadPool, Signal
from project.interface.threads import AddOrgThread
from project.interface.api_manager import manager


class AddOrgTab(QWidget):
    org_added = Signal(dict)

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.inn_label = QLabel("Новый ИНН:")
        self.inn_edit = QLineEdit()
        self.layout.addWidget(self.inn_label)
        self.layout.addWidget(self.inn_edit)

        self.org_name_label = QLabel("Название организации:")
        self.org_name_edit = QLineEdit()
        self.layout.addWidget(self.org_name_label)
        self.layout.addWidget(self.org_name_edit)

        self.add_org_button = QPushButton("Добавить")
        self.add_org_button.clicked.connect(self.add_org)
        self.layout.addWidget(self.add_org_button)

        self.threadpool = QThreadPool()

    @staticmethod
    def _validate_inn(inn: str):
        if inn.isnumeric():
            pat = re.compile(r"^\d{10,12}$")
            if re.fullmatch(pat, inn):
                return True
        return False

    @staticmethod
    def _check_inn_name_exists(inn: str, name: str) -> bool:
        if not manager.org_cash:
            manager.get_org_list()  # TODO: refactor
        for org in manager.org_cash:
            if name:
                if org.name != name and org.inn != inn:
                    return True
            else:
                if org.inn != inn:
                    return True
        return False

    def add_org(self) -> None:
        org_name = self.org_name_edit.text()
        org_inn = self.inn_edit.text()

        if not org_inn:
            QMessageBox.warning(self, "Ошибка","Поле 'ИНН' не может быть пустым.")
            return
        if not self._validate_inn(org_inn):
            QMessageBox.warning(self, "Ошибка","Некорерктный ИНН, проверьте правильность заполнения.")
            return

        thread = AddOrgThread(org_inn, org_name)
        thread.signals.finished.connect(self.on_update_finished)
        thread.signals.error.connect(self.on_update_error)
        self.threadpool.start(thread)

    def on_update_finished(self) -> None:
        QMessageBox.information(self, "Успешно", "ИНН успешно добавлен.")
        self.org_added.emit(
            {"org_name": self.org_name_edit.text(),
             "org_inn": self.inn_edit.text()}
        )

    def on_update_error(self, message: str) -> None:
        QMessageBox.warning(self, "Ошибка", message)