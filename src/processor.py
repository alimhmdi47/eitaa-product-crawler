import json
import os
import time
from dotenv import load_dotenv

from cache_service import CacheService
from analyzer import extract_bulk_products, client

load_dotenv()

def start_processor():
    # مقداردهی اولیه سرویس کش
    cache = CacheService()
    
    # گرفتن نام صف ورودی مستقیماً از تنظیمات کلاس کش
    input_queue = cache.channel_queue

    print(f"[*] Processor started. Listening to queue: {input_queue}...")

    while True:
        try:
            # 1. برداشتن دیتای خام کانال از Redis
            message = cache.pop_from_channels_queue()
            if not message:
                continue
            
            channel_data = json.loads(message)
            username = channel_data.get("username")
            posts = channel_data.get("posts", [])

            print(f"[*] Processing @{username} with AI...")

            # 2. استخراج محصولات (با مدیریت Rate Limit)
            success = False
            while not success:
                try:
                    # فراخوانی مدل AI برای استخراج لیست محصولات
                    bulk_data = extract_bulk_products(client, posts)
                    
                    if bulk_data and "products" in bulk_data:
                        for item in bulk_data["products"]:
                            # ساخت آبجکت نهایی محصول
                            product_job = {
                                "username": username,
                                "channel_name": channel_data.get("channel_name"),
                                "details": item,
                                "raw_caption": posts[item['post_id']] if isinstance(item.get('post_id'), int) and 0 <= item['post_id'] < len(posts) else "",
                                "processed_at_processor": time.strftime("%Y-%m-%d %H:%M:%S")
                            }
                            
                            # 3. ارسال به صف نهایی (ورکر مونگو) از طریق CacheService
                            cache.push_to_products_queue(product_job)
                        
                        print(f"   [✔] Successfully extracted {len(bulk_data['products'])} products from @{username}")
                    
                    success = True 

                except Exception as ai_error:
                    error_msg = str(ai_error).lower()
                    if "rate_limit" in error_msg or "429" in error_msg:
                        print(" [!!!] Groq Rate Limit Hit! Sleeping for 30 minutes...")
                        cache.set_rate_limit(1800)
                        
                        time.sleep(1800)
                        print(" [!] Waking up... retrying the last channel.")
                    else:
                        print(f" [AI Error]: {ai_error}")
                        success = True 

        except Exception as e:
            print(f"[Processor Error]: {e}")
            time.sleep(5)

if __name__ == "__main__":
    start_processor()