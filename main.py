import telebot
import requests
import schedule
import time
import threading
from dotenv import load_dotenv
import os
from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot is running"

def run():
   
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()


load_dotenv() 
API_TOKEN = os.getenv("BOT_TOKEN") 
CHAT_ID = os.getenv("CHAT_ID")    

bot = telebot.TeleBot(API_TOKEN)
GOLD_API_URL = "https://api.tgju.org/v1/market/indicator/summary-table-data/geram18"


import requests
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup

def get_gold_price():
    """گرفتن نرخ فعلی طلا مستقیم از سایت TGJU"""
    url = "https://www.tgju.org/"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # پیدا کردن المانی که دقیقاً نرخ فعلی (اون عدد بزرگ) رو داره
            # توی سایت TGJU این تگ با ویژگی data-col="info_last" مشخص میشه
            price_element = soup.find('span', {'data-col': 'info_last', 'data-market-row': 'geram18'})
            
            if price_element:
                # گرفتن متن و پاک کردن کاماها
                raw_price = price_element.text.strip()
                clean_price = int(raw_price.replace(',', ''))
                
                # تبدیل ریال به تومان (تقسیم بر ۱۰)
                price_toman = clean_price // 10
                return f"{price_toman:,}"
                
            # اگر تگ span پیدا نشد، شاید توی تگ td باشه (بک‌آپ)
            row = soup.find('tr', {'data-market-row': 'geram18'})
            if row:
                # اون عدد بزرگ معمولا توی دومین td با کلاس info_last هست
                td = row.find('td', {'class': 'info_last'})
                if td:
                    clean_price = int(td.text.strip().replace(',', ''))
                    return f"{(clean_price // 10):,}"

            return "قیمت فعلی پیدا نشد"
        else:
            return f"خطای سرور: {response.status_code}"
            
    except Exception as e:
        return f"خطای اتصال: {e}"
def job():
    print("در حال دریافت قیمت...")
    price = get_gold_price()
    message = f"💰 قیمت لحظه‌ای طلا (۱۸ عیار):\n{price} تومان"
    
    
    if CHAT_ID:
        try:
            bot.send_message(CHAT_ID, message)
            print(f"ارسال شد: {price} تومان")
        except Exception as e:
            print(f"خطا در ارسال: {e}")


def run_scheduler():
    schedule.every(60).minutes.do(job)
   
    job() 
    
    while True:
        schedule.run_pending()
        time.sleep(1)


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "سلام! ربات قیمت طلا روشن شد. هر یک ساعت خودم قیمت رو می‌فرستم.")
    
    global CHAT_ID
    CHAT_ID = message.chat.id

@bot.message_handler(commands=['price'])
def send_price(message):
    price = get_gold_price()
    bot.send_message(message.chat.id, f"💰 قیمت لحظه‌ای طلا:\n{price} تومان")


if __name__ == "__main__":
    print("ربات در حال روشن شدن...")
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    keep_alive()
    bot.infinity_polling()
