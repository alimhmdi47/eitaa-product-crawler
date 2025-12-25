# 🚀 Eitaa Intelligent Crawler & Analyzer
این پروژه یک پایپ‌لاین هوشمند برای جستجو، استخراج و تحلیل داده‌های پیام‌رسان ایتا (Eitaa) است. سیستم با استفاده از پروتکل اختصاصی ایتا جستجو را انجام داده، کانال‌های مرتبط را پیدا می‌کند و با استفاده از هوش مصنوعی (Groq/Llama3) تشخیص می‌دهد که آیا کانال مورد نظر فروشگاه است یا خیر. در نهایت داده‌های تایید شده در دیتابیس MongoDB ذخیره می‌شوند.

# 🛠 معماری سیستم
این سیستم از پنج بخش اصلی تشکیل شده است که به صورت موازی (Asynchronous logic) با هم در ارتباط هستند:

Main Finder Engine: وظیفه جستجوی کلمات کلیدی استراتژیک و یافتن یوزرنیم‌های جدید را دارد.

AI Shop Detector: در مرحله اول، محتوای کانال را بررسی کرده و در صورت تایید "فروشگاه بودن"، آن را به صف پردازش می‌فرستد.

AI Product Processor: (جدید) به عنوان مغز متفکر میانی، پست‌ها را تحلیل کرده و جزئیات محصول (نام، قیمت، سایز و...) را استخراج می‌کند. این بخش دارای مدیریت هوشمند Rate Limit برای Groq است.

Redis Buffer: مدیریت دو صف مجزا (CHANNELS_QUEUE و PRODUCTS_QUEUE) برای تضمین عدم گم شدن داده‌ها.

Database Worker: ورکر نهایی که داده‌های پارس شده را در MongoDB ذخیره می‌کند.

# 📂 ساختار پروژه
```plaintext
.
├── main.py              # موتور اصلی جستجو و مدیریت پروسس‌ها
├── processor.py         # ورکر استخراج محصولات (AI Detail Extractor)
├── worker.py            # ورکر ذخیره‌سازی داده در MongoDB
├── analyzer.py          # هسته تعامل با Groq API و مدیریت کلاینت AI
├── scraper.py           # هندلر پروتکل ایتا و استخراج داده‌های خام
├── cache_service.py     # سرویس مرکزی مدیریت Redis و صف‌ها
├── session_service.py   # مدیریت چرخش حساب‌ها (Session Rotation)
├── docker-compose.yaml  # زیرساخت Redis و MongoDB
└── doc/                 # گزارشات لحظه‌ای و فایل‌های لاگ JSON
```

# ⚙️ پیش‌نیازها
Python 3.13+

Docker & Docker Compose

Groq API Key (برای پردازش هوش مصنوعی)

uv (پیشنهادی برای مدیریت پکیج‌ها)

# 🚀 راهنمای راه‌اندازی و اجرا
۱. تنظیمات محیطی (Environment Variables)
ابتدا فایل .env.example را به .env تغییر نام دهید و مقادیر را بر اساس نیاز خود پر کنید:

``` 
# Eitaa Config
EITAA_TOKEN=your_token_here,your_token_here2
EITAA_USER_ID=your_id_here,your_id_here2
EITAA_PROXIES=proxy1,proxy2

# AI Config
GROQ_API_KEY=gsk_your_key
SOCKS_PROXY=socks5://127.0.0.1:1080  # الزامی برای دسترسی به Groq

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_QUEUE=eitaa_products_queue          # صف نهایی برای مونگو
REDIS_CHANNELS_QUEUE=eitaa_channels_queue   # صف میانی برای پردازش AI

# MongoDB
MONGO_URI=mongodb://admin:password123@localhost:27017/
MONGO_DB_NAME=eitaa_db
MONGO_COLLECTION=products
```

۲. بالا آوردن سرویس‌های دیتابیس (Docker)
دیتابیس‌ها و رابط‌های کاربری آن‌ها را با یک دستور اجرا کنید:

```
docker-compose up -d
```

Mongo Express (UI): http://localhost:8081 (User: admin, Pass: pass)

Redis Insight (UI): http://localhost:5540

۳. نصب وابستگی‌ها
اگر از uv استفاده می‌کنید (پیشنهادی):
```
اگر از uv استفاده می‌کنید:
uv sync

اگر از pip استفاده می‌کنید:
uv export --format requirements-txt > requirements.txt
pip install -r requirements.txt
```

۴. اجرای پایپ‌لاین
کافیست فایل اصلی را اجرا کنید. این فایل به صورت خودکار Worker را در یک پروسس جداگانه بالا آورده و سپس از شما Keyword جستجو را می‌پرسد:

```
python main.py
```

# 🔍 نحوه کارکرد بخش‌ها
Scraper: ارسال درخواست‌های باینری به ایتا، استخراج یوزرنیم‌های خام و جمع‌آوری Bio/Posts.

Detector (Analyzer): فیلتر اول AI برای تشخیص ماهیت کانال؛ اگر فروشگاه باشد، آن را به صف CHANNELS_QUEUE می‌فرستد.

Processor: مغز متفکر سیستم؛ پست‌ها را از صف برداشته، جزئیات محصول (قیمت، نام و...) را استخراج و به صف PRODUCTS_QUEUE منتقل می‌کند.

Worker: مصرف‌کننده نهایی؛ محصولات آماده را از صف برداشته و در MongoDB ذخیره می‌کند (با قابلیت بازیابی در صورت خطا).

Session Service: مدیریت چرخش اکانت‌ها و پروکسی‌ها برای دور زدن محدودیت‌های نرخ درخواست (Rate Limit).

# 📝 گزارش‌گیری
خروجی‌ها علاوه بر دیتابیس، در فولدر doc نیز ذخیره می‌شوند:

channel_info.json: جزییات استخراج شده (Bio/Posts).

analysis.json: تحلیل‌های متنی هوش مصنوعی.

raw_response.txt: پاسخ خام شبکه جهت عیب‌یابی.

# ⚠️ نکات مهم
Proxy: به دلیل تحریم‌های API، حتماً از صحت کانکشن SOCKS_PROXY برای بخش Groq اطمینان حاصل کنید.