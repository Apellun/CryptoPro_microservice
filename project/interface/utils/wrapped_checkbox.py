from PySide6.QtWidgets import QWidget, QHBoxLayout, QCheckBox, QLabel


class WrappedCheckBox(QWidget):
    def __init__(self, text='', parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.checkbox = QCheckBox()
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)