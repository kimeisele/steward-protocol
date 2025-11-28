# UNIVERSE MIGRATION PLAN
## The Complete Architecture Integration (Compact & Iterative)

**Date:** 2025-11-28
**Backup:** `/tmp/steward-protocol-backup-20251128-082020`
**Strategy:** STAY IN REPO + FIX ITERATIVELY
**Approach:** Understand the UNIVERSE first, then fix systematically

---

## 🌌 WHAT WE HAVE (The Universe)

### CORE PHILOSOPHY

**GAD-000: Operator Inversion**
- AI operates, human directs
- Foundation of EVERYTHING
- **Location:** `GAD-000.md`

**GAD-1000: Identity Fusion**
- Human + AI = Same cryptographic protocol (ECDSA P-256)
- **Binary World Break** - No more user/service distinction
- **USB for Intelligence**
- **Location:** `GAD-1000.md`

**A.G.I. = Artificial GOVERNED Intelligence**
- NOT "General" → "Governed"
- Capability + Cryptographic Identity + Accountability
- **HERALD wrote the manifesto ITSELF**
- **Location:** `AGI_MANIFESTO.md`

---

### AGENT CITY (The Living System)

**19 ACTIVE AGENTS** (not 13!):

**System Agents (13):**
1. CIVIC - Governance, Registry, Economy, Lifecycle
2. ORACLE - Introspection, System Health
3. WATCHMAN - Integrity, Monitoring
4. FORUM - Democracy, Voting
5. SUPREME_COURT - Justice, Mercy
6. HERALD - Media, Broadcasting
7. ARCHIVIST - History, Ledger
8. SCIENCE - Research, Intelligence
9. ENGINEER - Meta-Building
10. AUDITOR - Verification, Compliance
11. ENVOY - Universal Operator Interface
12. CHRONICLE - Temporal Operations
13. SCRIBE - Documentation

**Citizen Agents (6):**
14. DHRUVA - Data Ethics, Truth
15. MARKET - Trading
16. TEMPLE - Offerings
17. AMBASSADOR - Outreach
18. PULSE - Twitter API
19. MECHANIC - Maintenance
20. ARTISAN - Media Production
21. AGORA - Community
22. LENS - Observation

**Current Status:**
- ✅ 5 working (Oracle, Watchman, Forum, Supreme Court, Herald)
- ❌ 8 crashing (Civic, Science, Engineer, Archivist, Auditor, Envoy, Chronicle, Scribe)
- ❓ Citizens unknown status

---

