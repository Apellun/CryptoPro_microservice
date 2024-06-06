from PySide6.QtWidgets import QMessageBox
from project.interface.dialogs.popups import InfoPopup
from project.interface.utils.text import MainText


class ProgressDialog(InfoPopup):
    def __init__(self, parent):
        super().__init__(parent)

    def show_finished_popup(
            self, message: str = MainText.success_message,
            title: str = MainText.success_title
    ) -> None:
        self.close()
        QMessageBox.information(self, title, message)

    def show_progress_popup(self, message: str = MainText.in_progress) -> None:
        self.set_text(message)
        self.show()

    def show_error_popup(
            self, message: str = MainText.error_message,
            title: str = MainText.error_title
    ) -> None:
        self.close()
        QMessageBox.warning(self, title, message)
