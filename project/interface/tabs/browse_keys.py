import numpy as np
from typing import Dict, List
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox,
    QListWidget, QPushButton, QMessageBox, QListWidgetItem,
    QCheckBox, QAbstractItemView
)
from PySide6.QtCore import QThreadPool
from project.interface.threads import AddOrgKeysThread, GetOrgKeysThread, DeleteOrgKeysThread
from project.interface.api_manager import manager
from project.utils.csp.win_csp import WinCspManager
from project.interface.utils.popups import InfoPopup
from project.api.load_mock_data import keys


class BrowseKeysTab(QWidget):
    def __init__(self):
        super().__init__()

        self.org_list = manager.get_org_list()

        self.threadpool = QThreadPool()

        # self.keys_list = self._get_keys_list() #TODO wincsp
        self.keys_list = keys
        self.key_checkboxes = None

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        #Left part

        self.left_layout = QVBoxLayout()

        self.org_label = QLabel("Организация:")
        self.inn_selection = QComboBox()
        self.left_layout.addWidget(self.org_label)
        self.left_layout.addWidget(self.inn_selection)

        self.key_list_label = QLabel("Привязанные ключи:")
        self.key_list = QListWidget()
        self.key_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.left_layout.addWidget(self.key_list_label)
        self.left_layout.addWidget(self.key_list)

        self.unbind_key_button = QPushButton("Отвязать ключи")
        self.unbind_key_button.clicked.connect(self.unbind_key_from_org)
        self.left_layout.addWidget(self.unbind_key_button)

        self.layout.addLayout(self.left_layout)

        #Right part

        self.right_layout = QVBoxLayout()

        self.browse_keys_label = QLabel("Все ключи:")
        self.browse_keys_list = QListWidget()
        self.right_layout.addWidget(self.browse_keys_label)
        self.right_layout.addWidget(self.browse_keys_list)

        self.bind_key_button = QPushButton("Привязать ключи")
        self.bind_key_button.clicked.connect(self.bind_key_to_org)
        self.right_layout.addWidget(self.bind_key_button)

        self.refresh_keys_button = QPushButton("Обновить список ключей")
        self.refresh_keys_button.clicked.connect(self._get_keys_list)
        self.right_layout.addWidget(self.refresh_keys_button)

        self.layout.addLayout(self.right_layout)

        self._populate_org_combobox()
        self._populate_all_keys_list()

        self.inn_selection.currentIndexChanged.connect(self._update_org_keys)
        self._update_org_keys(self.inn_selection.currentIndex())

        self.progress_popup = InfoPopup("Подождите, операция выполняется.", self)

    def _get_org_list(self) -> None:
        try:
            self.org_list = manager.get_org_list()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            self.org_list = []

    def _populate_org_combobox(self) -> None:
        for org in self.org_list:
            self.inn_selection.addItem(f"{org["inn"]} ({org["name"]})")

    def _populate_all_keys_list(self) -> None:
        for key in self.keys_list:
            item = QListWidgetItem()
            checkbox = QCheckBox()
            # key_str = f"{key.SubjectName}\n{key.ValidToDate}\n{key.IsValid()}"
            checkbox.setText(key)
            self.browse_keys_list.addItem(item)
            self.browse_keys_list.setItemWidget(item, checkbox)

            if self.key_checkboxes is None:
                self.key_checkboxes = []
            self.key_checkboxes.append(checkbox)

    def _update_keys_list(self, keys: List[Dict[str, str]]) -> None: #TODO: typehint
        self.key_list.clear()
        if keys:
            for key in keys:
                self.key_list.addItem(key["key"])

    def _update_org_list(self, new_org: Dict) -> None:
        self.org_list.append(new_org)
        self.inn_selection.addItem(f"{new_org[0]} ({new_org[1]})")

    def _update_org_keys(self, index: int) -> None:
        if index == -1:
            selected_org_inn = self.org_list[0].inn
        else:
            org_info = self.inn_selection.itemText(index)
            selected_org_inn = org_info.split(' ')[0]

        thread = GetOrgKeysThread(selected_org_inn)
        thread.signals.finished.connect(self._on_update_finished)
        thread.signals.result.connect(self._update_keys_list)
        thread.signals.error.connect(self._on_update_error)
        self.threadpool.start(thread)

    def _get_keys_list(self) -> List: #TODO typing
        win_csp_manager = WinCspManager()
        return win_csp_manager.certificates()

    def _on_update_progress(self) -> None:
        self.progress_popup.show()

    def _on_update_finished(self) -> None:
        QMessageBox.information(self, "Успешно", "Настройки успешно изменены.")

    def _on_update_error(self, message: str) -> None:
        if self.progress_popup:
            self.progress_popup.close()
        QMessageBox.warning(self, "Ошибка", message)

    def _on_add_org_keys(self, keys: List[str]) -> None:
        if self.progress_popup.isVisible():
            self.progress_popup.close()
        if keys:
            for key in keys:
                self.key_list.addItem(key)

    def _on_delete_org_keys(self, keys: List[str]) -> None:
        self.progress_popup.close()
        old_keys = [self.key_list.item(index).text() for index in range(self.key_list.count())]
        new_keys = np.setdiff1d(old_keys, keys)
        new_keys = new_keys.tolist()
        self.key_list.clear()
        if new_keys:
            for key in new_keys:
                self.key_list.addItem(key)

    def unbind_key_from_org(self) -> None:
        selected_keys = [item.text() for item in self.key_list.selectedItems()]
        if not selected_keys:
            QMessageBox.warning(self, "Ошибка", "Выберите ключ, который требуется отвязать.")
            return

        index = self.inn_selection.currentIndex()
        org_info = self.inn_selection.itemText(index)
        selected_org_inn = org_info.split(' ')[0]

        thread = DeleteOrgKeysThread(selected_org_inn, selected_keys)
        thread.signals.finished.connect(lambda: self._on_delete_org_keys(selected_keys))
        thread.signals.error.connect(self._on_update_error)
        self.threadpool.start(thread)
        self._on_update_progress()
        self._update_org_keys(self.inn_selection.currentIndex())

    def bind_key_to_org(self) -> None:
        checked_keys = []

        for checkbox in self.key_checkboxes:
            if checkbox.isChecked():
                checked_keys.append(checkbox.text())
        if not checked_keys:
            QMessageBox.warning(self, "Ошибка", "Выберите ключи для привязки.")
            return

        index = self.inn_selection.currentIndex()
        org_info = self.inn_selection.itemText(index)
        selected_org_inn = org_info.split(' ')[0]

        thread = AddOrgKeysThread(selected_org_inn, checked_keys)
        thread.signals.finished.connect(lambda: self._on_add_org_keys(checked_keys))
        thread.signals.error.connect(self._on_update_error)
        self.threadpool.start(thread)
        self._on_update_progress()
        self._update_org_keys(self.inn_selection.currentIndex())