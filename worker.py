import redis
import json
import os
import time
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def start_worker():
    # اتصال به Redis
    r = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0)
    queue_name = os.getenv("REDIS_QUEUE")

    # اتصال به MongoDB
    mongo_client = MongoClient(os.getenv("MONGO_URI"))
    db = mongo_client[os.getenv("MONGO_DB_NAME")]
    collection = db[os.getenv("MONGO_COLLECTION")]

    print(f"[*] Worker started. Listening to queue: {queue_name}...")

    while True:
        try:
            # BLPOP باعث می‌شود اسکریپت منتظر بماند تا دیتای جدید وارد صف شود
            _, message = r.blpop(queue_name)
            
            if message:
                product_data = json.loads(message)
                
                # اینجا می‌توانید پردازش‌های اضافی (مثل Bonus Features) را انجام دهید
                product_data["processed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                product_data["status"] = "verified"

                # ذخیره نهایی در MongoDB
                result = collection.insert_one(product_data)
                
                print(f"[Worker] Success! Product from @{product_data['username']} saved to Mongo. ID: {result.inserted_id}")
        
        except Exception as e:
            print(f"[Worker Error]: {e}")
            time.sleep(5)

if __name__ == "__main__":
    start_worker()