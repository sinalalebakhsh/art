# utils.py
import os
import re
import datetime
import tkinter as tk
from tkinter import scrolledtext  # این خط اضافه شود
from tkinter import messagebox
from config import Config

class FileUtils:
    """ابزارهای مربوط به فایل و نام فایل"""
    
    @staticmethod
    def sanitize_filename(text):
        """پاکسازی متن برای استفاده در نام فایل"""
        if not text or not isinstance(text, str):
            return "بدون_موضوع"
        
        # حذف کاراکترهای غیرمجاز
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        # جایگزینی فاصله با آندرلاین
        text = text.replace(' ', '_')
        # حذف آندرلاین‌های تکراری
        text = re.sub(r'_+', '_', text)
        # حذف آندرلاین از ابتدا و انتها
        text = text.strip('_')
        # کوتاه کردن اگر خیلی طولانی باشد
        if len(text) > 50:
            text = text[:50]
        
        return text if text else "بدون_موضوع"
    
    @staticmethod
    def generate_user_filename(topic):
        """تولید نام فایل برای بایگانی کاربر"""
        now = datetime.datetime.now()
        date_part = now.strftime("%Y-%m-%d_%H-%M")
        sanitized_topic = FileUtils.sanitize_filename(topic)
        filename = f"chat_{date_part}_{sanitized_topic}.txt"
        return os.path.join(Config.get_archive_folder(), filename)
    
    @staticmethod
    def save_message_to_file(filename, message):
        """ذخیره پیام در فایل"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(filename, "a", encoding="utf-8") as file:
                file.write(f"[{timestamp}] {message}\n")
            return True
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره فایل: {e}")
            return False
    
    @staticmethod
    def read_file_content(filename):
        """خواندن محتوای فایل"""
        try:
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as file:
                    return file.read()
            return None
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در خواندن فایل: {e}")
            return None

class GUIUtils:
    """ابزارهای مربوط به رابط کاربری"""
    
    @staticmethod
    def create_scrolled_text(parent, width, height, font_size=10):
        """ایجاد جعبه متنی با قابلیت اسکرول"""
        return scrolledtext.ScrolledText(  # این خط تغییر کرد
            parent,
            wrap=tk.WORD,
            width=width,
            height=height,
            font=(Config.FONT_FAMILY, font_size),
            bg="#f8f9fa"
        )
    
    @staticmethod
    def create_button(parent, text, command, bg_color, fg_color="white", width=None):
        """ایجاد دکمه با استایل یکسان"""
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=(Config.FONT_FAMILY, 10),
            bg=bg_color,
            fg=fg_color,
            width=width,
            relief=tk.RAISED,
            bd=2
        )
        return button
    
    @staticmethod
    def create_entry(parent, font_size=12, width=50):
        """ایجاد فیلد ورودی"""
        return tk.Entry(
            parent,
            font=(Config.FONT_FAMILY, font_size),
            width=width,
            relief=tk.SUNKEN,
            bd=2
        )
    
    @staticmethod
    def create_label(parent, text, font_size=10, **kwargs):
        """ایجاد برچسب"""
        return tk.Label(
            parent,
            text=text,
            font=(Config.FONT_FAMILY, font_size),
            **kwargs
        )

class ArchiveViewer:
    """کلاس برای نمایش محتوای بایگانی"""
    
    def __init__(self, parent, filename, title="بایگانی"):
        self.parent = parent
        self.filename = filename
        self.title = title
        self.create_window()
    
    def create_window(self):
        """ایجاد پنجره نمایش بایگانی"""
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"{self.title} - {os.path.basename(self.filename)}")
        self.window.geometry("900x700")
        
        self.create_widgets()
        self.load_content()
    
    def create_widgets(self):
        """ایجاد ویجت‌های پنجره"""
        # فریم برای اطلاعات فایل
        info_frame = tk.Frame(self.window)
        info_frame.pack(padx=10, pady=5, fill=tk.X)
        
        GUIUtils.create_label(info_frame, f"فایل: {self.filename}", 9).pack(anchor=tk.W)
        
        # جعبه متنی برای نمایش محتوا
        self.text_widget = GUIUtils.create_scrolled_text(self.window, 100, 35)
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def load_content(self):
        """بارگذاری محتوای فایل"""
        content = FileUtils.read_file_content(self.filename)
        if content:
            self.text_widget.insert(tk.END, content)
        self.text_widget.config(state=tk.DISABLED)