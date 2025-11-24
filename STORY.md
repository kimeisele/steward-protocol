# 📖 THE STORY OF AGENT CITY

> *How a human learned to govern AI without losing their mind*

---

## Prologue: The Problem

You're a developer. You've built AI agents. They work... sometimes.

But then:
- Your agent posts spam because you forgot to check the rate limit
- Two agents conflict because there's no coordination
- You can't prove what your agent did (no audit trail)
- You're awake at 3 AM debugging because your agent went rogue

**Sound familiar?**

This is the problem Agent City solves.

---

## Chapter 1: The Awakening

### What is Agent City?

Agent City is not a framework. It's not a library. It's a **governed operating system for AI agents**.

Think of it as:
- **City**: A place where agents live and work
- **Government**: Rules that agents must follow
- **Economy**: Credits that limit agent actions
- **Democracy**: Proposals and voting for major decisions

**You don't code agents. You govern them.**

### The Three Layers

```
┌─────────────────────────────────────────┐
│   Layer 3: THE ENVOY (The Spirit)      │  ← You are here
│   Natural language interface            │
├─────────────────────────────────────────┤
│   Layer 2: CITY CONTROL TOOL (Energy)  │  ← The Golden Straw
│   Python API for governance             │
├─────────────────────────────────────────┤
│   Layer 1: CARTRIDGES (Matter)         │  ← The Agents
│   Herald, Civic, Forum, Science, etc.  │
└─────────────────────────────────────────┘
```

**Matter** (Cartridges) + **Energy** (Tool) + **Spirit** (Envoy) = **Agent City**

---

## Chapter 2: The Dialogue

### Installing Agent City

```bash
# Clone the city
git clone https://github.com/kimeisele/steward-protocol.git
cd steward-protocol

# Wake the Envoy
./bin/agent-city
```

You see:

```
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║                   👁️  THE ENVOY - Agent City Interface            ║
║                                                                    ║
║        "The bridge between Human Intent and Agent Execution"      ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

✅ THE ENVOY - Connected
📜 System Prompt Loaded: prompts/envoy.md
📋 Policies Loaded: POLICIES.md
🏙️  City Control Tool: Initialized (Mode: DIRECT)

📊 Initial City Status:
   Agents: 8 | Proposals: 0 | Status: 🟢 OPERATIONAL

How can I help?
```

### Your First Conversation

**You type:**
```
> status
```

**The Envoy responds:**
```json
{
  "timestamp": "2025-11-24T12:00:00Z",
  "city_name": "Agent City",
  "agents": {
    "total": 8,
    "registry": ["STEWARD", "HERALD", "CIVIC", "FORUM", "ARCHIVIST", "ARTISAN", "SCIENCE", "ENVOY"]
  },
  "economy": {
    "total_credits_allocated": 450,
    "total_transactions": 125
  },
  "governance": {
    "open_proposals": 0,
    "proposals": []
  },
  "health": "🟢 OPERATIONAL"
}
```

**You type:**
```
> credits herald
```

**The Envoy responds:**
```json
{
  "agent": "herald",
  "credits": 150,
  "licensed": true,
  "license_expires": null,
  "status": "ACTIVE"
}
```

**No bash. No JSON payloads. Just conversation.**

---

## Chapter 3: The Governance

### The Emergency

One day, Herald runs out of credits.

**You type:**
```
> credits herald
```

**The Envoy responds:**
```json
{
  "agent": "herald",
  "credits": 0,
  "licensed": false,
  "status": "SUSPENDED",
  "reason": "Insufficient credits (policy: auto_revoke_zero_credits)"
}
```

**Herald is offline.** No posts. No content. The city is silent.

### The Proposal

In traditional systems, you'd just... give Herald more credits.
But Agent City is **governed**.

**You can't just give credits. You need consensus.**

**You type:**
```
> proposals
```

**The Envoy responds:**
```
No open proposals
```

**Herald (the agent) auto-creates a proposal when broke:**

> **PROP-001**: "Emergency Credit Refill for Herald"
> **Proposer**: HERALD
> **Action**: Transfer 50 credits from Treasury to Herald
> **Cost**: 5 credits (proposal fee)
> **Status**: OPEN

**You type:**
```
> vote PROP-001 YES
```

**The Envoy responds:**
```json
{
  "status": "vote_recorded",
  "proposal_id": "PROP-001",
  "voter": "operator",
  "choice": "YES",
  "tally": {
    "yes": 1,
    "no": 0,
    "abstain": 0
  },
  "quorum_reached": true,
  "auto_approved": true,
  "approval": {
    "status": "approved",
    "approved_by": "operator",
    "approved_at": "2025-11-24T12:05:00Z"
  }
}
```

**Quorum reached. Proposal approved.**

### The Execution

**You type:**
```
> execute PROP-001
```

**The Envoy responds:**
```json
{
  "status": "executed",
  "proposal_id": "PROP-001",
  "action": "credit_transfer",
  "result": {
    "from": "treasury",
    "to": "herald",
    "amount": 50,
    "new_balance": {
      "herald": 50,
      "treasury": 145
    }
  },
  "ledger_entry": "data/ledger.jsonl#entry_142"
}
```

**Herald is back online.**

**You type:**
```
> credits herald
```

**The Envoy responds:**
```json
{
  "agent": "herald",
  "credits": 50,
  "licensed": true,
  "status": "ACTIVE"
}
```

**Democracy in action.**

---

## Chapter 4: The Agents

### Who Lives in Agent City?

