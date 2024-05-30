import re
from PySide6.QtWidgets import (
    QWidget, QLineEdit, QVBoxLayout,
    QLabel, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QThreadPool, Signal
from project.interface.utils.threads import AddOrgThread
from project.interface.utils.text import MainText, AddOrgText as Text
from project.interface.utils.const import Const


class AddOrgWidget(QWidget):
    org_added = Signal(dict)

    def __init__(self):
        super().__init__()

        self._init_ui_()
        self.threadpool = QThreadPool()

    @staticmethod
    def _validate_inn(inn: str) -> bool:
        if inn.isnumeric():
            pat = re.compile(Const.inn_validation_pattern)
            if re.fullmatch(pat, inn):
                return True
        return False

    def _init_ui_(self):
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.inn_label = QLabel(Text.inn_label)
        self.inn_edit = QLineEdit()
        self.layout.addWidget(self.inn_label)
        self.layout.addWidget(self.inn_edit)

        self.org_name_label = QLabel(Text.org_name_label)
        self.org_name_edit = QLineEdit()
        self.layout.addWidget(self.org_name_label)
        self.layout.addWidget(self.org_name_edit)

        self.add_org_button = QPushButton(Text.add_org_button)
        self.add_org_button.clicked.connect(self.add_org)
        self.layout.addWidget(self.add_org_button)

    def _on_update_finished(self) -> None:
        QMessageBox.information(
            self,
            MainText.success_title,
            Text.org_added)
        self.org_added.emit(
            {
                Const.org_name_index: self.org_name_edit.text(),
                Const.org_inn_index: self.inn_edit.text()
            }
        )

    def _on_update_error(self, message: str) -> None:
        QMessageBox.warning(self, MainText.error_title, message)

    def add_org(self) -> None:
        org_name = self.org_name_edit.text()
        org_inn = self.inn_edit.text()

        if not org_inn:
            QMessageBox.warning(
                self,
                MainText.error_title,
                Text.empty_inn_error)
            return
        if not self._validate_inn(org_inn):
            QMessageBox.warning(
                self,
                MainText.error_title,
                MainText.inn_validation_error)
            return

        thread = AddOrgThread(org_inn, org_name)
        thread.signals.finished.connect(self._on_update_finished)
        thread.signals.error_popup.connect(lambda error: self._on_update_error(error))
        self.threadpool.start(thread)