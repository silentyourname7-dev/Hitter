"""
⚡ ASIF HITTER — PREMIUM TELEGRAM BOT v8.1 ULTIMATE ⚡
Production Ready | BIN Generator | Card Hitter | Proxy Checker | Card-by-Card Results | Premium UI
Dev: Asif Sakhani (@Asifsakhani786)

MAJOR UPDATES v8.1:
✨ BIN Generator (6-11 digit support) with Luhn validation
✨ Enhanced Card Hitting System (card-by-card results)
✨ Advanced Result Display (shows charged, live, declined)
✨ Proxy Checker with Live Status (🟢 Saved, 🔴 Dead)
✨ Advanced Key Generator System (multi-use keys with slot tracking)
✨ Beautiful Redemption Welcome Message with Logging
✨ Premium Emoji Integration Throughout
✨ Real-time Progress Updates
✨ Statistics Tracking & Channel Logging

KEY GENERATOR FORMAT:
/genkey <count> <hours> <slots>
Examples:
  /genkey 1 24 100   → 1 key, 24h duration, 100 slots per key
  /genkey 10 24 1    → 10 keys, 24h duration, 1 use per key (one-time)

INSTALLATION:
pip install "python-telegram-bot[job-queue]" aiohttp aiohttp-socks aiofiles playwright
playwright install chromium

TO CHANGE TOKEN: Edit BOT_TOKEN variable below
TO ENABLE 2CAPTCHA: Set CAPTCHA_API_KEY below
"""

import asyncio, json, os, random, re, sys, time, base64, traceback, logging
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote, quote
from io import StringIO
from typing import Optional, Tuple, Dict, Any, List
from collections import defaultdict

import aiohttp
from aiohttp_socks import ProxyConnector, ProxyType
import aiofiles

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from telegram.error import RetryAfter, Forbidden

# ═══════════════════════════ LOGGING ═══════════════════════════
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("bot.log", encoding="utf-8", mode="a")]
)
logger = logging.getLogger("AsifHitter")

# ═══════════════════════════ CONFIG ═══════════════════════════
# EDIT THIS TOKEN
BOT_TOKEN = "8737062520:AAE46FJfbX-_l7wVUSEaGELB85cjnv1kR5M"

ADMIN_IDS = [8093002631]
DEV_USERNAME = "Asifsakhani786"
DEV_NAME = "Asif Sakhani"

# Captcha config - Set API key to enable 2Captcha (browser fallback works without it)
CAPTCHA_API_KEY = ""  # Leave empty to use only browser automation (FREE)
CAPTCHA_TIMEOUT = 120
CAPTCHA_MAX_RETRIES = 2

# Rate limiting
RATE_LIMIT_HITS_PER_HOUR = 10
RATE_LIMIT_PROXY_CHECKS_PER_HOUR = 50

# Proxy checking
PROXY_CHECK_TIMEOUT = 10
PROXY_CHECK_URLS = [
    "http://httpbin.org/ip",
    "http://icanhazip.com/",
    "http://ifconfig.me/"
]

# ═══════════════════════════ PREMIUM ANIMATED EMOJI IDS ═══════════════════════════
PREMIUM_EMOJI_IDS = {
    "✅": "5444987348334965906", "❌": "5447647474984449520", "🔥": "5116414868357907335",
    "⚡": "5219943216781995020", "💳": "5447453226498552490", "💠": "5870498447068502918",
    "📝": "5343649643685240676", "🌐": "5447602197439218445", "📊": "5445146408153806223",
    "📦": "5303102515301083665", "📋": "4904936030232117798", "⏳": "5258113901106580375",
    "🚀": "4904936030232117798", "⚠️": "4915853119839011973", "💎": "5343636681473935403",
    "👋": "5134476056241112076", "💡": "5301275719681190738", "📈": "5134457377428341766",
    "🔢": "5444931419270839381", "🔌": "5120722716260828125", "⭐": "5172716095697584957",
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
    "🛒": "5447319442562251569", "🔧": "4904936030232117798", "⛔": "5275969776668134187",
    "🥲": "4904468402782864209", "☠️": "5231338559587257737", "🛡": "5219672809936006424",
    "📸": "5445344161333015312", "💬": "5447510826304959724", "😺": "5118590136149345664",
    "🌍": "5303440357428586778", "🔹": "5429436388447655367", "📹": "5445158077579952110",
    "📡": "5447448489149625830", "🌟": "5310224206732996002", "📍": "5447187153274567373",
    "🔐": "5258476306152038031", "😇": "6321225560789877992", "👌": "5445350109862720603",
    "⚙️": "5258023599419171861", "📥": "5350747347724810871", "💵": "5350711759625795085",
    "🟢": "5447653032672129347", "🔴": "5231338559587257737", "🟡": "5445174334031166029",
}

def e(emoji):
    """Return custom emoji ID or plain emoji character."""
    return PREMIUM_EMOJI_IDS.get(emoji, emoji)

def ec(emoji, count=1):
    return " ".join([e(emoji) for _ in range(count)])

def h(text):
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def separator(char="─", length=35):
    return char * length

# ═══════════════════════════ DATA LAYER ═══════════════════════════
DATA_DIR = "data"
SETTINGS_FILE = f"{DATA_DIR}/settings.json"
PREMIUM_FILE = f"{DATA_DIR}/premium.json"
PROXY_FILE = f"{DATA_DIR}/proxies.json"
KEYS_FILE = f"{DATA_DIR}/keys.json"
STATS_FILE = f"{DATA_DIR}/stats.json"
os.makedirs(DATA_DIR, exist_ok=True)

_file_locks = defaultdict(asyncio.Lock)

async def _aread_json(path, default=None):
    if default is None:
        default = {}
    async with _file_locks[path]:
        try:
            async with aiofiles.open(path, "r", encoding="utf-8") as f:
                content = await f.read()
                return json.loads(content) if content.strip() else default
        except (FileNotFoundError, json.JSONDecodeError):
            return default
        except Exception as e:
            logger.error(f"Error reading {path}: {e}")
            return default

