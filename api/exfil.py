from http.server import BaseHTTPRequestHandler
import json
import os
import base64
import requests

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
PROXY_SECRET = os.environ.get("PROXY_SECRET")


def forward_to_discord(payload):
    if not DISCORD_WEBHOOK_URL:
        return {"error": "Discord not configured"}, 500
    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=30)
        return {"status": "ok", "code": resp.status_code}, 200
    except Exception as e:
        return {"error": str(e)}, 500


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
        except Exception:
            self._send(400, {"error": "Invalid JSON"})
            return

        # auth header
        auth = self.headers.get('x-proxy-secret')
        if not auth or auth != PROXY_SECRET:
            self._send(401, {"error": "Unauthorized"})
            return

        target = data.get("target")
        payload = data.get("payload")

        if target == "discord":
            result, status = forward_to_discord(payload)
        else:
            self._send(400, {"error": "Invalid target"})
            return

        self._send(status, result)

    def _send(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
