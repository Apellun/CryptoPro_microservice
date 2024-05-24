from typing import Dict, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QHBoxLayout, QScrollArea,
    QSizePolicy, QCheckBox
)
from PySide6.QtCore import QThreadPool, Qt
from project.interface.utils.threads import UpdateOrgKeysThread, GetOrgKeysThread
from project.interface.dialogs.progress_dialog import ProgressDialog
from project.utils.csp.win_csp import WinCspManager
from project.interface.utils import mock_csp


class KeyItemWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_content = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content_layout.setSpacing(15)
        self.scroll_content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)


class BrowseKeysTab(QWidget):
    def __init__(self, org_list):
        super().__init__()

        self.org_list = org_list
        self.keys = None #immutable, objects
        self._checked_keys = None #mutable, string reprs
        self._unchecked_keys = None #mutable, string reprs

        self.threadpool = QThreadPool()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.org_label = QLabel("Организация:")
        self.inn_selection = QComboBox()
        self.layout.addWidget(self.org_label)
        self.layout.addWidget(self.inn_selection)
        self.inn_selection.currentIndexChanged.connect(self._set_checked_keys)

        self.browse_keys_label = QLabel("Все ключи:")

        self.refresh_keys_button = QPushButton("Обновить список ключей")
        self.refresh_keys_button.clicked.connect(self._set_checked_keys)

        line_layout = QHBoxLayout()
        line_layout.addWidget(self.browse_keys_label)
        line_layout.addWidget(self.refresh_keys_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addLayout(line_layout)

        self.browse_keys_list = KeyItemWidget(self)
        self.layout.addWidget(self.browse_keys_list)

        self.bind_key_button = QPushButton("Использовать ключи для организации")
        self.bind_key_button.clicked.connect(self.update_org_keys)
        self.layout.addWidget(self.bind_key_button)

        self.progress_dialog = ProgressDialog(self)

        self._processing_update = False

        self._get_keys_list()
        self._render_keys_list()
        self._fill_org_combobox()
        self._set_checked_keys()

    def _get_keys_list(self) -> None:
        win_csp_manager = WinCspManager()
        self.keys_list = win_csp_manager.certificates() + mock_csp.get_mock_keys()

    def _on_checkbox_checked(self, state: int, key_str: str) -> None:
        if not self._processing_update:
            if state == 2:
                self._checked_keys.append(key_str)
                try:
                    self._unchecked_keys.remove(key_str)
                except ValueError:
                    pass
            elif state == 0:
                self._unchecked_keys.append(key_str)
                try:
                    self._checked_keys.remove(key_str)
                except ValueError:
                    pass

    def _create_key_widget(self, key_str: str) -> QWidget:
        key_widget = QWidget()
        key_layout = QHBoxLayout(key_widget)
        key_layout.setContentsMargins(0, 0, 0, 0)

        checkbox = QCheckBox(parent=key_widget)
        checkbox.stateChanged.connect(lambda state: self._on_checkbox_checked(state, label.text()))

        label = QLabel(key_str)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        label.setWordWrap(True)

        key_layout.addWidget(checkbox)
        key_layout.addWidget(label, stretch=1)

        return key_widget

    def _render_keys_list(self) -> None:
        for key in self.keys_list:
            key_widget = self._create_key_widget(str(key))
            self.browse_keys_list.scroll_content_layout.addWidget(key_widget)

    def _fill_org_combobox(self) -> None:
        for org in self.org_list:
            self.inn_selection.addItem(f"{org["inn"]} ({org["name"]})")

    def _get_current_org_inn(self) -> str:
        index = self.inn_selection.currentIndex()
        if index == -1:
            selected_org_inn = self.org_list[0]["inn"]
        else:
            org_info = self.inn_selection.itemText(index)
            selected_org_inn = org_info.split(' ')[0]
        return selected_org_inn

    def _sort_org_keys(self, keys: List[Dict]) -> None:
        thumbprints = [key["thumbprint"] for key in keys]
        thumbprints = [str(key) for key in self.keys_list if key.Thumbprint in thumbprints]

        self._checked_keys = []
        self._unchecked_keys = []

        for key in self.keys_list:
            if str(key) in thumbprints:
                self._checked_keys.append(str(key))
            else:
                self._unchecked_keys.append(str(key))

    def _render_checked_keys(self, keys: List[Dict]) -> None:
        self._sort_org_keys(keys)
        self._update_checked_keys() #TODO: signal?

    def _set_checked_keys(self) -> None:
        selected_org_inn = self._get_current_org_inn()

        thread = GetOrgKeysThread(selected_org_inn)
        thread.signals.error_popup.connect(lambda error: self.progress_dialog.update_error(message=error))
        thread.signals.result.connect(lambda keys: self._render_checked_keys(keys))
        self.threadpool.start(thread)

    def _update_key_widget(self, index: int, key: str, checked: bool = False) -> None:
        container_widget = self.browse_keys_list.scroll_content_layout.itemAt(index).widget()
        key_layout = container_widget.layout()
        label = key_layout.itemAt(1).widget()
        label.setText(key)

        checkbox = key_layout.itemAt(0).widget()
        if checked:
            checkbox.setChecked(True)
        else:
            checkbox.setChecked(False)

    def _update_checked_keys(self) -> None:
        self._processing_update = True

        keys = sorted(self._checked_keys) + sorted(self._unchecked_keys)
        checked_amount = len(self._checked_keys)

        for i in range(self.browse_keys_list.scroll_content_layout.count()):
            if i < checked_amount:
                self._update_key_widget(i, keys[i], checked=True)
            else:
                self._update_key_widget(i, keys[i])

        self._processing_update = False

    def _get_keys_to_update(self) -> List[str]:
        keys = []
        for key in self.keys_list:
            if str(key) in self._checked_keys:
                keys.append(key.Thumbprint)
        return keys

    def update_org_keys(self) -> None:
        index = self.inn_selection.currentIndex()
        org_info = self.inn_selection.itemText(index)
        selected_org_inn = org_info.split(' ')[0]

        new_org_keys = self._get_keys_to_update()

        thread = UpdateOrgKeysThread(selected_org_inn, new_org_keys) #TODO: QMessageBox ??
        thread.signals.progress_popup.connect(lambda message: self.progress_dialog.update_progress(message=message))
        thread.signals.finished.connect(self._update_checked_keys)
        thread.signals.finished_popup.connect(lambda message: self.progress_dialog.update_finished(message=message))
        thread.signals.error_popup.connect(lambda error: self.progress_dialog.update_error(message=error))
        self.threadpool.start(thread)

    def _add_org_to_list(self, new_org: Dict[str, str]) -> None:
        self.org_list.append(new_org)
        org_str = f"{new_org['inn']}"
        if new_org['name']:
            org_str += f" ({new_org['name']})"
        self.inn_selection.addItem(org_str)

    def _delete_org_from_list(self, org_inn: str) -> None:
        item_count = self.inn_selection.count()
        for index in range(item_count):
            item_text = self.inn_selection.itemText(index)
            if item_text.startswith(org_inn):
                self.inn_selection.removeItem(index)

    def _update_org_in_list(self, org_info: tuple[Dict[str, str], Dict[str, str]]) -> None:
        item_count = self.inn_selection.count()
        for index in range(item_count):
            item_text = self.inn_selection.itemText(index)
            if item_text.startswith(org_info[0]["inn"]):
                self.inn_selection.setItemText(index, f"{org_info[1]["inn"]} ({org_info[1]["name"]})")