#!/bin/bash

# ۱. بروزرسانی سرور و نصب پایتون
echo "🔄 در حال بروزرسانی سرور و نصب پایتون..."
sudo apt update && sudo apt install -y python-is-python3 python3-pip

# ۲. نصب کتابخانه‌های پایتون از روی فایل requirements
echo "📦 در حال نصب کتابخانه‌های پایتون..."
pip install -r requirements.txt

echo "✅ تمام پیش‌نیازها با موفقیت نصب شدند!"
echo "🚀 حالا می‌توانید با دستور 'python brain.py' برنامه را اجرا کنید."
