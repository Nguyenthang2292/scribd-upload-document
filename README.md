# PDF Utility Toolkit

A powerful toolkit for advanced PDF processing with a modern, user-friendly PyQt5 GUI and comprehensive batch capabilities.

## Main Features

- ✅ **Bypass Scribd**: Create Scribd-compatible PDFs (single or batch)
- ✅ **EPUB to PDF**: Convert EPUB files to PDF
- ✅ **DOC to PDF**: Convert DOC/DOCX files to PDF
- ✅ **XLS to PDF**: Convert XLS/XLSX files to PDF
- ✅ **PPT to PDF**: Convert PPT/PPTX files to PDF
- ✅ **PNG to PDF**: Convert PNG images to PDF
- ✅ **JPG to PDF**: Convert JPG/JPEG images to PDF
- ✅ **PDF to DOC**: Convert PDF files to DOC/DOCX format with OCR support
- ✅ **Merge 2 Vertical Pages**: Combine every two consecutive portrait pages into one landscape page (single or batch)
- ✅ **Merge PDFs**: Merge multiple PDFs and other supported formats (DOC, XLS, PPT, PNG, JPG) into a single PDF with drag & drop reordering
- ✅ **Compress PDF**: Reduce PDF file size with 3 compression levels (Low, Medium, High)
- ✅ **Batch Processor**: Advanced batch processing with progress tracking and multiple operation types
- ✅ **Duplicate Finder**: Find duplicate PDFs by size, hash, or content analysis
- ✅ **Metadata Cleaner**: Remove all metadata from PDFs for privacy
- ✅ **PDF Encryption**: Encrypt/decrypt PDFs with password protection and selectable encryption levels
- ✅ **PDF Splitter**: Split PDFs into multiple files by number of pages
- ✅ **Watermark PDF**: Add or remove text watermarks from PDFs
- ✅ **Modern PyQt5 GUI**: Professional interface with theme switching (Light/Dark/Auto), drag & drop, preview thumbnails
- ✅ **Detailed Logging**: Track progress and results in real-time
- ✅ **Error Handling**: Robust error handling and reporting

## Changelog

### v3.1.0 (Current)

- ✅ **PDF to DOC Conversion**: Convert PDF files to DOC/DOCX format with OCR support
- ✅ **Advanced Text Extraction**: Multiple extraction methods including PyPDF2, PyMuPDF, and OCR
- ✅ **Image Preservation**: Option to include or exclude images in DOC conversion
- ✅ **OCR Support**: Optical Character Recognition for scanned PDFs
- ✅ **Batch PDF to DOC**: Process multiple PDF files to DOC format simultaneously

### v3.0.0

- ✅ **Complete PyQt5 GUI Overhaul**: Modern, professional interface with theme support
- ✅ **Advanced Theme System**: Light/Dark/Auto themes with customizable colors
- ✅ **Batch Processor**: Comprehensive batch processing with multiple operation types
- ✅ **Duplicate Finder**: Find and manage duplicate PDFs with detailed reporting
- ✅ **Metadata Cleaner**: Remove sensitive metadata from PDFs
- ✅ **PDF Encryption**: Secure PDF encryption/decryption with multiple levels
- ✅ **PDF Splitter**: Split large PDFs into smaller files
- ✅ **Watermark PDF**: Add or remove watermarks from PDFs
- ✅ **Enhanced Merge PDFs**: Drag & drop reordering, preview thumbnails, multi-format support
- ✅ **Progress Tracking**: Real-time progress bars and detailed logging
- ✅ **Modular Architecture**: Clean component-based structure for easy maintenance

### v2.3.1

- ✅ Add PyQt5 GUI to enhance UI/UX

### v2.3.0

- ✅ Remove Hash Changer feature
- ✅ Add DOC, XLS, PPT, PNG, JPG to PDF conversion (GUI & CLI)
- ✅ Refactor: all file-to-PDF conversion in convert_to_pdf.py

### v2.2.0

- ✅ Add PDF compression with 3 modes: low, medium, high (using PyMuPDF)
- ✅ Add GUI for PDF compression
- ✅ Refactor README for clarity and completeness

### v2.1.0

- ✅ Merge multiple file formats (PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, PNG, JPG) into a single PDF
- ✅ Auto-convert images and Office files to PDF before merging
- ✅ Clean up temporary files after merging
- ⚠️ Requires: Pillow, docx2pdf (for Word), unoconv/LibreOffice (for Excel/PowerPoint)

