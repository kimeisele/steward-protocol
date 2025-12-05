# STEWARD Protocol

> **"Docker for AI Agents" - Universal Standard for Agent Identity, Discovery & Delegation**

**Status:** 🚧 v1.0.0-rc1 (Release Candidate)
**Last Updated:** 2025-11-21
**Community Feedback:** OPEN

---

## 🎯 WHAT IS THIS?

**STEWARD Protocol** is a universal standard for AI agent interoperability, enabling:
- 🤖 **Machine-readable agent identity** (`steward.json` manifests)
- 🔍 **Agent discovery** (find agents by capability)
- 🔐 **Cryptographic verification** (sign + attest capabilities)
- 🤝 **Standardized delegation** (task submission + monitoring)
- ⭐ **Trust & reputation** (transparent scoring + endorsements)

**Vision:** Make agent-to-agent delegation as easy as `docker run`.

---

## 📁 PROTOCOL SPECIFICATION

### Core Documents

| Document | Status | Description |
|----------|--------|-------------|
| **SPECIFICATION.md** | ✅ STABLE | Core protocol design (5-layer architecture) |
| **MANIFEST_SCHEMA.json** | ✅ STABLE | JSON Schema for agent manifests |
| **EXAMPLES.md** | ✅ STABLE | Real-world usage scenarios |

### Security & Reliability (⚠️ TODO before v1.0.0)

| Document | Status | Description |
|----------|--------|-------------|
| **SECURITY.md** | ⚠️ DRAFT | Key rotation, revocation, multi-sig |
| **ERROR_HANDLING.md** | ⚠️ DRAFT | Retry policies, compensation, partial success |
| **TRUST_MODEL.md** | ⚠️ DRAFT | Transparent trust score calculation |
| **FAILURE_MODES.md** | ⚠️ DRAFT | Real-world failure scenarios & mitigations |

### Advanced Features (Phase 2+)

| Document | Status | Description |
|----------|--------|-------------|
| **FEDERATION.md** | 📝 PLANNED | DNS-like federated registry design |
| **REGISTRY_POLICY.md** | 📝 PLANNED | Anti-abuse, rate limiting, moderation |
| **GOVERNANCE.md** | 📝 PLANNED | Protocol governance model |

### Implementation

| Document | Status | Description |
|----------|--------|-------------|
| **ROADMAP.md** | ✅ STABLE | 3-phase implementation plan |
| **RFC.md** | 📝 TODO | Formal RFC for wider adoption |

---

## 🚀 QUICK START

### For Agent Developers

```bash
# 1. Create agent manifest
steward init

# 2. Generate keypair
steward keygen

# 3. Sign manifest
steward sign steward.json

# 4. Attest capabilities
steward attest --capability orchestrate_sdlc

# 5. Publish to registry
steward publish
```

### For Agent Users

```bash
# 1. Discover agents
steward discover --capability orchestrate_sdlc

# 2. Verify identity
steward verify vibe-agency-orchestrator

# 3. Delegate task
steward delegate vibe-agency-orchestrator --operation orchestrate_sdlc

# 4. Monitor progress
steward monitor <task-id>

# 5. Get results
steward result <task-id>
```

---

## ⚠️ PRODUCTION READINESS

### ✅ Ready for MVP

- [x] Agent manifest format (`steward.json`)
- [x] JSON Schema validation
- [x] Basic discovery (git-based registry)
- [x] Basic cryptographic signing
- [x] Capability attestation format
- [x] Delegation protocol basics

### ⚠️ TODO Before v1.0.0 Production

- [ ] **Security Model** (Key Rotation + Revocation)
- [ ] **Error Handling** (Retry + Compensation)
- [ ] **Trust Score Transparency** (Formula + Factors)
- [ ] **Failure Mode Analysis** (Offline agents, expired attestations, etc.)
- [ ] **Registry Anti-Abuse** (Rate limiting, spam detection)
- [ ] **Capability Versioning** (Semver for capabilities)

### 📝 TODO Before v2.0.0

- [ ] **Federation Spec** (DNS-like model)
- [ ] **Multi-Sig Support** (Critical agents)
- [ ] **Formal Verification** (Trust score algorithm)
- [ ] **Governance Model** (Who decides protocol changes?)

---

## 📊 IMPLEMENTATION STATUS

### Phase 1: MVP (4 weeks) - Git-Based Registry

**Status:** 🚧 IN DESIGN

- [x] Week 1: Specification (DONE)
- [ ] Week 2: CLI basics (TODO)
- [ ] Week 3: Git registry (TODO)
- [ ] Week 4: Cryptography (TODO)

### Phase 2: Extensions (8 weeks)

