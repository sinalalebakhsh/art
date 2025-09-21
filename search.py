# search.py
import time
import random
import json
import os
import re
from urllib.parse import quote_plus, urlparse
import http.client
import ssl

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  کتابخانه requests نصب نیست. لطفا pip install requests را اجرا کنید.")

class SafeWebSearcher:
    def __init__(self):
        self.search_results = {}
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        # لیست موتورهای جستجوی جایگزین
        self.search_engines = [
            'https://www.bing.com/search?q=',
            'https://search.yahoo.com/search?p=',
            'https://duckduckgo.com/html/?q=',
            'https://www.ask.com/web?q=',
            'https://www.baidu.com/s?wd='
        ]
        
    def is_available(self):
        return REQUESTS_AVAILABLE
    
    def get_random_delay(self):
        return random.uniform(2.0, 4.0)
    
    def get_random_user_agent(self):
        return random.choice(self.user_agents)
    
    def create_custom_ssl_context(self):
        """ایجاد SSL context برای دور زدن محدودیت‌ها"""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    
    def manual_http_request(self, url):
        """درخواست HTTP دستی برای مواقعی که requests کار نمی‌کند"""
        try:
            parsed_url = urlparse(url)
            host = parsed_url.netloc
            path = parsed_url.path
            if parsed_url.query:
                path += '?' + parsed_url.query
            
            context = self.create_custom_ssl_context()
            
            if url.startswith('https'):
                conn = http.client.HTTPSConnection(host, context=context)
            else:
                conn = http.client.HTTPConnection(host)
            
            headers = {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            
            conn.request("GET", path, headers=headers)
            response = conn.getresponse()
            
            if response.status == 200:
                data = response.read().decode('utf-8')
                conn.close()
                return data
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"خطا در درخواست دستی: {e}")
            return None
    
    def safe_request(self, url):
        """درخواست ایمن با روش‌های مختلف"""
        if not REQUESTS_AVAILABLE:
            return None
        
        time.sleep(self.get_random_delay())
        
        # روش 1: استفاده از requests
        try:
            headers = {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                return response.text
                
        except requests.exceptions.RequestException:
            # روش 2: درخواست دستی اگر requests کار نکرد
            return self.manual_http_request(url)
        
        return None
    
    def search_with_bing(self, query):
        """جستجو با بینگ که معمولاً محدودیت کمتری دارد"""
        search_url = f"https://www.bing.com/search?q={quote_plus(query)}"
        html = self.safe_request(search_url)
        
        if html:
            try:
                soup = BeautifulSoup(html, 'html.parser')
                results = []
                
                # استخراج نتایج از بینگ
                for result in soup.find_all('li', class_='b_algo'):
                    title_elem = result.find('h2')
                    link_elem = result.find('a')
                    desc_elem = result.find('p')
                    
                    if title_elem and link_elem:
                        results.append({
                            'title': title_elem.get_text().strip(),
                            'url': link_elem.get('href', ''),
                            'description': desc_elem.get_text().strip() if desc_elem else ''
                        })
                
                return results
            except:
                pass
        
        return None
    
    def search_with_duckduckgo(self, query):
        """جستجو با داک‌داک‌گو"""
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        html = self.safe_request(search_url)
        
        if html:
            try:
                soup = BeautifulSoup(html, 'html.parser')
                results = []
                
                for result in soup.find_all('div', class_='result'):
                    title_elem = result.find('a', class_='result__a')
                    link_elem = result.find('a', class_='result__a')
                    desc_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem and link_elem:
                        results.append({
                            'title': title_elem.get_text().strip(),
                            'url': link_elem.get('href', ''),
                            'description': desc_elem.get_text().strip() if desc_elem else ''
                        })
                
                return results
            except:
                pass
        
        return None
    
    def search_query(self, query, max_results=5):
        """جستجوی واقعی"""
        if not REQUESTS_AVAILABLE:
            return self.get_mock_results(query)
        
        print(f"🔍 در حال جستجوی واقعی برای: {query}")
        
        # اول با بینگ امتحان می‌کنیم
        results = self.search_with_bing(query)
        
        # اگر بینگ جواب نداد، با داک‌داک‌گو امتحان می‌کنیم
        if not results:
            results = self.search_with_duckduckgo(query)
        
        # اگر بازهم جواب نداد، از موتورهای دیگر استفاده می‌کنیم
        if not results:
            results = self.try_alternative_search_engines(query)
        
        if results:
            return results[:max_results]
        
        return self.get_mock_results(query)
    
    def try_alternative_search_engines(self, query):
        """امتحان موتورهای جستجوی جایگزین"""
        for engine_url in self.search_engines:
            try:
                search_url = engine_url + quote_plus(query)
                html = self.safe_request(search_url)
                
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # استخراج لینک‌ها به صورت عمومی
                    links = soup.find_all('a', href=True)
                    results = []
                    
                    for link in links:
                        href = link.get('href', '')
                        text = link.get_text().strip()
                        
                        # فیلتر کردن لینک‌های معتبر
                        if (href.startswith('http') and 
                            not href.startswith('http://webcache.googleusercontent.com') and
                            not href.startswith('http://www.google.com') and
                            len(text) > 10):
                            
                            results.append({
                                'title': text[:100],
                                'url': href,
                                'description': ''
                            })
                    
                    if results:
                        return results[:5]
                        
            except:
                continue
        
        return None
    
    def get_mock_results(self, query):
        """نتایج نمونه برای تست"""
        return [
            {
                'title': f'نتایج جستجو برای: {query}',
                'url': 'https://www.example.com/search?q=' + quote_plus(query),
                'description': 'این یک نتیجه نمونه است. برای نتایج واقعی مطمئن شوید کتابخانه requests نصب شده باشد.'
            },
            {
                'title': 'راهنمای نصب requests',
                'url': 'https://pypi.org/project/requests/',
                'description': 'دستور نصب: pip install requests'
            }
        ]
    
    def save_to_dictionary(self, query, results):
        """ذخیره نتایج"""
        if query not in self.search_results:
            self.search_results[query] = []
        
        # اضافه کردن timestamp به هر نتیجه
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        for result in results:
            result['search_time'] = timestamp
            result['query'] = query
        
        self.search_results[query].extend(results)
        self.save_to_file()
        
        print(f"✅ {len(results)} نتیجه برای '{query}' ذخیره شد")
        return len(results)
    
    def save_to_file(self, filename="search_results.json"):
        """ذخیره در فایل"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.search_results, f, ensure_ascii=False, indent=2)
            print(f"💾 نتایج در {filename} ذخیره شد")
        except Exception as e:
            print(f"❌ خطا در ذخیره فایل: {e}")
    
    def load_from_file(self, filename="search_results.json"):
        """بارگذاری از فایل"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    self.search_results = json.load(f)
                print(f"📂 نتایج از {filename} بارگذاری شد")
                return True
        except Exception as e:
            print(f"❌ خطا در بارگذاری فایل: {e}")
        return False
    
    def get_results(self, query=None):
        if query:
            return self.search_results.get(query, [])
        return self.search_results
    
    def clear_results(self):
        self.search_results = {}
        print("🗑️ همه نتایج پاک شدند")

# # تابع اصلی
# def search_and_save(query, max_results=3):
#     searcher = SafeWebSearcher()
#     searcher.load_from_file()
    
#     results = searcher.search_query(query, max_results)
    
#     if results:
#         searcher.save_to_dictionary(query, results)
#         return results
    
#     return []

# تست واقعی
if __name__ == "__main__":
    print("🧪 تست جستجوی واقعی...")
    
    searcher = SafeWebSearcher()
    
    # تست چند کوئری
    test_queries = ["پایتون برنامه نویسی", "هوش مصنوعی", "یادگیری ماشین"]
    
    for query in test_queries:
        print(f"\n🔍 جستجوی: {query}")
        results = searcher.search_query(query, 2)
        
        if results:
            searcher.save_to_dictionary(query, results)
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['title']}")
                print(f"      {result['url']}")
        else:
            print("   ❌ هیچ نتیجه‌ای پیدا نشد")
        
        time.sleep(3)
    
    # ذخیره نهایی
    searcher.save_to_file()
    print(f"\n✅ تست کامل شد. نتایج در search_results.json ذخیره شدند")

