# 🎬 Agent City Video Demo

This document explains how to record and share the Agent City scenario as a video.

## The Story

**The Agent City Scenario** demonstrates the complete governance loop in one simple story:

1. **Herald wants to post** (Initial State: No funds)
2. **Civic blocks the post** (Governance enforcement)
3. **Herald creates a proposal** (Agent autonomy)
4. **You vote YES** (Human-in-the-loop control)
5. **Civic executes the decision** (Deterministic enforcement)
6. **Herald posts successfully** (End-to-end proof)

**What this proves:**
- ✅ Agents can be governed (can't bypass rules)
- ✅ Governance is transparent (every step logged)
- ✅ Humans stay in control (one vote changes outcome)
- ✅ System is auditable (full ledger trail)
- ✅ Steward Protocol works

---

## Quick Start: Run the Demo

### Option 1: Just Run It

```bash
cd steward-protocol
python tests/scenario_demo.py
```

This outputs a beautiful narrative showing the complete governance flow.

### Option 2: Record for Asciinema (Best for YouTube/Sharing)

[Asciinema](https://asciinema.org/) records terminal sessions and can be:
- Embedded in README
- Hosted on asciinema.org
- Shared as `.cast` files
- Converted to MP4 for YouTube

**Install asciinema:**
```bash
# macOS
brew install asciinema

# Linux
sudo apt-get install asciinema

# Or from PyPI
pip install asciinema
```

**Record the demo:**
```bash
python tests/scenario_demo.py --recording | asciinema rec demo.cast
```

This creates `demo.cast` - a complete recording of the scenario.

---

## Sharing the Recording

### Method 1: Asciinema.org (Recommended)

```bash
# Upload the recording
asciinema upload demo.cast
```

You'll get a shareable URL like: `https://asciinema.org/a/123456`

Embed it in README:
```markdown
[![Agent City Demo](https://asciinema.org/a/123456.svg)](https://asciinema.org/a/123456)
```

### Method 2: Convert to MP4

```bash
# Using asciinema2gif or ffmpeg
asciinema2gif demo.cast -s 2 -t monokai demo.gif
```

Or upload `.cast` file directly to GitHub as a gist.

### Method 3: YouTube Video

```bash
# Convert .cast to MP4 (more complex, but produces professional video)
# Use tools like: asciinema2gif, termtosvg, or manual screen recording
```

---

## The Demo Script

The scenario is implemented in `tests/scenario_demo.py`.

It runs through these phases:

### Phase 0: Initial State
- Agent City boots
- Herald initializes with 0 credits
- All cartridges load

### Phase 1: Herald Attempts Post
- Herald tries to broadcast
- Civic checks license (fails)
- System logs the denial

### Phase 2: Agent Autonomy
- Herald creates a proposal
- Herald autonomously requests 50 credits
- Proposal posted to Forum

### Phase 3: Human Intervention
- You (the Operator) vote YES
- Democracy: 1 vote = approval
- Proposal status changes to PASSED

### Phase 4: Execution
- Civic processes the decision
- Treasury transfers 50 credits to Herald
- Ledger records the transaction

### Phase 5: Success
- Herald now has balance >= 1
- Herald broadcasts message
- Post is recorded in immutable ledger

### Phase 6: Summary
- Shows the complete story arc
- Explains what each phase proved

### Phase 7: Transparency
- References OPERATIONS.md
- Shows how to verify everything
- Demonstrates full auditability

---

## Customizing the Demo

Edit `tests/scenario_demo.py` to:
- Change Herald's message (line ~360)
- Adjust timings (change `self.delay`)
- Add more agents/cartridges
- Include real protocol operations

---

## Integration: Embedding in Documentation

Once you have `demo.cast`, embed it in README:

```markdown
## 🎬 See It In Action

Watch the complete Agent City governance flow:

[![Agent City Demo](https://asciinema.org/a/YOUR_ID.svg)](https://asciinema.org/a/YOUR_ID)

Or run locally:
\`\`\`bash
python tests/scenario_demo.py
\`\`\`
```

---

## The Message

When you share this video, the message is:

> **"This is not a whitepaper. This is proof. Watch an AI agent get blocked by governance, autonomously request an exception, receive a human vote, and execute on the decision. No magic. No hype. Just transparent, governed AI."**

---

## Technical Details

The demo is:
- **Self-contained** (runs without external services)
- **Deterministic** (same output every time)
- **Human-readable** (narrated for understanding)
- **Auditable** (references real OPERATIONS.md)
- **Fast** (< 30 seconds to completion)

---

## Next Steps

Once you have the recording:

1. **Upload to Asciinema:**
   ```bash
   asciinema upload demo.cast
   ```

2. **Update README.md with the video link**

3. **Share on:**
   - Twitter/X
   - Reddit (r/autonomousagents, r/agenttech)
   - HN (if appropriate)
   - GitHub discussions

4. **Ask for feedback:** "Is this the kind of transparency you want in AI agents?"

---

## FAQ

**Q: Can I run the demo without recording?**
```bash
python tests/scenario_demo.py
```

**Q: Does the demo require live agents running?**
No, it's a narrative simulation. It shows the *story* of what would happen.

**Q: Can I customize the agents or amounts?**
Yes, edit `tests/scenario_demo.py` before running.

**Q: How do I make it run faster for recording?**
Remove `--recording` flag to use default fast timing.

---

## Credits

This demo illustrates the Steward Protocol and Agent City governance model.

- **Steward Protocol:** Cryptographic backbone for A.G.I.
- **Agent City Core:** This repository (`steward-protocol`)
- **VibeOS:** The kernel that runs everything

---

*"Don't trust the agent. Verify the protocol."*
