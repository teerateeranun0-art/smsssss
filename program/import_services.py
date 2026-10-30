# -*- coding: utf-8 -*-
# program/import_services.py
import json
import re

def parse_services_json():
    with open("services.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    services = data.get("services", [])
    print(f"Total services in json: {len(services)}")

    imported_apis = []
    idx = 7
    for item in services:
        url = item.get("url", "")
        if not url:
            continue
            
        # สร้างชื่อจาก domain
        domain_match = re.search(r"https?://(?:www\.)?([^/]+)", url)
        domain = domain_match.group(1).replace(".", "_") if domain_match else f"service_{idx}"
        
        has_post_data = "data" in item or "json" in item
        method = "POST" if has_post_data else "GET"
        
        # จัดการ url ถ้ามี phone
        formatted_url = url.replace("%phone%", "{phone}").replace("+%phone%", "66{phone}").replace("%phone5%", "{phone}")

        api_def = {
            "key": f"api{idx}",
            "name": domain,
            "url": formatted_url,
            "method": method,
            "has_data": has_post_data,
            "raw_data": item.get("data") or item.get("json")
        }
        imported_apis.append(api_def)
        idx += 1

    print(f"Successfully converted {len(imported_apis)} APIs")
    return imported_apis

if __name__ == "__main__":
    parse_services_json()
