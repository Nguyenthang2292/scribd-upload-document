import sys
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from io import BytesIO


def pdf_page_to_image(page):
    """
    Convert a PDF page to an image using pdf2image.
    """
    from pdf2image import convert_from_bytes
    pdf_bytes = BytesIO()
    writer = PdfWriter()
    writer.add_page(page)
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)
    images = convert_from_bytes(pdf_bytes.read())
    return images[0]


def merge_4_pages_landscape(input_pdf_path, output_pdf_path):
    """
    Merge every 4 PDF pages into one landscape page (2x2 grid).
    """
    reader = PdfReader(input_pdf_path)
    num_pages = len(reader.pages)
    orig_page = reader.pages[0]
    orig_width = float(orig_page.mediabox.width)
    orig_height = float(orig_page.mediabox.height)
    new_width = orig_width * 2
    new_height = orig_height * 2

    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(new_width, new_height))

    i = 0
    while i < num_pages:
        # Top-left (1)
        if i < num_pages:
            page1 = reader.pages[i]
            img1 = pdf_page_to_image(page1)
            c.drawInlineImage(img1, 0, orig_height, width=orig_width, height=orig_height)
        # Top-right (2)
        if i + 1 < num_pages:
            page2 = reader.pages[i + 1]
            img2 = pdf_page_to_image(page2)
            c.drawInlineImage(img2, orig_width, orig_height, width=orig_width, height=orig_height)
        # Bottom-left (3)
        if i + 2 < num_pages:
            page3 = reader.pages[i + 2]
            img3 = pdf_page_to_image(page3)
            c.drawInlineImage(img3, 0, 0, width=orig_width, height=orig_height)
        # Bottom-right (4)
        if i + 3 < num_pages:
            page4 = reader.pages[i + 3]
            img4 = pdf_page_to_image(page4)
            c.drawInlineImage(img4, orig_width, 0, width=orig_width, height=orig_height)
        c.showPage()
        i += 4
    c.save()
    packet.seek(0)

    with open(output_pdf_path, 'wb') as f_out:
        f_out.write(packet.read())


def main():
    if len(sys.argv) != 3:
        print("Usage: python merge_4_pages_landscape.py input.pdf output.pdf")
        sys.exit(1)
    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    merge_4_pages_landscape(input_pdf, output_pdf)
    print(f"Đã ghép xong: {output_pdf}")


if __name__ == "__main__":
    main()
