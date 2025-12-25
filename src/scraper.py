import requests
import re

def build_eitaa_payload(token, query, imei):
    # ساخت دیتای باینری برای پروتکل اختصاصی ایتا
    print(imei)
    header = b"\xed\x77\xbe\x7a\x1f" + token.encode() + b"\x14" + imei.encode() + b"\x00\x00\x00\x2c\x10\xac\x6c\x2a\x00\x00\x04\x00"
    content = query.encode("utf-8")
    length = len(content)
    size_header = bytes([length]) if length <= 253 else b"\xfe" + length.to_bytes(3, 'little')
    body = size_header + content
    body += b"\x00" * ((4 - (len(body) % 4)) % 4)
    footer = b"\x00\x00\x00\x00\x00\xea\x18\x3b\x7f\x00\x00\x00\x0f\x00\x00\x00\x87\x00\x00\x80\x00\x00"
    return header + body + footer

def get_channel_details(username):
    # دریافت بیوگرافی و ۱۰ پست آخر از وب‌سایت ایتا
    try:
        url = f"https://eitaa.com/{username}"
        res = requests.get(url, timeout=10)
        bio_match = re.search(r'<div class="etme_channel_info_description".*?>(.*?)</div>', res.text, re.DOTALL)
        bio = bio_match.group(1).strip() if bio_match else "بدون بیوگرافی"
        post_blocks = re.findall(r'<div class="etme_widget_message_wrap.*?>(.*?)<div class="etme_widget_message_footer', res.text, re.DOTALL)
        posts = []
        for block in post_blocks:
            text_match = re.search(r'<div class="etme_widget_message_text.*?>(.*?)</div>', block, re.DOTALL)
            text = re.sub(r'<.*?>', '', text_match.group(1)).strip() if text_match else ""
            image_match = re.search(r'background-image:url\(\'(.*?)\'\)', block)
            image_url = image_match.group(1) if image_match else None
            if text or image_url:
                posts.append({"text": text, "image": image_url})
        return {"bio": bio, "posts": posts[-10:]}
    except Exception as e:
        print(f"Scraper Error: {e}")
        return None

def extract_clean_usernames(raw_stream):
    final_map = {}
    
    blacklist = {
        'eitaa', 'video', 'html', 'https', 'utf8', 'none', 'joinchat', 
        'search', 'mp4', 'jfif', 'lavc', 'android', 'index', 'view'
    }

    patterns = [
        r'@([A-Za-z0-9_]{5,32})',                             # @username
        r'eitaa\.com/([A-Za-z0-9_]{5,32})',                   # eitaa.com/username
        r'url=https://eitaa\.com/([A-Za-z0-9_]{5,32})'        # search links
    ]
    
    for pattern in patterns:
        found = re.findall(pattern, raw_stream)
        for u in found:
            u_low = u.lower()
            if u_low not in blacklist and not u.isdigit() and len(u) >= 5:
                if u not in final_map:
                    final_map[u] = {"channel_name": "استخراج شده از متن"}

    binary_contacts = re.findall(r'([\u0600-\u06FF\s]{3,40})[\x00-\x20]+([A-Za-z][A-Za-z0-9_]{4,31})', raw_stream)
    
    for name, user in binary_contacts:
        u = user.strip()
        n = name.strip()
        u_low = u.lower()
        
        if u_low not in blacklist and not u.isdigit():
            if len(n) > 2:
                final_map[u] = {"channel_name": n}

    return final_map