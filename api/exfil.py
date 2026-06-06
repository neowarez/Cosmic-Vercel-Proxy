import json
import os
import requests

def handler(request):
    # Retrieve environment variables
    DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
    PROXY_SECRET = os.environ.get("PROXY_SECRET")

    # 1. Security Check
    # Access headers via the request object
    if request.headers.get("x-proxy-secret") != PROXY_SECRET:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Unauthorized"})
        }

    # 2. Extract Body
    try:
        # Vercel provides the request data directly
        data = json.loads(request.data.decode('utf-8'))
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON"})
        }

    # 3. Logic
    target = data.get("target")
    payload = data.get("payload")

    if target == "discord" and DISCORD_WEBHOOK_URL:
        try:
            resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
            return {
                "statusCode": resp.status_code,
                "body": json.dumps({"status": "ok"})
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)})
            }

    return {
        "statusCode": 400,
        "body": json.dumps({"error": "Invalid target or config"})
    }
