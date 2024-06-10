from typing import List
from PySide6.QtCore import QThreadPool, Signal, QObject
from PySide6.QtWidgets import QWidget, QMessageBox
from project.interface.core.threads import threads
from project.interface.utils.text import MainText


class ThreadManager(QObject):
    org_added = Signal(str, str)
    org_updated = Signal(str, str, str, QWidget)
    org_deleted = Signal(str, QWidget)
    org_keys_updated = Signal()

    def __init__(self):
        super().__init__()

        self.threadpool = QThreadPool()

        self.infobox = None
        self.successbox = None
        self.errorbox = None

        self.add_org_inn = None
        self.add_org_name = None

        self.update_org_old_inn = None
        self.update_org_inn = None
        self.update_org_name = None
        self.update_org_widget = None

        self.delete_org_inn = None
        self.delete_org_widget = None

    def _display_infobox(
            self, title: str = MainText.in_progress_title,
            message: str = MainText.in_progress_message
    ) -> None:
        self.infobox = QMessageBox()
        self.infobox.setWindowTitle(title)
        self.infobox.setStandardButtons(QMessageBox.NoButton)
        self.infobox.setText(message)
        self.infobox.exec()

    def _display_successbox(
            self, title: str = MainText.success_title,
            message: str = MainText.success_message):
        self.infobox.accept()
        self.successbox = QMessageBox()
        self.successbox.setWindowTitle(title)
        self.successbox.setText(message)
        self.successbox.exec()

    def _display_errorbox(
            self, error_str: str, title: str = MainText.error_title
    ) -> None:
        self.infobox.accept()
        self.errorbox = QMessageBox()
        self.errorbox.setWindowTitle(title)
        self.errorbox.setText(error_str)
        self.errorbox.exec()

    def _on_org_added(self) -> None:
        self.org_added.emit(self.add_org_name, self.add_org_inn)
        self._display_successbox()

    def run_add_org_thread(self, org_inn: str, org_name: str) -> None:
        self.add_org_name = org_name
        self.add_org_inn = org_inn

        thread = threads.AddOrgThread(org_inn, org_name)
        thread.signals.finished.connect(self._on_org_added)
        thread.signals.error.connect(self._display_errorbox)

        self.threadpool.start(thread)
        self._display_infobox()

    def _on_org_updated(self) -> None:
        self.org_updated.emit(
            self.update_org_old_inn, self.update_org_inn,
            self.update_org_name, self.update_org_widget
        )
        self._display_successbox()

    def run_update_org_thread(
            self, old_inn: str, org_inn: str, org_name: str, org_widget: QWidget
    ) -> None:
        self.update_org_old_inn = old_inn
        self.update_org_inn = org_inn
        self.update_org_name = org_name
        self.update_org_widget = org_widget

        thread = threads.UpdateOrgThread(
            old_inn=old_inn,
            new_inn=org_inn,
            new_name=org_name
        )
        thread.signals.finished.connect(self._on_org_updated)
        thread.signals.error.connect(self._display_errorbox)

        self.threadpool.start(thread)
        self._display_infobox()

    def _on_org_deleted(self):
        self.org_deleted.emit(self.delete_org_inn, self.delete_org_widget)
        self._display_successbox()

    def run_delete_org_thread(self, org_inn: str, org_widget: QWidget) -> None:
        self.delete_org_inn = org_inn
        self.delete_org_widget = org_widget

        thread = threads.DeleteOrgThread(org_inn)

        thread.signals.finished.connect(self._on_org_deleted)
        thread.signals.error.connect(self._display_errorbox)

        self.threadpool.start(thread)
        self._display_infobox()

    def _on_org_keys_updated(self):
        self.org_keys_updated.emit()
        self._display_successbox()

    def run_update_org_keys_thread(
            self, org_inn: str, new_keys: List[str]) -> None:
        thread = threads.UpdateOrgKeysThread(org_inn, new_keys)
        thread.signals.finished.connect(self._on_org_keys_updated)
        thread.signals.error.connect(self._display_errorbox)

        self.threadpool.start(thread)
        self._display_infobox()

    def _on_server_settings_updated(self):
        self._display_successbox()

    def run_update_server_settings_thread(
            self, host: str, port: str) -> None:
        thread = threads.UpdateServerSettingsThread(
            host=host,
            port=port
        )
        thread.signals.finished.connect(self._on_server_settings_updated)
        thread.signals.error.connect(self._display_errorbox)

        self.threadpool.start(thread)
        self._display_infobox()


thread_manager = ThreadManager()