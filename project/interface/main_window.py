from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget
from project.interface import config
from project.interface.core.threads.thread_manager import thread_manager
from project.interface.core.api_manager import api_manager
from project.interface.dialogs.progress_dialog import ProgressDialog
from project.interface.tabs.browse_keys import BrowseKeysTab
from project.interface.tabs.configure_server import ConfigureServerTab
from project.interface.tabs.org_list import OrgListTab
from project.interface.utils.text import MainText


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.org_list = api_manager.get_orgs_list()

        self._init_ui()
        self._add_tabs()
        self.progress_dialog = ProgressDialog(self)
        thread_manager.set_progress_dialog(self.progress_dialog)

        self._connect_signals()

    def _init_ui(self) -> None:
        self.setWindowTitle(MainText.main_window_title)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setMinimumHeight(config.MAIN_WINDOW_HEIGHT)
        self.setMinimumWidth(config.MAIN_WINDOW_WIDTH)

        screen_geometry = QApplication.primaryScreen().geometry()
        center_point = screen_geometry.center()
        self.move(center_point - self.rect().center())

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

    def _add_tabs(self) -> None:
        self.server_settings_tab = ConfigureServerTab(self)
        self.browse_keys_tab = BrowseKeysTab(self)
        self.org_list_tab = OrgListTab(self)

        self.tabs.addTab(self.browse_keys_tab, MainText.browse_keys_tab_title)
        self.tabs.addTab(self.org_list_tab, MainText.org_list_tab_title)
        self.tabs.addTab(self.server_settings_tab, MainText.server_details_tab_title)

    def _connect_signals(self) -> None:
        thread_manager.org_added.connect(self.org_list_tab.on_org_added)
        thread_manager.org_added.connect(self.browse_keys_tab.on_org_added)

        thread_manager.org_updated.connect(self.org_list_tab.on_org_updated)
        thread_manager.org_updated.connect(self.browse_keys_tab.on_org_updated)

        thread_manager.org_deleted.connect(self.org_list_tab.on_org_deleted)
        thread_manager.org_deleted.connect(self.browse_keys_tab.on_org_deleted)

        thread_manager.org_keys_updated.connect(self.browse_keys_tab.on_updated_org_keys)