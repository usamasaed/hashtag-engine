from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error
import os


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            hashtags = data.get("hashtags", "").strip()
            if not hashtags:
                self._send_json({"error": "Hashtags are required"}, 400)
                return

            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            if not api_key:
                self._send_json({"error": "ANTHROPIC_API_KEY not configured"}, 500)
                return

            prompt = f"""You are a hashtag auditor. Analyze these hashtags and provide a quality audit.

Hashtags: {hashtags}

Respond ONLY in valid JSON (no markdown, no backticks):
{{
  "score": 7,
  "tier_balance": {{
    "branded": 1,
    "high_volume": 3,
    "mid_tier": 5,
    "niche": 2
  }},
  "risk_flags": ["List any banned, shadowbanned, overly saturated, or irrelevant tags"],
  "missing_opportunities": "What tier or type is missing from this set?",
  "quick_wins": ["replacement suggestion 1", "replacement suggestion 2", "replacement suggestion 3"],
  "summary": "2-3 sentence overall assessment and top recommendation."
}}"""

            payload = json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 800,
                "messages": [{"role": "user", "content": prompt}]
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_data = json.loads(resp.read())
                text = resp_data["content"][0]["text"]
                clean = text.replace("```json", "").replace("```", "").strip()
                result = json.loads(clean)
                self._send_json(result)

        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            self._send_json({"error": f"Anthropic API error: {error_body}"}, 502)
        except json.JSONDecodeError as e:
            self._send_json({"error": f"JSON parse error: {str(e)}"}, 500)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _send_json(self, data, status=200):
        self.send_response(status)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format, *args):
        pass
