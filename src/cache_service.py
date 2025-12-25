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
        
        # نام صف محصولات (برای ذخیره در مونگو)
        self.product_queue = os.getenv("REDIS_QUEUE", "eitaa_products_queue")
        # نام صف کانال‌ها (برای پردازش توسط AI)
        self.channel_queue = os.getenv("REDIS_CHANNELS_QUEUE", "eitaa_channels_queue")

    def push_to_channels_queue(self, channel_data):
        """ارسال اطلاعات خام کانال به صف پردازشگر AI"""
        try:
            serialized_data = json.dumps(channel_data, ensure_ascii=False)
            # استفاده از rpush برای رعایت ترتیب
            self.redis_client.rpush(self.channel_queue, serialized_data)
            return True
        except Exception as e:
            print(f"Redis Channel Push Error: {e}")
            return False

    def push_to_products_queue(self, product_data):
        """ارسال محصول نهایی به صف ذخیره‌سازی مونگو"""
        try:
            serialized_data = json.dumps(product_data, ensure_ascii=False)
            self.redis_client.rpush(self.product_queue, serialized_data)
            return True
        except Exception as e:
            print(f"Redis Product Push Error: {e}")
            return False
        
    def pop_from_channels_queue(self, timeout=0):
        """برداشتن دیتا از صف کانال‌ها (Blocking Pop)"""
        try:
            # blpop خروجی به صورت (queue_name, value) می‌دهد
            result = self.redis_client.blpop(self.channel_queue, timeout=timeout)
            return result[1] if result else None
        except Exception as e:
            print(f"Redis Pop Error: {e}")
            return None

    def set_rate_limit(self, duration_seconds=1800):
        """تنظیم وضعیت محدودیت نرخ برای سرویس AI"""
        try:
            self.redis_client.setex("groq_limit_active", duration_seconds, "true")
            return True
        except Exception as e:
            print(f"Redis Set Limit Error: {e}")
            return False