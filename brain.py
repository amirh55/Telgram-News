import os
import json
import time  # اضافه شدن کتابخانه زمان برای مدیریت تاخیرها
from typing import Optional
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# ... بقیه کدهای ابتدای فایل و کلاس NewsAnalysis دست‌نخورده باقی می‌مانند ...

def analyze_news(source_name: str, news_content: str) -> Optional[dict]:
    prompt = f"""
    تو یک سردبیر خبر ارشد و مسلط به امور ایران و خاورمیانه هستی.
    متن زیر را از منبع "{source_name}" بررسی کن:
    \"\"\"{news_content}\"\"\"
    
    با معیارهای زیر بسنج:
    ۱. ربط به ایران؟ ۲. اثر اقتصادی؟ ۳. ترند شدن در توییتر فارسی؟ ۴. جذابیت مخاطب؟ ۵. حس خبر مهم؟ ۶. پوشش همزمان رسانه‌ها؟ ۷. قابلیت تحلیل؟
    
    اگر مرتبط بود، is_relevant را true کن و بقیه فیلدها را به زبان فارسی روان و بدون حشو پر کن.
    اگر مرتبط نبود، is_relevant را false بگذار.
    """
    
    # تلاش مجدد تا ۳ بار در صورت برخورد با محدودیت سرعت گوگل
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=NewsAnalysis,
                    temperature=0.2,
                ),
            )
            
            data = json.loads(response.text)
            
            if not data.get("is_relevant"):
                return None
                
            formatted_output = {
                "urgent": f"{source_name}: {data['short_urgent']}",
                "full_report": (
                    f"📌 **خلاصه خبر:** {data['summary']}\n\n"
                    f"💡 **چرا مهم است:** {data['why_important']}\n\n"
                    f"💬 **واکنش‌ها:** {data['reactions']}\n\n"
                    f"📊 **اثر احتمالی:** {data['potential_effect']}\n\n"
                    f"🔹 [{source_name}]\n"
                    f"📰 [{data['short_title']}]\n"
                    f"📝 [{data['one_line_explanation']}]"
                )
            }
            return formatted_output
            
        except Exception as e:
            error_str = str(e)
            # اگر خطا مربوط به محدودیت تعداد درخواست (Rate Limit) بود
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                print(f"⏳ به سقف درخواست‌های رایگان گوگل رسیدیم. ۴۵ ثانیه خواب هوشمند برای آزاد شدن خط... (تلاش {attempt + 1} از ۳)")
                time.sleep(45)
                continue  # رفتن به تلاش بعدی بعد از ۴۵ ثانیه استراحت
            else:
                print(f"❌ خطا در پردازش هوش مصنوعی: {e}")
                return None
                
    print("❌ پس از ۳ بار تلاش، ارتباط با جمی‌نای به دلیل محدودیت شدید برقرار نشد.")
    return None
