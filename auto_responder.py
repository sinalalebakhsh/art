# auto_responder.py
import random
import datetime
import os
from utils import FileUtils
from config import Config
from search import search_and_save  # اضافه کردن import

class AutoResponder:
    """کلاس پاسخ‌دهنده خودکار به پیام‌های کاربر"""
    
    RESPONSE_TEMPLATES = {
        "سلام": ["سلام! چطور می‌تونم کمک کنم؟", "سلام عزیز! چه خبر؟"],
        "خداحافظ": ["خداحافظ! موفق باشید.", "به امید دیدار!"],
        "تشکر": ["خواهش می‌کنم!", "قابل نداشت!"],
        "سوال": ["چه سوالی دارید؟", "با کمال میل پاسخ می‌دم."],
        "کمک": ["چه کمکی نیاز دارید؟", "در خدمتم!"],
        "جستجو": ["در حال جستجو برای شما...", "لطفاً منتظر بمانید، در حال جستجو هستم."]
    }
    
    DEFAULT_RESPONSES = [
        "جالب است! می‌خواهید بیشتر بدانید؟",
        "متوجه شدم! ادامه بدهید...",
        "خب، این رو فهمیدم. چی دیگه؟"
    ]
    
    @staticmethod
    def generate_response(user_message, topic):
        """تولید پاسخ خودکار بر اساس پیام کاربر"""
        user_message_lower = user_message.lower()
        
        # اگر پیام مربوط به جستجو باشد
        if any(keyword in user_message_lower for keyword in ["جستجو", "پیدا کن", "سرچ", "search", "find"]):
            # انجام جستجو
            search_results = search_and_save(user_message, max_results=3)
            
            if search_results:
                response = f"من درباره '{user_message}' جستجو کردم. {len(search_results)} نتیجه پیدا شد:\n"
                for i, result in enumerate(search_results[:2], 1):
                    response += f"{i}. {result['title'][:50]}...\n"
                response += "می‌خواهید بیشتر بدانید؟"
            else:
                response = f"متأسفم، نتوانستم اطلاعاتی درباره '{user_message}' پیدا کنم."
            
            return response
        
        # پاسخ‌های معمولی بر اساس کلمات کلیدی
        for keyword, responses in AutoResponder.RESPONSE_TEMPLATES.items():
            if keyword in user_message_lower:
                return random.choice(responses)
        
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
    def process_message(user_message, topic):
        """پردازش پیام کاربر و تولید پاسخ"""
        response = AutoResponder.generate_response(user_message, topic)
        response_filename = AutoResponder.generate_response_filename(topic)
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(response_filename, "a", encoding="utf-8") as file:
                file.write(f"[{timestamp}] کاربر: {user_message}\n")
                file.write(f"[{timestamp}] ربات: {response}\n")
                file.write("-" * 50 + "\n")
        except Exception as e:
            print(f"خطا در ذخیره پاسخ: {e}")
        
        return response