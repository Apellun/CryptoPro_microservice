from typing import Dict, List
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QSizePolicy,
    QScrollArea, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, QThreadPool, Signal
from PySide6.QtGui import QIcon
from project.interface.dialogs.add_org_widget import AddOrgWidget
from project.interface.dialogs.update_org_widget import UpdateOrgWidget
from project.interface.dialogs.popups import InfoPopup, ConfirmationPopup
from project.interface.utils.threads import DeleteOrgThread


class OrgListTab(QWidget):
    org_updated = Signal(list)
    org_deleted = Signal(str)

    def __init__(self, parent: QWidget, org_list: List[object]):
        super().__init__()

        self.parent = parent
        self.org_list = org_list

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.scroll_content = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        self._populate_org_list()

        self.add_org_button = QPushButton("Добавить организацию")
        self.add_org_button.clicked.connect(self._add_org)
        self.main_layout.addWidget(self.add_org_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.threadpool = QThreadPool()
        self.progress_popup = InfoPopup("Подождите, операция выполняется.", self)

        self.add_org_widget = AddOrgWidget()

    def _create_org_widget(self, org) -> QWidget:
        org_widget = QWidget()
        org_layout = QHBoxLayout(org_widget)
        org_layout.setContentsMargins(0, 0, 0, 0)
        org_layout.setSpacing(10)

        org_str = f"{org['inn']}"
        if org['name']:
            org_str += f" ({org['name']})"

        label = QLabel(org_str)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(5)

        edit_button = QPushButton()
        edit_button.setIcon(QIcon("path/to/pencil_icon.png"))
        edit_button.setFixedSize(16, 16)
        edit_button.clicked.connect(lambda: self.update_org(org['inn'], org['name'], org_widget))

        delete_button = QPushButton()
        delete_button.setIcon(QIcon("path/to/minus_icon.png"))
        delete_button.setFixedSize(16, 16)
        delete_button.clicked.connect(lambda: self.confirm_delete(org['inn'], org_widget))

        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)

        org_layout.addWidget(label)
        org_layout.addLayout(button_layout)

        return org_widget

    def _add_org_to_list(self, org) -> None:
        org_widget = self._create_org_widget(org)
        self.scroll_content_layout.addWidget(org_widget)

    def _populate_org_list(self) -> None:
        for org in self.org_list:
            self._add_org_to_list(org)

    def _add_org(self) -> None:
        self.add_org_widget.show()

    def _on_finished_update(self, org_widget: QWidget, previous_org: Dict, org_details: Dict)\
            -> None:
        layout = org_widget.layout()
        for j in range(org_widget.layout().count()):
            child = layout.itemAt(j).widget()
            if isinstance(child, QLabel):
                child.setText(f"{org_details["inn"]} ({org_details["name"]})")
        self.org_updated.emit([previous_org, org_details])

    def _on_delete_org(self, org_inn: str, org_widget: QWidget) -> None:
        if self.progress_popup:
            self.progress_popup.close()
        org_widget.deleteLater()
        self.org_deleted.emit(org_inn)

    def _on_update_progress(self) -> None:
        self.progress_popup.show()

    def _on_update_error(self, message: str) -> None:
        if self.progress_popup:
            self.progress_popup.close()
        QMessageBox.warning(self, "Ошибка", message)

    def confirm_delete(self, org_inn: str, org_widget: QWidget) -> None:
        confirmation_popup = ConfirmationPopup(
            f"Удалить организацию с ИНН {org_inn}?"
        )
        if confirmation_popup.exec() == QDialog.Accepted:
            self.delete_org(org_inn, org_widget)

    def update_org(self, org_inn: str, org_name: str, org_widget: QWidget) -> None:
        self.update_org_widget = UpdateOrgWidget(org_inn, org_name, org_widget)
        previous_org = (
            {"name": org_widget,
             "inn": org_inn}
        )
        self.update_org_widget.org_updated.connect(
            lambda updated_org: self._on_finished_update(
                org_widget, previous_org, updated_org
            )
        )
        self.update_org_widget.show()

    def delete_org(self, org_inn: str, org_widget: QWidget) -> None:
        thread = DeleteOrgThread(org_inn)
        thread.signals.finished.connect(lambda: self._on_delete_org(org_inn, org_widget))
        thread.signals.error.connect(self._on_update_error)
        self.threadpool.start(thread)
        self._on_update_progress()
