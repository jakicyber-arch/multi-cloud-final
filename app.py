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
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

BOT_TOKEN = '8980059554:AAGi4797fL5HA4HIfFO74HFhEEmt6A2OoUQ'
CHAT_ID = '6584278242'

try:
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1", timeout=5)
    time.sleep(2)
except: pass

bot = telebot.TeleBot(BOT_TOKEN)

SUPABASE_URL = "https://drrbibjafmqcxqhxswfy.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRycmJpYmphZm1xY3hxaHhzd2Z5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MzQ2NjQ2NiwiZXhwIjoyMTA5MDQyNDY2fQ.XElFDbLqZT_bbRP9EomuZlH7gbflUni46fvGvm9hleo"

def get_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

TELEGRAM_CHANNELS = ["freetohell", "Crackers_Official", "internettweaksforum", "netflix_disney_hotstar_nord", "mrplan254", "DARKNET240", "PremiumAccounts_Free", "Combos", "Netflix_Cookies", "Spotify_Premium", "FreeNetflixDaily", "Cookies_Netflix", "Netflix_Account_Drop", "Free_Account_Drop", "NetflixCookiesFree", "NetflixFreebies", "accountsharing", "streamingpartners", "Netflix_Drops", "Spotify_Accounts", "rtl_plus_free", "disney_plus_accounts", "crunchyroll_free"]

PATTERN = re.compile(r'(https?://(?:www\.)?netflix\.com/(?:tv2|browse)\?nftoken=[^\s]+)', re.IGNORECASE)

def scan_telegram(channel):
    found = []
    try:
        r = requests.get(f"https://t.me/s/{channel}", timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        for m in PATTERN.findall(r.text):
            if m and 'unsupported' not in m.lower(): found.append(m)
    except Exception: pass 
    return found

def scan_duckduckgo():
    found = []
    try:
        q = 'site:pastebin.com "nftoken="'
        r = requests.get(f"https://html.duckduckgo.com/html/?q={q}", timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.select('.result__a')[:5]:
            url = a['href']
            if 'pastebin.com' in url and '/raw/' not in url:
                raw_url = url.replace('pastebin.com/', 'pastebin.com/raw/')
                raw_r = requests.get(raw_url, timeout=5)
                if raw_r.status_code == 200:
                    for m in PATTERN.findall(raw_r.text):
                        if m and 'unsupported' not in m.lower(): found.append(m)
    except Exception: pass
    return found

def grabber_loop():
    while True:
        found_raw = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(scan_telegram, TELEGRAM_CHANNELS)
            for res in results: found_raw.extend(res)
        found_raw.extend(scan_duckduckgo())
        found_raw = list(set(found_raw)) 
        
        if found_raw:
            for item in found_raw:
                check = requests.get(f"{SUPABASE_URL}/rest/v1/keys?data=eq.{item}", headers=get_headers())
                if check.status_code == 200 and not check.json():
                    meta = {"email": "NFToken Link", "password": None, "country": "Unknown", "plan": "Premium", "profiles": []}
                    newKey = 'CLM-' + os.urandom(4).hex().upper()
                    requests.post(f"{SUPABASE_URL}/rest/v1/keys", headers=get_headers(), json={"key": newKey, "data": item, "metadata": meta, "used": False, "platform": "netflix"})
                    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": f"🚨 **NEUER NFToken!**\n\n{newKey}", "parse_mode": "Markdown"})
                    except: pass
        time.sleep(60)

def bot_loop():
    @bot.message_handler(commands=['start', 'key'])
    def send_key(message):
        try:
            # Sucht einen komplett neuen Key, der noch nie benutzt wurde
            r = requests.get(f"{SUPABASE_URL}/rest/v1/keys?data=not.is.null&used=eq.false&platform=eq.netflix&limit=1", headers=get_headers())
            if r.status_code == 200 and r.json():
                bot.reply_to(message, f"Dein Key: `{r.json()[0]['key']}`\n\nLöse ihn ein: https://multi-cloud-final.onrender.com", parse_mode='Markdown')
            else: bot.reply_to(message, "❌ Keine Links verfügbar.")
        except: pass
    bot.polling(non_stop=True)

threading.Thread(target=grabber_loop, daemon=True).start()
threading.Thread(target=bot_loop, daemon=True).start()

@app.route('/')
def home(): return render_template('index.html')

@app.route('/api/claim', methods=['POST'])
def claim():
    data = request.json
    key = data.get('key')
    
    # Prüft ob der Key existiert
    r = requests.get(f"{SUPABASE_URL}/rest/v1/keys?key=eq.{key}&data=not.is.null", headers=get_headers())
    if r.status_code == 200 and r.json():
        k = r.json()[0]
        # WICHTIG: 'used' wird hier NICHT auf True gesetzt. Der Key bleibt für immer gültig.
        return jsonify({"success": True, "data": k['data'], "platform": "netflix"})
        
    return jsonify({"success": False, "msg": "Key ungültig oder nicht gefunden!"})

@app.route('/api/replace', methods=['POST'])
def replace():
    data = request.json
    old_key = data.get('key')
    
    # 1. Finde einen komplett neuen Link, der nicht der alte ist
    r = requests.get(f"{SUPABASE_URL}/rest/v1/keys?data=not.is.null&used=eq.false&platform=eq.netflix&key=neq.{old_key}&limit=1", headers=get_headers())
    
    if r.status_code == 200 and r.json():
        new_acc = r.json()[0]
        new_link = new_acc['data']
        
        # 2. Update den alten Key mit dem neuen Link (Der Key bleibt für immer bestehen)
        requests.patch(f"{SUPABASE_URL}/rest/v1/keys?key=eq.{old_key}", headers=get_headers(), json={"data": new_link})
        
        # 3. Lösche den temporären neuen Key aus der DB, damit er nicht doppelt existiert
        requests.delete(f"{SUPABASE_URL}/rest/v1/keys?id=eq.{new_acc['id']}", headers=get_headers())
        
        return jsonify({"success": True, "data": new_link})
    
    return jsonify({"success": False, "msg": "Keine Ersatz-Accounts verfügbar!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
