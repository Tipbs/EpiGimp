# metadata dialog - shows metadata of the current project
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                               QTreeWidget, QTreeWidgetItem, QPushButton, QWidget,
                               QLabel, QLineEdit, QTextEdit, QComboBox)
from PySide6.QtCore import Qt
from typing import Dict, Any
from datetime import datetime


class MetadataDialog(QDialog):
    """Dialog to display and edit image metadata"""
    
    def __init__(self, image_metadata=None, parent=None):
        super().__init__(parent)
        self.metadata = image_metadata or {}
        self.setWindowTitle("Metadata Viewer - [No Title]")
        self.setMinimumSize(650, 600)
        self.setModal(True)
        
        self.init_ui()
        self.load_metadata()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Tab widget for different metadata categories
        self.tabs = QTabWidget(self)
        
        # Add tabs
        self.tabs.addTab(self._create_exif_tab(), "Exif")
        self.tabs.addTab(self._create_xmp_tab(), "XMP")
        self.tabs.addTab(self._create_iptc_tab(), "IPTC")
        
        layout.addWidget(self.tabs)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.help_btn = QPushButton("Help", self)
        self.close_btn = QPushButton("Close", self)
        
        button_layout.addWidget(self.help_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.help_btn.clicked.connect(self._on_help)
        self.close_btn.clicked.connect(self.accept)
    
    def _create_exif_tab(self):
        """Create EXIF metadata tab"""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        
        self.exif_tree = QTreeWidget(self)
        self.exif_tree.setHeaderLabels(["Property", "Value"])
        self.exif_tree.setColumnWidth(0, 300)
        self.exif_tree.setAlternatingRowColors(True)
        
        layout.addWidget(self.exif_tree)
        
        return widget
    
    def _create_xmp_tab(self):
        """Create XMP metadata tab"""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        
        self.xmp_tree = QTreeWidget(self)
        self.xmp_tree.setHeaderLabels(["Property", "Value"])
        self.xmp_tree.setColumnWidth(0, 300)
        self.xmp_tree.setAlternatingRowColors(True)
        
        layout.addWidget(self.xmp_tree)
        
        return widget
    
    def _create_iptc_tab(self):
        """Create IPTC metadata tab"""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        
        self.iptc_tree = QTreeWidget(self)
        self.iptc_tree.setHeaderLabels(["Property", "Value"])
        self.iptc_tree.setColumnWidth(0, 300)
        self.iptc_tree.setAlternatingRowColors(True)
        
        layout.addWidget(self.iptc_tree)
        
        return widget
    
    def load_metadata(self):
        """Load metadata into the trees"""
        # Parse and load EXIF data
        exif_data = self._extract_exif_data()
        self._populate_tree(self.exif_tree, exif_data)
        
        # Parse and load XMP data
        xmp_data = self._extract_xmp_data()
        self._populate_tree(self.xmp_tree, xmp_data)
        
        # Parse and load IPTC data
        iptc_data = self._extract_iptc_data()
        self._populate_tree(self.iptc_tree, iptc_data)
    
    def _extract_exif_data(self) -> Dict[str, Any]:
        """Extract EXIF metadata from image"""
        exif_data = {}
        
        # Check for EXIF data in metadata
        if 'exif' in self.metadata:
            exif_data = self.metadata['exif']
        else:
            # Create default EXIF categories
            exif_data = {
                'Exif.Image.BitsPerSample': self.metadata.get('bits_per_sample', '8 8 8'),
                'Exif.Image.DateTime': self.metadata.get('datetime', datetime.now().strftime('%Y:%m:%d %H:%M:%S')),
                'Exif.Image.DateTimeOriginal': self.metadata.get('datetime_original', datetime.now().strftime('%Y:%m:%d %H:%M:%S')),
                'Exif.Image.ImageLength': self.metadata.get('height', 1080),
                'Exif.Image.ImageWidth': self.metadata.get('width', 1920),
                'Exif.Image.ResolutionUnit': self.metadata.get('resolution_unit', 'inch'),
                'Exif.Image.XResolution': self.metadata.get('x_resolution', 300),
                'Exif.Image.YResolution': self.metadata.get('y_resolution', 300),
                'Exif.Photo.ColorSpace': self.metadata.get('color_space', 'sRGB'),
                'Exif.Photo.DateTimeDigitized': self.metadata.get('datetime_digitized', datetime.now().strftime('%Y:%m:%d %H:%M:%S')),
                'Exif.Photo.DateTimeOriginal': self.metadata.get('datetime_original', datetime.now().strftime('%Y:%m:%d %H:%M:%S')),
                'Exif.Photo.OffsetTime': self.metadata.get('offset_time', '+01:00'),
                'Exif.Photo.OffsetTimeDigitized': self.metadata.get('offset_time_digitized', '+01:00'),
                'Exif.Photo.OffsetTimeOriginal': self.metadata.get('offset_time_original', '+01:00'),
            }
        
        return exif_data
    
    def _extract_xmp_data(self) -> Dict[str, Any]:
        """Extract XMP metadata"""
        if 'xmp' in self.metadata:
            return self.metadata['xmp']
        return {}
    
    def _extract_iptc_data(self) -> Dict[str, Any]:
        """Extract IPTC metadata"""
        if 'iptc' in self.metadata:
            return self.metadata['iptc']
        return {}
    
    def _populate_tree(self, tree: QTreeWidget, data: Dict[str, Any]):
        """Populate tree widget with metadata"""
        tree.clear()
        
        # Group by category (e.g., Exif.Image, Exif.Photo)
        categories = {}
        for key, value in data.items():
            parts = key.split('.')
            if len(parts) >= 2:
                category = '.'.join(parts[:-1])
                property_name = parts[-1]
            else:
                category = "Other"
                property_name = key
            
            if category not in categories:
                categories[category] = {}
            categories[category][property_name] = value
        
        # Add to tree
        for category, properties in sorted(categories.items()):
            category_item = QTreeWidgetItem(tree)
            category_item.setText(0, category)
            category_item.setExpanded(True)
            
            # Set category item appearance
            font = category_item.font(0)
            font.setBold(True)
            category_item.setFont(0, font)
            
            for prop_name, prop_value in sorted(properties.items()):
                prop_item = QTreeWidgetItem(category_item)
                prop_item.setText(0, prop_name)
                prop_item.setText(1, str(prop_value))
        
        tree.expandAll()
    
    def set_metadata(self, metadata: Dict[str, Any]):
        """Update metadata and refresh display"""
        self.metadata = metadata
        self.load_metadata()
    
    def _on_help(self):
        """Show help dialog"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Metadata Help",
            "This dialog displays image metadata in three formats:\n\n"
            "• EXIF: Technical camera and image data\n"
            "• XMP: Adobe's Extensible Metadata Platform\n"
            "• IPTC: International Press Telecommunications Council data\n\n"
            "Metadata is organized by category for easy viewing."
        )


class EditableMetadataDialog(MetadataDialog):
    """Extended metadata dialog with editing capabilities"""
    
    def __init__(self, image_metadata=None, parent=None):
        super().__init__(image_metadata, parent)
        self.setWindowTitle("Edit Metadata - [No Title]")
        
        # Add save/cancel buttons
        self._add_edit_buttons()
    
    def _add_edit_buttons(self):
        """Add save and cancel buttons for editing"""
        layout = self.layout()
        button_layout = layout.itemAt(layout.count() - 1)
        
        # Remove close button temporarily
        close_btn = button_layout.itemAt(2).widget()
        button_layout.removeWidget(close_btn)
        
        # Add save and cancel buttons
        self.save_btn = QPushButton("Save", self)
        self.cancel_btn = QPushButton("Cancel", self)
        
        button_layout.insertWidget(2, self.save_btn)
        button_layout.insertWidget(3, self.cancel_btn)
        
        # Connect new buttons
        self.save_btn.clicked.connect(self._on_save)
        self.cancel_btn.clicked.connect(self.reject)
        
        # Make trees editable
        self.exif_tree.setEditTriggers(QTreeWidget.EditTrigger.DoubleClicked)
        self.xmp_tree.setEditTriggers(QTreeWidget.EditTrigger.DoubleClicked)
        self.iptc_tree.setEditTriggers(QTreeWidget.EditTrigger.DoubleClicked)
    
    def _on_save(self):
        """Save edited metadata"""
        # Collect edited data from trees
        self.metadata['exif'] = self._collect_tree_data(self.exif_tree)
        self.metadata['xmp'] = self._collect_tree_data(self.xmp_tree)
        self.metadata['iptc'] = self._collect_tree_data(self.iptc_tree)
        
        self.accept()
    
    def _collect_tree_data(self, tree: QTreeWidget) -> Dict[str, Any]:
        """Collect data from tree widget"""
        data = {}
        
        root = tree.invisibleRootItem()
        for i in range(root.childCount()):
            category_item = root.child(i)
            category = category_item.text(0)
            
            for j in range(category_item.childCount()):
                prop_item = category_item.child(j)
                prop_name = prop_item.text(0)
                prop_value = prop_item.text(1)
                
                full_key = f"{category}.{prop_name}"
                data[full_key] = prop_value
        
        return data
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get the edited metadata"""
        return self.metadata