import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from merge_pages_landscape import merge_pdf_vertical_to_horizontal


class MergePagesLandscapeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ghép PDF - 2 trang dọc thành 1 trang ngang")
        self.root.geometry("750x700")
        self.root.resizable(True, True)
        
        # Biến lưu đường dẫn
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        
        # Biến tùy chọn
        self.preserve_aspect_ratio = tk.BooleanVar(value=True)
        self.add_margin = tk.BooleanVar(value=True)
        self.auto_adjust = tk.BooleanVar(value=True)
        self.dpi_value = tk.IntVar(value=200)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Cấu hình grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Tiêu đề
        title_label = ttk.Label(main_frame, text="Ghép PDF - 2 trang dọc thành 1 trang ngang", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Mô tả
        desc_label = ttk.Label(main_frame, 
                              text="Chức năng này sẽ ghép 2 trang PDF dọc thành 1 trang ngang với tùy chọn điều chỉnh tỷ lệ tự động",
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
        
        # Frame tùy chọn
        options_frame = ttk.LabelFrame(main_frame, text="Tùy chọn điều chỉnh", padding="15")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        options_frame.columnconfigure(1, weight=1)
        
        # Tùy chọn giữ nguyên tỷ lệ
        ttk.Checkbutton(options_frame, text="Giữ nguyên tỷ lệ khung hình", 
                       variable=self.preserve_aspect_ratio).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Tùy chọn thêm margin
        ttk.Checkbutton(options_frame, text="Thêm khoảng cách giữa 2 trang", 
                       variable=self.add_margin).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Tùy chọn tự động điều chỉnh
        ttk.Checkbutton(options_frame, text="Tự động điều chỉnh để tránh giãn trang", 
                       variable=self.auto_adjust).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Tùy chọn DPI
        ttk.Label(options_frame, text="Độ phân giải (DPI):").grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        dpi_frame = ttk.Frame(options_frame)
        dpi_frame.grid(row=3, column=1, sticky=tk.W, pady=(10, 5))
        
        # Thanh kéo DPI
        dpi_scale = ttk.Scale(dpi_frame, from_=100, to=300, variable=self.dpi_value, 
                             orient=tk.HORIZONTAL, length=150, command=self.on_dpi_scale_change)
        dpi_scale.grid(row=0, column=0, padx=(0, 10))
        
        # Ô input DPI
        dpi_entry = ttk.Entry(dpi_frame, textvariable=self.dpi_value, width=8)
        dpi_entry.grid(row=0, column=1, padx=(0, 5))
        dpi_entry.bind('<FocusOut>', self.on_dpi_focus_out)
        dpi_entry.bind('<Return>', self.on_dpi_entry_change)
        
        # Label đơn vị
        ttk.Label(dpi_frame, text="DPI").grid(row=0, column=2)
        
        # Thông tin về tùy chọn
        info_text = """
• Giữ nguyên tỷ lệ: Đảm bảo nội dung không bị méo
• Thêm khoảng cách: Tạo margin giữa 2 trang để dễ đọc
• Tự động điều chỉnh: Tính toán kích thước tối ưu để tránh giãn
• Độ phân giải: Càng cao càng rõ nét nhưng file sẽ lớn hơn (100-300 DPI)
        """
        ttk.Label(options_frame, text=info_text, justify=tk.LEFT, 
                 font=("Arial", 9)).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        # Nút thực hiện
        self.merge_button = ttk.Button(main_frame, text="Bắt đầu ghép PDF", 
                                      command=self.start_merge, style="Accent.TButton")
        self.merge_button.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Label trạng thái
        self.status_label = ttk.Label(main_frame, text="Sẵn sàng", font=("Arial", 10))
        self.status_label.grid(row=7, column=0, columnspan=3, pady=10)
    
    def on_dpi_scale_change(self, value):
        """Xử lý khi thanh kéo DPI thay đổi"""
        try:
            dpi = int(float(value))
            self.dpi_value.set(dpi)
        except (ValueError, tk.TclError):
            pass
    
    def on_dpi_entry_change(self, event):
        """Xử lý khi người dùng nhấn Enter trong ô input DPI"""
        self.validate_dpi_value()
    
    def on_dpi_focus_out(self, event):
        """Xử lý khi ô input DPI mất focus"""
        self.validate_dpi_value()
    
    def validate_dpi_value(self):
        """Kiểm tra và điều chỉnh giá trị DPI"""
        try:
            # Lấy giá trị từ ô input
            input_value = self.dpi_value.get()
            
            # Kiểm tra nếu ô input trống
            if input_value == "":
                self.dpi_value.set(200)  # Đặt về giá trị mặc định
                return
            
            dpi = int(input_value)
            # Đảm bảo giá trị trong khoảng hợp lệ
            if dpi < 100:
                self.dpi_value.set(100)
            elif dpi > 300:
                self.dpi_value.set(300)
        except (ValueError, tk.TclError):
            # Nếu giá trị không hợp lệ, đặt về giá trị mặc định
            self.dpi_value.set(200)
    
    def browse_input_file(self):
        """Chọn file PDF đầu vào"""
        filename = filedialog.askopenfilename(
            title="Chọn file PDF đầu vào",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Tự động đề xuất tên file output
            if not self.output_file.get():
                base_name = os.path.splitext(os.path.basename(filename))[0]
                output_path = os.path.join(os.path.dirname(filename), f"{base_name}_merged.pdf")
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
    
    def start_merge(self):
        """Bắt đầu quá trình ghép PDF"""
        input_path = self.input_file.get()
        output_path = self.output_file.get()
        
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
        
        # Bắt đầu xử lý trong thread riêng
        self.merge_button.config(state='disabled')
        self.progress.start()
        self.status_label.config(text="Đang xử lý...")
        
        # Lấy các tùy chọn
        preserve_ratio = self.preserve_aspect_ratio.get()
        add_margin = self.add_margin.get()
        dpi = self.dpi_value.get()
        
        thread = threading.Thread(target=self.merge_pdf_thread, 
                                args=(input_path, output_path, preserve_ratio, add_margin, dpi))
        thread.daemon = True
        thread.start()
    
    def merge_pdf_thread(self, input_path, output_path, preserve_ratio, add_margin, dpi):
        """Xử lý ghép PDF trong thread riêng"""
        try:
            merge_pdf_vertical_to_horizontal(input_path, output_path, preserve_ratio, add_margin, dpi)
            
            # Cập nhật UI trong main thread
            self.root.after(0, self.merge_completed, True, output_path)
            
        except Exception as e:
            # Cập nhật UI trong main thread
            self.root.after(0, self.merge_completed, False, str(e))
    
    def merge_completed(self, success, result):
        """Xử lý khi hoàn thành ghép PDF"""
        self.progress.stop()
        self.merge_button.config(state='normal')
        
        if success:
            self.status_label.config(text=f"Hoàn thành! File đã được lưu tại: {result}")
            messagebox.showinfo("Thành công", 
                              f"Đã ghép PDF thành công!\n\n"
                              f"File được lưu tại:\n{result}\n\n"
                              f"Các tùy chọn đã áp dụng:\n"
                              f"• Giữ nguyên tỷ lệ: {'Có' if self.preserve_aspect_ratio.get() else 'Không'}\n"
                              f"• Thêm margin: {'Có' if self.add_margin.get() else 'Không'}\n"
                              f"• Tự động điều chỉnh: {'Có' if self.auto_adjust.get() else 'Không'}\n"
                              f"• Độ phân giải: {self.dpi_value.get()} DPI")
        else:
            self.status_label.config(text=f"Lỗi: {result}")
            messagebox.showerror("Lỗi", f"Không thể ghép PDF:\n{result}")


def main():
    root = tk.Tk()
    app = MergePagesLandscapeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
