import multiprocessing
import os
import json
import time
import requests
import re
import httpx
from dotenv import load_dotenv
from groq import Groq

# وارد کردن توابع از فایل‌های جانبی
from cache_service import CacheService
from scraper import build_eitaa_payload, extract_clean_usernames, get_channel_details
from analyzer import analyze_with_groq
from worker import start_worker

# لود کردن تنظیمات .env
load_dotenv()

def run_crawler():
    token = os.getenv("EITAA_TOKEN")
    uid = os.getenv("EITAA_USER_ID")
    ai_key = os.getenv("GROQ_API_KEY")
    proxy = os.getenv("SOCKS_PROXY")
    
    # راه‌اندازی کلاینت AI با تنظیمات پروکسی
    client = Groq(api_key=ai_key, http_client=httpx.Client(proxy=proxy))
    cache = CacheService()
    
    search_query = input("Enter keyword (e.g. لاک پاک کن): ")
    payload = build_eitaa_payload(token, search_query)
    headers = {"User-Agent": "Mozilla/5.0", "Origin": "https://web.eitaa.com"}
    
    print("[*] Searching IDs on Eitaa...")
    try:
        response = requests.post("https://hosna.eitaa.com/eitaa/", data=payload, headers=headers, params={"id": uid})
        raw_stream = response.content.decode('utf-8', errors='ignore')

        with open("./doc/raw_response.txt", "w", encoding="utf-8") as f:
            f.write(raw_stream)
        
        # استخراج یوزرنیم‌ها و بلاک‌های متنی
        final_usernames_map = extract_clean_usernames(raw_stream)
        usernames = list(final_usernames_map.keys())

        # ذخیره نتایج اولیه جستجو
        results_map = {}
        info_db = {}
        analysis_db = {}

        print(f"[*] Processing {len(usernames)} channels...")
        for user in usernames:
            print(f" -> Processing @{user}...")
            
            data = get_channel_details(user) 
            if data:
                # پر کردن دیتای results (مربوط به بخش اول قبلی)
                results_map[f"@{user}"] = data["posts"][-1:] if data["posts"] else []
                
                # پر کردن دیتای info
                info_db[f"@{user}"] = {"bio": data["bio"], "posts": data["posts"]}
                
                # ۲. تحلیل توسط هوش مصنوعی (Analyzer)
                analysis_res = analyze_with_groq(client, user, data["bio"], data["posts"])
                analysis_db[f"@{user}"] = analysis_res
                
                # ارسال به صف Redis (اگر فروشگاه بود)
                if any(word in analysis_res.upper() for word in ["YES", "بله"]):
                    product_job = {
                        "username": user,
                        "channel_name": str(final_usernames_map[user]["channel_name"]), 
                        "bio": str(data["bio"]),
                        "analysis": str(analysis_res),
                        "timestamp": time.time(),
                        "posts": data["posts"]
                    }
                    cache.push_to_queue(product_job)
            
            time.sleep(1.5) 

        # ذخیره فایل‌های نهایی
        with open("./doc/channel_info.json", "w", encoding="utf-8") as f:
            json.dump(info_db, f, ensure_ascii=False, indent=4)
        with open("./doc/analysis.json", "w", encoding="utf-8") as f:
            json.dump(analysis_db, f, ensure_ascii=False, indent=4)

        print("\n[DONE] Data collection and analysis complete.")

    except Exception as e:
        print(f"Pipeline Error: {e}")

if __name__ == "__main__":
    worker_process = multiprocessing.Process(target=start_worker, name="Mongo-Worker")
    worker_process.start()

    run_crawler()

    print("[!] Crawler is done. Waiting for worker to finish pending jobs...")
    time.sleep(5)

    worker_process.terminate() 
    print("[✔] Entire Pipeline stopped.")