# OPUS-015a: Security Architecture Addendum

> **Status**: SUPERSEDED
> **Date**: 2025-12-10
> **Author**: Senior Architect (Self-Audit)
> **Parent**: OPUS-015 (Container Format)
> **Superseded By**: OPUS-018, OPUS-019 (ECDSA implementation)

<!-- @HARNESS
files:
  - path: vibe_core/steward/crypto.py
    required: true
  - path: vibe_core/loaders/container_loader.py
    required: true
  - path: tests/unit/test_crypto_verification.py
    required: true
  - path: tests/integration/test_container_integrity.py
    required: true
tests:
  - tests/unit/test_crypto_verification.py
  - tests/integration/test_container_integrity.py
wiring:
  - pattern: "NIST256p"
    in: vibe_core/steward/crypto.py
  - pattern: "_verify_signature"
    in: vibe_core/loaders/container_loader.py
-->

---

## Status: SUPERSEDED

This document proposed Ed25519 for container signing. The actual implementation used **ECDSA (NIST P-256)** instead.

### What Was Actually Implemented

| Proposed (015a) | Actual Implementation |
|-----------------|----------------------|
| Ed25519 via PyNaCl | ECDSA via `ecdsa` library |
| `vibe_core/plugins/crypto/` | `vibe_core/steward/crypto.py` |
| New CryptoPlugin | Integrated into steward module |

### Current Crypto Status

- **Location**: `vibe_core/steward/crypto.py`
- **Algorithm**: ECDSA NIST P-256
- **Tests**: `tests/unit/test_crypto_verification.py`
- **Container Signing**: `vibe_core/loaders/container_loader.py` (v2 ECDSA format)

### Resolved Issues from Original Proposal

| Original Issue | Resolution |
|---------------|------------|
| HMAC symmetric crypto | ECDSA asymmetric (OPUS-019) |
| `sha256(private_key)` fake public key | Real ECDSA keypairs (OPUS-019) |
| `/tmp` cache insecure | Still TODO (P2) |
| Hollows trust model undefined | Still TODO (P2) |

---

## Reference

See:
- **OPUS-018**: Security audit findings
- **OPUS-019**: P0 security fixes (ECDSA implementation)

---

*Superseded 2025-12-11 - Original proposal replaced by ECDSA implementation*
