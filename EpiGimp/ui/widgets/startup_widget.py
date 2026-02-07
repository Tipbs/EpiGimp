#startup widget, shown on startup if enabled in settings
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QTabWidget, QWidget, QListWidget, 
                               QCheckBox, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap


class StartupDialog(QDialog):
    create_new_clicked = Signal()
    open_existing_clicked = Signal()
    open_recent_clicked = Signal(str)
    
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("Welcome to EpiGimp")
        self.setModal(True)
        self.setMinimumSize(700, 500)
        
        self.init_ui()
        self.load_recent_files()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header with logo/title
        header = self._create_header()
        layout.addWidget(header)
        
        # Tab widget for different sections
        self.tabs = QTabWidget(self)
        self.tabs.addTab(self._create_welcome_tab(), "Welcome")
        self.tabs.addTab(self._create_personalize_tab(), "Personalize")
        self.tabs.addTab(self._create_create_tab(), "Create")
        self.tabs.addTab(self._create_release_notes_tab(), "Release Notes")
        
        layout.addWidget(self.tabs)
        
        # Footer with show on start and close button
        footer = self._create_footer()
        layout.addWidget(footer)
    
    def _create_header(self):
        """Create header with app name and version"""
        header_frame = QFrame(self)
        header_layout = QHBoxLayout(header_frame)
        
        title_label = QLabel("Welcome to EpiGimp 1.0.0", self)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        return header_frame
    
    def _create_welcome_tab(self):
        """Create the main welcome tab"""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        
        # Top section with create/open buttons
        top_section = QHBoxLayout()
        
        # Create new image section
        create_section = QVBoxLayout()
        create_label = QLabel("Create a new image", self)
        create_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        create_btn = QPushButton("Create", self)
        create_btn.setMinimumHeight(40)
        create_btn.clicked.connect(self._on_create_new)
        create_section.addWidget(create_label)
        create_section.addWidget(create_btn)
        
        # Open existing section
        open_section = QVBoxLayout()
        open_label = QLabel("Open an Existing Image", self)
        open_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        open_btn = QPushButton("Open", self)
        open_btn.setMinimumHeight(40)
        open_btn.clicked.connect(self._on_open_existing)
        open_section.addWidget(open_label)
        open_section.addWidget(open_btn)
        
        top_section.addLayout(create_section)
        top_section.addSpacing(20)
        top_section.addLayout(open_section)
        
        layout.addLayout(top_section)
        layout.addSpacing(20)
        
        # Recent images section
        recent_label = QLabel("Recent Images", self)
        recent_label.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(recent_label)
        
        self.recent_list = QListWidget(self)
        self.recent_list.itemDoubleClicked.connect(self._on_recent_double_clicked)
        layout.addWidget(self.recent_list)
        
        self.open_selected_btn = QPushButton("Open Selected Images", self)
        self.open_selected_btn.clicked.connect(self._on_open_selected)
        layout.addWidget(self.open_selected_btn)
        
        layout.addStretch()
        
        return widget
    
    def _create_personalize_tab(self):
        """Create personalize tab"""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        
        info_label = QLabel("Customize EpiGimp to your preferences", self)
        layout.addWidget(info_label)
        
        settings_btn = QPushButton("Open Settings", self)
        settings_btn.clicked.connect(self._on_open_settings)
        layout.addWidget(settings_btn)
        
        layout.addStretch()
        
        return widget
    
    def _create_create_tab(self):
        """Create create tab with templates"""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        
        templates_label = QLabel("Quick Start Templates", self)
        templates_label.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(templates_label)
        
        # Add template buttons
        templates = [
            ("Web Banner (1920x1080)", 1920, 1080),
            ("Social Media Post (1080x1080)", 1080, 1080),
            ("A4 Document (2480x3508)", 2480, 3508),
            ("HD Wallpaper (1920x1080)", 1920, 1080),
        ]
        
        for name, width, height in templates:
            btn = QPushButton(name, self)
            btn.clicked.connect(lambda checked, w=width, h=height: self._create_template(w, h))
            layout.addWidget(btn)
        
        layout.addStretch()
        
        return widget
    
    def _create_release_notes_tab(self):
        """Create release notes tab"""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        
        notes_label = QLabel(
            "EpiGimp 1.0.0 - Initial Release\n\n"
            "Features:\n"
            "• Layer support\n"
            "• Basic drawing tools\n"
            "• Image import/export\n"
            "• Customizable interface\n",
            self
        )
        layout.addWidget(notes_label)
        
        layout.addStretch()
        
        return widget
    
    def _create_footer(self):
        """Create footer with checkbox and buttons"""
        footer_frame = QFrame(self)
        footer_layout = QHBoxLayout(footer_frame)
        
        self.show_on_start_cb = QCheckBox(
            "Show on Start (You can show the Welcome dialog again from the \"Help\" menu)",
            self
        )
        self.show_on_start_cb.setChecked(
            self.settings_manager.settings['general'].show_welcome_screen
        )
        footer_layout.addWidget(self.show_on_start_cb)
        
        footer_layout.addStretch()
        
        help_btn = QPushButton("Help", self)
        help_btn.clicked.connect(self._on_help)
        footer_layout.addWidget(help_btn)
        
        close_btn = QPushButton("Close", self)
        close_btn.clicked.connect(self._on_close)
        footer_layout.addWidget(close_btn)
        
        return footer_frame
    
    def load_recent_files(self):
        """Load recent files into the list"""
        self.recent_list.clear()
        #recent_files = self.settings_manager.settings['general'].recent_files
        
        #for file_path in recent_files:
        #    self.recent_list.addItem(file_path)
    
    def _on_create_new(self):
        """Handle create new button"""
        self.create_new_clicked.emit()
        self._save_preference()
        self.accept()
    
    def _on_open_existing(self):
        """Handle open existing button"""
        self.open_existing_clicked.emit()
        self._save_preference()
        self.accept()
    
    def _on_recent_double_clicked(self, item):
        """Handle double click on recent file"""
        self.open_recent_clicked.emit(item.text())
        self._save_preference()
        self.accept()
    
    def _on_open_selected(self):
        """Handle open selected button"""
        selected_items = self.recent_list.selectedItems()
        if selected_items:
            self.open_recent_clicked.emit(selected_items[0].text())
            self._save_preference()
            self.accept()
    
    def _on_open_settings(self):
        """Open settings dialog"""
        from EpiGimp.ui.dialogs.settings_dialog import SettingsDialog
        settings_dlg = SettingsDialog(self)
        settings_dlg.exec()
    
    def _create_template(self, width, height):
        """Create new image from template"""
        # You can emit a signal with dimensions or handle directly
        self.create_new_clicked.emit()
        self._save_preference()
        self.accept()
    
    def _on_help(self):
        """Show help"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Help",
            "Welcome to EpiGimp!\n\n"
            "Use the tabs above to explore features."
        )
    
    def _on_close(self):
        """Close dialog"""
        self._save_preference()
        self.reject()
    
    def _save_preference(self):
        self.settings_manager.settings['general'].show_welcome_screen = \
            self.show_on_start_cb.isChecked()

