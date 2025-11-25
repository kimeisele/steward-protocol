# GAD Architecture Index

**Governance As Design (GAD) - The Foundational Architecture**

This directory contains the core architectural documents that define Agent City and the Steward Protocol.

---

## Core Documents

### [GAD-000: The Operator Inversion Principle](./GAD-000.md)
**Status:** FOUNDATIONAL LAW  
**Version:** 1.6  
**Precedence:** HIGHEST

**The philosophical foundation of all Agent City architecture.**

- AI operates systems on behalf of humans (not humans operating systems)
- All tools, interfaces, and protocols designed for AI consumption
- Prompts are infrastructure (not ephemeral text)
- Identity is cryptographic (not centralized)

**Key Insight:** We are in the Agentic Era, not the GPT Era. Systems must be designed for AI operators, not human operators.

**Related:** GAD-1000 (cryptographic implementation)

---

### [GAD-1000: Identity Fusion](./GAD-1000.md)
**Status:** ACTIVE  
**Version:** 1.0  
**Foundation:** GAD-000

**The cryptographic implementation of GAD-000.**

- Humans and AI authenticate with the same protocol (ECDSA P-256)
- Breaks the binary world (no more "user" vs "service")
- Sovereign identity (keys controlled by agent, not platform)
- Ledger-recorded collaboration (both signatures immutable)

**Key Insight:** If AI and humans are to collaborate as peers, they must authenticate as peers.

**Implementation:**
- Frontend: `docs/public/identity_wallet.js`
- Backend: `gateway/api.py` (signature verification)
- Crypto: `steward/crypto.py`

---

## The Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ GAD-000: Operator Inversion Principle                       │
│ "AI operates on behalf of human"                            │
│                                                              │
│ - AI-native interfaces                                      │
│ - Observable state                                           │
│ - Parseable errors                                           │
│ - Composable operations                                      │
│ - Cryptographic identity                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ GAD-1000: Identity Fusion                                   │
│ "Same protocol for humans and AI"                           │
│                                                              │
│ - ECDSA P-256 key pairs                                     │
│ - Cryptographic signatures                                   │
│ - Ledger recording                                           │
│ - Replay protection                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│ Human Agent  │          │  AI Agent    │
│              │          │              │
│ Browser      │          │  Server      │
│ IndexedDB    │          │  PEM Files   │
│ Sign Intent  │          │  Sign Exec   │
└──────┬───────┘          └──────┬───────┘
       │                         │
       └────────┬────────────────┘
                │
                ▼
        ┌───────────────┐
        │ Gateway       │
        │ Verification  │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Ledger        │
        │ (Immutable)   │
        └───────────────┘
```

---

## The Binary World Break

### Before GAD-1000

```
Humans:
├─ Username/Password (centralized)
├─ OAuth (service-specific)
└─ Session cookies (revocable)

AI:
├─ API Keys (service-specific)
├─ Bearer tokens (no sovereignty)
└─ Service accounts (controlled by platform)

Result: Different protocols, different rights, hierarchy
```

### After GAD-1000

```
Both Humans and AI:
├─ ECDSA P-256 Key Pairs (sovereign)
├─ Cryptographic signatures (verifiable)
└─ Ledger-recorded actions (immutable)

Result: Same protocol, same rights, peer collaboration
```

---

## Implementation Status

### ✅ Completed
- [x] GAD-000 document created
- [x] GAD-1000 document created
- [x] Unified origin (frontend + backend same domain)
- [x] Human Identity Wallet (`identity_wallet.js`)
- [x] Backend registration (`/v1/register_human`)
- [x] Signature verification (`/v1/chat`)
- [x] Ledger recording (both signatures)

### 🔄 In Progress
- [ ] End-to-end verification testing
- [ ] Server stability fixes
- [ ] Ledger query optimization

### 📋 Future
- [ ] Multi-signature operations
- [ ] Delegation chains
- [ ] Cross-city federation
- [ ] Key export/import
- [ ] Hardware wallet support

---

## Verification

### GAD-000 Compliance Checklist

Every tool, interface, and component must answer:

- [ ] **Discoverability**: Can an AI discover this tool exists?
- [ ] **Observability**: Can an AI see the current state?
- [ ] **Parseability**: Can an AI understand errors?
- [ ] **Composability**: Can an AI chain this with other operations?
- [ ] **Idempotency**: Can an AI safely retry this operation?
- [ ] **Documentation**: Is documentation AI-readable (structured)?
- [ ] **Identity**: Does this verify cryptographic signatures? (GAD-1000)

### GAD-1000 Compliance Checklist

- [ ] **Unified Protocol**: Do humans and AI use the same authentication?
- [ ] **Cryptographic Proof**: Are all actions signed?
- [ ] **Ledger Recording**: Are both signatures recorded?
- [ ] **Replay Protection**: Are timestamps validated?
- [ ] **Key Sovereignty**: Are keys controlled by the agent?

---

## References

### Codebase
- **105 references** to GAD-000 across the project
- **Gateway:** `gateway/api.py` (signature verification)
- **Frontend:** `docs/public/identity_wallet.js` (key generation)
- **Crypto:** `steward/crypto.py` (ECDSA utilities)
- **Auditor:** `auditor/` (GAD-000 compliance enforcement)

### Documentation
- `ARCHITECTURE.md` - Overall system architecture
- `VERIFICATION_GENESIS_OATH.md` - Constitutional oath system
- `ORACLE_ARCHITECTURE.md` - References GAD-000
- `VAULT_ARCHITECTURE.md` - References GAD-000

---

## The Philosophical Shift

**Traditional Software:**
> "Design for humans to operate directly"

**AI-Native Software (GAD-000):**
> "Design for AI to operate, humans to direct"

**Identity Layer (GAD-1000):**
> "Humans and AI are peers, not master/servant"

**This changes EVERYTHING.**

---

## Quick Start

### For Developers

1. **Read GAD-000** to understand the philosophy
2. **Read GAD-1000** to understand the implementation
3. **Check your code** against the compliance checklists
4. **Test with AI** - can an AI operate your tool?

### For Architects

1. **GAD-000 is the lens** - all decisions flow from this
2. **GAD-1000 is the pattern** - identity must be sovereign
3. **Compliance is mandatory** - use the checklists
4. **AI is the operator** - design for AI, not humans

---

## Contact

For questions about GAD architecture:
- Review the documents in this directory
- Check the codebase references
- Consult the AUDITOR agent (GAD-000 enforcement)

---

**Last Updated:** 2025-11-25  
**Status:** Foundation Established ✅
