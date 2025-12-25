import requests
import re

def build_eitaa_payload(token, query):
    # ساخت دیتای باینری برای پروتکل اختصاصی ایتا
    header = b"\xed\x77\xbe\x7a\x1f" + token.encode() + b"\x14mggbh3ndmw1mj7d__web\x00\x00\x00\x2c\x10\xac\x6c\x2a\x00\x00\x04\x00"
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
    
import re

def extract_clean_usernames(raw_stream):
    usernames_with_at = re.findall(r'@([A-Za-z0-9_]{3,})', raw_stream)

    contact_pairs = re.findall(r'([\u0600-\u06FF\s]{3,30}).*?([A-Za-z0-9_]{5,32})', raw_stream)
    
    blacklist = {'EITAA_TOKEN', 'SOCKS_PROXY', 'video', 'html', 'https', 'UTF8', 'None'}
    
    final_map = {}

    for u in usernames_with_at:
        if u not in blacklist and not u.isdigit():
            final_map[u] = {"channel_name": "نامشخص"}

    for name, user in contact_pairs:
        u = user.strip()
        n = name.strip()
        if u not in blacklist and not u.isdigit() and len(n) > 2:
            final_map[u] = {"channel_name": n}

    return final_map