🚀 Eitaa Intelligent Crawler & Analyzer
این پروژه یک پایپ‌لاین هوشمند برای جستجو، استخراج و تحلیل داده‌های پیام‌رسان ایتا (Eitaa) است. سیستم با استفاده از پروتکل اختصاصی ایتا جستجو را انجام داده، کانال‌های مرتبط را پیدا می‌کند و با استفاده از هوش مصنوعی (Groq/Llama3) تشخیص می‌دهد که آیا کانال مورد نظر فروشگاه است یا خیر. در نهایت داده‌های تایید شده در دیتابیس MongoDB ذخیره می‌شوند.

🛠 معماری سیستم
این سیستم از چهار بخش اصلی تشکیل شده است:

Main Engine: بخش جستجو و کراولر اولیه که یوزرنیم‌ها را استخراج می‌کند.

AI Analyzer: تحلیل محتوای Bio و پست‌ها توسط مدل Llama-3 برای تشخیص ماهیت تجاری.

Redis Queue: مدیریت صف پیام‌ها جهت پایداری سیستم (Buffer).

Worker: پردازشگر پس‌زمینه که داده‌های نهایی را با احراز هویت در MongoDB ذخیره می‌کند.

📂 ساختار پروژه
Plaintext

.
├── main.py              # نقطه ورود اصلی و مدیریت فرآیندهای همزمان (Multiprocessing)
├── worker.py            # پردازشگر صف Redis و ذخیره‌ساز MongoDB
├── analyzer.py          # ماژول تحلیل هوش مصنوعی (Groq API)
├── scraper.py           # توابع استخراج داده و ارتباط با پروتکل باینری ایتا
├── cache_service.py     # سرویس مدیریت ارتباط با Redis
├── docker-compose.yaml  # راه‌اندازی Redis, MongoDB و محیط‌های UI
├── pyproject.toml       # مدیریت مدرن وابستگی‌ها با uv
└── doc/                 # محل ذخیره گزارش‌های متنی و خروجی‌های JSON
⚙️ پیش‌نیازها
Python 3.13+

Docker & Docker Compose

Groq API Key (برای پردازش هوش مصنوعی)

ابزار uv (پیشنهادی برای مدیریت پکیج‌ها)

🚀 راهنمای راه‌اندازی و اجرا
۱. تنظیمات محیطی (Environment Variables)
ابتدا فایل .env.example را به .env تغییر نام دهید و مقادیر را بر اساس نیاز خود پر کنید:

Code snippet

# Eitaa Config
EITAA_TOKEN=your_token_here
EITAA_USER_ID=your_id_here

# AI Config
GROQ_API_KEY=gsk_your_key
SOCKS_PROXY=socks5://127.0.0.1:1080  # الزامی برای دسترسی به Groq

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_QUEUE=eitaa_products_queue

# MongoDB
MONGO_URI=mongodb://admin:password123@localhost:27017/
MONGO_DB_NAME=eitaa_db
MONGO_COLLECTION=products
۲. بالا آوردن سرویس‌های دیتابیس (Docker)
دیتابیس‌ها و رابط‌های کاربری آن‌ها را با یک دستور اجرا کنید:

Bash

docker-compose up -d
Mongo Express (UI): http://localhost:8081 (User: admin, Pass: pass)

Redis Insight (UI): http://localhost:5540

۳. نصب وابستگی‌ها
اگر از uv استفاده می‌کنید (پیشنهادی):

Bash

uv sync
اگر از pip استفاده می‌کنید:

Bash

uv export --format requirements-txt > requirements.txt
pip install -r requirements.txt
۴. اجرای پایپ‌لاین
کافیست فایل اصلی را اجرا کنید. این فایل به صورت خودکار Worker را در یک پروسس جداگانه بالا آورده و سپس از شما Keyword جستجو را می‌پرسد:

Bash

python main.py
🔍 نحوه کارکرد بخش‌ها
Scraper: از طریق تابع build_eitaa_payload درخواست‌های باینری به سرورهای ایتا ارسال کرده و یوزرنیم‌های یافت شده را استخراج می‌کند.

Analyzer: محتوای کانال را به مدل llama-3.3-70b-versatile می‌فرستد تا با بررسی Bio و آخرین پست‌ها، فروشگاه بودن کانال را تایید کند.

Worker: با متد blpop به صف ردیس گوش می‌دهد و به محض دریافت دیتای تایید شده، آن را در MongoDB اینسرت می‌کند.

📝 گزارش‌گیری
خروجی‌ها علاوه بر دیتابیس، در فولدر doc نیز ذخیره می‌شوند:

channel_info.json: جزییات استخراج شده (Bio/Posts).

analysis.json: تحلیل‌های متنی هوش مصنوعی.

raw_response.txt: پاسخ خام شبکه جهت عیب‌یابی.

⚠️ نکات مهم
Proxy: به دلیل تحریم‌های API، حتماً از صحت کانکشن SOCKS_PROXY برای بخش Groq اطمینان حاصل کنید.