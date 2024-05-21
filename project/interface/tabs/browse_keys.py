from typing import Dict, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QMessageBox, QHBoxLayout,
    QScrollArea, QSizePolicy, QCheckBox
)
from PySide6.QtCore import QThreadPool, Qt
from project.interface.utils.threads import UpdateOrgKeysThread, GetOrgKeysThread
from project.interface.api_manager import manager
from project.interface.dialogs.popups import InfoPopup
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
        self.scroll_content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)


class BrowseKeysTab(QWidget):
    def __init__(self, org_list):
        super().__init__()

        self.org_list = org_list
        self.keys_list = None

        self.threadpool = QThreadPool()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.org_label = QLabel("Организация:")
        self.inn_selection = QComboBox()
        self.layout.addWidget(self.org_label)
        self.layout.addWidget(self.inn_selection)
        self.inn_selection.currentIndexChanged.connect(self._update_checked_keys)

        self.browse_keys_label = QLabel("Все ключи:")

        self.refresh_keys_button = QPushButton("Обновить список ключей")
        self.refresh_keys_button.clicked.connect(self._get_keys_list)

        line_layout = QHBoxLayout()
        line_layout.addWidget(self.browse_keys_label)
        line_layout.addWidget(self.refresh_keys_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addLayout(line_layout)

        self.browse_keys_list = KeyItemWidget(self)
        self.layout.addWidget(self.browse_keys_list)

        self.bind_key_button = QPushButton("Использовать ключи для организации")
        self.bind_key_button.clicked.connect(self.update_org_keys)
        self.layout.addWidget(self.bind_key_button)

        self._populate_org_combobox()
        self.inn_selection.currentIndexChanged.connect(lambda index: self._update_checked_keys(index))

        self.progress_popup = InfoPopup("Подождите, операция выполняется.", self)

    def _get_keys_list(self) -> None:
        win_csp_manager = WinCspManager()
        self.keys_list = win_csp_manager.certificates()
        self.keys_list += mock_csp.get_mock_keys()

    def _populate_keys_list(self):
        while self.browse_keys_list.scroll_content_layout.count():
            item = self.browse_keys_list.scroll_content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for key in self.keys_list:
            container_widget = QWidget()
            key_layout = QHBoxLayout(container_widget)
            key_layout.setContentsMargins(0, 0, 0, 0)

            checkbox = QCheckBox()

            label = QLabel(str(key))
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            label.setWordWrap(True)

            checkbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            checkbox.setFixedHeight(checkbox.sizeHint().height())

            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            label.setFixedHeight(label.sizeHint().height())

            key_layout.addWidget(checkbox)
            key_layout.addWidget(label, stretch=1)

            container_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            container_widget.setFixedHeight(label.sizeHint().height())

            self.browse_keys_list.scroll_content_layout.addWidget(container_widget)

    def _get_org_list(self) -> None:
        try:
            self.org_list = manager.get_org_list()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            self.org_list = []

    def _populate_org_combobox(self) -> None:
        for org in self.org_list:
            self.inn_selection.addItem(f"{org["inn"]} ({org["name"]})")

    def _add_org_to_list(self, new_org: Dict) -> None:
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

    def _update_org_in_list(self, org_info: List) -> None: #TODO: better typing
        item_count = self.inn_selection.count()
        for index in range(item_count):
            item_text = self.inn_selection.itemText(index)
            if item_text.startswith(org_info[0]["inn"]):
                self.inn_selection.setItemText(index, f"{org_info[1]["inn"]} ({org_info[1]["name"]})")

    def _on_update_checked_keys(self, keys):
        if not self.keys_list:
            self._get_keys_list()

        keys = [key['thumbprint'] for key in keys]
        checked_keys = [key for key in self.keys_list if key.Thumbprint in keys]
        unchecked_keys = [key for key in self.keys_list if key not in checked_keys]

        self.keys_list = checked_keys + unchecked_keys
        self._populate_keys_list()

        keys = [str(key) for key in checked_keys]

        for i in range(self.browse_keys_list.scroll_content_layout.count()):
            key_widget = self.browse_keys_list.scroll_content_layout.itemAt(i).widget()
            label = key_widget.layout().itemAt(1).widget()
            if label.text() in keys:
                checkbox = key_widget.layout().itemAt(0).widget()
                checkbox.setChecked(True)
            else:
                checkbox = key_widget.layout().itemAt(0).widget()
                checkbox.setChecked(False)

    def _update_checked_keys(self, index: int) -> None:
        if index == -1:
            selected_org_inn = self.org_list[0].inn
        else:
            org_info = self.inn_selection.itemText(index)
            selected_org_inn = org_info.split(' ')[0]

        thread = GetOrgKeysThread(selected_org_inn)
        thread.signals.result.connect(lambda keys: self._on_update_checked_keys(keys))
        thread.signals.error.connect(self._on_update_error)
        self.threadpool.start(thread)

    def _on_update_progress(self) -> None:
        self.progress_popup.show()

    def _on_update_finished(self) -> None:
        if self.progress_popup:
            self.progress_popup.close()
        QMessageBox.information(self, "Успешно", "Настройки успешно изменены.")

    def _on_update_error(self, message: str) -> None:
        if self.progress_popup:
            self.progress_popup.close()
        QMessageBox.warning(self, "Ошибка", message)

    def update_org_keys(self) -> None:
        checked_keys = []

        for i in range(self.browse_keys_list.scroll_content_layout.count()):
            key_widget = self.browse_keys_list.scroll_content_layout.itemAt(i).widget()
            checkbox = key_widget.layout().itemAt(0).widget()
            if checkbox.isChecked():
                checked_keys.append(self.keys_list[i])

        index = self.inn_selection.currentIndex()
        org_info = self.inn_selection.itemText(index)
        selected_org_inn = org_info.split(' ')[0]

        thread = UpdateOrgKeysThread(selected_org_inn, checked_keys)
        thread.signals.finished.connect(self._on_update_finished)
        thread.signals.error.connect(self._on_update_error)
        self.threadpool.start(thread)
        self._on_update_progress()

        self._on_update_checked_keys([{'thumbprint': key.Thumbprint} for key in checked_keys])