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

            script = data.get("script", "").strip()
            platform = data.get("platform", "instagram")
            niche = data.get("niche", "general")
            audience = data.get("audience", "growth")
            tone = data.get("tone", "educational")
            stage = data.get("stage", "growing")

            if not script:
                self._send_json({"error": "Script is required"}, 400)
                return

            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            if not api_key:
                self._send_json({"error": "ANTHROPIC_API_KEY not configured"}, 500)
                return

            prompt = f"""You are a professional hashtag strategist. Analyze this video script/content and generate an optimal hashtag strategy.

Platform: {platform}
Niche: {niche}
Goal: {audience}
Tone: {tone}
Account stage: {stage}

Content:
\"\"\"
{script}
\"\"\"

Respond ONLY in valid JSON (no markdown, no backticks, no extra text):
{{
  "branded": ["hashtag1","hashtag2"],
  "high_volume": ["hashtag1","hashtag2","hashtag3"],
  "mid_tier": ["hashtag1","hashtag2","hashtag3","hashtag4","hashtag5","hashtag6"],
  "niche": ["hashtag1","hashtag2","hashtag3","hashtag4"],
  "total_count": 15,
  "estimated_reach": "50K-150K",
  "competition_level": "Medium",
  "strategy_notes": "2-3 sentence explanation of why these hashtags were chosen and how to use them effectively for this platform."
}}

Rules:
- Each hashtag must start with #
- No spaces in hashtags
- branded: 1-3 unique brand/campaign tags
- high_volume: 2-3 broad tags with 1M+ posts
- mid_tier: 5-8 tags with 50K-1M posts (sweet spot)
- niche: 3-5 highly specific tags under 50K posts
- All must be directly relevant to the content"""

            payload = json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
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
