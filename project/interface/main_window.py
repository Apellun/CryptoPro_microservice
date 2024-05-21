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
        self.browse_keys_tab = BrowseKeysTab(org_list)
        self.org_list_tab = OrgListTab(self, org_list)

        self.tabs.addTab(self.browse_keys_tab, "Доступные ключи")
        self.tabs.addTab(self.org_list_tab, "Список организаций")
        self.tabs.addTab(self.server_details_tab, "Настройки сервера")

        self.org_list_tab.add_org_widget.org_added.connect(self.browse_keys_tab._add_org_to_list)
        self.org_list_tab.add_org_widget.org_added.connect(self.org_list_tab._on_finished_update)

        self.org_list_tab.org_updated.connect(lambda org_info: self.browse_keys_tab._update_org_in_list(org_info))
        self.org_list_tab.org_deleted.connect(lambda org_inn: self.browse_keys_tab._delete_org_from_list(org_inn))

        self.setMinimumHeight(600)
        screen_geometry = QApplication.primaryScreen().geometry()
        center_point = screen_geometry.center()

        self.move(center_point - self.rect().center())
