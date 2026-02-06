from PySide6.QtCore import QSettings
from typing import Dict, List, Tuple

class Settings:
    def __init__(self, type: int = 0):
        pass
    
    def save(self, qsettings: QSettings):
        pass

    def load(self, qsettings: QSettings):
        pass

# get all settings classes here
def get_settings() -> Dict:
    return {
        'general': GeneralSettings,
        'appearance': AppearanceSettings,
        'shortcuts': ShortcutsSettings
    }

class GeneralSettings(Settings):
    def __init__(self):
        self.last_project = [False, '']
        self.show_welcome_screen = True 
        self.restore_window = (1200, 800)
    
    def save(self, qsettings: QSettings):
        qsettings.beginGroup('General')
        qsettings.setValue('last_project', self.last_project)
        qsettings.setValue('show_welcome_screen', self.show_welcome_screen)
        qsettings.setValue('restore_window', self.restore_window)
        qsettings.endGroup()
    
    def load(self, qsettings: QSettings):
        qsettings.beginGroup('General')
        self.last_project = qsettings.value('last_project', [False, ''], type=list)
        self.show_welcome_screen = qsettings.value('show_welcome_screen', True, type=bool)
        self.restore_window = qsettings.value('restore_window', [True, (1200, 800)], type=list)
        qsettings.endGroup()

class AppearanceSettings(Settings):
    def __init__(self):
        self.theme = 'Light'
        self.font_size = 12

    def save(self, qsettings: QSettings):
        qsettings.beginGroup('Appearance')
        qsettings.setValue('theme', self.theme)
        qsettings.setValue('font_size', self.font_size)
        qsettings.endGroup()

    def load(self, qsettings: QSettings):
        qsettings.beginGroup('Appearance')
        self.theme = qsettings.value('theme', 'Light')
        self.font_size = int(qsettings.value('font_size', 12))
        qsettings.endGroup()

class ShortcutsSettings(Settings):
    def __init__(self):
        self.shortcuts = {
            'New Project': 'Ctrl+N',
            'Open Project': 'Ctrl+O',
            'Save Project': 'Ctrl+S',
        }
    
    def save(self, qsettings: QSettings):
        qsettings.beginGroup('Shortcuts')
        for action, shortcut in self.shortcuts.items():
            qsettings.setValue(action, shortcut)
        qsettings.endGroup()
    
    def load(self, qsettings: QSettings):
        qsettings.beginGroup('Shortcuts')
        for action in self.shortcuts.keys():
            self.shortcuts[action] = qsettings.value(action, self.shortcuts[action])
        qsettings.endGroup()


class SettingsManager:
    def __init__(self):
        self.settings = self.load_settings()

    def load_settings(self):
        qsettings = QSettings('EpiGimp', 'EpiGimp')
        settings = {}
        for key, setting_class in get_settings().items():
            setting_instance = setting_class()
            setting_instance.load(qsettings)
            settings[key] = setting_instance
        return settings

    def save_settings(self, settings):
        qsettings = QSettings('EpiGimp', 'EpiGimp')
        for setting in settings.values():
            setting.save(qsettings)
        qsettings.sync()
