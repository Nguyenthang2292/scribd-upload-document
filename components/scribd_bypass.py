#!/usr/bin/env python3
"""
Scribd Bypass Tool - Tạo file PDF với metadata tùy chỉnh để upload lên Scribd
Dựa trên các nghiên cứu từ GitHub repositories về Scribd bypass
"""

import os
import random
import string
import time
from pathlib import Path
from typing import Dict, Any, Optional
from .change_hash_pdf import PDFHashChanger


class ScribdBypass:
    """Class chuyên dụng để bypass Scribd upload restrictions"""

    def __init__(self, output_dir: str = "scribd_output"):
        """
        Khởi tạo Scribd Bypass

        Args:
            output_dir: Thư mục lưu file output
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.changer = PDFHashChanger(str(self.output_dir))

    def generate_scribd_metadata(self, file_type: str = "document") -> Dict[str, Any]:
        """
        Tạo metadata phù hợp cho Scribd

        Args:
            file_type: Loại file (document, book, presentation, etc.)

        Returns:
            Dictionary chứa metadata
        """
        current_time = int(time.time())
        random_time = current_time - random.randint(0, 63072000)
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        base_metadata = {
            "/CustomHashBypass": str(random.randint(1, 999)),
            "/ScribdUpload": "true",
            "/UploadTimestamp": str(random_time),
            "/FileID": random_id,
            "/ProcessingDate": time.strftime("%Y-%m-%d", time.localtime(random_time)),
            "/Version": f"{random.randint(1, 9)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            "/Creator": "Document Creator",
            "/Producer": "PDF Producer",
            "/CreationDate": f"D:{random_time}",
            "/ModDate": f"D:{random_time}"
        }
        if file_type == "document":
            base_metadata.update({
                "/DocumentType": "Document",
                "/Category": "General",
                "/Language": "en-US"
            })
        elif file_type == "book":
            base_metadata.update({
                "/DocumentType": "Book",
                "/Category": "Literature",
                "/Language": "en-US",
                "/ISBN": f"978-{random.randint(100000000, 999999999)}-{random.randint(0, 9)}"
            })
        elif file_type == "presentation":
            base_metadata.update({
                "/DocumentType": "Presentation",
                "/Category": "Business",
                "/Language": "en-US",
                "/SlideCount": str(random.randint(10, 50))
            })
        elif file_type == "academic":
            base_metadata.update({
                "/DocumentType": "Academic",
                "/Category": "Education",
                "/Language": "en-US",
                "/Subject": "Research Paper",
                "/Keywords": "research, academic, study"
            })
        return base_metadata

    def create_scribd_file(self, input_file: str, file_type: str = "document",
                          custom_title: Optional[str] = None) -> Optional[str]:
        """
        Tạo file PDF phù hợp cho Scribd

        Args:
            input_file: Đường dẫn file PDF gốc
            file_type: Loại file (document, book, presentation, academic)
            custom_title: Tên file tùy chỉnh

        Returns:
            Đường dẫn file output hoặc None nếu lỗi
        """
        try:
            if not os.path.exists(input_file):
                print(f"❌ File không tồn tại: {input_file}")
                return None
            metadata = self.generate_scribd_metadata(file_type)
            if custom_title:
                output_filename = f"{custom_title}_{int(time.time())}.pdf"
            else:
                random_name = ''.join(random.choices(string.ascii_lowercase, k=8))
                output_filename = f"scribd_{random_name}_{int(time.time())}.pdf"
            print(f"🔄 Đang xử lý file: {input_file}")
            print(f"📄 Loại file: {file_type}")
            print(f"🏷️  Tên file output: {output_filename}")
            result = self.changer.process_pdf(input_file, metadata, output_filename)
            if result:
                print(f"✅ Thành công! File đã được tạo: {result}")
                print(f"📊 Metadata được thêm: {len(metadata)} trường")
                return result
            else:
                print("❌ Lỗi khi xử lý file")
                return None
        except Exception as e:
            print(f"❌ Lỗi: {str(e)}")
            return None

    def create_multiple_scribd_files(self, input_file: str, count: int = 5,
                                   file_types: Optional[list] = None) -> list:
        """
        Tạo nhiều file với metadata khác nhau

        Args:
            input_file: File PDF gốc
            count: Số lượng file cần tạo
            file_types: Danh sách loại file (nếu None sẽ random)

        Returns:
            Danh sách đường dẫn file đã tạo
        """
        if file_types is None:
            file_types = ["document", "book", "presentation", "academic"]
        results = []
        print(f"🔄 Đang tạo {count} file cho Scribd...")
        for i in range(count):
            file_type = random.choice(file_types)
            custom_title = f"scribd_file_{i+1}"
            print(f"\n📄 Tạo file {i+1}/{count}...")
            result = self.create_scribd_file(input_file, file_type, custom_title)
            if result:
                results.append(result)
            else:
                print(f"⚠️  Lỗi khi tạo file {i+1}")
        print(f"\n✅ Hoàn thành! Đã tạo {len(results)}/{count} file thành công")
        return results

    def show_metadata_info(self, file_path: str):
        """
        Hiển thị thông tin metadata của file

        Args:
            file_path: Đường dẫn file PDF
        """
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            metadata = reader.metadata
            print(f"\n📊 Metadata của file: {file_path}")
            print("-" * 50)
            if metadata:
                for key, value in metadata.items():
                    print(f"{key}: {value}")
            else:
                print("Không có metadata")
        except Exception as e:
            print(f"❌ Lỗi khi đọc metadata: {str(e)}")


def main():
    """Main function với CLI interface"""
    import argparse
    parser = argparse.ArgumentParser(
        description="Scribd Bypass Tool - Tạo file PDF để upload lên Scribd",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  python scribd_bypass.py input.pdf
  python scribd_bypass.py input.pdf --type book --title "My Book"
  python scribd_bypass.py input.pdf --multiple 10 --types document book
  python scribd_bypass.py input.pdf --show-metadata
        """
    )
    parser.add_argument("input_file", help="File PDF gốc")
    parser.add_argument("--type", "-t", default="document",
                       choices=["document", "book", "presentation", "academic"],
                       help="Loại file (default: document)")
    parser.add_argument("--title", help="Tên file tùy chỉnh")
    parser.add_argument("--multiple", "-m", type=int, help="Tạo nhiều file")
    parser.add_argument("--types", nargs="+",
                       choices=["document", "book", "presentation", "academic"],
                       help="Danh sách loại file cho multiple mode")
    parser.add_argument("--output-dir", "-o", default="scribd_output",
                       help="Thư mục output (default: scribd_output)")
    parser.add_argument("--show-metadata", "-s", action="store_true",
                       help="Hiển thị metadata của file gốc")
    args = parser.parse_args()
    bypass = ScribdBypass(args.output_dir)
    if args.show_metadata:
        bypass.show_metadata_info(args.input_file)
        return
    if args.multiple:
        results = bypass.create_multiple_scribd_files(
            args.input_file,
            args.multiple,
            args.types
        )
        if results:
            print(f"\n📁 Tất cả file đã được lưu trong: {args.output_dir}")
            print("🎯 Bây giờ bạn có thể upload các file này lên Scribd!")
    else:
        result = bypass.create_scribd_file(
            args.input_file,
            args.type,
            args.title
        )
        if result:
            print(f"\n📁 File đã được lưu trong: {args.output_dir}")
            print("🎯 Bây giờ bạn có thể upload file này lên Scribd!")


if __name__ == "__main__":
    main() 