import os
import json
import requests

def handler(request):
    # Retrieve environment variables
    DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
    PROXY_SECRET = os.environ.get("PROXY_SECRET")

    # Simple authentication
    if request.headers.get("x-proxy-secret") != PROXY_SECRET:
        return {"statusCode": 401, "body": json.dumps({"error": "Unauthorized"})}

    # Parse body
    try:
        data = json.loads(request.data.decode('utf-8'))
    except:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid JSON"})}

    # Logic for Discord
    if data.get("target") == "discord":
        try:
            resp = requests.post(DISCORD_WEBHOOK_URL, json=data.get("payload"), timeout=10)
            return {"statusCode": 200, "body": json.dumps({"status": "success"})}
        except Exception as e:
            return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

    return {"statusCode": 400, "body": json.dumps({"error": "Invalid target"})}