### 3-LAYER ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 3: AGENT LAYER                                   │
│  19 autonomous agents (System + Citizens)               │
├─────────────────────────────────────────────────────────┤
│  LAYER 2: ROUTING LAYER                                 │
│  - Milk Ocean Router (Kshira-Samudra Gateway)           │
│  - City Control Tool (ENVOY)                            │
│  - Semantic Analysis & Workflow Execution               │
├─────────────────────────────────────────────────────────┤
│  LAYER 1: KERNEL LAYER (vibe_core/)                     │
│  - Boot Orchestrator (Sarga - Cosmic Creation)          │
│  - Topology (Bhu-Mandala - Vedic Geometry)              │
│  - Event Bus (The Flute - Agent Communication)          │
│  - Pulse (Spandana - Primordial Vibration)              │
│  - Narasimha (Hypervisor Kill-Switch)                   │
│  - Ledger (Immutable Event Log)                         │
│  - Phoenix Config (Graceful Degradation)                │
│  - Bridge (Neural Connection)                           │
└─────────────────────────────────────────────────────────┘
```

---

### VEDIC CONCEPTS (Integrated)

**Bhu-Mandala Topology** (`topology.py`)
- Cosmic geography for agent placement
- Varsha (regions), routing based on geometry

**Sarga** (`sarga.py`)
- Boot process as cosmic creation
- Creation cycles, elements

**Spandana** (`pulse.py`)
- Primordial vibration, system heartbeat
- Pulse frequencies

**Kshira-Samudra** (`milk_ocean.py`)
- Milk Ocean Router for request routing
- 741 lines of routing logic!

**Narasimha** (`narasimha.py`)
- Hypervisor protection layer
- Kill-switch for threats
- 307 lines

---

### STEWARD PROTOCOL (The Standard)

**5 Layers (from SPECIFICATION.md):**
1. Agent Manifest Format (steward.json)
2. Registry & Discovery
3. Verification Protocol (Crypto signatures)
4. Delegation Protocol (Agent-to-agent)
5. Federation Interface (Multi-city)

**Current Status:**
- ✅ Designed (specs exist)
- ❌ NOT fully implemented
- ❌ Agents NOT compliant

---

### ECONOMIC SUBSTRATE

**CivicBank** (`civic/tools/economy.py` - 427 lines)
- Double-entry bookkeeping
- Credit system
- **Problem:** Eager loading crashes system

**CivicVault** (`civic/tools/vault.py` - 378 lines)
- Secure asset management
- Cryptography (Fernet)
- **Problem:** Import-time crash (Rust panic)

**License Tool** (`civic/tools/license_tool.py` - 560 lines)
- Broadcasting permissions
- Governance gates

---

### SPECIALIZED TOOLS

**ENVOY Tools** (Universal Operator):
- `city_control_tool.py` (506 lines) - City operations
- `milk_ocean.py` (741 lines) - Router
- `curator_tool.py` (342 lines) - Governance analysis
- `gap_report_tool.py` (484 lines) - Governability audit
- `run_campaign_tool.py` (527 lines) - Marketing campaigns
- `hil_assistant_tool.py` (114 lines) - Verbal abstraction

**CIVIC Tools** (Governance):
- `dashboard_tool.py` (333 lines) - Operations dashboard
- `lifecycle_enforcer.py` (345 lines) - Kernel-level gates
- `lifecycle_manager.py` (507 lines) - Vedic lifecycle
- `ledger_tool.py` (376 lines) - Bank wrapper

---

## 💥 THE REAL PROBLEMS

### Problem 1: Import-Time Crashes (8 agents)
**Root Cause:** Eager loading of CivicBank/Vault
**Crash Chain:**
```
Agent __init__
  → EconomyAgent()
    → LedgerTool()
      → from .economy import CivicBank
        → from .vault import CivicVault
          → from cryptography.fernet import Fernet
            → pyo3_runtime.PanicException (Rust panic!)
