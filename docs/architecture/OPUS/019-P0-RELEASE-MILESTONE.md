# OPUS-019: Security Milestone - P0 Complete

> **Status**: ✅ RELEASED
> **Date**: 2025-12-10
> **Branch**: main @ 1b3eb29
> **Author**: Antigravity

<!-- @HARNESS
files:
  - path: vibe_core/cartridges/system/herald/tools/identity_tool.py
    required: true
  - path: vibe_core/plugins/tools/plugin_main.py
    required: true
  - path: steward/crypto.py
    required: true
tests:
  - tests/unit/test_crypto_verification.py
wiring:
  - pattern: "from steward.crypto import"
    in: vibe_core/cartridges/system/herald/tools/identity_tool.py
  - pattern: "InvariantChecker"
    in: vibe_core/plugins/tools/plugin_main.py
  - pattern: "STEWARD_CRYPTO_AVAILABLE"
    in: vibe_core/cartridges/system/herald/tools/identity_tool.py
absent:
  - pattern: "hmac\\.new"
    in: vibe_core/cartridges/system/herald/tools/identity_tool.py
  - pattern: "sha256.*_private_key.*hexdigest"
    in: vibe_core/cartridges/system/herald/tools/identity_tool.py
config:
  - section: opus.verification
-->

---

## Release Summary

**P0 (Critical Security Fixes) - COMPLETE**

This release addresses the critical security vulnerabilities identified in OPUS-017 and OPUS-018.

---

## What Was Fixed

### P0.1: HMAC → ECDSA in identity_tool.py ✅
**Commit**: 2011e7b

| Before | After |
|--------|-------|
| `sha256(private_key)` "public key" | Real ECDSA PEM keypairs |
| `hmac.new()` symmetric signing | ECDSA asymmetric signatures |
| Anyone with key can forge | Only private key holder can sign |

**Files Changed**:
- `vibe_core/cartridges/system/herald/tools/identity_tool.py`
- `tests/unit/test_crypto_verification.py`

### P0.2: Wire InvariantChecker for soul.yaml Enforcement ✅
**Commit**: 2288072

| Before | After |
|--------|-------|
| soul.yaml rules were DEAD CODE | 8 rules enforced on every tool call |
| `.git/` writes allowed | 🛡️ BLOCKED |
| `kernel.py` writes allowed | 🛡️ BLOCKED |
| `soul.yaml` writes allowed | 🛡️ BLOCKED |

**Files Changed**:
- `vibe_core/plugins/tools/plugin_main.py`

---

## Verification Proof

```bash
# P0.1 - ECDSA signing works
$ python -c "from steward.crypto import load_or_generate_keys, sign_content, verify_signature; \
  priv, pub = load_or_generate_keys(); \
  sig = sign_content('test', priv); \
  print(f'Valid: {verify_signature(\"test\", sig, pub)}')"
Valid: True

# P0.2 - Soul governance active
$ python -c "from vibe_core.governance import InvariantChecker; \
  c = InvariantChecker('config/soul.yaml'); \
  print(f'Rules: {c.rule_count}'); \
  print(f'.git blocked: {not c.check_tool_call(\"write_file\", {\"path\": \".git/x\"}).allowed}')"
Rules: 8
.git blocked: True
```

---

## Remaining Roadmap

| Priority | Task | Status | Notes |
|----------|------|--------|-------|
| P0.1 | HMAC → ECDSA | ✅ DONE | identity_tool.py now uses real crypto |
| P0.2 | Wire InvariantChecker | ✅ DONE | soul.yaml rules enforced |
| **P1** | **Per-event ledger signatures** | 📋 TODO | Add `agent_signature` to ledger events |
| P2 | Secure cache dir | 📋 TODO | Move `/tmp` → `~/.cache/vibe/` |
| P2 | Hollows trust model | 📋 TODO | Define nested container trust |
| P3 | Federation TLS | 📋 TODO | Cert pinning for peers |

---

## P1 Clarification

**What P1 IS**:
- Add cryptographic signature field to each ledger event
- Agent signs event before recording
- Prevents DB admin from tampering and recomputing hash chain

**What P1 is NOT**:
- NOT changing the hash chain (keep it)
- NOT changing crypto library (keep ECDSA)
- NOT about containers (that's done)

**Why it matters**:
- Current hash chain detects tampering AFTER THE FACT
- Per-event signatures PREVENT tampering (can't forge without private key)

---

## Test Commands

```bash
# Run all container security tests
pytest tests/integration/test_container_integrity.py -v

# Run crypto verification test  
pytest tests/unit/test_crypto_verification.py -v

# Verify InvariantChecker rules
python -c "from vibe_core.governance import InvariantChecker; print(InvariantChecker('config/soul.yaml').get_rule_ids())"
```
