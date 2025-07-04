"""
PDF Metadata Cleaner Component

This module provides functionality to clean metadata and hidden information from PDF files.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from PyPDF4 import PdfFileReader, PdfFileWriter
except ImportError:
    from PyPDF2 import PdfFileReader, PdfFileWriter


class PDFMetadataCleaner:
    """PDF Metadata Cleaner for removing hidden information."""
    
    def __init__(self):
        self.metadata_fields = [
            '/Title', '/Author', '/Subject', '/Creator', '/Producer',
            '/Keywords', '/CreationDate', '/ModDate', '/Trapped'
        ]
    
    def clean_metadata(
        self,
        input_file: str,
        output_file: str,
        remove_fields: Optional[List[str]] = None,
        replace_with: Optional[Dict[str, str]] = None
    ) -> bool:
        """Clean metadata from PDF file.
        
        Args:
            input_file: Path to input PDF file
            output_file: Path to output PDF file
            remove_fields: List of metadata fields to remove (None for all)
            replace_with: Dictionary of field:value to replace
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read input PDF
            with open(input_file, 'rb') as pdf_file:
                pdf_reader = PdfFileReader(pdf_file, strict=False)
                pdf_writer = PdfFileWriter()
                
                # Copy all pages
                for page_num in range(pdf_reader.getNumPages()):
                    page = pdf_reader.getPage(page_num)
                    pdf_writer.addPage(page)
                
                # Get document info
                doc_info = pdf_reader.getDocumentInfo()
                
                # Clean metadata
                if remove_fields is None:
                    remove_fields = self.metadata_fields
                
                # Remove specified fields
                for field in remove_fields:
                    if field in doc_info:
                        del doc_info[field]
                
                # Replace with new values
                if replace_with:
                    for field, value in replace_with.items():
                        doc_info[field] = value
                
                # Set cleaned metadata
                pdf_writer.addMetadata(doc_info)
                
                # Write output file
                with open(output_file, 'wb') as output_pdf:
                    pdf_writer.write(output_pdf)
                
                return True
                
        except Exception as e:
            print(f"Error cleaning metadata: {str(e)}")
            return False
    
    def get_metadata(self, pdf_file: str) -> Dict[str, Any]:
        """Get metadata from PDF file.
        
        Args:
            pdf_file: Path to PDF file
            
        Returns:
            Dictionary containing metadata
        """
        try:
            with open(pdf_file, 'rb') as file:
                pdf_reader = PdfFileReader(file, strict=False)
                doc_info = pdf_reader.getDocumentInfo()
                
                metadata = {
                    'file_path': pdf_file,
                    'num_pages': pdf_reader.getNumPages(),
                    'is_encrypted': pdf_reader.isEncrypted,
                    'file_size': os.path.getsize(pdf_file)
                }
                
                if doc_info:
                    for field in self.metadata_fields:
                        if hasattr(doc_info, field[1:].lower()):
                            value = getattr(doc_info, field[1:].lower())
                            if value:
                                metadata[field[1:].lower()] = value
                
                return metadata
                
        except Exception as e:
            return {
                'error': str(e),
                'file_path': pdf_file
            }
    
    def remove_all_metadata(
        self,
        input_file: str,
        output_file: str
    ) -> bool:
        """Remove all metadata from PDF file.
        
        Args:
            input_file: Path to input PDF file
            output_file: Path to output PDF file
            
        Returns:
            True if successful, False otherwise
        """
        return self.clean_metadata(input_file, output_file, remove_fields=self.metadata_fields)
    
    def anonymize_pdf(
        self,
        input_file: str,
        output_file: str,
        author: str = "Anonymous",
        creator: str = "PDF Utility Toolkit",
        producer: str = "PDF Utility Toolkit"
    ) -> bool:
        """Anonymize PDF by replacing identifying metadata.
        
        Args:
            input_file: Path to input PDF file
            output_file: Path to output PDF file
            author: Author name to set
            creator: Creator name to set
            producer: Producer name to set
            
        Returns:
            True if successful, False otherwise
        """
        replace_with = {
            '/Author': author,
            '/Creator': creator,
            '/Producer': producer,
            '/Title': '',
            '/Subject': '',
            '/Keywords': ''
        }
        
        return self.clean_metadata(input_file, output_file, replace_with=replace_with)
    
    def clean_creation_dates(
        self,
        input_file: str,
        output_file: str,
        new_date: Optional[str] = None
    ) -> bool:
        """Clean creation and modification dates.
        
        Args:
            input_file: Path to input PDF file
            output_file: Path to output PDF file
            new_date: New date to set (format: YYYYMMDDHHmmSSOHH'mm')
            
        Returns:
            True if successful, False otherwise
        """
        if new_date is None:
            new_date = datetime.now().strftime("%Y%m%d%H%M%S")
        
        replace_with = {
            '/CreationDate': new_date,
            '/ModDate': new_date
        }
        
        return self.clean_metadata(input_file, output_file, replace_with=replace_with)


def clean_pdf_metadata(
    input_file: str,
    output_file: str,
    remove_fields: Optional[List[str]] = None
) -> bool:
    """Convenience function to clean PDF metadata.
    
    Args:
        input_file: Path to input PDF file
        output_file: Path to output PDF file
        remove_fields: List of metadata fields to remove
        
    Returns:
        True if successful, False otherwise
    """
    cleaner = PDFMetadataCleaner()
    return cleaner.clean_metadata(input_file, output_file, remove_fields)


def remove_all_pdf_metadata(
    input_file: str,
    output_file: str
) -> bool:
    """Convenience function to remove all PDF metadata.
    
    Args:
        input_file: Path to input PDF file
        output_file: Path to output PDF file
        
    Returns:
        True if successful, False otherwise
    """
    cleaner = PDFMetadataCleaner()
    return cleaner.remove_all_metadata(input_file, output_file)


def anonymize_pdf_file(
    input_file: str,
    output_file: str
) -> bool:
    """Convenience function to anonymize PDF file.
    
    Args:
        input_file: Path to input PDF file
        output_file: Path to output PDF file
        
    Returns:
        True if successful, False otherwise
    """
    cleaner = PDFMetadataCleaner()
    return cleaner.anonymize_pdf(input_file, output_file)


def get_pdf_metadata(pdf_file: str) -> Dict[str, Any]:
    """Convenience function to get PDF metadata.
    
    Args:
        pdf_file: Path to PDF file
        
    Returns:
        Dictionary containing metadata
    """
    cleaner = PDFMetadataCleaner()
    return cleaner.get_metadata(pdf_file) 