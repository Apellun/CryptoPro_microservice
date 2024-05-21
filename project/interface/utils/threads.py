from typing import Dict, List
from PySide6.QtCore import QRunnable, Signal, Slot, QObject
from project.interface.api_manager import manager


class UpdateServerSettingsSignals(QObject):
    finished = Signal()
    error = Signal(str)
    result = Signal(list)


class UpdateServerSettingsThread(QRunnable):
    def __init__(self, host: str, port: int):
        super(UpdateServerSettingsThread, self).__init__()
        self.host = host
        self.port = port
        self.signals = UpdateServerSettingsSignals()

    @Slot()
    def run(self) -> None:
        try:
            manager.update_server_settings(self.host, self.port)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))


class AddOrgThread(QRunnable):
    def __init__(self, org_inn: str, org_name: str):
        super(AddOrgThread, self).__init__()
        self.org_inn = org_inn
        self.org_name = org_name
        self.signals = UpdateServerSettingsSignals()

    @Slot()
    def run(self) -> None:
        try:
            manager.add_org(self.org_inn, self.org_name)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))


class UpdateOrgThread(QRunnable):
    def __init__(self, old_inn: str, new_org_details: Dict):
        super(UpdateOrgThread, self).__init__()
        self.old_inn = old_inn
        self.new_org_details = new_org_details
        self.signals = UpdateServerSettingsSignals()

    @Slot()
    def run(self) -> None:
        try:
            manager.update_org(self.old_inn, self.new_org_details)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))


class UpdateOrgKeysThread(QRunnable):
    def __init__(self, org_inn: str, keys: List[str]):
        super(UpdateOrgKeysThread, self).__init__()
        self.org_inn = org_inn
        self.keys = keys
        self.signals = UpdateServerSettingsSignals()

    @Slot()
    def run(self) -> None:
        try:
            manager.update_org_keys(self.org_inn, self.keys)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))


class DeleteOrgThread(QRunnable):
    def __init__(self, org_inn: str):
        super(DeleteOrgThread, self).__init__()
        self.org_inn = org_inn
        self.signals = UpdateServerSettingsSignals()

    @Slot()
    def run(self) -> None:
        try:
            manager.delete_org(self.org_inn)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))


class GetOrgKeysThread(QRunnable):
    def __init__(self, org_inn):
        super(GetOrgKeysThread, self).__init__()
        self.org_inn = org_inn
        self.signals = UpdateServerSettingsSignals()

    @Slot()
    def run(self):
        try:
            result = manager.get_org_keys(self.org_inn)
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))


class GetOrgListThread(QRunnable):
    def __init__(self):
        super(GetOrgListThread, self).__init__()
        self.signals = UpdateServerSettingsSignals()

    @Slot()
    def run(self):
        try:
            result = manager.get_org_list()
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))