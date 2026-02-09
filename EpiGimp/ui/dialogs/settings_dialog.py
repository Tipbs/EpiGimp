from PySide6.QtWidgets import QDialog, QListWidget, QListWidgetItem, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QStackedWidget, QPushButton
from PySide6.QtCore import Signal, Slot
from EpiGimp.config.settings import SettingsManager

class SettingsPage(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.label = QLabel(title, self)
        self.layout.addWidget(self.label, 0)
    
    def save_settings(self):
        pass

    def load_settings(self):
        pass

class SettingsContainer(QStackedWidget):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.pages = self._create_settings_pages(settings_manager)
        for page in self.pages.values():
            self.addWidget(page)
    def _create_settings_pages(self, settings_manager):
        from EpiGimp.ui.dialogs.settings.general import GeneralSettingsPage
        from EpiGimp.ui.dialogs.settings.appearance import AppearanceSettingsPage
        from EpiGimp.ui.dialogs.settings.shortcuts import ShortcutsSettingsPage

        pages = {}
        pages['General'] = GeneralSettingsPage(self, settings_manager)
        pages['Appearance'] = AppearanceSettingsPage(self, settings_manager)
        pages['Shortcuts'] = ShortcutsSettingsPage(self, settings_manager)

        for page in pages.values():
            page.load_settings()
        return pages
    
    def _save_settings(self):
        for page in self.pages.values():
            page.save_settings()

class SettingsDialog(QDialog):
    apply_signal = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_manager = SettingsManager()
        self.minimumSizeHint = (400, 300)
        self.setWindowTitle('Settings')
        self.setModal(True)

        self.init_ui()
        self.list_widget.currentRowChanged.connect(self.on_page_changed)
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.hlayout = QHBoxLayout()
        self.layout.addLayout(self.hlayout)

        self.list_widget = QListWidget(self)
        self.list_widget.addItem(QListWidgetItem('General'))
        self.list_widget.addItem(QListWidgetItem('Appearance'))
        self.list_widget.addItem(QListWidgetItem('Shortcuts'))
        self.hlayout.addWidget(self.list_widget, 1)

        self.settings_container = SettingsContainer(self.settings_manager, self)
        self.hlayout.addWidget(self.settings_container, 3)

        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton('Save', self)
        self.cancel_button = QPushButton('Cancel', self)
        self.apply_button = QPushButton('Apply', self)

        self.layout.addLayout(self.button_layout, 0)
        
        self.button_layout.addWidget(self.apply_button, 1)
        self.button_layout.addWidget(self.save_button,  1)
        self.button_layout.addWidget(self.cancel_button, 1)

        self.save_button.clicked.connect(self.on_save)
        self.cancel_button.clicked.connect(self.on_reject)
        self.apply_button.clicked.connect(self.on_apply)
        
    
    def on_page_changed(self, index):
        self.settings_container.setCurrentIndex(index)

    def on_apply(self):
        for page in self.settings_container.pages.values():
            page.save_settings()
        self.settings_manager.save_settings(self.settings_manager.settings)
        self.apply_signal.emit(1)
        print("Settings applied")
    
    def on_save(self):
        self.on_apply()
        print("Settings saved")
        self.accept()
    
    def on_reject(self):
        print("Settings changes canceled")
        self.reject()