"""
Theme Manager Component

This module provides functionality for managing dark and light themes
in the PDF Utility Toolkit application.
"""

import os
import json
from typing import Dict, Any, Optional
from enum import Enum
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings


class Theme(Enum):
    """Available themes."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"  # Follow system theme


class ThemeManager:
    """Theme manager for the application."""
    
    def __init__(self):
        self.settings = QSettings('PDFUtilityToolkit', 'Theme')
        self.current_theme = self._load_theme_setting()
        
        # Default color schemes
        self.light_theme = {
            'background': '#f0f0f0',
            'foreground': '#000000',
            'primary': '#0078d4',
            'secondary': '#605e5c',
            'accent': '#0078d4',
            'surface': '#ffffff',
            'border': '#d0d0d0',
            'text_primary': '#000000',
            'text_secondary': '#605e5c',
            'text_disabled': '#a19f9d',
            'button_background': '#ffffff',
            'button_foreground': '#000000',
            'button_hover': '#f3f2f1',
            'button_pressed': '#e1dfdd',
            'input_background': '#ffffff',
            'input_border': '#d0d0d0',
            'input_focus': '#0078d4',
            'success': '#107c10',
            'warning': '#ff8c00',
            'error': '#d13438',
            'info': '#0078d4'
        }
        
        self.dark_theme = {
            'background': '#1f1f1f',
            'foreground': '#ffffff',
            'primary': '#0078d4',
            'secondary': '#8a8a8a',
            'accent': '#0078d4',
            'surface': '#2d2d30',
            'border': '#3f3f3f',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'text_disabled': '#6a6a6a',
            'button_background': '#2d2d30',
            'button_foreground': '#ffffff',
            'button_hover': '#3e3e42',
            'button_pressed': '#007acc',
            'input_background': '#2d2d30',
            'input_border': '#3f3f3f',
            'input_focus': '#0078d4',
            'success': '#107c10',
            'warning': '#ff8c00',
            'error': '#d13438',
            'info': '#0078d4'
        }
    
    def _load_theme_setting(self) -> Theme:
        """Load theme setting from QSettings."""
        theme_str = self.settings.value('theme', Theme.LIGHT.value)
        try:
            return Theme(theme_str)
        except ValueError:
            return Theme.LIGHT
    
    def _save_theme_setting(self, theme: Theme) -> None:
        """Save theme setting to QSettings."""
        self.settings.setValue('theme', theme.value)
    
    def get_current_theme(self) -> Theme:
        """Get current theme."""
        return self.current_theme
    
    def set_theme(self, theme: Theme) -> None:
        """Set application theme.
        
        Args:
            theme: Theme to set
        """
        self.current_theme = theme
        self._save_theme_setting(theme)
        self._apply_theme(theme)
    
    def _apply_theme(self, theme: Theme) -> None:
        """Apply theme to the application.
        
        Args:
            theme: Theme to apply
        """
        if theme == Theme.AUTO:
            # Try to detect system theme
            theme = self._detect_system_theme()
        
        color_scheme = self.light_theme if theme == Theme.LIGHT else self.dark_theme
        
        # Create stylesheet
        stylesheet = self._create_stylesheet(color_scheme)
        
        # Apply to application
        app = QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)
    
    def _detect_system_theme(self) -> Theme:
        """Detect system theme preference.
        
        Returns:
            Detected theme
        """
        # This is a simplified detection - in a real application,
        # you might want to use platform-specific APIs
        try:
            # For Windows, check registry
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return Theme.LIGHT if value == 1 else Theme.DARK
            except:
                pass
        except ImportError:
            pass
        
        # Default to light theme if detection fails
        return Theme.LIGHT
    
    def _create_stylesheet(self, colors: Dict[str, str]) -> str:
        """Create Qt stylesheet from color scheme.
        
        Args:
            colors: Color scheme dictionary
            
        Returns:
            Qt stylesheet string
        """
        return f"""
        QMainWindow {{
            background-color: {colors['background']};
            color: {colors['foreground']};
        }}
        
        QWidget {{
            background-color: {colors['background']};
            color: {colors['foreground']};
        }}
        
        QPushButton {{
            background-color: {colors['button_background']};
            color: {colors['button_foreground']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {colors['button_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['button_pressed']};
        }}
        
        QPushButton:disabled {{
            background-color: {colors['text_disabled']};
            color: {colors['text_disabled']};
        }}
        
        QLineEdit {{
            background-color: {colors['input_background']};
            color: {colors['text_primary']};
            border: 1px solid {colors['input_border']};
            border-radius: 4px;
            padding: 6px 8px;
        }}
        
        QLineEdit:focus {{
            border: 2px solid {colors['input_focus']};
        }}
        
        QTextEdit {{
            background-color: {colors['input_background']};
            color: {colors['text_primary']};
            border: 1px solid {colors['input_border']};
            border-radius: 4px;
            padding: 6px 8px;
        }}
        
        QComboBox {{
            background-color: {colors['input_background']};
            color: {colors['text_primary']};
            border: 1px solid {colors['input_border']};
            border-radius: 4px;
            padding: 6px 8px;
        }}
        
        QComboBox:focus {{
            border: 2px solid {colors['input_focus']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {colors['text_primary']};
        }}
        
        QGroupBox {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 8px 0 8px;
        }}
        
        QRadioButton {{
            color: {colors['text_primary']};
            spacing: 8px;
        }}
        
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 8px;
            border: 2px solid {colors['border']};
            background-color: {colors['input_background']};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {colors['primary']};
            border: 2px solid {colors['primary']};
        }}
        
        QScrollArea {{
            background-color: {colors['background']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
        }}
        
        QScrollBar:vertical {{
            background-color: {colors['background']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['border']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['text_secondary']};
        }}
        
        QFrame {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
        }}
        
        QLabel {{
            color: {colors['text_primary']};
        }}
        
        QLabel[class="title"] {{
            font-size: 16px;
            font-weight: bold;
            color: {colors['primary']};
        }}
        
        QLabel[class="subtitle"] {{
            font-size: 14px;
            color: {colors['text_secondary']};
        }}
        
        QMessageBox {{
            background-color: {colors['background']};
            color: {colors['foreground']};
        }}
        
        QMessageBox QPushButton {{
            min-width: 80px;
        }}
        
        QFileDialog {{
            background-color: {colors['background']};
            color: {colors['foreground']};
        }}
        
        QProgressBar {{
            border: 1px solid {colors['border']};
            border-radius: 4px;
            text-align: center;
            background-color: {colors['input_background']};
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: 3px;
        }}
        """
    
    def get_color(self, color_name: str) -> str:
        """Get color value for current theme.
        
        Args:
            color_name: Name of the color
            
        Returns:
            Color value as hex string
        """
        theme = self.get_current_theme()
        if theme == Theme.AUTO:
            theme = self._detect_system_theme()
        
        color_scheme = self.light_theme if theme == Theme.LIGHT else self.dark_theme
        return color_scheme.get(color_name, '#000000')
    
    def toggle_theme(self) -> Theme:
        """Toggle between light and dark themes.
        
        Returns:
            New theme
        """
        current = self.get_current_theme()
        if current == Theme.LIGHT:
            new_theme = Theme.DARK
        elif current == Theme.DARK:
            new_theme = Theme.LIGHT
        else:  # AUTO
            detected = self._detect_system_theme()
            new_theme = Theme.DARK if detected == Theme.LIGHT else Theme.LIGHT
        
        self.set_theme(new_theme)
        return new_theme
    
    def export_theme_config(self, file_path: str) -> bool:
        """Export current theme configuration to file.
        
        Args:
            file_path: Path to export file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            config = {
                'theme': self.current_theme.value,
                'light_theme': self.light_theme,
                'dark_theme': self.dark_theme
            }
            
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting theme config: {e}")
            return False
    
    def import_theme_config(self, file_path: str) -> bool:
        """Import theme configuration from file.
        
        Args:
            file_path: Path to import file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            # Update theme
            if 'theme' in config:
                try:
                    theme = Theme(config['theme'])
                    self.set_theme(theme)
                except ValueError:
                    pass
            
            # Update color schemes
            if 'light_theme' in config:
                self.light_theme.update(config['light_theme'])
            
            if 'dark_theme' in config:
                self.dark_theme.update(config['dark_theme'])
            
            return True
        except Exception as e:
            print(f"Error importing theme config: {e}")
            return False


# Global theme manager instance
_theme_manager = None


def get_theme_manager() -> ThemeManager:
    """Get global theme manager instance.
    
    Returns:
        ThemeManager instance
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def set_application_theme(theme: Theme) -> None:
    """Set application theme.
    
    Args:
        theme: Theme to set
    """
    manager = get_theme_manager()
    manager.set_theme(theme)


def get_current_theme() -> Theme:
    """Get current application theme.
    
    Returns:
        Current theme
    """
    manager = get_theme_manager()
    return manager.get_current_theme()


def toggle_application_theme() -> Theme:
    """Toggle application theme.
    
    Returns:
        New theme
    """
    manager = get_theme_manager()
    return manager.toggle_theme() 