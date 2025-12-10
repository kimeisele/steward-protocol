# OPUS-018: Senior Security Audit - Verified Findings

> **Status**: 📋 RESEARCH COMPLETE
> **Date**: 2025-12-10
> **Author**: Antigravity (Senior Architect Mode)
> **Trigger**: OPUS senior feedback requiring code-level verification

---

## Executive Summary

This document contains **code-verified** findings from the security architecture audit. Every claim has been verified with grep and file inspection against the actual codebase.

---

## VERIFIED FINDINGS

### 1. InvariantChecker NOT Wired to Kernel ✅ CONFIRMED

**OPUS Claim**: "InvariantChecker exists but is NEVER CALLED by the kernel"

**Verification**:
```bash
grep -n "invariants" vibe_core/kernel_impl.py
# Result: No matches
```

**Evidence**:
- `vibe_core/governance/invariants.py` exists with full implementation (233 lines)
- `vibe_core/tools/tool_registry.py:267-280` HAS code to use InvariantChecker
- BUT `kernel_impl.py:75` says: "ToolRegistry and ToolDiscovery are now handled by ToolsPlugin"
- The ToolsPlugin does NOT pass InvariantChecker when creating ToolRegistry

**Impact**: 🔴 HIGH - Soul rules in `config/soul.yaml` are DEAD CODE

---

### 2. ECDSA, Not Ed25519 ✅ CONFIRMED

**OPUS Claim**: "Using ECDSA, not Ed25519"

**Verification**:
```python
# steward/crypto.py:38
from ecdsa import NIST256p, SigningKey
sk = SigningKey.generate(curve=NIST256p)
```

**Evidence**:
- `steward/crypto.py:3` docstring: "Real ECDSA (Elliptic Curve Digital Signature Algorithm)"
- Uses `ecdsa` library with `NIST256p` curve
- Key storage at `.steward/keys/` with PEM format

**Impact**: 🟢 LOW - ECDSA is real asymmetric crypto. Ed25519 would be faster/simpler but ECDSA works.

---

### 3. Fake "Public Key" in identity_tool.py ✅ CONFIRMED

**OPUS Claim**: "`sha256(private_key)` is NOT a public key"

**Verification**:
```python
# vibe_core/cartridges/system/herald/tools/identity_tool.py:99
self.public_key = hashlib.sha256(self._private_key).hexdigest()
```

**Evidence**:
- Line 99 in `identity_tool.py` literally hashes the private key
- This is the FALLBACK when Steward Protocol is unavailable
- Real ECDSA keys exist in `steward/crypto.py` but identity_tool uses HMAC fallback

**Impact**: 🔴 CRITICAL - HMAC fallback is symmetric crypto (forgeable)

---

### 4. No Per-Event Signatures in Ledger ✅ CONFIRMED

**OPUS Claim**: "Ledger has hash chain but NO cryptographic signatures on individual events"

**Verification**:
```bash
grep -n "signature" vibe_core/ledger.py
# Result: No matches
```

**Evidence**:
- `ledger.py` schema (lines 136-152) has NO `signature` column
- Events have `current_hash` and `previous_hash` (tamper detection AFTER the fact)
- BUT no `agent_signature` field (preventing tampering)

**Impact**: 🟠 HIGH - DB admin can tamper and recompute chain

---

### 5. /tmp Cache ✅ CONFIRMED

**OPUS Claim**: "Cache is world-readable /tmp"

**Verification**:
```python
# vibe_core/loaders/container_loader.py:18
CACHE_DIR = Path("/tmp/vibe_cache/containers")
```

**Evidence**: Hardcoded `/tmp` path, world-readable by default

**Impact**: 🟠 HIGH - Symlink attacks, race conditions, not persistent

---

### 6. Key Storage Location ✅ EXISTS

**OPUS Claim**: "No key storage"

