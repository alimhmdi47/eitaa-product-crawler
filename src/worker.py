import json
import os
import time
from pymongo import MongoClient
from dotenv import load_dotenv

from cache_service import CacheService

load_dotenv()

def start_worker():
    cache = CacheService()
    queue_name = cache.product_queue

    try:
        mongo_client = MongoClient(os.getenv("MONGO_URI"))
        db = mongo_client[os.getenv("MONGO_DB_NAME")]
        collection = db[os.getenv("MONGO_COLLECTION")]
        # تست اتصال
        mongo_client.admin.command('ping')
    except Exception as e:
        print(f"[!] MongoDB Connection Error: {e}")
        return

    print(f"[*] Worker started. Listening to queue: {queue_name}...")

    while True:
        message = None
        try:
            # برداشتن دیتا از صف نهایی محصولات
            result = cache.redis_client.blpop(queue_name)
            if not result:
                continue
            
            _, message = result
            product_data = json.loads(message)
            
            # افزودن متادیتا
            product_data["processed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            product_data["status"] = "verified"

            #  ذخیره نهایی در MongoDB
            result = collection.insert_one(product_data)
            
            print(f"[Worker] Success! Product from @{product_data['username']} saved. ID: {result.inserted_id}")
        
        except Exception as e:
            print(f"[Worker Error]: {e}")
            
            # استراتژی محافظت از داده:
            # اگر دیتا برداشته شده بود ولی در مونگو ذخیره نشد، آن را به صف برمی‌گردانیم
            if message:
                print("[!] Re-queuing failed message...")
                cache.redis_client.lpush(queue_name, message)
            
            time.sleep(5)

if __name__ == "__main__":
    start_worker()