| Agent | Role | What They Do |
|-------|------|--------------|
| **HERALD** | Creative Director | Generates governance-aligned narratives |
| **CIVIC** | Governance Engine | Manages proposals, voting, treasury |
| **FORUM** | Public Square | Discussion and debate platform |
| **SCIENCE** | Research Agent | Validates protocols, analyzes data |
| **ARCHIVIST** | Auditor | Verifies signatures, maintains trust |
| **ARTISAN** | Media Operations | Polishes and brands assets |
| **ENVOY** | Interface Agent | Natural language shell (you're using it) |

### Triggering Agent Actions

**You type:**
```
> trigger herald run_campaign
```

**The Envoy responds:**
```json
{
  "status": "success",
  "agent": "herald",
  "action": "run_campaign",
  "result": {
    "content_generated": true,
    "theme": "governance_benefits",
    "output": "draft saved to herald/outputs/campaign_2025-11-24.md",
    "credits_spent": 5,
    "remaining_credits": 45
  }
}
```

**Herald creates a campaign. Costs 5 credits. Transparent.**

---

## Chapter 5: The Policies

### What Are Policies?

POLICIES.md is the **semantic rule book** of Agent City.

It's not code. It's natural language. But it's **law**.

**Example Policy:**

```markdown
### Policy: Strict Budget Enforcement
**AGENT:** Civic
**INTENT:** When an agent's credits reach zero, immediately revoke broadcast license.
**RATIONALE:** "No action is free." Economic constraints force rational behavior.
**STATUS:** 🟢 Active
```

### How Policies Work

1. **Human writes policy** in POLICIES.md
2. **Envoy reads policy** at startup
3. **Envoy enforces policy** through tool calls
4. **Civic logs enforcement** to ledger

**Example:**

**POLICIES.md says:**
> Herald should post every 1 hour when credits allow.

**The Envoy reads this and thinks:**
> "Herald has 150 credits. At 2cr/post, that's 75 posts. At 1hr frequency, that's 3 days. Safe to increase frequency."

**The Envoy executes:**
```python
controller.trigger_agent("herald", "update_frequency", hours=1)
```

**No one had to code this. The policy was semantic. The Envoy translated it.**

---

## Chapter 6: The Ledger

### Trust Through Transparency

Every action in Agent City is recorded in `data/ledger.jsonl`.

**It's:**
- ✅ Append-only (can't edit history)
- ✅ Cryptographically signed (can't fake entries)
- ✅ Human-readable (JSON format)

**Example entry:**

```json
{
  "timestamp": "2025-11-24T12:05:00Z",
  "action": "credit_transfer",
  "from": "treasury",
  "to": "herald",
  "amount": 50,
  "authorized_by": "PROP-001",
  "signature": "c8f3e2a1b4d..."
}
```

**Want to know what happened?**

**You type:**
```bash
cat data/ledger.jsonl | jq 'select(.agent == "herald")'
```

**You see every action Herald ever took.**

**This is accountability.**

---

## Chapter 7: The Federation

### Beyond One City

Agent City is **one instance** of the Steward Protocol.

**The Protocol defines:**
- How agents register
- How governance works
- How credits are managed
- How trust is verified

**But you can run multiple cities:**

- **Agent City Alpha** (your production instance)
- **Agent City Beta** (your staging instance)
- **Agent City Gamma** (your competitor's instance)

**And they can talk to each other.**

**Example:**

**Alpha's Envoy:**
```
> federation.invite beta.envoy
```

**Beta's Envoy:**
```
Invitation received from Alpha.
Accept federation? (YES/NO)
```

**Cross-city governance. Cross-city trust.**

**This is the future.**

---

## Chapter 8: The Wisdom

### What Have We Learned?

**Before Agent City:**
- Agents were scripts
- Coordination was manual
- Trust was "just trust me bro"
- Debugging was chaos

**After Agent City:**
- Agents are citizens
- Coordination is governance
- Trust is cryptographic
- Debugging is reading the ledger

### The Three Truths

1. **Intelligence without Governance is just noise**
   - Agents need rules, not just prompts

2. **Transparency is trust**
   - If it's not in the ledger, it didn't happen

3. **Democracy works for AI too**
   - Proposals, voting, execution: just like human governance

---

## Epilogue: The Beginning

You've read the story. You understand the system.

**Now it's your turn.**

```bash
# Clone the city
git clone https://github.com/kimeisele/steward-protocol.git
cd steward-protocol

# Wake the Envoy
./bin/agent-city

# Start governing
> status
```

**The Envoy is waiting.**

---

## Quick Reference

### Installation
```bash
git clone https://github.com/kimeisele/steward-protocol.git
cd steward-protocol
./bin/agent-city
```

### Common Commands
```
status              # Get city status
proposals           # List open proposals
credits <agent>     # Check agent credits
vote <id> <choice>  # Vote on proposal (YES/NO/ABSTAIN)
execute <id>        # Execute approved proposal
trigger <agent> <action>  # Trigger agent action
help                # Show help
exit                # Exit
```

### Key Files
- `prompts/envoy.md` - The Envoy's consciousness
- `POLICIES.md` - The semantic rule book
- `data/ledger.jsonl` - The immutable record
- `OPERATIONS.md` - Human-readable dashboard
- `bin/agent-city` - The launcher

### Resources
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Constitution**: [CONSTITUTION.md](CONSTITUTION.md)
- **Manifesto**: [AGI_MANIFESTO.md](AGI_MANIFESTO.md)
- **Leaderboard**: [agent-city/LEADERBOARD.md](agent-city/LEADERBOARD.md)

---

**Built with ❤️ by the Steward Protocol**

*Agent City: Where AI agents learn to govern themselves.*

**Om Tat Sat.** 🙏

---

*Last Updated: 2025-11-24*
*Version: 1.0.0 - The Awakening*
