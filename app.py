# app.py
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import os
import datetime
from config import Config
from utils import FileUtils, GUIUtils, ArchiveViewer
from auto_responder import AutoResponder

# در app.py به این صورت استفاده کنید
from search import search_and_save

# در متد send_message اضافه کنید:
def send_message(self, event=None):
    message = self.user_input.get().strip()
    if message:
        # نمایش پیام کاربر
        self.display_message(f"شما: {message}", "user")
        
        # ذخیره پیام کاربر
        user_filename, _ = self.get_current_filenames()
        FileUtils.save_message_to_file(user_filename, f"کاربر: {message}")
        
        # جستجوی خودکار در اینترنت
        search_results = search_and_save(message, max_results=3)
        
        # تولید پاسخ بر اساس نتایج جستجو
        if search_results:
            bot_response = f"من درباره '{message}' جستجو کردم. {len(search_results)} نتیجه پیدا شد."
        else:
            bot_response = f"متأسفم، نتوانستم اطلاعاتی درباره '{message}' پیدا کنم."
        
        self.display_message(f"ربات: {bot_response}", "bot")
        
        # پاک کردن فیلد ورودی
        self.user_input.delete(0, tk.END)

       
class ChatApplication:
    def __init__(self, root):
        self.root = root
        self.root.title(Config.APP_NAME)
        self.root.geometry("850x700")
        
        self.setup_ui()
        
    def setup_ui(self):
        """تنظیم رابط کاربری"""
        self.create_session_frame()
        self.create_chat_display()
        self.create_input_frame()
        self.create_multi_line_input_button()
        self.create_control_buttons()
        
        # به روز رسانی نمایش نام فایل
        self.update_filename_display()
        self.chat_topic.bind("<KeyRelease>", self.on_topic_change)
    
    def create_session_frame(self):
        """ایجاد فریم برای اطلاعات جلسه"""
        session_frame = tk.Frame(self.root, relief=tk.GROOVE, bd=2, bg="#e9ecef")
        session_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Label(session_frame, text="موضوع جلسه/چت:", 
                font=("Arial", 10, "bold"), bg="#e9ecef").pack(side=tk.LEFT, padx=5)
        
        self.chat_topic = tk.Entry(
            session_frame,
            font=("Arial", 11),
            width=40,
            relief=tk.SUNKEN,
            bd=2
        )
        self.chat_topic.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.chat_topic.insert(0, "جلسه_عمومی")
        
        # نمایش نام فایل پیش‌بینی شده
        self.filename_label = tk.Label(
            session_frame,
            text="",
            font=("Arial", 8),
            bg="#e9ecef",
            fg="blue",
            wraplength=400
        )
        self.filename_label.pack(side=tk.LEFT, padx=10)
    
    def create_chat_display(self):
        """ایجاد ناحیه نمایش گفتگو"""
        self.chat_display = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            width=85,
            height=20,
            font=("Arial", 10),
            bg="#f8f9fa"
        )
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
    
    def create_input_frame(self):
        """ایجاد فریم برای ورودی و دکمه ارسال"""
        input_frame = tk.Frame(self.root)
        input_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.user_input = tk.Entry(
            input_frame,
            font=("Arial", 12),
            width=50,
            relief=tk.SUNKEN,
            bd=2
        )
        self.user_input.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        self.user_input.bind("<Return>", self.send_message)
        
        self.send_button = tk.Button(
            input_frame,
            text="ارسال",
            command=self.send_message,
            font=("Arial", 10, "bold"),
            bg="#4CAF50",
            fg="white",
            width=8,
            relief=tk.RAISED,
            bd=2
        )
        self.send_button.pack(side=tk.RIGHT)
    
    def create_multi_line_input_button(self):
        """ایجاد دکمه برای ورودی چندخطی"""
        multi_line_frame = tk.Frame(self.root)
        multi_line_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.multi_line_button = tk.Button(
            multi_line_frame,
            text="📝 نوشتن پیام چندخطی",
            command=self.open_multi_line_input,
            font=("Arial", 10),
            bg="#FF9800",
            fg="white",
            width=20,
            relief=tk.RAISED,
            bd=2
        )
        self.multi_line_button.pack()
    
    def create_control_buttons(self):
        """ایجاد دکمه‌های کنترلی"""
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)
        
        self.clear_button = tk.Button(
            button_frame,
            text="پاک کردن چت",
            command=self.clear_chat,
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            width=15,
            relief=tk.RAISED,
            bd=2
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.view_archive_button = tk.Button(
            button_frame,
            text="مشاهده بایگانی کاربر",
            command=self.view_user_archive,
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
            width=18,
            relief=tk.RAISED,
            bd=2
        )
        self.view_archive_button.pack(side=tk.LEFT, padx=5)
        
        self.view_response_button = tk.Button(
            button_frame,
            text="مشاهده بایگانی پاسخ",
            command=self.view_response_archive,
            font=("Arial", 10),
            bg="#9C27B0",
            fg="white",
            width=18,
            relief=tk.RAISED,
            bd=2
        )
        self.view_response_button.pack(side=tk.LEFT, padx=5)
        
        self.open_folder_button = tk.Button(
            button_frame,
            text="بازکردن پوشه‌ها",
            command=self.open_folders,
            font=("Arial", 10),
            bg="#607D8B",
            fg="white",
            width=15,
            relief=tk.RAISED,
            bd=2
        )
        self.open_folder_button.pack(side=tk.LEFT, padx=5)
    
    def open_multi_line_input(self):
        """باز کردن پنجره ورودی چندخطی"""
        MultiLineInputWindow(self.root, self.process_multi_line_message)
    
    def process_multi_line_message(self, message):
        """پردازش پیام چندخطی"""
        if message.strip():
            # نمایش پیام کاربر در چت
            self.display_message(f"شما: {message}", "user")
            
            # ذخیره پیام کاربر در فایل
            user_filename, _ = self.get_current_filenames()
            FileUtils.save_message_to_file(user_filename, f"کاربر: {message}")
            
            # تولید و نمایش پاسخ خودکار
            topic = self.chat_topic.get().strip()
            bot_response = AutoResponder.process_message(message, topic)
            self.display_message(f"ربات: {bot_response}", "bot")
    
    def on_topic_change(self, event=None):
        """هنگام تغییر موضوع"""
        self.update_filename_display()
    
    def update_filename_display(self):
        """به روز رسانی نمایش نام فایل"""
        topic = self.chat_topic.get().strip()
        user_filename = FileUtils.generate_user_filename(topic)
        response_filename = AutoResponder.generate_response_filename(topic)
        
        display_text = f"کاربر: {os.path.basename(user_filename)}\nپاسخ: {os.path.basename(response_filename)}"
        self.filename_label.config(text=display_text)
    
    def get_current_filenames(self):
        """دریافت نام فایل‌های جاری"""
        topic = self.chat_topic.get().strip()
        user_filename = FileUtils.generate_user_filename(topic)
        response_filename = AutoResponder.generate_response_filename(topic)
        return user_filename, response_filename
    
    def send_message(self, event=None):
        """ارسال پیام"""
        message = self.user_input.get().strip()
        if message:
            # نمایش پیام کاربر در چت
            self.display_message(f"شما: {message}", "user")
            
            # ذخیره پیام کاربر در فایل
            user_filename, _ = self.get_current_filenames()
            FileUtils.save_message_to_file(user_filename, f"کاربر: {message}")
            
            # تولید و نمایش پاسخ خودکار
            topic = self.chat_topic.get().strip()
            bot_response = AutoResponder.process_message(message, topic)
            self.display_message(f"ربات: {bot_response}", "bot")
            
            # پاک کردن فیلد ورودی
            self.user_input.delete(0, tk.END)
    
    def display_message(self, message, sender_type):
        """نمایش پیام در چت"""
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        formatted_message = f"[{timestamp}] {message}\n"
        self.chat_display.insert(tk.END, formatted_message)
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def clear_chat(self):
        """پاک کردن محتوای چت"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def view_user_archive(self):
        """نمایش بایگانی کاربر"""
        user_filename, _ = self.get_current_filenames()
        if os.path.exists(user_filename):
            ArchiveViewer(self.root, user_filename, "بایگانی کاربر")
        else:
            messagebox.showinfo("اطلاعات", "هنوز بایگانی برای این موضوع وجود ندارد.")
    
    def view_response_archive(self):
        """نمایش بایگانی پاسخ‌ها"""
        _, response_filename = self.get_current_filenames()
        if os.path.exists(response_filename):
            ArchiveViewer(self.root, response_filename, "بایگانی پاسخ‌ها")
        else:
            messagebox.showinfo("اطلاعات", "هنوز پاسخ‌های بایگانی شده وجود ندارد.")
    
    def open_folders(self):
        """باز کردن پوشه‌های بایگانی"""
        folders = [Config.ARCHIVE_FOLDER, Config.RESPONSE_FOLDER]
        
        for folder in folders:
            try:
                if os.path.exists(folder):
                    os.startfile(folder)
                else:
                    os.makedirs(folder)
                    os.startfile(folder)
            except:
                try:
                    import subprocess
                    subprocess.Popen(['xdg-open', folder])
                except:
                    try:
                        import subprocess
                        subprocess.Popen(['open', folder])
                    except:
                        messagebox.showinfo("اطلاعات", f"پوشه: {os.path.abspath(folder)}")

class MultiLineInputWindow:
    """پنجره برای ورودی چندخطی"""
    
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.create_window()
    
    def create_window(self):
        """ایجاد پنجره ورودی چندخطی"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("نوشتن پیام چندخطی")
        self.window.geometry("600x400")
        self.window.resizable(True, True)
        
        self.create_widgets()
        
        # فوکوس روی پنجره
        self.window.focus_set()
        self.window.grab_set()
    
    def create_widgets(self):
        """ایجاد ویجت‌های پنجره"""
        # برچسب راهنما
        label_frame = tk.Frame(self.window)
        label_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Label(
            label_frame,
            text="پیام خود را در زیر بنویسید (از Enter برای خط جدید استفاده کنید):",
            font=("Arial", 10),
            justify=tk.RIGHT
        ).pack(anchor=tk.W)
        
        # جعبه متنی برای ورودی چندخطی
        self.text_widget = scrolledtext.ScrolledText(
            self.window,
            wrap=tk.WORD,
            width=70,
            height=15,
            font=("Arial", 11),
            relief=tk.SUNKEN,
            bd=2
        )
        self.text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # دکمه‌های کنترلی
        button_frame = tk.Frame(self.window)
        button_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # دکمه ارسال
        send_button = tk.Button(
            button_frame,
            text="ارسال پیام",
            command=self.send_message,
            font=("Arial", 10, "bold"),
            bg="#4CAF50",
            fg="white",
            width=12
        )
        send_button.pack(side=tk.RIGHT, padx=5)
        
        # دکمه لغو
        cancel_button = tk.Button(
            button_frame,
            text="لغو",
            command=self.window.destroy,
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            width=8
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # دکمه پاک کردن
        clear_button = tk.Button(
            button_frame,
            text="پاک کردن",
            command=self.clear_text,
            font=("Arial", 10),
            bg="#FF9800",
            fg="white",
            width=8
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # فوکوس روی جعبه متنی
        self.text_widget.focus_set()
    
    def send_message(self):
        """ارسال پیام چندخطی"""
        message = self.text_widget.get("1.0", tk.END).strip()
        if message:
            self.callback(message)
            self.window.destroy()
        else:
            messagebox.showwarning("هشدار", "لطفاً پیامی وارد کنید!")
    
    def clear_text(self):
        """پاک کردن متن"""
        self.text_widget.delete("1.0", tk.END)

from search import SafeWebSearcher

# search.py (اضافه کردن تابع اصلی)
def search_and_save(query, max_results=5):
    """تابع اصلی برای جستجو و ذخیره"""
    searcher = SafeWebSearcher()
    
    # بارگذاری نتایج قبلی اگر وجود داشته باشد
    searcher.load_from_file()
    
    # جستجوی کوئری جدید
    results = searcher.search_query(query, max_results)
    
    if results:
        count = searcher.save_to_dictionary(query, results)
        print(f"{count} نتیجه برای '{query}' پیدا و ذخیره شد")
        return results
    else:
        print("هیچ نتیجه‌ای پیدا نشد")
        return []