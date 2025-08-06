"""
PDF Utility Toolkit - PyQt5 GUI Application.

This module provides a comprehensive GUI application for PDF manipulation
including Scribd bypass, compression, conversion, and merging operations.
"""

import os
import sys
from typing import List, Dict, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QAction,
    QToolBar,
    QDialog,
    QCheckBox,
    QProgressBar,
)

from PIL import Image
from pdf2image import convert_from_path

import config
from components.compress_pdf import compress_pdf
from components.convert_to_pdf import (
    doc_to_pdf,
    epub_to_pdf,
    jpg_to_pdf,
    png_to_pdf,
    ppt_to_pdf,
    xls_to_pdf,
)
from components.merge_pages_landscape import merge_pdf_vertical_to_horizontal
from components.merge_pdf import merge_pdfs
from components.scribd_bypass import ScribdBypass
from theme.theme_manager import Theme, get_theme_manager, set_application_theme, get_current_theme, toggle_application_theme
from components.batch_processor import process_pdf_directory
from components.duplicate_finder import generate_duplicate_report
from components.metadata_cleaner import remove_all_pdf_metadata
from components.pdf_encryption import encrypt_pdf_file, decrypt_pdf_file
from components.pdf_splitter import split_pdf_by_pages_per_file
from components.watermark_pdf import add_watermark_to_pdf, remove_watermark_from_pdf
from components.pdf_to_doc import pdf_to_doc, batch_pdf_to_doc
from components_UI.ThemeSettingsDialog import ThemeSettingsDialog
from components_UI.DraggableThumbFrame import DraggableThumbFrame

