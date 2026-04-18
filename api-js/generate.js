export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  
  const { script, platform, niche, goal } = req.body;
  const api_key = process.env.OPENROUTER_API_KEY;
  
  const prompt = `Generate hashtags for ${platform}. Niche: ${niche}. Goal: ${goal}. Script: ${script}. Return ONLY valid JSON with keys: branded, high_volume, mid_tier, niche, strategy_notes. Each except strategy_notes is a list of hashtags.`;
  
  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${api_key}` },
    body: JSON.stringify({ model: 'meta-llama/llama-3.3-70b-instruct:free', messages: [{ role: 'user', content: prompt }] })
  });
  
  const data = await response.json();
  let text = data.choices[0].message.content;
  text = text.replace(/```json/g, '').replace(/```/g, '').trim();
  res.status(200).json(JSON.parse(text));
}