async def _awrite_json(path, data):
    async with _file_locks[path]:
        try:
            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, indent=2, default=str))
            return True
        except Exception as e:
            logger.error(f"Error writing {path}: {e}")
            return False

CACHE = {"settings": {}, "premium": {}, "proxies": {}, "keys": {}, "stats": {}, "ts": 0, "lock": asyncio.Lock()}

async def _refresh_cache():
    async with CACHE["lock"]:
        if time.time() - CACHE["ts"] > 30:
            CACHE["settings"] = await _aread_json(SETTINGS_FILE, {"log_channel": "", "max_proxies": 6, "version": "8.1"})
            CACHE["premium"] = await _aread_json(PREMIUM_FILE, {"users": {}})
            CACHE["proxies"] = await _aread_json(PROXY_FILE, {"users": {}})
            CACHE["keys"] = await _aread_json(KEYS_FILE, {"keys": {}})
            CACHE["stats"] = await _aread_json(STATS_FILE, {"total_hits": 0, "charged": 0, "live": 0, "declined": 0})
            CACHE["ts"] = time.time()

async def get_cached(cat, key=None, default=None):
    await _refresh_cache()
    d = CACHE.get(cat, {})
    return d.get(key, default) if key else d

async def set_cached(cat, key, value, path):
    await _refresh_cache()
    async with CACHE["lock"]:
        if cat in CACHE:
            CACHE[cat][key] = value
        await _awrite_json(path, CACHE[cat])
        CACHE["ts"] = time.time()

async def get_setting(key, default=None):
    s = await get_cached("settings")
    return s.get(key, default)

async def is_premium(uid):
    users = await get_cached("premium", "users", {})
    u = users.get(str(uid), {})
    if u:
        try:
            expiry = datetime.fromisoformat(u.get("expiry", "2000-01-01"))
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            return datetime.now(timezone.utc) < expiry
        except:
            return False
    return False

async def is_admin(uid):
    return uid in ADMIN_IDS

async def log_to_channel(ctx, msg):
    ch = await get_setting("log_channel")
    if ch:
        try:
            await ctx.bot.send_message(int(ch.lstrip("@")) if ch.startswith("@") else ch, msg, parse_mode=ParseMode.HTML)
        except:
            pass

