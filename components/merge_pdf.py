import os
import tempfile
import shutil
import subprocess
from typing import List
from PIL import Image
import PyPDF2

# Optional: import docx2pdf if available
try:
    from docx2pdf import convert as docx2pdf_convert
except ImportError:
    docx2pdf_convert = None

def convert_image_to_pdf(image_path: str, output_pdf: str):
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img.save(output_pdf, 'PDF')

def convert_doc_to_pdf(doc_path: str, output_pdf: str):
    if docx2pdf_convert and doc_path.lower().endswith(('.docx', '.doc')):
        # Use docx2pdf (requires MS Word on Windows)
        docx2pdf_convert(doc_path, output_pdf)
    else:
        # Fallback: use unoconv/libreoffice
        subprocess.run(['unoconv', '-f', 'pdf', '-o', output_pdf, doc_path], check=True)

def convert_xls_to_pdf(xls_path: str, output_pdf: str):
    # Use unoconv/libreoffice
    subprocess.run(['unoconv', '-f', 'pdf', '-o', output_pdf, xls_path], check=True)

def convert_ppt_to_pdf(ppt_path: str, output_pdf: str):
    # Use unoconv/libreoffice
    subprocess.run(['unoconv', '-f', 'pdf', '-o', output_pdf, ppt_path], check=True)

def merge_pdfs(input_files: List[str], output_file: str):
    """
    Merge multiple files (PDF, DOC, XLS, PPT, PNG, JPG) into a single PDF.
    Args:
        input_files (List[str]): List of file paths to merge (in order).
        output_file (str): Output PDF file path.
    """
    temp_dir = tempfile.mkdtemp()
    pdf_files = []
    temp_files = []
    try:
        for f in input_files:
            ext = os.path.splitext(f)[1].lower()
            if ext == '.pdf':
                pdf_files.append(f)
            elif ext in ['.png', '.jpg', '.jpeg']:
                temp_pdf = os.path.join(temp_dir, os.path.basename(f) + '.pdf')
                convert_image_to_pdf(f, temp_pdf)
                pdf_files.append(temp_pdf)
                temp_files.append(temp_pdf)
            elif ext in ['.doc', '.docx']:
                temp_pdf = os.path.join(temp_dir, os.path.basename(f) + '.pdf')
                convert_doc_to_pdf(f, temp_pdf)
                pdf_files.append(temp_pdf)
                temp_files.append(temp_pdf)
            elif ext in ['.xls', '.xlsx']:
                temp_pdf = os.path.join(temp_dir, os.path.basename(f) + '.pdf')
                convert_xls_to_pdf(f, temp_pdf)
                pdf_files.append(temp_pdf)
                temp_files.append(temp_pdf)
            elif ext in ['.ppt', '.pptx']:
                temp_pdf = os.path.join(temp_dir, os.path.basename(f) + '.pdf')
                convert_ppt_to_pdf(f, temp_pdf)
                pdf_files.append(temp_pdf)
                temp_files.append(temp_pdf)
            else:
                raise ValueError(f"Unsupported file type: {f}")
        merger = PyPDF2.PdfMerger()
        for pdf in pdf_files:
            merger.append(pdf)
        merger.write(output_file)
        merger.close()
    finally:
        # Clean up temp files
        shutil.rmtree(temp_dir, ignore_errors=True)
