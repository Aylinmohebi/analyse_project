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


def get_gold_price():
    """گرفتن قیمت طلا از TGJU"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        response = requests.get(GOLD_API_URL, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            gold_list = data.get("data", [])
            
            if gold_list:
                raw_price = gold_list[0][0] # مثلا "245,660,000"
                
                clean_price = int(raw_price.replace(",", ""))
                
             
                price_toman = clean_price // 10
                return f"{price_toman:,}"
            else:
                return "داده‌ای یافت نشد"
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
