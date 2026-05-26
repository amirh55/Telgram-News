import feedparser
from database import is_new_story
from brain import analyze_news

# لیست فیدهای RSS منابع شما (برای نمونه چند مورد رو ست کردم، بقیه رو هم میتونی اضافه کنی)
RSS_FEEDS = {
    "خبرگزاری فارس": "https://www.farsnews.ir/rss",
    "خبرگزاری تسنیم": "https://www.tasnimnews.com/fa/rss",
    "خبرگزاری ایرنا": "https://www.irna.ir/rss",
    "رویترز": "https://www.reutersagency.com/feed/", # فید رسمی رویترز
}

def check_websites():
    """بررسی تمام سایت‌ها و فرستادن اخبار جدید به هوش مصنوعی"""
    print("🌐 شروع پایش وب‌سایت‌های خبری...")
    
    for source_name, url in RSS_FEEDS.items():
        try:
            print(f"📥 در حال بررسی: {source_name}")
            feed = feedparser.parse(url)
            
            # بررسی ۵ خبر آخر هر سایت برای اینکه سرور شلوغ نشود
            for entry in feed.entries[:5]:
                news_link = entry.link
                news_title = entry.title
                # برخی سایت‌ها متن کامل رو در summary می‌ذارن، برخی فقط تیتر دارن
                news_content = entry.get("summary", news_title) 
                
                # ۱. چک کردن تکراری نبودن لینک در دیتابیس
                if is_new_story(news_link):
                    print(f"✨ خبر جدید یافت شد: {news_title}")
                    
                    # ۲. فرستادن به مغز ربات (Gemini) برای ارزیابی و ساخت خروجی
                    analysis_result = analyze_news(source_name, news_content)
                    
                    if analysis_result:
                        print(f"✅ خبر تکراری نبود و توسط Gemini تایید شد!")
                        print(f"📢 آماده ارسال به تلگرام:\n{analysis_result['urgent']}\n")
                        # در مرحله ۴ اینجا کد ارسال به تلگرام قرار می‌گیرد
                    else:
                        print("⏭️ خبر به ایران مرتبط نبود و رد شد.")
                else:
                    # خبر تکراری است، بیخیال میشیم
                    continue
                    
        except Exception as e:
            print(f"❌ خطا در پایش سایت {source_name}: {e}")

if __name__ == "__main__":
    # اجرای اسکرپر به صورت تست
    check_websites()
