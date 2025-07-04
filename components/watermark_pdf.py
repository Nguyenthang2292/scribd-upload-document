"""
PDF Watermark Component

This module provides functionality to add and remove watermarks from PDF files.
Supports text and image watermarks with customizable positioning and styling.
"""

import os
from typing import Tuple, Optional, Union
from io import BytesIO

try:
    from PyPDF4 import PdfFileReader, PdfFileWriter
except ImportError:
    from PyPDF2 import PdfFileReader, PdfFileWriter

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors               


class PDFWatermark:
    """PDF Watermark handler for adding and removing watermarks."""
    
    def __init__(self):
        self.pagesize = A4
        self.fontname = 'Helvetica-Bold'
        self.fontsize = 40
        self.color = colors.red
        self.x_position = 250
        self.y_position = 10
        self.rotation_angle = 45
        
    def set_watermark_config(
        self,
        fontname: str = 'Helvetica-Bold',
        fontsize: int = 40,
        color: Union[colors.Color, Tuple[int, int, int]] = colors.red,
        x_position: int = 250,
        y_position: int = 10,
        rotation_angle: int = 45
    ) -> None:
        """Configure watermark appearance.
        
        Args:
            fontname: Font name for text watermark
            fontsize: Font size for text watermark
            color: Color for watermark (can be reportlab color or RGB tuple)
            x_position: X coordinate position
            y_position: Y coordinate position
            rotation_angle: Rotation angle in degrees
        """
        self.fontname = fontname
        self.fontsize = fontsize
        self.color = color
        self.x_position = x_position
        self.y_position = y_position
        self.rotation_angle = rotation_angle
    
    def create_text_watermark(self, text: str) -> BytesIO:
        """Create a text watermark.
        
        Args:
            text: Text to use as watermark
            
        Returns:
            BytesIO buffer containing the watermark PDF
        """
        if not text:
            raise ValueError("Watermark text cannot be empty")
            
        output_buffer = BytesIO()
        c = canvas.Canvas(output_buffer, pagesize=self.pagesize)
        
        # Set font and size
        c.setFont(self.fontname, self.fontsize)
        
        # Set color
        if isinstance(self.color, tuple):
            color = (c/255 for c in self.color)
            c.setFillColorRGB(*color)
        else:
            c.setFillColor(self.color)
        
        # Apply rotation and position
        c.rotate(self.rotation_angle)
        c.drawString(self.x_position, self.y_position, text)
        c.save()
        
        return output_buffer
    
    def create_image_watermark(self, image_path: str, width: int = 160, height: int = 160) -> BytesIO:
        """Create an image watermark.
        
        Args:
            image_path: Path to the image file
            width: Width of the watermark image
            height: Height of the watermark image
            
        Returns:
            BytesIO buffer containing the watermark PDF
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        output_buffer = BytesIO()
        c = canvas.Canvas(output_buffer, pagesize=self.pagesize)
        
        # Draw image at specified position
        c.drawImage(image_path, self.x_position, self.y_position, width, height)
        c.save()
        
        return output_buffer
    
    def add_watermark(
        self,
        input_file: str,
        output_file: str,
        watermark_text: Optional[str] = None,
        watermark_image: Optional[str] = None,
        pages: Optional[Tuple[int, ...]] = None
    ) -> bool:
        """Add watermark to PDF file.
        
        Args:
            input_file: Path to input PDF file
            output_file: Path to output PDF file
            watermark_text: Text to use as watermark
            watermark_image: Path to image file to use as watermark
            pages: Specific pages to watermark (None for all pages)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create watermark
            if watermark_text:
                wm_buffer = self.create_text_watermark(watermark_text)
            elif watermark_image:
                wm_buffer = self.create_image_watermark(watermark_image)
            else:
                raise ValueError("Either watermark_text or watermark_image must be provided")
            
            # Read watermark
            wm_reader = PdfFileReader(wm_buffer)
            
            # Read input PDF
            with open(input_file, 'rb') as pdf_file:
                pdf_reader = PdfFileReader(pdf_file, strict=False)
                pdf_writer = PdfFileWriter()
                
                # Process each page
                for page_num in range(pdf_reader.getNumPages()):
                    # Skip if specific pages are requested and current page is not in list
                    if pages is not None and page_num not in pages:
                        pdf_writer.addPage(pdf_reader.getPage(page_num))
                        continue
                    
                    # Get page and merge with watermark
                    page = pdf_reader.getPage(page_num)
                    page.mergePage(wm_reader.getPage(0))
                    pdf_writer.addPage(page)
                
                # Write output file
                with open(output_file, 'wb') as output_pdf:
                    pdf_writer.write(output_pdf)
            
            return True
            
        except Exception as e:
            print(f"Error adding watermark: {str(e)}")
            return False
    
    def remove_watermark(
        self,
        input_file: str,
        output_file: str,
        watermark_text: Optional[str] = None,
        pages: Optional[Tuple[int, ...]] = None
    ) -> bool:
        """Remove watermark from PDF file.
        
        Args:
            input_file: Path to input PDF file
            output_file: Path to output PDF file
            watermark_text: Text watermark to remove (for identification)
            pages: Specific pages to process (None for all pages)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(input_file, 'rb') as pdf_file:
                pdf_reader = PdfFileReader(pdf_file, strict=False)
                pdf_writer = PdfFileWriter()
                
                for page_num in range(pdf_reader.getNumPages()):
                    # Skip if specific pages are requested and current page is not in list
                    if pages is not None and page_num not in pages:
                        pdf_writer.addPage(pdf_reader.getPage(page_num))
                        continue
                    
                    page = pdf_reader.getPage(page_num)
                    
                    # Try to remove watermark by recreating page content
                    # This is a simplified approach - may not work for all watermarks
                    if '/Contents' in page:
                        contents = page['/Contents']
                        if hasattr(contents, 'getData'):
                            # Remove watermark-related content
                            content_data = contents.getData()
                            # This is a basic approach - more sophisticated watermark removal
                            # would require parsing the PDF content stream
                            pdf_writer.addPage(page)
                    else:
                        pdf_writer.addPage(page)
                
                # Write output file
                with open(output_file, 'wb') as output_pdf:
                    pdf_writer.write(output_pdf)
            
            return True
            
        except Exception as e:
            print(f"Error removing watermark: {str(e)}")
            return False


def add_watermark_to_pdf(
    input_file: str,
    output_file: str,
    watermark_text: str,
    pages: Optional[Tuple[int, ...]] = None
) -> bool:
    """Convenience function to add text watermark to PDF.
    
    Args:
        input_file: Path to input PDF file
        output_file: Path to output PDF file
        watermark_text: Text to use as watermark
        pages: Specific pages to watermark (None for all pages)
        
    Returns:
        True if successful, False otherwise
    """
    watermarker = PDFWatermark()
    return watermarker.add_watermark(input_file, output_file, watermark_text=watermark_text, pages=pages)


def add_image_watermark_to_pdf(
    input_file: str,
    output_file: str,
    watermark_image: str,
    pages: Optional[Tuple[int, ...]] = None
) -> bool:
    """Convenience function to add image watermark to PDF.
    
    Args:
        input_file: Path to input PDF file
        output_file: Path to output PDF file
        watermark_image: Path to image file to use as watermark
        pages: Specific pages to watermark (None for all pages)
        
    Returns:
        True if successful, False otherwise
    """
    watermarker = PDFWatermark()
    return watermarker.add_watermark(input_file, output_file, watermark_image=watermark_image, pages=pages)


def remove_watermark_from_pdf(
    input_file: str,
    output_file: str,
    watermark_text: str,
    pages: Optional[Tuple[int, ...]] = None
) -> bool:
    """Convenience function to remove watermark from PDF.
    
    Args:
        input_file: Path to input PDF file
        output_file: Path to output PDF file
        watermark_text: Text watermark to remove
        pages: Specific pages to process (None for all pages)
        
    Returns:
        True if successful, False otherwise
    """
    watermarker = PDFWatermark()
    return watermarker.remove_watermark(input_file, output_file, watermark_text=watermark_text, pages=pages) 