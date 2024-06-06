import sys
from PySide6.QtWidgets import QApplication
from project.interface.main_window import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # try:
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
    # except Exception as e:
    #     error_popup = InfoPopup(f"Ошибка:\n{str(e)}")
    #     error_popup.show()
    #     sys.exit(1)
