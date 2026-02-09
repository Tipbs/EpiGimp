from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QLineEdit, QComboBox, QPushButton, 
                               QSpinBox, QDoubleSpinBox, QGroupBox, QTabWidget,
                               QWidget, QTextEdit, QCheckBox, QButtonGroup,
                               QToolButton, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from typing import Tuple, Dict
from EpiGimp.core.canva import Canva


class NewImageDialog(QDialog):
    
    image_created = Signal(Canva)
    
    TEMPLATES = {
        "1920 × 1080 (Full HD 16:9)": {"width": 1920, "height": 1080, "unit": "px", "ppi": 72},
        "1280 × 720 (HD 16:9)": {"width": 1280, "height": 720, "unit": "px", "ppi": 72},
        "3840 × 2160 (4K UHD 16:9)": {"width": 3840, "height": 2160, "unit": "px", "ppi": 72},
        "1080 × 1080 (Instagram)": {"width": 1080, "height": 1080, "unit": "px", "ppi": 72},
        "1920 × 1080 (YouTube)": {"width": 1920, "height": 1080, "unit": "px", "ppi": 72},
        "3508 × 2480 (A4 300 PPI)": {"width": 3508, "height": 2480, "unit": "px", "ppi": 300},
        "2480 × 3508 (A4 Portrait 300 PPI)": {"width": 2480, "height": 3508, "unit": "px", "ppi": 300},
        "4961 × 7016 (A3 300 PPI)": {"width": 4961, "height": 7016, "unit": "px", "ppi": 300},
        "640 × 480 (VGA)": {"width": 640, "height": 480, "unit": "px", "ppi": 72},
        "800 × 600 (SVGA)": {"width": 800, "height": 600, "unit": "px", "ppi": 72},
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create a New Image")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.init_ui()
        self.connect_signals()
        self.load_default_template()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Template selection
        template_group = self._create_template_group()
        layout.addWidget(template_group)
        
        # Image size section
        size_group = self._create_size_group()
        layout.addWidget(size_group)
        
        # Advanced options (collapsible)
        self.advanced_widget = self._create_advanced_options()
        layout.addWidget(self.advanced_widget)
        
        # Buttons
        button_layout = self._create_buttons()
        layout.addLayout(button_layout)
    
    def _create_template_group(self) -> QGroupBox:
        """Create template selection group"""
        group = QGroupBox("Template")
        layout = QVBoxLayout()
        
        self.template_combo = QComboBox()
        self.template_combo.addItems(self.TEMPLATES.keys())
        self.template_combo.setCurrentIndex(0)
        
        layout.addWidget(self.template_combo)
        group.setLayout(layout)
        
        return group
    
    def _create_size_group(self) -> QGroupBox:
        """Create image size configuration group"""
        group = QGroupBox("Image Size")
        layout = QGridLayout()
        
        # Width
        layout.addWidget(QLabel("Width:"), 0, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 100000)
        self.width_spin.setValue(1920)
        self.width_spin.setSuffix(" px")
        layout.addWidget(self.width_spin, 0, 1)
        
        # Orientation toggle buttons
        orientation_layout = QHBoxLayout()
        self.portrait_btn = QToolButton()
        self.portrait_btn.setText("⬜")
        self.portrait_btn.setCheckable(True)
        self.portrait_btn.setToolTip("Portrait")
        
        self.landscape_btn = QToolButton()
        self.landscape_btn.setText("▭")
        self.landscape_btn.setCheckable(True)
        self.landscape_btn.setChecked(True)
        self.landscape_btn.setToolTip("Landscape")
        
        self.orientation_group = QButtonGroup()
        self.orientation_group.addButton(self.portrait_btn)
        self.orientation_group.addButton(self.landscape_btn)
        
        orientation_layout.addWidget(self.portrait_btn)
        orientation_layout.addWidget(self.landscape_btn)
        orientation_layout.addStretch()
        
        layout.addLayout(orientation_layout, 0, 2, 2, 1)
        
        # Height
        layout.addWidget(QLabel("Height:"), 1, 0)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 100000)
        self.height_spin.setValue(1080)
        self.height_spin.setSuffix(" px")
        layout.addWidget(self.height_spin, 1, 1)
        
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line, 2, 0, 1, 3)
        
        # Resolution
        layout.addWidget(QLabel("Resolution:"), 3, 0)
        
        res_layout = QHBoxLayout()
        self.x_resolution = QDoubleSpinBox()
        self.x_resolution.setRange(1, 10000)
        self.x_resolution.setValue(72)
        self.x_resolution.setDecimals(2)
        res_layout.addWidget(self.x_resolution)
        
        res_layout.addWidget(QLabel("×"))
        
        self.y_resolution = QDoubleSpinBox()
        self.y_resolution.setRange(1, 10000)
        self.y_resolution.setValue(72)
        self.y_resolution.setDecimals(2)
        res_layout.addWidget(self.y_resolution)
        
        self.resolution_unit = QComboBox()
        self.resolution_unit.addItems(["pixels/in", "pixels/mm", "pixels/cm"])
        res_layout.addWidget(self.resolution_unit)
        
        layout.addLayout(res_layout, 3, 1, 1, 2)
        
        # Pixel info
        self.pixel_info = QLabel("1920 × 1080 pixels")
        self.pixel_info.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(self.pixel_info, 4, 1, 1, 2)
        
        # Color mode
        layout.addWidget(QLabel("Color Space:"), 5, 0)
        self.color_mode = QComboBox()
        self.color_mode.addItems([
            "RGB color",
            "Grayscale",
            "RGB color (linear)",
        ])
        layout.addWidget(self.color_mode, 5, 1, 1, 2)
        
        # Precision
        layout.addWidget(QLabel("Precision:"), 6, 0)
        self.precision = QComboBox()
        self.precision.addItems([
            "8-bit integer",
            "16-bit integer",
            "32-bit float",
        ])
        layout.addWidget(self.precision, 6, 1, 1, 2)
        
        # Gamma
        layout.addWidget(QLabel("Gamma:"), 7, 0)
        self.gamma = QComboBox()
        self.gamma.addItems([
            "sRGB",
            "Linear light",
        ])
        layout.addWidget(self.gamma, 7, 1, 1, 2)
        
        # Fill
        layout.addWidget(QLabel("Fill with:"), 8, 0)
        self.fill_combo = QComboBox()
        self.fill_combo.addItems([
            "Foreground color",
            "Background color",
            "White",
            "Transparency",
            "Pattern",
        ])
        self.fill_combo.setCurrentIndex(2)  # Default to White
        layout.addWidget(self.fill_combo, 8, 1, 1, 2)
        
        group.setLayout(layout)
        return group
    
    def _create_advanced_options(self) -> QWidget:
        """Create advanced options section"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Collapsible header
        header_layout = QHBoxLayout()
        self.advanced_toggle = QPushButton("▶ Advanced Options")
        self.advanced_toggle.setFlat(True)
        self.advanced_toggle.setCheckable(True)
        self.advanced_toggle.setStyleSheet("text-align: left; padding: 5px;")
        header_layout.addWidget(self.advanced_toggle)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Advanced content (initially hidden)
        self.advanced_content = QWidget()
        self.advanced_content.setVisible(False)
        
        advanced_layout = QVBoxLayout()
        
        # Comment field
        comment_group = QGroupBox("Comment")
        comment_layout = QVBoxLayout()
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Enter image description or metadata...")
        self.comment_edit.setMaximumHeight(80)
        comment_layout.addWidget(self.comment_edit)
        comment_group.setLayout(comment_layout)
        advanced_layout.addWidget(comment_group)
        
        self.advanced_content.setLayout(advanced_layout)
        layout.addWidget(self.advanced_content)
        
        widget.setLayout(layout)
        return widget
    
    def _create_buttons(self) -> QHBoxLayout:
        """Create dialog buttons"""
        layout = QHBoxLayout()
        
        self.help_btn = QPushButton("Help")
        self.reset_btn = QPushButton("Reset")
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        
        self.ok_btn.setDefault(True)
        
        layout.addWidget(self.help_btn)
        layout.addWidget(self.reset_btn)
        layout.addStretch()
        layout.addWidget(self.ok_btn)
        layout.addWidget(self.cancel_btn)
        
        return layout
    
    def connect_signals(self):
        """Connect all signal handlers"""
        self.template_combo.currentTextChanged.connect(self.on_template_changed)
        self.width_spin.valueChanged.connect(self.update_pixel_info)
        self.height_spin.valueChanged.connect(self.update_pixel_info)
        self.portrait_btn.toggled.connect(self.on_orientation_changed)
        self.landscape_btn.toggled.connect(self.on_orientation_changed)
        self.advanced_toggle.toggled.connect(self.toggle_advanced_options)
        
        self.ok_btn.clicked.connect(self.on_ok)
        self.cancel_btn.clicked.connect(self.reject)
        self.help_btn.clicked.connect(self.show_help)
        self.reset_btn.clicked.connect(self.load_default_template)
    
    def load_default_template(self):
        """Load the first template as default"""
        if self.template_combo.count() > 0:
            self.template_combo.setCurrentIndex(0)
            self.on_template_changed(self.template_combo.currentText())
    
    def on_template_changed(self, template_name: str):
        """Handle template selection change"""
        if template_name in self.TEMPLATES:
            template = self.TEMPLATES[template_name]
            
            # Block signals to prevent recursion
            self.width_spin.blockSignals(True)
            self.height_spin.blockSignals(True)
            
            self.width_spin.setValue(template["width"])
            self.height_spin.setValue(template["height"])
            
            if "ppi" in template:
                self.x_resolution.setValue(template["ppi"])
                self.y_resolution.setValue(template["ppi"])
            
            # Unblock signals
            self.width_spin.blockSignals(False)
            self.height_spin.blockSignals(False)
            
            # Update orientation buttons
            if template["width"] > template["height"]:
                self.landscape_btn.setChecked(True)
            else:
                self.portrait_btn.setChecked(True)
            
            self.update_pixel_info()
    
    def on_orientation_changed(self, checked: bool):
        """Handle orientation button toggle"""
        if not checked:
            return
        
        # Swap width and height
        current_width = self.width_spin.value()
        current_height = self.height_spin.value()
        
        if current_width != current_height:  # Only swap if not square
            self.width_spin.blockSignals(True)
            self.height_spin.blockSignals(True)
            
            self.width_spin.setValue(current_height)
            self.height_spin.setValue(current_width)
            
            self.width_spin.blockSignals(False)
            self.height_spin.blockSignals(False)
            
            self.update_pixel_info()
    
    def update_pixel_info(self):
        """Update the pixel dimensions display"""
        width = self.width_spin.value()
        height = self.height_spin.value()
        total_pixels = width * height
        
        # Format large numbers with separators
        if total_pixels >= 1_000_000:
            megapixels = total_pixels / 1_000_000
            self.pixel_info.setText(f"{width} × {height} pixels ({megapixels:.1f} MP)")
        else:
            self.pixel_info.setText(f"{width} × {height} pixels")
    
    def toggle_advanced_options(self, checked: bool):
        """Toggle advanced options visibility"""
        self.advanced_content.setVisible(checked)
        
        if checked:
            self.advanced_toggle.setText("▼ Advanced Options")
        else:
            self.advanced_toggle.setText("▶ Advanced Options")
        
        # Adjust dialog size
        self.adjustSize()
    
    def show_help(self):
        """Show help information"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "New Image Help",
            "Create a new image with specified dimensions and properties.\n\n"
            "• Choose from predefined templates or enter custom dimensions\n"
            "• Set resolution (PPI) for print projects\n"
            "• Select color mode (RGB, Grayscale, etc.)\n"
            "• Choose fill color or transparency\n"
            "• Use orientation buttons to quickly swap width/height"
        )
    
    def get_fill_color(self) -> Tuple[int, int, int, int]:
        """Get RGBA fill color based on selection"""
        fill_option = self.fill_combo.currentText()
        
        if fill_option == "White":
            return (255, 255, 255, 255)
        elif fill_option == "Transparency":
            return (0, 0, 0, 0)
        elif fill_option == "Foreground color":
            return (0, 0, 0, 255)  # Black
        elif fill_option == "Background color":
            return (255, 255, 255, 255)  # White
        elif fill_option == "Pattern":
            return (128, 128, 128, 255)  # Gray
        else:
            return (255, 255, 255, 255)
    
    def on_ok(self):
        """Handle OK button click - create the image"""
        width = self.width_spin.value()
        height = self.height_spin.value()
        fill_color = self.get_fill_color()
        
        # Create new canvas
        canva = Canva(shape=(height, width), background=fill_color)
        
        # Emit signal with the new canvas
        self.image_created.emit(canva)
        
        self.accept()
    
    def get_image_properties(self) -> Dict:
        """Get all image properties as a dictionary"""
        return {
            "width": self.width_spin.value(),
            "height": self.height_spin.value(),
            "x_resolution": self.x_resolution.value(),
            "y_resolution": self.y_resolution.value(),
            "resolution_unit": self.resolution_unit.currentText(),
            "color_mode": self.color_mode.currentText(),
            "precision": self.precision.currentText(),
            "gamma": self.gamma.currentText(),
            "fill": self.fill_combo.currentText(),
            "fill_color": self.get_fill_color(),
            "comment": self.comment_edit.toPlainText(),
        }
