# -*- coding: utf-8 -*-
# program/clean_apis.py
import re
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from API_LIST import API_CONFIG

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    C_GREEN = Fore.GREEN + Style.BRIGHT
    C_RED = Fore.RED + Style.BRIGHT
    C_YELLOW = Fore.YELLOW + Style.BRIGHT
    C_CYAN = Fore.CYAN + Style.BRIGHT
    C_RESET = Style.RESET_ALL
except ImportError:
    C_GREEN = C_RED = C_YELLOW = C_CYAN = C_RESET = ""

def test_single_api(api_key, api_data, phone):
    url = api_data["url"].format(phone=phone) if "{phone}" in api_data["url"] else api_data["url"]
    headers = api_data["headers"]() if api_data.get("headers") else {}
    payload = api_data["data"](phone) if api_data.get("data") else None
    
    try:
        kwargs = {"headers": headers, "timeout": 8}
        if isinstance(payload, dict): kwargs["json"] = payload
        elif isinstance(payload, str): kwargs["data"] = payload

        resp = requests.request(api_data["method"], url, **kwargs)
        
        if api_data.get("success_check"):
            if api_data["success_check"](resp.text):
                return api_key, True, "PASS"
        else:
            if resp.status_code in (200, 201) and "error" not in resp.text.lower():
                return api_key, True, "STATUS 200/201"
                
        return api_key, False, f"FAIL (HTTP {resp.status_code})"
    except Exception as e:
        return api_key, False, "ERROR"

def extract_api_blocks_from_file(source_file, valid_keys):
    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract header lines before API_CONFIG
    header_part = content.split("API_CONFIG = {")[0]

    # Find each api definition block
    matches = list(re.finditer(r'    ("api\d+":\s*\{[\s\S]*?\n    \},?)', content))
    
    extracted_blocks = []
    for m in matches:
        block = m.group(1)
        for key in valid_keys:
            if block.strip().startswith(f'"{key}":'):
                extracted_blocks.append(block)
                break

    output_content = header_part + "API_CONFIG = {\n" + "\n".join(extracted_blocks) + "\n}\n"
    return output_content

def main():
    print(f"{C_CYAN}=== 🧹 API CLEANER & FILTER SYSTEM 🧹 ==={C_RESET}")
    phone = input(f"{C_YELLOW}กรอกเบอร์โทรสำหรับยิงทดสอบคัดกรอง (เช่น 0955361145): {C_RESET}").strip()
    if not phone:
        phone = "0955361145"

    max_threads = 30
    total = len(API_CONFIG)
    print(f"{C_CYAN}กำลังสแกนทดสอบ API ทั้งหมด {total} ตัว ด้วย Concurrency {max_threads} Threads...{C_RESET}\n")

    valid_keys = []
    passed = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(test_single_api, k, v, phone): (k, v["name"]) for k, v in API_CONFIG.items()}
        for future in as_completed(futures):
            key, name = futures[future]
            try:
                api_key, is_ok, reason = future.result()
                if is_ok:
                    passed += 1
                    valid_keys.append(api_key)
                    print(f"{C_GREEN}[PASS] {name:<25} ({api_key}) -> {reason}{C_RESET}")
                else:
                    failed += 1
                    # print failed without cluttering
            except Exception:
                failed += 1

    print(f"\n{C_CYAN}" + "="*50 + f"{C_RESET}")
    print(f"ผลการทดสอบ: {C_GREEN}PASS = {passed}{C_RESET} | {C_RED}DEAD/FAILED = {failed}{C_RESET} จากทั้งหมด {total} ตัว")
    
    if valid_keys:
        out_file = "API_LIST_CLEAN.py"
        print(f"\n{C_YELLOW}กำลังสร้างไฟล์ {out_file} ที่มีเฉพาะ API ที่ใช้ได้จริง...{C_RESET}")
        try:
            clean_code = extract_api_blocks_from_file("API_LIST.py", valid_keys)
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(clean_code)
            print(f"{C_GREEN}[✓] สำเร็จ! บันทึก API ที่ใช้งานได้ {len(valid_keys)} ตัว ลงใน {out_file} เรียบร้อยแล้ว!{C_RESET}")
        except Exception as e:
            print(f"{C_RED}[!] ไม่สามารถเขียนไฟล์ได้: {e}{C_RESET}")
    else:
        print(f"{C_RED}[!] ไม่มี API ใดที่ผ่านการทดสอบเลย{C_RESET}")

if __name__ == "__main__":
    main()
