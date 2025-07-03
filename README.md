# PDF Hash Changer

Ứng dụng thay đổi hash PDF với giao diện đa dạng và tính năng nâng cao.

## Tính năng chính

- ✅ **Xử lý file đơn lẻ**: Thay đổi metadata của một file PDF
- ✅ **Xử lý hàng loạt**: Xử lý nhiều file PDF cùng lúc
- ✅ **Giao diện đồ họa**: GUI thân thiện với người dùng
- ✅ **Giao diện dòng lệnh**: CLI mạnh mẽ cho tự động hóa
- ✅ **Xử lý song song**: Tăng tốc độ xử lý với multi-threading
- ✅ **Báo cáo chi tiết**: Theo dõi tiến trình và kết quả xử lý
- ✅ **Tùy chỉnh metadata**: Hỗ trợ metadata tùy chỉnh
- ✅ **Xử lý lỗi**: Error handling toàn diện

## Cài đặt

### Yêu cầu hệ thống
- Python 3.7+
- Windows/Linux/macOS

### Cài đặt dependencies
```bash
pip install -r requirements.txt
```

## Sử dụng

### 1. Giao diện đồ họa (GUI)
```bash
python gui_app.py
```

**Tính năng GUI:**
- Chọn file đơn lẻ hoặc thư mục để xử lý hàng loạt
- Tùy chỉnh metadata JSON
- Theo dõi tiến trình xử lý
- Xem log chi tiết
- Báo cáo kết quả

### 2. Giao diện dòng lệnh (CLI)

#### Xử lý file đơn lẻ
```bash
# Cơ bản
python change_hash_pdf.py input.pdf

# Với thư mục output tùy chỉnh
python change_hash_pdf.py input.pdf --output-dir custom_output

# Với metadata tùy chỉnh
python change_hash_pdf.py input.pdf --metadata '{"CustomKey": "CustomValue"}'

# Với tên file output tùy chỉnh
python change_hash_pdf.py input.pdf --output-filename my_output.pdf

# Chế độ verbose
python change_hash_pdf.py input.pdf --verbose
```

#### Xử lý hàng loạt
```bash
# Xử lý tất cả PDF trong thư mục
python batch_processor.py /path/to/pdfs

# Với thư mục output tùy chỉnh
python batch_processor.py /path/to/pdfs --output-dir /path/to/output

# Với metadata tùy chỉnh
python batch_processor.py /path/to/pdfs --metadata '{"CustomKey": "CustomValue"}'

# Với số worker tùy chỉnh
python batch_processor.py /path/to/pdfs --workers 8

# Chế độ verbose
python batch_processor.py /path/to/pdfs --verbose
```

### 3. Sử dụng như module Python
```python
from change_hash_pdf import PDFHashChanger

# Khởi tạo
changer = PDFHashChanger("output_directory")

# Xử lý file
result = changer.process_pdf("input.pdf", {"CustomKey": "CustomValue"})
print(f"Output: {result}")
```

## Cấu trúc dự án

```
Fengshui/
├── change_hash_pdf.py      # Core PDF processing logic
├── batch_processor.py      # Batch processing functionality
├── gui_app.py             # GUI application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── output/               # Default output directory
```

## Cấu hình

Chỉnh sửa `config.py` để tùy chỉnh:

- **Thư mục output mặc định**
- **Metadata mặc định**
- **Số worker cho xử lý song song**
- **Cài đặt logging**
- **Cài đặt GUI**

## Ví dụ sử dụng

### Metadata tùy chỉnh
```json
{
  "/CustomHashBypass": "1",
  "/ProcessingDate": "2024-01-01",
  "/UserID": "user123",
  "/Version": "2.0"
}
```

### Xử lý hàng loạt với báo cáo
```bash
python batch_processor.py ./pdfs --workers 4 --verbose
```

Kết quả sẽ tạo file `processing_report.txt` với thông tin chi tiết.

## Tính năng nâng cao

### 1. Xử lý song song
- Tự động phát hiện số CPU cores
- Có thể tùy chỉnh số worker
- Tối ưu hiệu suất cho file lớn

### 2. Error Handling
- Xử lý file bị lỗi
- Log chi tiết các lỗi
- Tiếp tục xử lý khi gặp lỗi

### 3. Báo cáo chi tiết
- Thời gian xử lý từng file
- Tổng thời gian xử lý
- Tỷ lệ thành công/thất bại
- Đường dẫn file output

### 4. Tùy chỉnh metadata
- Hỗ trợ JSON metadata
- Validation JSON
- Metadata mặc định

## Troubleshooting

### Lỗi thường gặp

1. **File không tồn tại**
   ```
   Error: File not found: input.pdf
   ```
   **Giải pháp**: Kiểm tra đường dẫn file

2. **Lỗi JSON metadata**
   ```
   Error: Invalid JSON metadata
   ```
   **Giải pháp**: Sử dụng JSON validator

3. **Lỗi quyền truy cập**
   ```
   Error: Permission denied
   ```
   **Giải pháp**: Chạy với quyền admin hoặc thay đổi thư mục output

### Debug mode
```bash
# Bật debug logging
export LOG_LEVEL=DEBUG
python change_hash_pdf.py input.pdf --verbose
```

## Đóng góp

1. Fork dự án
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## License

MIT License - xem file LICENSE để biết thêm chi tiết.

## Changelog

### v2.0.0 (Current)
- ✅ Refactor hoàn toàn codebase
- ✅ Thêm GUI application
- ✅ Thêm batch processing
- ✅ Cải thiện error handling
- ✅ Thêm logging system
- ✅ Thêm configuration system
- ✅ Thêm CLI arguments
- ✅ Thêm progress tracking
- ✅ Thêm detailed reporting

### v1.0.0 (Original)
- ✅ Basic PDF hash changing
- ✅ Random filename generation 