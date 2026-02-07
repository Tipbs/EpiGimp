from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QDockWidget, QFileDialog, QMainWindow, QVBoxLayout, QWidget, QStatusBar, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from EpiGimp.ui.widgets.canvas_widget import CanvasWidget
from EpiGimp.ui.widgets.export_widget import ExportWidget
from EpiGimp.ui.dialogs.settings_dialog import SettingsDialog
from EpiGimp.ui.dialogs.new_image_dialog import NewImageDialog
from PySide6.QtGui import QResizeEvent, QCloseEvent
from EpiGimp.ui.widgets.layers_widget import LayersWidget
from EpiGimp.core.canva import Canva
from EpiGimp.ui.dialogs.metadata_dialog import MetadataDialog, EditableMetadataDialog

class MainWindow(QMainWindow):
    image_loaded = Signal(Canva)

    def __init__(self, parent=None):
        super().__init__(parent)
        #self.settings = load_settings()
        self.setWindowTitle('EpiGimp - prototype')
        self.layers_widget = LayersWidget()
        w = QWidget()
        self.setCentralWidget(w)
        self.settings = SettingsDialog(self)
        layout = QVBoxLayout(w)
        self.dock_widget = QDockWidget("Layers", self)
        # self.dock_widget.setObjectName("Layers")
        self.dock_widget.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        layers = QWidget()
        layout = QVBoxLayout(layers)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self.layers_widget)
        # layout.addWidget(self.input_line)
        self.dock_widget.setWidget(layers)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_widget)

        self.canvas_widget = CanvasWidget()
        self.canvas_widget.currentChanged.connect(lambda index: self.layers_widget.set_canva(self.current_canva()))
        self.image_loaded.connect(self.canvas_widget.add_canva)
        self.layers_widget.btn_add.clicked.connect(self.add_layer)
        self.canvas_widget.currentChanged.connect(self.canva_update)
        layout.addWidget(self.canvas_widget)
        layout.addWidget(self.layers_widget)
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

    def canva_update(self):
        self.layers_widget.update_layer_from_canva(self.canvas_widget.currentWidget().canva)
        self.canvas_widget.currentWidget().layer_created.connect(self.layers_widget.update_layer_from_canva)


    def add_layer(self):
        if self.canvas_widget.count() == 0:
            return None
        self.canvas_widget.currentWidget().add_layer()

    def current_canva(self) -> Canva|None:
        # print(self.canvas_widget.count())
        if self.canvas_widget.count() == 0:
            return None
        return self.canvas_widget.currentWidget().canva


    def _create_actions(self):
        self.new_act = QAction('New Project', self)
        self.new_act.setShortcut(QKeySequence('Ctrl+N'))
        self.new_act.triggered.connect(self.create_new_image)
        self.open_act = QAction('Open File in Project...', self)
        self.open_act.setShortcut(QKeySequence('Ctrl+O'))
        self.open_act.triggered.connect(lambda: self.open_file(type=1))

        self.open_new_act = QAction('Open File in New Tab...', self)
        self.open_new_act.setShortcut(QKeySequence('Ctrl+Shift+O'))
        self.open_new_act.triggered.connect(lambda: self.open_file(type=0))
        
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

        self.fullscreen_act = QAction('Toggle Fullscreen', self, checkable=True)
        self.fullscreen_act.setShortcut(QKeySequence('F11'))
        self.fullscreen_act.triggered.connect(self.toggle_fullscreen)

        self.metadata_act = QAction('See Metadata...', self)
        self.metadata_act.triggered.connect(self.show_metadata_dialog)

        self.metadata_edit_act = QAction('Edit Metadata...', self)
        self.metadata_edit_act.triggered.connect(self.edit_metadata_dialog)

        self.exit_act = QAction('Exit', self)
        self.exit_act.triggered.connect(self.close)

    def _create_menus(self):
        file_menu = self.menuBar().addMenu('File')
        file_menu.addAction(self.new_act)
        file_menu.addAction(self.open_act)
        file_menu.addAction(self.open_new_act)
        file_menu.addAction(self.save_act)
        file_menu.addAction(self.load_act)
        file_menu.addAction(self.export_act)
        file_menu.addSeparator()
        file_menu.addAction(self.settings_act)

        display_menu = self.menuBar().addMenu('Display')
        display_menu.addAction(self.fullscreen_act)

        image_menu = self.menuBar().addMenu('Image')
        image_menu.addAction(self.metadata_act)
        image_menu.addAction(self.metadata_edit_act)

    def toggle_fullscreen(self, checked):
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()

    def show_metadata_dialog(self):
        canva = self.current_canva()
        if canva is None:
            QMessageBox.warning(self, "No Image", "No image is currently loaded.")
            return
        dialog = MetadataDialog(canva, self)
        dialog.exec()

    def edit_metadata_dialog(self):
        canva = self.current_canva()
        if canva is None:
            QMessageBox.warning(self, "No Image", "No image is currently loaded.")
            return
        dialog = EditableMetadataDialog(canva, self)
        dialog.exec()
    
    def create_new_image(self):
        dialog = NewImageDialog(self)
        dialog.image_created.connect(self.image_loaded.emit)
        dialog.exec()

    def open_file(self, type: int = 0):
        path, _ = QFileDialog.getOpenFileName(self, 'Open image')
        if path is None or path == '':
            print("Can't open file")
            return
        self.image_loaded.emit(Canva.load_image(path))

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save image')
        if path:
            self.current_canva().save_project(path)
    
    def load_project(self, type: int = 0):
        path, _ = QFileDialog.getOpenFileName(self, 'Load project', filter="EpiGimp Projects (*.epigimp)")
        if path is None or path == '':
            print("Can't open project")
            return
        if type == 1:
            self.image_loaded.emit(self.current_canva().add_img_layer(path))
        else:
            self.image_loaded.emit(Canva.from_project(path))

    def load_project_from_startup(self, path: str):
        if path is None or path == '':
            print("No last project to load")
            return
        self.image_loaded.emit(Canva.from_project(path))

    def export_file(self):
        export_dialog = ExportWidget(self)
        export_dialog.export_image(self.current_canva())

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
        self.load_shortcuts_settings(self.settings.settings_manager.settings['shortcuts'], type)
    
    def load_general_settings(self, general_settings, type: int = 0):
        if general_settings.restore_window[0] and type == 0:
            self.resize(general_settings.restore_window[1][0], general_settings.restore_window[1][1])
        if general_settings.show_welcome_screen and type == 0:
            from EpiGimp.ui.widgets.startup_widget import StartupDialog
            welcome_dialog = StartupDialog(self.settings.settings_manager, self)
            welcome_dialog.create_new_clicked.connect(lambda: self.create_new_image())
            welcome_dialog.open_existing_clicked.connect(lambda: self.open_file(type=1))
            welcome_dialog.open_recent_clicked.connect(lambda path: self.canvas.load_image(path, type=0))
            welcome_dialog.show()
        if general_settings.last_project[0] and general_settings.last_project[1] and type == 0:
            self.load_project_from_startup(general_settings.last_project[1]) 
    
    def load_shortcuts_settings(self, shortcuts_settings, type: int = 0):
        # Map setting names to action attributes
        action_mapping = {
            'Open File in Project': 'self.open_act',
            'Open File in New Tab': 'self.open_new_act',
            'Load Project': 'self.load_act',
            'Save Project': 'self.save_act',
            'Export': 'self.export_act'
        }
        
        for action_name, shortcut in shortcuts_settings.shortcuts.items():
            action_attr = action_mapping.get(action_name)
            if action_attr:
                action = getattr(self, action_attr, None)
                if action:
                    action.setShortcut(QKeySequence(shortcut))

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        size = self.size()
        self.settings.settings_manager.settings['general'].restore_window = [True, (size.width(), size.height())]

    def closeEvent(self, event: QCloseEvent):
        if self.settings.settings_manager.settings['general'].last_project[0]:
            if self.canvas_widget.count() > 0 and self.current_canva().project_path:
                self.settings.settings_manager.settings['general'].last_project = [True, self.current_canva().project_path]
        if self.settings.settings_manager.settings['general'].confirm_unsaved and self.canvas_widget.count() > 0:
            reply = QMessageBox.question(self, 'Confirm Exit', 'Are you sure you want to exit? Unsaved work will be lost.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return

        self.settings.settings_manager.save_settings(self.settings.settings_manager.settings)
        event.accept()
