# Deploy to Render.com (No Credit Card Required)

## Why Render?
- **Free tier** with no credit card
- Auto-deploys from GitHub
- Simpler than Google Cloud
- Perfect for the "fucking cheap" proof

## Steps

### 1. Sign Up
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (1 click)

### 2. Create Web Service
1. Click **New** → **Web Service**
2. Connect your GitHub repo: `kimeisele/steward-protocol`
3. Configure:
   - **Name**: `steward-gateway`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Runtime**: `Docker`
   - **Instance Type**: `Free`

### 3. Add Environment Variables
In the **Environment** section, add:
- `API_KEY`: Your secret key (e.g., `steward-protocol-2025-secure`)
- `GOVERNANCE_MODE`: `SERVERLESS_BYPASS`
- `ENV`: `production`
- `LEDGER_PATH`: `/tmp/vibe_ledger.db`

### 4. Deploy
1. Click **Create Web Service**
2. Wait 2-3 minutes for build
3. Your service will be live at: `https://steward-gateway-xxx.onrender.com`

### 5. Update Frontend
1. Go to your GitHub Pages site
2. Click ⚙️ settings
3. Enter the Render URL
4. Enter your API Key
5. Start chatting!

## Cost
**$0.00/month** (Free tier)

## Limitations
- Spins down after 15 min of inactivity (first request takes 30s to wake up)
- 750 hours/month free (enough for proof of concept)

## Upgrade Path
If you need always-on: $7/month for starter instance (still cheaper than coffee)
