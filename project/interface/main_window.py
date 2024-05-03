from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from project.interface.tabs.browse_keys import BrowseKeysTab
from project.interface.tabs.configure_server import ConfigureServerTab
from project.interface.tabs.add_org import AddOrgTab
from project.interface.threads import AddOrgThread


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Привязка ключей к ИНН')
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.server_details_tab = ConfigureServerTab()
        self.add_org_tab = AddOrgTab()
        self.browse_keys_tab = BrowseKeysTab()

        self.tabs.addTab(self.browse_keys_tab, "ИНН и ключи")
        self.tabs.addTab(self.server_details_tab, "Настройки сервера")
        self.tabs.addTab(self.add_org_tab, "Добавить ИНН")

        self.add_org_tab.org_added.connect(self.browse_keys_tab._update_org_list)
