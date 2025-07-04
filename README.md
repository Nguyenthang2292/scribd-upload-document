# PDF Utility Toolkit

A powerful toolkit for advanced PDF processing with a modern, user-friendly GUI and batch capabilities.

## Main Features

- ✅ **Bypass Scribd**: Create Scribd-compatible PDFs (single or batch)
- ✅ **EPUB to PDF**: Convert EPUB files to PDF
- ✅ **DOC to PDF**: Convert DOC/DOCX files to PDF
- ✅ **XLS to PDF**: Convert XLS/XLSX files to PDF
- ✅ **PPT to PDF**: Convert PPT/PPTX files to PDF
- ✅ **PNG to PDF**: Convert PNG images to PDF
- ✅ **JPG to PDF**: Convert JPG/JPEG images to PDF
- ✅ **Merge 2 Vertical Pages**: Combine every two consecutive portrait pages into one landscape page (single or batch)
- ✅ **Merge PDFs**: Merge multiple PDFs and other supported formats (DOC, XLS, PPT, PNG, JPG) into a single PDF
- ✅ **Compress PDF**: Reduce PDF file size with 3 compression levels (Low, Medium, High)
- ✅ **Batch Processing**: All main features support both single file and batch (directory) mode
- ✅ **Detailed Logging**: Track progress and results
- ✅ **Error Handling**: Robust error handling and reporting

## Changelog

### v2.3.0 (Current)
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
    - `pymupdf` (for PDF compression)

### Install extra dependencies
```bash
pip install pillow docx2pdf pymupdf
# For Linux, also install unoconv/libreoffice:
sudo apt install unoconv libreoffice
```

## Usage

### 1. Graphical User Interface (GUI)
```bash
python GUI_main_app.py
```

**GUI Features:**
- Select the main function from the **dropdown menu** at the top (Bypass Scribd, EPUB to PDF, DOC to PDF, XLS to PDF, PPT to PDF, PNG to PDF, JPG to PDF, Merge 2 Vertical Pages, Merge PDFs, Compress PDF)
- Each function supports both **Single File** and **Batch Processing** (directory)
- Track progress and logs in real time
- All function names and UI are in English
- **Merge PDFs**: Drag & drop, reorder, multi-format support, auto output name
- **Compress PDF**: Choose file, compression level, and output location

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
#### Merge PDFs (multi-format)
```bash
python components/merge_pdf.py file1.pdf file2.docx file3.jpg output.pdf
```
#### Compress PDF
```bash
python components/zip_pdf.py input.pdf output.pdf --mode medium
```

## Project Structure

```
scribd-upload-document/
├── components/
│   ├── convert_to_pdf.py         # All file-to-PDF conversion logic
│   ├── batch_processor.py        # Batch processing functionality
│   ├── scribd_bypass.py          # Scribd bypass logic
│   ├── merge_pages_landscape.py  # Merge 2 vertical pages logic
│   ├── merge_pdf.py              # Merge PDFs and multi-format logic
│   ├── zip_pdf.py                # PDF compression logic
│   └── config.py                 # Configuration settings
├── GUI_main_app.py               # GUI application
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

### 1. Parallel Processing
- Automatic detection of CPU cores
- Customizable number of workers
- Optimized performance for large files

### 2. Error Handling
- Handle corrupted files
- Log detailed error messages
- Continue processing on error

### 3. Detailed Reporting
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
