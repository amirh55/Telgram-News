import sqlite3

DB_NAME = "news_bot.db"

def init_db():
    """ایجاد جدول دیتابیس در صورتی که از قبل وجود نداشته باشد"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_key TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def is_new_story(news_key: str) -> bool:
    """
    چک می‌کند که آیا این خبر جدید است یا قبلاً پردازش شده؟
    اگر جدید باشد، آن را ذخیره کرده و True برمی‌گرداند.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO processed_news (news_key) VALUES (?)", (news_key,))
        conn.commit()
        return True # خبر جدید بود و ذخیره شد
    except sqlite3.IntegrityError:
        return False # خبر تکراری است
    finally:
        conn.close()

# اجرای اولیه برای ساخت دیتابیس
init_db()
