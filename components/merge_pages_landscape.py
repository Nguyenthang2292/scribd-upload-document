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


def merge_pdf_vertical_to_horizontal(input_pdf_path, output_pdf_path):
    """
    Merge every two vertical PDF pages into one horizontal page.
    """
    reader = PdfReader(input_pdf_path)
    num_pages = len(reader.pages)
    orig_page = reader.pages[0]
    orig_width = float(orig_page.mediabox.width)
    orig_height = float(orig_page.mediabox.height)
    new_width = orig_height * 2
    new_height = orig_width

    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(orig_width * 2, orig_height))

    i = 0
    while i < num_pages:
        page1 = reader.pages[i]
        img1 = pdf_page_to_image(page1)
        c.drawInlineImage(img1, 0, 0, width=orig_width, height=orig_height)
        if i + 1 < num_pages:
            page2 = reader.pages[i + 1]
            img2 = pdf_page_to_image(page2)
            c.drawInlineImage(img2, orig_width, 0, width=orig_width, height=orig_height)
        c.showPage()
        i += 2
    c.save()
    packet.seek(0)

    with open(output_pdf_path, 'wb') as f_out:
        f_out.write(packet.read())


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
