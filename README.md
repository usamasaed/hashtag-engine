# Hashtag Strategy Engine

AI-powered hashtag generator for video content. Built with Python serverless functions (Vercel) + vanilla HTML/JS frontend.

## Project structure

```
hashtag-engine/
├── api/
│   ├── generate.py     # POST /api/generate — hashtag generation
│   └── audit.py        # POST /api/audit   — hashtag quality audit
├── public/
│   └── index.html      # Full frontend (single file)
├── vercel.json         # Vercel routing config
├── requirements.txt    # Python deps (stdlib only, nothing to install)
└── README.md
```

## Deploy to Vercel (step by step)

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Create a free account at vercel.com if you haven't

### 3. Deploy
```bash
cd hashtag-engine
vercel
```
Follow the prompts:
- Set up and deploy? → Y
- Which scope? → your account
- Link to existing project? → N
- Project name? → hashtag-engine (or anything you like)
- In which directory is your code? → ./
- Override settings? → N

### 4. Add your Anthropic API key
After first deploy, go to:
**Vercel Dashboard → Your Project → Settings → Environment Variables**

Add:
- Key: `ANTHROPIC_API_KEY`
- Value: `sk-ant-...` (your key from console.anthropic.com)
- Environment: Production + Preview + Development

### 5. Redeploy to apply the env variable
```bash
vercel --prod
```

Your app is live at `https://your-project.vercel.app`

## Local development

```bash
vercel dev
```
This runs the Python functions and static server locally at http://localhost:3000

You will need the Vercel CLI installed and to run `vercel link` first if not already linked.

Set your env variable locally:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## API endpoints

### POST /api/generate
Generate hashtags from a script.

Request body:
```json
{
  "script": "Your video script or content description",
  "platform": "instagram",
  "niche": "fitness",
  "audience": "growth",
  "tone": "educational",
  "stage": "growing"
}
```

Response:
```json
{
  "branded": ["#YourBrand"],
  "high_volume": ["#Fitness", "#Workout"],
  "mid_tier": ["#HomeWorkout", "#FitnessGoals"],
  "niche": ["#KettlebellMoms"],
  "total_count": 15,
  "estimated_reach": "50K-150K",
  "competition_level": "Medium",
  "strategy_notes": "..."
}
```

### POST /api/audit
Audit existing hashtags.

Request body:
```json
{
  "hashtags": "#fitness #workout #gym ..."
}
```

Response:
```json
{
  "score": 7,
  "tier_balance": { "branded": 1, "high_volume": 3, "mid_tier": 5, "niche": 2 },
  "risk_flags": ["#fitness is oversaturated"],
  "missing_opportunities": "Missing niche tags",
  "quick_wins": ["#FitnessTips2024", "#HomeGymLife"],
  "summary": "..."
}
```

## Customization

- **Add platforms**: Edit the `<select id="platform">` in `public/index.html`
- **Adjust hashtag counts**: Modify the prompt in `api/generate.py`
- **Change AI model**: Update `"model"` in both `api/*.py` files
- **Style changes**: All CSS is in the `<style>` block in `public/index.html`