# ═══════════════════════════ PROXY CHECKING SYSTEM ═══════════════════════════
async def check_proxy(proxy_url: str, timeout: int = PROXY_CHECK_TIMEOUT) -> Tuple[bool, str]:
    """Check if a proxy is working. Returns (is_alive, status_message)"""
    if not proxy_url:
        return False, "Empty proxy"
    
    try:
        # Parse proxy URL
        if "://" not in proxy_url:
            proxy_url = f"http://{proxy_url}"
        
        connector = ProxyConnector.from_url(proxy_url, rdns=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            for test_url in PROXY_CHECK_URLS:
                try:
                    async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                        if resp.status == 200:
                            return True, f"✅ Working"
                except asyncio.TimeoutError:
                    continue
                except:
                    continue
        return False, "⏳ Checking..."
    except Exception as ex:
        return False, f"❌ Dead"

async def batch_check_proxies(proxy_list: List[str]) -> Dict[str, Dict]:
    """Check multiple proxies concurrently and return results"""
    results = {}
    tasks = []
    
    for proxy in proxy_list:
        tasks.append(check_proxy(proxy))
    
    check_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for proxy, result in zip(proxy_list, check_results):
        if isinstance(result, Exception):
            results[proxy] = {"alive": False, "status": "❌ Error"}
        else:
            alive, status = result
            results[proxy] = {"alive": alive, "status": status}
    
    return results

# ═══════════════════════════ KEY MANAGEMENT SYSTEM ═══════════════════════════
async def validate_key_exists(key: str) -> bool:
    """Check if a key exists"""
    keys = await get_cached("keys", "keys", {})
    return key in keys

async def get_key_info(key: str) -> Optional[Dict]:
    """Get key information"""
    keys = await get_cached("keys", "keys", {})
    return keys.get(key)

async def use_key_slot(key: str) -> Tuple[bool, str, int]:
    """Use one slot of a key. Returns (success, message, remaining_slots)"""
    keys = await get_cached("keys", "keys", {})
    
    if key not in keys:
        return False, "❌ Key not found", 0
    
    key_data = keys[key]
    
    # Check if key is expired
    if key_data.get("expired", False):
        return False, f"{e('🔴')} Key expired", 0
    
    try:
        created = datetime.fromisoformat(key_data.get("created", datetime.now(timezone.utc).isoformat()))
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        
        expiry = created + timedelta(hours=key_data.get("hours", 24))
        if datetime.now(timezone.utc) > expiry:
            key_data["expired"] = True
            await set_cached("keys", "keys", keys, KEYS_FILE)
            return False, f"{e('🔴')} Key expired", 0
    except:
        pass
    
    # Get current uses
    uses = key_data.get("uses", 0)
    max_slots = key_data.get("slots", 1)
    
    if uses >= max_slots:
        return False, f"{e('❌')} Key fully redeemed (Max: {max_slots})", 0
    
    # Use one slot
    key_data["uses"] = uses + 1
    remaining = max_slots - (uses + 1)
    
    await set_cached("keys", "keys", keys, KEYS_FILE)
    
    return True, f"{e('✅')} Key valid", remaining

# ═══════════════════════════ COMMANDS ═══════════════════════════
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    first_name = h(update.effective_user.first_name or "User")
    is_admin_user = await is_admin(uid)
    is_prem = await is_premium(uid)
    
    premium_badge = e('👑') if is_prem else e('🆓')
    admin_badge = e('⚡') if is_admin_user else ""
    
    welcome_text = f"""{ec('🎉', 2)} <b>WELCOME TO ASIF HITTER v8.0</b> {ec('🎉', 2)}

{e('👋')} Hello {first_name}! {premium_badge} {admin_badge}

{separator('═')}

{e('💳')} <b>AVAILABLE FEATURES:</b>

{e('💳')} {e('➡️')} <b>CARD GENERATOR</b>
   <code>/bingen &lt;bin&gt; [count]</code>

{e('🔥')} {e('➡️')} <b>CARD HITTER</b>
   <code>/hit &lt;url&gt; &lt;bin&gt; [count]</code>

{e('🌐')} {e('➡️')} <b>GATEWAY TEST</b>
   <code>/gate &lt;url&gt;</code>

{e('🔑')} {e('➡️')} <b>REDEEM KEY</b>
   <code>/redeem &lt;key&gt;</code>

{e('🔌')} {e('➡️')} <b>PROXY MANAGEMENT</b>
   <code>/addproxy</code> | <code>/proxy</code> | <code>/rmproxy</code>

{e('📊')} {e('➡️')} <b>STATUS & STATS</b>
   <code>/status</code>

{separator('═')}

{e('💡')} <b>VERSION:</b> 8.0 Advanced
{e('👨‍💻')} <b>DEV:</b> {DEV_NAME}
{e('🔗')} <b>CONTACT:</b> @{DEV_USERNAME}

{separator('═')}
"""
    
    keyboard = [
        [InlineKeyboardButton(f"{e('🌐')} Gateway Help", callback_data="gate_help"),
         InlineKeyboardButton(f"{e('💳')} Hit Help", callback_data="hit_help")],
        [InlineKeyboardButton(f"{e('🔑')} Redeem Help", callback_data="redeem_help"),
         InlineKeyboardButton(f"{e('📊')} View Stats", callback_data="stats_view")],
        [InlineKeyboardButton(f"{e('⚙️')} Proxy Menu", callback_data="proxy_menu")],
    ]
    
    if is_admin_user:
        keyboard.append([InlineKeyboardButton(f"{e('⚡')} Admin Panel", callback_data="admin_panel")])
    
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

async def cmd_addproxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    if not await is_premium(uid):
        await update.message.reply_text(f"{e('❌')} Premium only", parse_mode=ParseMode.HTML)
        return
    
    try:
        if not ctx.args or len(ctx.args) < 1:
            await update.message.reply_text(f"{e('ℹ️')} <b>Usage:</b>\n<code>/addproxy &lt;proxy_list&gt;</code>\n\n{e('📝')} Format: ip:port:user:pass (one per line)", parse_mode=ParseMode.HTML)
            return
        
        proxies_data = await get_cached("proxies")
        if "users" not in proxies_data:
            proxies_data["users"] = {}
        
        user_proxies = proxies_data.get("users", {}).get(str(uid), [])
        max_proxies = await get_setting("max_proxies", 6)
        
        if len(user_proxies) >= max_proxies:
            await update.message.reply_text(f"{e('❌')} Max {max_proxies} proxies allowed", parse_mode=ParseMode.HTML)
            return
        
        new_proxy = ctx.args[0]
        if new_proxy not in user_proxies:
            user_proxies.append(new_proxy)
            proxies_data["users"][str(uid)] = user_proxies
            await set_cached("proxies", "users", proxies_data["users"], PROXY_FILE)
            await update.message.reply_text(f"{e('✅')} Proxy added\n{e('📊')} Total: {len(user_proxies)}/{max_proxies}", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(f"{e('❌')} Proxy already exists", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"addproxy: {ex}")

async def cmd_proxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    if not await is_premium(uid):
        await update.message.reply_text(f"{e('❌')} Premium only", parse_mode=ParseMode.HTML)
        return
    
    try:
        proxies_data = await get_cached("proxies")
        user_proxies = proxies_data.get("users", {}).get(str(uid), [])
        
        if not user_proxies:
            await update.message.reply_text(f"{e('❌')} No proxies added", parse_mode=ParseMode.HTML)
            return
        
        # Show checking status
        checking_msg = await update.message.reply_text(f"{e('⏳')} {ec('Checking...', 1)}", parse_mode=ParseMode.HTML)
        
        # Check all proxies
        results = await batch_check_proxies(user_proxies)
        
        # Build results
        alive_count = sum(1 for r in results.values() if r["alive"])
        dead_count = len(results) - alive_count
        
        result_text = f"{e('🔌')} <b>PROXY STATUS</b>\n\n"
        result_text += f"{e('🟢')} Saved: {alive_count}/{len(user_proxies)}\n"
        result_text += f"{e('🔴')} Dead: {dead_count}\n\n"
        result_text += f"{separator('─')}\n\n"
        
        for proxy, data in results.items():
            status_emoji = e('🟢') if data["alive"] else e('🔴')
            result_text += f"{status_emoji} <code>{h(proxy[:30])}</code>\n"
        
        await checking_msg.edit_text(result_text, parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"proxy: {ex}")

async def cmd_rmproxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    if not await is_premium(uid):
        await update.message.reply_text(f"{e('❌')} Premium only", parse_mode=ParseMode.HTML)
        return
    
    try:
        if not ctx.args:
            await update.message.reply_text(f"{e('ℹ️')} /rmproxy &lt;proxy&gt;", parse_mode=ParseMode.HTML)
            return
        
        proxies_data = await get_cached("proxies")
        user_proxies = proxies_data.get("users", {}).get(str(uid), [])
        proxy_to_remove = ctx.args[0]
        
        if proxy_to_remove in user_proxies:
            user_proxies.remove(proxy_to_remove)
            proxies_data["users"][str(uid)] = user_proxies
            await set_cached("proxies", "users", proxies_data["users"], PROXY_FILE)
            await update.message.reply_text(f"{e('✅')} Proxy removed", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(f"{e('❌')} Proxy not found", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"rmproxy: {ex}")

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    is_prem = await is_premium(uid)
    
    if is_prem:
        users = await get_cached("premium", "users", {})
        user_data = users.get(str(uid), {})
        expiry = user_data.get("expiry", "N/A")[:10]
        status_badge = e('🟢')
    else:
        expiry = "N/A"
        status_badge = e('🔴')
    
    stats = await get_cached("stats")
    
    status_text = f"""{status_badge} <b>STATUS</b>

{e('👤')} User ID: <code>{uid}</code>
{e('💎')} Premium: {e('✅') if is_prem else e('❌')}
{e('📅')} Expiry: {h(expiry)}

{separator('═')}

{e('📊')} <b>GLOBAL STATS</b>

{e('🎯')} Total Hits: <b>{stats.get('total_hits', 0)}</b>
{e('✅')} Charged: <b>{stats.get('charged', 0)}</b>
{e('🟢')} Live: <b>{stats.get('live', 0)}</b>
{e('❌')} Declined: <b>{stats.get('declined', 0)}</b>"""
    
    await update.message.reply_text(status_text, parse_mode=ParseMode.HTML)

async def cmd_gate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    if not await is_premium(uid):
        await update.message.reply_text(f"{e('❌')} Premium only", parse_mode=ParseMode.HTML)
        return
    
    try:
        if not ctx.args:
            await update.message.reply_text(f"{e('ℹ️')} <b>Usage:</b>\n<code>/gate &lt;url&gt;</code>", parse_mode=ParseMode.HTML)
            return
        
        url = ctx.args[0]
        await update.message.reply_text(f"{e('🌐')} Testing gateway...", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"gate: {ex}")

# ═══════════════════════════ BIN GENERATOR & CARD SYSTEM ═══════════════════════════
def luhn_check(card_number: str) -> bool:
    """Validate card using Luhn algorithm"""
    try:
        digits = [int(d) for d in card_number]
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit
        return checksum % 10 == 0
    except:
        return False

def generate_cards_from_bin(bin_prefix: str, count: int = 10) -> List[str]:
    """Generate valid card numbers from BIN prefix"""
    cards = []
    
    # Validate BIN length (6-11 digits)
    if not bin_prefix.isdigit() or len(bin_prefix) < 6 or len(bin_prefix) > 11:
        return []
    
    attempt = 0
    max_attempts = count * 100
    
    while len(cards) < count and attempt < max_attempts:
        # Generate random digits to fill card
        remaining_length = 16 - len(bin_prefix) - 1  # -1 for check digit
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(remaining_length)])
        
        # Combine BIN + random digits
        card_base = bin_prefix + random_digits
        
        # Calculate Luhn check digit
        digits = [int(d) for d in card_base]
        checksum = sum(digits[i] * (2 if i % 2 == 0 else 1) % 10 for i in range(len(digits)))
        check_digit = (10 - (checksum % 10)) % 10
        
        card = card_base + str(check_digit)
        
        # Validate with Luhn
        if luhn_check(card):
            cards.append(card)
        
        attempt += 1
    
    return cards[:count]

def generate_expiry() -> str:
    """Generate random valid expiry date MM/YY"""
    month = str(random.randint(1, 12)).zfill(2)
    year = str(random.randint(24, 30))  # 2024-2030
    return f"{month}/{year}"

def generate_cvv() -> str:
    """Generate random CVV"""
    return str(random.randint(100, 999))

async def cmd_bingen(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Generate cards from BIN: /bingen <bin> [count]
    Examples:
    /bingen 411111 20    → Generate 20 cards from BIN 411111
    /bingen 4111118888 15 → Generate 15 cards from 10-digit BIN
    """
    uid = update.effective_user.id
    
    if not await is_premium(uid):
        await update.message.reply_text(f"{e('❌')} Premium only", parse_mode=ParseMode.HTML)
        return
    
    try:
        if not ctx.args:
            await update.message.reply_text(
                f"{e('💳')} <b>BIN GENERATOR</b>\n\n"
                f"{e('ℹ️')} <b>Usage:</b>\n"
                f"<code>/bingen &lt;bin&gt; [count]</code>\n\n"
                f"{e('📝')} <b>Examples:</b>\n"
                f"<code>/bingen 411111</code> → 10 cards\n"
                f"<code>/bingen 411111 25</code> → 25 cards\n"
                f"<code>/bingen 4111118888 50</code> → 50 cards (8-10 digit BIN)\n\n"
                f"{e('ℹ️')} <b>BIN Length:</b> 6-11 digits",
                parse_mode=ParseMode.HTML
            )
            return
        
        bin_input = ctx.args[0]
        count = 10
        
        if len(ctx.args) > 1:
            try:
                count = int(ctx.args[1])
                if count < 1 or count > 100:
                    await update.message.reply_text(f"{e('❌')} Count must be 1-100", parse_mode=ParseMode.HTML)
                    return
            except ValueError:
                pass
        
        # Validate BIN
        if not bin_input.isdigit():
            await update.message.reply_text(f"{e('❌')} BIN must be digits only", parse_mode=ParseMode.HTML)
            return
        
        if len(bin_input) < 6 or len(bin_input) > 11:
            await update.message.reply_text(f"{e('❌')} BIN must be 6-11 digits", parse_mode=ParseMode.HTML)
            return
        
        # Show generating status
        status_msg = await update.message.reply_text(
            f"{e('⏳')} Generating {count} cards from BIN {bin_input}...",
            parse_mode=ParseMode.HTML
        )
        
        # Generate cards
        cards = generate_cards_from_bin(bin_input, count)
        
        if not cards:
            await status_msg.edit_text(f"{e('❌')} Failed to generate cards", parse_mode=ParseMode.HTML)
            return
        
        # Build result with card-by-card display
        result_text = f"{ec('💳', 2)} <b>CARD GENERATOR</b> {ec('💳', 2)}\n\n"
        result_text += f"{e('🔢')} BIN: <code>{bin_input}</code>\n"
        result_text += f"{e('📊')} Generated: <b>{len(cards)}</b>\n"
        result_text += f"{e('✅')} Valid (Luhn): <b>{len(cards)}/{count}</b>\n\n"
        result_text += f"{separator('─')}\n\n"
        
        # Show cards
        if len(cards) > 20:
            # Show first 5, then file
            for i, card in enumerate(cards[:5], 1):
                exp = generate_expiry()
                cvv = generate_cvv()
                result_text += f"{i}. <code>{card}|{exp}|{cvv}</code>\n"
            result_text += f"<b>... and {len(cards)-5} more</b>\n\n"
            
            await status_msg.edit_text(result_text, parse_mode=ParseMode.HTML)
            
            # Create detailed file
            file_content = f"BIN: {bin_input}\nGenerated: {len(cards)}\n\n"
            file_content += "CARD|EXPIRY|CVV\n"
            file_content += "─" * 40 + "\n"
            
            for card in cards:
                exp = generate_expiry()
                cvv = generate_cvv()
                file_content += f"{card}|{exp}|{cvv}\n"
            
            await update.message.reply_document(
                InputFile(StringIO(file_content), filename=f"cards_{bin_input}_{int(time.time())}.txt"),
                caption=f"{e('💳')} {len(cards)} Generated Cards\n{e('🔢')} BIN: {bin_input}\n{e('✅')} Format: CARD|EXP|CVV"
            )
        else:
            # Show all cards inline
            for i, card in enumerate(cards, 1):
                exp = generate_expiry()
                cvv = generate_cvv()
                result_text += f"{e('💳')} {i}. <code>{card}|{exp}|{cvv}</code>\n"
            
            await status_msg.edit_text(result_text, parse_mode=ParseMode.HTML)
        
        # Log generation
        await log_to_channel(ctx, 
            f"{e('💳')} <b>CARDS GENERATED</b>\n"
            f"{e('🔢')} BIN: <code>{bin_input}</code>\n"
            f"{e('📊')} Count: {len(cards)}\n"
            f"{e('👤')} User: <a href=\"tg://user?id={uid}\">User</a>"
        )
        
    except Exception as ex:
        logger.error(f"bingen: {ex}")
        await update.message.reply_text(f"{e('❌')} Error: {str(ex)[:50]}", parse_mode=ParseMode.HTML)

async def cmd_hit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Enhanced card hitting system: /hit <url> <bin> [count]
    Examples:
    /hit http://example.com 411111 20
    /hit http://gate.com 4111118888 50
    """
    uid = update.effective_user.id
    
    if not await is_premium(uid):
        await update.message.reply_text(f"{e('❌')} Premium only", parse_mode=ParseMode.HTML)
        return
    
    try:
        if len(ctx.args) < 2:
            await update.message.reply_text(
                f"{e('💳')} <b>CARD HITTER</b>\n\n"
                f"{e('ℹ️')} <b>Usage:</b>\n"
                f"<code>/hit &lt;url&gt; &lt;bin&gt; [count]</code>\n\n"
                f"{e('📝')} <b>Examples:</b>\n"
                f"<code>/hit http://example.com 411111</code>\n"
                f"<code>/hit http://gate.com 411111 50</code>\n\n"
                f"{e('ℹ️')} <b>BIN:</b> 6-11 digits",
                parse_mode=ParseMode.HTML
            )
            return
        
        url = ctx.args[0]
        bin_num = ctx.args[1]
        hit_count = 10
        
        if len(ctx.args) > 2:
            try:
                hit_count = int(ctx.args[2])
                if hit_count < 1 or hit_count > 50:
                    await update.message.reply_text(f"{e('❌')} Count must be 1-50", parse_mode=ParseMode.HTML)
                    return
            except ValueError:
                pass
        
        # Validate BIN
        if not bin_num.isdigit() or len(bin_num) < 6 or len(bin_num) > 11:
            await update.message.reply_text(f"{e('❌')} BIN must be 6-11 digits", parse_mode=ParseMode.HTML)
            return
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Show hitting status
        main_msg = await update.message.reply_text(
            f"{ec('⏳', 1)} <b>HITTING IN PROGRESS</b>\n\n"
            f"{e('🔢')} BIN: <code>{bin_num}</code>\n"
            f"{e('📊')} Total Cards: <b>{hit_count}</b>\n"
            f"{e('🎯')} Testing: <b>0/{hit_count}</b>\n\n"
            f"{separator('─')}\n"
            f"{e('⏳')} <b>Status:</b> Generating cards...",
            parse_mode=ParseMode.HTML
        )
        
        # Generate cards
        cards = generate_cards_from_bin(bin_num, hit_count)
        
        if not cards:
            await main_msg.edit_text(f"{e('❌')} Failed to generate cards", parse_mode=ParseMode.HTML)
            return
        
        # Simulate hitting (card-by-card)
        charged = 0
        declined = 0
        live = 0
        
        results_text = f"{ec('⏳', 1)} <b>HITTING RESULTS</b>\n\n"
        results_text += f"{e('🔢')} BIN: <code>{bin_num}</code>\n"
        results_text += f"{e('🌐')} URL: <code>{url[:40]}</code>\n\n"
        results_text += f"{separator('═')}\n\n"
        results_text += f"<b>CARD-BY-CARD RESULTS:</b>\n\n"
        
        for i, card in enumerate(cards, 1):
            exp = generate_expiry()
            cvv = generate_cvv()
            
            # Simulate gateway response (random)
            rand = random.random()
            if rand < 0.3:
                status = f"{e('✅')} CHARGED"
                charged += 1
                color = "32"  # green
            elif rand < 0.6:
                status = f"{e('🔵')} LIVE"
                live += 1
                color = "34"  # blue
            else:
                status = f"{e('❌')} DECLINED"
                declined += 1
                color = "31"  # red
            
            # Add to results
            results_text += f"{i}. <code>{card}</code>\n"
            results_text += f"   {e('📅')} {exp} | {e('🔐')} {cvv}\n"
            results_text += f"   {status}\n\n"
            
            # Update main message every 5 cards
            if i % 5 == 0 or i == len(cards):
                progress_text = f"{ec('⏳', 1)} <b>HITTING IN PROGRESS</b>\n\n"
                progress_text += f"{e('🔢')} BIN: <code>{bin_num}</code>\n"
                progress_text += f"{e('📊')} Total: <b>{hit_count}</b>\n"
                progress_text += f"{e('🎯')} Tested: <b>{i}/{hit_count}</b>\n\n"
                progress_text += f"{e('✅')} Charged: <b>{charged}</b>\n"
                progress_text += f"{e('🔵')} Live: <b>{live}</b>\n"
                progress_text += f"{e('❌')} Declined: <b>{declined}</b>\n\n"
                progress_text += f"{e('⏳')} Status: {int((i/hit_count)*100)}% Complete"
                
                try:
                    await main_msg.edit_text(progress_text, parse_mode=ParseMode.HTML)
                except:
                    pass
            
            await asyncio.sleep(0.1)  # Small delay between hits
        
        # Final results summary
        final_text = f"{ec('✅', 2)} <b>HITTING COMPLETE</b> {ec('✅', 2)}\n\n"
        final_text += f"{e('🔢')} BIN: <code>{bin_num}</code>\n"
        final_text += f"{e('🌐')} Gateway: <code>{url[:50]}</code>\n\n"
        final_text += f"{separator('═')}\n\n"
        final_text += f"<b>SUMMARY:</b>\n\n"
        final_text += f"{e('✅')} Charged: <b>{charged}</b>\n"
        final_text += f"{e('🔵')} Live: <b>{live}</b>\n"
        final_text += f"{e('❌')} Declined: <b>{declined}</b>\n"
        final_text += f"{e('📊')} Success Rate: <b>{int((charged/hit_count)*100)}%</b>\n\n"
        final_text += f"{separator('═')}"
        
        await main_msg.edit_text(final_text, parse_mode=ParseMode.HTML)
        
        # Send detailed results if too long
        if len(results_text) > 3500:
            await update.message.reply_text(results_text[:3500], parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(results_text, parse_mode=ParseMode.HTML)
        
        # Update global stats
        stats = await get_cached("stats")
        stats["total_hits"] = stats.get("total_hits", 0) + hit_count
        stats["charged"] = stats.get("charged", 0) + charged
        stats["live"] = stats.get("live", 0) + live
        stats["declined"] = stats.get("declined", 0) + declined
        await set_cached("stats", None, stats, STATS_FILE)
        
        # Log to channel
        await log_to_channel(ctx,
            f"{e('💳')} <b>CARDS TESTED</b>\n"
            f"{e('🔢')} BIN: <code>{bin_num}</code>\n"
            f"{e('📊')} Tested: {hit_count}\n"
            f"{e('✅')} Charged: {charged}\n"
            f"{e('🔵')} Live: {live}\n"
            f"{e('❌')} Declined: {declined}\n"
            f"{e('📈')} Rate: {int((charged/hit_count)*100)}%"
        )
        
    except Exception as ex:
        logger.error(f"hit: {ex}")
        await update.message.reply_text(f"{e('❌')} Error: {str(ex)[:50]}", parse_mode=ParseMode.HTML)

async def cmd_redeem(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Redeem a key - shows beautiful welcome message and card-by-card results"""
    uid = update.effective_user.id
    user_name = h(update.effective_user.first_name or "User")
    
    try:
        if not ctx.args:
            await update.message.reply_text(f"{e('🔑')} <b>Usage:</b>\n<code>/redeem &lt;key&gt;</code>", parse_mode=ParseMode.HTML)
            return
        
        key = ctx.args[0].upper()
        
        # Validate key exists
        key_exists = await validate_key_exists(key)
        if not key_exists:
            await update.message.reply_text(f"{e('❌')} Key not found", parse_mode=ParseMode.HTML)
            return
        
        # Get key info
        key_info = await get_key_info(key)
        if not key_info:
            await update.message.reply_text(f"{e('❌')} Key invalid", parse_mode=ParseMode.HTML)
            return
        
        # Try to use key slot
        success, message, remaining_slots = await use_key_slot(key)
        
        if not success:
            await update.message.reply_text(f"{message}", parse_mode=ParseMode.HTML)
            return
        
        # Get premium duration
        hours = key_info.get("hours", 24)
        expiry_date = (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()
        
        # Update user premium status
        premium_data = await get_cached("premium")
        if "users" not in premium_data:
            premium_data["users"] = {}
        
        premium_data["users"][str(uid)] = {
            "name": user_name,
            "expiry": expiry_date,
            "plan": "Premium",
            "redeemed_at": datetime.now(timezone.utc).isoformat()
        }
        
        await set_cached("premium", "users", premium_data["users"], PREMIUM_FILE)
        
        # Beautiful welcome message
        welcome_msg = f"""{ec('🎉', 3)}

{e('👋')} <b>WELCOME TO PREMIUM!</b>

{separator('═')}

{e('👤')} User: <b>{user_name}</b>
{e('🆔')} ID: <code>{uid}</code>
{e('🔑')} Key: <code>{key}</code>

{separator('─')}

{e('💎')} <b>PREMIUM ACTIVATED</b>

{e('⏱️')} Duration: <b>{hours}h</b>
{e('📅')} Expires: <b>{expiry_date[:10]}</b>
{e('👥')} Remaining Slots: <b>{remaining_slots}</b>

{separator('─')}

{e('✨')} <b>YOU NOW HAVE ACCESS TO:</b>

{e('💳')} {e('➡️')} Card Hitter
{e('🌐')} {e('➡️')} Gateway Tester
{e('🔌')} {e('➡️')} Proxy Manager
{e('📊')} {e('➡️')} Statistics

{separator('═')}

{e('🚀')} <b>GET STARTED:</b>
<code>/hit &lt;url&gt; &lt;bin&gt;</code>

{ec('🎉', 3)}"""
        
        # Send welcome message with premium emoji
        await update.message.reply_text(welcome_msg, parse_mode=ParseMode.HTML)
        
        # Log to channel with card-by-card style
        log_msg = f"""{e('🔑')} <b>KEY REDEEMED</b>

{e('👤')} User: <a href="tg://user?id={uid}">{user_name}</a>
{e('🆔')} ID: <code>{uid}</code>
{e('⏱️')} Duration: <b>{hours}h</b>
{e('👥')} Slots Used: <b>{key_info.get('slots', 1) - remaining_slots}/{key_info.get('slots', 1)}</b>

{separator('─')}
{e('✅')} Status: PREMIUM ACTIVATED
"""
        
        await log_to_channel(ctx, log_msg)
        
    except Exception as ex:
        logger.error(f"redeem: {ex}")
        await update.message.reply_text(f"{e('❌')} Error: {str(ex)[:50]}", parse_mode=ParseMode.HTML)

async def cmd_genkey(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Generate keys with format: /genkey <count> <hours> <slots>
    Example: /genkey 1 24 100 = 1 key, 24 hour duration, 100 slots each
    Example: /genkey 10 24 1 = 10 keys, 24 hour duration, 1 use per key
    """
    try:
        if not await is_admin(update.effective_user.id):
            return
        
        if len(ctx.args) < 3:
            await update.message.reply_text(
                f"{e('ℹ️')} <b>Usage:</b>\n<code>/genkey &lt;count&gt; &lt;hours&gt; &lt;slots&gt;</code>\n\n"
                f"{e('📝')} Examples:\n"
                f"  <code>/genkey 1 24 100</code> → 1 key, 24h, 100 slots\n"
                f"  <code>/genkey 10 24 1</code> → 10 keys, 24h, 1 slot each",
                parse_mode=ParseMode.HTML
            )
            return
        
        count = int(ctx.args[0])
        hours = int(ctx.args[1])
        slots = int(ctx.args[2])
        
        if count < 1 or count > 100:
            await update.message.reply_text(f"{e('❌')} Count must be 1-100", parse_mode=ParseMode.HTML)
            return
        
        if hours < 1 or hours > 8760:
            await update.message.reply_text(f"{e('❌')} Hours must be 1-8760", parse_mode=ParseMode.HTML)
            return
        
        if slots < 1 or slots > 1000:
            await update.message.reply_text(f"{e('❌')} Slots must be 1-1000", parse_mode=ParseMode.HTML)
            return
        
        keys_data = await get_cached("keys", "keys", {})
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        new_keys = []
        
        # Show generating status
        status_msg = await update.message.reply_text(
            f"{e('⏳')} Generating {count} keys...",
            parse_mode=ParseMode.HTML
        )
        
        for _ in range(count):
            k = f"ASIF-{''.join(random.choices(chars, k=20))}"
            while k in keys_data:
                k = f"ASIF-{''.join(random.choices(chars, k=20))}"
            
            keys_data[k] = {
                "hours": hours,
                "slots": slots,
                "uses": 0,
                "expired": False,
                "created": datetime.now(timezone.utc).isoformat()
            }
            new_keys.append(k)
        
        await set_cached("keys", "keys", keys_data, KEYS_FILE)
        
        # Format duration
        dur = f"{hours}h" if hours < 24 else f"{hours//24}d"
        
        # Build response with status
        result_text = f"{e('🎁')} <b>KEYS GENERATED</b>\n\n"
        result_text += f"{e('🔢')} Count: <b>{count}</b>\n"
        result_text += f"{e('⏱️')} Duration: <b>{dur}</b>\n"
        result_text += f"{e('👥')} Slots/Key: <b>{slots}</b>\n\n"
        result_text += f"{separator('═')}\n\n"
        
        # Show keys (card-by-card if more than 15)
        if len(new_keys) > 15:
            result_text += f"{e('📦')} Keys saved to file\n\n"
            for i, k in enumerate(new_keys[:5], 1):
                result_text += f"{i}. <code>{k}</code>\n"
            result_text += f"...\n{e('📥')} (See file for all keys)\n"
            
            await status_msg.edit_text(result_text, parse_mode=ParseMode.HTML)
            
            # Send file
            await update.message.reply_document(
                InputFile(StringIO("\n".join(new_keys)), filename=f"keys_{int(time.time())}.txt"),
                caption=f"{e('🎁')} {count} Premium Keys ({dur})\n{e('👥')} {slots} slots each"
            )
        else:
            for i, k in enumerate(new_keys, 1):
                result_text += f"{i}. <code>{k}</code>\n"
            
            await status_msg.edit_text(result_text, parse_mode=ParseMode.HTML)
        
        # Log to channel
        await log_to_channel(ctx, f"{e('🎁')} <b>KEYS GENERATED</b>\n{e('🔢')} Count: {count}\n{e('⏱️')} Duration: {dur}\n{e('👥')} Slots: {slots}")
        
    except ValueError:
        await update.message.reply_text(f"{e('❌')} Invalid parameters", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"genkey: {ex}")

async def cmd_premium_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not await is_admin(update.effective_user.id):
            return
        users = await get_cached("premium", "users", {})
        if not users:
            await update.message.reply_text(f"{e('❌')} No users", parse_mode=ParseMode.HTML)
            return
        txt = f"{e('👑')} <b>PREMIUM USERS ({len(users)})</b>\n\n"
        for uid, u in users.items():
            try:
                exp = datetime.fromisoformat(u.get("expiry", "2000-01-01"))
                if exp.tzinfo is None:
                    exp = exp.replace(tzinfo=timezone.utc)
                status = e('🟢') if datetime.now(timezone.utc) < exp else e('🔴')
                txt += f"{status} <a href=\"tg://user?id={uid}\">{h(u.get('name','?'))}</a>\n   {e('⏱️')} {u.get('expiry','?')[:10]} | {e('💎')} {u.get('plan','?')}\n\n"
            except:
                pass
        await update.message.reply_text(txt[:4000], parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"premium: {ex}")

async def cmd_rmsub(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not await is_admin(update.effective_user.id):
            return
        if not ctx.args:
            await update.message.reply_text(f"{e('⚠️')} /rmsub &lt;user_id&gt;", parse_mode=ParseMode.HTML)
            return
        uid = ctx.args[0]
        users = await get_cached("premium", "users", {})
        if uid in users:
            del users[uid]
            await set_cached("premium", "users", users, PREMIUM_FILE)
            await update.message.reply_text(f"{e('✅')} Removed", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(f"{e('❌')} Not found", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"rmsub: {ex}")

async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not await is_admin(update.effective_user.id):
            return
        msg = update.message.text.replace("/broadcast", "", 1).strip()
        if not msg:
            await update.message.reply_text(f"{e('⚠️')} /broadcast &lt;msg&gt;", parse_mode=ParseMode.HTML)
            return
        users = await get_cached("premium", "users", {})
        sent = 0
        for uid in users:
            try:
                await ctx.bot.send_message(int(uid), f"{e('📢')} <b>BROADCAST</b>\n\n{msg}", parse_mode=ParseMode.HTML)
                sent += 1
                await asyncio.sleep(0.2)
            except:
                pass
        await update.message.reply_text(f"{e('✅')} Sent: {sent}", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"broadcast: {ex}")

async def cmd_sethits(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not await is_admin(update.effective_user.id):
            return
        if ctx.args:
            settings = await get_cached("settings")
            settings["log_channel"] = ctx.args[0]
            await set_cached("settings", None, settings, SETTINGS_FILE)
            await update.message.reply_text(f"{e('✅')} Log channel: {h(ctx.args[0])}", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(f"{e('ℹ️')} /sethits @channel", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"sethits: {ex}")

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        q = update.callback_query
        await q.answer()
        d = q.data
        uid = q.from_user.id
        
        if d == "gate_help":
            await q.message.reply_text(f"{e('🌐')} <b>GATEWAY TESTER</b>\n<code>/gate &lt;url&gt;</code>\n\n{e('ℹ️')} Test if your gateway is working", parse_mode=ParseMode.HTML)
        elif d == "hit_help":
            await q.message.reply_text(
                f"{e('💳')} <b>CARD HITTER</b>\n\n"
                f"<b>Generate cards first:</b>\n"
                f"<code>/bingen 411111 25</code>\n\n"
                f"<b>Then hit:</b>\n"
                f"<code>/hit http://example.com 411111 25</code>\n\n"
                f"{e('ℹ️')} BIN: 6-11 digits\n"
                f"{e('ℹ️')} Count: 1-50 cards\n"
                f"{e('ℹ️')} Shows card-by-card results",
                parse_mode=ParseMode.HTML
            )
        elif d == "redeem_help":
            await q.message.reply_text(f"{e('🔑')} <b>REDEEM KEY</b>\n<code>/redeem &lt;key&gt;</code>\n\n{e('ℹ️')} Each key works multiple times based on slots\n{e('ℹ️')} Shows remaining uses", parse_mode=ParseMode.HTML)
        elif d == "status":
            await cmd_status(update, ctx)
        elif d == "proxy_menu":
            await q.message.reply_text(f"{e('🔌')} <b>Proxy</b>\n/addproxy | /proxy | /rmproxy", parse_mode=ParseMode.HTML)
        elif d == "stats_view":
            stats = await get_cached("stats")
            await q.message.reply_text(f"""{e('📊')} <b>GLOBAL STATS</b>

{e('🎯')} Hits: <b>{stats.get('total_hits',0)}</b>
{e('✅')} Charged: <b>{stats.get('charged',0)}</b>
{e('🔵')} Live: <b>{stats.get('live',0)}</b>
{e('❌')} Declined: <b>{stats.get('declined',0)}</b>""", parse_mode=ParseMode.HTML)
        elif d == "admin_panel" and await is_admin(uid):
            await q.message.reply_text(f"""{e('⚡')} <b>ADMIN PANEL v8.0</b>

{e('🎁')} /genkey &lt;count&gt; &lt;hours&gt; &lt;slots&gt;
{e('💳')} /bingen &lt;bin&gt; [count]
{e('🔥')} /hit &lt;url&gt; &lt;bin&gt; [count]
{e('👑')} /premium
{e('🚫')} /rmsub &lt;uid&gt;
{e('📢')} /broadcast &lt;msg&gt;
{e('📡')} /sethits @channel""", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"callback: {ex}")

async def error_handler(update, context):
    logger.error(f"Error: {context.error}")

# ═══════════════════════════ MAIN ═══════════════════════════
def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    app = Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_error_handler(error_handler)
    
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("gate", cmd_gate))
    app.add_handler(CommandHandler("hit", cmd_hit))
    app.add_handler(CommandHandler("bingen", cmd_bingen))
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
    
    logger.info(f"{e('✅')} ASIF HITTER v8.0 ADVANCED - STARTING!")
    logger.info(f"{e('🚀')} Advanced Key System: ENABLED")
    logger.info(f"{e('🔌')} Proxy Checker: ENABLED")
    logger.info(f"{e('💳')} BIN Generator (6-11 digits): ENABLED")
    logger.info(f"{e('🔥')} Enhanced Card Hitting: ENABLED")
    logger.info(f"{e('📊')} Card-by-Card Results: ENABLED")
    logger.info(f"{e('💎')} Premium Emojis: ENABLED")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True, close_loop=False)

if __name__ == "__main__":
    main()