class PDFUtilityToolkitPyQt(QMainWindow):
    """
    Main application window for the PDF Utility Toolkit.
    
    This class provides a comprehensive GUI for PDF manipulation operations
    including Scribd bypass, compression, conversion, and merging.
    """

    def __init__(self) -> None:
        """Initialize the main application window."""
        super().__init__()
        self._setup_window()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_ui()
        self._initialize_function_widgets()
        self._setup_function_switching()
        self._apply_initial_theme()

    def _setup_window(self) -> None:
        """Configure the main window properties."""
        self.setWindowTitle("PDF Utility Toolkit (PyQt)")
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Setup status bar
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage('Ready')

    def _setup_menu_bar(self) -> None:
        """Setup the menu bar with theme options."""
        menubar = self.menuBar()
        if menubar is None:
            return
        
        # View menu
        view_menu = menubar.addMenu('View')
        if view_menu is None:
            return
        
        # Theme submenu
        theme_menu = view_menu.addMenu('Theme')
        if theme_menu is None:
            return
        
        # Light theme action
        self.light_theme_action = QAction('Light Theme', self)
        self.light_theme_action.setCheckable(True)
        self.light_theme_action.triggered.connect(lambda: self._set_theme(Theme.LIGHT))
        theme_menu.addAction(self.light_theme_action)
        
        # Dark theme action
        self.dark_theme_action = QAction('Dark Theme', self)
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.triggered.connect(lambda: self._set_theme(Theme.DARK))
        theme_menu.addAction(self.dark_theme_action)
        
        # Auto theme action
        self.auto_theme_action = QAction('Auto (System)', self)
        self.auto_theme_action.setCheckable(True)
        self.auto_theme_action.triggered.connect(lambda: self._set_theme(Theme.AUTO))
        theme_menu.addAction(self.auto_theme_action)
        
        # Toggle theme action
        toggle_action = QAction('Toggle Theme', self)
        toggle_action.setShortcut('Ctrl+T')
        toggle_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(toggle_action)
        
        # Separator
        view_menu.addSeparator()
        
        # Theme settings action
        settings_action = QAction('Theme Settings...', self)
        settings_action.triggered.connect(self._show_theme_settings)
        view_menu.addAction(settings_action)

    def _setup_toolbar(self) -> None:
        """Setup the toolbar with theme controls."""
        toolbar = QToolBar('Main Toolbar', self)
        self.addToolBar(toolbar)
        
        # Theme selector combo box
        self.theme_label = QLabel('Theme:')
        self.theme_label.setObjectName('themeLabel')
        self.theme_label.setStyleSheet('background: transparent; border: none; padding: 0 4px 0 0;')
        toolbar.addWidget(self.theme_label)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Light', 'Dark', 'Auto'])
        self.theme_combo.currentIndexChanged.connect(self._on_theme_combo_changed)
        toolbar.addWidget(self.theme_combo)
        
        # Toggle theme button
        self.toggle_theme_btn = QPushButton('Toggle Theme')
        self.toggle_theme_btn.clicked.connect(self._toggle_theme)
        toolbar.addWidget(self.toggle_theme_btn)
        
        toolbar.addSeparator()

    def _apply_initial_theme(self) -> None:
        """Apply the initial theme based on saved settings."""
        current_theme = get_current_theme()
        self._update_theme_ui(current_theme)
        self._set_theme(current_theme)

    def _set_theme(self, theme: Theme) -> None:
        """Set the application theme.
        
        Args:
            theme: Theme to set
        """
        set_application_theme(theme)
        self._update_theme_ui(theme)

    def _toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        new_theme = toggle_application_theme()
        self._update_theme_ui(new_theme)

    def _update_theme_ui(self, theme: Theme) -> None:
        """Update the UI to reflect the current theme.
        
        Args:
            theme: Current theme
        """
        # Update menu checkmarks
        self.light_theme_action.setChecked(theme == Theme.LIGHT)
        self.dark_theme_action.setChecked(theme == Theme.DARK)
        self.auto_theme_action.setChecked(theme == Theme.AUTO)
        
        # Update combo box
        theme_index = {
            Theme.LIGHT: 0,
            Theme.DARK: 1,
            Theme.AUTO: 2
        }.get(theme, 0)
        
        if self.theme_combo.currentIndex() != theme_index:
            self.theme_combo.setCurrentIndex(theme_index)
        
        # Update button text
        if theme == Theme.LIGHT:
            self.toggle_theme_btn.setText('Switch to Dark')
        elif theme == Theme.DARK:
            self.toggle_theme_btn.setText('Switch to Light')
        else:  # AUTO
            detected_theme = get_theme_manager()._detect_system_theme()
            if detected_theme == Theme.LIGHT:
                self.toggle_theme_btn.setText('Switch to Dark')
            else:
                self.toggle_theme_btn.setText('Switch to Light')
        
        # Update status bar
        status_bar = self.statusBar()
        if status_bar:
            theme_name = theme.value.title()
            if theme == Theme.AUTO:
                detected = get_theme_manager()._detect_system_theme()
                theme_name = f"Auto ({detected.value.title()})"
            status_bar.showMessage(f'Theme: {theme_name}')

        # Update label colors for theme
        color = get_theme_manager().get_color('text_primary')
        if hasattr(self, 'theme_label'):
            self.theme_label.setStyleSheet(f'background: transparent; border: none; padding: 0 4px 0 0; color: {color};')
        if hasattr(self, 'select_function_label'):
            self.select_function_label.setStyleSheet(f'background: transparent; border: none; padding: 0 4px 0 0; color: {color};')

    def _on_theme_combo_changed(self, index: int) -> None:
        """Handle theme combo box selection change.
        
        Args:
            index: Selected index
        """
        theme_map = [Theme.LIGHT, Theme.DARK, Theme.AUTO]
        if 0 <= index < len(theme_map):
            self._set_theme(theme_map[index])

    def _show_theme_settings(self) -> None:
        """Show theme settings dialog."""
        dialog = ThemeSettingsDialog(self)
        if dialog.exec_() == QDialog.DialogCode.Accepted:
            # Refresh the UI after theme change
            current_theme = get_current_theme()
            self._update_theme_ui(current_theme)

    def _setup_ui(self) -> None:
        """Setup the main UI components."""
        self.function_options = sorted([
            "Bypass Scribd",
            "Compress PDF",
            "Convert to PDF",
            "PDF to DOC",
            "Merge 2 Vertical Pages",
            "Merge PDFs",
            "Batch Processor",
            "Duplicate Finder",
            "Metadata Cleaner",
            "PDF Encryption",
            "PDF Splitter",
            "Watermark PDF"
        ])
        
        self.selected_function = QComboBox()
        self.selected_function.addItems(self.function_options)
        
        func_layout = QHBoxLayout()
        self.select_function_label = QLabel("Select Function:")
        self.select_function_label.setObjectName('selectFunctionLabel')
        self.select_function_label.setStyleSheet('background: transparent; border: none; padding: 0 4px 0 0;')
        func_layout.addWidget(self.select_function_label)
        func_layout.addWidget(self.selected_function)
        self.main_layout.addLayout(func_layout)

    def _initialize_function_widgets(self) -> None:
        """Initialize all function-specific widgets."""
        self.function_widgets = {}
        
        self._init_bypass_scribd()
        self._init_convert_to_pdf()
        self._init_merge_vertical()
        self._init_merge_pdfs()
        self._init_compress_pdf()
        self._init_pdf_to_doc()
        self._init_batch_processor()
        self._init_duplicate_finder()
        self._init_metadata_cleaner()
        self._init_pdf_encryption()
        self._init_pdf_splitter()
        self._init_watermark_pdf()

    def _setup_function_switching(self) -> None:
        """Setup function switching mechanism."""
        self.selected_function.currentIndexChanged.connect(self._switch_function)
        self._switch_function(0)

    def _clear_function_widgets(self) -> None:
        """Hide all function widgets."""
        for widget in self.function_widgets.values():
            widget.setVisible(False)

    def _switch_function(self, idx: int) -> None:
        """Switch to the selected function widget.
        
        Args:
            idx: Index of the function to switch to
        """
        self._clear_function_widgets()
        func_name = self.function_options[idx]
        self.function_widgets[func_name].setVisible(True)

    # --- Scribd Bypass Function ---
    
    def _init_bypass_scribd(self) -> None:
        """Initialize the Scribd bypass function widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Input section
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("PDF Input:"))
        self.scribd_input = QLineEdit()
        input_layout.addWidget(self.scribd_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_scribd_input)
        input_layout.addWidget(browse_btn)
        layout.addLayout(input_layout)
        
        # Output section
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Directory:"))
        self.scribd_output = QLineEdit()
        output_layout.addWidget(self.scribd_output)
        
        output_btn = QPushButton("Browse")
        output_btn.clicked.connect(self._browse_scribd_output)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # Process button
        process_btn = QPushButton("Bypass Scribd")
        process_btn.clicked.connect(self._process_scribd_bypass)
        layout.addWidget(process_btn)
        
        # Log area
        self.scribd_log = QTextEdit()
        self.scribd_log.setReadOnly(True)
        layout.addWidget(self.scribd_log)
        
        self.main_layout.addWidget(widget)
        self.function_widgets["Bypass Scribd"] = widget
        widget.setVisible(False)

    def _browse_scribd_input(self) -> None:
        """Browse for Scribd input PDF file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)"
        )
        if filename:
            self.scribd_input.setText(filename)

    def _browse_scribd_output(self) -> None:
        """Browse for Scribd output directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.scribd_output.setText(directory)

    def _process_scribd_bypass(self) -> None:
        """Process the Scribd bypass operation."""
        input_file = self.scribd_input.text()
        output_dir = self.scribd_output.text() or "scribd_output"
        
        self.scribd_log.append(f"Bypassing Scribd: {input_file}")
        
        try:
            bypass = ScribdBypass(output_dir)
            result = bypass.create_scribd_file(input_file, file_type="document")
            
            if result:
                self.scribd_log.append(f"✅ Scribd file created: {result}")
            else:
                self.scribd_log.append("❌ Scribd processing failed")
        except Exception as e:
            self.scribd_log.append(f"❌ Error: {str(e)}")

    # --- Convert to PDF Function ---
    
    def _init_convert_to_pdf(self) -> None:
        """Initialize the convert to PDF function widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # File type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Source File Type:"))
        self.convert_type = QComboBox()
        self.convert_type.addItems([
            "DOC/DOCX", "XLS/XLSX", "PPT/PPTX", 
            "PNG", "JPG/JPEG", "EPUB"
        ])
        self.convert_type.currentIndexChanged.connect(self._update_convert_label)
        type_layout.addWidget(self.convert_type)
        layout.addLayout(type_layout)
        
        # Input/Output section
        io_layout = QHBoxLayout()
        self.convert_input = QLineEdit()
        input_btn = QPushButton("Browse")
        input_btn.clicked.connect(self._browse_convert_input)
        
        self.convert_output = QLineEdit()
        output_btn = QPushButton("Browse")
        output_btn.clicked.connect(self._browse_convert_output)
        
        io_layout.addWidget(QLabel("Input File:"))
        io_layout.addWidget(self.convert_input)
        io_layout.addWidget(input_btn)
        io_layout.addWidget(QLabel("Output PDF:"))
        io_layout.addWidget(self.convert_output)
        io_layout.addWidget(output_btn)
        layout.addLayout(io_layout)
        
        # Process button
        process_btn = QPushButton("Convert to PDF")
        process_btn.clicked.connect(self._process_convert_to_pdf)
        layout.addWidget(process_btn)
        
        # Log area
        self.convert_log = QTextEdit()
        self.convert_log.setReadOnly(True)
        layout.addWidget(self.convert_log)
        
        self.main_layout.addWidget(widget)
        self.function_widgets["Convert to PDF"] = widget
        widget.setVisible(False)
        self._update_convert_label()

    def _update_convert_label(self) -> None:
        """Update the convert label based on selected file type."""
        # Label is already fixed in the UI, no dynamic update needed
        pass

    def _browse_convert_input(self) -> None:
        """Browse for convert input file."""
        idx = self.convert_type.currentIndex()
        filters = [
            "Word files (*.doc *.docx)",
            "Excel files (*.xls *.xlsx)",
            "PowerPoint files (*.ppt *.pptx)",
            "PNG files (*.png)",
            "JPEG files (*.jpg *.jpeg)",
            "EPUB files (*.epub)"
        ]
        
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Input File", "", filters[idx]
        )
        
        if filename:
            self.convert_input.setText(filename)
            base, _ = os.path.splitext(filename)
            self.convert_output.setText(f"{base}.pdf")

    def _browse_convert_output(self) -> None:
        """Browse for convert output PDF file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save PDF As", "", "PDF Files (*.pdf)"
        )
        if filename:
            self.convert_output.setText(filename)

    def _process_convert_to_pdf(self) -> None:
        """Process the convert to PDF operation."""
        filetype = self.convert_type.currentText()
        input_file = self.convert_input.text()
        output_file = self.convert_output.text()
        
        if not input_file or not output_file:
            QMessageBox.critical(
                self, "Error", "Please select input file and output PDF file."
            )
            return
            
        self.convert_log.append(
            f"Converting {input_file} to {output_file} as {filetype}"
        )
        
        try:
            conversion_functions = {
                "DOC/DOCX": doc_to_pdf,
                "XLS/XLSX": xls_to_pdf,
                "PPT/PPTX": ppt_to_pdf,
                "PNG": png_to_pdf,
                "JPG/JPEG": jpg_to_pdf,
                "EPUB": epub_to_pdf,
            }
            
            if filetype in conversion_functions:
                conversion_functions[filetype](input_file, output_file)
                self.convert_log.append(f"✅ Converted successfully: {output_file}")
                QMessageBox.information(
                    self, "Success", f"Converted successfully: {output_file}"
                )
            else:
                raise ValueError(f"Unsupported file type: {filetype}")
                
        except Exception as e:
            self.convert_log.append(f"❌ Conversion error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Conversion error: {str(e)}")

    # --- Merge Vertical Pages Function ---
    
    def _init_merge_vertical(self) -> None:
        """Initialize the merge vertical pages function widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Input section
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("PDF Input:"))
        self.merge_input = QLineEdit()
        input_layout.addWidget(self.merge_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_merge_input)
        input_layout.addWidget(browse_btn)
        layout.addLayout(input_layout)
        
        # Output section
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Directory:"))
        self.merge_output = QLineEdit()
        output_layout.addWidget(self.merge_output)
        
        output_btn = QPushButton("Browse")
        output_btn.clicked.connect(self._browse_merge_output)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # Process button
        process_btn = QPushButton("Merge 2 Vertical Pages")
        process_btn.clicked.connect(self._process_merge_vertical)
        layout.addWidget(process_btn)
        
        # Log area
        self.merge_log = QTextEdit()
        self.merge_log.setReadOnly(True)
        layout.addWidget(self.merge_log)
        
        self.main_layout.addWidget(widget)
        self.function_widgets["Merge 2 Vertical Pages"] = widget
        widget.setVisible(False)

    def _browse_merge_input(self) -> None:
        """Browse for merge input PDF file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)"
        )
        if filename:
            self.merge_input.setText(filename)

    def _browse_merge_output(self) -> None:
        """Browse for merge output directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.merge_output.setText(directory)

    def _process_merge_vertical(self) -> None:
        """Process the merge vertical pages operation."""
        input_pdf = self.merge_input.text()
        output_dir = self.merge_output.text() or "output"
        
        if not input_pdf:
            QMessageBox.critical(self, "Error", "Please select an input PDF file")
            return
            
        base, _ = os.path.splitext(input_pdf)
        output_pdf = os.path.join(
            output_dir, f"{os.path.basename(base)}_2in1.pdf"
        )
        
        self.merge_log.append(f"Merging: {input_pdf} -> {output_pdf}")
        
        try:
            merge_pdf_vertical_to_horizontal(input_pdf, output_pdf)
            self.merge_log.append(f"✅ Merged: {output_pdf}")
            QMessageBox.information(self, "Success", f"Merged: {output_pdf}")
        except Exception as e:
            self.merge_log.append(f"❌ Merge error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Merge error: {str(e)}")

    # --- Merge PDFs Function ---
    
    def _init_merge_pdfs(self) -> None:
        """Initialize the merge PDFs function widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Input section
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("PDF Files (separate by ;):"))
        self.mergepdf_input = QLineEdit()
        self.mergepdf_input.textChanged.connect(self._refresh_mergepdf_preview)
        input_layout.addWidget(self.mergepdf_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_mergepdf_input)
        input_layout.addWidget(browse_btn)
        layout.addLayout(input_layout)
        
        # Preview area
        preview_group = QGroupBox("Preview & Order")
        preview_vbox = QVBoxLayout(preview_group)
        
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_frame = QFrame()
        self.preview_hbox = QHBoxLayout(self.preview_frame)
        self.preview_hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.preview_scroll.setWidget(self.preview_frame)
        preview_vbox.addWidget(self.preview_scroll)
        
        # Preview buttons
        btns_hbox = QHBoxLayout()
        refresh_btn = QPushButton("Refresh Preview")
        refresh_btn.clicked.connect(self._refresh_mergepdf_preview)
        btns_hbox.addWidget(refresh_btn)
        
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self._delete_selected_mergepdf_files)
        btns_hbox.addWidget(delete_btn)
        preview_vbox.addLayout(btns_hbox)
        layout.addWidget(preview_group)
        
        # Output section
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output PDF:"))
        self.mergepdf_output = QLineEdit()
        output_layout.addWidget(self.mergepdf_output)
        
        output_btn = QPushButton("Browse")
        output_btn.clicked.connect(self._browse_mergepdf_output)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # Process button
        process_btn = QPushButton("Merge PDFs")
        process_btn.clicked.connect(self._process_merge_pdfs)
        layout.addWidget(process_btn)
        
        # Log area
        self.mergepdf_log = QTextEdit()
        self.mergepdf_log.setReadOnly(True)
        layout.addWidget(self.mergepdf_log)
        
        self.main_layout.addWidget(widget)
        self.function_widgets["Merge PDFs"] = widget
        widget.setVisible(False)
        
        # Initialize state
        self.mergepdf_files: List[Dict] = []
        self.mergepdf_thumbnails: List[List[QPixmap]] = []
        self.last_selected_idx: Optional[int] = None
        self._refresh_mergepdf_preview()

    def _refresh_mergepdf_preview(self) -> None:
        """Refresh the PDF merge preview area."""
        # Clear existing preview
        for i in reversed(range(self.preview_hbox.count())):
            item = self.preview_hbox.itemAt(i)
            widget = item.widget() if item else None
            if widget:
                widget.setParent(None)
        
        self.mergepdf_thumbnails = []
        
        # Get file list
        input_val = self.mergepdf_input.text()
        if os.path.isdir(input_val):
            pdf_files = sorted([
                str(p.path) for p in os.scandir(input_val) 
                if p.name.lower().endswith('.pdf')
            ])
        else:
            pdf_files = [f.strip() for f in input_val.split(';') if f.strip()]
        
        # Build file dictionaries
        old_files = getattr(self, 'mergepdf_files', [])
        old_selected = {
            f['path']: f.get('selected', False) 
            for f in old_files if isinstance(f, dict)
        }
        
        self.mergepdf_files = []
        for pdf in pdf_files:
            thumbs = self._get_pdf_thumbnails_pyqt(pdf, num_pages=3)
            self.mergepdf_thumbnails.append(thumbs)
            self.mergepdf_files.append({
                'path': pdf,
                'selected': old_selected.get(pdf, False),
                'thumbnails': thumbs
            })
        
        # Show thumbnails
        for idx, fileinfo in enumerate(self.mergepdf_files):
            thumb_frame = DraggableThumbFrame(
                self.preview_frame, idx, 
                self._on_drag_drop_mergepdf, 
                self._toggle_select_mergepdf, 
                fileinfo['thumbnails']
            )
            thumb_frame.setFrameShape(QFrame.StyledPanel)
            thumb_frame.setStyleSheet(
                f"background: {'#bfefff' if fileinfo['selected'] else '#f0f0f0'};"
            )
            
            thumb_vbox = QVBoxLayout(thumb_frame)
            thumbs_hbox = QHBoxLayout()
            
            for thumb in fileinfo['thumbnails']:
                lbl = QLabel()
                lbl.setPixmap(thumb)
                thumbs_hbox.addWidget(lbl)
            
            thumb_vbox.addLayout(thumbs_hbox)
            
            name_lbl = QLabel(os.path.basename(fileinfo['path']))
            name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            thumb_vbox.addWidget(name_lbl)
            
            del_btn = QPushButton("Delete")
            del_btn.clicked.connect(lambda _, i=idx: self._delete_mergepdf_file(i))
            thumb_vbox.addWidget(del_btn)
            
            self.preview_hbox.addWidget(thumb_frame)

    def _get_pdf_thumbnails_pyqt(
        self, pdf_path: str, num_pages: int = 3
    ) -> List[QPixmap]:
        """Generate thumbnails for a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            num_pages: Number of pages to generate thumbnails for
            
        Returns:
            List of thumbnail pixmaps
        """
        thumbs = []
        try:
            images = convert_from_path(
                pdf_path, first_page=1, last_page=num_pages, size=(60, 80)
            )
            for img in images:
                if isinstance(img, Image.Image):
                    img = img.convert('RGB')
                    data = img.tobytes('raw', 'RGB')
                    qimg = QImage(data, img.width, img.height, QImage.Format_RGB888)
                    thumbs.append(QPixmap.fromImage(qimg))
        except Exception:
            # Fallback to gray placeholder
            img = Image.new("RGB", (60, 80), color="gray")
            data = img.tobytes('raw', 'RGB')
            qimg = QImage(data, img.width, img.height, QImage.Format_RGB888)
            thumbs.append(QPixmap.fromImage(qimg))
        
        return thumbs

    def _toggle_select_mergepdf(self, idx: int, event) -> None:
        """Toggle selection of a PDF file in the merge preview.
        
        Args:
            idx: Index of the file to toggle
            event: Mouse event
        """
        for i, fileinfo in enumerate(self.mergepdf_files):
            fileinfo['selected'] = (i == idx)
        self.last_selected_idx = idx
        self._refresh_mergepdf_preview()

    def _delete_mergepdf_file(self, idx: int) -> None:
        """Delete a PDF file from the merge list.
        
        Args:
            idx: Index of the file to delete
        """
        del self.mergepdf_files[idx]
        self.mergepdf_input.setText(
            ';'.join(fileinfo['path'] for fileinfo in self.mergepdf_files)
        )
        self._refresh_mergepdf_preview()

    def _delete_selected_mergepdf_files(self) -> None:
        """Delete all selected PDF files from the merge list."""
        self.mergepdf_files = [
            f for f in self.mergepdf_files if not f['selected']
        ]
        self.mergepdf_input.setText(
            ';'.join(fileinfo['path'] for fileinfo in self.mergepdf_files)
        )
        self._refresh_mergepdf_preview()

    def _browse_mergepdf_input(self) -> None:
        """Browse for multiple PDF files to merge."""
        filenames, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files", "", "PDF Files (*.pdf)"
        )
        if filenames:
            self.mergepdf_input.setText(';'.join(filenames))

    def _browse_mergepdf_output(self) -> None:
        """Browse for merge output PDF file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Merged PDF As", "", "PDF Files (*.pdf)"
        )
        if filename:
            self.mergepdf_output.setText(filename)

    def _process_merge_pdfs(self) -> None:
        """Process the merge PDFs operation."""
        pdf_files = [
            f.strip() for f in self.mergepdf_input.text().split(';') 
            if f.strip()
        ]
        output_pdf = self.mergepdf_output.text()
        
        if not pdf_files:
            QMessageBox.critical(self, "Error", "Please select input PDF files.")
            return
            
        if not output_pdf:
            out_dir = os.path.dirname(pdf_files[0]) if pdf_files else os.getcwd()
            output_pdf = os.path.join(out_dir, "merged_output.pdf")
            self.mergepdf_output.setText(output_pdf)
        
        self.mergepdf_log.append(f"Merging {len(pdf_files)} files into {output_pdf}")
        
        try:
            merge_pdfs(pdf_files, output_pdf)
            self.mergepdf_log.append(f"✅ Merged successfully: {output_pdf}")
            QMessageBox.information(
                self, "Success", f"Merged successfully: {output_pdf}"
            )
        except Exception as e:
            self.mergepdf_log.append(f"❌ Merge error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Merge error: {str(e)}")

    def _on_drag_drop_mergepdf(self, from_idx: int, to_idx: int) -> None:
        """Handle drag and drop reordering in merge PDF preview.
        
        Args:
            from_idx: Source index
            to_idx: Target index
        """
        if (from_idx < 0 or to_idx < 0 or 
            from_idx >= len(self.mergepdf_files) or 
            to_idx >= len(self.mergepdf_files)):
            return
            
        fileinfo = self.mergepdf_files.pop(from_idx)
        self.mergepdf_files.insert(to_idx, fileinfo)
        self.mergepdf_input.setText(
            ';'.join(fileinfo['path'] for fileinfo in self.mergepdf_files)
        )
        self._refresh_mergepdf_preview()

    # --- Compress PDF Function ---
    
    def _init_compress_pdf(self) -> None:
        """Initialize the compress PDF function widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Input section
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("PDF File:"))
        self.compress_input = QLineEdit()
        input_layout.addWidget(self.compress_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_compress_input)
        input_layout.addWidget(browse_btn)
        layout.addLayout(input_layout)
        
        # Output section
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output PDF:"))
        self.compress_output = QLineEdit()
        output_layout.addWidget(self.compress_output)
        
        output_btn = QPushButton("Browse")
        output_btn.clicked.connect(self._browse_compress_output)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # Compression level selection
        group_box = QGroupBox("Compression Level")
        group_layout = QHBoxLayout(group_box)
        
        self.compress_mode = QButtonGroup(self)
        self.rb_low = QRadioButton("Low (High Quality)")
        self.rb_medium = QRadioButton("Medium (Balanced)")
        self.rb_high = QRadioButton("High (Strong Compression)")
        
        self.rb_medium.setChecked(True)
        self.compress_mode.addButton(self.rb_low, 0)
        self.compress_mode.addButton(self.rb_medium, 1)
        self.compress_mode.addButton(self.rb_high, 2)
        
        group_layout.addWidget(self.rb_low)
        group_layout.addWidget(self.rb_medium)
        group_layout.addWidget(self.rb_high)
        layout.addWidget(group_box)
        
        # Process button
        process_btn = QPushButton("Compress PDF")
        process_btn.clicked.connect(self._process_compress_pdf)
        layout.addWidget(process_btn)
        
        # Log area
        self.compress_log = QTextEdit()
        self.compress_log.setReadOnly(True)
        layout.addWidget(self.compress_log)
        
        self.main_layout.addWidget(widget)
        self.function_widgets["Compress PDF"] = widget
        widget.setVisible(False)

    def _browse_compress_input(self) -> None:
        """Browse for compress input PDF file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)"
        )
        if filename:
            self.compress_input.setText(filename)
            base, _ = os.path.splitext(filename)
            self.compress_output.setText(f"{base}_compressed.pdf")

    def _browse_compress_output(self) -> None:
        """Browse for compress output PDF file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Compressed PDF As", "", "PDF Files (*.pdf)"
        )
        if filename:
            self.compress_output.setText(filename)

    def _process_compress_pdf(self) -> None:
        """Process the compress PDF operation."""
        input_pdf = self.compress_input.text()
        output_pdf = self.compress_output.text()
        
        # Determine compression mode
        if self.rb_low.isChecked():
            mode = 'low'
        elif self.rb_high.isChecked():
            mode = 'high'
        else:
            mode = 'medium'
        
        if not input_pdf or not output_pdf:
            QMessageBox.critical(
                self, "Error", "Please select input and output PDF file."
            )
            return
            
        self.compress_log.append(
            f"Compressing {input_pdf} to {output_pdf} (mode: {mode})"
        )
        
        try:
            compress_pdf(input_pdf, output_pdf, mode)
            self.compress_log.append(f"✅ Compressed successfully: {output_pdf}")
            QMessageBox.information(
                self, "Success", f"Compressed successfully: {output_pdf}"
            )
        except Exception as e:
            self.compress_log.append(f"❌ Compression error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Compression error: {str(e)}")

    # --- PDF to DOC Function ---
    
    def _init_pdf_to_doc(self) -> None:
        """Initialize the PDF to DOC function widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Input section
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("PDF File:"))
        self.pdf_to_doc_input = QLineEdit()
        input_layout.addWidget(self.pdf_to_doc_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_pdf_to_doc_input)
        input_layout.addWidget(browse_btn)
        layout.addLayout(input_layout)
        
        # Output section
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output DOC:"))
        self.pdf_to_doc_output = QLineEdit()
        output_layout.addWidget(self.pdf_to_doc_output)
        
        output_btn = QPushButton("Browse")
        output_btn.clicked.connect(self._browse_pdf_to_doc_output)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)
        
        # Options section
        options_group = QGroupBox("Conversion Options")
        options_layout = QVBoxLayout(options_group)
        
        # Include images checkbox
        self.pdf_to_doc_include_images = QCheckBox("Include Images")
        self.pdf_to_doc_include_images.setChecked(True)
        options_layout.addWidget(self.pdf_to_doc_include_images)
        
        # OCR checkbox
        self.pdf_to_doc_ocr = QCheckBox("Use OCR (for scanned PDFs)")
        self.pdf_to_doc_ocr.setChecked(False)
        options_layout.addWidget(self.pdf_to_doc_ocr)
        
        layout.addWidget(options_group)
        
        # Process button
        process_btn = QPushButton("Convert PDF to DOC")
        process_btn.clicked.connect(self._process_pdf_to_doc)
        layout.addWidget(process_btn)
        
        # Log area
        self.pdf_to_doc_log = QTextEdit()
        self.pdf_to_doc_log.setReadOnly(True)
        layout.addWidget(self.pdf_to_doc_log)
        
        self.main_layout.addWidget(widget)
        self.function_widgets["PDF to DOC"] = widget
        widget.setVisible(False)

    def _browse_pdf_to_doc_input(self) -> None:
        """Browse for PDF to DOC input file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)"
        )
        if filename:
            self.pdf_to_doc_input.setText(filename)
            base, _ = os.path.splitext(filename)
            self.pdf_to_doc_output.setText(f"{base}.docx")

    def _browse_pdf_to_doc_output(self) -> None:
        """Browse for PDF to DOC output file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save DOC As", "", "Word Documents (*.docx *.doc)"
        )
        if filename:
            self.pdf_to_doc_output.setText(filename)

    def _process_pdf_to_doc(self) -> None:
        """Process the PDF to DOC conversion."""
        input_pdf = self.pdf_to_doc_input.text()
        output_doc = self.pdf_to_doc_output.text()
        include_images = self.pdf_to_doc_include_images.isChecked()
        ocr_enabled = self.pdf_to_doc_ocr.isChecked()
        
        if not input_pdf or not output_doc:
            QMessageBox.critical(
                self, "Error", "Please select input PDF and output DOC file."
            )
            return
            
        self.pdf_to_doc_log.append(
            f"Converting PDF to DOC: {input_pdf} -> {output_doc}"
        )
        self.pdf_to_doc_log.append(f"Options: Include Images={include_images}, OCR={ocr_enabled}")
        
        try:
            success = pdf_to_doc(input_pdf, output_doc, include_images, ocr_enabled)
            
            if success:
                self.pdf_to_doc_log.append(f"✅ Converted successfully: {output_doc}")
                QMessageBox.information(
                    self, "Success", f"Converted successfully: {output_doc}"
                )
            else:
                self.pdf_to_doc_log.append("❌ Conversion failed")
                QMessageBox.critical(self, "Error", "PDF to DOC conversion failed")
                
        except Exception as e:
            self.pdf_to_doc_log.append(f"❌ Conversion error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Conversion error: {str(e)}")

    def _init_batch_processor(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Input dir
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input Directory:"))
        self.batch_input_dir = QLineEdit()
        input_layout.addWidget(self.batch_input_dir)
        input_browse = QPushButton("Browse")
        input_browse.clicked.connect(self._browse_batch_input_dir)
        input_layout.addWidget(input_browse)
        layout.addLayout(input_layout)

        # Output dir
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Directory:"))
        self.batch_output_dir = QLineEdit()
        output_layout.addWidget(self.batch_output_dir)
        output_browse = QPushButton("Browse")
        output_browse.clicked.connect(self._browse_batch_output_dir)
        output_layout.addWidget(output_browse)
        layout.addLayout(output_layout)

        # Operation type
        op_layout = QHBoxLayout()
        op_layout.addWidget(QLabel("Operation:"))
        self.batch_op_combo = QComboBox()
        self.batch_op_combo.addItems([
            "compress", "watermark", "encrypt", "split", "clean_metadata", "convert", "pdf_to_doc", "bypass_scribd"
        ])
        self.batch_op_combo.currentIndexChanged.connect(self._update_batch_op_options)
        op_layout.addWidget(self.batch_op_combo)
        layout.addLayout(op_layout)

        # Operation options area
        self.batch_op_options_widget = QWidget()
        self.batch_op_options_layout = QVBoxLayout(self.batch_op_options_widget)
        layout.addWidget(self.batch_op_options_widget)
        self._update_batch_op_options()

        # Progress bar
        self.batch_progress = QProgressBar()
        layout.addWidget(self.batch_progress)

        # Log
        self.batch_log = QTextEdit()
        self.batch_log.setReadOnly(True)
        layout.addWidget(self.batch_log)

        # Start/Cancel buttons
        btn_layout = QHBoxLayout()
        self.batch_start_btn = QPushButton("Start Batch")
        self.batch_start_btn.clicked.connect(self._start_batch_processing)
        btn_layout.addWidget(self.batch_start_btn)
        self.batch_cancel_btn = QPushButton("Cancel")
        self.batch_cancel_btn.setEnabled(False)
        btn_layout.addWidget(self.batch_cancel_btn)
        layout.addLayout(btn_layout)

        self.main_layout.addWidget(widget)
        self.function_widgets["Batch Processor"] = widget
        widget.setVisible(False)

    def _browse_batch_input_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if directory:
            self.batch_input_dir.setText(directory)

    def _browse_batch_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.batch_output_dir.setText(directory)

    def _update_batch_op_options(self):
        # Clear old options
        for i in reversed(range(self.batch_op_options_layout.count())):
            item = self.batch_op_options_layout.itemAt(i)
            widget = item.widget() if item else None
            if widget:
                widget.setParent(None)
        op = self.batch_op_combo.currentText()
        # Add options depending on operation
        if op == "compress":
            self.batch_compress_mode = QComboBox()
            self.batch_compress_mode.addItems(["low", "medium", "high"])
            self.batch_op_options_layout.addWidget(QLabel("Compression Mode:"))
            self.batch_op_options_layout.addWidget(self.batch_compress_mode)
        elif op == "watermark":
            self.batch_watermark_text = QLineEdit()
            self.batch_op_options_layout.addWidget(QLabel("Watermark Text:"))
            self.batch_op_options_layout.addWidget(self.batch_watermark_text)
        elif op == "encrypt":
            self.batch_encrypt_password = QLineEdit()
            self.batch_op_options_layout.addWidget(QLabel("Password:"))
            self.batch_op_options_layout.addWidget(self.batch_encrypt_password)
            self.batch_encrypt_level = QComboBox()
            self.batch_encrypt_level.addItems(["LOW", "MEDIUM", "HIGH"])
            self.batch_op_options_layout.addWidget(QLabel("Encryption Level:"))
            self.batch_op_options_layout.addWidget(self.batch_encrypt_level)
        elif op == "split":
            self.batch_split_pages = QLineEdit()
            self.batch_split_pages.setPlaceholderText("Pages per file (e.g. 1)")
            self.batch_op_options_layout.addWidget(QLabel("Pages per file:"))
            self.batch_op_options_layout.addWidget(self.batch_split_pages)
        elif op == "convert":
            self.batch_convert_type = QComboBox()
            self.batch_convert_type.addItems([
                "DOC/DOCX", "XLS/XLSX", "PPT/PPTX", "PNG", "JPG/JPEG", "EPUB"
            ])
            self.batch_op_options_layout.addWidget(QLabel("Convert Type:"))
            self.batch_op_options_layout.addWidget(self.batch_convert_type)
        elif op == "pdf_to_doc":
            self.batch_pdf_to_doc_include_images = QCheckBox("Include Images")
            self.batch_pdf_to_doc_include_images.setChecked(True)
            self.batch_op_options_layout.addWidget(self.batch_pdf_to_doc_include_images)
            self.batch_pdf_to_doc_ocr = QCheckBox("Use OCR (for scanned PDFs)")
            self.batch_pdf_to_doc_ocr.setChecked(False)
            self.batch_op_options_layout.addWidget(self.batch_pdf_to_doc_ocr)
        elif op == "bypass_scribd":
            self.batch_bypass_file_type = QComboBox()
            self.batch_bypass_file_type.addItems(["document", "book", "presentation", "academic"])
            self.batch_op_options_layout.addWidget(QLabel("File Type:"))
            self.batch_op_options_layout.addWidget(self.batch_bypass_file_type)
            self.batch_bypass_custom_title = QLineEdit()
            self.batch_bypass_custom_title.setPlaceholderText("Custom Title (optional)")
            self.batch_op_options_layout.addWidget(QLabel("Custom Title:"))
            self.batch_op_options_layout.addWidget(self.batch_bypass_custom_title)
        # clean_metadata: no extra options

    def _start_batch_processing(self):
        input_dir = self.batch_input_dir.text()
        output_dir = self.batch_output_dir.text()
        op = self.batch_op_combo.currentText()
        params = {}
        if op == "compress":
            params["mode"] = self.batch_compress_mode.currentText()
        elif op == "watermark":
            params["text"] = self.batch_watermark_text.text()
        elif op == "encrypt":
            params["password"] = self.batch_encrypt_password.text()
            params["encryption_level"] = self.batch_encrypt_level.currentText()
        elif op == "split":
            try:
                params["pages_per_file"] = int(self.batch_split_pages.text())
            except Exception:
                params["pages_per_file"] = 1
        elif op == "convert":
            params["file_type"] = self.batch_convert_type.currentText()
        elif op == "pdf_to_doc":
            params["include_images"] = self.batch_pdf_to_doc_include_images.isChecked()
            params["ocr_enabled"] = self.batch_pdf_to_doc_ocr.isChecked()
        elif op == "bypass_scribd":
            params["file_type"] = self.batch_bypass_file_type.currentText()
            params["custom_title"] = self.batch_bypass_custom_title.text()
        # clean_metadata: no extra params
        self.batch_log.clear()
        self.batch_progress.setValue(0)
        self.batch_start_btn.setEnabled(False)
        self.batch_cancel_btn.setEnabled(False)  # Not implemented
        def progress_callback(progress):
            self.batch_progress.setValue(int(progress["progress_percent"]))
            msg = f"{progress['processed']}/{progress['total']} | {progress['current_file']} | Failed: {progress['failed']}"
            self.batch_log.append(msg)
        if op == "pdf_to_doc":
            # Handle PDF to DOC batch processing separately
            result = batch_pdf_to_doc(input_dir, output_dir, 
                                    params.get("include_images", True),
                                    params.get("ocr_enabled", False))
            # Update progress to 100% when done
            self.batch_progress.setValue(100)
        else:
            result = process_pdf_directory(
                input_dir, output_dir, op, params, progress_callback=progress_callback
            )
        self.batch_log.append("\nBatch completed!")
        self.batch_log.append(str(result))
        self.batch_start_btn.setEnabled(True)

    def _init_duplicate_finder(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Input dir
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input Directory:"))
        self.dup_input_dir = QLineEdit()
        input_layout.addWidget(self.dup_input_dir)
        input_browse = QPushButton("Browse")
        input_browse.clicked.connect(self._browse_dup_input_dir)
        input_layout.addWidget(input_browse)
        layout.addLayout(input_layout)

        # Method
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Method:"))
        self.dup_method_combo = QComboBox()
        self.dup_method_combo.addItems(["size", "hash", "content"])
        method_layout.addWidget(self.dup_method_combo)
        layout.addLayout(method_layout)

        # Recursive
        self.dup_recursive = QCheckBox("Recursive")
        self.dup_recursive.setChecked(True)
        layout.addWidget(self.dup_recursive)

        # Log
        self.dup_log = QTextEdit()
        self.dup_log.setReadOnly(True)
        layout.addWidget(self.dup_log)

        # Start button
        btn_layout = QHBoxLayout()
        self.dup_start_btn = QPushButton("Find Duplicates")
        self.dup_start_btn.clicked.connect(self._start_duplicate_finder)
        btn_layout.addWidget(self.dup_start_btn)
        layout.addLayout(btn_layout)

        self.main_layout.addWidget(widget)
        self.function_widgets["Duplicate Finder"] = widget
        widget.setVisible(False)

    def _browse_dup_input_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if directory:
            self.dup_input_dir.setText(directory)

    def _start_duplicate_finder(self):
        input_dir = self.dup_input_dir.text()
        method = self.dup_method_combo.currentText()
        recursive = self.dup_recursive.isChecked()
        self.dup_log.clear()
        self.dup_log.append(f"Finding duplicates in: {input_dir}\nMethod: {method}\nRecursive: {recursive}")
        try:
            report = generate_duplicate_report(input_dir, recursive, method)
            if report['total_duplicate_groups'] == 0:
                self.dup_log.append("No duplicates found.")
            else:
                self.dup_log.append(f"Found {report['total_duplicate_groups']} groups, {report['total_duplicate_files']} duplicate files.")
                duplicate_groups = report.get('duplicate_groups', {})
                if isinstance(duplicate_groups, dict):
                    for group, info in duplicate_groups.items():
                        if isinstance(info, dict):
                            count = info.get('count', 0)
                            files = info.get('files', [])
                            self.dup_log.append(f"\nGroup: {group} ({count} files)")
                            for f in files:
                                self.dup_log.append(f"  {f}")
                summary = report.get('summary', {})
                if isinstance(summary, dict):
                    size_saved = summary.get('size_saved_mb', 0)
                    self.dup_log.append(f"\nPotential space saved: {size_saved:.2f} MB")
        except Exception as e:
            self.dup_log.append(f"Error: {str(e)}")

    def _init_metadata_cleaner(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Input file
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input PDF:"))
        self.meta_input = QLineEdit()
        input_layout.addWidget(self.meta_input)
        input_browse = QPushButton("Browse")
        input_browse.clicked.connect(self._browse_meta_input)
        input_layout.addWidget(input_browse)
        layout.addLayout(input_layout)

        # Output file
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output PDF:"))
        self.meta_output = QLineEdit()
        output_layout.addWidget(self.meta_output)
        output_browse = QPushButton("Browse")
        output_browse.clicked.connect(self._browse_meta_output)
        output_layout.addWidget(output_browse)
        layout.addLayout(output_layout)

        # Log
        self.meta_log = QTextEdit()
        self.meta_log.setReadOnly(True)
        layout.addWidget(self.meta_log)

        # Start button
        btn_layout = QHBoxLayout()
        self.meta_start_btn = QPushButton("Clean Metadata")
        self.meta_start_btn.clicked.connect(self._start_metadata_cleaner)
        btn_layout.addWidget(self.meta_start_btn)
        layout.addLayout(btn_layout)

        self.main_layout.addWidget(widget)
        self.function_widgets["Metadata Cleaner"] = widget
        widget.setVisible(False)

    def _browse_meta_input(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if filename:
            self.meta_input.setText(filename)
            base, _ = os.path.splitext(filename)
            self.meta_output.setText(f"{base}_cleaned.pdf")

    def _browse_meta_output(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Cleaned PDF As", "", "PDF Files (*.pdf)")
        if filename:
            self.meta_output.setText(filename)

    def _start_metadata_cleaner(self):
        input_pdf = self.meta_input.text()
        output_pdf = self.meta_output.text()
        self.meta_log.clear()
        self.meta_log.append(f"Cleaning metadata: {input_pdf} -> {output_pdf}")
        try:
            ok = remove_all_pdf_metadata(input_pdf, output_pdf)
            if ok:
                self.meta_log.append(f"✅ Cleaned metadata: {output_pdf}")
            else:
                self.meta_log.append("❌ Failed to clean metadata.")
        except Exception as e:
            self.meta_log.append(f"Error: {str(e)}")

    def _init_pdf_encryption(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Input file
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input PDF:"))
        self.enc_input = QLineEdit()
        input_layout.addWidget(self.enc_input)
        input_browse = QPushButton("Browse")
        input_browse.clicked.connect(self._browse_enc_input)
        input_layout.addWidget(input_browse)
        layout.addLayout(input_layout)

        # Output file
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output PDF:"))
        self.enc_output = QLineEdit()
        output_layout.addWidget(self.enc_output)
        output_browse = QPushButton("Browse")
        output_browse.clicked.connect(self._browse_enc_output)
        output_layout.addWidget(output_browse)
        layout.addLayout(output_layout)

        # Password
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Password:"))
        self.enc_password = QLineEdit()
        self.enc_password.setEchoMode(QLineEdit.Password)
        pass_layout.addWidget(self.enc_password)
        layout.addLayout(pass_layout)

        # Mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.enc_mode_combo = QComboBox()
        self.enc_mode_combo.addItems(["Encrypt", "Decrypt"])
        mode_layout.addWidget(self.enc_mode_combo)
        layout.addLayout(mode_layout)

        # Encryption level
        self.enc_level_combo = QComboBox()
        self.enc_level_combo.addItems(["LOW", "MEDIUM", "HIGH"])
        layout.addWidget(QLabel("Encryption Level:"))
        layout.addWidget(self.enc_level_combo)

        # Log
        self.enc_log = QTextEdit()
        self.enc_log.setReadOnly(True)
        layout.addWidget(self.enc_log)

        # Start button
        btn_layout = QHBoxLayout()
        self.enc_start_btn = QPushButton("Run")
        self.enc_start_btn.clicked.connect(self._start_pdf_encryption)
        btn_layout.addWidget(self.enc_start_btn)
        layout.addLayout(btn_layout)

        self.main_layout.addWidget(widget)
        self.function_widgets["PDF Encryption"] = widget
        widget.setVisible(False)

    def _browse_enc_input(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if filename:
            self.enc_input.setText(filename)
            base, _ = os.path.splitext(filename)
            self.enc_output.setText(f"{base}_encrypted.pdf")

    def _browse_enc_output(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save PDF As", "", "PDF Files (*.pdf)")
        if filename:
            self.enc_output.setText(filename)

    def _start_pdf_encryption(self):
        input_pdf = self.enc_input.text()
        output_pdf = self.enc_output.text()
        password = self.enc_password.text()
        mode = self.enc_mode_combo.currentText()
        level = self.enc_level_combo.currentText()
        self.enc_log.clear()
        self.enc_log.append(f"{mode}: {input_pdf} -> {output_pdf}")
        try:
            if mode == "Encrypt":
                from components.pdf_encryption import EncryptionLevel
                level_enum = getattr(EncryptionLevel, level)
                ok = encrypt_pdf_file(input_pdf, output_pdf, password, level_enum)
            else:
                ok = decrypt_pdf_file(input_pdf, output_pdf, password)
            if ok:
                self.enc_log.append(f"✅ {mode}ed PDF: {output_pdf}")
            else:
                self.enc_log.append(f"❌ Failed to {mode.lower()} PDF.")
        except Exception as e:
            self.enc_log.append(f"Error: {str(e)}")

    def _init_pdf_splitter(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Input file
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input PDF:"))
        self.split_input = QLineEdit()
        input_layout.addWidget(self.split_input)
        input_browse = QPushButton("Browse")
        input_browse.clicked.connect(self._browse_split_input)
        input_layout.addWidget(input_browse)
        layout.addLayout(input_layout)

        # Output dir
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Directory:"))
        self.split_output_dir = QLineEdit()
        output_layout.addWidget(self.split_output_dir)
        output_browse = QPushButton("Browse")
        output_browse.clicked.connect(self._browse_split_output_dir)
        output_layout.addWidget(output_browse)
        layout.addLayout(output_layout)

        # Pages per file
        pages_layout = QHBoxLayout()
        pages_layout.addWidget(QLabel("Pages per file:"))
        self.split_pages_per_file = QLineEdit()
        self.split_pages_per_file.setPlaceholderText("e.g. 1")
        pages_layout.addWidget(self.split_pages_per_file)
        layout.addLayout(pages_layout)

        # Log
        self.split_log = QTextEdit()
        self.split_log.setReadOnly(True)
        layout.addWidget(self.split_log)

        # Start button
        btn_layout = QHBoxLayout()
        self.split_start_btn = QPushButton("Split PDF")
        self.split_start_btn.clicked.connect(self._start_pdf_splitter)
        btn_layout.addWidget(self.split_start_btn)
        layout.addLayout(btn_layout)

        self.main_layout.addWidget(widget)
        self.function_widgets["PDF Splitter"] = widget
        widget.setVisible(False)

    def _browse_split_input(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if filename:
            self.split_input.setText(filename)

    def _browse_split_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.split_output_dir.setText(directory)

    def _start_pdf_splitter(self):
        input_pdf = self.split_input.text()
        output_dir = self.split_output_dir.text()
        try:
            pages_per_file = int(self.split_pages_per_file.text())
        except Exception:
            pages_per_file = 1
        self.split_log.clear()
        self.split_log.append(f"Splitting: {input_pdf} -> {output_dir} (pages per file: {pages_per_file})")
        try:
            files = split_pdf_by_pages_per_file(input_pdf, output_dir, pages_per_file)
            if files:
                self.split_log.append(f"✅ Split into {len(files)} files:")
                for f in files:
                    self.split_log.append(f"  {f}")
            else:
                self.split_log.append("❌ Failed to split PDF.")
        except Exception as e:
            self.split_log.append(f"Error: {str(e)}")

    def _init_watermark_pdf(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Input file
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input PDF:"))
        self.wm_input = QLineEdit()
        input_layout.addWidget(self.wm_input)
        input_browse = QPushButton("Browse")
        input_browse.clicked.connect(self._browse_wm_input)
        input_layout.addWidget(input_browse)
        layout.addLayout(input_layout)

        # Output file
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output PDF:"))
        self.wm_output = QLineEdit()
        output_layout.addWidget(self.wm_output)
        output_browse = QPushButton("Browse")
        output_browse.clicked.connect(self._browse_wm_output)
        output_layout.addWidget(output_browse)
        layout.addLayout(output_layout)

        # Watermark text
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Watermark Text:"))
        self.wm_text = QLineEdit()
        text_layout.addWidget(self.wm_text)
        layout.addLayout(text_layout)

        # Mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.wm_mode_combo = QComboBox()
        self.wm_mode_combo.addItems(["Add", "Remove"])
        mode_layout.addWidget(self.wm_mode_combo)
        layout.addLayout(mode_layout)

        # Log
        self.wm_log = QTextEdit()
        self.wm_log.setReadOnly(True)
        layout.addWidget(self.wm_log)

        # Start button
        btn_layout = QHBoxLayout()
        self.wm_start_btn = QPushButton("Run")
        self.wm_start_btn.clicked.connect(self._start_watermark_pdf)
        btn_layout.addWidget(self.wm_start_btn)
        layout.addLayout(btn_layout)

        self.main_layout.addWidget(widget)
        self.function_widgets["Watermark PDF"] = widget
        widget.setVisible(False)

    def _browse_wm_input(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if filename:
            self.wm_input.setText(filename)
            base, _ = os.path.splitext(filename)
            self.wm_output.setText(f"{base}_watermarked.pdf")

    def _browse_wm_output(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save PDF As", "", "PDF Files (*.pdf)")
        if filename:
            self.wm_output.setText(filename)

    def _start_watermark_pdf(self):
        input_pdf = self.wm_input.text()
        output_pdf = self.wm_output.text()
        text = self.wm_text.text()
        mode = self.wm_mode_combo.currentText()
        self.wm_log.clear()
        self.wm_log.append(f"{mode} watermark: {input_pdf} -> {output_pdf}")
        try:
            if mode == "Add":
                ok = add_watermark_to_pdf(input_pdf, output_pdf, text)
            else:
                ok = remove_watermark_from_pdf(input_pdf, output_pdf, text)
            if ok:
                self.wm_log.append(f"✅ {mode} watermark: {output_pdf}")
            else:
                self.wm_log.append(f"❌ Failed to {mode.lower()} watermark.")
        except Exception as e:
            self.wm_log.append(f"Error: {str(e)}")


def main() -> None:
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    
    # Initialize theme manager
    theme_manager = get_theme_manager()
    
    window = PDFUtilityToolkitPyQt()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 