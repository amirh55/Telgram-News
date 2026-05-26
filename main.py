import time
import asyncio
from site_scraper import check_websites
from twitter_scraper import scrape_twitter

# زمان استراحت ربات بین هر بار پایش (۶۰۰ ثانیه = ۱۰ دقیقه)
INTERVAL = 600 

def main():
    print("🚀 ربات هوشمند و هوش مصنوعی خبری فعال شد...")
    print("🤖 سیستم هر 10 دقیقه یک‌بار تمام منابع را پایش می‌کند.\n")
    
    while True:
        try:
            print(f"⏰ شروع چرخه پایش جدید در ساعت: {time.strftime('%H:%M:%S')}")
            
            # ۱. اجرای اسکرپر وب‌سایت‌ها
            check_websites()
            
            # ۲. اجرای اسکرپر توییتر (به دلیل async بودن با دستور زیر اجرا می‌شود)
            asyncio.run(scrape_twitter())
            
            print(f"🟢 چرخه با موفقیت پایان یافت. استراحت برای {INTERVAL // 60} دقیقه آینده...")
            time.sleep(INTERVAL)
            
        except Exception as e:
            # مدیریت خطاهای غیرمنتظره برای اینکه ربات هرگز کرش نکند و متوقف نشود
            print(f"❌ خطای غیرمنتظره در چرخه اصلی سیستم: {e}")
            print("⏳ سیستم ۱ دقیقه استراحت می‌کند و دوباره تلاش خواهد کرد...")
            time.sleep(60)

if __name__ == "__main__":
    main()
