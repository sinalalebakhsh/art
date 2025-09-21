# config.py
import os

class Config:
    """کلاس تنظیمات برنامه"""
    APP_NAME = "برنامه چت - بایگانی طبقه‌بندی شده با پاسخ خودکار"
    WINDOW_SIZE = "850x700"
    ARCHIVE_FOLDER = "chat_archives"
    RESPONSE_FOLDER = "response_archives"
    FONT_FAMILY = "Arial"
    
    @staticmethod
    def get_archive_folder():
        """دریافت مسیر پوشه بایگانی کاربر"""
        if not os.path.exists(Config.ARCHIVE_FOLDER):
            os.makedirs(Config.ARCHIVE_FOLDER)
        return Config.ARCHIVE_FOLDER
    
    @staticmethod
    def get_response_folder():
        """دریافت مسیر پوشه بایگانی پاسخ‌ها"""
        if not os.path.exists(Config.RESPONSE_FOLDER):
            os.makedirs(Config.RESPONSE_FOLDER)
        return Config.RESPONSE_FOLDER