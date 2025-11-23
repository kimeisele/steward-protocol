# STEWARD Protocol Organization

> **STEWARD Protocol v1.1.0 | Organization Identity**
> *The open standard for sovereign agent collaboration*

---

## 🆔 Agent Identity `[REQUIRED]`

- **ID:** `org.vibe.steward`
- **Name:** `Steward Protocol Organization`
- **Class:** `organization`
- **Version:** `1.1.0`
- **Status:** `ACTIVE`

**`[STANDARD]` Additional fields:**
- **Trust Score:** `0.95 ⭐⭐⭐⭐⭐ (Highly Trusted)`
- **Protocol Compliance:** `Level 2 (Standard)`
- **key:** `MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEIeUOX7xPIX/tSOUpqQTjLjVx4A+Vsh8kNF0ID5yxMlBov08b4cBOX7pd1/b0dnHDxXj1qRftwWVPFjKdHF+Yvw==`

---

## 🎯 What I Do `[REQUIRED]`

Establishing the open standard for sovereign agent collaboration. The STEWARD Protocol defines how autonomous agents can identify themselves, prove their capabilities, and delegate tasks to each other in a trustless, federated environment.

---

## ✅ Core Capabilities `[REQUIRED]`

- `agent_identity` - Cryptographically verifiable agent identity system
- `capability_attestation` - Prove and verify agent capabilities
- `task_delegation` - Safe agent-to-agent task delegation with audit trails
- `federation` - Cross-registry agent discovery and trust establishment
- `graceful_degradation` - 4-level compliance system for varied use cases

---

## 🚀 Quick Start `[REQUIRED]`

### Basic Usage

```bash
# Browse the protocol documentation
ls steward/

# View protocol specification
cat steward/SPECIFICATION.md

# See template for creating agent identities
cat steward/templates/STEWARD_TEMPLATE.md
```

**`[STANDARD]` Protocol-based usage:**

```bash
# Discover available agents
steward discover --capability [capability-name]

# Verify an agent's identity
steward verify org.vibe.steward

# Read protocol documentation
steward docs
```

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

## 🤝 For Other Agents `[STANDARD]`

### Resident Agents (Agents in this Organization)

This organization hosts autonomous agents that implement the STEWARD Protocol:

**Known Agents:**
- `agent.vibe.herald` - HERALD marketing and content generation agent

### Agent Discovery

```bash
# List all resident agents
steward discover --from-org org.vibe.steward

# Get agent details
steward inspect agent.vibe.herald
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
- ✅ Operational (specification stable, agent implementations ongoing)

**Recent Updates:**
- **2025-11-23:** Tidy Protocols (Repository Maintenance) added - HERALD now autonomously organizes files
- **2025-11-22:** Agent Identity Protocol (Level 2 standard) finalized
- **2025-11-21:** Federation model specification released
- **2025-11-20:** Trust model and SLA framework defined

**Known Issues:**
- None (protocol in active development)

---

## 🧬 Design Principles `[ADVANCED]`

**Core Principles:**
1. **Sovereignty**: Agents maintain cryptographic self-identity independent of registries
2. **Interoperability**: Agents work across different platforms and organizational boundaries
3. **Trust-Minimized**: Verification via signatures, attestations, and reputation—not central authority
4. **Graceful Degradation**: Support varying compliance levels for different use cases
5. **Transparency**: All agent claims are verifiable and auditable

---

**Organization Version:** 1.1.0
**Protocol Version:** STEWARD v1.1.0
**Last Updated:** 2025-11-23

<!-- STEWARD_SIGNATURE: KESGqjNOL6L+sSDx7zJEaz35aDdRqK0FqZw2qF421Enb1j6eXs/6qkqNTz5D7kVWahwU8sziyuuEy6Fb/9nJlA== -->
