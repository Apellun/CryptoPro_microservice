from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget
from project.interface.tabs.browse_keys import BrowseKeysTab
from project.interface.tabs.configure_server import ConfigureServerTab
from project.interface.tabs.org_list import OrgListTab
from project.interface.api_manager import manager
from project.interface.utils.const import Const
from project.interface.utils.text import MainText


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self._init_ui()
        self._add_tabs()
        self._connect_signals()

    def _init_ui(self) -> None:
        self.setWindowTitle(MainText.main_window_title)
        self.setGeometry(*Const.main_window_geometry)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.setMinimumHeight(Const.main_window_min_height)
        screen_geometry = QApplication.primaryScreen().geometry()
        center_point = screen_geometry.center()

        self.move(center_point - self.rect().center())

    def _add_tabs(self) -> None:
        self.server_details_tab = ConfigureServerTab()

        org_list = manager.get_org_list() #TODO: separate?

        self.browse_keys_tab = BrowseKeysTab(org_list)
        self.org_list_tab = OrgListTab(org_list)

        self.tabs.addTab(self.browse_keys_tab, MainText.browse_keys_tab_title)
        self.tabs.addTab(self.org_list_tab, MainText.org_list_tab_title)
        self.tabs.addTab(self.server_details_tab, MainText.server_details_tab_title)

    def _connect_signals(self) -> None:
        self.org_list_tab.add_org_widget.org_added.connect(self.browse_keys_tab._add_org_to_list)
        self.org_list_tab.org_updated.connect(
            lambda to_update_info: self.browse_keys_tab._update_org_in_list(to_update_info))
        self.org_list_tab.org_deleted.connect(lambda org_inn: self.browse_keys_tab._delete_org_from_list(org_inn))
