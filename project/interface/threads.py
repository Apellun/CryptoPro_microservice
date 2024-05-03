from PySide6.QtCore import QRunnable, Signal, Slot, QObject
from project.interface.api_manager import manager


class UpdateServerSettingsSignals(QObject):
    finished = Signal()
    error = Signal(str)
    result = Signal(list)


class UpdateServerSettingsThread(QRunnable):
    finished = Signal(int)

    def __init__(self, host, port):
        super(UpdateServerSettingsThread, self).__init__()
        self.host = host
        self.port = port
        self.signals = UpdateServerSettingsSignals()

    @Slot()
    def run(self):
        try:
            manager.update_server_settings(self.host, self.port)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))


class AddOrgThread(QRunnable):
    finished = Signal(int)

    def __init__(self, org_inn, org_name):
        super(AddOrgThread, self).__init__()
        self.org_inn = org_inn
        self.org_name = org_name
        self.signals = UpdateServerSettingsSignals()

    @Slot()
    def run(self):
        try:
            manager.add_org(self.org_inn, self.org_name)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))


class AddOrgKeysThread(QRunnable):
    finished = Signal(int)

    def __init__(self, org_inn, keys):
        super(AddOrgKeysThread, self).__init__()
        self.org_inn = org_inn
        self.keys = keys
        self.signals = UpdateServerSettingsSignals()

    @Slot()
    def run(self):
        try:
            manager.add_org_keys(self.org_inn, self.keys)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))


class DeleteOrgKeysThread(QRunnable):
    finished = Signal(int)

    def __init__(self, org_inn, keys):
        super(DeleteOrgKeysThread, self).__init__()
        self.org_inn = org_inn
        self.keys = keys
        self.signals = UpdateServerSettingsSignals()

    @Slot()
    def run(self):
        try:
            manager.delete_org_keys(self.org_inn, self.keys)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))


class GetOrgKeysThread(QRunnable):
    finished = Signal(int)

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
    finished = Signal(int)

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