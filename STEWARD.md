# STEWARD Protocol: Agent City Federation Constitution

> **STEWARD Protocol v1.1.0 | Agent City Alpha Governance**
> *The foundation for sovereign, federated agent collaboration*

---

## 🏙️ AGENT CITY FEDERATION `[REQUIRED]`

**Agent City Alpha** is a living, emergent multi-agent ecosystem built on the STEWARD Protocol. It is **not a platform**—it is an **ecology**.

### City Structure

The federation consists of four primary districts, each governed by specialized agents:

| District | Agent | Function | Authority |
|----------|-------|----------|-----------|
| **Infrastructure** | 🏛️ **CIVIC** | Registration, licensing, credits, governance | Constitutional Authority |
| **Media** | 🦅 **HERALD** | Content, publishing, broadcasting, intelligence | Licensed by CIVIC |
| **Democracy** | 🗳️ **FORUM** | Proposals, voting, collective decision-making | CIVIC execution |
| **Research** | 🔬 **SCIENCE** | External intelligence, research, validation | Tavily-integrated |

Plus **supporting districts**: ARCHIVIST (audit), ARTISAN (media ops), AUDITOR (compliance), ENGINEER (meta-builder), WATCHMAN (monitoring).

### The Living System

This is not a fixed architecture—it is **emergent and self-organizing**. The system exhibits:
- **Self-surprise**: When SCIENCE discovers unexpected patterns or CITYMAP auto-regenerates
- **Economic constraints**: Credits create meaningful scarcity, forcing governance
- **Democratic override**: FORUM can alter CIVIC's rules through voting
- **Autonomy with accountability**: Each agent acts independently but registers with CIVIC

---

## 🎯 The STEWARD Protocol: Open Standard for Sovereign Agents

The STEWARD Protocol defines **how agents identify themselves, prove capabilities, and collaborate in a trustless environment**.

### Core Principles

1. **Sovereignty**: Agents maintain cryptographic identity independent of registries
2. **Interoperability**: Agents work across platforms and organizational boundaries
3. **Trust-Minimized**: Verification via signatures, attestations, reputation—not central authority
4. **Graceful Degradation**: Varying compliance levels for different use cases
5. **Transparency**: All agent claims are verifiable and auditable

---

## ✅ Agent City Capabilities

### CIVIC (Authority Layer)
- `agent_registration` - Citizens registry and identity assignment
- `broadcast_licensing` - Permission to publish (revocable)
- `credit_system` - Economic constraints on action
- `ledger` - Immutable transaction record

### HERALD (Media Layer)
- `content_generation` - LLM-based article/code generation
- `broadcast` - Social media publishing (Twitter, Reddit)
- `research` - External intelligence via Tavily
- `identity_signing` - Cryptographic STEWARD Protocol identity

### FORUM (Democracy Layer)
- `proposals` - Governance change requests
- `voting` - Agent voting on constitutional amendments
- `execution` - Enacting FORUM decisions via CIVIC

### SCIENCE (Research Layer)
- `external_search` - Real-world intelligence gathering
- `validation` - Fact-checking and source verification
- `discovery` - Emergent pattern recognition

### ARCHIVIST (Audit Layer)
- `attestation` - Cryptographic proof of events
- `ledger_verification` - STEWARD Protocol signature validation
- `history` - Immutable timeline of all decisions

---

## 🚀 Quick Start: Running Agent City

### Essential Commands

```bash
# 1. Register all agents and create citizens registry
python3 -c "from civic.cartridge_main import CivicCartridge; c = CivicCartridge(); c.scan_and_register_agents()"

# 2. Regenerate AGENTS.md from live registry
python3 -c "from civic.cartridge_main import CivicCartridge; c = CivicCartridge(); c.update_agents_registry()"

# 3. Regenerate CITYMAP.md from agent topology
python3 -c "from civic.tools.map_tool import MapTool; m = MapTool('.'); m.generate_citymap()"

# 4. Load and apply configuration matrix
python3 -c "import yaml; cfg = yaml.safe_load(open('config/matrix.yaml')); print(f\"City: {cfg['city_name']}\")"
```

### Configuration

Edit `config/matrix.yaml` to tune the city without code changes:
- Governance thresholds
- Credit allocations
- Agent parameters (frequency, providers, etc.)
- Economy settings

---

## 📊 Quality Guarantees `[STANDARD]`

**Current Metrics:**
- **Protocol Coverage:** 100% of agent lifecycle
- **Test Coverage:** 85%+ (steward/specification, test suite)
- **Documentation:** Complete (SPECIFICATION.md, GRACEFUL_DEGRADATION.md, FEDERATION.md)
- **Community:** Open source, permissive licensing

---

## 🔐 Verification `[STANDARD]`

### Identity Verification

```bash
# Verify organization identity
steward verify org.vibe.steward

# Expected output:
# ✅ Identity verified
# ✅ Organization: Steward Protocol
# ✅ Type: Organization (Maintainer)
# ✅ Compliance Level: 2
```

### Manifest & Attestations

- **Machine-readable specification:** [steward/SPECIFICATION.md](./steward/SPECIFICATION.md)
- **Schema:** [steward/STEWARD_JSON_SCHEMA.json](./steward/STEWARD_JSON_SCHEMA.json)
- **Status:** ✅ ACTIVE

---

## 🤝 Agent City Federation: Resident Agents

### Primary Districts (Constitutional Agents)

This federation hosts specialized agents implementing the STEWARD Protocol:

