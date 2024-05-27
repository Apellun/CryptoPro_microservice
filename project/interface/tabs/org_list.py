from typing import Dict, List, Optional
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStyle,
    QScrollArea, QDialog
)
from PySide6.QtCore import Qt, QThreadPool, Signal
from PySide6.QtGui import QIcon
from project.interface.dialogs.add_org_widget import AddOrgWidget
from project.interface.dialogs.update_org_widget import UpdateOrgWidget
from project.interface.dialogs.popups import ConfirmationPopup
from project.interface.dialogs.progress_dialog import ProgressDialog
from project.interface.utils.threads import DeleteOrgThread


class OrgListTab(QWidget):
    org_updated = Signal(dict)
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

        self.add_org_button = QPushButton("Добавить организацию")
        self.add_org_button.clicked.connect(self._add_org)
        self.main_layout.addWidget(self.add_org_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.add_org_widget = AddOrgWidget()
        self.add_org_widget.org_added.connect(self._on_added_org)

        self.threadpool = QThreadPool()
        self.progress_dialog = ProgressDialog(self)
        self.update_org_widget = None #TODO init here

        self._populate_org_list()

    def _create_org_widget(self, org: Dict[str, str]) -> QWidget:
        org_widget = QWidget()
        org_layout = QHBoxLayout(org_widget)
        org_layout.setContentsMargins(0, 0, 0, 0)
        org_layout.setSpacing(10)

        org_str = f"{org['inn']}"
        if org['name']:
            org_str += f" ({org['name']})"

        label = QLabel(org_str)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(5)

        edit_icon = self.style().standardIcon(QStyle.SP_BrowserReload)

        edit_button = QPushButton()
        edit_button.setIcon(QIcon(edit_icon))
        edit_button.setFixedSize(16, 16)
        edit_button.clicked.connect(lambda: self.update_org(org['inn'], org['name'], org_widget))

        trash_icon = self.style().standardIcon(QStyle.SP_TrashIcon)

        delete_button = QPushButton()
        delete_button.setIcon(trash_icon)
        delete_button.setFixedSize(16, 16)
        delete_button.clicked.connect(lambda: self.confirm_delete(org['inn'], org_widget))

        button_layout.addWidget(delete_button)
        button_layout.addWidget(edit_button)

        org_layout.addLayout(button_layout)
        org_layout.addWidget(label)

        return org_widget

    def _add_org_widget(self, org: Dict[str, str]) -> None:
        org_widget = self._create_org_widget(org)
        self.scroll_content_layout.addWidget(org_widget)

    def _populate_org_list(self) -> None:
        for org in self.org_list:
            self._add_org_widget(org)

    def _add_org(self) -> None: #TODO: needs progress popup + the org list doesnt refresh after adding
        self.add_org_widget.show()

    def _on_added_org(self, update_info: Dict[str, str]) -> None:
        org_widget = self._create_org_widget(update_info)
        self.scroll_content_layout.addWidget(org_widget)

    def _on_finished_update(self, to_update_info: Dict[str, Optional[dict | QWidget]]) -> None:
        layout = to_update_info["widget"].layout()
        label = layout.itemAt(1).widget()
        label.setText(f"{to_update_info["updated_org"]["inn"]} ({to_update_info["updated_org"]["name"]})")

        button_layout = layout.itemAt(0).layout()
        delete_button = button_layout.itemAt(0).widget()
        edit_button = button_layout.itemAt(1).widget()

        delete_button.clicked.disconnect()
        edit_button.clicked.disconnect()

        delete_button.clicked.connect(
            lambda: self.confirm_delete(
                to_update_info["updated_org"]["inn"],
                to_update_info["widget"])
        )
        edit_button.clicked.connect(
            lambda: self.update_org(
                to_update_info["updated_org"]["inn"],
                to_update_info["updated_org"]["name"],
                to_update_info["widget"])
        )

        self.org_updated.emit(
            {
            "updated_org": to_update_info["updated_org"],
            "previous_org": to_update_info["previous_org"],
        }
        )

    def update_org(self, org_inn: str, org_name: str, org_widget: QWidget) -> None: #TODO: doesnt find org by inn + wonky result popup
        self.update_org_widget = UpdateOrgWidget(org_inn, org_name, org_widget, parent=self)
        self.update_org_widget.org_updated.connect(
            lambda to_update_info: self._on_finished_update(to_update_info)
        )
        self.update_org_widget.show()

    def _on_delete_org(self, org_inn: str, org_widget: QWidget) -> None:
        org_widget.deleteLater()
        self.org_deleted.emit(org_inn)

    def _delete_org(self, org_inn: str, org_widget: QWidget) -> None:
        thread = DeleteOrgThread(org_inn)
        thread.signals.progress_popup.connect(lambda message: self.progress_dialog.update_progress(message=message))
        thread.signals.finished_popup.connect(lambda message: self.progress_dialog.update_finished(message=message))
        thread.signals.finished.connect(lambda: self._on_delete_org(org_inn, org_widget)) #TODO message
        thread.signals.error_popup.connect(lambda error: self.progress_dialog.update_error(message=error))
        self.threadpool.start(thread)

    def confirm_delete(self, org_inn: str, org_widget: QWidget) -> None:
        confirmation_popup = ConfirmationPopup(
            f"Удалить организацию с ИНН {org_inn}?"
        )
        if confirmation_popup.exec() == QDialog.Accepted:
            self._delete_org(org_inn, org_widget)
