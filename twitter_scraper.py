import asyncio
import json
import os
from playwright.async_api import async_playwright
from database import is_new_story
from brain import analyze_news

# لیست اکانت‌های توییتر که مایل به پایش آن‌ها هستید
TWITTER_ACCOUNTS = [
    "IranIntl",
    "IranIntlbrk",
    "AlArabiya_Fa",
    "AlArabiya",
    "AJArabic",
    "AlHadath"
]

async def scrape_twitter():
    print("🐦 شروع پایش توییتر (X)...")
    
    if not os.path.exists("cookies.json"):
        print("❌ خطا: فایل cookies.json یافت نشد! ابتدا کوکی اکانت خود را قرار دهید.")
        return

    async with async_playwright() as p:
        # باز کردن مرورگر کرومیوم به صورت مخفی و بهینه برای رم ۲ گیگابایتی
        browser = await p.chromium.launch(headless=True, args=["--disable-gpu", "--no-sandbox"])
        
        # ساخت یک ستاپ با لود کردن کوکی‌های اکانت شما
        context = await browser.new_context(storage_state="cookies.json")
        page = await context.new_page()
        
        for account in TWITTER_ACCOUNTS:
            try:
                url = f"https://x.com/{account}"
                print(f"📥 در حال بررسی توییتر: {account}")
                
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                # یک مکث کوتاه برای بارگذاری کامل توییت‌ها
                await asyncio.sleep(4)
                
                # پیدا کردن باکس‌های مربوط به توییت‌ها
                tweets = await page.query_selector_all('article[data-testid="tweet"]')
                
                # بررسی ۳ توییت اخیر برای سرعت بیشتر و مصرف رم کمتر
                for tweet in tweets[:3]:
                    # ۱. استخراج شناسه یا لینک یکتای توییت برای دیتابیس
                    links = await tweet.query_selector_all('a[href*="/status/"]')
                    if not links:
                        continue
                    tweet_href = await links[0].get_attribute("href")
                    tweet_url = f"https://x.com{tweet_href}"
                    
                    # ۲. چک کردن تکراری نبودن توییت
                    if not is_new_story(tweet_url):
                        continue # اگر قبلاً بررسی شده بود، برو توییت بعدی
                        
                    # ۳. استخراج متن توییت
                    text_element = await tweet.query_selector('div[data-testid="tweetText"]')
                    tweet_text = await text_element.inner_text() if text_element else ""
                    
                    if not tweet_text:
                        continue
                    
                    # ۴. استخراج تصاویر (مدیریت چند عکسی در یک پست)
                    media_elements = await tweet.query_selector_all('div[data-testid="tweetPhoto"] img')
                    image_urls = []
                    for img in media_elements:
                        img_src = await img.get_attribute("src")
                        if img_src and "card_img" not in img_src: # فیلتر کردن تصاویر نامربوط
                            image_urls.append(img_src)
                    
                    print(f"✨ توییت جدید یافت شد. تعداد عکس‌ها: {len(image_urls)}")
                    
                    # ۵. ارسال متن به Gemini جهت پردازش هوشمند
                    analysis_result = analyze_news(account, tweet_text)
                    
                    if analysis_result:
                        print(f"✅ توییت توسط Gemini تایید شد!")
                        print(f"📢 خروجی آماده: {analysis_result['urgent']}")
                        print(f"🖼️ لینک عکس‌ها برای آلبوم تلگرام: {image_urls}\n")
                        # در مرحله بعدی اطلاعات و لیست عکس‌ها به ربات تلگرام فرستاده می‌شوند
                        
            except Exception as e:
                print(f"❌ خطا در پایش اکانت {account}: {e}")
                
        # بستن کامل مرورگر برای آزاد شدن فوری رم سرور
        await browser.close()

if __name__ == "__main__":
    # اجرای اسکرپر توییتر
    asyncio.run(scrape_twitter())
