from PySide6.QtWidgets import QMessageBox, QWidget
from project.interface.dialogs.popups import InfoPopup


class ProgressDialog(InfoPopup):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent=parent, text="Подождите, настройки сохраняются.")
        self.parent = parent

    def update_finished(self, title: str = "Успешно", message: str = None) -> None:
        if self.isVisible():
            self.close()
        QMessageBox.information(self, title, message)

    def update_progress(self, message: str) -> None:
        super().set_text(message)
        self.show()

    def update_error(self, title: str = "Ошибка", message: str = None) -> None:
        if self.isVisible():
            self.close()
        QMessageBox.warning(self, title, message)