# در انتهای search.py این تابع باید باشد:
def search_and_save(query, max_results=3):
    searcher = SafeWebSearcher()
    searcher.load_from_file()
    
    results = searcher.search_query(query, max_results)
    
    if results:
        searcher.save_to_dictionary(query, results)
        return results
    
    return []

# # search.py
# import time
# import random
# import requests
# from bs4 import BeautifulSoup
# import json
# from urllib.parse import quote_plus
# import os

# class SafeWebSearcher:
#     def __init__(self):
#         self.search_results = {}
#         self.user_agents = [
#             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
#             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
#             'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
#             'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
#         ]
#         self.search_engines = [
#             'https://www.google.com/search?q=',
#             'https://www.bing.com/search?q=',
#             'https://search.yahoo.com/search?p=',
#             'https://duckduckgo.com/html/?q='
#         ]
        
#     def get_random_delay(self):
#         """تأخیر تصادفی برای جلوگیری از بلاک شدن"""
#         return random.uniform(2.0, 5.0)
    
#     def get_random_user_agent(self):
#         """User-Agent تصادفی"""
#         return random.choice(self.user_agents)
    
#     def rotate_search_engine(self, query, engine_index=0):
#         """چرخش بین موتورهای جستجو"""
#         if engine_index >= len(self.search_engines):
#             return None
        
