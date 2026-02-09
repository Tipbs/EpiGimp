from EpiGimp.ui.dialogs.settings_dialog import SettingsPage
from PySide6.QtWidgets import QGroupBox, QFormLayout, QLineEdit

class ShortcutsSettingsPage(SettingsPage):
    def __init__(self, parent=None, settings=None):
        super().__init__('Shortcuts Settings', parent)
        self.settings_manager = settings

        # Add shortcuts settings widgets here
        self.shortcut_groups = {}
        #for category, shortcuts in self.settings_manager.settings['shortcuts'].shortcuts.items():
        category = 'File Operations'
        group_box = QGroupBox(category, self)
        form_layout = QFormLayout()
        for action, shortcut in self.settings_manager.settings['shortcuts'].shortcuts.items():
            # Create a widget to display and edit the shortcut (e.g., QLineEdit or custom ShortcutEdit)
            shortcut_widget = QLineEdit(shortcut)
            form_layout.addRow(action, shortcut_widget)
        group_box.setLayout(form_layout)
        self.layout.addWidget(group_box)
        self.shortcut_groups[category] = (group_box, form_layout)

        self.layout.addStretch()
        
    def save_settings(self):
        for category, (group_box, form_layout) in self.shortcut_groups.items():
            shortcuts = {}
            for i in range(form_layout.rowCount()):
                action = form_layout.itemAt(i, QFormLayout.LabelRole).widget().text()
                shortcut = form_layout.itemAt(i, QFormLayout.FieldRole).widget().text()
                shortcuts[action] = shortcut
            self.settings_manager.settings['shortcuts'].shortcuts[category] = shortcuts
        
    def load_settings(self):
        for category, shortcuts in self.settings_manager.settings['shortcuts'].shortcuts.items():
            if category in self.shortcut_groups:
                group_box, form_layout = self.shortcut_groups[category]
                for i in range(form_layout.rowCount()):
                    action = form_layout.itemAt(i, QFormLayout.LabelRole).widget().text()
                    if action in shortcuts:
                        form_layout.itemAt(i, QFormLayout.FieldRole).widget().setText(shortcuts[action])

    
