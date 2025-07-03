#!/usr/bin/env python3
"""
GUI Application for PDF Hash Changer
Simple tkinter-based interface for the PDF processing tool
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

from change_hash_pdf import PDFHashChanger
from batch_processor import BatchPDFProcessor
import config
from scribd_bypass import ScribdBypass
from epub_to_pdf import epub_to_pdf
from tkinterdnd2 import DND_FILES, TkinterDnD


class PDFHashChangerGUI:
    """GUI application for PDF Hash Changer"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Hash Changer")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        
        # Variables
        self.input_file = tk.StringVar()
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.custom_metadata = tk.StringVar(value=json.dumps(config.DEFAULT_METADATA, indent=2))
        self.processing_mode = tk.StringVar(value="single")
        self.scribd_mode = tk.BooleanVar(value=False)
        self.epub_file = tk.StringVar()
        self.epub_pdf_output = tk.StringVar()
        
        # Initialize UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Canvas + Scrollbar
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Main frame inside canvas
        main_frame = ttk.Frame(canvas, padding="10")
        self.main_frame = main_frame
        main_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        window_id = canvas.create_window((0, 0), window=main_frame, anchor="nw")

        def _on_canvas_resize(event):
            # Cập nhật chiều rộng main_frame cho khớp canvas
            canvas_width = event.width
            canvas.itemconfig(window_id, width=canvas_width)
        canvas.bind("<Configure>", _on_canvas_resize)

        # Mouse wheel scroll support
        def _on_mousewheel(event):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif event.num == 4:
                canvas.yview_scroll(-3, "units")
            elif event.num == 5:
                canvas.yview_scroll(3, "units")
        # Windows & Mac
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # Linux
        canvas.bind_all("<Button-4>", _on_mousewheel)
        canvas.bind_all("<Button-5>", _on_mousewheel)

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="PDF Hash Changer", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="we")
        
        # Processing mode
        mode_frame = ttk.LabelFrame(main_frame, text="Processing Mode", padding="10")
        mode_frame.grid(row=1, column=0, columnspan=3, sticky="we", pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="Single File", variable=self.processing_mode, 
                       value="single", command=self.on_mode_change).grid(row=0, column=0, padx=(0, 20))
        ttk.Radiobutton(mode_frame, text="Batch Processing", variable=self.processing_mode, 
                       value="batch", command=self.on_mode_change).grid(row=0, column=1)
        
        # Thêm checkbox Scribd Bypass
        self.scribd_checkbox = ttk.Checkbutton(mode_frame, text="Scribd Bypass Mode", variable=self.scribd_mode, command=self.on_scribd_mode)
        self.scribd_checkbox.grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        
        # Input section
        self.setup_input_section(main_frame)
        
        # Output section
        self.setup_output_section(main_frame)
        
        # Metadata section
        self.setup_metadata_section(main_frame)
        
        # EPUB to PDF section
        self.setup_epub_section(main_frame)
        
        # Buttons
        self.setup_buttons(main_frame)
        
        # Progress and log
        self.setup_progress_section(main_frame)
        
        # Initialize mode
        self.on_mode_change()
        
    def setup_input_section(self, parent):
        """Setup input file/directory selection"""
        input_frame = ttk.LabelFrame(parent, text="Input", padding="10")
        input_frame.grid(row=2, column=0, columnspan=3, sticky="we", pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Single file input
        self.single_input_frame = ttk.Frame(input_frame)
        self.single_input_frame.grid(row=0, column=0, columnspan=3, sticky="we")
        self.single_input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.single_input_frame, text="PDF File:").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.single_input_frame, textvariable=self.input_file, width=50).grid(row=0, column=1, sticky="we", padx=(5, 5))
        ttk.Button(self.single_input_frame, text="Browse", command=self.browse_input_file).grid(row=0, column=2)
        
        # Batch input
        self.batch_input_frame = ttk.Frame(input_frame)
        self.batch_input_frame.grid(row=1, column=0, columnspan=3, sticky="we")
        self.batch_input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.batch_input_frame, text="Directory:").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.batch_input_frame, textvariable=self.input_dir, width=50).grid(row=0, column=1, sticky="we", padx=(5, 5))
        ttk.Button(self.batch_input_frame, text="Browse", command=self.browse_input_dir).grid(row=0, column=2)
        
    def setup_output_section(self, parent):
        """Setup output directory selection"""
        output_frame = ttk.LabelFrame(parent, text="Output", padding="10")
        output_frame.grid(row=3, column=0, columnspan=3, sticky="we", pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky="w")
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).grid(row=0, column=1, sticky="we", padx=(5, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir).grid(row=0, column=2)
        
    def setup_metadata_section(self, parent):
        """Setup metadata configuration"""
        metadata_frame = ttk.LabelFrame(parent, text="Custom Metadata (JSON)", padding="10")
        metadata_frame.grid(row=4, column=0, columnspan=3, sticky="we", pady=(0, 10))
        metadata_frame.columnconfigure(0, weight=1)
        
        self.metadata_text = scrolledtext.ScrolledText(metadata_frame, height=6, width=60)
        self.metadata_text.grid(row=0, column=0, sticky="we")
        self.metadata_text.insert(tk.END, self.custom_metadata.get())
        
        # Buttons for metadata
        metadata_buttons = ttk.Frame(metadata_frame)
        metadata_buttons.grid(row=1, column=0, pady=(5, 0))
        
        ttk.Button(metadata_buttons, text="Reset to Default", 
                  command=self.reset_metadata).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(metadata_buttons, text="Validate JSON", 
                  command=self.validate_metadata).grid(row=0, column=1)
        
    def setup_epub_section(self, parent):
        """Setup EPUB to PDF section"""
        epub_frame = ttk.LabelFrame(parent, text="EPUB to PDF", padding="10")
        epub_frame.grid(row=5, column=0, columnspan=3, sticky="we", pady=(0, 10))
        epub_frame.columnconfigure(1, weight=1)
        
        ttk.Label(epub_frame, text="EPUB File:").grid(row=0, column=0, sticky="w")
        epub_entry = ttk.Entry(epub_frame, textvariable=self.epub_file, width=50)
        epub_entry.grid(row=0, column=1, sticky="we", padx=(5, 5))
        epub_entry.drop_target_register(DND_FILES)
        epub_entry.dnd_bind('<<Drop>>', self.on_drop_epub_file)
        ttk.Label(epub_frame, text="Output PDF:").grid(row=1, column=0, sticky="w")
        ttk.Entry(epub_frame, textvariable=self.epub_pdf_output, width=50).grid(row=1, column=1, sticky="we", padx=(5, 5))
        ttk.Button(epub_frame, text="Browse", command=self.browse_epub_file).grid(row=0, column=2)
        ttk.Button(epub_frame, text="Browse", command=self.browse_epub_pdf_output).grid(row=1, column=2)
        ttk.Button(epub_frame, text="Convert EPUB to PDF", command=self.convert_epub_to_pdf).grid(row=2, column=0, columnspan=3, pady=(10,0))
        
    def setup_buttons(self, parent):
        """Setup action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=6, column=0, columnspan=3, pady=(0, 10))
        
        self.process_button = ttk.Button(button_frame, text="Process PDF(s)", 
                                       command=self.process_files, style="Accent.TButton")
        self.process_button.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).grid(row=0, column=1)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).grid(row=0, column=2, padx=(10, 0))
        
    def setup_progress_section(self, parent):
        """Setup progress bar and log"""
        progress_frame = ttk.LabelFrame(parent, text="Progress & Log", padding="10")
        progress_frame.grid(row=7, column=0, columnspan=3, sticky="we", pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)
        parent.rowconfigure(7, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          mode='indeterminate')
        self.progress_bar.grid(row=0, column=0, sticky="we", pady=(0, 5))
        
        # Log text
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=10, width=80)
        self.log_text.grid(row=1, column=0, sticky="we")
        
    def on_mode_change(self):
        """Handle processing mode change"""
        if self.processing_mode.get() == "single":
            self.single_input_frame.grid()
            self.batch_input_frame.grid_remove()
        else:
            self.single_input_frame.grid_remove()
            self.batch_input_frame.grid()
            
    def browse_input_file(self):
        """Browse for input PDF file"""
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            
    def browse_input_dir(self):
        """Browse for input directory"""
        directory = filedialog.askdirectory(title="Select Directory with PDF Files")
        if directory:
            self.input_dir.set(directory)
            
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
            
    def reset_metadata(self):
        """Reset metadata to default"""
        self.metadata_text.delete(1.0, tk.END)
        self.metadata_text.insert(tk.END, json.dumps(config.DEFAULT_METADATA, indent=2))
        
    def validate_metadata(self):
        """Validate JSON metadata"""
        try:
            metadata_text = self.metadata_text.get(1.0, tk.END).strip()
            if metadata_text:
                json.loads(metadata_text)
                messagebox.showinfo("Validation", "✅ JSON metadata is valid!")
            else:
                messagebox.showinfo("Validation", "ℹ️ No metadata specified (will use default)")
        except json.JSONDecodeError as e:
            messagebox.showerror("Validation Error", f"❌ Invalid JSON: {str(e)}")
            
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Get metadata from text widget"""
        metadata_text = self.metadata_text.get(1.0, tk.END).strip()
        if metadata_text:
            try:
                return json.loads(metadata_text)
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Invalid JSON metadata")
                return None
        return None
        
    def log_message(self, message: str):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """Clear log text"""
        self.log_text.delete(1.0, tk.END)
        
    def on_scribd_mode(self):
        if self.scribd_mode.get():
            # Gợi ý metadata Scribd
            scribd_metadata = {
                "/CustomHashBypass": "1",
                "/ScribdUpload": "true",
                "/FileID": "unique_id",
                "/ProcessingDate": "2024-01-01"
            }
            self.metadata_text.delete(1.0, tk.END)
            self.metadata_text.insert(tk.END, json.dumps(scribd_metadata, indent=2))
        else:
            self.reset_metadata()
        
    def process_files(self):
        """Process PDF files based on selected mode"""
        # Nếu bật chế độ Scribd, dùng ScribdBypass
        if self.scribd_mode.get():
            if self.processing_mode.get() == "single":
                if not self.input_file.get():
                    messagebox.showerror("Error", "Please select an input PDF file")
                    return
                output_dir = self.output_dir.get() or "scribd_output"
                metadata = self.get_metadata()
                self.process_button.config(state="disabled")
                self.progress_bar.start()
                thread = threading.Thread(target=self._scribd_single_thread, args=(output_dir, metadata))
                thread.daemon = True
                thread.start()
                return
            else:
                if not self.input_dir.get():
                    messagebox.showerror("Error", "Please select an input directory")
                    return
                output_dir = self.output_dir.get() or "scribd_output"
                metadata = self.get_metadata()
                self.process_button.config(state="disabled")
                self.progress_bar.start()
                thread = threading.Thread(target=self._scribd_batch_thread, args=(output_dir, metadata))
                thread.daemon = True
                thread.start()
                return
        # Validate inputs
        if self.processing_mode.get() == "single":
            if not self.input_file.get():
                messagebox.showerror("Error", "Please select an input PDF file")
                return
        else:
            if not self.input_dir.get():
                messagebox.showerror("Error", "Please select an input directory")
                return
                
        # Get output directory
        output_dir = self.output_dir.get() or "output"
        
        # Get metadata
        metadata = self.get_metadata()
        
        # Start processing in separate thread
        self.process_button.config(state="disabled")
        self.progress_bar.start()
        
        thread = threading.Thread(
            target=self._process_files_thread,
            args=(output_dir, metadata)
        )
        thread.daemon = True
        thread.start()
        
    def _process_files_thread(self, output_dir: str, metadata: Optional[Dict[str, Any]]):
        """Process files in separate thread"""
        try:
            if self.processing_mode.get() == "single":
                self._process_single_file(output_dir, metadata)
            else:
                self._process_batch_files(output_dir, metadata)
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
        finally:
            # Re-enable UI
            self.root.after(0, self._processing_finished)
            
    def _process_single_file(self, output_dir: str, metadata: Optional[Dict[str, Any]]):
        """Process single file"""
        input_file = self.input_file.get()
        self.log_message(f"Processing single file: {input_file}")
        
        changer = PDFHashChanger(output_dir)
        result = changer.process_pdf(input_file, metadata)
        
        if result:
            self.log_message(f"✅ Success! Output: {result}")
            messagebox.showinfo("Success", f"PDF processed successfully!\nOutput: {result}")
        else:
            self.log_message("❌ Processing failed")
            messagebox.showerror("Error", "Failed to process PDF")
            
    def _process_batch_files(self, output_dir: str, metadata: Optional[Dict[str, Any]]):
        """Process batch files"""
        input_dir = self.input_dir.get()
        self.log_message(f"Processing batch files from: {input_dir}")
        
        processor = BatchPDFProcessor(input_dir, output_dir)
        results = processor.process_batch(metadata)
        
        # Display results
        successful = sum(1 for r in results if r["success"])
        total = len(results)
        
        self.log_message(f"Batch processing completed: {successful}/{total} successful")
        
        # Show detailed results
        report = processor.generate_report(results)
        self.log_message(report)
        
        # Show summary dialog
        messagebox.showinfo("Batch Processing Complete", 
                          f"Processed {total} files\nSuccessful: {successful}\nFailed: {total - successful}")
        
    def _processing_finished(self):
        """Called when processing is finished"""
        self.progress_bar.stop()
        self.process_button.config(state="normal")

    def _scribd_single_thread(self, output_dir, metadata):
        try:
            bypass = ScribdBypass(output_dir)
            input_file = self.input_file.get()
            result = bypass.create_scribd_file(input_file, file_type="document")
            if result:
                self.log_message(f"✅ Scribd file created: {result}")
                messagebox.showinfo("Success", f"Scribd PDF created!\nOutput: {result}")
            else:
                self.log_message("❌ Scribd processing failed")
                messagebox.showerror("Error", "Failed to create Scribd PDF")
        finally:
            self.root.after(0, self._processing_finished)

    def _scribd_batch_thread(self, output_dir, metadata):
        try:
            bypass = ScribdBypass(output_dir)
            input_dir = self.input_dir.get()
            pdf_files = list(Path(input_dir).glob("*.pdf"))
            results = []
            for i, pdf in enumerate(pdf_files, 1):
                self.log_message(f"Scribd: Processing {pdf.name} ({i}/{len(pdf_files)})")
                result = bypass.create_scribd_file(str(pdf), file_type="document")
                if result:
                    results.append(result)
            self.log_message(f"Batch Scribd processing completed: {len(results)}/{len(pdf_files)} successful")
            messagebox.showinfo("Batch Complete", f"Created {len(results)}/{len(pdf_files)} Scribd files!")
        finally:
            self.root.after(0, self._processing_finished)

    def browse_epub_file(self):
        filename = filedialog.askopenfilename(
            title="Select EPUB File",
            filetypes=[("EPUB files", "*.epub"), ("All files", "*.*")]
        )
        if filename:
            self.epub_file.set(filename)
            # Tự động điền output PDF cùng tên, cùng thư mục
            base, _ = os.path.splitext(filename)
            self.epub_pdf_output.set(base + ".pdf")

    def browse_epub_pdf_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.epub_pdf_output.set(filename)

    def convert_epub_to_pdf(self):
        epub_path = self.epub_file.get()
        pdf_path = self.epub_pdf_output.get()
        if not epub_path or not pdf_path:
            messagebox.showerror("Error", "Please select both EPUB file and output PDF path.")
            return
        try:
            epub_to_pdf(epub_path, pdf_path)
            messagebox.showinfo("Success", f"Đã chuyển đổi {epub_path} thành {pdf_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Lỗi khi chuyển đổi: {str(e)}")

    def on_drop_epub_file(self, event):
        file_path = event.data.strip('{}')
        self.epub_file.set(file_path)
        base, _ = os.path.splitext(file_path)
        self.epub_pdf_output.set(base + ".pdf")

    def on_drop_pdf_file(self, event):
        file_path = event.data.strip('{}')
        self.input_file.set(file_path)

    def on_drop_input_dir(self, event):
        dir_path = event.data.strip('{}')
        self.input_dir.set(dir_path)


def main():
    """Main function"""
    root = TkinterDnD.Tk()
    
    # Set theme if available
    try:
        style = ttk.Style()
        available_themes = style.theme_names()
        if config.THEME in available_themes:
            style.theme_use(config.THEME)
    except:
        pass
    
    app = PDFHashChangerGUI(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (config.WINDOW_WIDTH // 2)
    y = (root.winfo_screenheight() // 2) - (config.WINDOW_HEIGHT // 2)
    root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main() 