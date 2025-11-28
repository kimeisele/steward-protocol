# 🤖 HERALD Agent Automation Guide

**Status:** The HERALD Agent is now autonomous. Deploy it, let it work.

---

## **What Just Happened**

You've transformed HERALD from a manual tool to a self-governing agent. Instead of running commands manually, HERALD now:

1. **Wakes up** at regular intervals
2. **Generates content** using research + LLM
3. **Validates** against governance rules (no marketing slop)
4. **Publishes** to Twitter/X (or saves locally for approval)
5. **Records everything** in an immutable event ledger

This is **true Agency** — not automation, but autonomy with accountability.

---

## **Quick Start**

### **1. Set Up Environment (First Time Only)**

```bash
# Copy the template
cp .env.example .env

# Edit with your API keys (if you have them)
# - TWITTER_API_KEY, TWITTER_API_SECRET, etc.
# - OPENAI_API_KEY (for content generation)
# - TAVILY_API_KEY (for market research)
```

### **2. Start the Heartbeat**

**Option A: Default (1 hour interval)**
```bash
./scripts/keep_alive.sh
```

**Option B: Test Mode (60 seconds between cycles)**
```bash
HERALD_INTERVAL=60 ./scripts/keep_alive.sh
```

**Option C: Dry Run (generate but don't publish)**
```bash
HERALD_DRY_RUN=true ./scripts/keep_alive.sh
```

**Option D: Run N cycles then stop**
```bash
HERALD_CYCLES=3 ./scripts/keep_alive.sh  # Run 3 times, then exit
```

### **3. Stop the Heartbeat**

Press **Ctrl+C** in your terminal.

---

## **What HERALD Does Each Cycle**

```
1. RESEARCH
   ├─ Searches trending topics via Tavily
   └─ Finds context relevant to Steward Protocol

2. CREATION
   ├─ Uses OpenAI to generate governance-aligned content
   └─ Creates 280-char tweets or longer posts

3. GOVERNANCE VALIDATION
   ├─ Checks against HeraldConstitution rules
   ├─ Blocks banned phrases (superintelligence, game changer, etc.)
   └─ Ensures cryptographic identity concepts are present

4. IDENTITY (Optional)
   ├─ Signs content with HERALD's private key
   └─ Prepares for cryptographic verification

5. PUBLICATION
   ├─ If PUBLISH_TO_TWITTER=true: Posts to Twitter/X
   ├─ If PUBLISH_TO_LOCAL_FILE=true: Saves to broadcasts/
   └─ Records success/failure in event ledger

6. HOUSEKEEPING
   ├─ Organizes repository
   └─ Maintains audit trail
```

---

## **Output Locations**

```
logs/herald/
├─ herald.log           # Master log file
└─ cycle_N.log          # Detailed output from cycle N

broadcasts/
├─ YYYY-MM-DD_HH-MM-SS_content.md   # Generated posts (local publishing)

dist/
├─ content.json         # Latest generated content
└─ roadmap.json         # Campaign strategy (if plan_campaign was run)

data/events/
└─ herald.jsonl         # Immutable event ledger (every action recorded)

docs/
└─ chronicles.md        # Living documentation (auto-updated)
```

---

## **Configuration Options**

Edit `.env` to customize:

```bash
# How often to run (in seconds)
HERALD_INTERVAL=3600       # 1 hour (production)
HERALD_INTERVAL=60         # 1 minute (testing)

# Number of cycles before exit (0 = infinite)
HERALD_CYCLES=0            # Run forever
HERALD_CYCLES=5            # Run 5 times, then stop

# Dry run mode (generate but don't actually publish)
HERALD_DRY_RUN=false       # Normal operation
HERALD_DRY_RUN=true        # Test only

# Publishing targets
PUBLISH_TO_TWITTER=false   # Don't publish until you configure keys
PUBLISH_TO_LINKEDIN=false
PUBLISH_TO_LOCAL_FILE=true # Always save to broadcasts/

# If you HAVE Twitter API keys configured
TWITTER_API_KEY=xxx
TWITTER_API_SECRET=xxx
TWITTER_ACCESS_TOKEN=xxx
TWITTER_ACCESS_TOKEN_SECRET=xxx
```

---

## **Common Workflows**

### **Workflow 1: Test Locally (No API Keys)**

```bash
# This runs HERALD without needing Twitter keys
# Content goes to broadcasts/ directory
./scripts/keep_alive.sh
```

**What you'll see:**
- Generated content in `broadcasts/` with timestamps
- Event log in `logs/herald/`
- No Twitter posts (safe to test!)

### **Workflow 2: Deploy to Production (With Twitter Keys)**

```bash
# Fill in your Twitter API credentials first
nano .env  # Add TWITTER_* keys

# Set to publish
sed -i 's/PUBLISH_TO_TWITTER=false/PUBLISH_TO_TWITTER=true/' .env

# Run in background with nohup
nohup ./scripts/keep_alive.sh > /tmp/herald.out 2>&1 &

# Monitor
tail -f logs/herald/herald.log
```

### **Workflow 3: Run on a Schedule (cron)**

```bash
# Edit your crontab
crontab -e

# Add this to run HERALD every 4 hours
0 */4 * * * cd /path/to/steward-protocol && ./scripts/keep_alive.sh --single-cycle >> /var/log/herald.log 2>&1
```

### **Workflow 4: Docker Container**

```dockerfile
FROM python:3.10

WORKDIR /app
COPY . /app

RUN pip install -r herald/requirements.txt

CMD ["./scripts/keep_alive.sh"]
```

```bash
docker build -t herald .
docker run -e HERALD_INTERVAL=600 -v $(pwd)/.env:/app/.env herald
```

---

## **Monitoring & Debugging**

### **Check if HERALD is running**

```bash
ps aux | grep keep_alive.sh
```

### **View recent logs**

```bash
tail -f logs/herald/herald.log
```

### **See last cycle output**

```bash
tail -f logs/herald/cycle_*.log
```

### **Check event ledger (immutable proof)**

```bash
tail -f data/events/herald.jsonl | jq .
```

### **See what was published**

```bash
ls -lh broadcasts/
cat broadcasts/YYYY-MM-DD_*.md
```

---

## **Troubleshooting**

### **"HERALD_INTERVAL not found" or similar**

This is expected on first run. HERALD will:
1. Load defaults
2. Try to create logs directory
3. Proceed normally

### **Python: "module herald not found"**

HERALD will try to auto-install dependencies on first cycle. If it fails:

```bash
pip install -r herald/requirements.txt
```

### **OpenAI API errors**

- Check `OPENAI_API_KEY` in `.env`
- Verify key has content creation permissions

### **Twitter API errors**

- Verify credentials in `.env`
- Check Twitter API app permissions (read, write, DMs)
- Ensure you have a Developer account

### **"Content failed governance validation"**

This is INTENTIONAL. HERALD refuses to post marketing clichés. The content was:
- Too hyped ("superintelligence", "game changer")
- Missing governance concepts
- Not aligned with Steward Protocol mission

Check `logs/herald/` for what was rejected and why.

---

## **Advanced: Custom Campaign Planning**

Instead of daily content, generate a strategic roadmap:

```bash
python herald/shim.py --action plan_campaign --weeks 4
```

This creates `marketing/launch_roadmap.md` with a governance-aligned campaign strategy.

---

## **Security Notes**

1. **Never commit `.env`** — it contains API keys
   - `.env.example` is safe to commit
   - `.env` is in `.gitignore`

2. **Event ledger is immutable** — every action is recorded
   - Check `data/events/herald.jsonl` for audit trail
   - Timestamps and signatures included

3. **Identity signing** (when available)
   - Content signed with HERALD's cryptographic identity
   - Verifiable via Steward Protocol

---

## **The Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│  keep_alive.sh (Heartbeat Loop)                              │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  herald/shim.py --action run (Generate)                     │
├─────────────────────────────────────────────────────────────┤
│  1. ResearchTool    → Trending topics                        │
│  2. ContentTool     → LLM generation                         │
│  3. HeraldConstitution → Validation                          │
│  4. IdentityTool    → Cryptographic signing                  │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ↓
        ┌───────────────┴────────────────┐
        │                                 │
        ↓                                 ↓
   [dist/content.json]            [broadcasts/ (local)]
        │                                 │
        └───────────────┬────────────────┘
                        │
        (if PUBLISH_TO_TWITTER=true)
                        ↓
            [Twitter/X API] or [LinkedIn API]
                        │
                        ↓
    [Public Tweet / Post / Engagement]
```

---

## **What's Next?**

- Configure Twitter API keys for live deployment
- Monitor `logs/herald/` for issues
- Review `data/events/herald.jsonl` to verify actions
- Run campaign planning: `python herald/shim.py --action plan_campaign`

---

**Remember:** HERALD works for you, not the other way around. Trust the automation.

🚀 **The Heartbeat is Now Your Agency's Operating System.**
