from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStyle,
    QScrollArea, QDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from project.interface.core.threads.thread_manager import thread_manager
from project.interface.dialogs.add_org_widget import AddOrgWidget
from project.interface.dialogs.update_org_widget import UpdateOrgWidget
from project.interface.dialogs.popups import ConfirmationPopup
from project.interface.utils.text import OrgListText as Text
from project.interface.utils.data_manager import data_manager
from project.interface.utils.const import Const


class OrgListTab(QWidget):
    def __init__(self, parent: QWidget):
        self.parent = parent
        super().__init__(parent=self.parent)

        self.org_list = parent.org_list

        self.update_org_widget = UpdateOrgWidget(parent=self)

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

        self.add_org_popup = AddOrgWidget()

    def _connect_buttons(self):
        self.add_org_button.clicked.connect(self._add_org)

    def _create_org_widget(self, org_name: str, org_inn: str) -> QWidget:
        org_widget = QWidget()
        org_layout = QHBoxLayout(org_widget)
        org_layout.setContentsMargins(*Const.org_list_margins)
        org_layout.setSpacing(Const.org_list_layout_spacing)

        org_str = data_manager.get_org_string(
            org_name=org_name,
            org_inn=org_inn
        )
        label = QLabel(org_str)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(*Const.org_list_margins)
        button_layout.setSpacing(Const.org_list_button_spacing)

        edit_icon = self.style().standardIcon(QStyle.SP_BrowserReload)

        edit_button = QPushButton()
        edit_button.setIcon(QIcon(edit_icon))
        edit_button.setFixedSize(*Const.org_list_button_size)
        edit_button.clicked.connect(
            lambda: self.update_org(org_inn, org_name, org_widget)
        )

        trash_icon = self.style().standardIcon(QStyle.SP_TrashIcon)

        delete_button = QPushButton()
        delete_button.setIcon(trash_icon)
        delete_button.setFixedSize(*Const.org_list_button_size)
        delete_button.clicked.connect(
            lambda: self.confirm_delete(org_inn, org_widget)
        )

        button_layout.addWidget(delete_button)
        button_layout.addWidget(edit_button)

        org_layout.addLayout(button_layout)
        org_layout.addWidget(label)

        return org_widget

    def _add_org_widget(self, org_name: str, org_inn: str) -> None:
        org_widget = self._create_org_widget(org_name, org_inn)
        self.scroll_content_layout.addWidget(org_widget)

    def _populate_org_list(self) -> None:
        for org in self.org_list:
            self._add_org_widget(org["name"], org["inn"])

    def _add_org(self) -> None:
        self.add_org_popup.show()

    def on_org_added(self, org_name: str, org_inn: str) -> None:
        org_widget = self._create_org_widget(org_name, org_inn)
        self.scroll_content_layout.addWidget(org_widget)

    @staticmethod
    def _update_org_label(
            widget: QWidget, org_inn: str,
            org_name: str = None
    ) -> None:
        layout = widget.layout() #TODO separate
        label = layout.itemAt(1).widget()

        org_str = data_manager.get_org_string(
            org_inn=org_inn,
            org_name=org_name
        )
        label.setText(org_str)

    def _update_org_buttons(
            self, org_inn: str, org_name: str, widget: QWidget
    ) -> None:
        layout = widget.layout()

        button_layout = layout.itemAt(0).layout() #TODO separate
        delete_button = button_layout.itemAt(0).widget()
        edit_button = button_layout.itemAt(1).widget()

        delete_button.clicked.disconnect()
        edit_button.clicked.disconnect()

        delete_button.clicked.connect(
            lambda: self.confirm_delete(org_inn, widget)
        )
        edit_button.clicked.connect(
            lambda: self.update_org(org_inn, org_name, widget)
        )

    def on_org_updated(
            self, old_inn: str, org_inn: str, org_name: str, org_widget: QWidget
    ) -> None:
        self._update_org_label(
            org_name=org_name,
            org_inn=org_inn,
            widget=org_widget
        )
        self._update_org_buttons(
            widget=org_widget,
            org_inn=org_inn,
            org_name=org_name
        )

    def update_org(self, org_inn: str, org_name: str, org_widget: QWidget) -> None: #TODO: wonky result popup
        self.update_org_widget.set_data(
            org_inn=org_inn,
            org_name=org_name,
            org_widget=org_widget
        )
        self.update_org_widget.show()

    @staticmethod
    def on_org_deleted(org_inn: str, org_widget: QWidget) -> None:
        org_widget.deleteLater()

    @staticmethod
    def _delete_org(org_inn: str, org_widget: QWidget) -> None:
        thread_manager.run_delete_org_thread(
            org_inn=org_inn,
            org_widget=org_widget
        )

    def confirm_delete(self, org_inn: str, org_widget: QWidget) -> None:
        confirmation_popup = ConfirmationPopup(
            Text.get_confirm_delete_message(org_inn)
        )
        if confirmation_popup.exec() == QDialog.Accepted:
            self._delete_org(org_inn, org_widget)
