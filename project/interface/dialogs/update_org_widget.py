import re
from PySide6.QtWidgets import (
    QWidget, QLineEdit, QVBoxLayout,
    QLabel, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QThreadPool, Signal
from project.interface.utils.threads import UpdateOrgThread


class UpdateOrgWidget(QWidget):
    org_updated = Signal(dict)

    def __init__(self, org_inn, org_name, widget, parent=None):
        super().__init__()
        self.org_inn = org_inn
        self.org_name = org_name
        self.widget = widget
        self.parent = parent

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.inn_label = QLabel("ИНН:")
        self.inn_edit = QLineEdit()
        self.inn_edit.setText(self.org_inn)
        self.layout.addWidget(self.inn_label)
        self.layout.addWidget(self.inn_edit)

        self.org_name_label = QLabel("Название организации:")
        self.org_name_edit = QLineEdit()
        self.org_name_edit.setText(self.org_name)
        self.layout.addWidget(self.org_name_label)
        self.layout.addWidget(self.org_name_edit)

        self.add_org_button = QPushButton("Изменить данные организации")
        self.add_org_button.clicked.connect(self.update_org)
        self.layout.addWidget(self.add_org_button)

        self.threadpool = QThreadPool()

    @staticmethod
    def _validate_inn(inn: str):
        if inn.isnumeric():
            pat = re.compile(r"^\d{10,12}$")
            if re.fullmatch(pat, inn):
                return True
        return False

    def _on_finished_update(self) -> None:
        self.org_updated.emit(
            {"name": self.org_name_edit.text(),
             "inn": self.inn_edit.text()}
        )

    def update_org(self) -> None:
        org_name = self.org_name_edit.text()
        org_inn = self.inn_edit.text()

        if org_inn:
            if not self._validate_inn(org_inn):
                QMessageBox.warning(self, "Ошибка","Некорерктный ИНН, проверьте правильность заполнения.")
                return

        thread = UpdateOrgThread(
            self.org_inn,
            {"inn": org_inn,
             "name": org_name}
        )

        thread.signals.progress_popup.connect(lambda message: self.parent.progress_dialog.update_progress(message))
        thread.signals.finished_popup.connect(lambda message: self.parent.update_finished.update_progress(message))
        thread.signals.finished.connect(self._on_finished_update)
        thread.signals.error_popup.connect(lambda error: self.parent.progress_dialog.update_error(message=error))
        self.threadpool.start(thread)