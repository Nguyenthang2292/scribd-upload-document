#!/usr/bin/env python3
"""
PDF Hash Changer - Utility to modify PDF metadata and generate new files
Refactored version with improved error handling and modularity
"""

import os
import sys
import random
import string
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
from pypdf import PdfReader, PdfWriter
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFHashChanger:
    """Class to handle PDF hash changing operations"""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize PDFHashChanger
        
        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_random_filename(self, prefix: str = "", suffix: str = ".pdf") -> str:
        """
        Generate a random filename
        
        Args:
            prefix: Optional prefix for filename
            suffix: File extension (default: .pdf)
            
        Returns:
            Random filename string
        """
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{prefix}{random_part}{suffix}"
    
    def read_pdf(self, input_path: str) -> Optional[PdfReader]:
        """
        Read PDF file with error handling
        
        Args:
            input_path: Path to input PDF file
            
        Returns:
            PdfReader object or None if error
        """
        try:
            if not os.path.exists(input_path):
                logger.error(f"File not found: {input_path}")
                return None
                
            reader = PdfReader(input_path)
            logger.info(f"Successfully read PDF: {input_path} ({len(reader.pages)} pages)")
            return reader
            
        except Exception as e:
            logger.error(f"Error reading PDF {input_path}: {str(e)}")
            return None
    
    def create_modified_pdf(self, reader: PdfReader, metadata: Optional[Dict[str, Any]] = None) -> Optional[PdfWriter]:
        """
        Create modified PDF with new metadata
        
        Args:
            reader: PdfReader object
            metadata: Optional metadata to add
            
        Returns:
            PdfWriter object or None if error
        """
        try:
            writer = PdfWriter()
            
            # Copy all pages
            for page in reader.pages:
                writer.add_page(page)
            
            # Add custom metadata
            if metadata:
                writer.add_metadata(metadata)
            else:
                # Default metadata
                writer.add_metadata({"/CustomHashBypass": "1"})
            
            logger.info("Successfully created modified PDF")
            return writer
            
        except Exception as e:
            logger.error(f"Error creating modified PDF: {str(e)}")
            return None
    
    def save_pdf(self, writer: PdfWriter, filename: str) -> bool:
        """
        Save PDF to file
        
        Args:
            writer: PdfWriter object
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = self.output_dir / filename
            with open(output_path, "wb") as f:
                writer.write(f)
            
            logger.info(f"PDF saved successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving PDF: {str(e)}")
            return False
    
    def process_pdf(self, input_path: str, custom_metadata: Optional[Dict[str, Any]] = None,
                   output_filename: Optional[str] = None) -> Optional[str]:
        """
        Complete PDF processing pipeline

        Args:
            input_path: Path to input PDF file
            custom_metadata: Optional custom metadata
            output_filename: Optional custom output filename

        Returns:
            Path to output file if successful, None otherwise
        """
        # Read PDF
        reader = self.read_pdf(input_path)
        if not reader:
            return None

        # Create modified PDF
        writer = self.create_modified_pdf(reader, custom_metadata)
        if not writer:
            return None

        # Generate output filename
        if not output_filename:
            output_filename = self.generate_random_filename()

        # Save PDF
        if self.save_pdf(writer, output_filename):
            return str(self.output_dir / output_filename)

        return None


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description="PDF Hash Changer - Modify PDF metadata and generate new files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python change_hash_pdf.py input.pdf
  python change_hash_pdf.py input.pdf --output-dir custom_output
  python change_hash_pdf.py input.pdf --metadata '{"CustomKey": "CustomValue"}'
        """
    )

    parser.add_argument("input_file", help="Input PDF file path")
    parser.add_argument("--output-dir", "-o", default="output",
                       help="Output directory (default: output)")
    parser.add_argument("--metadata", "-m", type=str,
                       help="Custom metadata as JSON string")
    parser.add_argument("--output-filename", "-f",
                       help="Custom output filename")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Parse metadata if provided
    custom_metadata = None
    if args.metadata:
        try:
            import json
            custom_metadata = json.loads(args.metadata)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON metadata: {e}")
            sys.exit(1)

    # Process PDF
    changer = PDFHashChanger(args.output_dir)
    result = changer.process_pdf(
        args.input_file,
        custom_metadata,
        args.output_filename
    )

    if result:
        print(f"✅ Success! Output file: {result}")
        sys.exit(0)
    else:
        print("❌ Failed to process PDF")
        sys.exit(1)


if __name__ == "__main__":
    # For backward compatibility, also support simple usage
    if len(sys.argv) == 1:
        # Original simple usage
        input_file = "nhasachmienphi-phong-thuy-thuc-dung.pdf"
        if os.path.exists(input_file):
            changer = PDFHashChanger()
            result = changer.process_pdf(input_file)
            if result:
                print(f"✅ Success! Output file: {result}")
            else:
                print("❌ Failed to process PDF")
        else:
            print(f"❌ File not found: {input_file}")
            print("Usage: python change_hash_pdf.py <input_file> [options]")
    else:
        main()
