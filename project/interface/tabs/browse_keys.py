from typing import Dict
from functools import partial
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QHBoxLayout, QScrollArea,
    QSizePolicy, QCheckBox
)
from PySide6.QtCore import QThreadPool, Qt
from project.interface.utils.threads import UpdateOrgKeysThread
from project.interface.dialogs.progress_dialog import ProgressDialog
from project.utils.csp.win_csp import WinCspManager, CspCertificate
from project.interface.api_manager import manager
from project.interface.utils import mock_csp
from project.interface.utils.mock_csp_updated import get_refreshed_keys_list
from project.interface.utils.const import Const
from project.interface.utils.text import BrowseKeysText as Text
from project.interface.utils.data_manager import data_manager


class KeyItemWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(*Const.browse_keys_margins)
        self.setLayout(self.layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_content = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content_layout.setSpacing(Const.browse_keys_spacing)
        self.scroll_content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)


class BrowseKeysTab(QWidget):
    def __init__(self, org_list):
        super().__init__()

        self.org_list = org_list

        self.orgs_keys_dict = None #half mmutable, dict inn: [key.thumbprint]
        self.keys = None #immutable, objects
        self._checked_keys = None #mutable, dict inn: [key]
        self._unchecked_keys = None #mutable, dict inn: [key]

        self.threadpool = QThreadPool()
        self.progress_dialog = ProgressDialog(self)

        self._processing_update = False

        self._init_ui()
        self._load_data()
        self._fill_ui_with_data()
        self._connect_buttons()

        self.refresh_counter = 0 #TODO cut

    def _on_checkbox_checked(self, state: int, key: CspCertificate) -> None:
        if not self._processing_update:
            if state == Const.checked_checkbox_state:
                key_exists = self._checked_keys.get(key.Thumbprint, None)
                if not key_exists:
                    self._checked_keys[key.Thumbprint] = str(key)
                try:
                    del self._unchecked_keys[key.Thumbprint]
                except KeyError:
                    pass

            elif state == Const.unchecked_checkbox_state:
                key_exists = self._unchecked_keys.get(key.Thumbprint, None)
                if not key_exists:
                    self._unchecked_keys[key.Thumbprint] = str(key)
                    try:
                        del self._checked_keys[key.Thumbprint]
                    except KeyError:
                        pass

    def _on_org_selected(self) -> None:
        self._set_checked_keys()
        self._render_keys()

    def _on_keys_refreshed(self) -> None:
        self.keys_list = get_refreshed_keys_list(self.refresh_counter)

        if self.refresh_counter: #TODO: to cut
            self.refresh_counter = 0
        else:
            self.refresh_counter = 1

        widgets_amount = self.browse_keys_list.scroll_content_layout.count()
        # self._get_keys_list()

        diff = len(self.keys_list) - widgets_amount
        i = abs(diff)

        match diff:
            case x if x < 0:
                while i > 0:
                    item = self.browse_keys_list.scroll_content_layout.itemAt(widgets_amount - 1 - i)
                    widget = item.widget()
                    self.browse_keys_list.scroll_content_layout.removeWidget(widget)
                    widget.deleteLater()
                    i -= 1

            case x if x > 0:
                while i > 0:
                    key_widget = self._create_key_widget("")
                    self.browse_keys_list.scroll_content_layout.addWidget(key_widget)
                    i -= 1

        self._set_checked_keys()
        self._render_keys()

    def _init_ui(self) -> None:
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.org_label = QLabel(Text.org_label)
        self.inn_selection = QComboBox()
        self.layout.addWidget(self.org_label)
        self.layout.addWidget(self.inn_selection)

        self.browse_keys_label = QLabel(Text.browse_keys_label)

        self.refresh_keys_button = QPushButton(Text.refresh_keys_button)

        line_layout = QHBoxLayout()
        line_layout.addWidget(self.browse_keys_label)
        line_layout.addWidget(
            self.refresh_keys_button,
            alignment=Qt.AlignmentFlag.AlignRight
        )
        self.layout.addLayout(line_layout)

        self.browse_keys_list = KeyItemWidget(self)
        self.layout.addWidget(self.browse_keys_list)

        self.bind_key_button = QPushButton(Text.bind_key_button)
        self.layout.addWidget(self.bind_key_button)

    def _create_orgs_keys_cache(self) -> None:
        orgs_keys = manager.get_all_orgs_keys()
        orgs_keys_cache = {}

        for item in orgs_keys:
            orgs_keys_cache[
                item[Const.org_inn_index]] = [
                    key[Const.key_thumbprint_index]
                    for key in item[Const.key_list_index]
            ]
        self.orgs_keys_dict = orgs_keys_cache

    def _get_keys_list(self) -> None:
        win_csp_manager = WinCspManager()
        self.keys_list = win_csp_manager.certificates() + mock_csp.get_mock_keys()

    def _load_data(self):
        self._create_orgs_keys_cache()
        self._get_keys_list()

    def _create_key_widget(self, key: CspCertificate) -> QWidget:
        key_widget = QWidget()
        key_layout = QHBoxLayout(key_widget)
        key_layout.setContentsMargins(*Const.browse_keys_margins)

        checkbox = QCheckBox(parent=key_widget)
        checkbox.stateChanged.connect(lambda state: self._on_checkbox_checked(state, key))

        label = QLabel(str(key))
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        label.setWordWrap(True)

        key_layout.addWidget(checkbox)
        key_layout.addWidget(label, stretch=Const.browse_keys_key_layout_stretch)

        return key_widget

    def _render_keys_list(self) -> None:
        for key in self.keys_list:
            key_widget = self._create_key_widget(key)
            self.browse_keys_list.scroll_content_layout.addWidget(key_widget)

    def _fill_org_combobox(self) -> None:
        for org in self.org_list:
            org_str = data_manager.get_org_string(org)
            self.inn_selection.addItem(org_str)

    def _get_current_org_inn(self) -> str:
        index = self.inn_selection.currentIndex()
        if index == -1:
            selected_org_inn = self.org_list[0][Const.org_inn_index]
        else:
            org_info = self.inn_selection.itemText(index)
            selected_org_inn = data_manager.get_org_inn(org_info)
        return selected_org_inn

    def _get_checked_keys(self, selected_org_inn: str) -> None:
        checked_keys = self.orgs_keys_dict.get(selected_org_inn, {})
        self._checked_keys = {}
        self._unchecked_keys = {}

        for key in self.keys_list:
            if key.Thumbprint in checked_keys:
                self._checked_keys[key.Thumbprint] = key
            else:
                self._unchecked_keys[key.Thumbprint] = key

    def _set_checked_keys(self) -> None:
        selected_org_inn = self._get_current_org_inn()
        self._get_checked_keys(selected_org_inn)

    def _update_key_widget(self, index: int, key: CspCertificate, checked: bool = False) -> None:
        container_widget = self.browse_keys_list.scroll_content_layout.itemAt(index).widget()
        key_layout = container_widget.layout()
        label = key_layout.itemAt(Const.browse_keys_key_widget_label_index).widget()
        label.setText(str(key))

        checkbox = key_layout.itemAt(Const.browse_keys_key_widget_checkbox_index).widget()
        if checked:
            checkbox.setChecked(True)
        else:
            checkbox.setChecked(False)

        checkbox.stateChanged.disconnect()
        checkbox.stateChanged.connect(lambda state: self._on_checkbox_checked(state, key))

    def _render_keys(self) -> None:
        self._processing_update = True
        i = 0

        for key in self._checked_keys.values():
            self._update_key_widget(i, key, checked=True)
            i += 1

        for key in self._unchecked_keys.values():
            self._update_key_widget(i, key)
            i += 1

        self._processing_update = False

    def _fill_ui_with_data(self) -> None:
        self._fill_org_combobox()
        self._render_keys_list()
        self._set_checked_keys()
        self._render_keys()

    def _connect_buttons(self) -> None:
        self.inn_selection.currentIndexChanged.connect(self._on_org_selected)
        self.refresh_keys_button.clicked.connect(self._on_keys_refreshed)
        self.bind_key_button.clicked.connect(self.update_org_keys)

    def _on_updated_org_keys(self):
        self._render_keys()

        org_inn = self._get_current_org_inn()
        self.orgs_keys_dict[org_inn] = [
            thumbprint for thumbprint in self._checked_keys.keys()
        ]

    def update_org_keys(self) -> None:
        index = self.inn_selection.currentIndex()
        org_info = self.inn_selection.itemText(index)
        selected_org_inn = data_manager.get_org_inn(org_info)

        new_org_keys = [thumbprint for thumbprint in self._checked_keys.keys()]

        thread = UpdateOrgKeysThread(selected_org_inn, new_org_keys) #TODO: QMessageBox ??
        thread.signals.progress_popup.connect(
            lambda message: self.progress_dialog.update_progress(message=message)
        )
        thread.signals.finished.connect(self._on_updated_org_keys)
        thread.signals.finished_popup.connect(
            self.progress_dialog.update_finished
        )
        thread.signals.error_popup.connect(
            lambda error: self.progress_dialog.update_error(message=error)
        )
        self.threadpool.start(thread)

    def _add_org_to_list(self, new_org: Dict[str, str]) -> None:
        self.org_list.append(new_org)
        org_str = data_manager.get_org_string(new_org)
        self.inn_selection.addItem(org_str)

    def _delete_org_from_list(self, org_inn: str) -> None:
        item_count = self.inn_selection.count()
        for index in range(item_count):
            item_text = self.inn_selection.itemText(index)
            if item_text.startswith(org_inn):
                self.inn_selection.removeItem(index)

    def _update_org_in_list(self, to_update_info: Dict[str, str]) -> None:
        item_count = self.inn_selection.count()

        for index in range(item_count):
            item_text = self.inn_selection.itemText(index)
            if item_text.startswith(
                    to_update_info[Const.previous_org_index]
            ):
                self.inn_selection.setItemText(
                        index,
                        data_manager.get_org_string(to_update_info[Const.updated_org_index])
                   )

        org_keys = self.orgs_keys_dict[to_update_info[Const.previous_org_index]]
        del self.orgs_keys_dict[to_update_info[Const.previous_org_index]]
        self.orgs_keys_dict[to_update_info[Const.updated_org_index][Const.org_inn_index]] = org_keys