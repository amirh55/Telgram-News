import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

def send_to_telegram(text: str, images: list = None):
    """
    ارسال هوشمند محتوا به تلگرام. 
    اگر عکس داشته باشد به صورت آلبوم یا تک عکس، و اگر نداشته باشد به صورت متن ساده می‌فرستد.
    """
    if not BOT_TOKEN or not CHANNEL_ID:
        print("⚠️ خطا: توکن تلگرام یا آیدی کانال در فایل .env تنظیم نشده است.")
        return False

    # حالت اول: پست حاوی تصویر است
    if images and len(images) > 0:
        # اگر فقط یک عکس بود
        if len(images) == 1:
            url = f"https://api.telegram.com/bot{BOT_TOKEN}/sendPhoto"
            payload = {
                "chat_id": CHANNEL_ID,
                "photo": images[0],
                "caption": text,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=payload)
        
        # اگر چند عکس بود (ارسال به صورت آلبوم تصویری)
        else:
            url = f"https://api.telegram.com/bot{BOT_TOKEN}/sendMediaGroup"
            media = []
            for i, img_url in enumerate(images[:10]): # تلگرام حداکثر ۱۰ عکس در یک آلبوم قبول می‌کند
                media.append({
                    "type": "photo",
                    "media": img_url,
                    "caption": text if i == 0 else "", # متن فقط روی عکس اول آلبوم بیفتد
                    "parse_mode": "Markdown"
                })
            payload = {
                "chat_id": CHANNEL_ID,
                "media": media
            }
            response = requests.post(url, json=payload)
            
    # حالت دوم: پست فقط متن ساده است
    else:
        url = f"https://api.telegram.com/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL_ID,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        response = requests.post(url, json=payload)

    # بررسی وضعیت ارسال
    if response.status_code == 200:
        print("🚀 پست با موفقیت به کانال تلگرام ارسال شد.")
        return True
    else:
        print(f"❌ خطا در ارسال به تلگرام: {response.text}")
        return False