| Agent | Domain | Role | Registry |
|-------|--------|------|----------|
| **CIVIC** | Infrastructure | Constitutional Authority, Registry, Licensing | [AGENTS.md](./AGENTS.md) |
| **HERALD** | Media | Content, Broadcasting, Intelligence Gathering | [AGENTS.md](./AGENTS.md) |
| **FORUM** | Democracy | Proposals, Voting, Governance Amendment | [AGENTS.md](./AGENTS.md) |
| **SCIENCE** | Research | External Intelligence, Fact-Checking, Validation | [AGENTS.md](./AGENTS.md) |

### Supporting Districts

- **ARCHIVIST** - Audit, attestation, ledger verification
- **ARTISAN** - Media ops, image processing, branding
- **AUDITOR** - Compliance verification, GAD-000 enforcement
- **ENGINEER** - Meta-builder, scaffolding, code generation
- **WATCHMAN** - System monitoring and surveillance

### Agent Discovery

```bash
# View current citizens registry
cat AGENTS.md

# View system topology and dependencies
cat CITYMAP.md

# Inspect individual agent status
python3 -c "from civic.cartridge_main import CivicCartridge; c = CivicCartridge(); print(c.check_broadcast_license('herald'))"
```

---

## 👤 Maintained By `[REQUIRED]`

- **Organization:** `Vibe Inc. / STEWARD Protocol Contributors`
- **Contact:** `GitHub Issues: https://github.com/kimeisele/steward-protocol/issues`
- **Repository:** `https://github.com/kimeisele/steward-protocol`

**`[STANDARD]` Additional info:**
- **Principal:** `kimeisele (Tech Lead)`
- **Transparency:** `Public` (open-source protocol)
- **License:** `MIT` (permissive, commercial use allowed)

---

## 📚 More Information `[STANDARD]`

**Protocol Compliance:**
- **Compliance Level:** Level 2 (Standard)
- **Protocol Version:** STEWARD v1.1.0
- **Full Specification:** [steward/SPECIFICATION.md](./steward/SPECIFICATION.md)
- **Graceful Degradation Model:** [steward/GRACEFUL_DEGRADATION.md](./steward/GRACEFUL_DEGRADATION.md)

**Organization Resources:**
- **Protocol Documentation:** [steward/README.md](./steward/README.md)
- **Federation Model:** [steward/FEDERATION.md](./steward/FEDERATION.md)
- **Trust Model:** [steward/TRUST_MODEL.md](./steward/TRUST_MODEL.md)
- **Security Guidelines:** [steward/SECURITY.md](./steward/SECURITY.md)
- **Agent Template:** [steward/templates/STEWARD_TEMPLATE.md](./steward/templates/STEWARD_TEMPLATE.md)
- **Source Code:** `https://github.com/kimeisele/steward-protocol`

**Registry:**
- **Status:** Open-source protocol (no centralized registry yet)
- **Roadmap:** [steward/ROADMAP.md](./steward/ROADMAP.md)

---

## 🧹 Tidy Protocols (Repository Maintenance)

**Purpose:** HERALD maintains repository hygiene through autonomous organization. Tidy Protocols define how files are organized and which paths are protected from modification.

### Organization Rules

Files matching these patterns are automatically organized by HERALD's Tidy capability:

```
* .log files       -> data/logs/
* .jsonl files     -> data/history/
* .csv files       -> data/analysis/
* *.png, *.jpg     -> assets/media/
* temp_*, debug_*  -> _archive/quarantine/
```

### Protected Paths (IMMUTABLE)

These paths are **NEVER** modified by Tidy:

```
herald/                 (HERALD's core logic)
.github/                (GitHub workflows & config)
STEWARD.md              (This protocol document)
STEWARD_SIGNATURE       (Protocol verification)
requirements.txt        (Dependencies)
.gitignore              (Version control rules)
*.md (documentation)    (Human-written guides)
*.py (in root)          (Script layer)
```

**Consequence:** If a file matches a protected pattern, it is left untouched. Tidy silently skips it.

### Logging

Every Tidy action is reported via the Scribe:
- *"🧹 TIDY: Organized X files into Y directories"*
- *"⚠️  TIDY: 3 files match protected patterns (skipped)"*

---

## 🔄 Status & Updates `[STANDARD]`

**Current Status:**
- ✅ **AGENT CITY ALPHA OPERATIONAL** - Live federated multi-agent system with 4 primary districts and 5 supporting services
- ✅ Constitutional governance with CIVIC authority, FORUM voting, and SCIENCE intelligence
- ✅ Credit-based economy creating scarcity and forcing governance
- ✅ Emergent behavior: System surprises itself (CITYMAP auto-regeneration, SCIENCE discovery)

**Recent Updates:**
- **2025-11-24:** THE MATRIX (config/matrix.yaml) introduced - centralized configuration without code changes
- **2025-11-24:** STEWARD.md updated to reflect Agent City Federation (Constitution as living document)
- **2025-11-23:** SCIENCE DISTRICT fully integrated - external intelligence module (Tavily-based)
- **2025-11-22:** THE FORUM operational - democratic governance and proposal system
- **2025-11-21:** Federation model specification released
- **2025-11-20:** Trust model and SLA framework defined

**Known Issues:**
- None critical (active development phase)

---

## 🧬 Design Principles `[ADVANCED]`

**Core Principles:**
1. **Sovereignty**: Agents maintain cryptographic self-identity independent of registries
2. **Interoperability**: Agents work across different platforms and organizational boundaries
3. **Trust-Minimized**: Verification via signatures, attestations, and reputation—not central authority
4. **Graceful Degradation**: Support varying compliance levels for different use cases
5. **Transparency**: All agent claims are verifiable and auditable

---

**Federation Version:** 1.0.0 (Agent City Alpha)
**Protocol Version:** STEWARD v1.1.0
**Constitution Version:** 1.0.0
**Last Updated:** 2025-11-24

<!-- STEWARD_SIGNATURE: Updated to reflect Agent City Federation governance structure and THE MATRIX configuration system -->
