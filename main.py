import multiprocessing
import os
import json
import random
import time
import requests
import re
import httpx
from dotenv import load_dotenv
from groq import Groq

# وارد کردن توابع از فایل‌های جانبی
from cache_service import CacheService
from scraper import build_eitaa_payload, extract_clean_usernames, get_channel_details
from analyzer import analyze_with_groq, generate_advanced_keywords
from session_service import SessionManager
from worker import start_worker

# لود کردن تنظیمات .env
load_dotenv()

def run_crawler(search_query, client, cache, token, uid, acc_proxy):
    
    # search_query = input("Enter keyword (e.g. لاک پاک کن): ")
    payload = build_eitaa_payload(token, search_query)
    headers = {"User-Agent": "Mozilla/5.0", "Origin": "https://web.eitaa.com"}
    proxies = None
    if acc_proxy:
        proxies = {"http": acc_proxy, "https": acc_proxy}
    
    print("[*] Searching IDs on Eitaa...")
    try:
        response = requests.post("https://hosna.eitaa.com/eitaa/", data=payload, headers=headers, params={"id": uid}, proxies=proxies)
        print(f"status: {response.status_code}")
        if response.status_code == 429 or len(response.content) < 100:
            return "LIMITED"
        
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
        return "SUCCESS"

    except Exception as e:
        print(f"Pipeline Error: {e}")
        return "ERROR"

if __name__ == "__main__":
    # لود کردن تنظیمات .env
    load_dotenv()
    tokens = os.getenv("EITAA_TOKENS")
    uids = os.getenv("EITAA_USER_IDS")
    eitaa_proxies = os.getenv("EITAA_PROXIES")
    ai_key = os.getenv("GROQ_API_KEY")
    proxy = os.getenv("SOCKS_PROXY")
    
    session_mgr = SessionManager(tokens, uids, eitaa_proxies)
    client = Groq(api_key=ai_key, http_client=httpx.Client(proxy=proxy))
    cache = CacheService()

    worker_process = multiprocessing.Process(target=start_worker, name="Mongo-Worker")
    worker_process.start()
    try:
            print("[] AI is generating strategic keywords...")
            search_keywords = generate_advanced_keywords(client) 
            print(f"[search_keywords] : \n {search_keywords}")

            word_idx = 0
            while word_idx < len(search_keywords):
                word = search_keywords[word_idx]
                
                token, uid, acc_proxy = session_mgr.get_random_session()
                if token is None:
                    print("[!!!] All accounts are in cooldown. Sleeping for 60s...")
                    time.sleep(60)
                    continue

                print(f"token: {token}, uid: {uid}, proxy: {acc_proxy}")

                status = run_crawler(word, client, cache, token, uid, acc_proxy) 

                if status == "LIMITED":
                    session_mgr.penalize(token, duration=600)
                    time.sleep(2)
                    continue

                word_idx += 1
                
                print(f"[*] Cooling down for 5-10 seconds...")
                time.sleep(random.uniform(5, 10))

    except KeyboardInterrupt:
        print("\n[!] User stopped the process.")
    finally:
        print("\n[!] Crawler is done. Waiting for worker to finish pending jobs...")
        time.sleep(5)
        worker_process.terminate() 
        print("[✔] Entire Pipeline stopped.")