from EpiGimp.ui.dialogs.settings_dialog import SettingsPage
from PySide6.QtWidgets import QGroupBox, QFormLayout

class ShortcutsSettingsPage(SettingsPage):
    def __init__(self, parent=None, settings=None):
        super().__init__('Shortcuts Settings', parent)
        self.settings = settings
        # Add shortcuts settings widgets here
