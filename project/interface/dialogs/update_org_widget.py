import re
from PySide6.QtWidgets import (
    QWidget, QLineEdit, QVBoxLayout,
    QLabel, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from project.interface.core.threads.thread_manager import thread_manager
from project.interface.utils.text import MainText
from project.interface.utils.const import Const


class UpdateOrgWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.inn_label = QLabel("ИНН:")
        self.inn_edit = QLineEdit()
        self.layout.addWidget(self.inn_label)
        self.layout.addWidget(self.inn_edit)

        self.org_name_label = QLabel("Название организации:")
        self.org_name_edit = QLineEdit()
        self.layout.addWidget(self.org_name_label)
        self.layout.addWidget(self.org_name_edit)

        self.add_org_button = QPushButton("Изменить данные организации")
        self.add_org_button.clicked.connect(self.update_org)
        self.layout.addWidget(self.add_org_button)

        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)


    @staticmethod
    def _validate_inn(inn: str) -> bool:
        if inn.isnumeric():
            pat = re.compile(Const.inn_validation_pattern)
            if re.fullmatch(pat, inn):
                return True
        return False

    def set_data(self, org_inn, org_name, org_widget) -> None:
        self.org_inn = org_inn
        self.inn_edit.setText(self.org_inn)
        self.org_name = org_name
        self.org_name_edit.setText(self.org_name)
        self.org_widget = org_widget

    def update_org(self) -> None:
        org_name = self.org_name_edit.text()
        org_inn = self.inn_edit.text()

        if org_inn:
            if not self._validate_inn(org_inn):
                QMessageBox.warning(
                    self,
                    MainText.error_title,
                    MainText.inn_validation_error)
                return

        thread_manager.run_update_org_thread(
            old_inn=self.org_inn,
            org_inn=org_inn,
            org_name=org_name,
            org_widget=self.org_widget
        )