import os
import json
from typing import Optional
import google-generativeai as genai
from pydantic import BaseModel, Field
from dotenv import load_dotenv

def setup_environment():
    """
    این تابع در اولین اجرا روی سرور، فایل .env را در صورت عدم وجود می‌سازد
    و کلیدهای امنیتی را از کاربر در ترمینال دریافت می‌کند.
    """
    env_file = ".env"
    if not os.path.exists(env_file):
        print("⚠️ فایل تنظیمات (.env) یافت نشد. در حال راه‌اندازی اولیه...")
        gemini_key = input("🔑 لطفاً Gemini API Key خود را وارد کنید: ").strip()
        
        # در فازهای بعدی توکن تلگرام و کوکی توییتر هم به همینجا اضافه می‌شوند
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"GEMINI_API_KEY={gemini_key}\n")
        print("✅ فایل .env با موفقیت ساخته شد.\n")

# اجرای خودکار تنظیمات قبل از شروع برنامه
setup_environment()
load_dotenv()

# پیکربندی هوش مصنوعی
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# تعریف ساختار داده برای هوش مصنوعی
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
    """
    تحلیل متن خبر و تولید دو خروجی فوری و کامل بر اساس ساختار درخواستی.
    """
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": NewsAnalysis,
            "temperature": 0.2
        }
    )
    
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
        response = model.generate_content(prompt)
        data = json.loads(response.text)
        
        if not data.get("is_relevant"):
            return None
            
        # قالب‌بندی نهایی خروجی‌ها دقیقاً طبق ساختار درخواستی کاربر
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

# --- تست زنده خروجی مطبوعاتی رویترز ---
if __name__ == "__main__":
    sample_news = "Reuters: Oil prices jumped 3% today following new geopolitical tensions in the Middle East and threats to shipping lanes in the Persian Gulf."
    
    print("⏳ در حال تحلیل خبر نمونه رویترز...")
    output = analyze_news("رویترز", sample_news)
    
    if output:
        print("\n" + "="*20 + " خروجی کوتاه فوری " + "="*20)
        print(output["urgent"])
        
        print("\n" + "="*20 + " خروجی کامل تلگرامی " + "="*20)
        print(output["full_report"])
    else:
        print("❌ خبر به ایران مرتبط تشخیص داده نشد.")
