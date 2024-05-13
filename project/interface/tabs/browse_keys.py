from typing import Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QMessageBox, QHBoxLayout,
    QScrollArea, QSizePolicy, QCheckBox, QLayout
)
from PySide6.QtCore import QThreadPool, Qt
from project.interface.threads import UpdateOrgKeysThread, GetOrgKeysThread
from project.interface.api_manager import manager
from project.interface.utils.popups import InfoPopup
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
        self.scroll_content_layout.addStretch(1)

        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)


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
            key_widget = QWidget()
            key_layout = QHBoxLayout()
            key_layout.setContentsMargins(1, 1, 1, 1)
            key_layout.setStretch(0, 0)

            checkbox = QCheckBox()
            key_layout.addWidget(checkbox)

            label = QLabel()
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            label.setWordWrap(True)
            label.setText(str(key))

            key_layout.addWidget(label, stretch=1)

            key_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            key_widget.setLayout(key_layout)
            self.browse_keys_list.scroll_content_layout.addWidget(key_widget)

    def _get_org_list(self) -> None:
        try:
            self.org_list = manager.get_org_list()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            self.org_list = []

    def _populate_org_combobox(self) -> None:
        for org in self.org_list:
            self.inn_selection.addItem(f"{org["inn"]} ({org["name"]})")

    def _update_org_list(self, new_org: Dict) -> None:
        self.org_list.append(new_org)
        org_str = f"{new_org['org_inn']}"
        if new_org['org_name']:
            org_str += f" ({new_org['org_name']})"
        self.inn_selection.addItem(f"{new_org['org_inn']}")

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