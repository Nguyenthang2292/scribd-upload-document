# Cải tiến chức năng ghép PDF - Khắc phục vấn đề giãn trang

## Vấn đề ban đầu
- Trang sách bị giãn không hợp lý khi ghép 2 trang dọc thành 1 trang ngang
- Không có tùy chọn điều chỉnh tỷ lệ
- Chất lượng hình ảnh thấp

## Các cải tiến đã thực hiện

### 1. Thuật toán tính toán tỷ lệ tối ưu
- **Tính toán dựa trên chiều cao**: Sử dụng chiều cao lớn nhất của 2 trang làm chuẩn
- **Tỷ lệ scale thông minh**: 
  - Tối thiểu: 0.7 (đảm bảo không quá nhỏ)
  - Tối đa: 1.0 (đảm bảo không bị phóng to)
- **Căn giữa tự động**: Mỗi trang được căn giữa trong nửa không gian của mình

### 2. Tùy chọn điều chỉnh linh hoạt
- **Giữ nguyên tỷ lệ khung hình**: Đảm bảo nội dung không bị méo
- **Thêm khoảng cách**: Tạo margin 30px giữa 2 trang để dễ đọc
- **Tự động điều chỉnh**: Tính toán kích thước tối ưu để tránh giãn
- **Độ phân giải (DPI)**: Từ 100-300 DPI, mặc định 200 DPI

### 3. Cải thiện chất lượng
- **DPI cao hơn**: Tăng từ 150 lên 200 DPI mặc định
- **Xử lý lỗi tốt hơn**: Fallback khi không có pdf2image
- **Hỗ trợ trang lẻ**: Xử lý trường hợp số trang không chẵn

### 4. Giao diện người dùng
- **Thêm tùy chọn DPI**: Thanh trượt điều chỉnh độ phân giải
- **Thông tin chi tiết**: Hiển thị các tùy chọn đã áp dụng
- **Giao diện rộng hơn**: Tăng kích thước cửa sổ để hiển thị đầy đủ

## Cách sử dụng

### Tùy chọn khuyến nghị:
1. **Giữ nguyên tỷ lệ khung hình**: ✅ Bật
2. **Thêm khoảng cách giữa 2 trang**: ✅ Bật  
3. **Tự động điều chỉnh**: ✅ Bật
4. **Độ phân giải**: 200 DPI (cân bằng giữa chất lượng và kích thước file)

### Cho chất lượng cao nhất:
- Độ phân giải: 250-300 DPI
- Tất cả tùy chọn bật

### Cho file nhỏ gọn:
- Độ phân giải: 150 DPI
- Tắt "Thêm khoảng cách" nếu muốn tiết kiệm không gian

## Thuật toán mới

### Tính toán kích thước trang mới:
```
new_height = max(height1, height2)
half_width = new_height
new_width = half_width * 2
```

### Tính toán tỷ lệ scale:
```
scale1 = min(half_width / width1, new_height / height1)
scale2 = min(half_width / width2, new_height / height2)

// Giới hạn tỷ lệ
scale1 = max(0.7, min(1.0, scale1))
scale2 = max(0.7, min(1.0, scale2))
```

### Vị trí căn chỉnh:
```
// Trang 1 (bên trái)
x1 = margin
y1 = (new_height - height1 * scale1) / 2

// Trang 2 (bên phải)  
x2 = half_width + margin
y2 = (new_height - height2 * scale2) / 2
```

## Kết quả mong đợi
- Trang sách không bị giãn méo
- Nội dung rõ ràng, dễ đọc
- Tỷ lệ khung hình được bảo toàn
- Chất lượng hình ảnh cao
- File PDF có kích thước hợp lý

## Lưu ý kỹ thuật
- Cần cài đặt `pdf2image` để có chất lượng tốt nhất
- Nếu không có `pdf2image`, sẽ sử dụng fallback với chất lượng thấp hơn
- Thời gian xử lý tăng theo DPI được chọn
- Kích thước file tăng theo DPI
