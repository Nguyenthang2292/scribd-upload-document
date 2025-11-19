import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from compress_pdf import compress_pdf


class CompressPDFGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Nén PDF - Giảm kích thước file")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Biến lưu đường dẫn và cài đặt
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.compression_mode = tk.StringVar(value="medium")
        
        self.setup_ui()
        
        # Bind events
        self.compression_mode.trace('w', self.update_mode_info)
        
    def setup_ui(self):
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Cấu hình grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Tiêu đề
        title_label = ttk.Label(main_frame, text="Nén PDF - Giảm kích thước file", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Mô tả
        desc_label = ttk.Label(main_frame, 
                              text="Chức năng này sẽ nén file PDF bằng cách giảm chất lượng ảnh để giảm kích thước file",
                              font=("Arial", 10))
        desc_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # Chọn file input
        ttk.Label(main_frame, text="File PDF đầu vào:").grid(row=2, column=0, sticky=tk.W, pady=5)
        input_entry = ttk.Entry(main_frame, textvariable=self.input_file, width=50)
        input_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(main_frame, text="Chọn file", command=self.browse_input_file).grid(row=2, column=2, pady=5)
        
        # Chọn file output
        ttk.Label(main_frame, text="File PDF đầu ra:").grid(row=3, column=0, sticky=tk.W, pady=5)
        output_entry = ttk.Entry(main_frame, textvariable=self.output_file, width=50)
        output_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(main_frame, text="Chọn thư mục", command=self.browse_output_file).grid(row=3, column=2, pady=5)
        
        # Chọn mức nén
        ttk.Label(main_frame, text="Mức nén:").grid(row=4, column=0, sticky=tk.W, pady=10)
        compression_frame = ttk.Frame(main_frame)
        compression_frame.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=10)
        
        # Radio buttons cho mức nén
        ttk.Radiobutton(compression_frame, text="Nén nhẹ (Chất lượng cao)", 
                       variable=self.compression_mode, value="low").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(compression_frame, text="Nén vừa (Cân bằng)", 
                       variable=self.compression_mode, value="medium").grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(compression_frame, text="Nén mạnh (Kích thước nhỏ)", 
                       variable=self.compression_mode, value="high").grid(row=2, column=0, sticky=tk.W)
        
        # Thông tin mức nén
        self.mode_info_label = ttk.Label(compression_frame, text="", font=("Arial", 9), foreground="gray")
        self.mode_info_label.grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        # Nút thực hiện
        self.compress_button = ttk.Button(main_frame, text="Bắt đầu nén PDF", 
                                         command=self.start_compress)
        self.compress_button.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Label trạng thái
        self.status_label = ttk.Label(main_frame, text="Sẵn sàng", font=("Arial", 10))
        self.status_label.grid(row=7, column=0, columnspan=3, pady=10)
        
        # Frame thông tin kích thước
        self.size_frame = ttk.LabelFrame(main_frame, text="Thông tin kích thước", padding="10")
        self.size_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        self.size_frame.columnconfigure(1, weight=1)
        
        self.original_size_label = ttk.Label(self.size_frame, text="Kích thước gốc: Chưa chọn file")
        self.original_size_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        self.compressed_size_label = ttk.Label(self.size_frame, text="Kích thước sau nén: -")
        self.compressed_size_label.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        
        self.savings_label = ttk.Label(self.size_frame, text="Tiết kiệm: -")
        self.savings_label.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        
        # Frame thông tin
        info_frame = ttk.LabelFrame(main_frame, text="Thông tin", padding="10")
        info_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        info_frame.columnconfigure(0, weight=1)
        
        info_text = """
• Nén nhẹ: Giữ chất lượng cao, giảm kích thước ít (10-30%)
• Nén vừa: Cân bằng chất lượng và kích thước (30-60%)
• Nén mạnh: Giảm kích thước nhiều, chất lượng thấp hơn (60-80%)
• Chỉ nén được file có chứa ảnh, file text thuần sẽ không giảm nhiều
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)
        
    def update_mode_info(self, *args):
        """Cập nhật thông tin mức nén"""
        mode = self.compression_mode.get()
        if mode == "low":
            info = "Chất lượng ảnh: 90%, Tỷ lệ: 100% - Giảm ít kích thước"
        elif mode == "medium":
            info = "Chất lượng ảnh: 65%, Tỷ lệ: 70% - Cân bằng tốt"
        else:  # high
            info = "Chất lượng ảnh: 40%, Tỷ lệ: 50% - Giảm nhiều kích thước"
        self.mode_info_label.config(text=info)
        
    def format_file_size(self, size_bytes):
        """Chuyển đổi bytes thành đơn vị dễ đọc"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def update_file_info(self, file_path):
        """Cập nhật thông tin file"""
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            self.original_size_label.config(text=f"Kích thước gốc: {self.format_file_size(size)}")
        else:
            self.original_size_label.config(text="Kích thước gốc: Chưa chọn file")
        
    def browse_input_file(self):
        """Chọn file PDF đầu vào"""
        filename = filedialog.askopenfilename(
            title="Chọn file PDF đầu vào",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            self.update_file_info(filename)
            # Tự động đề xuất tên file output
            if not self.output_file.get():
                base_name = os.path.splitext(os.path.basename(filename))[0]
                output_path = os.path.join(os.path.dirname(filename), f"{base_name}_compressed.pdf")
                self.output_file.set(output_path)
    
    def browse_output_file(self):
        """Chọn file PDF đầu ra"""
        filename = filedialog.asksaveasfilename(
            title="Chọn vị trí lưu file PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
    
    def start_compress(self):
        """Bắt đầu quá trình nén PDF"""
        input_path = self.input_file.get()
        output_path = self.output_file.get()
        mode = self.compression_mode.get()
        
        # Kiểm tra input
        if not input_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn file PDF đầu vào!")
            return
        
        if not output_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn vị trí lưu file PDF!")
            return
        
        if not os.path.exists(input_path):
            messagebox.showerror("Lỗi", "File PDF đầu vào không tồn tại!")
            return
        
        # Kiểm tra thư mục output
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except:
                messagebox.showerror("Lỗi", "Không thể tạo thư mục lưu file!")
                return
        
        # Lưu kích thước gốc
        original_size = os.path.getsize(input_path)
        
        # Bắt đầu xử lý trong thread riêng
        self.compress_button.config(state='disabled')
        self.progress.start()
        self.status_label.config(text="Đang nén PDF...")
        
        thread = threading.Thread(target=self.compress_pdf_thread, args=(input_path, output_path, mode, original_size))
        thread.daemon = True
        thread.start()
    
    def compress_pdf_thread(self, input_path, output_path, mode, original_size):
        """Xử lý nén PDF trong thread riêng"""
        try:
            compress_pdf(input_path, output_path, mode)
            
            # Tính toán kích thước sau nén
            compressed_size = os.path.getsize(output_path)
            savings = original_size - compressed_size
            savings_percent = (savings / original_size) * 100
            
            # Cập nhật UI trong main thread
            self.root.after(0, self.compress_completed, True, output_path, original_size, compressed_size, savings_percent)
            
        except Exception as e:
            # Cập nhật UI trong main thread
            self.root.after(0, self.compress_completed, False, str(e), 0, 0, 0)
    
    def compress_completed(self, success, result, original_size=0, compressed_size=0, savings_percent=0):
        """Xử lý khi hoàn thành nén PDF"""
        self.progress.stop()
        self.compress_button.config(state='normal')
        
        if success:
            # Cập nhật thông tin kích thước
            self.compressed_size_label.config(text=f"Kích thước sau nén: {self.format_file_size(compressed_size)}")
            self.savings_label.config(text=f"Tiết kiệm: {self.format_file_size(original_size - compressed_size)} ({savings_percent:.1f}%)")
            
            self.status_label.config(text=f"Hoàn thành! File đã được lưu tại: {result}")
            messagebox.showinfo("Thành công", 
                              f"Đã nén PDF thành công!\n\n"
                              f"Kích thước gốc: {self.format_file_size(original_size)}\n"
                              f"Kích thước sau nén: {self.format_file_size(compressed_size)}\n"
                              f"Tiết kiệm: {self.format_file_size(original_size - compressed_size)} ({savings_percent:.1f}%)\n\n"
                              f"File được lưu tại:\n{result}")
        else:
            self.status_label.config(text=f"Lỗi: {result}")
            messagebox.showerror("Lỗi", f"Không thể nén PDF:\n{result}")


def main():
    root = tk.Tk()
    app = CompressPDFGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
