from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget
from project.interface.tabs.browse_keys import BrowseKeysTab
from project.interface.tabs.configure_server import ConfigureServerTab
from project.interface.tabs.org_list import OrgListTab
from project.interface.api_manager import manager


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Привязка ключей к ИНН')
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        org_list = manager.get_org_list()

        self.server_details_tab = ConfigureServerTab()
        self.org_list_tab = OrgListTab(org_list)
        self.browse_keys_tab = BrowseKeysTab(org_list)

        self.tabs.addTab(self.browse_keys_tab, "Доступные ключи")
        self.tabs.addTab(self.server_details_tab, "Настройки сервера")
        self.tabs.addTab(self.org_list_tab, "Добавить организацию")

        self.org_list_tab.org_added.connect(self.browse_keys_tab._update_org_list)

        self.setMinimumHeight(600)
        screen_geometry = QApplication.primaryScreen().geometry()
        center_point = screen_geometry.center()

        self.move(center_point - self.rect().center())
