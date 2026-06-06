import json
import os
import requests
from http.server import BaseHTTPRequestHandler

# Fetch environment variables
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
PROXY_SECRET = os.environ.get("PROXY_SECRET")

def handler(request):
    """
    Vercel serverless function entry point.
    'request' is a dictionary-like object provided by the Vercel Python runtime.
    """
    
    # 1. Basic Auth Check
    auth = request.headers.get("x-proxy-secret")
    if not auth or auth != PROXY_SECRET:
        return {
            "statusCode": 401,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Unauthorized"})
        }

    # 2. Parse Body
    try:
        body = json.loads(request.data.decode('utf-8'))
    except Exception:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON"})
        }

    target = body.get("target")
    payload = body.get("payload")

    # 3. Handle Discord
    if target == "discord":
        if not DISCORD_WEBHOOK_URL:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Discord URL not configured"})
            }
        
        try:
            resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
            return {
                "statusCode": resp.status_code,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "ok", "code": resp.status_code})
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": str(e)})
            }

    return {
        "statusCode": 400,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": "Invalid target"})
    }
