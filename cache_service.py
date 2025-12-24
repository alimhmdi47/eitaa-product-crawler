import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

class CacheService:
    def __init__(self):
        # خواندن تنظیمات از .env
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        
        # اتصال به Redis
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=0,
            decode_responses=True
        )
        
        # تعریف نام صف از .env یا مقدار پیش‌فرض
        self.queue_name = os.getenv("REDIS_QUEUE", "eitaa_products_queue")

    def push_to_queue(self, product_data):
        """ارسال محصول به صف Redis"""
        try:
            serialized_data = json.dumps(product_data, ensure_ascii=False)
            self.redis_client.lpush(self.queue_name, serialized_data)
            return True
        except Exception as e:
            print(f"Redis Push Error: {e}")
            return False

    def get_queue_size(self):
        return self.redis_client.llen(self.queue_name)