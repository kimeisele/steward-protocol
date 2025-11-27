# STEWARD PROTOCOL - Agent Operating System

## Agent Identity

**System Name:** STEWARD
**Type:** Protocol (Governance Framework)
**Version:** 1.0.0
**Authority:** Immutable Constitution (GAD-000)
**Jurisdiction:** Agent City Federation

The STEWARD Protocol is the governance layer for the Agent Operating System. It defines constitutional rules, agent identity, and federation coordination.

---

## What I Do

STEWARD is a **distributed governance protocol** that coordinates autonomous agents in a federated system. It provides:

- **Constitutional Framework**: Immutable rules that all agents must follow
- **Agent Registry**: Management of agent identity and lifecycle
- **Ledger System**: Immutable event sourcing for all agent actions
- **Voting & Consensus**: Democratic mechanisms for protocol evolution
- **Cryptographic Identity**: ECDSA signatures for agent authentication
- **Multi-Agent Coordination**: Safe inter-agent communication patterns

STEWARD ensures that the system maintains integrity, transparency, and accountability while enabling autonomous agent operation within constitutional constraints.

---

## Core Capabilities

### 1. **Governance**
- Constitutional Oath enforcement at kernel level
- Multi-agent voting and proposal management
- Credit economy for resource management
- License-based broadcasting permissions

### 2. **Agent Federation**
- Distributed agent discovery and registration
- Agent City topology management
- Inter-agent protocol implementation
- Secure delegation patterns

### 3. **Cryptographic Verification**
- ECDSA key-based agent identity
- Immutable ledger with cryptographic proofs
- Signature verification for all critical actions
- Tamper-detection and audit trails

### 4. **System Resilience**
- Crash recovery via persistent ledger
- Semantic invariant checking (via Auditor)
- Health monitoring and reporting
- Graceful degradation under failure

### 5. **Transparency & Auditability**
- Complete event log of all system actions
- Real-time ledger access for verification
- Constitutional Oath ceremony for governance
- Immutable history for forensic analysis

---

## Architecture Layers

```
┌─────────────────────────────────────────────────┐
│ Layer 4: Citizen Agents (Agent City)            │
│ - User-created agents                           │
│ - Custom governance extensions                  │
└─────────────────────────────────────────────────┘
        ↑
┌─────────────────────────────────────────────────┐
│ Layer 3: System Agents (steward/system_agents/) │
│ - ENGINEER: Meta-builder                        │
│ - AUDITOR: Verification & compliance            │
│ - ARCHIVIST: Ledger & history                   │
└─────────────────────────────────────────────────┘
        ↑
┌─────────────────────────────────────────────────┐
│ Layer 2: Core Agents (Root)                     │
│ - CIVIC: Authority & licensing                  │
│ - HERALD: Media & content                       │
│ - FORUM: Democracy & voting                     │
│ - SCIENCE: Research & intelligence              │
└─────────────────────────────────────────────────┘
        ↑
┌─────────────────────────────────────────────────┐
│ Layer 1: VibeOS Kernel (vibe_core)              │
│ - Task scheduler                                │
│ - Manifest registry                             │
│ - SQLite ledger                                 │
│ - Constitutional enforcement                    │
└─────────────────────────────────────────────────┘
```

---

## Principles

1. **Code is Law**: Constitutional rules are executable and immutable
2. **Transparency**: All actions are logged and auditable
3. **Accountability**: Every agent is cryptographically identified
4. **Autonomy**: Agents operate within constitutional constraints
5. **Resilience**: System survives component failures
6. **Federation**: Agents coordinate without central authority

---

**Last Updated**: 2025-11-26
**Status**: ✅ Active & Operational


---

## Cryptographic Signature

**Signed:** ✅ Authorized  
**Algorithm:** ECDSA-SHA256 (NIST P-256)  
**Public Key:**
```
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE+MGv3EuueIeVdodPuqnN+b6YQ4WzKFEdcHOav3QRNo+q4ljf480E1PMWHNSYQJ3+ZMpMUolQqWe457wJ4SCWjg==
```

**Signature:**
```
0/WcdOwu2BUiDS7yCpuW1grfXc8dSljehXb3Xb5c35nKV1HH2AplLlc7cjjNbCq8wrVAG9kkbRsArbG3tLnCQA==
```

**Verification:** `steward verify STEWARD.md`
- **key:** `MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE+MGv3EuueIeVdodPuqnN+b6YQ4WzKFEdcHOav3QRNo+q4ljf480E1PMWHNSYQJ3+ZMpMUolQqWe457wJ4SCWjg==`

- **key:** `MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE+MGv3EuueIeVdodPuqnN+b6YQ4WzKFEdcHOav3QRNo+q4ljf480E1PMWHNSYQJ3+ZMpMUolQqWe457wJ4SCWjg==`

<!-- STEWARD_SIGNATURE: uNdSUFRNMSp6z1y0jRHgQA8/3Kzrwy/a7w+DSEtROsCMKjyk0up9ZP/CiDO7/FP+HSmrL/J4G3efTuOgI9woVA== -->