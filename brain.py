import os
import json
from typing import Optional
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

def setup_environment():
    env_file = ".env"
    if not os.path.exists(env_file):
        print("⚠️ فایل تنظیمات (.env) یافت نشد. در حال راه‌اندازی اولیه...")
        gemini_key = input("🔑 لطفاً Gemini API Key خود را وارد کنید: ").strip()
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"GEMINI_API_KEY={gemini_key}\n")
        print("✅ فایل .env با موفقیت ساخته شد.\n")

setup_environment()
load_dotenv()

# ساخت کلاینت جدید جمی‌نای بر اساس استاندارد جدید گوگل
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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
    prompt = f"""
    تو یک سردبیر خبر ارشد و مسلط به امور ایران و خاورمیانه هستی.
    متن زیر را از منبع "{source_name}" بررسی کن:
    \"\"\"{news_content}\"\"\"
    
    با معیارهای زیر بسنج:
    ۱. ربط به ایران؟ ۲. اثر اقتصادی؟ ۳. ترند شدن در توییتر فارسی؟ ۴. جذابیت مخاطب؟ ۵. حس خبر مهم؟ ۶. پوشش همزمان رسانه‌ها؟ ۷. قابلیت تحلیل؟
    
    اگر مرتبط بود، is_relevant را true کن و بقیه فیلدها را به زبان فارسی روان و بدون حشو پر کن.
    اگر مرتبط نبود، is_relevant را false بگذار.
    """
    
    try:
        # استفاده از متد و ساختار جدید ساختاریافته گوگل
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
        print(f"❌ خطا در پردازش هوش مصنوعی: {e}")
        return None
