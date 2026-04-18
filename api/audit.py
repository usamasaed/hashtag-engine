from http.server import BaseHTTPRequestHandler
import json, os, urllib.request

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        hashtags = body.get("hashtags", "")
        api_key = os.environ.get("GEMINI_API_KEY")
        prompt = f"You are a hashtag audit expert. Analyze these hashtags: {hashtags}. Return ONLY JSON: {{\"score\": 75, \"issues\": [\"issue1\"], \"good\": [\"#tag\"], \"remove\": [\"#tag\"], \"suggestions\": [\"#tag\"]}}"
        data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
        req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}", data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req) as res:
            result = json.loads(res.read())
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            text = text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(parsed).encode())
