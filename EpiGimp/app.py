import sys
from PySide6.QtWidgets import QApplication
from EpiGimp.ui.windows.main_window import MainWindow

def run_app(argv=None):
    argv = argv or sys.argv
    app = QApplication(argv)
    window = MainWindow()
    window.show()
    return app.exec()
