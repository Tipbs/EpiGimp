import typing
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot, QPoint
from PySide6.QtGui import QAction, QKeySequence, QResizeEvent, QCloseEvent
from PySide6.QtWidgets import (
    QDockWidget, QFileDialog, QMainWindow, QWidget, QStatusBar, QMessageBox
)

from EpiGimp.ui.widgets.canvas_widget import CanvasWidget, CanvaWidget
from EpiGimp.ui.widgets.export_widget import ExportWidget
from EpiGimp.ui.dialogs.settings_dialog import SettingsDialog
from EpiGimp.ui.dialogs.new_image_dialog import NewImageDialog
from EpiGimp.ui.widgets.layers_widget import LayersWidget
from EpiGimp.core.canva import Canva
from EpiGimp.ui.dialogs.metadata_dialog import MetadataDialog, EditableMetadataDialog
from EpiGimp.ui.widgets.tools_widget import ToolsWidget
from EpiGimp.ui.dialogs.color_adjustment_dialog import ColorTemperatureDialog

if typing.TYPE_CHECKING:
    pass

class MainWindow(QMainWindow):
    """
    The main application window for EpiGimp.
    
    Manages the central canvas area, dockable widgets (Layers, Tools),
    menus, and global application state.
    """
    
    image_loaded = Signal(Canva)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the MainWindow.

        Args:
            parent (Optional[QWidget]): The parent widget, if any.
        """
        super().__init__(parent)
        self.setWindowTitle('EpiGimp - prototype')
        
        # Initialize UI Components
        self.settings = SettingsDialog(self)
        self._init_ui()
        self._setup_docks()
        self._create_actions()
        self._create_menus()
        
        # Status Bar
        self.setStatusBar(QStatusBar(self))

        # logic connections
        self._connect_signals()

        # Set initial tool
        initial_tool = self.tools_panel.get_current_tool()
        if initial_tool:
            self.on_tool_selected(initial_tool)

        # Load initial settings
        self.load_settings(0)
        self.settings.apply_signal[int].connect(lambda: self.load_settings(1))

    def _init_ui(self) -> None:
        """Initialize the central widget and main layout."""
        self.canvas_widget = CanvasWidget()
        self.setCentralWidget(self.canvas_widget)

    def _setup_docks(self) -> None:
        """Initialize and arrange dock widgets (Layers, Toolbox)."""
        # --- Layers Dock ---
        self.layers_widget = LayersWidget()
        
        # Primary Layers Dock (Right Side)
        self.layers_dock = QDockWidget("Layers", self)
        self.layers_dock.setWidget(self.layers_widget)
        self.layers_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.layers_dock)

        # Note: Original code had a second empty dock named "Layers" at the bottom. 
        # I have consolidated it into one functional dock above. 
        # If the bottom dock was intended for a different purpose (e.g. History), rename it.

        # --- Toolbox Dock ---
        self.tools_panel = ToolsWidget()
        self.tools_dock = QDockWidget("Toolbox", self)
        self.tools_dock.setWidget(self.tools_panel)
        self.tools_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.tools_dock)

    def _connect_signals(self) -> None:
        """Connect internal signals and slots."""
        # Canvas <-> Layers connections
        self.canvas_widget.currentChanged.connect(lambda index: self.layers_widget.set_canva(self.current_canva()))
        self.image_loaded.connect(self.canvas_widget.add_canva)
        self.image_loaded.connect(self._set_tool_on_new_canvas)  # Set tool on new canvases
        self.canvas_widget.currentChanged.connect(self.canva_update)
        
        # Layer Widget Buttons
        self.layers_widget.btn_add.clicked.connect(self.add_layer)
        self.layers_widget.btn_del.clicked.connect(
            lambda: self.del_layer(self.layers_widget.list_widget.currentRow())
        )
        self.layers_widget.btn_up.clicked.connect(
            lambda: self.swap_layer(self.layers_widget.list_widget.currentRow(), self.layers_widget.list_widget.currentRow() - 1)
        )
        self.layers_widget.btn_down.clicked.connect(
            lambda: self.swap_layer(self.layers_widget.list_widget.currentRow(), self.layers_widget.list_widget.currentRow() + 1)
        )
        self.layers_widget.list_widget.currentItemChanged.connect(self.change_canva)

        # Tool selection
        self.tools_panel.toolSelected.connect(self.on_tool_selected)

        # Drawing
        self.canvas_widget.mouse_moved.connect(self.drawing)

    # =========================================================================
    # Canvas & Layer Logic
    # =========================================================================

    def current_canva(self) -> Optional[Canva]:
        """
        Get the data object (Canva) associated with the currently active tab.

        Returns:
            Optional[Canva]: The current Canva object, or None if no tabs are open.
        """
        widget = self.current_canva_widget()
        if not widget:
            return None
        return widget.canva
    
    def current_canva_widget(self) -> Optional[CanvaWidget]:
        """
        Get the widget wrapper (CanvaWidget) associated with the currently active tab.

        Returns:
            Optional[CanvaWidget]: The current widget, or None if no tabs are open.
        """
        if self.canvas_widget.count() == 0:
            return None
        return self.canvas_widget.current_canva_widget()

    @Slot()
    def change_canva(self) -> None:
        """
        Handle switching focus between canvas layers or updating the current canvas state.
        Ensures the layer widget is synced with the active canvas.
        """
        cw = self.current_canva_widget()
        if not cw or not cw.canva.layers:
            return

        # Disconnect old signals if necessary to avoid multiple connections (logic check recommended here in future)
        try:
            self.layers_widget.render.disconnect()
        except RuntimeError:
            pass # Signal wasn't connected

        self.layers_widget.render.connect(lambda: cw.draw_canva())
        
        current_row = self.layers_widget.list_widget.currentRow()
        if current_row >= 0:
            self.current_canva().set_active_layer(current_row)

    @Slot(QPoint)
    def drawing(self, pos: QPoint) -> None:
        """
        Apply the currently selected tool to the canvas at the given position.

        Args:
            pos (QPoint): The mouse position on the canvas.
        """
        cw = self.current_canva_widget()
        canva = self.current_canva()
        
        if not cw or not canva:
            return
            
        tool = self.tools_panel.get_current_tool()
        if tool:
            # apply returns a rect that was modified, logic can be used for partial updates
            _ = tool.apply(pos, canva.active_layer)
            cw.draw_canva()

    @Slot()
    def on_tool_selected(self, tool) -> None:
        """
        Handle tool selection from the tools widget.

        Args:
            tool: The selected tool instance
        """
        # Set tool for all canvas widgets
        for i in range(self.canvas_widget.count()):
            widget = self.canvas_widget.widget(i)
            if isinstance(widget, CanvaWidget):
                widget.set_tool(tool)

    @Slot()
    def _set_tool_on_new_canvas(self) -> None:
        """Set the current tool on the most recently created canvas."""
        cw = self.current_canva_widget()
        if cw:
            current_tool = self.tools_panel.get_current_tool()
            if current_tool:
                cw.set_tool(current_tool)

    @Slot()
    def canva_update(self) -> None:
        """Updates the layers widget when the canvas changes (e.g. switching tabs)."""
        cw = self.current_canva_widget()
        if cw:
            self.layers_widget.update_layer_from_canva(cw.canva)
            # Ensure we don't stack connections
            try:
                cw.layer_changed.disconnect(self.layers_widget.update_layer_from_canva)
            except RuntimeError:
                pass
            cw.layer_changed.connect(self.layers_widget.update_layer_from_canva)

    def swap_layer(self, fst: int, snd: int) -> None:
        """
        Swap two layers in the current canvas.

        Args:
            fst (int): Index of the first layer.
            snd (int): Index of the second layer.
        """
        if self.canvas_widget.count() == 0:
            return
        self.current_canva_widget().swap_layer(fst, snd)

    def add_layer(self) -> None:
        """Add a new empty layer to the current canvas."""
        if self.canvas_widget.count() == 0:
            return
        self.current_canva_widget().add_layer()

    def del_layer(self, idx: int) -> None:
        """
        Delete a layer from the current canvas.

        Args:
            idx (int): Index of the layer to delete.
        """
        if self.canvas_widget.count() == 0:
            return
        self.current_canva_widget().del_layer(idx)

    # =========================================================================
    # Selection Operations
    # =========================================================================

    def select_all(self) -> None:
        """Select the entire canvas."""
        canva = self.current_canva()
        cw = self.current_canva_widget()
        if canva and cw:
            # Create a rectangle covering the entire canvas
            from PySide6.QtCore import QRect
            full_rect = QRect(0, 0, canva.shape[1], canva.shape[0])
            canva.set_selection(full_rect, 'rectangle')
            cw.update()

    def deselect(self) -> None:
        """Clear the current selection."""
        canva = self.current_canva()
        cw = self.current_canva_widget()
        if canva and cw:
            canva.clear_selection()
            cw.update()

    # =========================================================================
    # Edit Operations
    # =========================================================================

    def copy_selection(self) -> None:
        """Copy the current selection to clipboard."""
        canva = self.current_canva()
        if canva and canva.has_selection():
            if canva.copy_selection():
                self.statusBar().showMessage("Selection copied", 2000)
            else:
                self.statusBar().showMessage("Failed to copy selection", 2000)

    def cut_selection(self) -> None:
        """Cut the current selection (copy then delete)."""
        canva = self.current_canva()
        cw = self.current_canva_widget()
        if canva and cw and canva.has_selection():
            if canva.cut_selection():
                cw.draw_canva()
                self.statusBar().showMessage("Selection cut", 2000)
            else:
                self.statusBar().showMessage("Failed to cut selection", 2000)

    def paste_selection(self) -> None:
        """Paste clipboard content as a new layer."""
        canva = self.current_canva()
        cw = self.current_canva_widget()
        if canva and cw:
            if canva.paste_selection():
                # Update layers widget
                self.layers_widget.update_layer_from_canva(canva)
                cw.draw_canva()
                self.statusBar().showMessage("Pasted as new layer", 2000)
            else:
                self.statusBar().showMessage("Nothing to paste", 2000)

    def delete_selection(self) -> None:
        """Delete the current selection."""
        canva = self.current_canva()
        cw = self.current_canva_widget()
        if canva and cw and canva.has_selection():
            if canva.delete_selection():
                cw.draw_canva()
                self.statusBar().showMessage("Selection deleted", 2000)
            else:
                self.statusBar().showMessage("Failed to delete selection", 2000)

    def fill_selection(self) -> None:
        """Fill the current selection with a color."""
        from PySide6.QtWidgets import QColorDialog
        
        canva = self.current_canva()
        cw = self.current_canva_widget()
        
        if not canva or not cw or not canva.has_selection():
            QMessageBox.warning(self, "No Selection", "Please create a selection first.")
            return
        
        # Open color picker
        color = QColorDialog.getColor()
        if color.isValid():
            rgba = (color.red(), color.green(), color.blue(), color.alpha())
            if canva.fill_selection(rgba):
                cw.draw_canva()
                self.statusBar().showMessage("Selection filled", 2000)
            else:
                self.statusBar().showMessage("Failed to fill selection", 2000)

    # =========================================================================
    # Actions & Menus
    # =========================================================================

    def _create_actions(self) -> None:
        """Create QActions for menus and shortcuts."""
        # File Actions
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

        self.exit_act = QAction('Exit', self)
        self.exit_act.triggered.connect(self.close)

        # Display Actions
        self.fullscreen_act = QAction('Toggle Fullscreen', self, checkable=True)
        self.fullscreen_act.setShortcut(QKeySequence('F11'))
        self.fullscreen_act.triggered.connect(self.toggle_fullscreen)

        # Image/Transform Actions
        self.metadata_act = QAction('See Metadata...', self)
        self.metadata_act.triggered.connect(self.show_metadata_dialog)

        self.metadata_edit_act = QAction('Edit Metadata...', self)
        self.metadata_edit_act.triggered.connect(self.edit_metadata_dialog)

        self.flip_horizontal_act = QAction('Flip Horizontal', self)
        self.flip_horizontal_act.triggered.connect(lambda: self._safe_transform('flip_horizontal'))

        self.flip_vertical_act = QAction('Flip Vertical', self)
        self.flip_vertical_act.triggered.connect(lambda: self._safe_transform('flip_vertical'))

        self.rotate_act = QAction('Rotate 90° Clockwise', self)
        self.rotate_act.triggered.connect(lambda: self._safe_transform('rotate_90_clockwise'))

        self._rotate_ccw_act = QAction('Rotate 90° Counterclockwise', self)
        self._rotate_ccw_act.triggered.connect(lambda: self._safe_transform('rotate_90_counterclockwise'))

        self._rotate_180_act = QAction('Rotate 180°', self)
        self._rotate_180_act.triggered.connect(lambda: self._safe_transform('rotate_180'))

        # Color Actions
        self._temp_adjust_act = QAction('Adjust Color Temperature...', self)
        self._temp_adjust_act.triggered.connect(self.adjust_temp_color)

        # Selection Actions
        self.select_all_act = QAction('Select All', self)
        self.select_all_act.setShortcut(QKeySequence('Ctrl+A'))
        self.select_all_act.triggered.connect(self.select_all)

        self.deselect_act = QAction('Deselect', self)
        self.deselect_act.setShortcut(QKeySequence('Ctrl+Shift+A'))
        self.deselect_act.triggered.connect(self.deselect)

        # Edit Actions
        self.copy_act = QAction('Copy', self)
        self.copy_act.setShortcut(QKeySequence('Ctrl+C'))
        self.copy_act.triggered.connect(self.copy_selection)

        self.cut_act = QAction('Cut', self)
        self.cut_act.setShortcut(QKeySequence('Ctrl+X'))
        self.cut_act.triggered.connect(self.cut_selection)

        self.paste_act = QAction('Paste', self)
        self.paste_act.setShortcut(QKeySequence('Ctrl+V'))
        self.paste_act.triggered.connect(self.paste_selection)

        self.delete_sel_act = QAction('Delete Selection', self)
        self.delete_sel_act.setShortcut(QKeySequence('Delete'))
        self.delete_sel_act.triggered.connect(self.delete_selection)

        self.fill_act = QAction('Fill Selection...', self)
        self.fill_act.setShortcut(QKeySequence('Ctrl+F'))
        self.fill_act.triggered.connect(self.fill_selection)

    def _safe_transform(self, method_name: str) -> None:
        """Helper to apply transforms only if a widget exists."""
        cw = self.current_canva_widget()
        if cw:
            cw.transform(method_name)

    def _create_menus(self) -> None:
        """Assemble the menu bar."""
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu('File')
        file_menu.addAction(self.new_act)
        file_menu.addAction(self.open_act)
        file_menu.addAction(self.open_new_act)
        file_menu.addAction(self.save_act)
        file_menu.addAction(self.load_act)
        file_menu.addAction(self.export_act)
        file_menu.addSeparator()
        file_menu.addAction(self.settings_act)
        file_menu.addAction(self.exit_act)

        # Edit Menu
        edit_menu = menu_bar.addMenu('Edit')
        edit_menu.addAction(self.copy_act)
        edit_menu.addAction(self.cut_act)
        edit_menu.addAction(self.paste_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.delete_sel_act)
        edit_menu.addAction(self.fill_act)

        # Display Menu
        display_menu = menu_bar.addMenu('Display')
        display_menu.addAction(self.fullscreen_act)

        # Image Menu
        image_menu = menu_bar.addMenu('Image')
        image_menu.addAction(self.metadata_act)
        image_menu.addAction(self.metadata_edit_act)
        
        transform_menu = image_menu.addMenu('Transform')
        transform_menu.addAction(self.flip_horizontal_act)
        transform_menu.addAction(self.flip_vertical_act)
        transform_menu.addAction(self.rotate_act)
        transform_menu.addAction(self._rotate_ccw_act)
        transform_menu.addAction(self._rotate_180_act)

        # Select Menu
        select_menu = menu_bar.addMenu('Select')
        select_menu.addAction(self.select_all_act)
        select_menu.addAction(self.deselect_act)

        # Color Menu
        color_menu = menu_bar.addMenu('Color')
        color_menu.addAction(self._temp_adjust_act)

    # =========================================================================
    # Dialogs & Features
    # =========================================================================

    def toggle_fullscreen(self, checked: bool) -> None:
        """Toggle between fullscreen and normal mode."""
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()

    def show_metadata_dialog(self) -> None:
        """Show the read-only metadata dialog."""
        canva = self.current_canva()
        if canva is None:
            QMessageBox.warning(self, "No Image", "No image is currently loaded.")
            return
        dialog = MetadataDialog(canva, self)
        dialog.exec()

    def edit_metadata_dialog(self) -> None:
        """Show the editable metadata dialog."""
        canva = self.current_canva()
        if canva is None:
            QMessageBox.warning(self, "No Image", "No image is currently loaded.")
            return
        dialog = EditableMetadataDialog(canva, self)
        dialog.exec()
    
    def adjust_temp_color(self) -> None:
        """Open the color temperature adjustment dialog."""
        canva_widget = self.current_canva_widget()
        if canva_widget is None:
            QMessageBox.warning(self, "No Image", "No image is currently loaded.")
            return
        temp_adjust_widget = ColorTemperatureDialog(parent=self, canva_widget=canva_widget)
        temp_adjust_widget.exec()
    
    def create_new_image(self) -> None:
        """Open dialog to create a new empty image project."""
        dialog = NewImageDialog(self)
        dialog.image_created.connect(self.image_loaded.emit)
        dialog.exec()

    def open_file(self, type: int = 0) -> None:
        """
        Open an image file.

        Args:
            type (int): 0 to open in a new tab, 1 to import as layer into current project.
        """
        path, _ = QFileDialog.getOpenFileName(self, 'Open image')
        if not path:
            return
        
        if type == 1 and self.canvas_widget.count() > 0:
            cw = self.current_canva_widget()
            if cw:
                cw.import_image_as_layer(path)
        else:
            self.image_loaded.emit(Canva.load_image(path))

    def save_file(self) -> None:
        """Save the current project to disk."""
        canva = self.current_canva()
        if not canva:
            return
            
        path, _ = QFileDialog.getSaveFileName(self, 'Save image')
        if path:
            canva.save_project(path)
    
    def load_project(self, type: int = 0) -> None:
        """Load an existing .epigimp project."""
        path, _ = QFileDialog.getOpenFileName(self, 'Load project', filter="EpiGimp Projects (*.epigimp)")
        if not path:
            return
        self.image_loaded.emit(Canva.from_project(path))

    def load_project_from_startup(self, path: str) -> None:
        """
        Load a project programmatically (used by StartupDialog).

        Args:
            path (str): File path to the project.
        """
        if not path:
            return
        self.image_loaded.emit(Canva.from_project(path))

    def export_file(self) -> None:
        """Open export dialog for the current image."""
        canva = self.current_canva()
        if canva:
            export_dialog = ExportWidget(self)
            export_dialog.export_image(canva)

    def open_settings(self) -> None:
        """Display the settings window."""
        self.settings.show()

    # =========================================================================
    # Settings & State Management
    # =========================================================================

    def load_settings(self, type: int = 0) -> None:
        """
        Load application settings.
        
        Args:
            type (int): 0 for Initialization (startup), 1 for Apply (user changed settings).
        """
        if 'general' in self.settings.settings_manager.settings:
            self.load_general_settings(self.settings.settings_manager.settings['general'], type)
        
        if 'shortcuts' in self.settings.settings_manager.settings:
            self.load_shortcuts_settings(self.settings.settings_manager.settings['shortcuts'], type)
    
    def load_general_settings(self, general_settings, type: int = 0) -> None:
        """
        Apply general settings (window size, startup screen, etc.).
        
        Args:
            general_settings: The settings object.
            type (int): 0 for startup, 1 for update.
        """
        # Restore Window Size on Startup
        if general_settings.restore_window[0] and type == 0:
            width, height = general_settings.restore_window[1]
            self.resize(width, height)

        # Show Startup Screen
        if general_settings.show_welcome_screen and type == 0:
            from EpiGimp.ui.widgets.startup_widget import StartupDialog
            welcome_dialog = StartupDialog(self.settings.settings_manager, self)
            welcome_dialog.create_new_clicked.connect(lambda: self.create_new_image())
            welcome_dialog.open_existing_clicked.connect(lambda: self.open_file(type=1))
            # Note: Changed lambda to use self.image_loaded or self.open_file consistently if possible
            welcome_dialog.open_recent_clicked.connect(lambda path: self.load_project_from_startup(path))
            welcome_dialog.show()

        # Load Last Project
        if general_settings.last_project[0] and general_settings.last_project[1] and type == 0:
            project_path = general_settings.last_project[1]
            if project_path.endswith('.epigimp'):
                self.load_project_from_startup(project_path) 
    
    def load_shortcuts_settings(self, shortcuts_settings, type: int = 0) -> None:
        """
        Apply keyboard shortcuts from settings.

        Args:
            shortcuts_settings: The shortcuts settings object.
            type (int): Context (unused currently but kept for consistency).
        """
        # Map human-readable setting names to class attribute names for actions
        action_mapping = {
            'Open File in Project': 'open_act',
            'Open File in New Tab': 'open_new_act',
            'Load Project': 'load_act',
            'Save Project': 'save_act',
            'Export': 'export_act'
        }
        
        # Iterate over settings and update actions dynamically
        if hasattr(shortcuts_settings, 'shortcuts'):
            for action_name, shortcut in shortcuts_settings.shortcuts.items():
                attr_name = action_mapping.get(action_name)
                if attr_name:
                    action: Optional[QAction] = getattr(self, attr_name, None)
                    if action:
                        action.setShortcut(QKeySequence(shortcut))

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle window resize events to save window geometry preference."""
        super().resizeEvent(event)
        size = self.size()
        # Save current size to settings manager directly
        if 'general' in self.settings.settings_manager.settings:
            self.settings.settings_manager.settings['general'].restore_window = [True, (size.width(), size.height())]

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle application close event. 
        Prompts for confirmation if unsaved work exists and saves state.
        """
        general_settings = self.settings.settings_manager.settings.get('general')

        if general_settings:
            # Save last project path if enabled
            if general_settings.last_project[0]:
                current_canva = self.current_canva()
                if self.canvas_widget.count() > 0 and current_canva and hasattr(current_canva, 'project_path'):
                    general_settings.last_project = [True, current_canva.project_path]
            
            # Confirm Exit
            if general_settings.confirm_unsaved and self.canvas_widget.count() > 0:
                reply = QMessageBox.question(
                    self, 
                    'Confirm Exit', 
                    'Are you sure you want to exit? Unsaved work will be lost.', 
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    event.ignore()
                    return

        # Persist settings to disk
        self.settings.settings_manager.save_settings(self.settings.settings_manager.settings)
        event.accept()
