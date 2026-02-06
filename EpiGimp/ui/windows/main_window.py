from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QFileDialog, QMainWindow, QVBoxLayout, QWidget, QStatusBar
from EpiGimp.ui.widgets.canvas_widgets import CanvasWidget
from EpiGimp.ui.widgets.export_widget import ExportWidget
from EpiGimp.ui.dialogs.settings_dialog import SettingsDialog
from PySide6.QtGui import QResizeEvent, QCloseEvent

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        #self.settings = load_settings()
        self.setWindowTitle('EpiGimp - prototype')
        w = QWidget()
        self.setCentralWidget(w)
        self.settings = SettingsDialog(self)
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


        self.load_settings(0)
        self.settings.apply_signal[int].connect(lambda: self.load_settings(1))
        #self.resize(self.settings.get('window', {}).get('width', 1200),
        #self.settings.get('window', {}).get('height', 800))


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

        self.settings_act = QAction('Settings...', self)
        self.settings_act.triggered.connect(self.open_settings)

    def _create_menus(self):
        file_menu = self.menuBar().addMenu('File')
        file_menu.addAction(self.open_act)
        file_menu.addAction(self.open_new_act)
        file_menu.addAction(self.save_act)
        file_menu.addAction(self.load_act)
        file_menu.addAction(self.export_act)
        file_menu.addSeparator()
        file_menu.addAction(self.settings_act)

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
    
    def load_project(self, path=None):
        if path is None:
            path, _ = QFileDialog.getOpenFileName(self, 'Load project', filter="EpiGimp Projects (*.epigimp)")
        if path:
            self.canvas.load_project(path)

    def export_file(self):
        export_dialog = ExportWidget(self)
        export_dialog.export_image(self.canvas.canvas[self.canvas.canva_selected])

    def open_settings(self):
        self.settings.show()

    # def toggle_circle_mode(self, checked):
    #     self.canvas.set_circle_mode(checked)
    #     if checked:
    #         self.circle_btn.setText("Circle Mode: ON")
    #     else:
    #         self.circle_btn.setText("Circle Mode: OFF")

    def load_settings(self, type: int = 0):

        self.load_general_settings(self.settings.settings_manager.settings['general'], type)
        #self.load_appearance_settings(self.settings.settings['appearance'])
        #self.load_shortcuts_settings(self.settings.settings['shortcuts'])
    
    def load_general_settings(self, general_settings, type: int = 0):
        if general_settings.restore_window[0] and type == 0:
            self.resize(general_settings.restore_window[1][0], general_settings.restore_window[1][1])
        if general_settings.show_welcome_screen and type == 0:
            pass
        if general_settings.last_project[0] and general_settings.last_project[1] and type == 0:
            self.load_project(general_settings.last_project[1]) 

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        size = self.size()
        self.settings.settings_manager.settings['general'].restore_window = [True, (size.width(), size.height())]

    def closeEvent(self, event: QCloseEvent):
        self.settings.settings_manager.save_settings(self.settings.settings_manager.settings)
        if self.settings.settings_manager.settings['general'].last_project[0]:
            if len(self.canvas.canvas) > 0 and self.canvas.canvas[self.canvas.canva_selected].project_path:
                self.settings.settings_manager.settings['general'].last_project = [True, self.canvas[self.canvas.canva_selected].project_path]

        event.accept()