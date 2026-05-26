import feedparser
from database import is_new_story
from brain import analyze_news
from telegram_sender import send_to_telegram

# لیست فیدهای RSS منابع شما (می‌توانید منابع خبری بیشتری را هم به همین شکل اضافه کنید)
RSS_FEEDS = {
    "خبرگزاری فارس": "https://www.farsnews.ir/rss",
    "خبرگزاری تسنیم": "https://www.tasnimnews.com/fa/rss",
    "خبرگزاری ایرنا": "https://www.irna.ir/rss",
    "رویترز": "https://www.reutersagency.com/feed/",
}

def check_websites():
    """بررسی تمام سایت‌ها، فیلتر با هوش مصنوعی و ارسال خودکار به تلگرام"""
    print("🌐 شروع پایش وب‌سایت‌های خبری...")
    
    for source_name, url in RSS_FEEDS.items():
        try:
            print(f"📥 در حال بررسی: {source_name}")
            feed = feedparser.parse(url)
            
            # بررسی ۵ خبر آخر هر سایت برای سرعت بیشتر و مصرف کمتر رم سرور
            for entry in feed.entries[:5]:
                news_link = entry.link
                news_title = entry.title
                
                # برخی سایت‌ها متن کامل را در summary می‌گذارند، برخی فقط تیتر دارند
                news_content = entry.get("summary", news_title) 
                
                # ۱. چک کردن تکراری نبودن لینک در دیتابیس
                if is_new_story(news_link):
                    print(f"✨ خبر جدید یافت شد: {news_title}")
                    
                    # ۲. فرستادن به مغز ربات (Gemini) برای ارزیابی و ساخت خروجی
                    analysis_result = analyze_news(source_name, news_content)
                    
                    if analysis_result:
                        print(f"✅ خبر توسط Gemini تایید شد! در حال شلیک به تلگرام...")
                        
                        # ۳. ارسال گزارش ساختاریافته و کامل به کانال تلگرام
                        send_to_telegram(analysis_result['full_report'])
                    else:
                        print("⏭️ خبر به ایران مرتبط نبود و رد شد.")
                else:
                    # خبر تکراری است، بیخیال می‌شویم
                    continue
                    
        except Exception as e:
            print(f"❌ خطا در پایش سایت {source_name}: {e}")

if __name__ == "__main__":
    # اجرای اسکرپر به صورت تست مستقل
    check_websites()
