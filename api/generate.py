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
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            script = body.get("script", "")
            platform = body.get("platform", "Instagram")
            niche = body.get("niche", "")
            goal = body.get("goal", "")
            api_key = os.environ.get("OPENROUTER_API_KEY", "")
            if not api_key:
                raise Exception("OPENROUTER_API_KEY not set")
            prompt = "You are a hashtag expert. Generate hashtags for " + platform + " niche:" + niche + " goal:" + goal + " script:" + script + ". Return ONLY valid JSON with keys: branded, high_volume, mid_tier, niche, strategy_notes. Each except strategy_notes is a list of hashtags."
            data = json.dumps({"model": "meta-llama/llama-3.3-70b-instruct:free", "messages": [{"role": "user", "content": prompt}]}).encode()
            req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=data, headers={"Content-Type": "application/json", "Authorization": "Bearer " + api_key}, method="POST")
            with urllib.request.urlopen(req) as res:
                result = json.loads(res.read())
                text = result["choices"][0]["message"]["content"]
                text = text.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(text)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(parsed).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())