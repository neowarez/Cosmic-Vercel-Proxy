import os
import json
import requests

def handler(event, context):
    # 1. Only allow POST
    if event.get('httpMethod') != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    # 2. Authenticate
    headers = event.get('headers', {})
    auth = headers.get('x-proxy-secret') or headers.get('X-Proxy-Secret')
    secret = os.environ.get('PROXY_SECRET')
    if not auth or auth != secret:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Unauthorized'})
        }
    
    # 3. Parse body
    try:
        body = json.loads(event.get('body', '{}'))
    except Exception:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Invalid JSON'})
        }
    
    target = body.get('target')
    payload = body.get('payload')
    if not target or not payload:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Missing target or payload'})
        }
    
    # 4. Discord proxy
    if target == 'discord':
        webhook = os.environ.get('DISCORD_WEBHOOK_URL')
        if not webhook:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Discord webhook not configured'})
            }
        try:
            resp = requests.post(webhook, json=payload, timeout=10)
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'status': 'ok', 'discord_status': resp.status_code})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': str(e)})
            }
    
    # 5. Unknown target
    return {
        'statusCode': 400,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': 'Invalid target'})
    }
