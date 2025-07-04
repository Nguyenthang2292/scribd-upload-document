"""
PDF Duplicate Finder Component

This module provides functionality to find duplicate PDF files based on content,
file size, or hash comparison.
"""

import os
import hashlib
from typing import List, Dict, Optional
from pathlib import Path
from collections import defaultdict

try:
    from PyPDF4 import PdfFileReader
except ImportError:
    from PyPDF2 import PdfFileReader


class PDFDuplicateFinder:
    """PDF Duplicate Finder for identifying duplicate files."""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
        self.chunk_size = 8192  # 8KB chunks for reading files
    
    def find_duplicates_by_size(
        self,
        directory: str,
        recursive: bool = True
    ) -> Dict[int, List[str]]:
        """Find PDF files with the same file size.
        
        Args:
            directory: Directory to search
            recursive: Whether to search recursively
            
        Returns:
            Dictionary mapping file size to list of file paths
        """
        size_groups = defaultdict(list)
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            size_groups[file_size].append(file_path)
                        except (OSError, IOError):
                            continue
        else:
            try:
                for file in os.listdir(directory):
                    if file.lower().endswith('.pdf'):
                        file_path = os.path.join(directory, file)
                        if os.path.isfile(file_path):
                            try:
                                file_size = os.path.getsize(file_path)
                                size_groups[file_size].append(file_path)
                            except (OSError, IOError):
                                continue
            except (OSError, IOError):
                pass
        
        # Return only groups with more than one file
        return {size: files for size, files in size_groups.items() if len(files) > 1}
    
    def calculate_file_hash(self, file_path: str) -> Optional[str]:
        """Calculate MD5 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash string or None if error
        """
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(self.chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (OSError, IOError) as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return None
    
    def find_duplicates_by_hash(
        self,
        directory: str,
        recursive: bool = True
    ) -> Dict[str, List[str]]:
        """Find PDF files with the same content hash.
        
        Args:
            directory: Directory to search
            recursive: Whether to search recursively
            
        Returns:
            Dictionary mapping hash to list of file paths
        """
        # First find files with same size
        size_groups = self.find_duplicates_by_size(directory, recursive)
        
        hash_groups = defaultdict(list)
        
        for size, files in size_groups.items():
            for file_path in files:
                file_hash = self.calculate_file_hash(file_path)
                if file_hash:
                    hash_groups[file_hash].append(file_path)
        
        # Return only groups with more than one file
        return {hash_val: files for hash_val, files in hash_groups.items() if len(files) > 1}
    
    def calculate_pdf_content_hash(self, file_path: str) -> Optional[str]:
        """Calculate hash based on PDF content (excluding metadata).
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Content hash string or None if error
        """
        try:
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PdfFileReader(pdf_file, strict=False)
                
                # Create content hash from page count and first few pages
                content_data = []
                content_data.append(str(pdf_reader.getNumPages()))
                
                # Add first page content if available
                if pdf_reader.getNumPages() > 0:
                    try:
                        first_page = pdf_reader.getPage(0)
                        if hasattr(first_page, 'getContents'):
                            contents = first_page.getContents()
                            if contents:
                                content_data.append(str(contents.getData()[:1000]))  # First 1000 chars
                    except:
                        pass
                
                content_string = "".join(content_data)
                return hashlib.md5(content_string.encode()).hexdigest()
                
        except Exception as e:
            print(f"Error calculating content hash for {file_path}: {e}")
            return None
    
    def find_duplicates_by_content(
        self,
        directory: str,
        recursive: bool = True
    ) -> Dict[str, List[str]]:
        """Find PDF files with similar content.
        
        Args:
            directory: Directory to search
            recursive: Whether to search recursively
            
        Returns:
            Dictionary mapping content hash to list of file paths
        """
        content_groups = defaultdict(list)
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        file_path = os.path.join(root, file)
                        content_hash = self.calculate_pdf_content_hash(file_path)
                        if content_hash:
                            content_groups[content_hash].append(file_path)
        else:
            try:
                for file in os.listdir(directory):
                    if file.lower().endswith('.pdf'):
                        file_path = os.path.join(directory, file)
                        if os.path.isfile(file_path):
                            content_hash = self.calculate_pdf_content_hash(file_path)
                            if content_hash:
                                content_groups[content_hash].append(file_path)
            except (OSError, IOError):
                pass
        
        # Return only groups with more than one file
        return {hash_val: files for hash_val, files in content_groups.items() if len(files) > 1}
    
    def find_all_duplicates(
        self,
        directory: str,
        recursive: bool = True,
        method: str = "hash"
    ) -> Dict[str, List[str]]:
        """Find all duplicates using specified method.
        
        Args:
            directory: Directory to search
            recursive: Whether to search recursively
            method: Method to use ("size", "hash", "content")
            
        Returns:
            Dictionary mapping identifier to list of file paths
        """
        if method == "size":
            size_duplicates = self.find_duplicates_by_size(directory, recursive)
            # Convert int keys to strings for consistency
            return {str(size): files for size, files in size_duplicates.items()}
        elif method == "hash":
            return self.find_duplicates_by_hash(directory, recursive)
        elif method == "content":
            return self.find_duplicates_by_content(directory, recursive)
        else:
            raise ValueError("Method must be 'size', 'hash', or 'content'")
    
    def get_file_info(self, file_path: str) -> Dict[str, object]:
        """Get detailed information about a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing file information
        """
        try:
            info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': os.path.getsize(file_path),
                'modified': os.path.getmtime(file_path),
                'hash': self.calculate_file_hash(file_path)
            }
            
            # Try to get PDF-specific info
            try:
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PdfFileReader(pdf_file, strict=False)
                    info['num_pages'] = pdf_reader.getNumPages()
                    info['is_encrypted'] = pdf_reader.isEncrypted
                    
                    # Try to get metadata
                    try:
                        doc_info = pdf_reader.getDocumentInfo()
                        if doc_info:
                            info['title'] = doc_info.title
                            info['author'] = doc_info.author
                    except:
                        pass
            except:
                info['num_pages'] = 0
                info['is_encrypted'] = False
            
            return info
            
        except Exception as e:
            return {
                'path': file_path,
                'error': str(e)
            }
    
    def generate_duplicate_report(
        self,
        directory: str,
        recursive: bool = True,
        method: str = "hash"
    ) -> Dict[str, object]:
        """Generate a comprehensive duplicate report.
        
        Args:
            directory: Directory to search
            recursive: Whether to search recursively
            method: Method to use for duplicate detection
            
        Returns:
            Dictionary containing duplicate report
        """
        duplicates = self.find_all_duplicates(directory, recursive, method)
        
        report = {
            'directory': directory,
            'method': method,
            'total_duplicate_groups': len(duplicates),
            'total_duplicate_files': sum(len(files) for files in duplicates.values()),
            'duplicate_groups': {},
            'summary': {}
        }
        
        total_size_saved = 0
        
        for identifier, files in duplicates.items():
            group_info = {
                'files': files,
                'count': len(files),
                'file_infos': [self.get_file_info(f) for f in files],
                'size_saved': 0
            }
            
            # Calculate potential space savings
            if files:
                file_size = os.path.getsize(files[0])
                group_info['size_saved'] = file_size * (len(files) - 1)
                total_size_saved += group_info['size_saved']
            
            report['duplicate_groups'][str(identifier)] = group_info
        
        report['summary'] = {
            'total_size_saved': total_size_saved,
            'size_saved_mb': total_size_saved / (1024 * 1024),
            'size_saved_gb': total_size_saved / (1024 * 1024 * 1024)
        }
        
        return report


def find_pdf_duplicates(
    directory: str,
    recursive: bool = True,
    method: str = "hash"
) -> Dict[str, List[str]]:
    """Convenience function to find PDF duplicates.
    
    Args:
        directory: Directory to search
        recursive: Whether to search recursively
        method: Method to use ("size", "hash", "content")
        
    Returns:
        Dictionary mapping identifier to list of file paths
    """
    finder = PDFDuplicateFinder()
    return finder.find_all_duplicates(directory, recursive, method)


def generate_duplicate_report(
    directory: str,
    recursive: bool = True,
    method: str = "hash"
) -> Dict[str, object]:
    """Convenience function to generate duplicate report.
    
    Args:
        directory: Directory to search
        recursive: Whether to search recursively
        method: Method to use for duplicate detection
        
    Returns:
        Dictionary containing duplicate report
    """
    finder = PDFDuplicateFinder()
    return finder.generate_duplicate_report(directory, recursive, method) 