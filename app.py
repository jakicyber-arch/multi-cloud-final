import threading
import time
import re
import json
import os
import random
import telebot
from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# DEIN NEUER GODDROP BOT TOKEN
BOT_TOKEN = '8980059554:AAGi4797fL5HA4HIfFO74HFhEEmt6A2OoUQ'
bot = telebot.TeleBot(BOT_TOKEN)

# DEINE SUPABASE DATEN
SUPABASE_URL = "https://drrbibjafmqcxqhxswfy.supabase.co" 
SUPABASE_KEY = "sb_secret_8v78Z65NYG5BHQvCciywbQ_KSUWQuO_"

def get_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

TELEGRAM_CHANNELS = ["freetohell", "Crackers_Official", "internettweaksforum", "netflix_disney_hotstar_nord", "mrplan254", "DARKNET240", "PremiumAccounts_Free", "Combos"]
REDDIT_SUBS = ["accountsharing", "AccountShare", "subscriptionsharing"]

PATTERN = re.compile(r'((?:NetflixId|SecureNetflixId|sp_dc|sp_key|token)=[^;]+)', re.IGNORECASE)

def grabber_loop():
    while True:
        found_raw = []
        for channel in TELEGRAM_CHANNELS:
            try:
                r = requests.get(f"https://t.me/s/{channel}", timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                for m in PATTERN.findall(r.text):
                    if m and m not in found_raw: found_raw.append(m)
            except: pass

        if found_raw:
            for item in found_raw:
                if SUPABASE_URL and SUPABASE_KEY:
                    newKey = 'CLM-' + os.urandom(4).hex().upper()
                    meta = {"email": "Token Login", "password": None, "country": "Unknown", "plan": "Premium", "profiles": []}
                    requests.post(f"{SUPABASE_URL}/rest/v1/keys", headers=get_headers(), json={"key": newKey, "data": item, "metadata": meta, "used": False, "platform": "netflix"})
        time.sleep(60)

def bot_loop():
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "Willkommen bei GodDrop!\nSende /key netflix oder /key spotify")

    @bot.message_handler(commands=['key'])
    def send_key(message):
        try:
            args = message.text.split()
            platform = args[1].lower() if len(args) > 1 else "netflix" 
            r = requests.get(f"{SUPABASE_URL}/rest/v1/keys?data=not.is.null&used=eq.false&platform=eq.{platform}&limit=1", headers=get_headers())
            if r.status_code == 200 and r.json():
                bot.reply_to(message, f"Dein {platform.capitalize()} Key: `{r.json()[0]['key']}`\n\nLöse ihn ein: https://multi-cloud-final.onrender.com", parse_mode='Markdown')
            else:
                bot.reply_to(message, f"❌ Keine {platform.capitalize()} Accounts verfügbar.")
        except Exception as e: bot.reply_to(message, f"Fehler: {e}")
    bot.polling(none_stop=True)

threading.Thread(target=grabber_loop, daemon=True).start()
threading.Thread(target=bot_loop, daemon=True).start()

@app.route('/')
def home(): return render_template('index.html')

@app.route('/api/claim', methods=['POST'])
def claim():
    data = request.json
    r = requests.get(f"{SUPABASE_URL}/rest/v1/keys?key=eq.{data.get('key')}&used=eq.false&data=not.is.null", headers=get_headers())
    if r.status_code == 200 and r.json():
        k = r.json()[0]
        requests.patch(f"{SUPABASE_URL}/rest/v1/keys?id=eq.{k['id']}", headers=get_headers(), json={"used": True})
        return jsonify({"success": True, "data": k['data'], "meta": k['metadata'], "platform": k.get('platform', 'unknown')})
    return jsonify({"success": False, "msg": "Key ungültig oder leer!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
