#!/usr/bin/env python3
"""
GUI Application for PDF Hash Changer
Simple tkinter-based interface for the PDF processing tool
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image, ImageTk

import config
from components.scribd_bypass import ScribdBypass
from components.compress_pdf import compress_pdf
from tkinterdnd2 import DND_FILES, TkinterDnD
from components.merge_pages_landscape import merge_pdf_vertical_to_horizontal
from components.merge_pdf import merge_pdfs
from components.convert_to_pdf import epub_to_pdf, doc_to_pdf, xls_to_pdf, ppt_to_pdf, png_to_pdf, jpg_to_pdf


class PDFUtilityToolkitGUI:
    """GUI application for PDF Utility Toolkit"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Utility Toolkit")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        
        # Variables
        self.pdf_input = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.custom_metadata = tk.StringVar(value=json.dumps(config.DEFAULT_METADATA, indent=2))
        self.processing_mode = tk.StringVar(value="single")
        self.scribd_mode = tk.BooleanVar(value=False)
        self.epub_file = tk.StringVar()
        self.epub_pdf_output = tk.StringVar()
        self.merge_landscape_mode = tk.BooleanVar(value=False)
        self.merge_input_file = tk.StringVar()
        self.merge_input_dir = tk.StringVar()
        
        self.function_options = sorted([
            "Bypass Scribd",
            "Convert to PDF",
            "Merge 2 Vertical Pages",
            "Merge PDFs",
            "Compress PDF"
        ])
        self.selected_function = tk.StringVar(value=self.function_options[0])
        self.frames = {}
        self.setup_menu_and_frames()
        
    def setup_menu_and_frames(self):
        # Dropdown menu
        menu_frame = ttk.Frame(self.root)
        menu_frame.pack(fill="x", padx=10, pady=10)
        ttk.Label(menu_frame, text="Select Function:").pack(side="left")
        style = ttk.Style()
        style.configure('Custom.TCombobox', fieldbackground='#e0e0e0', background='#e0e0e0', foreground='black', borderwidth=2, relief='raised')
        function_menu = ttk.Combobox(menu_frame, textvariable=self.selected_function, values=self.function_options, state="readonly", width=25, style='Custom.TCombobox')
        function_menu.pack(side="left", padx=10)
        function_menu.bind("<<ComboboxSelected>>", self.on_function_change)
        # Main content area
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(fill="both", expand=True)
        # Create all function frames but only show the selected one
        self.frames["Bypass Scribd"] = self.create_bypass_scribd_frame(self.content_frame)
        self.frames["Convert to PDF"] = self.create_convert_to_pdf_frame(self.content_frame)
        self.frames["Merge 2 Vertical Pages"] = self.create_merge_vertical_frame(self.content_frame)
        self.frames["Merge PDFs"] = self.create_merge_pdfs_frame(self.content_frame)
        self.frames["Compress PDF"] = self.create_compress_pdf_frame(self.content_frame)
        self.show_function_frame(self.selected_function.get())
        
    def on_function_change(self, event=None):
        self.show_function_frame(self.selected_function.get())

    def show_function_frame(self, function_name):
        for name, frame in self.frames.items():
            frame.pack_forget()
        self.frames[function_name].pack(fill="both", expand=True)

    def create_bypass_scribd_frame(self, parent):
        frame = ttk.Frame(parent)
        # Input
        input_frame = ttk.LabelFrame(frame, text="Input", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(input_frame, text="PDF Input:").grid(row=0, column=0, sticky="w")
        pdf_input_entry = tk.Entry(input_frame, textvariable=self.pdf_input, width=60)
        pdf_input_entry.grid(row=0, column=1, sticky="we", padx=(5, 5))
        ttk.Button(input_frame, text="Browse", command=self.browse_pdf_input, style='Accent.TButton').grid(row=0, column=2)
        # Enable drag & drop
        if hasattr(pdf_input_entry, 'drop_target_register'):
            pdf_input_entry.drop_target_register(DND_FILES)  # type: ignore
        if hasattr(pdf_input_entry, 'dnd_bind'):
            pdf_input_entry.dnd_bind('<<Drop>>', self.on_pdf_input_drop)  # type: ignore
        # Output
        output_frame = ttk.LabelFrame(frame, text="Output", padding="10")
        output_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky="w")
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).grid(row=0, column=1, sticky="we", padx=(5, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir, style='Accent.TButton').grid(row=0, column=2)
        # Process button
        ttk.Button(frame, text="Bypass Scribd", command=self.process_scribd_bypass, style='Accent.TButton').pack(pady=10)
        # Log
        self.scribd_log_text = scrolledtext.ScrolledText(frame, height=8, width=80)
        self.scribd_log_text.pack(fill="x", padx=10, pady=5)
        return frame

    def create_convert_to_pdf_frame(self, parent):
        frame = ttk.Frame(parent)
        # File type selection
        type_frame = ttk.LabelFrame(frame, text="Select File Type", padding="10")
        type_frame.pack(fill="x", padx=10, pady=5)
        self.convert_type = tk.StringVar(value="DOC/DOCX")
        type_options = ["DOC/DOCX", "XLS/XLSX", "PPT/PPTX", "PNG", "JPG/JPEG", "EPUB"]
        ttk.Label(type_frame, text="Source File Type:").pack(side="left")
        type_menu = ttk.Combobox(type_frame, textvariable=self.convert_type, values=type_options, state="readonly", width=12)
        type_menu.pack(side="left", padx=10)
        type_menu.bind("<<ComboboxSelected>>", lambda e: self.update_convert_input_fields())
        # Input/output fields
        self.convert_input = tk.StringVar()
        self.convert_output = tk.StringVar()
        input_frame = ttk.LabelFrame(frame, text="Input/Output", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)
        self.input_label = ttk.Label(input_frame, text="Input File:")
        self.input_label.grid(row=0, column=0, sticky="w")
        self.input_entry = ttk.Entry(input_frame, textvariable=self.convert_input, width=50)
        self.input_entry.grid(row=0, column=1, sticky="we", padx=(5, 5))
        self.input_browse_btn = ttk.Button(input_frame, text="Browse", command=self.browse_convert_input, style='Accent.TButton')
        self.input_browse_btn.grid(row=0, column=2)
        ttk.Label(input_frame, text="Output PDF:").grid(row=1, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.convert_output, width=50).grid(row=1, column=1, sticky="we", padx=(5, 5))
        ttk.Button(input_frame, text="Browse", command=self.browse_convert_output, style='Accent.TButton').grid(row=1, column=2)
        # Convert button
        ttk.Button(frame, text="Convert to PDF", command=self.process_convert_to_pdf, style='Accent.TButton').pack(pady=10)
        # Log
        self.convert_log_text = scrolledtext.ScrolledText(frame, height=8, width=80)
        self.convert_log_text.pack(fill="x", padx=10, pady=5)
        self.update_convert_input_fields()
        return frame

    def update_convert_input_fields(self):
        # Cập nhật bộ lọc file cho nút Browse dựa trên loại file
        filetype = self.convert_type.get()
        if filetype == "DOC/DOCX":
            self.input_label.config(text="DOC/DOCX File:")
        elif filetype == "XLS/XLSX":
            self.input_label.config(text="XLS/XLSX File:")
        elif filetype == "PPT/PPTX":
            self.input_label.config(text="PPT/PPTX File:")
        elif filetype == "PNG":
            self.input_label.config(text="PNG File:")
        elif filetype == "JPG/JPEG":
            self.input_label.config(text="JPG/JPEG File:")
        elif filetype == "EPUB":
            self.input_label.config(text="EPUB File:")

    def browse_convert_input(self):
        filetype = self.convert_type.get()
        if filetype == "DOC/DOCX":
            types = [("Word files", "*.doc;*.docx"), ("All files", "*.*")]
        elif filetype == "XLS/XLSX":
            types = [("Excel files", "*.xls;*.xlsx"), ("All files", "*.*")]
        elif filetype == "PPT/PPTX":
            types = [("PowerPoint files", "*.ppt;*.pptx"), ("All files", "*.*")]
        elif filetype == "PNG":
            types = [("PNG files", "*.png"), ("All files", "*.*")]
        elif filetype == "JPG/JPEG":
            types = [("JPEG files", "*.jpg;*.jpeg"), ("All files", "*.*")]
        elif filetype == "EPUB":
            types = [("EPUB files", "*.epub"), ("All files", "*.*")]
        else:
            types = [("All files", "*.*")]
        filename = filedialog.askopenfilename(title="Select Input File", filetypes=types)
        if filename:
            self.convert_input.set(filename)
            base, _ = os.path.splitext(filename)
            self.convert_output.set(base + ".pdf")

    def browse_convert_output(self):
        filename = filedialog.asksaveasfilename(title="Save PDF As", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if filename:
            self.convert_output.set(filename)

    def process_convert_to_pdf(self):
        filetype = self.convert_type.get()
        input_file = self.convert_input.get()
        output_file = self.convert_output.get()
        if not input_file or not output_file:
            messagebox.showerror("Error", "Please select input file and output PDF file.")
            return
        self.convert_log_text.insert(tk.END, f"Converting {input_file} to {output_file} as {filetype}\n")
        try:
            if filetype == "DOC/DOCX":
                doc_to_pdf(input_file, output_file)
            elif filetype == "XLS/XLSX":
                xls_to_pdf(input_file, output_file)
            elif filetype == "PPT/PPTX":
                ppt_to_pdf(input_file, output_file)
            elif filetype == "PNG":
                png_to_pdf(input_file, output_file)
            elif filetype == "JPG/JPEG":
                jpg_to_pdf(input_file, output_file)
            elif filetype == "EPUB":
                epub_to_pdf(input_file, output_file)
            self.convert_log_text.insert(tk.END, f"✅ Converted successfully: {output_file}\n")
            messagebox.showinfo("Success", f"Converted successfully: {output_file}")
        except Exception as e:
            self.convert_log_text.insert(tk.END, f"❌ Conversion error: {str(e)}\n")
            messagebox.showerror("Error", f"Conversion error: {str(e)}")

    def create_merge_vertical_frame(self, parent):
        frame = ttk.Frame(parent)
        # Input
        input_frame = ttk.LabelFrame(frame, text="Input", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(input_frame, text="PDF Input:").grid(row=0, column=0, sticky="w")
        pdf_input_entry = tk.Entry(input_frame, textvariable=self.pdf_input, width=60)
        pdf_input_entry.grid(row=0, column=1, sticky="we", padx=(5, 5))
        ttk.Button(input_frame, text="Browse", command=self.browse_pdf_input, style='Accent.TButton').grid(row=0, column=2)
        # Enable drag & drop
        if hasattr(pdf_input_entry, 'drop_target_register'):
            pdf_input_entry.drop_target_register(DND_FILES)  # type: ignore
        if hasattr(pdf_input_entry, 'dnd_bind'):
            pdf_input_entry.dnd_bind('<<Drop>>', self.on_pdf_input_drop)  # type: ignore
        # Output
        output_frame = ttk.LabelFrame(frame, text="Output", padding="10")
        output_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky="w")
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).grid(row=0, column=1, sticky="we", padx=(5, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir, style='Accent.TButton').grid(row=0, column=2)
        ttk.Button(frame, text="Merge 2 Vertical Pages", command=self.process_merge_landscape, style='Accent.TButton').pack(pady=10)
        self.merge_log_text = scrolledtext.ScrolledText(frame, height=8, width=80)
        self.merge_log_text.pack(fill="x", padx=10, pady=5)
        return frame

    def create_merge_pdfs_frame(self, parent):
        frame = ttk.Frame(parent)
        # Input
        input_frame = ttk.LabelFrame(frame, text="Input", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)
        self.mergepdf_input = tk.StringVar()
        ttk.Label(input_frame, text="PDF Files or Directory:").grid(row=0, column=0, sticky="w")
        pdf_input_entry = tk.Entry(input_frame, textvariable=self.mergepdf_input, width=60)
        pdf_input_entry.grid(row=0, column=1, sticky="we", padx=(5, 5))
        ttk.Button(input_frame, text="Browse", command=self.browse_mergepdf_input, style='Accent.TButton').grid(row=0, column=2)
        # Enable drag & drop
        if hasattr(pdf_input_entry, 'drop_target_register'):
            pdf_input_entry.drop_target_register(DND_FILES)  # type: ignore
        if hasattr(pdf_input_entry, 'dnd_bind'):
            pdf_input_entry.dnd_bind('<<Drop>>', self.on_mergepdf_input_drop)  # type: ignore
        # Tự động render preview khi input thay đổi
        self.mergepdf_input.trace_add('write', lambda *args: self.refresh_mergepdf_preview())
        # Preview area
        preview_frame = ttk.LabelFrame(frame, text="Preview & Order", padding="10")
        preview_frame.pack(fill="x", padx=10, pady=5)
        self.mergepdf_preview_frame = tk.Frame(preview_frame)
        self.mergepdf_preview_frame.pack(fill="x")
        btns_frame = ttk.Frame(preview_frame)
        btns_frame.pack(fill="x", pady=5)
        ttk.Button(btns_frame, text="Refresh Preview", command=self.refresh_mergepdf_preview, style='Accent.TButton').pack(side="left", padx=5)
        ttk.Button(btns_frame, text="Delete Selected", command=self.delete_selected_mergepdf_files, style='Accent.TButton').pack(side="left", padx=5)
        # Output
        output_frame = ttk.LabelFrame(frame, text="Output", padding="10")
        output_frame.pack(fill="x", padx=10, pady=5)
        self.mergepdf_output = tk.StringVar()
        ttk.Label(output_frame, text="Output PDF:").grid(row=0, column=0, sticky="w")
        ttk.Entry(output_frame, textvariable=self.mergepdf_output, width=50).grid(row=0, column=1, sticky="we", padx=(5, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_mergepdf_output, style='Accent.TButton').grid(row=0, column=2)
        # Process button
        ttk.Button(frame, text="Merge PDFs", command=self.process_merge_pdfs, style='Accent.TButton').pack(pady=10)
        # Log
        self.mergepdf_log_text = scrolledtext.ScrolledText(frame, height=8, width=80)
        self.mergepdf_log_text.pack(fill="x", padx=10, pady=5)
        # State for preview
        self.mergepdf_files = []  # List of dict: {path, selected, thumbnails}
        self.mergepdf_thumbnails = []  # List of PhotoImage objects to keep refs
        self.drag_data = {"widget": None, "start_idx": None, "dragging": False}
        self.last_selected_idx = None
        self.refresh_mergepdf_preview()
        return frame

    def create_compress_pdf_frame(self, parent):
        frame = ttk.Frame(parent)
        # Input
        input_frame = ttk.LabelFrame(frame, text="Input", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)
        self.compress_input = tk.StringVar()
        ttk.Label(input_frame, text="PDF File:").grid(row=0, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.compress_input, width=60).grid(row=0, column=1, sticky="we", padx=(5, 5))
        ttk.Button(input_frame, text="Browse", command=self.browse_compress_input, style='Accent.TButton').grid(row=0, column=2)
        # Output
        output_frame = ttk.LabelFrame(frame, text="Output", padding="10")
        output_frame.pack(fill="x", padx=10, pady=5)
        self.compress_output = tk.StringVar()
        ttk.Label(output_frame, text="Output PDF:").grid(row=0, column=0, sticky="w")
        ttk.Entry(output_frame, textvariable=self.compress_output, width=50).grid(row=0, column=1, sticky="we", padx=(5, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_compress_output, style='Accent.TButton').grid(row=0, column=2)
        # Mode
        mode_frame = ttk.LabelFrame(frame, text="Compression Level", padding="10")
        mode_frame.pack(fill="x", padx=10, pady=5)
        self.compress_mode = tk.StringVar(value="medium")
        ttk.Radiobutton(mode_frame, text="Low (High Quality)", variable=self.compress_mode, value="low", style='Switch.TCheckbutton').pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="Medium (Balanced)", variable=self.compress_mode, value="medium", style='Switch.TCheckbutton').pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="High (Strong Compression)", variable=self.compress_mode, value="high", style='Switch.TCheckbutton').pack(side="left", padx=5)
        # Process button
        ttk.Button(frame, text="Compress PDF", command=self.process_compress_pdf, style='Accent.TButton').pack(pady=10)
        # Log
        self.compress_log_text = scrolledtext.ScrolledText(frame, height=8, width=80)
        self.compress_log_text.pack(fill="x", padx=10, pady=5)
        return frame

    def process_scribd_bypass(self):
        mode = self.scribd_mode.get()
        output_dir = self.output_dir.get() or "scribd_output"
        if mode == "single":
            input_file = self.pdf_input.get()
            self.scribd_log_text.insert(tk.END, f"Bypassing Scribd: {input_file}\n")
            bypass = ScribdBypass(output_dir)
            result = bypass.create_scribd_file(input_file, file_type="document")
            if result:
                self.scribd_log_text.insert(tk.END, f"✅ Scribd file created: {result}\n")
            else:
                self.scribd_log_text.insert(tk.END, "❌ Scribd processing failed\n")
        else:
            input_dir = self.pdf_input.get()
            self.scribd_log_text.insert(tk.END, f"Batch Scribd from: {input_dir}\n")
            bypass = ScribdBypass(output_dir)
            pdf_files = list(Path(input_dir).glob("*.pdf"))
            results = []
            for i, pdf in enumerate(pdf_files, 1):
                self.scribd_log_text.insert(tk.END, f"Scribd: Processing {pdf.name} ({i}/{len(pdf_files)})\n")
                result = bypass.create_scribd_file(str(pdf), file_type="document")
                if result:
                    results.append(result)
            self.scribd_log_text.insert(tk.END, f"Batch Scribd completed: {len(results)}/{len(pdf_files)} successful\n")

    def process_merge_landscape(self):
        mode = self.merge_landscape_mode.get()
        output_dir = self.output_dir.get() or "output"
        if mode == "single":
            input_pdf = self.merge_input_file.get()
            if not input_pdf:
                messagebox.showerror("Error", "Please select an input PDF file")
                return
            base, ext = os.path.splitext(input_pdf)
            output_pdf = base + "_2in1.pdf"
            self.merge_log_text.insert(tk.END, f"Merging: {input_pdf} -> {output_pdf}\n")
            try:
                merge_pdf_vertical_to_horizontal(input_pdf, output_pdf)
                self.merge_log_text.insert(tk.END, f"✅ Merged: {output_pdf}\n")
                messagebox.showinfo("Success", f"Merged: {output_pdf}")
            except Exception as e:
                self.merge_log_text.insert(tk.END, f"❌ Merge error: {str(e)}\n")
                messagebox.showerror("Error", f"Merge error: {str(e)}")
        else:
            input_dir = self.merge_input_dir.get()
            self.merge_log_text.insert(tk.END, f"Batch merge from: {input_dir}\n")
            pdf_files = list(Path(input_dir).glob("*.pdf"))
            results = []
            for i, pdf in enumerate(pdf_files, 1):
                base, ext = os.path.splitext(str(pdf))
                output_pdf = base + "_2in1.pdf"
                self.merge_log_text.insert(tk.END, f"Merging: {pdf} -> {output_pdf}\n")
                try:
                    merge_pdf_vertical_to_horizontal(str(pdf), output_pdf)
                    results.append(output_pdf)
                except Exception as e:
                    self.merge_log_text.insert(tk.END, f"❌ Merge error for {pdf}: {str(e)}\n")
            self.merge_log_text.insert(tk.END, f"Batch merge completed: {len(results)}/{len(pdf_files)} successful\n")

    def on_pdf_input_drop(self, event):
        # event.data có thể là 1 hoặc nhiều file, cách nhau bởi dấu cách hoặc ;
        paths = self.root.tk.splitlist(event.data)
        # Nếu chỉ 1 file/thư mục thì set luôn, nhiều file thì nối bằng ;
        if len(paths) == 1:
            self.pdf_input.set(paths[0])
        else:
            self.pdf_input.set(';'.join(paths))

    def browse_pdf_input(self):
        # Cho phép chọn nhiều file hoặc 1 thư mục
        files = filedialog.askopenfilenames(title="Select PDF File(s)", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if files:
            if len(files) == 1:
                self.pdf_input.set(files[0])
            else:
                self.pdf_input.set(';'.join(files))
        else:
            directory = filedialog.askdirectory(title="Select PDF Directory")
            if directory:
                self.pdf_input.set(directory)
    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
    def browse_epub_file(self):
        filename = filedialog.askopenfilename(title="Select EPUB File", filetypes=[("EPUB files", "*.epub"), ("All files", "*.*")])
        if filename:
            self.epub_file.set(filename)
            base, _ = os.path.splitext(filename)
            self.epub_pdf_output.set(base + ".pdf")
    def browse_epub_pdf_output(self):
        filename = filedialog.asksaveasfilename(title="Save PDF As", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if filename:
            self.epub_pdf_output.set(filename)
    def browse_merge_input_file(self):
        filename = filedialog.askopenfilename(title="Select PDF File to Merge", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if filename:
            self.merge_input_file.set(filename)
    def browse_merge_input_dir(self):
        directory = filedialog.askdirectory(title="Select PDF Directory to Merge")
        if directory:
            self.merge_input_dir.set(directory)

    def on_mergepdf_input_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        if len(paths) == 1:
            self.mergepdf_input.set(paths[0])
        else:
            self.mergepdf_input.set(';'.join(paths))

    def browse_mergepdf_input(self):
        files = filedialog.askopenfilenames(title="Select PDF File(s)", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if files:
            if len(files) == 1:
                self.mergepdf_input.set(files[0])
            else:
                self.mergepdf_input.set(';'.join(files))
        else:
            directory = filedialog.askdirectory(title="Select PDF Directory")
            if directory:
                self.mergepdf_input.set(directory)

    def browse_mergepdf_output(self):
        filename = filedialog.asksaveasfilename(title="Save Merged PDF As", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if filename:
            self.mergepdf_output.set(filename)

    def refresh_mergepdf_preview(self):
        for widget in self.mergepdf_preview_frame.winfo_children():
            widget.destroy()
        self.mergepdf_thumbnails = []
        # Get file list
        input_val = self.mergepdf_input.get()
        if os.path.isdir(input_val):
            pdf_files = sorted(str(p) for p in Path(input_val).glob("*.pdf"))
        else:
            pdf_files = [f.strip() for f in input_val.split(';') if f.strip()]
        # Build file dicts
        old_files = getattr(self, 'mergepdf_files', [])
        old_selected = {f['path']: f.get('selected', False) for f in old_files if isinstance(f, dict)}
        self.mergepdf_files = []
        for pdf in pdf_files:
            thumbs = self.get_pdf_thumbnails(pdf, num_pages=5)
            self.mergepdf_thumbnails.append(thumbs)
            self.mergepdf_files.append({'path': pdf, 'selected': old_selected.get(pdf, False), 'thumbnails': thumbs})
        # Show thumbnails
        for idx, fileinfo in enumerate(self.mergepdf_files):
            thumb_frame = tk.Frame(self.mergepdf_preview_frame, bd=3, relief="groove", bg="#bfefff" if fileinfo['selected'] else "#f0f0f0")
            thumb_frame.grid(row=0, column=idx, padx=5, pady=5)
            # Show up to 5 thumbnails horizontally
            for i, thumb in enumerate(fileinfo['thumbnails']):
                lbl = tk.Label(thumb_frame, image=thumb, bd=1, relief="solid")
                lbl.grid(row=0, column=i, padx=1)
            name_lbl = tk.Label(thumb_frame, text=os.path.basename(fileinfo['path']), wraplength=100, bg=thumb_frame['bg'])
            name_lbl.grid(row=1, column=0, columnspan=5)
            del_btn = tk.Button(thumb_frame, text="Delete", command=lambda i=idx: self.delete_mergepdf_file(i))
            del_btn.grid(row=2, column=0, columnspan=5, pady=2)
            # Select/multi-select events
            thumb_frame.bind("<Button-1>", lambda e, i=idx: self.toggle_select_mergepdf(i, e))
            thumb_frame.bind("<Control-Button-1>", lambda e, i=idx: self.ctrl_select_mergepdf(i, e))
            thumb_frame.bind("<Shift-Button-1>", lambda e, i=idx: self.shift_select_mergepdf(i, e))
            # Drag & drop events (chuột trái)
            thumb_frame.bind("<ButtonPress-1>", lambda e, i=idx: self.start_drag_mergepdf(i, e))
            thumb_frame.bind("<B1-Motion>", self.on_drag_mergepdf)
            thumb_frame.bind("<ButtonRelease-1>", self.on_drop_mergepdf)

    def get_pdf_thumbnails(self, pdf_path, num_pages=5):
        thumbs = []
        try:
            images = convert_from_path(pdf_path, first_page=1, last_page=num_pages, size=(60, 80))
            for img in images:
                thumbs.append(ImageTk.PhotoImage(img))
        except Exception:
            img = Image.new("RGB", (60, 80), color="gray")
            thumbs.append(ImageTk.PhotoImage(img))
        return thumbs

    def toggle_select_mergepdf(self, idx, event):
        # Single click: select only this
        for i, f in enumerate(self.mergepdf_files):
            f['selected'] = (i == idx)
        self.last_selected_idx = idx
        self.refresh_mergepdf_preview()

    def ctrl_select_mergepdf(self, idx, event):
        # Ctrl+click: toggle selection
        self.mergepdf_files[idx]['selected'] = not self.mergepdf_files[idx]['selected']
        self.last_selected_idx = idx
        self.refresh_mergepdf_preview()

    def shift_select_mergepdf(self, idx, event):
        # Shift+click: select range
        if self.last_selected_idx is None:
            self.toggle_select_mergepdf(idx, event)
            return
        start = min(self.last_selected_idx, idx)
        end = max(self.last_selected_idx, idx)
        for i in range(len(self.mergepdf_files)):
            self.mergepdf_files[i]['selected'] = (start <= i <= end)
        self.refresh_mergepdf_preview()

    def delete_mergepdf_file(self, idx):
        del self.mergepdf_files[idx]
        self.mergepdf_input.set(';'.join(f['path'] for f in self.mergepdf_files))
        self.refresh_mergepdf_preview()

    def delete_selected_mergepdf_files(self):
        self.mergepdf_files = [f for f in self.mergepdf_files if not f['selected']]
        self.mergepdf_input.set(';'.join(f['path'] for f in self.mergepdf_files))
        self.refresh_mergepdf_preview()

    def start_drag_mergepdf(self, idx, event):
        self.drag_data = {"widget": event.widget, "start_idx": idx, "dragging": True}
        # Highlight dragging
        for i, child in enumerate(self.mergepdf_preview_frame.winfo_children()):
            try:
                if i == idx:
                    child.config(bg="#00bfff")  # type: ignore
                else:
                    child.config(bg="#e0e0e0")  # type: ignore
            except Exception:
                pass

    def on_drag_mergepdf(self, event):
        # Hiển thị vị trí drop
        x = event.x_root - self.mergepdf_preview_frame.winfo_rootx()
        col_width = 120
        drop_idx = min(max(int(x // col_width), 0), len(self.mergepdf_files)-1)
        for i, child in enumerate(self.mergepdf_preview_frame.winfo_children()):
            try:
                if i == drop_idx:
                    child.config(highlightbackground="#ff6600", highlightthickness=3)  # type: ignore
                else:
                    child.config(highlightthickness=0)  # type: ignore
            except Exception:
                pass

    def on_drop_mergepdf(self, event):
        if not self.drag_data.get("dragging"):
            return
        x = event.x_root - self.mergepdf_preview_frame.winfo_rootx()
        col_width = 120
        drop_idx = min(max(int(x // col_width), 0), len(self.mergepdf_files)-1)
        start_idx = self.drag_data.get("start_idx")
        if start_idx is not None and drop_idx != start_idx:
            file = self.mergepdf_files.pop(int(start_idx))
            self.mergepdf_files.insert(int(drop_idx), file)
            self.mergepdf_input.set(';'.join(f['path'] for f in self.mergepdf_files))
            self.refresh_mergepdf_preview()
        # Reset highlight
        for child in self.mergepdf_preview_frame.winfo_children():
            try:
                child.config(bg="#f0f0f0", highlightthickness=0)  # type: ignore
            except Exception:
                pass
        self.drag_data = {"widget": None, "start_idx": None, "dragging": False}

    def process_merge_pdfs(self):
        output_pdf = self.mergepdf_output.get()
        pdf_files = [f['path'] for f in self.mergepdf_files]
        if not pdf_files:
            messagebox.showerror("Error", "Please select input PDF files or directory.")
            return
        # Nếu chưa nhập output, tự động tạo tên
        if not output_pdf:
            if os.path.isdir(self.mergepdf_input.get()):
                out_dir = self.mergepdf_input.get()
            else:
                out_dir = os.path.dirname(pdf_files[0]) if pdf_files else os.getcwd()
            output_pdf = os.path.join(out_dir, "merged_output.pdf")
            self.mergepdf_output.set(output_pdf)
        self.mergepdf_log_text.insert(tk.END, f"Merging {len(pdf_files)} files into {output_pdf}\n")
        try:
            merge_pdfs(pdf_files, output_pdf)
            self.mergepdf_log_text.insert(tk.END, f"✅ Merged successfully: {output_pdf}\n")
            messagebox.showinfo("Success", f"Merged successfully: {output_pdf}")
        except Exception as e:
            self.mergepdf_log_text.insert(tk.END, f"❌ Merge error: {str(e)}\n")
            messagebox.showerror("Error", f"Merge error: {str(e)}")

    def browse_compress_input(self):
        filename = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if filename:
            self.compress_input.set(filename)
            base, _ = os.path.splitext(filename)
            self.compress_output.set(base + "_compressed.pdf")

    def browse_compress_output(self):
        filename = filedialog.asksaveasfilename(title="Save Compressed PDF As", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if filename:
            self.compress_output.set(filename)

    def process_compress_pdf(self):
        input_pdf = self.compress_input.get()
        output_pdf = self.compress_output.get()
        mode = self.compress_mode.get()
        if not input_pdf or not output_pdf:
            messagebox.showerror("Error", "Please select input and output PDF file.")
            return
        self.compress_log_text.insert(tk.END, f"Compressing {input_pdf} to {output_pdf} (mode: {mode})\n")
        try:
            compress_pdf(input_pdf, output_pdf, mode)
            self.compress_log_text.insert(tk.END, f"✅ Compressed successfully: {output_pdf}\n")
            messagebox.showinfo("Success", f"Compressed successfully: {output_pdf}")
        except Exception as e:
            self.compress_log_text.insert(tk.END, f"❌ Compression error: {str(e)}\n")
            messagebox.showerror("Error", f"Compression error: {str(e)}")


def main():
    """Main function"""
    root = TkinterDnD.Tk()
    
    # Load Azure theme và đặt dark mode
    import os
    try:
        # Get the absolute path to the azure.tcl file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        theme_path = os.path.join(script_dir, "azure.tcl")
        
        # Source the theme file
        root.tk.call("source", theme_path)
        
        # Set the theme
        style = ttk.Style(root)
        style.theme_use("azure-light")  # Use azure-light theme directly
        root.tk.call("set_theme", "light")
        # Custom button style: grey background, white text
        style.configure('Accent.TButton', background='#888888', foreground='white', font=('Segoe UI', 10, 'bold'))
        style.map('Accent.TButton', background=[('active', '#666666')])
        style.configure('TButton', background='#888888', foreground='white', font=('Segoe UI', 10))
        style.map('TButton', background=[('active', '#666666')])
        
    except Exception as e:
        print(f"Warning: Could not load Azure theme: {e}")
        print("Using default theme instead.")
        # Fallback to default theme
        style = ttk.Style(root)
        style.theme_use("clam")  # Use a built-in theme as fallback
    
    app = PDFUtilityToolkitGUI(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (config.WINDOW_WIDTH // 2)
    y = (root.winfo_screenheight() // 2) - (config.WINDOW_HEIGHT // 2)
    root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main() 