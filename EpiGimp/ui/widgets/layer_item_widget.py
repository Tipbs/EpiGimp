from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QStackedWidget)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap

class LayerItemWidget(QWidget):
    """
    A generic GIMP-like layer row.
    Contains: Visibility Toggle, Lock Toggle, Thumbnail, and Editable Name.
    """
    # Signals to communicate with your Canvas/Controller
    visibilityToggled = Signal(bool)
    lockToggled = Signal(bool)
    nameChanged = Signal(str)

    def __init__(self, name="New Layer", thumbnail=None, parent=None):
        super().__init__(parent)
        
        # Main Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)

        # 1. Visibility Button (Eye Icon)
        self.btn_visible = QPushButton("👁")
        self.btn_visible.setCheckable(True)
        self.btn_visible.setChecked(True)
        self.btn_visible.setFixedSize(24, 24)
        self.btn_visible.setToolTip("Toggle Visibility")
        self.btn_visible.setStyleSheet("""
            QPushButton { border: none; background: transparent; color: #888; font-size: 14px; }
            QPushButton:checked { color: white; }
            QPushButton:hover { background: #444; }
        """)

        # 2. Thumbnail Label
        self.lbl_thumb = QLabel()
        self.lbl_thumb.setFixedSize(28, 28)
        self.lbl_thumb.setStyleSheet("background-color: #222; border: 1px solid #111;")
        self.lbl_thumb.setScaledContents(True)
        if thumbnail:
            self.lbl_thumb.setPixmap(thumbnail)
        else:
            # Placeholder for empty layer
            self.lbl_thumb.setText("░")
            self.lbl_thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 3. Layer Name (with double-click to edit)
        self.name_stack = QStackedWidget()
        
        self.lbl_name = QLabel(name)
        self.edit_name = QLineEdit(name)
        
        self.name_stack.addWidget(self.lbl_name)
        self.name_stack.addWidget(self.edit_name)
        
        # 4. Lock Button (Padlock Icon)
        # self.btn_lock = QPushButton("🔒")
        # self.btn_lock.setCheckable(True)
        # self.btn_lock.setFixedSize(24, 24)
        # self.btn_lock.setToolTip("Lock Layer")
        # self.btn_lock.setStyleSheet("""
        #     QPushButton { border: none; background: transparent; color: #888; }
        #     QPushButton:checked { color: #f39c12; }
        # """)

        # Assembly
        layout.addWidget(self.btn_visible)
        layout.addWidget(self.lbl_thumb)
        layout.addWidget(self.name_stack, 1) # Give name stretch priority
        # layout.addWidget(self.btn_lock)
        # self.setLayout(layout)


        # Logical Connections
        self.btn_visible.toggled.connect(self.visibilityToggled.emit)
        # self.btn_lock.toggled.connect(self.lockToggled.emit)
        self.edit_name.returnPressed.connect(self._finish_renaming)
        self.edit_name.editingFinished.connect(self._finish_renaming)

    def mouseDoubleClickEvent(self, event):
        """Enter rename mode on double click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.name_stack.setCurrentIndex(1)
            self.edit_name.setFocus()
            self.edit_name.selectAll()

    def _finish_renaming(self):
        new_name = self.edit_name.text()
        self.lbl_name.setText(new_name)
        self.name_stack.setCurrentIndex(0)
        self.nameChanged.emit(new_name)

    def update_thumbnail(self, pixmap: QPixmap):
        """Call this whenever the Canvas changes to update the layer icon"""
        self.lbl_thumb.setPixmap(pixmap.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
