"""
Enhanced Batch Processor Component

This module provides functionality for batch processing PDF files with progress tracking
and support for multiple operations.
"""

import os
import time
from typing import List, Dict, Any, Callable, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class ProgressTracker:
    """Progress tracker for batch operations."""
    
    def __init__(self, total_files: int):
        self.total_files = total_files
        self.processed_files = 0
        self.failed_files = 0
        self.current_file = ""
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def update_progress(self, file_path: str, success: bool = True):
        """Update progress for a processed file.
        
        Args:
            file_path: Path of the processed file
            success: Whether the operation was successful
        """
        with self.lock:
            self.processed_files += 1
            if not success:
                self.failed_files += 1
            self.current_file = os.path.basename(file_path)
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress information.
        
        Returns:
            Dictionary containing progress information
        """
        with self.lock:
            elapsed_time = time.time() - self.start_time
            progress_percent = (self.processed_files / self.total_files * 100) if self.total_files > 0 else 0
            
            # Estimate remaining time
            if self.processed_files > 0:
                avg_time_per_file = elapsed_time / self.processed_files
                remaining_files = self.total_files - self.processed_files
                estimated_remaining = avg_time_per_file * remaining_files
            else:
                estimated_remaining = 0
            
            return {
                'processed': self.processed_files,
                'total': self.total_files,
                'failed': self.failed_files,
                'success': self.processed_files - self.failed_files,
                'progress_percent': progress_percent,
                'current_file': self.current_file,
                'elapsed_time': elapsed_time,
                'estimated_remaining': estimated_remaining,
                'is_complete': self.processed_files >= self.total_files
            }


class BatchProcessor:
    """Enhanced batch processor for PDF operations."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.supported_operations = {
            'compress': self._compress_operation,
            'watermark': self._watermark_operation,
            'encrypt': self._encrypt_operation,
            'split': self._split_operation,
            'clean_metadata': self._clean_metadata_operation,
            'convert': self._convert_operation,
            'bypass_scribd': self._bypass_scribd_operation,  # Thêm dòng này
        }
    
    def process_directory(
        self,
        input_dir: str,
        output_dir: str,
        operation: str,
        operation_params: Dict[str, Any],
        file_pattern: str = "*.pdf",
        recursive: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Process all files in a directory with the specified operation.
        
        Args:
            input_dir: Input directory path
            output_dir: Output directory path
            operation: Operation to perform
            operation_params: Parameters for the operation
            file_pattern: File pattern to match
            recursive: Whether to search recursively
            progress_callback: Callback function for progress updates
            
        Returns:
            Dictionary containing processing results
        """
        # Find all matching files
        files = self._find_files(input_dir, file_pattern, recursive)
        
        if not files:
            return {
                'success': False,
                'error': 'No files found matching the pattern',
                'processed_files': 0,
                'failed_files': 0
            }
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize progress tracker
        progress_tracker = ProgressTracker(len(files))
        
        # Process files
        results = {
            'processed_files': [],
            'failed_files': [],
            'total_files': len(files),
            'success_count': 0,
            'failure_count': 0
        }
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(
                    self._process_single_file,
                    file_path,
                    output_dir,
                    operation,
                    operation_params
                ): file_path for file_path in files
            }
            
            # Process completed tasks
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result['success']:
                        results['processed_files'].append(result)
                        results['success_count'] += 1
                        progress_tracker.update_progress(file_path, True)
                    else:
                        results['failed_files'].append(result)
                        results['failure_count'] += 1
                        progress_tracker.update_progress(file_path, False)
                    
                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(progress_tracker.get_progress())
                        
                except Exception as e:
                    error_result = {
                        'file_path': file_path,
                        'success': False,
                        'error': str(e)
                    }
                    results['failed_files'].append(error_result)
                    results['failure_count'] += 1
                    progress_tracker.update_progress(file_path, False)
                    
                    if progress_callback:
                        progress_callback(progress_tracker.get_progress())
        
        results['success'] = results['failure_count'] == 0
        return results
    
    def _find_files(
        self,
        directory: str,
        pattern: str,
        recursive: bool
    ) -> List[str]:
        """Find files matching the pattern in the directory.
        
        Args:
            directory: Directory to search
            pattern: File pattern to match
            recursive: Whether to search recursively
            
        Returns:
            List of matching file paths
        """
        files = []
        
        if recursive:
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    if filename.lower().endswith('.pdf'):
                        files.append(os.path.join(root, filename))
        else:
            try:
                for filename in os.listdir(directory):
                    if filename.lower().endswith('.pdf'):
                        file_path = os.path.join(directory, filename)
                        if os.path.isfile(file_path):
                            files.append(file_path)
            except (OSError, IOError):
                pass
        
        return sorted(files)
    
    def _process_single_file(
        self,
        input_file: str,
        output_dir: str,
        operation: str,
        operation_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a single file with the specified operation.
        
        Args:
            input_file: Input file path
            output_dir: Output directory path
            operation: Operation to perform
            operation_params: Parameters for the operation
            
        Returns:
            Dictionary containing processing result
        """
        try:
            # Generate output file path
            base_name = Path(input_file).stem
            output_file = os.path.join(output_dir, f"{base_name}_processed.pdf")
            
            # Perform operation
            if operation in self.supported_operations:
                success = self.supported_operations[operation](
                    input_file, output_file, operation_params
                )
            else:
                return {
                    'file_path': input_file,
                    'success': False,
                    'error': f'Unsupported operation: {operation}'
                }
            
            if success:
                return {
                    'file_path': input_file,
                    'output_path': output_file,
                    'success': True
                }
            else:
                return {
                    'file_path': input_file,
                    'success': False,
                    'error': 'Operation failed'
                }
                
        except Exception as e:
            return {
                'file_path': input_file,
                'success': False,
                'error': str(e)
            }
    
    def _compress_operation(
        self,
        input_file: str,
        output_file: str,
        params: Dict[str, Any]
    ) -> bool:
        """Compress PDF operation."""
        try:
            from components.compress_pdf import compress_pdf
            mode = params.get('mode', 'medium')
            return compress_pdf(input_file, output_file, mode)
        except Exception as e:
            print(f"Compression error: {e}")
            return False
    
    def _watermark_operation(
        self,
        input_file: str,
        output_file: str,
        params: Dict[str, Any]
    ) -> bool:
        """Add watermark operation."""
        try:
            from components.watermark_pdf import add_watermark_to_pdf
            watermark_text = params.get('text', 'WATERMARK')
            pages = params.get('pages', None)
            return add_watermark_to_pdf(input_file, output_file, watermark_text, pages)
        except Exception as e:
            print(f"Watermark error: {e}")
            return False
    
    def _encrypt_operation(
        self,
        input_file: str,
        output_file: str,
        params: Dict[str, Any]
    ) -> bool:
        """Encrypt PDF operation."""
        try:
            from components.pdf_encryption import encrypt_pdf_file
            password = params.get('password', '')
            encryption_level = params.get('encryption_level', 'MEDIUM')
            return encrypt_pdf_file(input_file, output_file, password, encryption_level)
        except Exception as e:
            print(f"Encryption error: {e}")
            return False
    
    def _split_operation(
        self,
        input_file: str,
        output_file: str,
        params: Dict[str, Any]
    ) -> bool:
        """Split PDF operation."""
        try:
            from components.pdf_splitter import split_pdf_by_pages_per_file
            pages_per_file = params.get('pages_per_file', 1)
            output_dir = os.path.dirname(output_file)
            result = split_pdf_by_pages_per_file(input_file, output_dir, pages_per_file)
            return len(result) > 0
        except Exception as e:
            print(f"Split error: {e}")
            return False
    
    def _clean_metadata_operation(
        self,
        input_file: str,
        output_file: str,
        params: Dict[str, Any]
    ) -> bool:
        """Clean metadata operation."""
        try:
            from components.metadata_cleaner import remove_all_pdf_metadata
            return remove_all_pdf_metadata(input_file, output_file)
        except Exception as e:
            print(f"Metadata cleaning error: {e}")
            return False
    
    def _convert_operation(
        self,
        input_file: str,
        output_file: str,
        params: Dict[str, Any]
    ) -> bool:
        """Convert to PDF operation."""
        try:
            from components.convert_to_pdf import (
                doc_to_pdf, xls_to_pdf, ppt_to_pdf, png_to_pdf, jpg_to_pdf, epub_to_pdf
            )
            
            file_type = params.get('file_type', 'DOC/DOCX')
            conversion_functions = {
                'DOC/DOCX': doc_to_pdf,
                'XLS/XLSX': xls_to_pdf,
                'PPT/PPTX': ppt_to_pdf,
                'PNG': png_to_pdf,
                'JPG/JPEG': jpg_to_pdf,
                'EPUB': epub_to_pdf
            }
            
            if file_type in conversion_functions:
                return conversion_functions[file_type](input_file, output_file)
            else:
                return False
        except Exception as e:
            print(f"Conversion error: {e}")
            return False

    def _bypass_scribd_operation(
        self,
        input_file: str,
        output_file: str,
        params: Dict[str, Any]
    ) -> bool:
        """Bypass Scribd operation."""
        try:
            from components.scribd_bypass import ScribdBypass
            file_type = params.get('file_type', 'document')
            custom_title = params.get('custom_title', None)
            output_dir = os.path.dirname(output_file) or 'scribd_output'
            bypass = ScribdBypass(output_dir)
            result = bypass.create_scribd_file(input_file, file_type, custom_title)
            if result:
                # Nếu output_file khác với result, đổi tên file cho đúng output_file
                if os.path.abspath(result) != os.path.abspath(output_file):
                    import shutil
                    shutil.move(result, output_file)
                return True
            return False
        except Exception as e:
            return False


def process_pdf_directory(
    input_dir: str,
    output_dir: str,
    operation: str,
    operation_params: Dict[str, Any],
    progress_callback: Optional[Callable] = None
) -> Dict[str, Any]:
    """Convenience function to process PDF directory.
    
    Args:
        input_dir: Input directory path
        output_dir: Output directory path
        operation: Operation to perform
        operation_params: Parameters for the operation
        progress_callback: Callback function for progress updates
        
    Returns:
        Dictionary containing processing results
    """
    processor = BatchProcessor()
    return processor.process_directory(
        input_dir, output_dir, operation, operation_params,
        progress_callback=progress_callback
    ) 