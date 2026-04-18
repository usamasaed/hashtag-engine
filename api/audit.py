import json
import os
import urllib.request

def handler(request):
    if request.method == "OPTIONS":
        return Response("", headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        })

    try:
        body = json.loads(request.body)
        hashtags = body.get("hashtags", "")
        
        api_key = os.environ.get("GEMINI_API_KEY")

        prompt = f"""You are a hashtag audit expert. Analyze these hashtags and return ONLY a JSON object:

Hashtags: {hashtags}

Return ONLY this JSON:
{{
  "score": 75,
  "issues": ["issue1", "issue2"],
  "good": ["#goodtag1", "#goodtag2"],
  "remove": ["#badtag1"],
  "suggestions": ["#newtag1", "#newtag2"]
}}"""

        data = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}]
        }).encode()

        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req) as res:
            result = json.loads(res.read())
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            text = text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text)

        return Response(json.dumps(parsed), headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        })

    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        })
