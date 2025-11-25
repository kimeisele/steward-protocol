# THE ORACLE: SYSTEM SELF-AWARENESS ARCHITECTURE

**Status:** PHASE 5 - PRODUCTION READY
**Last Updated:** 2025-11-25
**Compliance:** GAD-000 (Operator Inversion & Radical Safety)

---

## PHILOSOPHY

**"The system must be able to see itself."**

The Oracle is the voice of the system. It reads all ledgers (Bank, Vault, Events) and translates raw data into human-understandable narratives.

**Key Properties:**
- **READ-ONLY:** Never modifies state
- **TRANSPARENT:** Always provides raw evidence alongside interpretation
- **TRUTHFUL:** Separates facts from inferences
- **COMPLETE:** Aggregates disparate data sources into one coherent view

---

## ARCHITECTURE

### Three Layers

```
┌─────────────────────────────────────┐
│   User Interface (consult_oracle.py)│ ← Human asks questions
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Oracle Agent (oracle/cartridge_main.py)│ ← Interprets data
│   - explain_agent()                 │
│   - explain_freeze()                │
│   - audit_timeline()                │
│   - system_health()                 │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Introspection Engine              │ ← Reads all ledgers
│   (oracle/tools/introspection_tool) │
│   - Bank Ledger (transactions)      │
│   - Vault Ledger (leases)           │
│   - Event Logs (agent activity)     │
└─────────────────────────────────────┘
```

### 1. THE INTROSPECTION TOOL (`oracle/tools/introspection_tool.py`)

**READ-ONLY access to all system state.**

**Methods:**

#### `get_agent_status(agent_id) -> Dict`
Returns aggregated snapshot:
```python
{
    "agent_id": "science",
    "status": "active",
    "balance": 40,
    "account": { ... },
    "recent_leases": [ ... ],
    "timestamp": "2025-11-25T11:59:40"
}
```

#### `trace_transaction(tx_id) -> Dict`
Follows the money through the double-entry ledger:
```python
{
    "tx_id": "TX-abc123",
    "timestamp": "...",
    "sender": "science",
    "receiver": "VAULT",
    "amount": 5,
    "reason": "LEASE_SECRET_tavily_api",
    "previous_hash": "...",
    "tx_hash": "...",
    "entries": [ ... ]  # Double-entry detail
}
```

#### `explain_freeze(agent_id) -> Dict`
**THE CORE INTROSPECTION.**

Finds the exact violation that caused a freeze:
```python
{
    "agent_id": "herald",
    "is_frozen": true,
    "freeze_timestamp": "2025-11-25T10:30:00",
    "freeze_reason": "FREEZE: Mock Return in herald/tools/social_tool.py::post",
    "violation": {
        "type": "Mock Implementation",
        "severity": "CRITICAL",
        "description": "Function returns hardcoded value without real implementation"
    },
    "freeze_tx_id": "TX-FREEZE-88291"
}
```

#### `audit_trail(limit, agent_id) -> List[Dict]`
Returns recent transactions:
```python
[
    {
        "tx_id": "TX-...",
        "timestamp": "...",
        "sender_id": "science",
        "receiver_id": "VAULT",
        "amount": 5,
        "reason": "LEASE_SECRET_tavily_api"
    },
    # ... more
]
```

#### `system_status() -> Dict`
Overall health snapshot:
```python
{
    "timestamp": "...",
    "total_agents": 4,
    "frozen_agents": 0,
    "active_agents": 4,
    "total_credits": 1000000000,
    "circulating_credits": 45,
    "integrity_verified": true,
    "system_status": "healthy"
}
```

#### `vault_assets() -> List[Dict]`
Lists encrypted assets in Vault (names only, not values):
```python
[
    {
        "key_name": "tavily_api",
        "created_at": "...",
        "rotated_at": "..."
    }
]
```

#### `vault_access_log(limit) -> List[Dict]`
Vault access audit trail:
```python
[
    {
        "agent_id": "science",
        "key_name": "tavily_api",
        "lease_time": "2025-11-25T11:52:19",
        "credits_charged": 5,
        "tx_id": "TX-09e1955d"
    }
]
```

### 2. THE ORACLE AGENT (`oracle/cartridge_main.py`)

**Interprets introspection data into narratives.**

**Methods:**

#### `explain_agent(agent_id) -> Dict`
```python
{
    "query": "Status of science",
    "agent_id": "science",
    "raw_data": { ... },
    "narrative": """
Agent: science
Status: ACTIVE
Balance: 40 Credits

Recent Activity (3 transactions):
  • TX TX-09e1955d: science → VAULT (5 Credits) - LEASE_SECRET_tavily_api
  • ...

Vault Leases (2 recent):
  • tavily_api: 5 Credits at 2025-11-25T11:52:19
  • ...
    """,
    "evidence": { ... }
}
```

#### `explain_freeze(agent_id) -> Dict`
```python
{
    "query": "Why is herald frozen?",
    "agent_id": "herald",
    "raw_data": { ... },
    "narrative": """
🔒 herald IS FROZEN
Freeze Time: 2025-11-25T10:30:00
Violation Type: Mock Implementation
Severity: CRITICAL
Description: Function returns hardcoded value without real implementation

Root Cause: FREEZE: Mock Return in herald/tools/social_tool.py
Evidence TX: TX-FREEZE-88291
    """,
    "remediation": {
        "action": "code_fix",
        "message": "Remove mock/placeholder code and implement real logic",
        "steps": [ ... ]
    }
}
```

#### `audit_timeline(limit, agent_id) -> Dict`
Returns narrative timeline of events.

#### `system_health() -> Dict`
Returns health report with alerts.

### 3. THE USER INTERFACE (`scripts/consult_oracle.py`)

**Natural language query interface.**

