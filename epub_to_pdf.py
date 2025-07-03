from ebooklib import epub
from ebooklib import ITEM_DOCUMENT
from bs4 import BeautifulSoup, NavigableString, Tag
from fpdf import FPDF
import sys
import os
import tempfile
import shutil
import posixpath

FONT_PATH = os.path.join(os.path.dirname(__file__), 'dejavu-sans ttf', 'DejaVuSans.ttf')

def save_epub_image(book, src, temp_dir):
    # Normalize đường dẫn ảnh
    src_norm = posixpath.normpath(src).lstrip('./')
    for item in book.get_items():
        item_name = posixpath.normpath(item.get_name()).lstrip('./')
        ext = os.path.splitext(item_name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif']:
            # So sánh phần cuối đường dẫn (ảnh thường nằm trong thư mục con)
            if item_name.endswith(src_norm) or os.path.basename(item_name) == os.path.basename(src_norm):
                img_path = os.path.join(temp_dir, os.path.basename(item_name))
                with open(img_path, 'wb') as f:
                    f.write(item.get_content())
                return img_path
    print(f"[DEBUG] Không tìm thấy ảnh cho src: {src}. Danh sách item: {[item.get_name() for item in book.get_items()]}")
    return None

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
                        pdf.image(img_path, w=pdf.w * 0.6)  # scale ảnh vừa phải
                        pdf.ln(2)
                    except Exception as e:
                        print(f"Không thể chèn ảnh: {img_path} - {e}")

def epub_to_pdf(epub_path, pdf_path):
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

def main():
    if len(sys.argv) != 3:
        print("Cách dùng: python epub_to_pdf.py <đường_dẫn_epub> <đường_dẫn_pdf>")
        sys.exit(1)
    epub_path = sys.argv[1]
    pdf_path = sys.argv[2]
    if not os.path.exists(epub_path):
        print(f"Không tìm thấy file: {epub_path}")
        sys.exit(1)
    epub_to_pdf(epub_path, pdf_path)

if __name__ == "__main__":
    main()
