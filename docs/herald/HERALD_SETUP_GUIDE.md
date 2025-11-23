# HERALD Agent - Setup Guide

## 🚀 Quick Start (Manual Mode First!)

**IMPORTANT**: Start with manual mode for 1-2 weeks before automating!

### Why Manual First?
- Learn what content resonates
- Build karma on Reddit organically  
- Test different tones/formats
- Avoid being flagged as a bot
- Understand community norms

---

## 📋 Prerequisites

1. **Python 3.9+**
2. **STEWARD Protocol** installed
3. **API Keys**:
   - Twitter Developer Account
   - Reddit Developer Account
   - Anthropic API Key (for Claude)

---

## 🔧 Installation

### Step 1: Clone and Setup

```bash
# Navigate to your project directory
cd /path/to/steward-protocol

# Create herald directory
mkdir herald
cd herald

# Copy files
cp /path/to/herald_agent.py .
cp /path/to/herald_config.json .
cp /path/to/HERALD_AGENT_SPEC.md .

# Install dependencies
pip install tweepy praw anthropic steward-protocol
```

### Step 2: Generate HERALD Identity

```bash
# Generate STEWARD keys for HERALD
cd ../steward
steward keygen --agent-id agent.vibe.herald

# This creates:
# - steward/keys/herald_identity.md (public)
# - steward/keys/herald_private_key (SECRET!)
# - steward/keys/herald_public_key (public)
```

### Step 3: Twitter API Setup

1. Go to https://developer.twitter.com
2. Create a new App
3. Enable OAuth 2.0 with Read+Write permissions
4. Generate:
   - API Key
   - API Secret
   - Bearer Token
   - Access Token
   - Access Token Secret

### Step 4: Reddit API Setup

1. Go to https://www.reddit.com/prefs/apps
2. Create a new app (script type)
3. Note down:
   - Client ID
   - Client Secret
4. Use your Reddit username/password

### Step 5: Set Environment Variables

```bash
# Create .env file
cat > .env << 'EOF'
# Twitter
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# Reddit
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password

# Anthropic (for content generation)
ANTHROPIC_API_KEY=your_anthropic_key
EOF

# Load environment
source .env
```

---

## 🎯 Phase 1: Manual Mode (Week 1-2)

### Day 1-3: Research & Learn

```bash
# Don't post yet! Just research.

# 1. Lurk on target subreddits
# - Read top posts from past week
# - Note what gets upvoted vs downvoted
# - Understand community culture

# 2. Build Reddit karma organically
# - Comment helpfully on others' posts
# - Answer technical questions
# - Don't mention STEWARD yet

# 3. Test content generation
python herald_agent.py --test-mode
```

### Day 4-7: First Posts (Manual Review)

```python
# Generate content but review before posting
from herald_agent import HeraldAgent

herald = HeraldAgent()

# Generate draft
research = herald.research_trend("agent identity systems")
content = herald.generate_twitter_thread(research, "agent identity")

# Review manually
print(content.text)

# Quality check
quality = herald.check_quality(content)
print(f"Quality: {quality}")

# If approved, post manually to test
# (Copy/paste to Twitter/Reddit first time)
```

### Day 8-14: Manual Posting with Logging

```python
# Post through HERALD but monitor closely

herald = HeraldAgent()

# Post to Twitter
result = herald.create_and_post(
    topic="graceful degradation in multi-agent systems",
    platform="twitter"
)

# Monitor engagement
# - Check replies
# - Note what works
# - Adjust strategy
```

---

## 🤖 Phase 2: Semi-Automated (Week 3-4)

### Setup Scheduled Generation

```python
# herald_scheduler.py

import schedule
import time
from herald_agent import HeraldAgent

herald = HeraldAgent()

def daily_content_generation():
    """Generate content daily, but wait for manual approval"""
    
    topics = [
        "cryptographic agent identity",
        "multi-agent trust models", 
        "federated agent discovery"
    ]
    
    for topic in topics:
        # Generate content
        research = herald.research_trend(topic)
        content = herald.generate_twitter_thread(research, topic)
        quality = herald.check_quality(content)
        
        # Save for manual review
        if quality['recommendation'] == 'APPROVE':
            with open(f'queue/{topic.replace(" ", "_")}.json', 'w') as f:
                json.dump({
                    'content': content.text,
                    'quality': quality,
                    'topic': topic
                }, f, indent=2)
            
            print(f"Generated content for: {topic}")
            print(f"Review at: queue/{topic.replace(' ', '_')}.json")

# Run daily at 9 AM
schedule.every().day.at("09:00").do(daily_content_generation)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Manual Approval Workflow

```bash
# Review generated content
ls queue/

# Review specific piece
cat queue/cryptographic_agent_identity.json

# If approved, post:
python -c "
from herald_agent import HeraldAgent
import json

herald = HeraldAgent()
with open('queue/cryptographic_agent_identity.json') as f:
    data = json.load(f)
    
# Post approved content
herald.post_to_twitter(data['content'])
"
```

---

## 🔄 Phase 3: Supervised Automation (Week 5-8)

### Auto-Post Non-Promotional Content

```python
# herald_autopilot.py

from herald_agent import HeraldAgent
import schedule
import time

herald = HeraldAgent()