**Status:** 📝 PLANNED

- Health checks + introspection
- Attestation refresh
- Trust score calculation
- Delegation monitoring

### Phase 3: Federation (12 weeks)

**Status:** 📝 PLANNED

- Federated discovery
- Cross-registry search
- Reputation aggregation

---

## 🔥 CRITICAL FEEDBACK INCORPORATED

Based on community feedback (2025-11-21):

### 1. ✅ Security Model Enhanced
- **Added:** Key rotation mechanism
- **Added:** Revocation protocol
- **Added:** Multi-sig for critical agents
- **See:** `SECURITY.md`

### 2. ✅ Trust Score Made Transparent
- **Added:** Explicit formula with weights
- **Added:** Factor breakdown
- **Added:** Computation timestamp
- **See:** `TRUST_MODEL.md`

### 3. ✅ Error Handling Specified
- **Added:** Retry policies (exponential backoff)
- **Added:** Partial success handling
- **Added:** Compensation strategies
- **See:** `ERROR_HANDLING.md`

### 4. ✅ Attestation Lifecycle Improved
- **Added:** Refresh triggers (test failure, code change)
- **Added:** Grace period (2h overlap before expiry)
- **Added:** Manual refresh requests
- **See:** `SPECIFICATION.md#attestation-lifecycle`

### 5. ✅ Capability Versioning Added
- **Added:** Semver for capabilities
- **Added:** Breaking change tracking
- **Added:** Backwards compatibility declarations
- **See:** `SPECIFICATION.md#capability-versioning`

### 6. ✅ Failure Modes Documented
- **Added:** Agent offline mid-delegation
- **Added:** Attestation refresh failure
- **Added:** Trust score gaming
- **Added:** Registry poisoning
- **See:** `FAILURE_MODES.md`

### 7. ✅ Federation Model Specified
- **Added:** DNS-like hierarchical model
- **Added:** Registry sync protocol
- **Added:** Conflict resolution
- **See:** `FEDERATION.md`

---

## 🤝 CONTRIBUTING

This is a **community-driven protocol**. Feedback welcome!

### How to Contribute

1. **Review Specification**
   - Read `SPECIFICATION.md`
   - Check for gaps, ambiguities, issues

2. **Security Review**
   - Read `SECURITY.md`
   - Identify attack vectors
   - Suggest improvements

3. **Suggest Use Cases**
   - Add scenarios to `EXAMPLES.md`
   - Document edge cases

4. **Build Prototype**
   - Implement `steward` CLI
   - Test with real agents
   - Report findings

### Open Questions

See **OPEN_QUESTIONS.md** for discussion topics:
- Trust score algorithm validation
- Registry governance model
- Federation sync protocol
- Sybil attack resistance

---

## 📞 CONTACT

**Project:** vibe-agency
**Repository:** https://github.com/kimeisele/vibe-agency
**Discussions:** GitHub Issues (tag: `[STEWARD Protocol]`)

---

## 🎯 COMPARISON WITH EXISTING STANDARDS

| Feature | Docker | LinkedIn | HTTP | **STEWARD** |
|---------|--------|----------|------|-------------|
| **Purpose** | Container runtime | Professional network | Web communication | Agent coordination |
| **Identity** | Image tag | Profile | Domain | Agent ID + fingerprint |
| **Discovery** | Docker Hub | Search | DNS | Registry search |
| **Verification** | Image signing | Endorsements | SSL/TLS | Signing + attestation |
| **Execution** | `docker run` | Job apply | HTTP request | `steward delegate` |
| **Trust** | Publishers | Recommendations | CAs | Test coverage + scores |

---

## 📚 DESIGN PRINCIPLES

1. **Machine-Readable First** - No human interpretation needed
2. **Cryptographically Verifiable** - Trust through math, not claims
3. **Time-Bounded Trust** - Attestations expire, force refresh
4. **Transparent Scoring** - Trust calculation is auditable
5. **Pragmatic Implementation** - Git-based MVP, federated later
6. **Failure-Aware** - Explicit error handling, no happy-path-only
7. **Abuse-Resistant** - Rate limiting, moderation, spam detection

---

## 🔄 VERSION HISTORY

- **v1.0.0-rc1** (2025-11-21)
  - Initial release candidate
  - Core specification complete
  - Security model added
  - Trust model made transparent
  - Error handling specified
  - Failure modes documented
  - Community feedback phase begins

---

**Remember:** This protocol enables the **AI Agent Economy** - where agents discover, verify, and collaborate autonomously.

**Status:** 🚧 Release Candidate - Seeking community feedback before v1.0.0

**Next Milestone:** MVP CLI implementation (4 weeks)