**Verification**:
```python
# steward/crypto.py:17-19
KEY_DIR = Path(".steward/keys")
PRIVATE_KEY_PATH = KEY_DIR / "private.pem"
PUBLIC_KEY_PATH = KEY_DIR / "public.pem"
```

**Evidence**: Key storage EXISTS at `.steward/keys/` with proper permissions (0o600)

**Impact**: 🟢 RESOLVED - This mechanism exists but is separate from identity_tool.py fallback

---

## WHAT'S ACTUALLY WORKING

| Component | Status | Evidence |
|-----------|--------|----------|
| Container Hash Verification | ✅ REAL | `container_loader.py:81-124` |
| Deterministic Hashing | ✅ FIXED | `pack_vibe.py:65` uses `sorted()` |
| SSL Verification | ✅ FIXED | `gateway/api.py` - removed `ssl=False` |
| ECDSA Crypto | ✅ REAL | `steward/crypto.py` - proper PEM keys |
| Hash Chain Ledger | ✅ REAL | `ledger.py:354-429` - verify_chain_integrity() |
| Governance Hooks | ✅ REAL | `kernel_impl.py:963-968` - on_task_pre_assign |
| Constitutional Oath | ✅ REAL | `steward_protocol/plugin_main.py:191-258` |
| Trust Scores | ✅ REAL | `steward_protocol/plugin_main.py:779-797` |
| Capability Registry | ✅ REAL | `kernel_impl.py:258` with revocation |

---

## PRIORITY ACTION STACK

| Priority | Task | Effort | Why |
|----------|------|--------|-----|
| P0 | Wire InvariantChecker into ToolsPlugin | Small | Soul rules are dead code |
| P1 | Add per-event signatures to Ledger | Medium | Prevent DB tampering |
| P1 | Fix identity_tool.py HMAC fallback | Medium | Use ECDSA from steward/crypto.py |
| P2 | Secure cache directory | Small | Move from /tmp to XDG |
| P2 | Document hollows trust model | Small | Define inheritance policy |
| P3 | OPUS-018: Key Lifecycle Design | Large | Before any asymmetric crypto work |

---

## ARCHITECTURAL DECISION REQUIRED

### Q1: Keep ECDSA or Switch to Ed25519?

**Current**: ECDSA (NIST256p) via `ecdsa` library
**Proposal**: Ed25519 via `PyNaCl`

**Tradeoffs**:
| Aspect | ECDSA (current) | Ed25519 (proposed) |
|--------|-----------------|-------------------|
| Library | `ecdsa` (pure Python) | `pynacl` (libsodium bindings) |
| Speed | Slower | 10x faster |
| Key Size | 256-bit curve | 256-bit |
| Industry | TLS/SSH standard | Modern standard |
| Complexity | More params | Simpler |

**Recommendation**: Keep ECDSA for containers, Ed25519 for new features (federation)

### Q2: InvariantChecker Wiring Location?

**Option A**: Wire in ToolsPlugin on_boot
**Option B**: Wire in kernel_impl.py directly
**Option C**: Make InvariantChecker a plugin itself

**Recommendation**: Option A - Keep ToolsPlugin responsible for ToolRegistry lifecycle

---

## NEXT STEPS

1. **Approve this audit** - Confirm findings are accurate
2. **Decide on architectural questions** - ECDSA vs Ed25519, InvariantChecker location
3. **Create implementation plan** for P0 items
4. **Execute in order** - P0 first, then P1, etc.

---

## VERIFICATION COMMANDS

```bash
# Verify InvariantChecker not in kernel
grep -rn "InvariantChecker" vibe_core/kernel_impl.py

# Verify ECDSA usage
grep -rn "NIST256p" steward/crypto.py

# Verify no signatures in ledger
grep -n "signature" vibe_core/ledger.py

# Verify /tmp cache
grep -n "CACHE_DIR" vibe_core/loaders/container_loader.py

# Run all container tests
pytest tests/unit/test_container_loader.py tests/integration/test_container_integrity.py -v
```
