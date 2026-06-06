import os
import json
import requests

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
PROXY_SECRET = os.environ.get("PROXY_SECRET")

def forward_to_discord(payload):
    if not DISCORD_WEBHOOK_URL:
        return {"error": "Discord not configured"}, 500
    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=30)
        return {"status": "ok", "code": resp.status_code}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def handler(event, context):
    # Vercel calls this function
    if event.get('httpMethod') != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({"error": "Method not allowed"})
        }
    
    # Parse body
    try:
        body = json.loads(event.get('body', '{}'))
    except Exception:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Invalid JSON"})
        }
    
    # Auth header (Vercel lowercases headers)
    auth = event.get('headers', {}).get('x-proxy-secret')
    if not auth or auth != PROXY_SECRET:
        return {
            'statusCode': 401,
            'body': json.dumps({"error": "Unauthorized"})
        }
    
    target = body.get('target')
    payload = body.get('payload')
    if target != 'discord':
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Invalid target"})
        }
    
    result, status = forward_to_discord(payload)
    return {
        'statusCode': status,
        'body': json.dumps(result)
    }
