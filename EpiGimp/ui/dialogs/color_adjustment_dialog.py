from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QSlider, QSpinBox, QCheckBox,
                               QComboBox, QGroupBox, QWidget)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap, QImage
import numpy as np


class ColorTemperatureDialog(QDialog):
    temperature_changed = Signal(float, float, float)
    
    def __init__(self, parent=None, canva_widget=None):
        super().__init__(parent)
        self.canva_widget = canva_widget
        self.original_temp = 6500.0
        self.target_temp = 6500.0
        self.original_pixels = None
        
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._do_update_preview)
        
        if self.canva_widget:
            canva = self.canva_widget.canva
            active_layer = canva.get_img()
            if active_layer:
                self.original_pixels = active_layer.pixels.copy()
        
        self.setWindowTitle("Température de couleur")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        header_layout = QHBoxLayout()
        icon_label = QLabel("🌡️", self)
        icon_label.setStyleSheet("font-size: 24px;")
        title_label = QLabel("Température de couleur", self)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        if self.canva_widget:
            from PySide6.QtGui import QPixmap
            composite = self.canva_widget.canva.composite()
            h, w = composite.shape[:2]
            bytes_per_line = 4 * w
            q_image = QImage(composite.data, w, h, bytes_per_line, QImage.Format.Format_RGBA8888)
            preview_label = QLabel(self)
            preview_label.setPixmap(QPixmap.fromImage(q_image).scaled(
                100, 100, Qt.AspectRatioMode.KeepAspectRatio
            ))
            header_layout.addWidget(preview_label)
        
        layout.addLayout(header_layout)
        
        presets_layout = QHBoxLayout()
        presets_label = QLabel("Préréglages :", self)
        self.presets_combo = QComboBox(self)
        self.presets_combo.addItems([
            "Personnalisé",
            "Lumière du jour (5500K)",
            "Néon (4000K)", 
            "Tungstène (3200K)",
            "Bougie (1850K)"
        ])
        self.presets_combo.currentIndexChanged.connect(self._on_preset_changed)
        
        add_preset_btn = QPushButton("+", self)
        add_preset_btn.setMaximumWidth(30)
        add_preset_btn.setToolTip("Ajouter un préréglage")
        
        remove_preset_btn = QPushButton("-", self)
        remove_preset_btn.setMaximumWidth(30)
        remove_preset_btn.setToolTip("Supprimer le préréglage")
        
        presets_layout.addWidget(presets_label)
        presets_layout.addWidget(self.presets_combo, 1)
        presets_layout.addWidget(add_preset_btn)
        presets_layout.addWidget(remove_preset_btn)
        
        layout.addLayout(presets_layout)
        
        from PySide6.QtWidgets import QDoubleSpinBox
        
        original_group = QGroupBox("Température originale", self)
        original_layout = QHBoxLayout(original_group)
        
        self.original_spinbox = QDoubleSpinBox(self)
        self.original_spinbox.setRange(1000, 15000)
        self.original_spinbox.setValue(6500.0)
        self.original_spinbox.setSuffix(" K")
        self.original_spinbox.setSingleStep(100)
        self.original_spinbox.valueChanged.connect(self._on_original_changed)
        
        original_slider = QSlider(Qt.Orientation.Horizontal, self)
        original_slider.setRange(1000, 15000)
        original_slider.setValue(6500)
        original_slider.setSingleStep(100)
        original_slider.valueChanged.connect(self.original_spinbox.setValue)
        self.original_spinbox.valueChanged.connect(original_slider.setValue)
        
        original_layout.addWidget(self.original_spinbox)
        original_layout.addWidget(original_slider, 1)
        
        info_label = QLabel("Température en Kelvins estimée de la source de lumière lors de la prise de vue.", self)
        info_label.setStyleSheet("color: #888; font-size: 10px; padding: 5px;")
        info_label.setWordWrap(True)
        
        target_group = QGroupBox("Température souhaitée", self)
        target_layout = QHBoxLayout(target_group)
        
        self.target_spinbox = QDoubleSpinBox(self)
        self.target_spinbox.setRange(1000, 15000)
        self.target_spinbox.setValue(6500.0)
        self.target_spinbox.setSuffix(" K")
        self.target_spinbox.setSingleStep(100)
        self.target_spinbox.valueChanged.connect(self._on_target_changed)
        
        target_slider = QSlider(Qt.Orientation.Horizontal, self)
        target_slider.setRange(1000, 15000)
        target_slider.setValue(6500)
        target_slider.setSingleStep(100)
        target_slider.valueChanged.connect(self.target_spinbox.setValue)
        self.target_spinbox.valueChanged.connect(target_slider.setValue)
        
        target_layout.addWidget(self.target_spinbox)
        target_layout.addWidget(target_slider, 1)
        
        layout.addWidget(original_group)
        layout.addWidget(info_label)
        layout.addWidget(target_group)
        
        options_group = QGroupBox("Options de dégradé", self)
        options_layout = QVBoxLayout(options_group)
        
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Mode", self)
        self.mode_combo = QComboBox(self)
        self.mode_combo.addItems([
            "Remplacer",
            "Multiplier", 
            "Diviser",
            "Écran",
            "Superposer"
        ])
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo, 1)
        
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("Opacité", self)
        self.opacity_spinbox = QDoubleSpinBox(self)
        self.opacity_spinbox.setRange(0, 100)
        self.opacity_spinbox.setValue(100.0)
        self.opacity_spinbox.setSingleStep(1)
        self.opacity_spinbox.valueChanged.connect(self._on_opacity_changed)
        
        opacity_slider = QSlider(Qt.Orientation.Horizontal, self)
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(100)
        opacity_slider.valueChanged.connect(self.opacity_spinbox.setValue)
        self.opacity_spinbox.valueChanged.connect(opacity_slider.setValue)
        
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.opacity_spinbox)
        opacity_layout.addWidget(opacity_slider, 1)
        
        options_layout.addLayout(mode_layout)
        options_layout.addLayout(opacity_layout)
        
        layout.addWidget(options_group)
        
        preview_layout = QHBoxLayout()
        self.preview_checkbox = QCheckBox("Aperçu", self)
        self.preview_checkbox.setChecked(True)
        self.preview_checkbox.stateChanged.connect(self._on_preview_toggled)
        
        self.merge_checkbox = QCheckBox("Merge filter", self)
        self.split_view_checkbox = QCheckBox("Diviser la vue", self)
        
        preview_layout.addWidget(self.preview_checkbox)
        preview_layout.addWidget(self.merge_checkbox)
        preview_layout.addWidget(self.split_view_checkbox)
        preview_layout.addStretch()
        
        layout.addLayout(preview_layout)
        
        layout.addStretch()
        
        button_layout = QHBoxLayout()
        
        self.help_btn = QPushButton("Help", self)
        self.reset_btn = QPushButton("Réinitialiser", self)
        self.validate_btn = QPushButton("Valider", self)
        self.cancel_btn = QPushButton("Annuler", self)
        
        button_layout.addWidget(self.help_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.validate_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.help_btn.clicked.connect(self._on_help)
        self.reset_btn.clicked.connect(self._on_reset)
        self.validate_btn.clicked.connect(self._on_accept)
        self.cancel_btn.clicked.connect(self._on_cancel)
    
    def _on_preset_changed(self, index):
        presets = {
            0: None,
            1: 5500.0,
            2: 4000.0,
            3: 3200.0,
            4: 1850.0
        }
        
        if index in presets and presets[index] is not None:
            self.target_spinbox.setValue(presets[index])
    
    def _on_original_changed(self, value):
        self.original_temp = value
        self.update_preview()
    
    def _on_target_changed(self, value):
        self.target_temp = value
        self.update_preview()
    
    def _on_opacity_changed(self, value):
        self.update_preview()
    
    def _on_preview_toggled(self, state):
        if state == Qt.CheckState.Checked.value:
            self.update_preview()
        else:
            self._restore_original()
    
    def _on_reset(self):
        self.original_spinbox.setValue(6500.0)
        self.target_spinbox.setValue(6500.0)
        self.opacity_spinbox.setValue(100.0)
        self.mode_combo.setCurrentIndex(0)
        self._restore_original()
    
    def _on_accept(self):
        self.update_timer.stop()
        
        if self.canva_widget and self.original_pixels is not None:
            canva = self.canva_widget.canva
            active_layer = canva.get_img()
            
            if active_layer:
                opacity = self.opacity_spinbox.value() / 100.0
                
                active_layer.pixels = self.original_pixels.copy()
                active_layer.adjust_color_temperature(
                    self.original_temp, 
                    self.target_temp, 
                    opacity
                )
                
                self.canva_widget.set_temperature_settings(
                    self.original_temp,
                    self.target_temp
                )
                
                self.canva_widget.draw_canva()
        
        self.accept()
    
    def _on_cancel(self):
        self.update_timer.stop()
        self._restore_original()
        self.reject()
    
    def _restore_original(self):
        if self.canva_widget and self.original_pixels is not None:
            canva = self.canva_widget.canva
            active_layer = canva.get_img()
            if active_layer:
                active_layer.pixels = self.original_pixels.copy()
                self.canva_widget.draw_canva()
    
    def _on_help(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Aide - Température de couleur",
            "Ajuste la température de couleur de l'image.\n\n"
            "• Température originale : Température estimée de la source lumineuse\n"
            "• Température souhaitée : Température cible pour la correction\n"
            "• Mode : Mode de fusion pour appliquer l'effet\n"
            "• Opacité : Intensité de l'effet (0-100%)\n\n"
            "Valeurs de température courantes :\n"
            "• Bougie : ~1850K\n"
            "• Tungstène : ~3200K\n"
            "• Néon : ~4000K\n"
            "• Lumière du jour : ~5500K\n"
            "• Ciel nuageux : ~6500K"
        )
    
    def update_preview(self):
        if not self.canva_widget or not self.preview_checkbox.isChecked():
            return
        
        self.update_timer.stop()
        self.update_timer.start(50)
    
    def _do_update_preview(self):
        if not self.canva_widget or not self.preview_checkbox.isChecked():
            return
        
        opacity = self.opacity_spinbox.value() / 100.0
        
        canva = self.canva_widget.canva
        active_layer = canva.get_img()
        
        if not active_layer:
            return
        
        active_layer.pixels = self.original_pixels.copy()
        
        active_layer.adjust_color_temperature(
            self.original_temp, 
            self.target_temp, 
            opacity
        )
        
        self.canva_widget.draw_canva()
    
    def get_settings(self):
        return {
            'original_temp': self.original_temp,
            'target_temp': self.target_temp,
            'mode': self.mode_combo.currentText(),
            'opacity': self.opacity_spinbox.value() / 100.0
        }


from PySide6.QtWidgets import QDoubleSpinBox