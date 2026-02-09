from EpiGimp.ui.dialogs.settings_dialog import SettingsPage
from PySide6.QtWidgets import QGroupBox, QFormLayout, QCheckBox

class GeneralSettingsPage(SettingsPage):
    def __init__(self, parent=None, settings =None):
        super().__init__('General Settings', parent)
        
        # Startup group
        self.settings_manager = settings
        startup_group = QGroupBox("Startup", self)
        startup_layout = QFormLayout()
        self.open_last_project = QCheckBox("Open last project on startup")
        self.show_welcome = QCheckBox("Show welcome screen")
        self.restore_window = QCheckBox("Restore window size and position")
        startup_layout.addRow(self.open_last_project)
        startup_layout.addRow(self.show_welcome)
        startup_layout.addRow(self.restore_window)
        startup_group.setLayout(startup_layout)
        self.layout.addWidget(startup_group)

        # File handling group
        #file_group = QGroupBox("File Handling", self)
        #file_layout = QFormLayout()
        #self.autosave_interval = QSpinBox()
        #self.autosave_interval.setRange(0, 60)
        #self.autosave_interval.setSuffix(" minutes")
        #self.recent_files_count = QSpinBox()
        #self.recent_files_count.setRange(5, 50)
        #file_layout.addRow("Auto-save interval:", self.autosave_interval)
        #file_layout.addRow("Recent files count:", self.recent_files_count)
        #file_group.setLayout(file_layout)
        #self.layout.addWidget(file_group)
        
        ## Performance group
        #perf_group = QGroupBox("Performance", self)
        #perf_layout = QFormLayout()
        #self.undo_levels = QSpinBox()
        #self.undo_levels.setRange(10, 200)
        #perf_layout.addRow("Undo levels:", self.undo_levels)
        #perf_group.setLayout(perf_layout)
        #self.layout.addWidget(perf_group)
        
        ## Misc group
        misc_group = QGroupBox("Miscellaneous", self)
        misc_layout = QFormLayout()
        self.confirm_unsaved = QCheckBox("Confirm before closing unsaved work")
        self.show_tooltips = QCheckBox("Show tooltips")
        misc_layout.addRow(self.confirm_unsaved)
        misc_layout.addRow(self.show_tooltips)
        misc_group.setLayout(misc_layout)
        self.layout.addWidget(misc_group)
        
        self.layout.addStretch()
    
    def save_settings(self):
        self.settings_manager.settings['general'].show_welcome_screen = self.show_welcome.isChecked()
        self.settings_manager.settings['general'].last_project = [self.open_last_project.isChecked(), self.settings_manager.settings['general'].last_project[1]]
        self.settings_manager.settings['general'].restore_window = [self.restore_window.isChecked(), self.settings_manager.settings['general'].restore_window[1]]
        self.settings_manager.settings['general'].confirm_unsaved = self.confirm_unsaved.isChecked()
        self.settings_manager.settings['general'].show_tooltips = self.show_tooltips.isChecked()
    def load_settings(self):
        general = self.settings_manager.settings['general']
        self.show_welcome.setChecked(general.show_welcome_screen)
        self.open_last_project.setChecked(bool(general.last_project[0]))
        self.restore_window.setChecked(general.restore_window[0] is not None)
        self.confirm_unsaved.setChecked(general.confirm_unsaved)
        self.show_tooltips.setChecked(general.show_tooltips)
