from PySide6.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
                               QTreeWidget, QTreeWidgetItem, QComboBox, 
                               QLineEdit, QLabel, QPushButton, QSplitter,
                               QApplication, QHeaderView)
from PySide6.QtCore import Qt, QDir, QFileInfo
import os
from EpiGimp.core.fileio.file_exporter import FileExporter
from EpiGimp.core.canva import Canva

class ExportWidget(QDialog):
    def __init__(self, parent=None, filename: str = "untitled"):
        super().__init__(parent)
        self.current_folder = QDir.homePath()
        self.setup_size()
        self.setWindowTitle('Exporter l\'image')
        self.setup_ui()
        self.populate_folders()
        
    def setup_size(self):
        screen = QApplication.primaryScreen().availableGeometry()
        width = min(1200, int(screen.width() * 0.8))
        height = min(800, int(screen.height() * 0.8))
        self.resize(width, height)
        
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.move(x, y)
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit("untitled.png")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        splitter = QSplitter(Qt.Horizontal)
        
        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabel("Folders")
        self.folder_tree.itemClicked.connect(self.on_folder_selected)
        self.folder_tree.itemExpanded.connect(self.on_folder_expanded)
        splitter.addWidget(self.folder_tree)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.path_label = QLabel(self.current_folder)
        self.path_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc; }")
        right_layout.addWidget(self.path_label)
        
        self.file_list = QTreeWidget()
        self.file_list.setHeaderLabels(["Name", "Type", "Size"])
        self.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.file_list.setRootIsDecorated(False)
        
        header = self.file_list.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        right_layout.addWidget(self.file_list)
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("File type:"))
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems([
            "From Extension",
            "JPEG Image (*.jpg)",
            "PNG Image (*.png)", 
            "BMP Image (*.bmp)",
            "TIFF Image (*.tiff)",
            "GIF Image (*.gif)"
        ])
        type_layout.addWidget(self.file_type_combo)
        type_layout.addStretch()
        right_layout.addLayout(type_layout)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        help_btn = QPushButton("Help")
        export_btn = QPushButton("Export")
        cancel_btn = QPushButton("Cancel")
        
        export_btn.clicked.connect(self.accept_export)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(help_btn)
        button_layout.addWidget(export_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def populate_folders(self):
        self.folder_tree.clear()
        
        home_dir = QDir.homePath()

        personal_item = QTreeWidgetItem(["Personal Folder"])
        personal_item.setData(0, Qt.UserRole, home_dir)
        self.add_placeholder_child(personal_item)
        self.folder_tree.addTopLevelItem(personal_item)
        
        other_item = QTreeWidgetItem(["Other Locations"])
        self.folder_tree.addTopLevelItem(other_item)
        
        drives = QDir.drives()
        for drive in drives:
            drive_path = drive.absolutePath()
            drive_name = f"Drive {drive_path}"
            drive_item = QTreeWidgetItem([drive_name])
            drive_item.setData(0, Qt.UserRole, drive_path)
            self.add_placeholder_child(drive_item)
            other_item.addChild(drive_item)
        
        personal_item.setExpanded(True)
        personal_item.setSelected(True)
        self.on_folder_selected(personal_item, 0)
    
    def add_placeholder_child(self, parent_item):
        placeholder = QTreeWidgetItem(["Loading..."])
        placeholder.setData(0, Qt.UserRole, "PLACEHOLDER")
        parent_item.addChild(placeholder)
    
    def on_folder_expanded(self, item):
        if item.childCount() == 1:
            child = item.child(0)
            if child.data(0, Qt.UserRole) == "PLACEHOLDER":
                item.removeChild(child)
                self.load_subfolders(item)
    
    def load_subfolders(self, parent_item):
        folder_path = parent_item.data(0, Qt.UserRole)
        if not folder_path or folder_path == "PLACEHOLDER":
            return
            
        try:
            dir_obj = QDir(folder_path)
            dir_obj.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)
            for folder_name in dir_obj.entryList():
                subfolder_path = os.path.join(folder_path, folder_name)
                folder_item = QTreeWidgetItem([folder_name])
                folder_item.setData(0, Qt.UserRole, subfolder_path)
                if self.has_subfolders(subfolder_path):
                    self.add_placeholder_child(folder_item)
                parent_item.addChild(folder_item)
        except PermissionError:
            no_access_item = QTreeWidgetItem(["Access Denied"])
            no_access_item.setData(0, Qt.UserRole, "NO_ACCESS")
            parent_item.addChild(no_access_item)
    
    def has_subfolders(self, folder_path):
        try:
            dir_obj = QDir(folder_path)
            dir_obj.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)
            return len(dir_obj.entryList()) > 0
        except:
            return False
        
    def on_folder_selected(self, item, column):
        folder_path = item.data(0, Qt.UserRole)
        if folder_path and folder_path not in ["PLACEHOLDER", "NO_ACCESS"]:
            if os.path.exists(folder_path):
                self.current_folder = folder_path
                self.path_label.setText(folder_path)
                self.populate_files(folder_path)
    
    def populate_files(self, folder_path):
        self.file_list.clear()
        try:
            dir_obj = QDir(folder_path)
            dir_obj.setFilter(QDir.Files)
            
            for filename in dir_obj.entryList():
                file_path = os.path.join(folder_path, filename)
                file_info = QFileInfo(file_path)
                
                name = filename
                file_type = file_info.suffix().upper() if file_info.suffix() else "File"
                size = self.format_file_size(file_info.size())
                
                item = QTreeWidgetItem([name, file_type, size])
                item.setData(0, Qt.UserRole, file_path)
                self.file_list.addTopLevelItem(item)
        except PermissionError:
            item = QTreeWidgetItem(["Access Denied - Cannot read folder contents", "", ""])
            item.setFlags(Qt.NoItemFlags)
            self.file_list.addTopLevelItem(item)
    
    def format_file_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        size_index = 0
        size = float(size_bytes)
        while size >= 1024.0 and size_index < len(size_names) - 1:
            size /= 1024.0
            size_index += 1
        if size_index == 0:
            return f"{int(size)} {size_names[size_index]}"
        else:
            return f"{size:.1f} {size_names[size_index]}"
    
    def on_file_double_clicked(self, item, column):
        filename = item.text(0)
        if filename != "Access Denied - Cannot read folder contents":
            self.name_input.setText(filename)
    
    def accept_export(self):
        filename = self.name_input.text()
        if not filename:
            return
            
        if self.current_folder:
            full_path = os.path.join(self.current_folder, filename)
            self.selected_path = full_path
            self.accept()
    
    def get_selected_path(self):
        return getattr(self, 'selected_path', None)

    def export_image(self, canva: Canva):
        if self.exec() == QDialog.Accepted:
            path = self.get_selected_path()
            if path:
                image_data = canva.composite()
                exporter = FileExporter(path, image_data)
                exporter.export()
                return True
        return False
