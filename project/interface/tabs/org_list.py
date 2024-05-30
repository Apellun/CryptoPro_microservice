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
from project.interface.utils.text import OrgListText as Text
from project.interface.utils.data_manager import data_manager
from project.interface.utils.const import Const


class OrgListTab(QWidget):
    org_updated = Signal(dict)
    org_deleted = Signal(str)

    def __init__(self, org_list: List[Dict[str, str]]):
        super().__init__()

        self.org_list = org_list

        self.threadpool = QThreadPool()
        self.progress_dialog = ProgressDialog(self)
        self.update_org_widget = None

        self._init_ui_()
        self._connect_buttons()
        self._populate_org_list()

    def _init_ui_(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )

        self.scroll_content = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        self.add_org_button = QPushButton(Text.add_org_button)
        self.main_layout.addWidget(
            self.add_org_button,
            alignment=Qt.AlignmentFlag.AlignRight
        )

        self.add_org_widget = AddOrgWidget()

    def _connect_buttons(self):
        self.add_org_button.clicked.connect(self._add_org)
        self.add_org_widget.org_added.connect(self._on_added_org)

    def _create_org_widget(self, org: Dict[str, str]) -> QWidget:
        org_widget = QWidget()
        org_layout = QHBoxLayout(org_widget)
        org_layout.setContentsMargins(*Const.org_list_margins)
        org_layout.setSpacing(Const.org_list_layout_spacing)

        org_str = data_manager.get_org_string(org)
        label = QLabel(org_str)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(*Const.org_list_margins)
        button_layout.setSpacing(Const.org_list_button_spacing)

        edit_icon = self.style().standardIcon(QStyle.SP_BrowserReload)

        edit_button = QPushButton()
        edit_button.setIcon(QIcon(edit_icon))
        edit_button.setFixedSize(*Const.org_list_button_size)
        edit_button.clicked.connect(
            lambda: self.update_org(
                org[Const.org_inn_index],
                org[Const.org_name_index],
                org_widget
            )
        )

        trash_icon = self.style().standardIcon(QStyle.SP_TrashIcon)

        delete_button = QPushButton()
        delete_button.setIcon(trash_icon)
        delete_button.setFixedSize(*Const.org_list_button_size)
        delete_button.clicked.connect(
            lambda: self.confirm_delete(
                org[Const.org_inn_index],
                org_widget
            )
        )

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

    def _add_org(self) -> None: #TODO: add progress popup
        self.add_org_widget.show()

    def _on_added_org(self, update_info: Dict[str, str]) -> None:
        org_widget = self._create_org_widget(update_info)
        self.scroll_content_layout.addWidget(org_widget)

    def _update_org_label(
            self, widget: QWidget, updated_org: Dict[str, str]
    ) -> None:
        layout = widget.layout()

        label = layout.itemAt(
            Const.org_list_layout_label_index
        ).widget()
        org_str = data_manager.get_org_string(updated_org)
        label.setText(org_str)

    def _update_org_buttons(
            self, widget: QWidget, updated_org: Dict[str, str]
    ) -> None:
        layout = widget.layout()

        button_layout = layout.itemAt(
            Const.org_list_layout_buttons_index
        ).layout()
        delete_button = button_layout.itemAt(
            Const.org_list_buttons_delete_index
        ).widget()
        edit_button = button_layout.itemAt(
            Const.org_list_buttons_edit_index
        ).widget()

        delete_button.clicked.disconnect()
        edit_button.clicked.disconnect()

        delete_button.clicked.connect(
            lambda: self.confirm_delete(
                updated_org[Const.org_inn_index],
                widget)
        )
        edit_button.clicked.connect(
            lambda: self.update_org(
                updated_org[Const.org_inn_index],
                updated_org[Const.org_name_index],
                widget)
        )

    def _on_finished_update(
            self, to_update_info: Dict[str, Optional[Dict | str | QWidget]]
    ) -> None:
        self._update_org_label(
            to_update_info[Const.widget_index],
            to_update_info[Const.updated_org_index]
        )
        self._update_org_buttons(
            to_update_info[Const.widget_index],
            to_update_info[Const.updated_org_index]
        )
        self.org_updated.emit(to_update_info) #TODO: make sure that is received properly

    def update_org(self, org_inn: str, org_name: str, org_widget: QWidget) -> None: #TODO: wonky result popup
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
        thread.signals.progress_popup.connect(
            lambda message: self.progress_dialog.update_progress(message=message)
        )
        thread.signals.finished_popup.connect(
            lambda message: self.progress_dialog.update_finished(message=message)
        )
        thread.signals.finished.connect(
            lambda: self._on_delete_org(org_inn, org_widget)
        )
        thread.signals.error_popup.connect(
            lambda error: self.progress_dialog.update_error(message=error)
        )
        self.threadpool.start(thread)

    def confirm_delete(self, org_inn: str, org_widget: QWidget) -> None:
        confirmation_popup = ConfirmationPopup(
            Text.get_confirm_delete_message(org_inn)
        )
        if confirmation_popup.exec() == QDialog.Accepted:
            self._delete_org(org_inn, org_widget)