### v2.0.0

- ✅ Refactor the entire codebase
- ✅ Add GUI application
- ✅ Add batch processing
- ✅ Improve error handling
- ✅ Add logging system
- ✅ Add configuration system
- ✅ Add CLI arguments
- ✅ Add progress tracking
- ✅ Add detailed reporting

### v1.0.0 (Original)

- ✅ Basic PDF hash changing
- ✅ Random filename generation

## Supported Formats

- PDF
- DOC, DOCX (Word)
- XLS, XLSX (Excel)
- PPT, PPTX (PowerPoint)
- PNG, JPG, JPEG (Images)
- EPUB (to PDF)

## Installation

### System Requirements

- Python 3.7+
- Windows/Linux/macOS

### Install dependencies

```bash
pip install -r requirements.txt
```

**Note:**

- To use the Merge 2 Vertical Pages feature, you must install Poppler:

  - **Windows:**

        1. Download Poppler: https://github.com/oschwartz10612/poppler-windows/releases/
        2. Extract, e.g., to C:\poppler-xx\
        3. Add the `bin` folder (e.g., `C:\poppler-xx\Library\bin` or `C:\poppler-xx\bin`) to your PATH environment variable.
        4. Open a new Command Prompt and check: `pdftoppm -h` (should show help message).
    - **Linux:**

        ```bash
        sudo apt install poppler-utils
        ```

    - **Mac:**

        ```bash
        brew install poppler
        ```

- For merging and compressing PDFs, you may need:
  - `pillow` (for image to PDF conversion)
  - `docx2pdf` (for Word to PDF, requires Microsoft Word on Windows)
  - `unoconv` or `libreoffice` (for Excel/PowerPoint to PDF)
  - `pymupdf` (for PDF compression and text extraction)
  - `PyPDF2` (for PDF merging and text extraction)
  - `PyQt5` (for modern GUI)
  - `fitz` (alias for pymupdf, but use pymupdf)
  - `python-docx` (for creating DOC files)
  - `pytesseract` (for OCR text extraction)
  - `pdf2image` (for PDF to image conversion)

### Install extra dependencies

```bash
pip install pillow docx2pdf pymupdf PyPDF2 PyQt5 python-docx pytesseract pdf2image
# For Linux, also install unoconv/libreoffice and tesseract:
sudo apt install unoconv libreoffice tesseract-ocr
# For Windows, download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
```

## Usage

### 1. Graphical User Interface (GUI)

#### PyQt5 GUI (Modern, Professional Interface)

```bash
python GUI_main_app_pyqt.py
```

**GUI Features:**

- **Modern Interface**: Professional PyQt5-based GUI with theme support
- **Theme Switching**: Light/Dark/Auto themes with customizable colors
- **Function Selection**: Dropdown menu to select from 11 different PDF operations
- **Drag & Drop**: Support for dragging files and folders directly into the interface
- **Preview System**: Thumbnail previews for PDF merging with drag & drop reordering
- **Real-time Progress**: Progress bars and detailed logging for all operations
- **Batch Processing**: All functions support both single file and batch processing
- **Advanced Options**: Operation-specific settings and parameters

**Available Functions:**

1. **Bypass Scribd**: Create Scribd-compatible files
2. **Compress PDF**: Reduce file size with quality options
3. **Convert to PDF**: Convert various formats to PDF
4. **PDF to DOC**: Convert PDF files to DOC/DOCX with OCR support
5. **Merge 2 Vertical Pages**: Combine portrait pages into landscape
6. **Merge PDFs**: Merge multiple files with preview and reordering
7. **Batch Processor**: Advanced batch operations with progress tracking
8. **Duplicate Finder**: Find duplicate files with detailed analysis
9. **Metadata Cleaner**: Remove sensitive metadata
10. **PDF Encryption**: Secure encryption/decryption
11. **PDF Splitter**: Split large PDFs into smaller files
12. **Watermark PDF**: Add or remove watermarks

### 2. Command Line Interface (CLI)

#### DOC to PDF

```bash
python components/convert_to_pdf.py --doc input.docx --pdf output.pdf
```

#### XLS to PDF

```bash
python components/convert_to_pdf.py --xls input.xlsx --pdf output.pdf
```

#### PPT to PDF

