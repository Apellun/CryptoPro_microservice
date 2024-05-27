import re
from PySide6.QtWidgets import (
    QWidget, QLineEdit, QVBoxLayout,
    QLabel, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QThreadPool, Signal
from project.interface.utils.threads import AddOrgThread


class AddOrgWidget(QWidget):
    org_added = Signal(dict)

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.inn_label = QLabel("Новый ИНН:")
        self.inn_edit = QLineEdit()
        self.layout.addWidget(self.inn_label)
        self.layout.addWidget(self.inn_edit)

        self.org_name_label = QLabel("Название организации:")
        self.org_name_edit = QLineEdit()
        self.layout.addWidget(self.org_name_label)
        self.layout.addWidget(self.org_name_edit)

        self.add_org_button = QPushButton("Добавить организацию")
        self.add_org_button.clicked.connect(self.add_org)
        self.layout.addWidget(self.add_org_button)

        self.threadpool = QThreadPool()

    @staticmethod
    def _validate_inn(inn: str) -> bool:
        if inn.isnumeric():
            pat = re.compile(r"^\d{10,12}$")
            if re.fullmatch(pat, inn):
                return True
        return False

    def _on_update_finished(self) -> None:
        QMessageBox.information(self, "Успешно", "Организация успешно добавлена.")
        self.org_added.emit(
            {
                "name": self.org_name_edit.text(),
                "inn": self.inn_edit.text()
            }
        )

    def _on_update_error(self, message: str) -> None:
        QMessageBox.warning(self, "Ошибка", message)

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
        thread.signals.finished.connect(self._on_update_finished)
        thread.signals.error_popup.connect(lambda error: self._on_update_error(error))
        self.threadpool.start(thread)