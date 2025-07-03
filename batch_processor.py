#!/usr/bin/env python3
"""
Batch PDF Processor - Process multiple PDF files with hash changing
"""

import os
import sys
import time
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from change_hash_pdf import PDFHashChanger
import config

logger = logging.getLogger(__name__)


class BatchPDFProcessor:
    """Process multiple PDF files in batch"""
    
    def __init__(self, input_dir: str, output_dir: str = None):
        """
        Initialize batch processor
        
        Args:
            input_dir: Directory containing input PDF files
            output_dir: Output directory (default: input_dir/output)
        """
        self.input_dir = Path(input_dir)
        if not self.input_dir.exists():
            raise ValueError(f"Input directory does not exist: {input_dir}")
        
        self.output_dir = Path(output_dir) if output_dir else self.input_dir / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        self.changer = PDFHashChanger(str(self.output_dir))
        
    def find_pdf_files(self) -> List[Path]:
        """
        Find all PDF files in input directory
        
        Returns:
            List of PDF file paths
        """
        pdf_files = []
        for ext in config.SUPPORTED_EXTENSIONS:
            pdf_files.extend(self.input_dir.glob(f"*{ext}"))
            pdf_files.extend(self.input_dir.glob(f"*{ext.upper()}"))
        
        return sorted(pdf_files)
    
    def process_single_file(self, pdf_path: Path, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a single PDF file
        
        Args:
            pdf_path: Path to PDF file
            metadata: Optional custom metadata
            
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        result = {
            "input_file": str(pdf_path),
            "success": False,
            "output_file": None,
            "error": None,
            "processing_time": 0
        }
        
        try:
            output_file = self.changer.process_pdf(str(pdf_path), metadata)
            if output_file:
                result["success"] = True
                result["output_file"] = output_file
            else:
                result["error"] = "Processing failed"
                
        except Exception as e:
            result["error"] = str(e)
            
        result["processing_time"] = time.time() - start_time
        return result
    
    def process_batch(self, metadata: Optional[Dict[str, Any]] = None, 
                     max_workers: int = None) -> List[Dict[str, Any]]:
        """
        Process all PDF files in batch
        
        Args:
            metadata: Optional custom metadata for all files
            max_workers: Maximum number of concurrent workers
            
        Returns:
            List of processing results
        """
        pdf_files = self.find_pdf_files()
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.input_dir}")
            return []
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        max_workers = max_workers or config.MAX_CONCURRENT_PROCESSES
        
        results = []
        
        # Process files in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.process_single_file, pdf_path, metadata): pdf_path
                for pdf_path in pdf_files
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_file):
                pdf_path = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result["success"]:
                        logger.info(f"✅ Processed: {pdf_path.name} -> {Path(result['output_file']).name}")
                    else:
                        logger.error(f"❌ Failed: {pdf_path.name} - {result['error']}")
                        
                except Exception as e:
                    logger.error(f"❌ Exception processing {pdf_path.name}: {str(e)}")
                    results.append({
                        "input_file": str(pdf_path),
                        "success": False,
                        "output_file": None,
                        "error": str(e),
                        "processing_time": 0
                    })
        
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate processing report
        
        Args:
            results: List of processing results
            
        Returns:
            Formatted report string
        """
        if not results:
            return "No files processed"
        
        total_files = len(results)
        successful = sum(1 for r in results if r["success"])
        failed = total_files - successful
        total_time = sum(r["processing_time"] for r in results)
        
        report = f"""
=== BATCH PROCESSING REPORT ===
Total files: {total_files}
Successful: {successful}
Failed: {failed}
Total processing time: {total_time:.2f} seconds
Average time per file: {total_time/total_files:.2f} seconds

Output directory: {self.output_dir}

DETAILED RESULTS:
"""
        
        for i, result in enumerate(results, 1):
            status = "✅" if result["success"] else "❌"
            report += f"{i:2d}. {status} {Path(result['input_file']).name}"
            
            if result["success"]:
                report += f" -> {Path(result['output_file']).name}"
            else:
                report += f" (Error: {result['error']})"
            
            report += f" ({result['processing_time']:.2f}s)\n"
        
        return report


def main():
    """Main function for batch processing"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Batch PDF Hash Changer - Process multiple PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_processor.py /path/to/pdfs
  python batch_processor.py /path/to/pdfs --output-dir /path/to/output
  python batch_processor.py /path/to/pdfs --metadata '{"CustomKey": "CustomValue"}'
  python batch_processor.py /path/to/pdfs --workers 8
        """
    )
    
    parser.add_argument("input_dir", help="Directory containing PDF files")
    parser.add_argument("--output-dir", "-o", help="Output directory")
    parser.add_argument("--metadata", "-m", type=str,
                       help="Custom metadata as JSON string")
    parser.add_argument("--workers", "-w", type=int, 
                       default=config.MAX_CONCURRENT_PROCESSES,
                       help=f"Number of concurrent workers (default: {config.MAX_CONCURRENT_PROCESSES})")
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
    
    try:
        # Initialize processor
        processor = BatchPDFProcessor(args.input_dir, args.output_dir)
        
        # Process files
        print(f"Starting batch processing of PDF files in: {args.input_dir}")
        results = processor.process_batch(custom_metadata, args.workers)
        
        # Generate and display report
        report = processor.generate_report(results)
        print(report)
        
        # Save report to file
        report_file = processor.output_dir / "processing_report.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"\nReport saved to: {report_file}")
        
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 