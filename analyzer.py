def analyze_with_groq(client, username, bio, posts):
    # آماده‌سازی داده‌ها برای تحلیل توسط هوش مصنوعی
    clean_bio = str(bio)[:300].replace('{', '').replace('}', '')
    clean_posts = " | ".join([str(p)[:200] for p in posts[:5]]).replace('{', '').replace('}', '')
    
    # دستور به زبان فارسی برای دریافت تحلیل فارسی
    prompt = f"Is @{username} a shop? Bio: {clean_bio}. Posts: {clean_posts}. Answer with YES/NO? + a short Persian reason. "
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=100
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"AI Error: {str(e)[:40]}"