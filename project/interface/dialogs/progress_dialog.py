from PySide6.QtWidgets import QMessageBox, QWidget
from project.interface.dialogs.popups import InfoPopup
from project.interface.utils.text import MainText


class ProgressDialog(InfoPopup):
    def __init__(self, parent: QWidget = None):
        super().__init__(
            parent=parent,
            text=MainText.in_progress
        )
        self.parent = parent

    def update_finished(
            self, message: str = None
    ) -> None:
        self.close()
        QMessageBox.information(self, text = message)

    def update_progress(self, message: str) -> None:
        super().set_text(message)
        self.show()

    def update_error(
            self, message: str = None,
            title: str = MainText.error_title,
    ) -> None:
        self.close()
        QMessageBox.warning(self, title, message)
