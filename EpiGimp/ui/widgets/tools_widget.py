from PySide6.QtWidgets import (QWidget, QGridLayout, QToolButton, 
                             QButtonGroup, QVBoxLayout, QLabel, QFrame)
from PySide6.QtCore import Qt, Signal

from EpiGimp.tools.base_tool import ToolNotImplemented
from EpiGimp.tools.brush import Brush
from EpiGimp.tools.eraser import Eraser
from EpiGimp.tools.selection import RectangleSelection, EllipseSelection
from EpiGimp.tools.move import Move

class ToolsWidget(QWidget):
    """
    The Main Toolbox (Left Panel in GIMP).
    Emits 'toolSelected(str)' when a user clicks a tool.
    """
    toolSelected = Signal(ToolNotImplemented) # e.g., emits "brush", "eraser", "move"

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(10)

        # 1. The Tool Grid
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        
        # We use a button group to ensure only ONE tool is active at a time
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        self.btn_group.idClicked.connect(self._on_tool_clicked)

        # 2. Add Standard Tools
        # Format: (Tool Instance, Row, Col)
        self.brush = Brush()
        self.eraser = Eraser()
        self.rect_select = RectangleSelection()
        self.ellipse_select = EllipseSelection()
        self.move = Move()
        
        tools_config = [
            (self.rect_select, 0, 0),
            (self.ellipse_select, 0, 1),
            (self.move, 1, 0),
            (self.brush, 1, 1),
            (self.eraser, 2, 0),
            (ToolNotImplemented(), 2, 1),
            (ToolNotImplemented(), 3, 0),
            (ToolNotImplemented(), 3, 1),
        ]

            # ("move",    "Move Tool",      0, 0),
            # ("select",  "Rect Select",    0, 1),
            # ("brush",   "Paintbrush",     1, 0),
            # ("pencil",  "Pencil",         1, 1),
            # ("eraser",  "Eraser",         2, 0),
            # ("fill",    "Bucket Fill",    2, 1),
            # ("text",    "Text Tool",      3, 0),
            # ("picker",  "Color Picker",   3, 1),
        for tool, r, c in tools_config:
            btn = self._create_tool_button(tool)
            self.grid_layout.addWidget(btn, r, c)
            self.btn_group.addButton(btn)
            
            # Set default tool to Brush
            if tool.name == "Brush":
                btn.setChecked(True)

        self.main_layout.addLayout(self.grid_layout)
        self.main_layout.addStretch() # Push everything up

        # 3. (Optional) Foreground/Background Color Swatches
        # GIMP always has this at the bottom of the tools
        self._add_color_swatches()

    def _create_tool_button(self, tool):
        """Helper to create a standardized GIMP-like button"""
        btn = QToolButton()
        btn.setCheckable(True)
        btn.setFixedSize(30, 30)
        btn.setToolTip(tool.tooltip)
        
        # Store the tool ID in the button itself for easy retrieval
        btn.setProperty("tool", tool) 
        
        # Styling to make it look flat and highlight when selected
        btn.setStyleSheet("""
            QToolButton { border: 1px solid transparent; border-radius: 3px; background: #444; color: white; }
            QToolButton:hover { background: #555; border: 1px solid #666; }
            QToolButton:checked { background: #666; border: 1px solid #888; }
            QToolButton:pressed { background: #333; }
        """)
        
        # Placeholder Icon (Replace with QIcon("path/to/icon.png"))
        # Using text for now so it runs without assets
        btn.setText(tool.name[0].upper()) 
        
        return btn

    def _on_tool_clicked(self, btn_id):
        """Handle the signal emission"""
        btn = self.btn_group.button(btn_id)
        if btn:
            tool = btn.property("tool")
            self.toolSelected.emit(tool)

    def _add_color_swatches(self):
        """Adds the FG/BG color squares typical of GIMP"""
        container = QFrame()
        container.setFixedSize(50, 50)
        
        # Background Color (Bottom Right)
        self.bg_color = QLabel(container)
        self.bg_color.setStyleSheet("background-color: white; border: 1px solid gray;")
        self.bg_color.setGeometry(20, 20, 30, 30) # x, y, w, h
        
        # Foreground Color (Top Left)
        self.fg_color = QLabel(container)
        self.fg_color.setStyleSheet("background-color: black; border: 1px solid gray;")
        self.fg_color.setGeometry(0, 0, 30, 30)

        self.main_layout.addWidget(container, 0, Qt.AlignCenter)

    def get_current_tool(self):
        """Public method to ask 'What tool is active?'"""
        current_btn = self.btn_group.checkedButton()
        if current_btn:
            return current_btn.property("tool")
        return ToolNotImplemented()
