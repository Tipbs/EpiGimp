# metadata dialog - shows metadata of the current project
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                               QTreeWidget, QTreeWidgetItem, QPushButton, QWidget,
                               QLabel, QLineEdit, QTextEdit, QComboBox, QFrame)
from PySide6.QtCore import Qt
from typing import Dict, Any
from datetime import datetime


class MetadataDialog(QDialog):
    """Dialog to display and edit image metadata"""
    
    def __init__(self, canva=None, parent=None):
        super().__init__(parent)
        self.canva = canva
        self.metadata = canva.get_metadata() if canva else {}
        
        # Set window title with project name if available
        project_name = "No Title"
        if canva and canva.project_path:
            import os
            project_name = os.path.basename(canva.project_path)
        
        self.setWindowTitle(f"Metadata Viewer - [{project_name}]")
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
        self.tabs.addTab(self._create_basic_tab(), "Basic Info")
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
    
    def _create_basic_tab(self):
        """Create basic info tab with canvas information"""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        
        self.basic_tree = QTreeWidget(self)
        self.basic_tree.setHeaderLabels(["Property", "Value"])
        self.basic_tree.setColumnWidth(0, 300)
        self.basic_tree.setAlternatingRowColors(True)
        
        layout.addWidget(self.basic_tree)
        
        return widget
    
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
        # Load basic canvas info
        basic_data = self._extract_basic_data()
        self._populate_tree(self.basic_tree, basic_data)
        
        # Parse and load EXIF data
        exif_data = self.metadata.get('exif', {})
        self._populate_tree(self.exif_tree, exif_data)
        
        # Parse and load XMP data
        xmp_data = self.metadata.get('xmp', {})
        self._populate_tree(self.xmp_tree, xmp_data)
        
        # Parse and load IPTC data
        iptc_data = self.metadata.get('iptc', {})
        self._populate_tree(self.iptc_tree, iptc_data)
    
    def _extract_basic_data(self) -> Dict[str, Any]:
        """Extract basic canvas information"""
        basic_data = {
            'Canvas.Width': self.metadata.get('width', 'N/A'),
            'Canvas.Height': self.metadata.get('height', 'N/A'),
            'Canvas.Layers': self.metadata.get('layer_count', 0),
            'Canvas.ColorSpace': self.metadata.get('color_space', 'sRGB'),
            'Canvas.BitsPerSample': self.metadata.get('bits_per_sample', '8 8 8'),
            'Resolution.X': f"{self.metadata.get('x_resolution', 72)} {self.metadata.get('resolution_unit', 'inch')}",
            'Resolution.Y': f"{self.metadata.get('y_resolution', 72)} {self.metadata.get('resolution_unit', 'inch')}",
            'DateTime.Created': self.metadata.get('datetime_original', 'N/A'),
            'DateTime.Modified': self.metadata.get('datetime', 'N/A'),
            'File.ProjectPath': self.metadata.get('project_path', 'Not saved'),
        }
        return basic_data
    
    def _populate_tree(self, tree: QTreeWidget, data: Dict[str, Any]):
        """Populate tree widget with metadata"""
        tree.clear()
        
        if not data:
            item = QTreeWidgetItem(tree)
            item.setText(0, "No metadata available")
            item.setText(1, "")
            return
        
        # Group by category (e.g., Exif.Image, Exif.Photo, Canvas, Resolution)
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
    
    def set_canva(self, canva):
        """Update canva and refresh display"""
        self.canva = canva
        self.metadata = canva.get_metadata() if canva else {}
        self.load_metadata()
        
        # Update window title
        project_name = "No Title"
        if canva and canva.project_path:
            import os
            project_name = os.path.basename(canva.project_path)
        self.setWindowTitle(f"Metadata Viewer - [{project_name}]")
    
    def _on_help(self):
        """Show help dialog"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Metadata Help",
            "This dialog displays image metadata in four categories:\n\n"
            "• Basic Info: Canvas dimensions, layers, and resolution\n"
            "• EXIF: Technical camera and image data\n"
            "• XMP: Adobe's Extensible Metadata Platform\n"
            "• IPTC: International Press Telecommunications Council data\n\n"
            "Metadata is organized by category for easy viewing."
        )


class EditableMetadataDialog(QDialog):
    """Extended metadata dialog with editing capabilities - GIMP style"""
    
    def __init__(self, canva=None, parent=None):
        self.canva = canva
        self.metadata = canva.get_metadata() if canva else {}
        
        # Set window title with project name
        project_name = "Sans titre"
        if canva and canva.project_path:
            import os
            project_name = os.path.basename(canva.project_path)
        
        super().__init__(parent)
        self.setWindowTitle(f"Éditeur de métadonnées : [{project_name}]")
        self.setModal(True)
        self.setMinimumSize(650, 550)
        
        self.init_ui()
        self.load_metadata_fields()
    
    def init_ui(self):
        """Initialize the user interface - GIMP style"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Tab widget for different metadata categories
        self.tabs = QTabWidget(self)
        
        # Add tabs with French labels like GIMP
        self.tabs.addTab(self._create_description_tab(), "Description")
        self.tabs.addTab(self._create_iptc_tab(), "IPTC")
        self.tabs.addTab(self._create_iptc_ext_tab(), "Extension IPTC")
        self.tabs.addTab(self._create_categories_tab(), "Catégories")
        self.tabs.addTab(self._create_gps_tab(), "GPS")
        self.tabs.addTab(self._create_dicom_tab(), "DICOM")
        
        layout.addWidget(self.tabs)
        
        # Dropdown selector at bottom
        selector_layout = QHBoxLayout()
        selector_layout.setContentsMargins(10, 5, 10, 5)
        
        self.selector_label = QLabel("Sélectionner :", self)
        self.selector_combo = QComboBox(self)
        self.selector_combo.addItems([
            "Métadonnées par défaut",
            "Métadonnées complètes",
            "Métadonnées essentielles"
        ])
        
        selector_layout.addWidget(self.selector_label)
        selector_layout.addWidget(self.selector_combo)
        selector_layout.addStretch()
        
        layout.addLayout(selector_layout)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 10, 10, 10)
        
        self.help_btn = QPushButton("Help", self)
        self.write_btn = QPushButton("Inscrire les métadonnées", self)
        self.cancel_btn = QPushButton("Annuler", self)
        
        button_layout.addWidget(self.help_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.write_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.help_btn.clicked.connect(self._on_help)
        self.write_btn.clicked.connect(self._on_save)
        self.cancel_btn.clicked.connect(self.reject)
        self.selector_combo.currentIndexChanged.connect(self._on_selector_changed)
    
    def _create_description_tab(self):
        """Create description tab with form fields"""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Create form layout
        from PySide6.QtWidgets import QFormLayout, QScrollArea
        
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(8)
        
        # Document title
        self.title_edit = QLineEdit(self)
        form_layout.addRow("Titre du document", self.title_edit)
        
        # Author
        self.author_edit = QLineEdit(self)
        form_layout.addRow("Auteur", self.author_edit)
        
        # Author title
        self.author_title_edit = QLineEdit(self)
        form_layout.addRow("Titre de l'auteur", self.author_title_edit)
        
        # Description
        self.description_edit = QTextEdit(self)
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("Description", self.description_edit)
        
        # Description writer
        self.description_writer_edit = QTextEdit(self)
        self.description_writer_edit.setMaximumHeight(80)
        form_layout.addRow("Description Writer", self.description_writer_edit)
        
        # Rating
        rating_layout = QHBoxLayout()
        self.rating_combo = QComboBox(self)
        self.rating_combo.addItems(["Non noté", "1 étoile", "2 étoiles", "3 étoiles", "4 étoiles", "5 étoiles"])
        rating_layout.addWidget(self.rating_combo)
        rating_layout.addStretch()
        form_layout.addRow("Note", rating_layout)
        
        # Keywords
        self.keywords_edit = QTextEdit(self)
        self.keywords_edit.setMaximumHeight(80)
        form_layout.addRow("Mots-clés", self.keywords_edit)
        
        # Copyright
        self.copyright_edit = QLineEdit(self)
        form_layout.addRow("Copyright", self.copyright_edit)
        
        # Copyright URL
        self.copyright_url_edit = QLineEdit(self)
        form_layout.addRow("URL du copyright", self.copyright_url_edit)
        
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        return widget
    
    def _create_iptc_tab(self):
        """Create IPTC tab"""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        from PySide6.QtWidgets import QFormLayout, QScrollArea
        
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        # Creator
        self.iptc_creator_edit = QLineEdit(self)
        form_layout.addRow("Créateur", self.iptc_creator_edit)
        
        # Creator job title
        self.iptc_creator_job_edit = QLineEdit(self)
        form_layout.addRow("Fonction du créateur", self.iptc_creator_job_edit)
        
        # Credit
        self.iptc_credit_edit = QLineEdit(self)
        form_layout.addRow("Crédit", self.iptc_credit_edit)
        
        # Source
        self.iptc_source_edit = QLineEdit(self)
        form_layout.addRow("Source", self.iptc_source_edit)
        
        # Usage terms
        self.iptc_usage_edit = QTextEdit(self)
        self.iptc_usage_edit.setMaximumHeight(60)
        form_layout.addRow("Conditions d'utilisation", self.iptc_usage_edit)
        
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        return widget
    
    def _create_iptc_ext_tab(self):
        """Create IPTC Extension tab"""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        
        info_label = QLabel("IPTC Extension metadata fields", self)
        info_label.setStyleSheet("color: #666; padding: 10px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        return widget
    
    def _create_categories_tab(self):
        """Create categories tab"""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        
        info_label = QLabel("Categories for image classification", self)
        info_label.setStyleSheet("color: #666; padding: 10px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        return widget
    
    def _create_gps_tab(self):
        """Create GPS tab"""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        from PySide6.QtWidgets import QFormLayout
        
        form_layout = QFormLayout()
        
        # Latitude
        self.gps_lat_edit = QLineEdit(self)
        form_layout.addRow("Latitude", self.gps_lat_edit)
        
        # Longitude
        self.gps_lon_edit = QLineEdit(self)
        form_layout.addRow("Longitude", self.gps_lon_edit)
        
        # Altitude
        self.gps_alt_edit = QLineEdit(self)
        form_layout.addRow("Altitude", self.gps_alt_edit)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        return widget
    
    def _create_dicom_tab(self):
        """Create DICOM tab"""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        
        info_label = QLabel("DICOM medical imaging metadata", self)
        info_label.setStyleSheet("color: #666; padding: 10px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        return widget
    
    def load_metadata_fields(self):
        """Load metadata into form fields"""
        # Description tab
        self.title_edit.setText(self.metadata.get('title', ''))
        self.author_edit.setText(self.metadata.get('author', ''))
        self.author_title_edit.setText(self.metadata.get('author_title', ''))
        self.description_edit.setPlainText(self.metadata.get('description', ''))
        self.description_writer_edit.setPlainText(self.metadata.get('description_writer', ''))
        self.keywords_edit.setPlainText(self.metadata.get('keywords', ''))
        self.copyright_edit.setText(self.metadata.get('copyright', ''))
        self.copyright_url_edit.setText(self.metadata.get('copyright_url', ''))
        
        # Rating
        rating = self.metadata.get('rating', 0)
        self.rating_combo.setCurrentIndex(rating)
        
        # IPTC tab
        iptc = self.metadata.get('iptc', {})
        self.iptc_creator_edit.setText(str(iptc.get('Iptc.Application2.Byline', '')))
        self.iptc_creator_job_edit.setText(str(iptc.get('Iptc.Application2.BylineTitle', '')))
        self.iptc_credit_edit.setText(str(iptc.get('Iptc.Application2.Credit', '')))
        self.iptc_source_edit.setText(str(iptc.get('Iptc.Application2.Source', '')))
        
        # GPS
        exif = self.metadata.get('exif', {})
        self.gps_lat_edit.setText(str(exif.get('Exif.GPSInfo.GPSLatitude', '')))
        self.gps_lon_edit.setText(str(exif.get('Exif.GPSInfo.GPSLongitude', '')))
        self.gps_alt_edit.setText(str(exif.get('Exif.GPSInfo.GPSAltitude', '')))
    
    def _on_save(self):
        """Save edited metadata back to canva"""
        if not self.canva:
            self.reject()
            return
        
        # Collect data from form fields
        updated_metadata = {
            'title': self.title_edit.text(),
            'author': self.author_edit.text(),
            'author_title': self.author_title_edit.text(),
            'description': self.description_edit.toPlainText(),
            'description_writer': self.description_writer_edit.toPlainText(),
            'keywords': self.keywords_edit.toPlainText(),
            'copyright': self.copyright_edit.text(),
            'copyright_url': self.copyright_url_edit.text(),
            'rating': self.rating_combo.currentIndex(),
            'iptc': {
                'Iptc.Application2.Byline': self.iptc_creator_edit.text(),
                'Iptc.Application2.BylineTitle': self.iptc_creator_job_edit.text(),
                'Iptc.Application2.Credit': self.iptc_credit_edit.text(),
                'Iptc.Application2.Source': self.iptc_source_edit.text(),
            },
            'exif': {}
        }
        
        # Add GPS data if provided
        if self.gps_lat_edit.text():
            updated_metadata['exif']['Exif.GPSInfo.GPSLatitude'] = self.gps_lat_edit.text()
        if self.gps_lon_edit.text():
            updated_metadata['exif']['Exif.GPSInfo.GPSLongitude'] = self.gps_lon_edit.text()
        if self.gps_alt_edit.text():
            updated_metadata['exif']['Exif.GPSInfo.GPSAltitude'] = self.gps_alt_edit.text()
        
        self.canva.set_metadata(updated_metadata)
        self.canva.update_metadata_datetime()
        
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Métadonnées enregistrées",
            "Les métadonnées ont été mises à jour avec succès.\n\n"
            "Note : Les modifications seront sauvegardées lors de l'enregistrement du projet."
        )
        
        self.accept()
    
    def _on_selector_changed(self, index):
        pass
    
    def _on_help(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Aide - Métadonnées",
            "L'éditeur de métadonnées vous permet de modifier les informations intégrées dans votre image.\n\n"
            "• Description : Informations générales sur l'image\n"
            "• IPTC : Métadonnées pour la presse et les médias\n"
            "• Extension IPTC : Champs IPTC supplémentaires\n"
            "• Catégories : Classification de l'image\n"
            "• GPS : Coordonnées de géolocalisation\n"
            "• DICOM : Métadonnées médicales\n\n"
            "Cliquez sur 'Inscrire les métadonnées' pour enregistrer les modifications."
        )
    
    def get_canva(self):
        """Get the canva with updated metadata"""
        return self.canva