```bash
python components/convert_to_pdf.py --ppt input.pptx --pdf output.pdf
```

#### PNG to PDF

```bash
python components/convert_to_pdf.py --png input.png --pdf output.pdf
```

#### JPG to PDF

```bash
python components/convert_to_pdf.py --jpg input.jpg --pdf output.pdf
```

#### EPUB to PDF

```bash
python components/convert_to_pdf.py --epub input.epub --pdf output.pdf
```

#### PDF to DOC

```bash
python components/pdf_to_doc.py input.pdf output.docx --ocr
```

#### Merge PDFs (multi-format)

```bash
python components/merge_pdf.py file1.pdf file2.docx file3.jpg output.pdf
```

#### Compress PDF

```bash
python components/compress_pdf.py input.pdf output.pdf --mode medium
```

## Project Structure

```
scribd-upload-document/
├── components/
│   ├── convert_to_pdf.py         # All file-to-PDF conversion logic
│   ├── pdf_to_doc.py             # PDF to DOC/DOCX conversion logic
│   ├── batch_processor.py        # Advanced batch processing functionality
│   ├── duplicate_finder.py       # Duplicate detection and analysis
│   ├── metadata_cleaner.py       # PDF metadata removal
│   ├── pdf_encryption.py         # PDF encryption/decryption
│   ├── pdf_splitter.py           # PDF splitting functionality
│   ├── watermark_pdf.py          # Watermark addition/removal
│   ├── scribd_bypass.py          # Scribd bypass logic
│   ├── merge_pages_landscape.py  # Merge 2 vertical pages logic
│   ├── merge_pdf.py              # Merge PDFs and multi-format logic
│   ├── compress_pdf.py           # PDF compression logic
│   └── config.py                 # Configuration settings
├── components_UI/
│   ├── DraggableThumbFrame.py    # Custom UI components for drag & drop
│   └── ThemeSettingsDialog.py    # Theme configuration dialog
├── theme/
│   ├── theme_manager.py          # Theme management system
│   ├── dark/                     # Dark theme assets
│   └── light/                    # Light theme assets
├── GUI_main_app_pyqt.py          # Modern PyQt5 GUI application
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── dejavu-sans ttf/              # Font files
└── output/                       # Default output directory (created at runtime)
```

## Configuration

Edit `config.py` to customize:

- **Default output directory**
- **Number of workers for parallel processing**
- **Logging setup**
- **GUI setup**

## Advanced Features

### 1. Theme System

- **Light/Dark/Auto Themes**: Automatic theme switching based on system preference
- **Customizable Colors**: Modify theme colors through the theme settings dialog
- **Persistent Settings**: Theme preferences are saved between sessions

### 2. Batch Processing

- **Multiple Operation Types**: Compress, watermark, encrypt, split, clean metadata, convert
- **Progress Tracking**: Real-time progress bars and detailed logging
- **Error Handling**: Continue processing even if individual files fail
- **Operation-Specific Options**: Configure parameters for each batch operation

### 3. Duplicate Detection

- **Multiple Detection Methods**: Size-based, hash-based, and content-based detection
- **Detailed Reporting**: Comprehensive reports with file groups and space savings
- **Recursive Scanning**: Option to scan subdirectories

### 4. PDF Security

- **Encryption Levels**: Low, Medium, and High encryption options
- **Password Protection**: Secure password-based encryption/decryption
- **Metadata Cleaning**: Remove sensitive information from PDFs

### 5. Parallel Processing

- Automatic detection of CPU cores
- Customizable number of workers
- Optimized performance for large files

### 6. Error Handling

- Handle corrupted files
- Log detailed error messages
- Continue processing on error

### 7. Detailed Reporting

- Processing time for each file
- Total processing time
- Success/Failure ratio
- Output file path

## Troubleshooting

### Common Issues

1. **File Not Found**

   ```
   Error: File not found: input.pdf
   ```

   **Solution**: Verify the file path

2. **Permission Denied**

   ```
   Error: Permission denied
   ```

   **Solution**: Run with admin privileges or change output directory

3. **Theme Loading Issues**

   ```
   Warning: Could not load theme
   ```

   **Solution**: The application will fall back to default theme

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python components/convert_to_pdf.py --doc input.docx --pdf output.pdf --verbose
```

## Contribution

1. Fork the project
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License - see LICENSE for more details.
