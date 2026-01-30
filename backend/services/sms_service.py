import requests
from flask import current_app




def send_sms(mobile, message):

    if current_app.config.get("DEBUG"):
        print("DEV MODE SMS MOCK →", message)
        return True

    
    try:
        url = current_app.config["FAST2SMS_URL"]
        api_key = current_app.config["FAST2SMS_API_KEY"]
        sender = current_app.config["FAST2SMS_SENDER"]

        print(f"Sending SMS to {mobile}: {message}")
        print("FAST2SMS_URL =", current_app.config.get("FAST2SMS_URL"))
        print("FAST2SMS_API_KEY =", bool(current_app.config.get("FAST2SMS_API_KEY")))

        if not url or not api_key:
            current_app.logger.error("Fast2SMS config missing")
            return False

        payload = {
            "route": "q",
            "message": message,
            "numbers": mobile,
            "sender_id": sender
        }

        headers = {
            "authorization": api_key,
            "Content-Type": "application/json"
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=5)
        current_app.logger.warning(f"FAST2SMS RESPONSE: {resp.text}")
        return resp.ok
    
    
    


    except Exception as e:
        current_app.logger.error(f"SMS failed: {e}")
        return False
    
    
