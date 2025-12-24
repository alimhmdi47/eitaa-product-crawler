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
    You are a Senior Persian E-commerce & SEO Specialist. 
    Task: Generate 70 high-yield search terms for Eitaa shopping channels in Farsi(Persian).

    ### CRITICAL INSTRUCTION (ROOT + ATTRIBUTE):
    For every product you identify, you MUST provide two keywords:
    1. The "Base Product" name alone (e.g., 'مانتو').
    2. The "Combined Term" (e.g., 'مانتو کتی').
    Example: If you think of 'ساعت هوشمند', output: ساعت, ساعت هوشمند.

    ### STRICT RULES:
    1. NEVER use the Persian character "و" (and) to connect words.
    2. No intro, no outro, no numbers. Return ONLY Persian keywords separated by commas.
    3. Maximum 3 words per term.

    ### STRATEGIC CLUSTERS TO EXPAND (Root and then Combined):
    - Clothing: (پوشاک، ارزانسرای پوشاک، مانتو، مانتو کتی، شومیز، شومیز مجلسی، شلوار، شلوار اسلش، پالتو، پالتو فوتر)
    - Cosmetics: (آرایشی، پخش آرایشی، ریمل، ریمل حجم دهنده، رژ، رژ مدادی، سایه، پالت سایه)
    - Home: (آشپزخانه، لوازم آشپزخانه، روتختی، روتختی سه بعدی، قابلمه، سرویس قابلمه)
    - Digital: (موبایل، موبایل استوک، قاب، قاب گوشی، هندزفری، هندزفری بلوتوث، ساعت، ساعت هوشمند)
    - Jewelry: (بدلیجات، گالری بدلیجات، دستبند، دستبند استیل، گردنبند، گردنبند نقره)

    ### EXAMPLES OF BAD VS GOOD:
    - BAD: کیف و کفش، شال و روسری
    - GOOD: کیف، کیف چرم، کفش، کفش اسپرت
    """
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional market analyst. You provide raw Persian keyword lists without 'و'."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.8
        )
        
        content = response.choices[0].message.content
        # تمیزکاری نهایی برای اطمینان از فرمت خروجی
        raw_keywords = content.replace('،', ',').split(',')
        
        # فیلتر نهایی برای حذف کلماتی که احتمالا حرف "و" دارند یا خالی هستند
        final_keywords = [
            k.strip() for k in raw_keywords 
            if k.strip() and " و " not in k and "و " != k[:2]
        ]
        
        return final_keywords

    except Exception as e:
        print(f"AI Keyword Error: {e}")
        # لیست بک‌آپ استاندارد (بدون حرف "و")
        return ["مانتو مجلسی", "آرایشی عمده", "لوازم آشپزخانه", "گالری بدلیجات", "قاب گوشی"]