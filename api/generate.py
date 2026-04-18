import json
import os
import urllib.request
import urllib.error

def handler(request):
    if request.method == "OPTIONS":
        return Response("", headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        })
    
    try:
        body = json.loads(request.body)
        script = body.get("script", "")
        platform = body.get("platform", "Instagram")
        niche = body.get("niche", "")
        goal = body.get("goal", "")
        
        api_key = os.environ.get("GEMINI_API_KEY")
        
        prompt = f"""You are a hashtag strategy expert. Analyze this video script and generate hashtags.

Platform: {platform}
Niche: {niche}
Goal: {goal}
Script: {script}

Return ONLY a JSON object like this:
{{
  "branded": ["#brand1", "#brand2"],
  "high_volume": ["#tag1", "#tag2", "#tag3"],
  "mid_tier": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "niche": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "strategy_notes": "Brief explanation of the strategy"
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
