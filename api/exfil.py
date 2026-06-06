import json
import os
import requests

def handler(request):
    # Retrieve environment variables
    DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
    PROXY_SECRET = os.environ.get("PROXY_SECRET")

    # Simple Check
    if request.headers.get("x-proxy-secret") != PROXY_SECRET:
        return {"statusCode": 401, "body": json.dumps({"error": "Unauthorized"})}

    # Basic Request Handling
    try:
        # Use request.get_data() or request.data depending on version
        data = json.loads(request.data)
    except Exception as e:
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}

    if data.get("target") == "discord":
        resp = requests.post(DISCORD_WEBHOOK_URL, json=data.get("payload"), timeout=10)
        return {"statusCode": resp.status_code, "body": json.dumps({"status": "sent"})}

    return {"statusCode": 400, "body": json.dumps({"error": "Invalid target"})}
