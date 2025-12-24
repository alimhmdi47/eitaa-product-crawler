def analyze_with_groq(client, username, bio, posts):
    # آماده‌سازی داده‌ها برای تحلیل توسط هوش مصنوعی
    clean_bio = str(bio)[:300].replace('{', '').replace('}', '')
    clean_posts = " | ".join([str(p)[:200] for p in posts[:5]]).replace('{', '').replace('}', '')
    
    # دستور به زبان فارسی برای دریافت تحلیل فارسی
    prompt = prompt = f"""
    Act as a Professional Data Validator. Analyze the following Eitaa channel data:
    Username: @{username}
    Bio: {clean_bio}
    Last Posts: {clean_posts}
    
    Task: Is this a physical product shop?
    Check for: Price (تومان/هزار), Admin ID for orders, shipping info.
    Answer Just by YES or NO + a short Persian reason. """
    
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
    
def generate_advanced_keywords(client):
    prompt = """
    You are a Senior Data Scientist specializing in Iranian E-commerce Discovery. 
    Your mission: Generate 25 high-yield search terms to find Eitaa shopping channels.
    
    CRITICAL INSTRUCTIONS:
    1. NO Underscores. Use natural Persian spacing.
    2. Focus on "Short-Tail" keywords (2-3 words max).
    3. Use keywords that appear in CHANNEL NAMES, not sentences.
    4. Categories: Clothing, Cosmetics, Home Appliances, Digital Goods, Accessories.
    
    STRATEGIC WORD LIST (Mix these):
    - Shop Terms: (آنلاین شاپ, فروشگاه, گالری, ارزان سرا, مزون, پخش, عمده, تک)
    - Product Roots: (پوشاک, کیف و کفش, لباس, لوازم خانگی, آرایشی, بدلیجات, موبایل)
    - Trust Signals: (ثبت سفارش, ارسال به سراسر کشور, واریزی, موجودی)

    OUTPUT FORMAT: Return ONLY the Persian keywords separated by commas. No intro/outro.
    """
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional Persian SEO & Market Analyst."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
        )
        return [k.strip() for k in response.choices[0].message.content.split(',')]
    except Exception as e:
        print(f"AI Keyword Error: {e}")
        return ["پوشاک", "آرایشی", "لوازم خانگی"]
    

