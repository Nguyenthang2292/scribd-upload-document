"""
PDF Splitter Component

This module provides functionality to split PDF files into multiple smaller files
based on page ranges, number of pages per file, or specific page numbers.
"""

import os
from typing import List, Tuple, Optional
from pathlib import Path

try:
    from PyPDF4 import PdfFileReader, PdfFileWriter
except ImportError:
    from PyPDF2 import PdfFileReader, PdfFileWriter


class PDFSplitter:
    """PDF Splitter for dividing PDF files into smaller parts."""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def split_by_page_ranges(
        self,
        input_file: str,
        output_dir: str,
        page_ranges: List[Tuple[int, int]],
        output_names: Optional[List[str]] = None
    ) -> List[str]:
        """Split PDF by specific page ranges.
        
        Args:
            input_file: Path to input PDF file
            output_dir: Directory to save split files
            page_ranges: List of (start_page, end_page) tuples (0-based)
            output_names: Optional list of output file names
            
        Returns:
            List of created output file paths
        """
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Read input PDF
            with open(input_file, 'rb') as pdf_file:
                pdf_reader = PdfFileReader(pdf_file, strict=False)
                total_pages = pdf_reader.getNumPages()
                
                output_files = []
                
                for i, (start_page, end_page) in enumerate(page_ranges):
                    # Validate page range
                    if start_page < 0 or end_page >= total_pages or start_page > end_page:
                        print(f"Invalid page range: {start_page}-{end_page}")
                        continue
                    
                    # Create output filename
                    if output_names and i < len(output_names):
                        output_name = output_names[i]
                    else:
                        base_name = Path(input_file).stem
                        output_name = f"{base_name}_pages_{start_page+1}-{end_page+1}.pdf"
                    
                    output_path = os.path.join(output_dir, output_name)
                    
                    # Create PDF writer for this range
                    pdf_writer = PdfFileWriter()
                    
                    # Add pages in range
                    for page_num in range(start_page, end_page + 1):
                        page = pdf_reader.getPage(page_num)
                        pdf_writer.addPage(page)
                    
                    # Write output file
                    with open(output_path, 'wb') as output_pdf:
                        pdf_writer.write(output_pdf)
                    
                    output_files.append(output_path)
                    print(f"Created: {output_path} (pages {start_page+1}-{end_page+1})")
                
                return output_files
                
        except Exception as e:
            print(f"Error splitting PDF by page ranges: {str(e)}")
            return []
    
    def split_by_pages_per_file(
        self,
        input_file: str,
        output_dir: str,
        pages_per_file: int,
        output_prefix: str = ""
    ) -> List[str]:
        """Split PDF into files with specified number of pages each.
        
        Args:
            input_file: Path to input PDF file
            output_dir: Directory to save split files
            pages_per_file: Number of pages per output file
            output_prefix: Prefix for output file names
            
        Returns:
            List of created output file paths
        """
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Read input PDF
            with open(input_file, 'rb') as pdf_file:
                pdf_reader = PdfFileReader(pdf_file, strict=False)
                total_pages = pdf_reader.getNumPages()
                
                output_files = []
                base_name = Path(input_file).stem
                
                # Calculate number of output files
                num_files = (total_pages + pages_per_file - 1) // pages_per_file
                
                for file_num in range(num_files):
                    start_page = file_num * pages_per_file
                    end_page = min(start_page + pages_per_file - 1, total_pages - 1)
                    
                    # Create output filename
                    if output_prefix:
                        output_name = f"{output_prefix}_part_{file_num + 1:03d}.pdf"
                    else:
                        output_name = f"{base_name}_part_{file_num + 1:03d}.pdf"
                    
                    output_path = os.path.join(output_dir, output_name)
                    
                    # Create PDF writer for this part
                    pdf_writer = PdfFileWriter()
                    
                    # Add pages for this part
                    for page_num in range(start_page, end_page + 1):
                        page = pdf_reader.getPage(page_num)
                        pdf_writer.addPage(page)
                    
                    # Write output file
                    with open(output_path, 'wb') as output_pdf:
                        pdf_writer.write(output_pdf)
                    
                    output_files.append(output_path)
                    print(f"Created: {output_path} (pages {start_page+1}-{end_page+1})")
                
                return output_files
                
        except Exception as e:
            print(f"Error splitting PDF by pages per file: {str(e)}")
            return []
    
    def extract_single_page(
        self,
        input_file: str,
        output_file: str,
        page_number: int
    ) -> bool:
        """Extract a single page from PDF.
        
        Args:
            input_file: Path to input PDF file
            output_file: Path to output PDF file
            page_number: Page number to extract (0-based)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read input PDF
            with open(input_file, 'rb') as pdf_file:
                pdf_reader = PdfFileReader(pdf_file, strict=False)
                total_pages = pdf_reader.getNumPages()
                
                # Validate page number
                if page_number < 0 or page_number >= total_pages:
                    print(f"Invalid page number: {page_number}")
                    return False
                
                # Create PDF writer
                pdf_writer = PdfFileWriter()
                
                # Add the specified page
                page = pdf_reader.getPage(page_number)
                pdf_writer.addPage(page)
                
                # Write output file
                with open(output_file, 'wb') as output_pdf:
                    pdf_writer.write(output_pdf)
                
                print(f"Extracted page {page_number + 1} to: {output_file}")
                return True
                
        except Exception as e:
            print(f"Error extracting page: {str(e)}")
            return False


def split_pdf_by_ranges(
    input_file: str,
    output_dir: str,
    page_ranges: List[Tuple[int, int]]
) -> List[str]:
    """Convenience function to split PDF by page ranges.
    
    Args:
        input_file: Path to input PDF file
        output_dir: Directory to save split files
        page_ranges: List of (start_page, end_page) tuples
        
    Returns:
        List of created output file paths
    """
    splitter = PDFSplitter()
    return splitter.split_by_page_ranges(input_file, output_dir, page_ranges)


def split_pdf_by_pages_per_file(
    input_file: str,
    output_dir: str,
    pages_per_file: int
) -> List[str]:
    """Convenience function to split PDF by pages per file.
    
    Args:
        input_file: Path to input PDF file
        output_dir: Directory to save split files
        pages_per_file: Number of pages per output file
        
    Returns:
        List of created output file paths
    """
    splitter = PDFSplitter()
    return splitter.split_by_pages_per_file(input_file, output_dir, pages_per_file)


def extract_pdf_page(
    input_file: str,
    output_file: str,
    page_number: int
) -> bool:
    """Convenience function to extract a single page from PDF.
    
    Args:
        input_file: Path to input PDF file
        output_file: Path to output PDF file
        page_number: Page number to extract (0-based)
        
    Returns:
        True if successful, False otherwise
    """
    splitter = PDFSplitter()
    return splitter.extract_single_page(input_file, output_file, page_number) 