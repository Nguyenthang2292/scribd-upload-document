import sys
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from io import BytesIO
import math


def get_page_size(page):
    """Lấy kích thước trang PDF"""
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    return width, height


def calculate_optimal_layout(page1, page2, preserve_aspect_ratio=True):
    """Tính toán layout tối ưu cho việc ghép 2 trang"""
    w1, h1 = get_page_size(page1)
    w2, h2 = get_page_size(page2)
    
    if preserve_aspect_ratio:
        # Tính tỷ lệ khung hình của từng trang
        ratio1 = w1 / h1
        ratio2 = w2 / h2
        
        # Kích thước trang mới (ngang) - sử dụng chiều cao lớn nhất
        max_height = max(h1, h2)
        new_height = max_height
        
        # Tính chiều rộng mới dựa trên tỷ lệ
        # Mỗi nửa trang sẽ có chiều rộng tối đa bằng chiều cao
        half_width = max_height
        new_width = half_width * 2
        
        # Tính toán tỷ lệ scale để vừa với nửa trang
        scale1 = min(half_width / w1, new_height / h1)
        scale2 = min(half_width / w2, new_height / h2)
        
        # Đảm bảo tỷ lệ scale không quá nhỏ (tối thiểu 0.7)
        scale1 = max(scale1, 0.7)
        scale2 = max(scale2, 0.7)
        
        # Đảm bảo tỷ lệ scale không quá lớn (tối đa 1.0)
        scale1 = min(scale1, 1.0)
        scale2 = min(scale2, 1.0)
        
    else:
        # Không giữ tỷ lệ - sử dụng kích thước cố định
        new_width = max(w1, w2) * 2
        new_height = max(h1, h2)
        scale1 = 1.0
        scale2 = 1.0
    
    return {
        'new_width': new_width,
        'new_height': new_height,
        'scale1': scale1,
        'scale2': scale2,
        'w1': w1, 'h1': h1,
        'w2': w2, 'h2': h2,
        'half_width': new_width / 2
    }


def merge_pdf_vertical_to_horizontal(input_pdf_path, output_pdf_path, preserve_aspect_ratio=True, add_margin=True, dpi=200):
    """
    Merge every two vertical PDF pages into one horizontal page.
    
    Args:
        input_pdf_path: Đường dẫn file PDF đầu vào
        output_pdf_path: Đường dẫn file PDF đầu ra
        preserve_aspect_ratio: Có giữ nguyên tỷ lệ khung hình không
        add_margin: Có thêm margin giữa 2 trang không
        dpi: Độ phân giải cho việc chuyển đổi PDF sang hình ảnh
    """
    reader = PdfReader(input_pdf_path)
    num_pages = len(reader.pages)
    
    if num_pages == 0:
        raise ValueError("File PDF không có trang nào")
    
    writer = PdfWriter()
    
    i = 0
    while i < num_pages:
        page1 = reader.pages[i]
        
        if i + 1 < num_pages:
            page2 = reader.pages[i + 1]
            # Ghép 2 trang
            merged_page = merge_two_pages(page1, page2, preserve_aspect_ratio, add_margin, dpi)
        else:
            # Trang cuối cùng, chỉ có 1 trang
            merged_page = merge_single_page(page1, preserve_aspect_ratio, dpi)
        
        writer.add_page(merged_page)
        i += 2
    
    # Lưu file
    with open(output_pdf_path, 'wb') as output_file:
        writer.write(output_file)


def merge_two_pages(page1, page2, preserve_aspect_ratio=True, add_margin=True, dpi=200):
    """Ghép 2 trang PDF thành 1 trang ngang"""
    layout = calculate_optimal_layout(page1, page2, preserve_aspect_ratio)
    
    # Tạo trang mới
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(layout['new_width'], layout['new_height']))
    
    # Tính toán vị trí và kích thước
    margin = 30 if add_margin else 0
    half_width = layout['half_width']
    
    # Vẽ trang 1 (bên trái)
    x1 = margin
    y1 = (layout['new_height'] - layout['h1'] * layout['scale1']) / 2
    width1 = layout['w1'] * layout['scale1']
    height1 = layout['h1'] * layout['scale1']
    
    # Vẽ trang 2 (bên phải)
    x2 = half_width + margin
    y2 = (layout['new_height'] - layout['h2'] * layout['scale2']) / 2
    width2 = layout['w2'] * layout['scale2']
    height2 = layout['h2'] * layout['scale2']
    
    # Vẽ trang 1
    draw_page_on_canvas(c, page1, x1, y1, width1, height1, dpi)
    
    # Vẽ trang 2
    draw_page_on_canvas(c, page2, x2, y2, width2, height2, dpi)
    
    c.showPage()
    c.save()
    
    packet.seek(0)
    return PdfReader(packet).pages[0]


def merge_single_page(page1, preserve_aspect_ratio=True, dpi=200):
    """Xử lý trang cuối cùng khi số trang lẻ"""
    w1, h1 = get_page_size(page1)
    
    if preserve_aspect_ratio:
        # Tạo trang mới với kích thước phù hợp
        new_width = h1 * 2  # Chiều rộng gấp đôi chiều cao
        new_height = h1
    else:
        # Sử dụng kích thước cố định
        new_width = w1 * 2
        new_height = h1
    
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(new_width, new_height))
    
    # Căn giữa trang
    x = (new_width - w1) / 2
    y = 0
    
    draw_page_on_canvas(c, page1, x, y, w1, h1, dpi)
    
    c.showPage()
    c.save()
    
    packet.seek(0)
    return PdfReader(packet).pages[0]


def draw_page_on_canvas(canvas_obj, page, x, y, width, height, dpi=200):
    """Vẽ trang PDF lên canvas với chất lượng cao"""
    try:
        from pdf2image import convert_from_bytes
        pdf_bytes = BytesIO()
        temp_writer = PdfWriter()
        temp_writer.add_page(page)
        temp_writer.write(pdf_bytes)
        pdf_bytes.seek(0)
        
        # Chuyển đổi với DPI cao để đảm bảo chất lượng
        images = convert_from_bytes(pdf_bytes.read(), dpi=dpi)
        img = images[0]
        
        # Vẽ hình ảnh lên canvas
        canvas_obj.drawInlineImage(img, x, y, width=width, height=height)
        
    except ImportError:
        # Fallback nếu không có pdf2image
        canvas_obj.saveState()
        canvas_obj.translate(x, y)
        canvas_obj.rect(0, 0, width, height)
        canvas_obj.setFont("Helvetica", 12)
        canvas_obj.drawString(10, height - 20, "Trang PDF")
        canvas_obj.restoreState()
    except Exception as e:
        # Fallback khác nếu có lỗi
        canvas_obj.saveState()
        canvas_obj.translate(x, y)
        canvas_obj.rect(0, 0, width, height)
        canvas_obj.setFont("Helvetica", 10)
        canvas_obj.drawString(10, height - 20, f"Lỗi: {str(e)[:20]}")
        canvas_obj.restoreState()


def main():
    if len(sys.argv) != 3:
        print("Usage: python merge_pdf.py input.pdf output.pdf")
        sys.exit(1)
    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    merge_pdf_vertical_to_horizontal(input_pdf, output_pdf)
    print(f"Đã ghép xong: {output_pdf}")


if __name__ == "__main__":
    main()