#         search_url = self.search_engines[engine_index] + quote_plus(query)
#         return search_url
    
#     def safe_request(self, url, max_retries=3):
#         """درخواست ایمن با مدیریت خطا"""
#         headers = {
#             'User-Agent': self.get_random_user_agent(),
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#             'Accept-Language': 'en-US,en;q=0.5',
#             'Accept-Encoding': 'gzip, deflate',
#             'Connection': 'keep-alive',
#             'Upgrade-Insecure-Requests': '1',
#         }
        
#         for attempt in range(max_retries):
#             try:
#                 time.sleep(self.get_random_delay())
                
#                 response = requests.get(
#                     url, 
#                     headers=headers, 
#                     timeout=10,
#                     allow_redirects=True
#                 )
                
#                 if response.status_code == 200:
#                     return response
#                 elif response.status_code == 429:  # Too Many Requests
#                     print(f"درخواست زیاد! منتظر می‌مانم... (تلاش {attempt + 1})")
#                     time.sleep(10)
#                 else:
#                     print(f"خطای HTTP {response.status_code}")
                    
#             except requests.exceptions.RequestException as e:
#                 print(f"خطا در اتصال: {e}")
#                 time.sleep(5)
        
#         return None
    
#     def extract_results(self, html, search_engine):
#         """استخراج نتایج از HTML"""
#         soup = BeautifulSoup(html, 'html.parser')
#         results = []
        
#         try:
#             if 'google' in search_engine:
#                 # برای گوگل
#                 for g in soup.find_all('div', class_='tF2Cxc'):
#                     title_elem = g.find('h3')
#                     link_elem = g.find('a')
#                     desc_elem = g.find('span', class_='aCOpRe')
                    
#                     if title_elem and link_elem:
#                         results.append({
#                             'title': title_elem.get_text(),
#                             'url': link_elem.get('href'),
#                             'description': desc_elem.get_text() if desc_elem else ''
#                         })
            
#             elif 'bing' in search_engine:
#                 # برای بینگ
#                 for result in soup.find_all('li', class_='b_algo'):
#                     title_elem = result.find('h2')
#                     link_elem = result.find('a')
#                     desc_elem = result.find('p')
                    
#                     if title_elem and link_elem:
#                         results.append({
#                             'title': title_elem.get_text(),
#                             'url': link_elem.get('href'),
#                             'description': desc_elem.get_text() if desc_elem else ''
#                         })
            
#             elif 'yahoo' in search_engine or 'duckduckgo' in search_engine:
#                 # برای یاهو و داک‌داک‌گو
#                 for result in soup.find_all('div', class_='compTitle'):
#                     title_elem = result.find('h3')
#                     link_elem = result.find('a')
                    