```

**Affected:** Civic, Science, Engineer, Archivist, Auditor, Envoy, Chronicle, Scribe

### Problem 2: STEWARD Protocol NOT Integrated
- No steward.json for agents
- No STEWARD.md (Level 2 compliance)
- No registry/discovery working
- No verification protocol
- Protocol exists as SPEC only

### Problem 3: Architecture Drift
- 60+ markdown docs
- Multiple "BLOCKER" migrations incomplete
- "Complete ✅" claims without verification
- Docs outdated

### Problem 4: Missing Lineage Chain
- Parampara concept mentioned but not built
- No blockchain-style succession tracking
- No immutable audit trail beyond ledger

---

## 🎯 THE SOLUTION (Iterative & Compact)

### PHASE 1: EMERGENCY TRIAGE (2-3 days) 🔴 CRITICAL

**Goal:** All 19 agents boot successfully

**Tasks:**
1. **Lazy Load Economic Substrate**
   ```python
   # vibe_core/kernel_impl.py
   class RealVibeKernel:
       def __init__(self):
           self._bank = None  # Lazy
           self._vault = None  # Lazy

       def get_bank(self):
           if self._bank is None:
               try:
                   from steward.system_agents.civic.tools.economy import CivicBank
                   self._bank = CivicBank()
               except ImportError:
                   self._bank = MockBank()  # Graceful degradation
           return self._bank
   ```

2. **Update All Crashing Agents**
   - Replace `from .economy import CivicBank` with `kernel.get_bank()`
   - Remove all `__init__` imports of Bank/Vault
   - Add graceful degradation

3. **Test All 19 Agents**
   - Boot test for each
   - No import crashes

**Success Criteria:**
- ✅ 19/19 agents boot without crashes
- ✅ Economic features still work (lazy-loaded)
- ✅ No Rust panics

---

### PHASE 2: LINEAGE CHAIN (3-5 days)

**Goal:** Build the blockchain succession chain

**Tasks:**
1. **Create Lineage Module**
   ```python
   # vibe_core/lineage.py
   class LineageChain:
       """
       Blockchain-style succession chain for agent lineage.
       Vedic concept: Immutable succession (guru → disciple)
       Tech: Chained blocks, cryptographically signed
       """
       def add_succession(self, agent_id, action, signature):
           # Add to chain
           pass

       def verify_lineage(self, agent_id):
           # Verify back to genesis
           pass
   ```

2. **Integrate with Kernel**
   - Add lineage to kernel boot
   - Record all agent registrations
   - Track Constitutional Oath succession

3. **Integrate with CivicBank**
   - All credit transactions in lineage
   - Immutable financial history

**Success Criteria:**
- ✅ Lineage chain tracks all agent actions
- ✅ Can trace any agent back to genesis
- ✅ Cryptographically verified

---

### PHASE 3: STEWARD PROTOCOL COMPLIANCE (1 week)

**Goal:** All 19 agents STEWARD Level 2 compliant

**Tasks:**
1. **Generate steward.json for all agents**
   - Use manifest generator
   - Include capabilities, identity, governance

2. **Create STEWARD.md for all agents**
   - Use template from vibe-agency
   - Level 2 compliance (all required sections)
   - Honest status (no fake ✅)

3. **Implement Verification**
   - Cryptographic signing
   - Manifest verification
   - `steward verify <agent>` command

**Success Criteria:**
- ✅ 19 steward.json files
- ✅ 19 STEWARD.md files (Level 2)
- ✅ All verified cryptographically

---

### PHASE 4: STEWARD CLI (5-7 days)

**Goal:** Build the actual steward CLI tool

**Tasks:**
1. **Core Commands**
   ```bash
   steward init              # Create steward.json
   steward boot              # Start kernel
   steward register <agent>  # Register with kernel
   steward verify <agent>    # Verify manifest
   steward discover          # Find agents
   steward delegate          # Submit tasks
   steward lineage <agent>   # Show succession chain
   steward introspect        # Kernel state
   ```

2. **Registry Integration**
   - Git-based registry (MVP)
   - Publish/discover agents
   - Trust score calculation

**Success Criteria:**
- ✅ steward CLI functional
- ✅ Can discover/verify/delegate
- ✅ Lineage traceable via CLI

---

### PHASE 5: DOCUMENTATION CONSOLIDATION (2-3 days)

**Goal:** Clean up 60+ docs, create single source of truth

**Tasks:**
1. **Archive Old Docs**
   - Move BLOCKER*.md to `/docs/archive/`
   - Move PHASE*.md to `/docs/archive/`
   - Move duplicate architecture docs to `/docs/archive/`

2. **Update Core Docs**
   - README.md (entry point)
   - ARCHITECTURE.md (current state)
   - AGENTS.md (auto-generated, keep)
   - CITYMAP.md (auto-generated, keep)
   - OPERATIONS.md (auto-generated, keep)
   - GAD-000.md (foundational, keep)
   - GAD-1000.md (identity fusion, keep)
   - AGI_MANIFESTO.md (core philosophy, keep)

3. **Create INDEX.md**
   - Navigation hub
   - Links to all active docs
   - Archive links

**Success Criteria:**
- ✅ < 20 active docs in root
- ✅ Clear navigation
- ✅ No outdated claims

---

### PHASE 6: TESTING & CI/CD (2-3 days)

**Goal:** Never allow regression

**Tasks:**
1. **Integration Tests**
   - Test all 19 agents boot
   - Test lazy loading
   - Test lineage chain
   - Test STEWARD compliance

2. **CI/CD Pipeline**
   - GitHub Actions
   - Run tests on every commit
   - Auto-generate AGENTS.md, CITYMAP.md, OPERATIONS.md
   - Attestation refresh (every 6 hours)

3. **Quality Gates**
   - Pre-commit hooks
   - Minimum 80% coverage
   - All agents boot successfully
   - STEWARD verification passes

**Success Criteria:**
- ✅ CI/CD running
- ✅ Quality gates enforced
- ✅ Auto-generated docs up-to-date

---

## 📊 TIMELINE

```
Week 1:  Phase 1 (Emergency Triage) - ALL AGENTS BOOT
Week 2:  Phase 2 (Lineage Chain) + Phase 3 Start (STEWARD)
Week 3:  Phase 3 Complete (STEWARD Compliance)
Week 4:  Phase 4 (steward CLI)
Week 5:  Phase 5 (Docs) + Phase 6 (Testing/CI)
```

**Total:** 5 weeks for complete integration

---

## 🎯 SUCCESS CRITERIA (Overall)

### Technical
- ✅ 19/19 agents boot successfully
- ✅ All agents STEWARD Level 2 compliant
- ✅ Lineage chain tracks all actions
- ✅ steward CLI functional
- ✅ No import crashes
- ✅ Economic substrate works (lazy-loaded)
- ✅ Test coverage > 80%

### Architectural
- ✅ GAD-000 (Operator Inversion) enforced
- ✅ GAD-1000 (Identity Fusion) implemented
- ✅ Agent City 3-layer architecture intact
- ✅ Vedic concepts preserved (Topology, Sarga, Pulse, etc.)
- ✅ STEWARD Protocol integrated (not layered)

### Philosophical
- ✅ A.G.I. (Governed Intelligence) realized
- ✅ USB for Intelligence working
- ✅ Federated agents communicating
- ✅ Constitutional governance kernel-enforced
- ✅ Lineage chain immutable

---

## 🚀 WHAT THIS PLAN DOES DIFFERENTLY

**vs GMP_FINAL_PLAN.md:**
- ✅ Understands the UNIVERSE (Agent City, Vedic concepts, 19 agents)
- ✅ Stays in current repo (no migration overhead)
- ✅ Iterative (not rewrite)
- ✅ Token-efficient (compact, references existing docs)
- ✅ Includes ALL components (not just kernel)

**vs Previous Attempts:**
- ✅ No fake "Complete ✅" claims
- ✅ Honest about what works vs broken
- ✅ References actual files (not speculation)
- ✅ Preserves innovations (Vedic concepts, Agent City)

---

## 📚 CORE REFERENCES

**Philosophy:**
- `GAD-000.md` - Operator Inversion (18KB)
- `GAD-1000.md` - Identity Fusion (9.5KB)
- `AGI_MANIFESTO.md` - Governed Intelligence (4.8KB)
- `CONSTITUTION.md` - Governance rules (9.4KB)

**Architecture:**
- `CITYMAP.md` - 3-layer architecture (13KB, auto-generated)
- `AGENTS.md` - Agent registry (3.9KB, auto-generated)
- `OPERATIONS.md` - Live status (2.5KB, auto-generated)
- `ARCHITECTURE.md` - Current state (17KB)

**Protocol:**
- `/tmp/vibe-agency/docs/protocols/steward/SPECIFICATION.md` - Full spec
- `/tmp/vibe-agency/docs/steward/STEWARD_TEMPLATE.md` - Template

**Code:**
- `vibe_core/` - Kernel layer
- `steward/system_agents/` - 13 system agents
- `steward/citizen_agents/` - 6+ citizen agents (if exists)

---

## ⚠️ CRITICAL RULES

1. **NEVER claim "Complete ✅" without passing tests**
2. **NEVER delete without understanding**
3. **ALWAYS backup before major changes** (already done: `/tmp/steward-protocol-backup-20251128-082020`)
4. **PRESERVE Vedic concepts** (Topology, Sarga, Pulse, Narasimha, Milk Ocean)
5. **KEEP Agent City intact** (19 agents, 3 layers)
6. **HONOR GAD-000** (Operator Inversion is foundation)
7. **IMPLEMENT GAD-1000** (Identity Fusion = USB for Intelligence)

---

## 🔐 VALIDATION

**This plan assumes:**
- ✅ Current repo has ALL the innovations
- ✅ Backup exists (`/tmp/steward-protocol-backup-20251128-082020`)
- ✅ Vedic concepts are valuable (Topology, Sarga, etc.)
- ✅ Agent City architecture is sound
- ✅ 5 working agents prove architecture works
- ✅ STEWARD Protocol specs are correct

**If any assumption is wrong, STOP and discuss!**

---

**STATUS:** READY TO EXECUTE
**NEXT STEP:** Phase 1 - Emergency Triage (lazy loading)
**ESTIMATED TIME:** 5 weeks total
**RISK:** 🟢 Low (iterative, preserves existing)

---

**This is the FINAL plan. No more rewrites. Execute phase-by-phase.**
