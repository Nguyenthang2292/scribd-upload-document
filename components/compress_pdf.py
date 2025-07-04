import fitz  # PyMuPDF
import os


def compress_pdf(input_pdf, output_pdf, mode='medium'):
    """
    Compress a PDF file by reducing image quality.
    mode: 'low' (giữ chất lượng cao, nén ít), 'medium' (nén vừa), 'high' (nén mạnh, giảm chất lượng nhiều)
    """
    # Chọn mức nén ảnh
    if mode == 'low':
        img_quality = 90
        img_scale = 1.0
    elif mode == 'high':
        img_quality = 40
        img_scale = 0.5
    else:  # medium
        img_quality = 65
        img_scale = 0.7

    doc = fitz.open(input_pdf)
    for page in doc:
        img_list = page.get_images(full=True)
        for img_index, img in enumerate(img_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image['image']
            ext = base_image['ext']
            # Đọc ảnh, resize và nén lại
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(image_bytes))
            new_size = (int(image.width * img_scale), int(image.height * img_scale))
            # Sử dụng Resampling.BICUBIC nếu có, nếu không thì dùng 0 (NEAREST = 0)
            try:
                resample = Image.Resampling.BICUBIC
            except AttributeError:
                resample = 0
            image = image.resize(new_size, resample)
            img_buffer = io.BytesIO()
            if ext.lower() in ['jpg', 'jpeg']:
                image.save(img_buffer, format='JPEG', quality=img_quality)
            else:
                image.save(img_buffer, format='PNG', optimize=True)
            img_buffer.seek(0)
            # TODO: Thay thế ảnh trong PDF đúng cách với PyMuPDF nếu insert_image không khả dụng
            # try:
            #     page.insert_image(page.rect, stream=img_buffer.getvalue(), keep_proportion=True, overlay=True)
            # except AttributeError:
            #     pass  # Nếu không có insert_image, bỏ qua (hoặc cần giải pháp khác)
    doc.save(output_pdf, garbage=4, deflate=True)
    doc.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compress PDF file size with 3 modes: low, medium, high.")
    parser.add_argument('input_pdf', help='Input PDF file')
    parser.add_argument('output_pdf', help='Output compressed PDF file')
    parser.add_argument('--mode', choices=['low', 'medium', 'high'], default='medium', help='Compression mode')
    args = parser.parse_args()
    compress_pdf(args.input_pdf, args.output_pdf, args.mode)
    print(f"Compressed {args.input_pdf} -> {args.output_pdf} with mode: {args.mode}")
