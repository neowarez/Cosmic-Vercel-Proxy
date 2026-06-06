import os
import json
import requests

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
PROXY_SECRET = os.environ.get("PROXY_SECRET")

def handler(event, context):
    # Only POST allowed
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
    
    # Authenticate
    auth = event.get('headers', {}).get('x-proxy-secret')
    if not auth or auth != PROXY_SECRET:
        return {
            'statusCode': 401,
            'body': json.dumps({"error": "Unauthorized"})
        }
    
    target = body.get('target')
    payload = body.get('payload')
    if not target or not payload:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Missing target or payload"})
        }
    
    if target == 'discord':
        if not DISCORD_WEBHOOK_URL:
            return {
                'statusCode': 500,
                'body': json.dumps({"error": "Discord not configured"})
            }
        try:
            resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=30)
            return {
                'statusCode': 200,
                'body': json.dumps({"status": "ok", "code": resp.status_code})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({"error": str(e)})
            }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Invalid target"})
        }
