from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, 
                             QListWidget, QListWidgetItem, QPushButton, QFrame, QAbstractItemView)
from PySide6.QtCore import Signal
from EpiGimp.ui.widgets.layer_item_widget import LayerItemWidget
from EpiGimp.core.canva import Canva

# class LayersWidget(QWidget):
#     def __init__(self, canva, parent=None):
#         super().__init__(parent)
#         layout = QHBoxLayout(self)
#         layout.setContentsMargins(5, 2, 5, 2)
#         layout.setSpacing(10)
#
#         layout.addWidget(LayersStackWidget(canva))

class LayersWidget(QFrame):
    layerSelected = Signal(int) # Emits index of selected layer

    def __init__(self, canva=None, parent=None):
        super().__init__(parent)
        self.canva: None | Canva = canva
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Plain)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # The List Container
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove) # Allows reordering
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.setStyleSheet("QListWidget::item { border-bottom: 1px solid #333; }")

        # Bottom Toolbar (Add/Delete/Move)
        self.toolbar = QHBoxLayout()
        self.btn_add = QPushButton("+")
        self.btn_del = QPushButton("-")
        self.toolbar.addWidget(self.btn_add)
        self.toolbar.addWidget(self.btn_del)
        self.toolbar.addStretch()

        self.main_layout.addWidget(self.list_widget)
        self.main_layout.addLayout(self.toolbar)

        # Internal Connections
        self.btn_add.clicked.connect(lambda: self.add_layer("New Layer"))
        self.btn_del.clicked.connect(self.remove_current_layer)
        self.list_widget.currentRowChanged.connect(self.layerSelected.emit)

    def set_canva(self, canva: Canva):
        self.canva = canva

    def add_layer(self, name, thumbnail=None):
        """Public method to add a layer from your external Canvas logic"""
        if self.canva is None:
            return
        self.canva.add_layer()
        item = QListWidgetItem(self.list_widget)
        custom_widget = LayerItemWidget(name, thumbnail)
        
        # Ensure the list item is large enough for our custom widget
        item.setSizeHint(custom_widget.sizeHint())
        
        self.list_widget.insertItem(0, item) # GIMP adds to top
        self.list_widget.setItemWidget(item, custom_widget)
        self.list_widget.setCurrentItem(item)

    def remove_current_layer(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            self.list_widget.takeItem(current_row)
