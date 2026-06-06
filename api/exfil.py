from http.server import BaseHTTPRequestHandler
import json
import os
import requests

# Fetch environment variables
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
PROXY_SECRET = os.environ.get("PROXY_SECRET")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 1. Read the incoming body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # 2. Authenticate
            auth = self.headers.get("x-proxy-secret")
            if not auth or auth != PROXY_SECRET:
                self._send_response(401, {"error": "Unauthorized"})
                return
            
            # 3. Parse JSON
            try:
                data = json.loads(post_data.decode('utf-8'))
            except Exception:
                self._send_response(400, {"error": "Invalid JSON"})
                return

            target = data.get("target")
            payload = data.get("payload")

            # 4. Process Logic
            if target == "discord":
                if not DISCORD_WEBHOOK_URL:
                    # If this triggers, your Vercel Env Vars aren't set properly
                    self._send_response(500, {"error": "Discord URL not configured in Vercel"})
                    return
                
                resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
                self._send_response(resp.status_code, {"status": "ok", "discord_code": resp.status_code})
                return
            else:
                self._send_response(400, {"error": "Invalid target"})
                return

        except Exception as e:
            # Catch-all to prevent silent 500s; this will tell us exactly what broke
            self._send_response(500, {"error": f"Internal Server Error: {str(e)}"})

    def _send_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
