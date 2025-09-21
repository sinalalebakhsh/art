# search.py
import time
import random
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import quote_plus
import os

class SafeWebSearcher:
    def __init__(self):
        self.search_results = {}
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        ]
        self.search_engines = [
            'https://www.google.com/search?q=',
            'https://www.bing.com/search?q=',
            'https://search.yahoo.com/search?p=',
            'https://duckduckgo.com/html/?q='
        ]
        
    def get_random_delay(self):
        """تأخیر تصادفی برای جلوگیری از بلاک شدن"""
        return random.uniform(2.0, 5.0)
    
    def get_random_user_agent(self):
        """User-Agent تصادفی"""
        return random.choice(self.user_agents)
    
    def rotate_search_engine(self, query, engine_index=0):
        """چرخش بین موتورهای جستجو"""
        if engine_index >= len(self.search_engines):
            return None
        
        search_url = self.search_engines[engine_index] + quote_plus(query)
        return search_url
    
    def safe_request(self, url, max_retries=3):
        """درخواست ایمن با مدیریت خطا"""
        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        for attempt in range(max_retries):
            try:
                time.sleep(self.get_random_delay())
                
                response = requests.get(
                    url, 
                    headers=headers, 
                    timeout=10,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Too Many Requests
                    print(f"درخواست زیاد! منتظر می‌مانم... (تلاش {attempt + 1})")
                    time.sleep(10)
                else:
                    print(f"خطای HTTP {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"خطا در اتصال: {e}")
                time.sleep(5)
        
        return None
    
    def extract_results(self, html, search_engine):
        """استخراج نتایج از HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        try:
            if 'google' in search_engine:
                # برای گوگل
                for g in soup.find_all('div', class_='tF2Cxc'):
                    title_elem = g.find('h3')
                    link_elem = g.find('a')
                    desc_elem = g.find('span', class_='aCOpRe')
                    
                    if title_elem and link_elem:
                        results.append({
                            'title': title_elem.get_text(),
                            'url': link_elem.get('href'),
                            'description': desc_elem.get_text() if desc_elem else ''
                        })
            
            elif 'bing' in search_engine:
                # برای بینگ
                for result in soup.find_all('li', class_='b_algo'):
                    title_elem = result.find('h2')
                    link_elem = result.find('a')
                    desc_elem = result.find('p')
                    
                    if title_elem and link_elem:
                        results.append({
                            'title': title_elem.get_text(),
                            'url': link_elem.get('href'),
                            'description': desc_elem.get_text() if desc_elem else ''
                        })
            
            elif 'yahoo' in search_engine or 'duckduckgo' in search_engine:
                # برای یاهو و داک‌داک‌گو
                for result in soup.find_all('div', class_='compTitle'):
                    title_elem = result.find('h3')
                    link_elem = result.find('a')
                    
                    if title_elem and link_elem:
                        results.append({
                            'title': title_elem.get_text(),
                            'url': link_elem.get('href'),
                            'description': ''
                        })
                        
        except Exception as e:
            print(f"خطا در استخراج نتایج: {e}")
        
        return results
    
    def search_query(self, query, max_results=10):
        """جستجوی یک کوئری"""
        print(f"در حال جستجو برای: {query}")
        
        all_results = []
        engine_index = 0
        
        while len(all_results) < max_results and engine_index < len(self.search_engines):
            search_url = self.rotate_search_engine(query, engine_index)
            if not search_url:
                break
            
            print(f"استفاده از موتور جستجو: {self.search_engines[engine_index].split('/')[2]}")
            
            response = self.safe_request(search_url)
            if response:
                results = self.extract_results(response.text, self.search_engines[engine_index])
                all_results.extend(results[:max_results - len(all_results)])
            
            engine_index += 1
            time.sleep(self.get_random_delay())
        
        return all_results[:max_results]
    
    def save_to_dictionary(self, query, results):
        """ذخیره نتایج در دیکشنری"""
        if query not in self.search_results:
            self.search_results[query] = []
        
        self.search_results[query].extend(results)
        
        # ذخیره در فایل JSON برای backup
        self.save_to_file()
        
        return len(results)
    
    def save_to_file(self, filename="search_results.json"):
        """ذخیره دیکشنری در فایل"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.search_results, f, ensure_ascii=False, indent=2)
            print(f"نتایج در {filename} ذخیره شد")
        except Exception as e:
            print(f"خطا در ذخیره فایل: {e}")
    
    def load_from_file(self, filename="search_results.json"):
        """بارگذاری دیکشنری از فایل"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    self.search_results = json.load(f)
                print(f"نتایج از {filename} بارگذاری شد")
                return True
        except Exception as e:
            print(f"خطا در بارگذاری فایل: {e}")
        return False
    
    def get_results(self, query=None):
        """دریافت نتایج"""
        if query:
            return self.search_results.get(query, [])
        return self.search_results
    
    def clear_results(self):
        """پاک کردن نتایج"""
        self.search_results = {}
        print("همه نتایج پاک شدند")

# تابع اصلی برای استفاده از خارج
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

# مثال استفاده
if __name__ == "__main__":
    # تست عملکرد
    queries = ["پایتون برنامه نویسی", "هوش مصنوعی", "یادگیری ماشین"]
    
    searcher = SafeWebSearcher()
    
    for query in queries:
        results = searcher.search_query(query, max_results=3)
        if results:
            searcher.save_to_dictionary(query, results)
            print(f"نتایج برای '{query}':")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   URL: {result['url']}")
                print()
        
        time.sleep(3)  # تأخیر بین جستجوها
    
    # ذخیره نهایی
    searcher.save_to_file()
    print("همه نتایج ذخیره شدند")