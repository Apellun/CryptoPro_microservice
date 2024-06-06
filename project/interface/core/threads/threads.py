import time
from typing import List
from PySide6.QtCore import QRunnable, Signal, Slot, QObject
from project.interface.core.api_manager import api_manager


class BaseSignals(QObject):
    started = Signal()
    finished = Signal()
    error = Signal(str)


class AddOrgThread(QRunnable):
    def __init__(self, org_inn: str, org_name: str):
        super(AddOrgThread, self).__init__()
        self.org_inn = org_inn
        self.org_name = org_name
        self.signals = BaseSignals()

    @Slot()
    def run(self) -> None:
        try:
            api_manager.add_org(self.org_inn, self.org_name)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))


class UpdateOrgThread(QRunnable):
    def __init__(self, old_inn: str, new_inn: str, new_name: str):
        super(UpdateOrgThread, self).__init__()
        self.signals = BaseSignals()

        self.old_inn = old_inn
        self.new_inn = new_inn
        self.new_name = new_name

    @Slot()
    def run(self) -> None:
        try:
            api_manager.update_org(
                old_inn=self.old_inn,
                new_inn=self.new_inn,
                new_name=self.new_name
            )
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))


class DeleteOrgThread(QRunnable):
    def __init__(self, org_inn: str):
        super(DeleteOrgThread, self).__init__()
        self.org_inn = org_inn
        self.signals = BaseSignals()

    @Slot()
    def run(self) -> None:
        try:
            # self.signals.progress_popup.emit(MainText.in_progress)
            api_manager.delete_org(self.org_inn)

            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))


class UpdateOrgKeysThread(QRunnable):
    def __init__(self, org_inn: str, new_keys: List[str]):
        super(UpdateOrgKeysThread, self).__init__()
        self.signals = BaseSignals()

        self.org_inn = org_inn
        self.new_keys = new_keys

    @Slot()
    def run(self) -> None:
        try:
            api_manager.update_org_keys(
                org_inn=self.org_inn,
                new_keys=self.new_keys
            )
            self.signals.finished.emit()

        except Exception as error:
            self.signals.error.emit(str(error))


class UpdateServerSettingsThread(QRunnable):
    def __init__(self, host: str, port: str):
        super(UpdateServerSettingsThread, self).__init__()
        self.host = host
        self.port = port
        self.signals = BaseSignals()

    @Slot()
    def run(self) -> None:
        try:
            api_manager.update_server_settings(
                host=self.host,
                port=self.port
            )
            self.signals.finished.emit()

        except Exception as error:
            self.signals.error.emit(str(error))