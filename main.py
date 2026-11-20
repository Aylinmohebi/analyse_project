import telebot
import requests
import schedule
import time
import threading
from dotenv import load_dotenv
import os
from flask import Flask
from bs4 import BeautifulSoup
from threading import Thread


app = Flask('')

@app.route('/')
def home():
    return "Bot is running"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()


load_dotenv() 
API_TOKEN = os.getenv("BOT_TOKEN") 

CHAT_ID = os.getenv("CHAT_ID") 

bot = telebot.TeleBot(API_TOKEN)


def get_gold_price():
    url = "https://www.tgju.org/profile/geram18"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            price_element = soup.find('span', {'data-col': 'info.last_trade.PDrCotVal'})
            
            if price_element:
                raw_price = price_element.text.strip()
                clean_price = int(raw_price.replace(',', ''))
                price_toman = clean_price // 10
                return f"{price_toman:,}"
            
            
            row = soup.find('tr', {'data-market-row': 'geram18'})
            if row:
                td = row.find('td', class_='nf')
                if td:
                    clean_price = int(td.text.strip().replace(',', ''))
                    return f"{(clean_price // 10):,}"
                    
            return "قیمت پیدا نشد"
        else:
            return f"خطای سرور: {response.status_code}"
    except Exception as e:
        return f"خطای اتصال: {e}"


def job():
  
   
    price = get_gold_price()
    message = f"💰 قیمت لحظه‌ای طلا (۱۸ عیار):\n{price} تومان"
    
     
    if CHAT_ID:
        try:
            bot.send_message(CHAT_ID, message)
            print(f"پیام خودکار ارسال شد: {price} تومان")
        except Exception as e:
            print(f"خطا در ارسال خودکار: {e}")
    else:
        print("هنوز کسی /start نزده تا CHAT_ID داشته باشیم.")

def run_scheduler():
   
    schedule.every(120).minutes.do(job)
    
    
    
    
    while True:
        schedule.run_pending()
        time.sleep(1)


@bot.message_handler(commands=['start'])
def start_command(message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    bot.send_message(message.chat.id, "سلام! ربات قیمت طلا روشن شد. هر یک ساعت خودم قیمت رو می‌فرستم.")
    print(f"کاربر جدید start زد. Chat ID: {CHAT_ID}")

@bot.message_handler(commands=['price'])
def send_price(message):
    price = get_gold_price()
    bot.send_message(message.chat.id, f"💰 قیمت لحظه‌ای طلا:\n{price} تومان")


if __name__ == "__main__":
    print("ربات در حال روشن شدن...")
    
   
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    
    keep_alive()
    

    print("ربات با موفقیت روشن شد و منتظر پیام‌هاست.")
    bot.infinity_polling()
