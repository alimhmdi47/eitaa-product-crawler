import os
import json
import time
import requests
import re
import httpx
from dotenv import load_dotenv
from groq import Groq

# وارد کردن توابع از فایل‌های جانبی
from scraper import build_eitaa_payload, get_channel_details

# لود کردن تنظیمات .env
load_dotenv()

def start_engine():
    token = os.getenv("EITAA_TOKEN")
    uid = os.getenv("EITAA_USER_ID")
    ai_key = os.getenv("GROQ_API_KEY")
    proxy = os.getenv("SOCKS_PROXY")
    
    # راه‌اندازی کلاینت AI با تنظیمات پروکسی
    client = Groq(api_key=ai_key, http_client=httpx.Client(proxy=proxy))
    
    search_query = input("Enter keyword (e.g. لاک پاک کن): ")
    payload = build_eitaa_payload(token, search_query)
    headers = {"User-Agent": "Mozilla/5.0", "Origin": "https://web.eitaa.com"}
    
    print("[*] Searching IDs on Eitaa...")
    try:
        response = requests.post("https://hosna.eitaa.com/eitaa/", data=payload, headers=headers, params={"id": uid})
        raw_stream = response.content.decode('utf-8', errors='ignore')
        
        # استخراج یوزرنیم‌ها و بلاک‌های متنی
        usernames = list(dict.fromkeys(re.findall(r'@([A-Za-z0-9_]{3,})', raw_stream)))
        raw_blocks = [b.strip() for b in re.split(r'[\x00-\x1F\x7F-\x9F]', raw_stream) if len(b.strip()) > 25]

        # ذخیره نتایج اولیه جستجو
        results_map = {f"@{u}": raw_blocks[i:i+1] for i, u in enumerate(usernames)}
        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(results_map, f, ensure_ascii=False, indent=4)

        info_db = {}
        analysis_db = {}

        print(f"[*] Processing {len(usernames)} channels...")
        for user in usernames:
            print(f" -> Fetching & Analyzing @{user}...")
            
            # ۱. استخراج دیتا (Scraper)
            data = get_channel_details(user)
            if data:
                info_db[f"@{user}"] = {"bio": data["bio"], "posts": data["posts"]}
                

            
            time.sleep(1.2) # وقفه برای امنیت

        # ذخیره فایل‌های نهایی
        with open("channel_info.json", "w", encoding="utf-8") as f:
            json.dump(info_db, f, ensure_ascii=False, indent=4)

        print("\n[DONE] Data collection and analysis complete.")

    except Exception as e:
        print(f"Pipeline Error: {e}")

if __name__ == "__main__":
    start_engine()