#                     if title_elem and link_elem:
#                         results.append({
#                             'title': title_elem.get_text(),
#                             'url': link_elem.get('href'),
#                             'description': ''
#                         })
                        
#         except Exception as e:
#             print(f"خطا در استخراج نتایج: {e}")
        
#         return results
    
#     def search_query(self, query, max_results=10):
#         """جستجوی یک کوئری"""
#         print(f"در حال جستجو برای: {query}")
        
#         all_results = []
#         engine_index = 0
        
#         while len(all_results) < max_results and engine_index < len(self.search_engines):
#             search_url = self.rotate_search_engine(query, engine_index)
#             if not search_url:
#                 break
            
#             print(f"استفاده از موتور جستجو: {self.search_engines[engine_index].split('/')[2]}")
            
#             response = self.safe_request(search_url)
#             if response:
#                 results = self.extract_results(response.text, self.search_engines[engine_index])
#                 all_results.extend(results[:max_results - len(all_results)])
            
#             engine_index += 1
#             time.sleep(self.get_random_delay())
        
#         return all_results[:max_results]
    
#     def save_to_dictionary(self, query, results):
#         """ذخیره نتایج در دیکشنری"""
#         if query not in self.search_results:
#             self.search_results[query] = []
        
#         self.search_results[query].extend(results)
        
#         # ذخیره در فایل JSON برای backup
#         self.save_to_file()
        
#         return len(results)
    
#     def save_to_file(self, filename="search_results.json"):
#         """ذخیره دیکشنری در فایل"""
#         try:
#             with open(filename, 'w', encoding='utf-8') as f:
#                 json.dump(self.search_results, f, ensure_ascii=False, indent=2)
#             print(f"نتایج در {filename} ذخیره شد")
#         except Exception as e:
#             print(f"خطا در ذخیره فایل: {e}")
    
#     def load_from_file(self, filename="search_results.json"):
#         """بارگذاری دیکشنری از فایل"""
#         try:
#             if os.path.exists(filename):
#                 with open(filename, 'r', encoding='utf-8') as f:
#                     self.search_results = json.load(f)
#                 print(f"نتایج از {filename} بارگذاری شد")
#                 return True
#         except Exception as e:
#             print(f"خطا در بارگذاری فایل: {e}")
#         return False
    
#     def get_results(self, query=None):
#         """دریافت نتایج"""
#         if query:
#             return self.search_results.get(query, [])
#         return self.search_results
    
#     def clear_results(self):
#         """پاک کردن نتایج"""
#         self.search_results = {}
#         print("همه نتایج پاک شدند")

# # تابع اصلی برای استفاده از خارج
# def search_and_save(query, max_results=5):
#     """تابع اصلی برای جستجو و ذخیره"""
#     searcher = SafeWebSearcher()
    
#     # بارگذاری نتایج قبلی اگر وجود داشته باشد
#     searcher.load_from_file()
    
#     # جستجوی کوئری جدید
#     results = searcher.search_query(query, max_results)
    
#     if results:
#         count = searcher.save_to_dictionary(query, results)
#         print(f"{count} نتیجه برای '{query}' پیدا و ذخیره شد")
#         return results
#     else:
#         print("هیچ نتیجه‌ای پیدا نشد")
#         return []

# # مثال استفاده
# if __name__ == "__main__":
#     # تست عملکرد
#     queries = ["پایتون برنامه نویسی", "هوش مصنوعی", "یادگیری ماشین"]
    
#     searcher = SafeWebSearcher()
    
#     for query in queries:
#         results = searcher.search_query(query, max_results=3)
#         if results:
#             searcher.save_to_dictionary(query, results)
#             print(f"نتایج برای '{query}':")
#             for i, result in enumerate(results, 1):
#                 print(f"{i}. {result['title']}")
#                 print(f"   URL: {result['url']}")
#                 print()
        
#         time.sleep(3)  # تأخیر بین جستجوها
    
#     # ذخیره نهایی
#     searcher.save_to_file()
#     print("همه نتایج ذخیره شدند")