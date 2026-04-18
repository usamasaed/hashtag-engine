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
            hashtags = body.get("hashtags", "")
            api_key = os.environ.get("GROQ_API_KEY", "")
            if not api_key:
                raise Exception("GROQ_API_KEY not set")
            prompt = "You are a hashtag audit expert. Analyze these hashtags: " + hashtags + ". Return ONLY valid JSON with keys: score (number 1-10), issues (list of strings), good (list of hashtags), remove (list of hashtags), suggestions (list of hashtags)."
            data = json.dumps({"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}]}).encode()
            req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=data, headers={"Content-Type": "application/json", "Authorization": "Bearer " + api_key}, method="POST")
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