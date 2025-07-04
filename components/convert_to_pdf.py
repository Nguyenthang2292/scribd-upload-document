import os
import tempfile
import shutil
import posixpath
from ebooklib import epub
from ebooklib import ITEM_DOCUMENT
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
from fpdf import FPDF
from PIL import Image


def epub_to_pdf(epub_path, pdf_path):
    FONT_PATH = os.path.join(os.path.dirname(__file__), 'dejavu-sans ttf', 'DejaVuSans.ttf')
    book = epub.read_epub(epub_path)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_font('DejaVu', '', FONT_PATH, uni=True)
    pdf.set_font('DejaVu', '', 12)
    temp_dir = tempfile.mkdtemp()
    try:
        for item in book.get_items():
            if item.get_type() == ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                render_html_to_pdf(soup, pdf, book, temp_dir)
                pdf.add_page()
        pdf.output(pdf_path)
        print(f"Đã chuyển đổi {epub_path} thành {pdf_path}")
    finally:
        shutil.rmtree(temp_dir)


def render_html_to_pdf(soup, pdf, book, temp_dir):
    for elem in soup.descendants:
        if isinstance(elem, NavigableString):
            text = str(elem).strip()
            if text:
                pdf.multi_cell(0, 10, text)
        elif isinstance(elem, Tag) and elem.name == 'img':
            src = elem.get('src')
            if src:
                img_path = save_epub_image(book, src, temp_dir)
                if img_path:
                    try:
                        pdf.ln(2)
                        pdf.image(img_path, w=pdf.w * 0.6)
                        pdf.ln(2)
                    except Exception as e:
                        print(f"Không thể chèn ảnh: {img_path} - {e}")


def save_epub_image(book, src, temp_dir):
    src_norm = posixpath.normpath(src).lstrip('./')
    for item in book.get_items():
        item_name = posixpath.normpath(item.get_name()).lstrip('./')
        ext = os.path.splitext(item_name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif']:
            if item_name.endswith(src_norm) or os.path.basename(item_name) == os.path.basename(src_norm):
                img_path = os.path.join(temp_dir, os.path.basename(item_name))
                with open(img_path, 'wb') as f:
                    f.write(item.get_content())
                return img_path
    print(f"[DEBUG] Không tìm thấy ảnh cho src: {src}. Danh sách item: {[item.get_name() for item in book.get_items()]}")
    return None


def doc_to_pdf(doc_path, pdf_path):
    try:
        from docx2pdf import convert
        convert(doc_path, pdf_path)
    except ImportError:
        raise RuntimeError("docx2pdf is required for DOC/DOCX to PDF conversion.")


def xls_to_pdf(xls_path, pdf_path):
    import subprocess
    subprocess.run(['unoconv', '-f', 'pdf', '-o', pdf_path, xls_path], check=True)


def ppt_to_pdf(ppt_path, pdf_path):
    import subprocess
    subprocess.run(['unoconv', '-f', 'pdf', '-o', pdf_path, ppt_path], check=True)


def png_to_pdf(png_path, pdf_path):
    img = Image.open(png_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img.save(pdf_path, 'PDF')


def jpg_to_pdf(jpg_path, pdf_path):
    img = Image.open(jpg_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img.save(pdf_path, 'PDF') 