def auto_post_educational():
    """Auto-post educational content only"""
    
    topics = [
        "agent capability attestation",
        "signature verification patterns",
        "distributed agent systems"
    ]
    
    for topic in topics:
        result = herald.create_and_post(
            topic=topic,
            platform="twitter"
        )
        
        if result['success']:
            print(f"✅ Posted: {topic}")
            # Send notification (email, Slack, etc.)
        else:
            print(f"❌ Failed: {topic} - {result['reason']}")
            # Alert human for review

# Post 3x per day
schedule.every().day.at("09:00").do(auto_post_educational)
schedule.every().day.at("14:00").do(auto_post_educational)
schedule.every().day.at("19:00").do(auto_post_educational)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Weekly Review

```bash
# Every Monday, review past week
python -c "
from herald_agent import HeraldAgent
import json

herald = HeraldAgent()

# Load audit log
with open('herald_audit_log.json') as f:
    posts = [json.loads(line) for line in f]

# Analyze engagement
for post in posts[-20:]:  # Last 20 posts
    print(f\"Post: {post['post_id']}\")
    print(f\"Quality: {post['quality_score']}\")
    print(f\"Platform: {post['platform']}\")
    print()
"
```

---

## 🚨 Emergency Protocols

### If Post Gets Downvoted

```python
# herald_emergency.py

def check_and_respond_to_downvotes():
    """Monitor posts and respond to issues"""
    
    herald = HeraldAgent()
    
    # Check Reddit posts
    for post in herald.reddit_client.user.me().submissions.new(limit=10):
        if post.score < -5:
            print(f"⚠️ Post downvoted: {post.id}")
            
            # Delete immediately
            post.delete()
            
            # Pause posting for 1 week
            with open('pause_until.txt', 'w') as f:
                future_date = (datetime.now() + timedelta(days=7)).isoformat()
                f.write(future_date)
            
            # Notify human
            print("🛑 POSTING PAUSED FOR 1 WEEK")
            print(f"Reason: Post {post.id} downvoted to {post.score}")
```

### Manual Override

```bash
# Pause HERALD immediately
touch herald_paused.txt

# Resume HERALD
rm herald_paused.txt

# Emergency stop all automation
pkill -f herald_autopilot.py
```

---

## 📊 Monitoring Dashboard

### Simple CLI Dashboard

```python
# herald_dashboard.py

from herald_agent import HeraldAgent
import json
from datetime import datetime, timedelta

def show_dashboard():
    """Display HERALD performance"""
    
    herald = HeraldAgent()
    
    # Load audit log
    with open('herald_audit_log.json') as f:
        posts = [json.loads(line) for line in f]
    
    # Last 7 days
    week_ago = datetime.now() - timedelta(days=7)
    recent = [
        p for p in posts 
        if datetime.fromisoformat(p['timestamp']) > week_ago
    ]
    
    print("=" * 50)
    print("HERALD DASHBOARD")
    print("=" * 50)
    print(f"Total posts (7 days): {len(recent)}")
    print(f"Twitter: {len([p for p in recent if p['platform'] == 'twitter'])}")
    print(f"Reddit: {len([p for p in recent if p['platform'] == 'reddit'])}")
    print()
    print(f"Avg quality score: {sum(p['quality_score'] for p in recent) / len(recent):.2f}")
    print()
    print("Recent posts:")
    for post in recent[-5:]:
        print(f"  - {post['timestamp'][:10]} | {post['platform']} | Q:{post['quality_score']:.2f}")
    print("=" * 50)

if __name__ == "__main__":
    show_dashboard()
```

---

## 🎯 Success Metrics

Track these weekly:

```bash
# Run weekly analysis
python herald_analytics.py

# Metrics to track:
# - Engagement rate (replies / posts)
# - Quality score trend
# - Downvote rate
# - Technical discussions sparked
# - GitHub stars/forks (after STEWARD mentions)
```

---

## 🔐 Security Best Practices

1. **Never commit API keys**
   ```bash
   echo ".env" >> .gitignore
   echo "steward/keys/*_private_key" >> .gitignore
   ```

2. **Backup HERALD keys securely**
   ```bash
   # Encrypted backup
   tar -czf herald_keys_backup.tar.gz steward/keys/herald_*
   gpg --encrypt herald_keys_backup.tar.gz
   ```

3. **Rotate keys every 90 days**
   ```bash
   steward rotate-key --agent-id agent.vibe.herald
   ```

---

## 🐛 Troubleshooting

### Posts Getting Downvoted
- ✅ Too promotional? Review quality gates
- ✅ Wrong subreddit culture? Research more
- ✅ Bad timing? Check posting schedule
- ✅ Low value? Strengthen research phase

### Rate Limits Hit
- ✅ Check herald_audit_log.json
- ✅ Adjust rate_limits in config
- ✅ Space out posts more

### Quality Checks Failing
- ✅ Lower quality_threshold in config (temporarily)
- ✅ Review rejected content manually
- ✅ Adjust content generation prompts

---

## 📚 Next Steps

Once HERALD is stable:

1. **Expand to Reddit** (after Twitter success)
2. **Add HackerNews** posting
3. **Monitor GitHub discussions**
4. **Auto-respond to relevant questions**
5. **Generate weekly reports**

---

## 🤝 Community Guidelines

Remember:
- **Value first, always**
- **Never spam**
- **Respect subreddit rules**
- **Be genuinely helpful**
- **Mention STEWARD only when truly relevant**

---

**Status**: Ready for Phase 1 (Manual Mode)  
**Last Updated**: 2025-11-23

Good luck! 🚀
