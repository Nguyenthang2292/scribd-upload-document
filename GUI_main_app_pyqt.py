import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit, QFileDialog, QRadioButton, QButtonGroup, QMessageBox, QListWidget, QListWidgetItem, QGroupBox, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QMimeData, QPoint
from PyQt5.QtGui import QPixmap, QImage, QDrag
import os
import json
from pdf2image import convert_from_path
from PIL import Image
from components.scribd_bypass import ScribdBypass
from components.compress_pdf import compress_pdf
from components.merge_pages_landscape import merge_pdf_vertical_to_horizontal
from components.merge_pdf import merge_pdfs
from components.convert_to_pdf import epub_to_pdf, doc_to_pdf, xls_to_pdf, ppt_to_pdf, png_to_pdf, jpg_to_pdf
import config

class DraggableThumbFrame(QFrame):
    def __init__(self, parent, idx, on_drag_drop, on_double_click, thumbnails=None):
        super().__init__(parent)
        self.idx = idx
        self.on_drag_drop = on_drag_drop
        self.on_double_click = on_double_click
        self.setAcceptDrops(True)
        self.drag_start_pos = None
        self.thumbnails = thumbnails or []

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if (event.pos() - self.drag_start_pos).manhattanLength() > 10:
                drag = QDrag(self)
                mime = QMimeData()
                mime.setText(str(self.idx))
                drag.setMimeData(mime)
                # Hiệu ứng hình mờ toàn bộ khung (alpha 30%)
                pixmap = self.grab()
                img = pixmap.toImage().convertToFormat(QImage.Format_ARGB32)
                for y in range(img.height()):
                    for x in range(img.width()):
                        c = img.pixelColor(x, y)
                        c.setAlpha(int(255 * 0.3))
                        img.setPixelColor(x, y, c)
                faded_pixmap = QPixmap.fromImage(img)
                drag.setPixmap(faded_pixmap)
                drag.setHotSpot(event.pos())
                drag.exec_(Qt.DropAction.MoveAction)
        super().mouseMoveEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        from_idx = int(event.mimeData().text())
        to_idx = self.idx
        if from_idx != to_idx:
            self.on_drag_drop(from_idx, to_idx)
        event.acceptProposedAction()

    def mouseDoubleClickEvent(self, event):
        self.on_double_click(self.idx, event)

class PDFUtilityToolkitPyQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Utility Toolkit (PyQt)")
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        # Function selection
        self.function_options = sorted([
            "Bypass Scribd",
            "Compress PDF",
            "Convert to PDF",
            "Merge 2 Vertical Pages",
            "Merge PDFs"
        ])
        self.selected_function = QComboBox()
        self.selected_function.addItems(self.function_options)
        self.selected_function.currentIndexChanged.connect(self.switch_function)
        func_layout = QHBoxLayout()
        func_layout.addWidget(QLabel("Select Function:"))
        func_layout.addWidget(self.selected_function)
        self.main_layout.addLayout(func_layout)
        # Stacked function widgets
        self.function_widgets = {}
        self.init_bypass_scribd()
        self.init_convert_to_pdf()
        self.init_merge_vertical()
        self.init_merge_pdfs()
        self.init_compress_pdf()
        self.switch_function(0)

    def clear_function_widgets(self):
        for w in self.function_widgets.values():
            w.setVisible(False)

    def switch_function(self, idx):
        self.clear_function_widgets()
        func = self.function_options[idx]
        self.function_widgets[func].setVisible(True)

    # --- Bypass Scribd ---
    def init_bypass_scribd(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        # Input
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("PDF Input:"))
        self.scribd_input = QLineEdit()
        input_layout.addWidget(self.scribd_input)
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self.browse_scribd_input)
        input_layout.addWidget(btn_browse)
        layout.addLayout(input_layout)
        # Output
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Directory:"))
        self.scribd_output = QLineEdit()
        output_layout.addWidget(self.scribd_output)
        btn_out = QPushButton("Browse")
        btn_out.clicked.connect(self.browse_scribd_output)
        output_layout.addWidget(btn_out)
        layout.addLayout(output_layout)
        # Process
        btn_process = QPushButton("Bypass Scribd")
        btn_process.clicked.connect(self.process_scribd_bypass)
        layout.addWidget(btn_process)
        # Log
        self.scribd_log = QTextEdit()
        self.scribd_log.setReadOnly(True)
        layout.addWidget(self.scribd_log)
        self.main_layout.addWidget(w)
        self.function_widgets["Bypass Scribd"] = w
        w.setVisible(False)

    def browse_scribd_input(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if fname:
            self.scribd_input.setText(fname)

    def browse_scribd_output(self):
        dname = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dname:
            self.scribd_output.setText(dname)

    def process_scribd_bypass(self):
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

    # --- Convert to PDF ---
    def init_convert_to_pdf(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        # File type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Source File Type:"))
        self.convert_type = QComboBox()
        self.convert_type.addItems(["DOC/DOCX", "XLS/XLSX", "PPT/PPTX", "PNG", "JPG/JPEG", "EPUB"])
        self.convert_type.currentIndexChanged.connect(self.update_convert_label)
        type_layout.addWidget(self.convert_type)
        layout.addLayout(type_layout)
        # Input/output
        io_layout = QHBoxLayout()
        self.convert_input = QLineEdit()
        btn_in = QPushButton("Browse")
        btn_in.clicked.connect(self.browse_convert_input)
        self.convert_output = QLineEdit()
        btn_out = QPushButton("Browse")
        btn_out.clicked.connect(self.browse_convert_output)
        io_layout.addWidget(QLabel("Input File:"))
        io_layout.addWidget(self.convert_input)
        io_layout.addWidget(btn_in)
        io_layout.addWidget(QLabel("Output PDF:"))
        io_layout.addWidget(self.convert_output)
        io_layout.addWidget(btn_out)
        layout.addLayout(io_layout)
        # Process
        btn_process = QPushButton("Convert to PDF")
        btn_process.clicked.connect(self.process_convert_to_pdf)
        layout.addWidget(btn_process)
        # Log
        self.convert_log = QTextEdit()
        self.convert_log.setReadOnly(True)
        layout.addWidget(self.convert_log)
        self.main_layout.addWidget(w)
        self.function_widgets["Convert to PDF"] = w
        w.setVisible(False)
        self.update_convert_label()

    def update_convert_label(self):
        idx = self.convert_type.currentIndex()
        label = ["DOC/DOCX File:", "XLS/XLSX File:", "PPT/PPTX File:", "PNG File:", "JPG/JPEG File:", "EPUB File:"][idx]
        # (Không cần đổi label động vì đã có label cố định)

    def browse_convert_input(self):
        idx = self.convert_type.currentIndex()
        filters = [
            "Word files (*.doc *.docx)",
            "Excel files (*.xls *.xlsx)",
            "PowerPoint files (*.ppt *.pptx)",
            "PNG files (*.png)",
            "JPEG files (*.jpg *.jpeg)",
            "EPUB files (*.epub)"
        ]
        fname, _ = QFileDialog.getOpenFileName(self, "Select Input File", "", filters[idx])
        if fname:
            self.convert_input.setText(fname)
            base, _ = os.path.splitext(fname)
            self.convert_output.setText(base + ".pdf")

    def browse_convert_output(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save PDF As", "", "PDF Files (*.pdf)")
        if fname:
            self.convert_output.setText(fname)

    def process_convert_to_pdf(self):
        filetype = self.convert_type.currentText()
        input_file = self.convert_input.text()
        output_file = self.convert_output.text()
        if not input_file or not output_file:
            QMessageBox.critical(self, "Error", "Please select input file and output PDF file.")
            return
        self.convert_log.append(f"Converting {input_file} to {output_file} as {filetype}")
        try:
            if filetype == "DOC/DOCX":
                doc_to_pdf(input_file, output_file)
            elif filetype == "XLS/XLSX":
                xls_to_pdf(input_file, output_file)
            elif filetype == "PPT/PPTX":
                ppt_to_pdf(input_file, output_file)
            elif filetype == "PNG":
                png_to_pdf(input_file, output_file)
            elif filetype == "JPG/JPEG":
                jpg_to_pdf(input_file, output_file)
            elif filetype == "EPUB":
                epub_to_pdf(input_file, output_file)
            self.convert_log.append(f"✅ Converted successfully: {output_file}")
            QMessageBox.information(self, "Success", f"Converted successfully: {output_file}")
        except Exception as e:
            self.convert_log.append(f"❌ Conversion error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Conversion error: {str(e)}")

    # --- Merge 2 Vertical Pages ---
    def init_merge_vertical(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        # Input
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("PDF Input:"))
        self.merge_input = QLineEdit()
        input_layout.addWidget(self.merge_input)
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self.browse_merge_input)
        input_layout.addWidget(btn_browse)
        layout.addLayout(input_layout)
        # Output
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Directory:"))
        self.merge_output = QLineEdit()
        output_layout.addWidget(self.merge_output)
        btn_out = QPushButton("Browse")
        btn_out.clicked.connect(self.browse_merge_output)
        output_layout.addWidget(btn_out)
        layout.addLayout(output_layout)
        # Process
        btn_process = QPushButton("Merge 2 Vertical Pages")
        btn_process.clicked.connect(self.process_merge_vertical)
        layout.addWidget(btn_process)
        # Log
        self.merge_log = QTextEdit()
        self.merge_log.setReadOnly(True)
        layout.addWidget(self.merge_log)
        self.main_layout.addWidget(w)
        self.function_widgets["Merge 2 Vertical Pages"] = w
        w.setVisible(False)

    def browse_merge_input(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if fname:
            self.merge_input.setText(fname)

    def browse_merge_output(self):
        dname = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dname:
            self.merge_output.setText(dname)

    def process_merge_vertical(self):
        input_pdf = self.merge_input.text()
        output_dir = self.merge_output.text() or "output"
        if not input_pdf:
            QMessageBox.critical(self, "Error", "Please select an input PDF file")
            return
        base, _ = os.path.splitext(input_pdf)
        output_pdf = os.path.join(output_dir, os.path.basename(base) + "_2in1.pdf")
        self.merge_log.append(f"Merging: {input_pdf} -> {output_pdf}")
        try:
            merge_pdf_vertical_to_horizontal(input_pdf, output_pdf)
            self.merge_log.append(f"✅ Merged: {output_pdf}")
            QMessageBox.information(self, "Success", f"Merged: {output_pdf}")
        except Exception as e:
            self.merge_log.append(f"❌ Merge error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Merge error: {str(e)}")

    # --- Merge PDFs ---
    def init_merge_pdfs(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        # Input
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("PDF Files (separate by ;):"))
        self.mergepdf_input = QLineEdit()
        self.mergepdf_input.textChanged.connect(self.refresh_mergepdf_preview)
        input_layout.addWidget(self.mergepdf_input)
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self.browse_mergepdf_input)
        input_layout.addWidget(btn_browse)
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
        btns_hbox = QHBoxLayout()
        btn_refresh = QPushButton("Refresh Preview")
        btn_refresh.clicked.connect(self.refresh_mergepdf_preview)
        btns_hbox.addWidget(btn_refresh)
        btn_delete = QPushButton("Delete Selected")
        btn_delete.clicked.connect(self.delete_selected_mergepdf_files)
        btns_hbox.addWidget(btn_delete)
        preview_vbox.addLayout(btns_hbox)
        layout.addWidget(preview_group)
        # Output
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output PDF:"))
        self.mergepdf_output = QLineEdit()
        output_layout.addWidget(self.mergepdf_output)
        btn_out = QPushButton("Browse")
        btn_out.clicked.connect(self.browse_mergepdf_output)
        output_layout.addWidget(btn_out)
        layout.addLayout(output_layout)
        # Process
        btn_process = QPushButton("Merge PDFs")
        btn_process.clicked.connect(self.process_merge_pdfs)
        layout.addWidget(btn_process)
        # Log
        self.mergepdf_log = QTextEdit()
        self.mergepdf_log.setReadOnly(True)
        layout.addWidget(self.mergepdf_log)
        self.main_layout.addWidget(w)
        self.function_widgets["Merge PDFs"] = w
        w.setVisible(False)
        # State for preview
        self.mergepdf_files = []  # List of dict: {path, selected, thumbnails}
        self.mergepdf_thumbnails = []  # List of QPixmap objects to keep refs
        self.last_selected_idx = None
        self.refresh_mergepdf_preview()

    def refresh_mergepdf_preview(self):
        # Clear preview
        for i in reversed(range(self.preview_hbox.count())):
            item = self.preview_hbox.itemAt(i)
            widget = item.widget() if item else None
            if widget:
                widget.setParent(None)
        self.mergepdf_thumbnails = []
        # Get file list
        input_val = self.mergepdf_input.text()
        if os.path.isdir(input_val):
            pdf_files = sorted(str(p.path) for p in os.scandir(input_val) if p.name.lower().endswith('.pdf'))
        else:
            pdf_files = [f.strip() for f in input_val.split(';') if f.strip()]
        # Build file dicts
        old_files = getattr(self, 'mergepdf_files', [])
        old_selected = {f['path']: f.get('selected', False) for f in old_files if isinstance(f, dict)}
        self.mergepdf_files = []
        for pdf in pdf_files:
            thumbs = self.get_pdf_thumbnails_pyqt(pdf, num_pages=3)
            self.mergepdf_thumbnails.append(thumbs)
            self.mergepdf_files.append({'path': pdf, 'selected': old_selected.get(pdf, False), 'thumbnails': thumbs})
        # Show thumbnails
        for idx, fileinfo in enumerate(self.mergepdf_files):
            thumb_frame = DraggableThumbFrame(self.preview_frame, idx, self.on_drag_drop_mergepdf, self.toggle_select_mergepdf, fileinfo['thumbnails'])
            thumb_frame.setFrameShape(QFrame.StyledPanel)
            thumb_frame.setStyleSheet(f"background: {'#bfefff' if fileinfo['selected'] else '#f0f0f0'};")
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
            del_btn.clicked.connect(lambda _, i=idx: self.delete_mergepdf_file(i))
            thumb_vbox.addWidget(del_btn)
            self.preview_hbox.addWidget(thumb_frame)

    def get_pdf_thumbnails_pyqt(self, pdf_path, num_pages=3):
        thumbs = []
        try:
            images = convert_from_path(pdf_path, first_page=1, last_page=num_pages, size=(60, 80))
            for img in images:
                if isinstance(img, Image.Image):
                    img = img.convert('RGB')
                    data = img.tobytes('raw', 'RGB')
                    qimg = QImage(data, img.width, img.height, QImage.Format_RGB888)
                    thumbs.append(QPixmap.fromImage(qimg))
        except Exception:
            img = Image.new("RGB", (60, 80), color="gray")
            data = img.tobytes('raw', 'RGB')
            qimg = QImage(data, img.width, img.height, QImage.Format_RGB888)
            thumbs.append(QPixmap.fromImage(qimg))
        return thumbs

    def toggle_select_mergepdf(self, idx, event):
        for i, f in enumerate(self.mergepdf_files):
            f['selected'] = (i == idx)
        self.last_selected_idx = idx
        self.refresh_mergepdf_preview()

    def delete_mergepdf_file(self, idx):
        del self.mergepdf_files[idx]
        self.mergepdf_input.setText(';'.join(f['path'] for f in self.mergepdf_files))
        self.refresh_mergepdf_preview()

    def delete_selected_mergepdf_files(self):
        self.mergepdf_files = [f for f in self.mergepdf_files if not f['selected']]
        self.mergepdf_input.setText(';'.join(f['path'] for f in self.mergepdf_files))
        self.refresh_mergepdf_preview()

    def browse_mergepdf_input(self):
        fnames, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
        if fnames:
            self.mergepdf_input.setText(';'.join(fnames))

    def browse_mergepdf_output(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF As", "", "PDF Files (*.pdf)")
        if fname:
            self.mergepdf_output.setText(fname)

    def process_merge_pdfs(self):
        pdf_files = [f.strip() for f in self.mergepdf_input.text().split(';') if f.strip()]
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
            QMessageBox.information(self, "Success", f"Merged successfully: {output_pdf}")
        except Exception as e:
            self.mergepdf_log.append(f"❌ Merge error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Merge error: {str(e)}")

    # --- Compress PDF ---
    def init_compress_pdf(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        # Input
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("PDF File:"))
        self.compress_input = QLineEdit()
        input_layout.addWidget(self.compress_input)
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self.browse_compress_input)
        input_layout.addWidget(btn_browse)
        layout.addLayout(input_layout)
        # Output
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output PDF:"))
        self.compress_output = QLineEdit()
        output_layout.addWidget(self.compress_output)
        btn_out = QPushButton("Browse")
        btn_out.clicked.connect(self.browse_compress_output)
        output_layout.addWidget(btn_out)
        layout.addLayout(output_layout)
        # Compression level
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
        # Process
        btn_process = QPushButton("Compress PDF")
        btn_process.clicked.connect(self.process_compress_pdf)
        layout.addWidget(btn_process)
        # Log
        self.compress_log = QTextEdit()
        self.compress_log.setReadOnly(True)
        layout.addWidget(self.compress_log)
        self.main_layout.addWidget(w)
        self.function_widgets["Compress PDF"] = w
        w.setVisible(False)

    def browse_compress_input(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if fname:
            self.compress_input.setText(fname)
            base, _ = os.path.splitext(fname)
            self.compress_output.setText(base + "_compressed.pdf")

    def browse_compress_output(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save Compressed PDF As", "", "PDF Files (*.pdf)")
        if fname:
            self.compress_output.setText(fname)

    def process_compress_pdf(self):
        input_pdf = self.compress_input.text()
        output_pdf = self.compress_output.text()
        mode = 'medium'
        if self.rb_low.isChecked():
            mode = 'low'
        elif self.rb_high.isChecked():
            mode = 'high'
        if not input_pdf or not output_pdf:
            QMessageBox.critical(self, "Error", "Please select input and output PDF file.")
            return
        self.compress_log.append(f"Compressing {input_pdf} to {output_pdf} (mode: {mode})")
        try:
            compress_pdf(input_pdf, output_pdf, mode)
            self.compress_log.append(f"✅ Compressed successfully: {output_pdf}")
            QMessageBox.information(self, "Success", f"Compressed successfully: {output_pdf}")
        except Exception as e:
            self.compress_log.append(f"❌ Compression error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Compression error: {str(e)}")

    def on_drag_drop_mergepdf(self, from_idx, to_idx):
        if from_idx < 0 or to_idx < 0 or from_idx >= len(self.mergepdf_files) or to_idx >= len(self.mergepdf_files):
            return
        file = self.mergepdf_files.pop(from_idx)
        self.mergepdf_files.insert(to_idx, file)
        self.mergepdf_input.setText(';'.join(f['path'] for f in self.mergepdf_files))
        self.refresh_mergepdf_preview()

def main():
    app = QApplication(sys.argv)
    window = PDFUtilityToolkitPyQt()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 