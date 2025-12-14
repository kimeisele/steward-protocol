# OPUS-039: ECDSA Signing Regression Analysis

**Status:** 🔴 INVESTIGATION IN PROGRESS
**Severity:** CRITICAL (CI Build Failure)
**Discovered:** 2025-12-14
**Reporter:** OPUS Assistant

## Executive Summary

The container signing mechanism has a **silent fallback bug** that causes containers to be unsigned in CI, failing the build. This report documents the investigation and proposes systematic fixes.

## The Bug Pattern

```
pack_vibe.py line 21-33:
┌─────────────────────────────────────────────────────────┐
│  try:                                                    │
│      from vibe_core.steward.crypto import (              │
│          get_public_key_fingerprint,                     │
│          load_or_generate_keys,                          │
│          sign_content,                                   │
│      )                                                   │
│      CRYPTO_AVAILABLE = True    ← SUCCESS PATH           │
│  except ImportError:                                     │
│      CRYPTO_AVAILABLE = False   ← SILENT FAILURE         │
│      load_or_generate_keys = None                        │
│      sign_content = None                                 │
│      get_public_key_fingerprint = None                   │
└─────────────────────────────────────────────────────────┘
```

When `CRYPTO_AVAILABLE = False`:
1. Container is built with hash-only signature (v1 format)
2. CI checks for `'"version": 2'` in SIGNATURE.sig
3. Check fails → BUILD FAILS

## Proof of Concept

```python
# v1 signature (hash only) - what happens when crypto fails:
SIGNATURE.sig = "e4544b13055c4a9feb37c13c2982c3d7ab7e6cfdfb60..."

# v2 signature (ECDSA signed) - what we need:
SIGNATURE.sig = {
  "version": 2,
  "hash": "...",
  "signature": "...",
  "signer": "..."
}
```

## Root Cause Analysis

### What We Know
1. ✅ Locally: All imports work, containers are signed correctly
2. ✅ `ecdsa>=0.18.0` is in pyproject.toml dependencies
3. ✅ factory.yml explicitly installs: `pip install pyyaml cryptography tomlkit ecdsa`
4. ❌ CI: Containers are NOT signed → build fails

### What We Don't Know
- WHY does `from vibe_core.steward.crypto import ...` fail in CI?
- Is there a cascading import error?
- Is there a "name mismatch" (user hypothesis)?

### Commits in Scope
Recent commits that could affect container building:
- `daef25a` - Added `events/mutation_handlers.py` (OPUS-038)
- `da93c71` - Added `events/diamond_handlers.py` (OPUS-037)
- `1c2870e` - Made signature verification STRICT (FAIL instead of WARN)

## The Deeper Problem: "Who Tests the Testers?"

This bug exposes a fundamental gap:

```
┌───────────────────────────────────────────────────────────┐
│  MUTATION TESTING REVEALS:                                 │
│                                                           │
│  • Green tests ≠ Valid tests                              │
│  • The crypto import can silently fail                    │
│  • No test verifies that signing ACTUALLY works           │
│  • We trusted a "fixed" bug that wasn't actually fixed    │
└───────────────────────────────────────────────────────────┘
```

## Proposed Fixes

### Fix 1: Fail Fast (Immediate)
Make pack_vibe.py FAIL if crypto is unavailable:

```python
# BEFORE: Silent fallback
try:
    from vibe_core.steward.crypto import ...
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False  # Silent!

# AFTER: Fail fast
try:
    from vibe_core.steward.crypto import ...
except ImportError as e:
    raise RuntimeError(f"FATAL: Cannot build containers without crypto: {e}")
```

### Fix 2: Add Mutation-Resistant Test
Create a test that FAILS when signing doesn't work:

```python
def test_container_signing_actually_works():
    """
    MUTATION KILLER: This test must fail if signing is broken.

    RED: Run with CRYPTO_AVAILABLE = False → should fail
    GREEN: Run with real crypto → should pass
    """
    # Build a test container
    container = build_container(test_plugin_dir)

    # Extract and verify signature
    with zipfile.ZipFile(container) as z:
        sig = json.loads(z.read('SIGNATURE.sig'))

    # MUST have version 2 (ECDSA)
    assert sig.get('version') == 2, "Container not ECDSA signed!"
    assert 'signature' in sig, "Missing ECDSA signature!"
    assert len(sig['signature']) > 20, "Signature too short!"
```

### Fix 3: CI Fail-Fast Verification
Add crypto verification BEFORE building:

```yaml
- name: Verify crypto available (fail-fast)
  run: |
    python -c "
    from vibe_core.steward.crypto import load_or_generate_keys, sign_content
    priv, pub = load_or_generate_keys()
    sig = sign_content('test', priv)
    assert len(sig) > 20, 'Signing failed!'
    print('✅ Crypto VERIFIED: ECDSA signing works')
    " || (echo '❌ FATAL: Crypto unavailable!' && exit 1)
```

## Path to 60% Singularity

This incident reveals we need:

1. **Mutation Testing for ALL critical paths**
   - Don't trust green tests
   - Every test must prove it can fail

2. **Fail-Fast Architecture**
   - No silent fallbacks for security-critical features
   - Explicit errors > silent degradation

3. **CI/CD Testing**
   - Test the build process itself
   - Verify artifacts match expectations

## Action Items

| Priority | Action | Owner |
|----------|--------|-------|
| P0 | Find WHY crypto fails in CI | OPUS |
| P0 | Add fail-fast to pack_vibe.py | OPUS |
| P1 | Create mutation-resistant signing test | OPUS |
| P1 | Add CI crypto verification step | OPUS |
| P2 | Document the fix for future sessions | OPUS |

## Request for Gemini Review

Dear Senior Partner,

This regression analysis requires your review:

1. Is the "fail-fast" approach correct?
2. Should we add more comprehensive mutation testing for crypto?
3. What other silent fallbacks might exist in the codebase?

The 51% singularity exposed that green tests can lie.
We need to push to 60% with mutation-resistant testing.

Respectfully,
OPUS Assistant

---

*This report was generated during investigation of CI build failure.*
*The bug may still be active - this is a living document.*
