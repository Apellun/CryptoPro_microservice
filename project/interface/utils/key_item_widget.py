from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel,
    QCheckBox, QSizePolicy, QScrollArea,
    QVBoxLayout
)
from PySide6.QtCore import Qt
from project.utils.csp.win_csp import WinCspManager
from PySide6.QtWidgets import QApplication
from project.interface.utils import mock_csp


class KeyItemWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_content = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)

        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self._get_keys_list()
        self._set_keys()

    def _get_keys_list(self): #TODO typing
        win_csp_manager = WinCspManager()
        self.keys_list = win_csp_manager.certificates()
        self.keys_list += mock_csp.get_mock_keys()

    def _set_keys(self):
        for key in self.keys_list:
            key_widget = QWidget()
            key_layout = QHBoxLayout()

            checkbox = QCheckBox()
            key_layout.addWidget(checkbox)

            label = QLabel()
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            label.setWordWrap(True)
            label.setText(str(key))

            key_layout.addWidget(label, stretch=1)

            key_widget.setLayout(key_layout)
            self.scroll_content_layout.addWidget(key_widget)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    widget = KeyItemWidget()
    widget.show()
    sys.exit(app.exec())