**Usage:**
```bash
python3 scripts/consult_oracle.py --ask "Why is Herald frozen?"
python3 scripts/consult_oracle.py --status science
python3 scripts/consult_oracle.py --timeline --limit 10
python3 scripts/consult_oracle.py --health
python3 scripts/consult_oracle.py --tx TX-abc123
```

**Output Formats:**
- `--format narrative` (default): Human-readable text with sections
- `--format json`: Raw JSON for machine processing

---

## GUARANTEES

| Guarantee | Implementation |
|-----------|---|
| **Accuracy** | All data comes from immutable ledgers (Bank, Vault) |
| **Completeness** | Aggregates all available context (no filtering) |
| **Immutability** | Oracle is READ-ONLY; cannot modify state |
| **Auditability** | Always provides raw data alongside narratives |
| **Transparency** | Explains reasoning (facts vs. inferences) |

---

## TRUST MODEL

**The Oracle provides:**
1. **Raw Evidence** (JSON): What the system recorded
2. **Narrative** (Text): What it means
3. **Remediation** (Suggestions): What to do about it

**Users verify:**
- Check raw evidence against the actual ledgers
- Understand reasoning in the narrative
- Make informed decisions based on remediation suggestions

Example:
```
NARRATIVE: "Herald was frozen because of a Mock Return in social_tool.py"
EVIDENCE: [TX-FREEZE-88291 shows sender="watchman", reason="FREEZE: Mock Return..."]
RAW DATA: [Look at data/economy.db → transactions table → TX-FREEZE-88291]
```

---

## USAGE EXAMPLES

### Example 1: Agent is Acting Weird
```bash
$ python3 scripts/consult_oracle.py --status herald

OUTPUT:
======================================================================
Agent: herald
Status: FROZEN
Balance: 15 Credits
⚠️  THIS AGENT IS FROZEN

Recent Activity (3 transactions):
  • TX TX-FREEZE-88291: watchman → herald (0 Credits) - FREEZE: Mock Return in social_tool.py
  • TX TX-xyz: herald → CIVIC (10 Credits) - BROADCAST_FEE
  • ...
======================================================================
```

### Example 2: Why Did Watchman Freeze Something?
```bash
$ python3 scripts/consult_oracle.py --ask "Why is Herald frozen?"

OUTPUT:
🔒 herald IS FROZEN
Freeze Time: 2025-11-25T10:30:00
Violation Type: Mock Implementation
Severity: CRITICAL
Description: Function returns hardcoded value without real implementation

Root Cause: FREEZE: Mock Return in herald/tools/social_tool.py::post_tweet
Evidence TX: TX-FREEZE-88291

HOW TO FIX:
1. Locate the violation (see root cause)
2. Replace mock implementation with real logic
3. Test thoroughly
4. Commit and push
5. Watchman will thaw on next patrol
```

### Example 3: System Health Check
```bash
$ python3 scripts/consult_oracle.py --health

OUTPUT:
=== SYSTEM HEALTH REPORT ===
Status: HEALTHY
Time: 2025-11-25T11:59:40

Agents:
  Total: 4
  Active: 4
  Frozen: 0

Credits:
  Total in System: 1000000000
  Circulating: 45

Integrity: ✅ VERIFIED

⚠️  SYSTEM ALERTS:
[INFO] All systems nominal
```

### Example 4: Trace the Money
```bash
$ python3 scripts/consult_oracle.py --tx TX-09e1955d

System Transaction Timeline:
  2025-11-25T11:52:19: science → VAULT (5 Credits)
    Reason: LEASE_SECRET_tavily_api
```

---

## INTEGRATION WITH OTHER COMPONENTS

### With The Bank
```python
bank = CivicBank()
oracle = Oracle(bank=bank)

# Oracle reads all bank ledgers
status = oracle.explain_agent("science")
# Accesses: bank.get_balance(), bank.get_account_statement(), etc.
```

### With The Vault
```python
# Oracle can explain vault access
leases = oracle.get_vault_access_log()
# Shows: who leased what, when, at what cost
```

### With The Watchman
```python
# Oracle explains WHY an agent was frozen
freeze_info = oracle.explain_freeze("herald")
# Reads the exact violation from bank ledger
```

---

## DESIGN DECISIONS

1. **READ-ONLY by Default:**
   - Oracle cannot modify state
   - Protects system from corrupted introspection
   - Users always control what happens

2. **Dual Output (Narrative + Raw Data):**
   - Narrative for humans (easy to understand)
   - Raw data for verification (trust but verify)
   - Users can spot-check Oracle against actual ledgers

3. **Natural Language Extraction:**
   - `--ask "Why is Herald frozen?"` works without parsing
   - Agent names extracted automatically
   - Question types recognized (freeze, status, timeline, health)

4. **No LLM Dependency:**
   - Oracle works offline
   - Narratives are template-based, not AI-generated
   - Future: Can add Claude for more sophisticated explanations

---

## FUTURE ENHANCEMENTS

- [ ] **Claude Integration:** Use Claude for complex question answering
- [ ] **Predictive Alerts:** "Service X will run out of credits in 2 hours"
- [ ] **Root Cause Analysis:** Trace cascading failures
- [ ] **Recommendation Engine:** "Herald should fix social_tool.py"
- [ ] **Audit Report Generation:** Export audit trail as PDF/markdown
- [ ] **Time-Series Analysis:** "Credits per agent over time"

---

## REFERENCES

- **GAD-000:** Operator Inversion & Radical Safety
- **Varnashrama:** Four-caste system in agent society
- **Transparency:** All facts are verifiable against ledgers
- **Immutability:** Oracle cannot modify the system

---

**The Oracle makes the invisible visible.**
**The system speaks to itself. Humans listen and understand.**
