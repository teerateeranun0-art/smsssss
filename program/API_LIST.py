# program/API_LIST.py
from fake_useragent import UserAgent
import random
from string import ascii_uppercase, digits

ua = UserAgent()

def randomString(N):
    return ''.join(random.choice(ascii_uppercase + digits) for _ in range(N))

def get_common_headers(referer=None, origin=None, content_type="application/json"):
    headers = {
        "User-Agent": ua.random,
        "Accept": "*/*"
    }
    if referer:
        headers["Referer"] = referer
    if origin:
        headers["Origin"] = origin
    if content_type:
        headers["Content-Type"] = content_type
    return headers

API_CONFIG = {
    "api1": {
        "name": "Imgur",
        "url": "https://api.imgur.com/account/v1/phones/verify",
        "method": "POST",
        "headers": lambda: get_common_headers("https://imgur.com/", "https://imgur.com/"),
        "data": lambda p: {
            "phone_number": f"+66{p[1:] if p.startswith('0') else p}",
            "region_code": "TH"
        },
        "success_check": lambda r: '"success":true' in r.lower() or '"data"' in r
    },

    "api2": {
        "name": "QIWI",
        "url": "https://mobile-api.qiwi.com/oauth/authorize",
        "method": "POST",
        "headers": lambda: get_common_headers("https://qiwi.com/", "https://qiwi.com/"),
        "data": lambda p: {
            "response_type": "urn:qiwi:oauth:response-type:confirmation-id",
            "username": f"+66{p[1:] if p.startswith('0') else p}",
            "client_id": "android-qw",
            "client_secret": "zAm4FKq9UnSe7id"
        },
        "success_check": lambda r: "confirmation" in r or "id" in r
    },

    "api3": {
        "name": "RedBus",
        "url": "https://m.redbus.in/api/getOtp?number={phone}&cc=66&whatsAppOpted=false",
        "method": "GET",
        "headers": lambda: get_common_headers("https://m.redbus.in", "https://m.redbus.in"),
        "data": None,
        "success_check": lambda r: '"status":true' in r.lower() or "200" in r
    },
    "api4": {
        "name": "1112Delivery",
        "url": "https://api.1112delivery.com/api/v1/otp/create",
        "method": "POST",
        "headers": lambda: {
            "User-Agent": ua.random,
            "Content-Type": "application/json"
        },
        "data": lambda p: {
            "phonenumber": f"{p}",
            "language": "th"
        },
        "success_check": lambda r: '"status":true' in r.lower() or '"code":200' in r or '"data"' in r
    },
    "api5": {
        "name": "Kex-Express",
        "url": "https://io.th.kex-express.com/firstmile-api/v3/keweb/otp/request/{phone}",
        "method": "POST",
        "headers": lambda: {
            "Appid": "Website_Api",
            "Appkey": "fcdf0569-c2a1-4dee-bd22-9d5361c047f2",
            "User-Agent": ua.random,
            "Origin": "https://th.kex-express.com",
            "Referer": "https://th.kex-express.com/"
        },
        "data": None,
        "success_check": lambda r: '"code":200' in r
    },

    "api6": {
        "name": "NocNoc",
        "url": "https://nocnoc.com/authentication-service/user/OTP?b-uid=1.0.661",
        "method": "POST",
        "headers": lambda: {
            "User-Agent": ua.random,
            "Content-Type": "application/json"
        },
        "data": lambda p: {
            "lang": "th",
            "userType": "BUYER",
            "locale": "th",
            "orgIdfier": "scg",
            "phone": f"+66{p[1:] if p.startswith('0') else p}",
            "type": "signup",
            "otpTemplate": "buyer_signup_otp_message",
            "userParams": {"buyerName": "dec"}
        },
        "success_check": lambda r: '"status":"success"' in r.lower() or '"code":200' in r or '"error":false' in r.lower()
    },
    "api7": {
        "name": "Giztix",
        "url": "https://api.giztix.com/graphql",
        "method": "POST",
        "headers": lambda: {
            "content-type": "application/json",
            "authorization": "null",
            "user-agent": ua.random,
            "origin": "https://app.giztix.com",
            "referer": "https://app.giztix.com/"
        },
        "data": lambda p: {
            "operationName": "OtpGeneratePhone",
            "variables": {
                "phone": f"66{p[1:] if p.startswith('0') else p}"
            },
            "query": "mutation OtpGeneratePhone($phone: ID!) {\n  otpGeneratePhone(phone: $phone) {\n    ref\n    __typename\n  }\n}\n"
        },
        "success_check": lambda r: "otpGeneratePhone" in r and "errors" not in r
    }
}