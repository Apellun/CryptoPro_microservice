from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox


class KeyItemWidget(QWidget):
    def __init__(self, key):
        super().__init__()
        layout = QVBoxLayout()

        self.checkbox = QCheckBox()
        self.label = QLabel()

        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)

        self.setLayout(layout)

        self.set_key(key)

    def set_key(self, key):
        key_str = f"{key.SubjectName}\n{key.ValidToDate}\n{key.IsValid()}"
        self.label.setText(key_str)