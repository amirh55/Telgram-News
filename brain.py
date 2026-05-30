import os
import json
import time
from typing import Optional
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# تعریف ساختار خروجی هوشمند برای دیتای ارسالی به تلگرام
class NewsAnalysis(BaseModel):
    is_relevant: bool = Field(description="آیا خبر بر اساس ۷ معیار به ایران مرتبط است؟")
    short_urgent: Optional[str] = Field(description="متن کوتاه خبر فوری بدون نام منبع")
    summary: Optional[str] = Field(description="خلاصه خبر")
    why_important: Optional[str] = Field(description="چرا این خبر مهم است")
    reactions: Optional[str] = Field(description="واکنش‌ها به این خبر")
    potential_effect: Optional[str] = Field(description="اثر احتمالی خبر")
    short_title: Optional[str] = Field(description="تیتر کوتاه خبر")
    one_line_explanation: Optional[str] = Field(description="یک خط توضیح کلیدی")

def analyze_news(source_name: str, news_content: str) -> Optional[dict]:
    """تابع اصلی تحلیل خبر با کلاینت داخلی و مکانیزم ضد محدودیت سرعت"""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("⚠️ خطا: GEMINI_API_KEY در فایل .env یافت نشد!")
        return None

    prompt = f"""
    تو یک سردبیر خبر ارشد و مسلط به امور ایران و خاورمیانه هستی.
    متن زیر را از منبع "{source_name}" بررسی کن:
    \"\"\"{news_content}\"\"\"
    
    با معیارهای زیر بسنج:
    ۱. ربط به ایران؟ ۲. اثر اقتصادی؟ ۳. ترند شدن در توییتر فارسی؟ ۴. جذابیت مخاطب؟ ۵. حس خبر مهم؟ ۶. پوشش همزمان رسانه‌ها؟ ۷. قابلیت تحلیل؟
    
    اگر مرتبط بود، is_relevant را true کن و بقیه فیلدها را به زبان فارسی روان و بدون حشو پر کن.
    اگر مرتبط نبود، is_relevant را false بگذار.
    """
    
    # تلاش مجدد تا ۳ بار در صورت برخورد با محدودیت سرعت ۵ درخواست در دقیقه
    for attempt in range(3):
        try:
            # ساخت مستقیم کلاینت درون تابع برای جلوگیری از خطاهای Namespace لینوکس
            client = genai.Client(api_key=api_key)
            
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
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                print(f"⏳ به سقف درخواست‌های رایگان گوگل رسیدیم. ۴۵ ثانیه خواب هوشمند برای آزاد شدن خط... (تلاش {attempt + 1} از ۳)")
                time.sleep(45)
                continue
            else:
                print(f"❌ خطا در پردازش هوش مصنوعی: {e}")
                return None
                
    print("❌ پس از ۳ بار تلاش، ارتباط با جمی‌نای به دلیل محدودیت شدید برقرار نشد.")
    return None
