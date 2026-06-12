import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import os
import subprocess

class ImageCompressor:
    def __init__(self, root):
        self.root = root
        self.root.title("图片压缩工具")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.selected_files = []
        self.output_folder = ""
        self.quality = tk.IntVar(value=80)
        self.max_width = tk.IntVar(value=1920)

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="图片压缩工具", font=("Arial", 16, "bold")).pack(pady=(0, 20))

        select_frame = ttk.Frame(main_frame)
        select_frame.pack(fill=tk.X, pady=(0, 15))
        self.select_btn = ttk.Button(select_frame, text="选择图片", command=self.select_images)
        self.select_btn.pack(side=tk.LEFT)
        self.file_label = ttk.Label(select_frame, text="未选择图片")
        self.file_label.pack(side=tk.LEFT, padx=(10, 0))

        quality_frame = ttk.Frame(main_frame)
        quality_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(quality_frame, text="压缩质量:").pack(side=tk.LEFT)
        ttk.Scale(quality_frame, from_=1, to=100, variable=self.quality, orient=tk.HORIZONTAL, length=300).pack(side=tk.LEFT, padx=(10, 10))
        self.quality_entry = ttk.Entry(quality_frame, textvariable=self.quality, width=5)
        self.quality_entry.pack(side=tk.LEFT)
        ttk.Label(quality_frame, text="%").pack(side=tk.LEFT)

        width_frame = ttk.Frame(main_frame)
        width_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(width_frame, text="最大宽度:").pack(side=tk.LEFT)
        ttk.Scale(width_frame, from_=100, to=4096, variable=self.max_width, orient=tk.HORIZONTAL, length=300).pack(side=tk.LEFT, padx=(10, 10))
        self.width_entry = ttk.Entry(width_frame, textvariable=self.max_width, width=6)
        self.width_entry.pack(side=tk.LEFT)
        ttk.Label(width_frame, text="像素").pack(side=tk.LEFT)

        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(output_frame, text="输出文件夹:").pack(side=tk.LEFT)
        self.output_entry = ttk.Entry(output_frame, state="readonly", width=40)
        self.output_entry.pack(side=tk.LEFT, padx=(10, 10))
        ttk.Button(output_frame, text="选择", command=self.select_output_folder).pack(side=tk.LEFT)

        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 15))

        self.info_text = tk.Text(main_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(fill=tk.X, pady=(0, 15))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        self.compress_btn = ttk.Button(button_frame, text="开始压缩", command=self.start_compress, state=tk.DISABLED)
        self.compress_btn.pack(side=tk.LEFT)
        ttk.Button(button_frame, text="清空", command=self.clear_all).pack(side=tk.RIGHT)

    def select_images(self):
        files = filedialog.askopenfilenames(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.webp"), ("JPG", "*.jpg;*.jpeg"), ("PNG", "*.png"), ("WebP", "*.webp")]
        )
        if files:
            self.selected_files = list(files)
            file_count = len(self.selected_files)
            self.file_label.config(text=f"已选择 {file_count} 张图片")
            self.check_ready()

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="选择输出文件夹")
        if folder:
            self.output_folder = folder
            self.output_entry.config(state=tk.NORMAL)
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)
            self.output_entry.config(state=tk.DISABLED)
            self.check_ready()

    def check_ready(self):
        if self.selected_files and self.output_folder:
            self.compress_btn.config(state=tk.NORMAL)
        else:
            self.compress_btn.config(state=tk.DISABLED)

    def clear_all(self):
        self.selected_files = []
        self.output_folder = ""
        self.file_label.config(text="未选择图片")
        self.output_entry.config(state=tk.NORMAL)
        self.output_entry.delete(0, tk.END)
        self.output_entry.config(state=tk.DISABLED)
        self.compress_btn.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)

    def append_info(self, text):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, text + "\n")
        self.info_text.see(tk.END)
        self.info_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def compress_image(self, input_path, output_path, quality, max_width):
        try:
            with Image.open(input_path) as img:
                original_size = os.path.getsize(input_path)

                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background

                width, height = img.size
                if width > max_width:
                    ratio = max_width / width
                    new_height = int(height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

                img.save(output_path, quality=quality)
                compressed_size = os.path.getsize(output_path)

                return original_size, compressed_size
        except Exception as e:
            return None, str(e)

    def start_compress(self):
        if not self.selected_files or not self.output_folder:
            return

        quality = self.quality.get()
        max_width = self.max_width.get()

        total_original = 0
        total_compressed = 0
        success_count = 0
        fail_count = 0

        self.progress_bar['maximum'] = len(self.selected_files)
        self.progress_bar['value'] = 0

        self.append_info("开始压缩...")

        for i, input_path in enumerate(self.selected_files):
            filename = os.path.basename(input_path)
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_compressed{ext.lower()}"
            output_path = os.path.join(self.output_folder, output_filename)

            original_size, compressed_size = self.compress_image(input_path, output_path, quality, max_width)

            if original_size is None:
                self.append_info(f"❌ {filename}: {compressed_size}")
                fail_count += 1
            else:
                total_original += original_size
                total_compressed += compressed_size
                percentage = (1 - compressed_size / original_size) * 100
                self.append_info(f"✓ {filename}: {self.format_size(original_size)} → {self.format_size(compressed_size)} (-{percentage:.1f}%)")
                success_count += 1

            self.progress_bar['value'] = i + 1
            self.root.update_idletasks()

        self.append_info("")
        self.append_info(f"压缩完成！成功: {success_count}, 失败: {fail_count}")
        if total_original > 0:
            total_percentage = (1 - total_compressed / total_original) * 100
            self.append_info(f"总计: {self.format_size(total_original)} → {self.format_size(total_compressed)} (-{total_percentage:.1f}%)")

        messagebox.showinfo("完成", "压缩完成！")

        try:
            if os.name == 'nt':
                subprocess.run(['explorer', self.output_folder], check=True)
            else:
                subprocess.run(['open', self.output_folder], check=True)
        except Exception:
            pass

    def format_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCompressor(root)
    root.mainloop()