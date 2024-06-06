from typing import List
from PySide6.QtCore import QThreadPool, Signal, QObject
from PySide6.QtWidgets import QWidget, QDialog
from project.interface.core.threads import threads


class ThreadManager(QObject):
    org_added = Signal(str, str)
    org_updated = Signal(str, str, str, QWidget)
    org_deleted = Signal(str, QWidget)
    org_keys_updated = Signal()

    def __init__(self):
        super().__init__()

        self.threadpool = QThreadPool()
        self.progress_dialog = None

        self.add_org_inn = None
        self.add_org_name = None

        self.update_org_old_inn = None
        self.update_org_inn = None
        self.update_org_name = None
        self.update_org_widget = None

        self.delete_org_inn = None
        self.delete_org_widget = None

    def set_progress_dialog(self, progress_dialog: QDialog) -> None:
        self.progress_dialog = progress_dialog

    def _on_org_added(self) -> None:
        self.org_added.emit(self.add_org_name, self.add_org_inn)
        self.progress_dialog.show_finished_popup()

    def run_add_org_thread(self, org_inn: str, org_name: str) -> None:
        self.add_org_name = org_name
        self.add_org_inn = org_inn

        thread = threads.AddOrgThread(org_inn, org_name)
        thread.signals.finished.connect(self._on_org_added)
        thread.signals.error.connect(self.progress_dialog.show_error_popup)

        self.threadpool.start(thread)
        self.progress_dialog.show_progress_popup()

    def _on_org_updated(self) -> None:
        self.org_updated.emit(
            self.update_org_old_inn, self.update_org_inn,
            self.update_org_name, self.update_org_widget
        )
        self.progress_dialog.show_finished_popup()

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
        self.threadpool.start(thread)
        self.progress_dialog.show_progress_popup()

    def _on_org_deleted(self):
        self.org_deleted.emit(self.delete_org_inn, self.delete_org_widget)
        self.progress_dialog.show_finished_popup()

    def run_delete_org_thread(self, org_inn: str, org_widget: QWidget) -> None:
        self.delete_org_inn = org_inn
        self.delete_org_widget = org_widget

        thread = threads.DeleteOrgThread(org_inn)

        thread.signals.finished.connect(self._on_org_deleted)
        self.threadpool.start(thread)
        self.progress_dialog.show_progress_popup()

    def _on_org_keys_updated(self):
        self.org_keys_updated.emit()
        self.progress_dialog.show_finished_popup()

    def run_update_org_keys_thread(
            self, org_inn: str, new_keys: List[str]) -> None:
        thread = threads.UpdateOrgKeysThread(org_inn, new_keys)
        thread.signals.finished.connect(self._on_org_keys_updated)

        self.threadpool.start(thread)
        self.progress_dialog.show_progress_popup()

    def _on_server_settings_updated(self):
        self.progress_dialog.show_finished_popup()

    def run_update_server_settings_thread(
            self, host: str, port: str) -> None:
        thread = threads.UpdateServerSettingsThread(
            host=host,
            port=port
        )
        thread.signals.finished.connect(self._on_server_settings_updated)
        self.threadpool.start(thread)
        self.progress_dialog.show_progress_popup()


thread_manager = ThreadManager()