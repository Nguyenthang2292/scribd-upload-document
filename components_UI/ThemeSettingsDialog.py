from PyQt5.QtWidgets import (QDialog, 
                             QVBoxLayout, 
                             QGroupBox, 
                             QVBoxLayout, 
                             QRadioButton, 
                             QCheckBox, 
                             QHBoxLayout, 
                             QPushButton)
from theme.theme_manager import Theme, set_application_theme, get_current_theme

class ThemeSettingsDialog(QDialog):
    """Dialog for theme settings and customization."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Theme Settings")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        self._setup_ui()
        self._load_current_settings()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Theme selection group
        theme_group = QGroupBox("Theme Selection")
        theme_layout = QVBoxLayout(theme_group)
        
        self.light_radio = QRadioButton("Light Theme")
        self.dark_radio = QRadioButton("Dark Theme")
        self.auto_radio = QRadioButton("Auto (Follow System)")
        
        theme_layout.addWidget(self.light_radio)
        theme_layout.addWidget(self.dark_radio)
        theme_layout.addWidget(self.auto_radio)
        
        layout.addWidget(theme_group)
        
        # Options group
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.save_preference = QCheckBox("Save theme preference")
        self.save_preference.setChecked(True)
        
        self.auto_detect = QCheckBox("Auto-detect system theme changes")
        self.auto_detect.setChecked(True)
        
        options_layout.addWidget(self.save_preference)
        options_layout.addWidget(self.auto_detect)
        
        layout.addWidget(options_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self._apply_settings)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self._apply_and_close)
        
        button_layout.addWidget(self.apply_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
    
    def _load_current_settings(self):
        """Load current theme settings."""
        current_theme = get_current_theme()
        
        if current_theme == Theme.LIGHT:
            self.light_radio.setChecked(True)
        elif current_theme == Theme.DARK:
            self.dark_radio.setChecked(True)
        else:  # AUTO
            self.auto_radio.setChecked(True)
    
    def _apply_settings(self):
        """Apply the selected theme settings."""
        if self.light_radio.isChecked():
            theme = Theme.LIGHT
        elif self.dark_radio.isChecked():
            theme = Theme.DARK
        else:  # auto_radio
            theme = Theme.AUTO
        
        set_application_theme(theme)
        
        # Theme is applied globally, no need to update parent specifically
    
    def _apply_and_close(self):
        """Apply settings and close dialog."""
        self._apply_settings()
        self.accept()