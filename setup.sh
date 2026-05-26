#!/bin/bash

# ۱. بروزرسانی سرور و نصب پایتون
echo "🔄 در حال بروزرسانی سرور و نصب پایتون..."
sudo apt update && sudo apt install -y python-is-python3 python3-pip

# ۲. نصب کتابخانه‌های پایتون
echo "📦 در حال نصب کتابخانه‌های پایتون..."
pip install -r requirements.txt

# ۳. نصب مرورگر کرومیوم و وابستگی‌های محیطی Playwright
echo "🌐 در حال نصب مرورگر Playwright و پیش‌نیازهای لینوکس..."
playwright install chromium
playwright install-deps

echo "✅ تمام پیش‌نیازها با موفقیت نصب شدند!"
