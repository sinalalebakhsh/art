# auto_responder.py
import random
import datetime
import os  # این خط اضافه شود
from utils import FileUtils
from config import Config

class AutoResponder:
    """کلاس پاسخ‌دهنده خودکار به پیام‌های کاربر"""
    
    # دیکشنری پاسخ‌های خودکار بر اساس کلمات کلیدی
    RESPONSE_TEMPLATES = {
        "سلام": [
            "سلام! چطور می‌تونم کمک کنم؟",
            "سلام عزیز! چه خبر؟",
            "درود! چه کمکی از دستم برمیاد؟"
        ],
        "خداحافظ": [
            "خداحافظ! موفق باشید.",
            "به امید دیدار!",
            "خدانگهدار! اگر سوالی داشتید در خدمتم."
        ],
        "تشکر": [
            "خواهش می‌کنم! خوشحالم که مفید بودم.",
            "قابل نداشت! anytime!",
            "ممنون از شما! 😊"
        ],
        "سوال": [
            "چه سوالی دارید؟ با کمال میل پاسخ می‌دم.",
            "سوال خود را بپرسید، من اینجا هستم تا کمک کنم.",
            "حتماً! چه چیزی می‌خواهید بدانید؟"
        ],
        "کمک": [
            "حتماً! چه کمکی نیاز دارید؟",
            "با pleasure! بگویید چه کاری می‌تونم انجام بدم.",
            "در خدمتم! چه مشکلی دارید؟"
        ],
        "چطور": [
            "خوبم ممنون! شما چطورید؟",
            "عالی! امیدوارم شما هم خوب باشید.",
            "Thanks for asking! همه چی رو به راهه."
        ]
    }
    
    # پاسخ‌های پیش‌فرض برای زمانی که کلمه کلیدی پیدا نمی‌شود
    DEFAULT_RESPONSES = [
        "جالب است! بیشتر توضیح می‌دید؟",
        "متوجه شدم! ادامه بدهید...",
        "خب، این رو فهمیدم. چی دیگه؟",
        "جالب توجه است! می‌خواهید در موردش بیشتر صحبت کنیم؟",
        "OK! چه چیز دیگری می‌خواهید بدانید؟"
    ]
    
    @staticmethod
    def generate_response(user_message):
        """تولید پاسخ خودکار بر اساس پیام کاربر"""
        user_message_lower = user_message.lower()
        
        # بررسی کلمات کلیدی در پیام کاربر
        for keyword, responses in AutoResponder.RESPONSE_TEMPLATES.items():
            if keyword in user_message_lower:
                return random.choice(responses)
        
        # اگر کلمه کلیدی پیدا نشد، پاسخ پیش‌فرض
        return random.choice(AutoResponder.DEFAULT_RESPONSES)
    
    @staticmethod
    def generate_response_filename(topic):
        """تولید نام فایل برای بایگانی پاسخ‌ها"""
        now = datetime.datetime.now()
        date_part = now.strftime("%Y-%m-%d_%H-%M")
        sanitized_topic = FileUtils.sanitize_filename(topic)
        filename = f"response_{date_part}_{sanitized_topic}.txt"
        return os.path.join(Config.get_response_folder(), filename)
    
    @staticmethod
    def save_response_to_archive(filename, user_message, bot_response):
        """ذخیره پاسخ در فایل بایگانی"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(filename, "a", encoding="utf-8") as file:
                file.write(f"[{timestamp}] کاربر: {user_message}\n")
                file.write(f"[{timestamp}] ربات: {bot_response}\n")
                file.write("-" * 50 + "\n")
            return True
        except Exception as e:
            print(f"خطا در ذخیره پاسخ: {e}")
            return False
    
    @staticmethod
    def process_message(user_message, topic):
        """پردازش پیام کاربر و تولید پاسخ"""
        # تولید پاسخ خودکار
        response = AutoResponder.generate_response(user_message)
        
        # تولید نام فایل برای بایگانی پاسخ
        response_filename = AutoResponder.generate_response_filename(topic)
        
        # ذخیره گفتگو در فایل پاسخ‌ها
        AutoResponder.save_response_to_archive(response_filename, user_message, response)
        
        return response