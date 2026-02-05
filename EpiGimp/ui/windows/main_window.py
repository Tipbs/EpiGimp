from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QFileDialog, QMainWindow, QVBoxLayout, QWidget, QStatusBar
from EpiGimp.ui.widgets.canvas_widgets import CanvasWidget
from EpiGimp.ui.widgets.export_widget import ExportWidget
from EpiGimp.config.settings import load_settings

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = load_settings()
        self.setWindowTitle('EpiGimp - prototype')
        w = QWidget()
        self.setCentralWidget(w)
        layout = QVBoxLayout(w)


        self.canvas = CanvasWidget()
        layout.addWidget(self.canvas)
        # self.canvas._drawButton = QPushButton("Draw", self)
        # self.canvas._drawButton.move(10, 10)
        # self.canvas._drawButton.clicked.connect(self.canvas._toggle_drawing_mode)
        vlayout = QVBoxLayout()
        layout.addLayout(vlayout)
        # vlayout.addWidget(self.canvas._drawButton, 0)

        # self.circle_btn = QPushButton("Circle Tool")
        # self.circle_btn.setCheckable(True)  
        # vlayout.addWidget(self.circle_btn, 2)
        # self.circle_btn.toggled.connect(self.toggle_circle_mode)
        #
        # self.select_btn = QPushButton("Select Tool")
        # vlayout.addWidget(self.select_btn, 3)
        # self.select_btn.clicked.connect(self.canvas.enable_selection_mode)

        self._create_actions()
        self._create_menus()
        self.setStatusBar(QStatusBar(self))


        self.resize(self.settings.get('window', {}).get('width', 1200),
        self.settings.get('window', {}).get('height', 800))


    def _create_actions(self):
        self.open_act = QAction('Open File in Project...', self)
        self.open_act.setShortcut(QKeySequence('Ctrl+O'))
        self.open_act.triggered.connect(lambda: self.open_file(type=0))

        self.open_new_act = QAction('Open File in New Canva...', self)
        self.open_new_act.setShortcut(QKeySequence('Ctrl+Shift+O'))
        self.open_new_act.triggered.connect(lambda: self.open_file(type=1))
        
        self.load_act = QAction('Load Project...', self)
        self.load_act.setShortcut(QKeySequence('Ctrl+L'))
        self.load_act.triggered.connect(self.load_project)

        self.save_act = QAction('Save As...', self)
        self.save_act.setShortcut(QKeySequence('Ctrl+S'))
        self.save_act.triggered.connect(self.save_file)
        
        self.export_act = QAction('Export...', self)
        self.export_act.setShortcut(QKeySequence('Ctrl+E'))
        self.export_act.triggered.connect(self.export_file)

    def _create_menus(self):
        file_menu = self.menuBar().addMenu('File')
        file_menu.addAction(self.open_act)
        file_menu.addAction(self.open_new_act)
        file_menu.addAction(self.save_act)
        file_menu.addAction(self.load_act)
        file_menu.addAction(self.export_act)

    def open_file(self, type: int = 0):
        path, _ = QFileDialog.getOpenFileName(self, 'Open image')
        if path is None or path == '':
            print("Can't open file")
            return
        self.canvas.load_image(path, type)

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save image')
        if path:
            self.canvas.save_project(path)
    
    def load_project(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Load project', filter="EpiGimp Projects (*.epigimp)")
        if path:
            self.canvas.load_project(path)

    def export_file(self):
        export_dialog = ExportWidget(self)
        export_dialog.export_image(self.canvas.canvas[self.canvas.canva_selected])

    # def toggle_circle_mode(self, checked):
    #     self.canvas.set_circle_mode(checked)
    #     if checked:
    #         self.circle_btn.setText("Circle Mode: ON")
    #     else:
    #         self.circle_btn.setText("Circle Mode: OFF")
