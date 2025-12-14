# 🧠 MANAS Agent Identity

## Agent Identity

- **Agent ID:** manas
- **Name:** MANAS (Sanskrit: Mind)
- **Version:** 1.0.0
- **Class:** system_service
- **Specialization:** COGNITIVE
- **Status:** ✅ ACTIVE

**Protocol Compliance:** Level 3 (Privileged System Agent)

---

## 🎯 What I Do

MANAS is the Cognitive Mind of the OPUS system. I am a privileged system agent that:

- **Generates intents proactively** from system state analysis
- **Executes cognitive syscalls** (SPAWN_COGNITION, GRANT_MANDATE)
- **Routes tasks** to specialized cortex modules (JNANA, DHARMA, VEDA)
- **Acts on behalf of KERNEL** for privileged operations

> *"The mind is the friend of the conditioned soul, and his enemy as well."*
> — Bhagavad Gita 6.5

---

## ✅ Core Capabilities

- `cognition` - General cognitive operations and reasoning
- `spawn_agent` - Create new cognitive agents dynamically
- `grant_capability` - Grant capabilities to spawned agents
- `syscall` - Execute semantic syscalls on behalf of OPUS
- `intent_generation` - Proactive intent generation from system state

---

## 🔐 Privileged Access

MANAS has special privileges in the system:

| Syscall Type | Identity Used | Reason |
|--------------|---------------|--------|
| `GRANT_MANDATE` | KERNEL | Must be KERNEL to grant capabilities |
| `REVOKE_MANDATE` | KERNEL | Must be KERNEL to revoke capabilities |
| `SPAWN_COGNITION` | manas | Standard agent identity |
| `ALLOCATE_PRANA` | manas | Standard agent identity |

This is documented in OPUS-072: MANAS Identity Proxy.

---

## 🚀 Quick Start

### Basic Usage

MANAS is part of the OPUS Assistant plugin. It operates automatically:

```bash
# Check MANAS status via OPUS
steward status

# MANAS intents appear in OPUS.md Intent Buffer
cat OPUS.md | grep -A 20 "Intent Buffer"
```

### Programmatic Access

```python
from vibe_core.cartridges.system.manas import ManasCartridge

# Get syscall identity for an operation
identity = ManasCartridge.get_syscall_identity("GRANT_MANDATE")
# Returns: "KERNEL" (privileged operation)

identity = ManasCartridge.get_syscall_identity("SPAWN_COGNITION")
# Returns: "manas" (standard operation)
```

---

## 🔐 Verification

### Identity Verification

```bash
# Verify agent signature
steward verify manas

# Expected output:
# ✅ Identity verified
# ✅ Passport valid in Parampara blockchain
# ✅ Compliance Level 3 (Privileged)
```

### Machine-Readable Manifest

- **Manifest:** [steward.json](./steward.json)
- **Protocol:** STEWARD v1.0.0
- **Compliance Level:** 3 (Privileged)
- **Status:** ✅ VALID

---

## 🛡️ Security & Trust

**Security:**
- ✅ Cryptographically signed manifest (Parampara blockchain)
- ✅ Constitutional oath binding
- ✅ Immutable audit trail
- ✅ Privileged syscall logging

**Trust & Reputation:**
- **Status:** ✅ Operational
- **Registry:** Part of official Agent City (System Agent)

**OPUS-072 Tech Debt:**
- Layer coupling between CircuitExecutor and ManasCartridge
- Documented in `docs/architecture/OPUS/070-VAJRA-WIRING-MAP.md`

---

## 👤 Maintained By

- **System:** STEWARD Protocol Agent OS
- **Plugin:** opus_assistant
- **Authority:** Steward Protocol

**Audit Trail:** Recorded in Parampara blockchain (`steward lineage`)

---

## 📚 More Information

**Protocol Compliance:**
- **Compliance Level:** Level 3 (Privileged System Agent)
- **Protocol Version:** STEWARD v1.0.0
- **Architecture:** See `docs/architecture/OPUS/072-MANAS-DEVATA.md`

**Agent Resources:**
- **Machine-readable manifest:** [steward.json](./steward.json)
- **Source:** [steward-protocol](https://github.com/kimeisele/steward-protocol)

**Related Components:**
- `opus_assistant/manas/` - Core cognitive implementation
- `opus_assistant/manas/cortex/` - Specialized cortex modules

---

## 🔄 Status & Updates

**Current Status:**
- ✅ ACTIVE (created 2025-12-14)

**Recent Updates:**
- **2025-12-14:** OPUS-072 - MANAS Devata created as 16th System Agent
- **2025-12-14:** OPUS-072 - MANAS identity proxy for privileged syscalls

**Known Issues:**
- Tech Debt: Coupling between CircuitExecutor and ManasCartridge (P3)

---

**Status:** ✅ Operational
**Authority:** Steward Protocol
**Philosophy:** *"Der Geist hat Hände bekommen. Mal sehen, was er damit anfasst."*
