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
        messages = re.findall(r'<div class="etme_widget_message_text.*?>(.*?)</div>', res.text, re.DOTALL)
        posts = [re.sub(r'<.*?>', '', m).strip() for m in messages]
        return {"bio": bio, "posts": posts[-10:]}
    except:
        return None