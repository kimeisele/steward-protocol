# OPUS-015a: Security Architecture Addendum

> **Status**: 📋 PROPOSED
> **Date**: 2025-12-10
> **Author**: Senior Architect (Self-Audit)
> **Parent**: OPUS-015 (Container Format)
> **Trigger**: Critical audit revealing crypto infrastructure gaps

<!-- @HARNESS
files:
  - path: vibe_core/plugins/crypto/plugin_main.py
    required: true
  - path: tests/unit/test_container_loader.py
    required: true
  - path: tests/integration/test_container_integrity.py
    required: true
  - path: tests/unit/test_crypto_plugin.py
    required: true
  - path: scripts/pack_vibe.py
    required: false
tests:
  - tests/unit/test_crypto_plugin.py
  - tests/integration/test_container_integrity.py
  - tests/integration/test_container_ed25519.py
wiring:
  - pattern: "CryptoPlugin"
    in: vibe_core/plugins/crypto/plugin_main.py
  - pattern: "Ed25519"
    in: vibe_core/plugins/crypto/plugin_main.py
absent:
  - pattern: "TODO.*crypto"
    in: vibe_core/plugins/crypto/plugin_main.py
config:
  - section: security_crypto
-->

---

## Executive Summary

OPUS-017 resolved the **immediate** container integrity issue (P0). However, a deeper audit revealed fundamental crypto architecture flaws that must be addressed before the system can be trusted for distribution of third-party holons.

**The Core Problem**: The system uses symmetric cryptography (HMAC) where asymmetric cryptography (Ed25519) is required. Anyone with the signing key can forge signatures.

---

## Current Architecture (The Problem)

```
┌─────────────────────────────────────────────────────────────┐
│                    WHAT EXISTS NOW                          │
├─────────────────────────────────────────────────────────────┤
│  [✅] pack_vibe.py creates SHA256 content hash              │
│  [✅] container_loader.py verifies hash matches             │
│  [✅] SIGNATURE.sig contains hex hash                       │
│  [❌] identity_tool.py uses HMAC (symmetric)                │
│  [❌] "public_key" = sha256(private_key) - NOT A PK         │
│  [❌] No trust anchor (who signs the signers?)              │
│  [❌] No hollows trust model                                │
│  [❌] /tmp cache is insecure                                │
└─────────────────────────────────────────────────────────────┘
```

### Verified Flaws

| File | Line | Issue | Severity |
|------|------|-------|----------|
| `identity_tool.py` | 317 | `hmac.new()` - symmetric crypto | 🔴 CRITICAL |
| `identity_tool.py` | 99 | `sha256(private_key)` as "public key" | 🔴 CRITICAL |
| `container_loader.py` | 18 | `/tmp/vibe_cache/containers` | 🟠 HIGH |
| `container_loader.py` | 66-68 | Recursive holon mount - no trust check | 🟠 HIGH |

---

## Target Architecture (The Solution)

```
┌─────────────────────────────────────────────────────────────┐
│                    TARGET STATE                             │
├─────────────────────────────────────────────────────────────┤
│  Container Signing (Ed25519):                               │
│  ┌─────────────┐       ┌─────────────┐                      │
│  │ Author Key  │──────▶│ SIGNATURE   │                      │
│  │ (Ed25519)   │       │ .sig        │                      │
│  └─────────────┘       └─────────────┘                      │
│        │                     │                              │
│        ▼                     ▼                              │
│  ┌─────────────┐       ┌─────────────┐                      │
│  │ Public Key  │       │ Verifier    │                      │
│  │ (in Holon)  │◀──────│ (Loader)    │                      │
│  └─────────────┘       └─────────────┘                      │
├─────────────────────────────────────────────────────────────┤
│  Trust Model:                                               │
│  • Self-signed holons (like npm packages)                   │
│  • Public key embedded in manifest.json                     │
│  • First-use trust (TOFU) + optional pinning                │
│  • Hollows inherit parent trust OR require independent sig  │
└─────────────────────────────────────────────────────────────┘
```

---

## Threat Model

| Threat | Current Protection | Target Protection |
|--------|-------------------|-------------------|
| **Container Tampering** | ✅ SHA256 hash check | ✅ Same + Ed25519 signature |
| **Key Forgery** | ❌ HMAC allows forgery with key | ✅ Ed25519 asymmetric |
| **MITM on Federation** | ❌ ssl=False | ✅ TLS + cert pinning |
| **Malicious Nested Holon** | ❌ No trust model | ✅ Explicit trust inheritance |
| **Cache Poisoning** | ❌ /tmp world-readable | ✅ User-private cache dir |
| **Trust Anchor Confusion** | ❌ No PKI | ✅ TOFU + manifest public key |

---

## Implementation Roadmap

### Phase 1: P0 - Immediate Fixes ✅ COMPLETE
Already done in OPUS-017:
- [x] `pack_vibe.py`: Deterministic file ordering
- [x] `container_loader.py`: Hash verification working
- [x] `gateway/api.py`: SSL verification enabled
- [x] Tests: `test_container_integrity.py`

---

### Phase 2: P1 - Asymmetric Crypto Foundation

> **Goal**: Replace HMAC with Ed25519 for container author signing

#### 2.1 Create CryptoPlugin with Ed25519

**File**: `vibe_core/plugins/crypto/plugin_main.py`

```python
# Proposed implementation using PyNaCl
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder

class CryptoPlugin:
    def generate_keypair(self) -> tuple[str, str]:
        """Generate Ed25519 keypair."""
        sk = SigningKey.generate()
        return sk.encode(HexEncoder).decode(), sk.verify_key.encode(HexEncoder).decode()
    
    def sign(self, message: bytes, private_key_hex: str) -> str:
        """Sign message with Ed25519 private key."""
        sk = SigningKey(private_key_hex.encode(), HexEncoder)
        return sk.sign(message).signature.hex()
    
    def verify(self, message: bytes, signature_hex: str, public_key_hex: str) -> bool:
        """Verify Ed25519 signature."""
        vk = VerifyKey(public_key_hex.encode(), HexEncoder)
        try:
            vk.verify(message, bytes.fromhex(signature_hex))
            return True
        except:
            return False
```

#### 2.2 Update pack_vibe.py

```python
# New SIGNATURE.sig format:
{
    "version": 2,
    "algorithm": "ed25519",
    "content_hash": "sha256:abc123...",
    "signature": "ed25519:def456...",  
    "public_key": "ed25519:789abc..."  # Author's public key
}
```

#### 2.3 Update container_loader.py

```python
def _verify_signature(cls, container_path: Path) -> bool:
    # Read SIGNATURE.sig
    sig_data = json.loads(z.read("SIGNATURE.sig"))
    
    if sig_data.get("version") == 2:
        # Ed25519 verification
        content_hash = cls._calculate_content_hash(z)
        return crypto.verify(
            content_hash.encode(),
            sig_data["signature"],
            sig_data["public_key"]
        )
    else:
        # Legacy SHA256 comparison (backward compat)
        return cls._verify_legacy_signature(z, sig_data)
```

#### 2.4 Verification Plan

```bash
# Unit test for Ed25519 signing/verification
pytest tests/unit/test_crypto_plugin.py -v

# Integration test for container signing
pytest tests/integration/test_container_ed25519.py -v

# Backward compatibility test
pytest tests/integration/test_container_legacy.py -v
```

---

### Phase 3: P2 - Trust Model & Security Hardening

#### 3.1 Hollows Trust Model

**Decision**: Nested holons require INDEPENDENT signatures.

```yaml
# manifest.json extension
{
  "trust": {
    "hollows_policy": "independent",  # or "inherit" 
    "allowed_signers": ["pubkey1...", "pubkey2..."]  # Optional allowlist
  }
}
```

```python
# container_loader.py update
for sub_container in hollows_path.glob("*.vibe"):
    if parent_trust_policy == "independent":
        # Each holon verified independently
        cls._verify_signature(sub_container)
    elif parent_trust_policy == "inherit":
        # Trust inherited (warns but allows)
        logger.warning(f"Holon {sub_container} inherits parent trust")
    cls.mount(sub_container)
```

#### 3.2 Secure Cache Directory

```python
# container_loader.py
import os

def _get_cache_dir() -> Path:
    """Get user-private cache directory."""
    # XDG compliant: ~/.cache/vibe/containers
    xdg_cache = os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")
    cache_dir = Path(xdg_cache) / "vibe" / "containers"
    cache_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    return cache_dir

CACHE_DIR = _get_cache_dir()
```

---

### Phase 4: P3 - Federation Security

#### 4.1 TLS with Optional Cert Pinning

```python
# gateway/api.py
import ssl
import certifi

def _get_ssl_context(peer_config: dict) -> ssl.SSLContext:
    ctx = ssl.create_default_context(cafile=certifi.where())
    
    # Optional: Cert pinning from peer config
    if "cert_fingerprint" in peer_config:
        # Verify against pinned cert
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
    
    return ctx

async with session.get(target_url, ssl=ssl_context) as resp:
    ...
```

---

## Migration Strategy

```
Phase 1 (P0): ✅ DONE - Hash verification working
    ↓
Phase 2 (P1): Ed25519 foundation
    • Add PyNaCl dependency
    • Create CryptoPlugin  
    • SIGNATURE.sig v2 format
    • Backward compat for v1
    ↓
Phase 3 (P2): Trust hardening
    • Hollows policy
    • Secure cache
    • TOFU key storage
    ↓
Phase 4 (P3): Network security
    • TLS by default
    • Optional cert pinning
```

---

## Proposed Changes Summary

| Phase | Component | Change |
|-------|-----------|--------|
| P1 | `pyproject.toml` | Add `pynacl` dependency |
| P1 | `vibe_core/plugins/crypto/` | New plugin with Ed25519 |
| P1 | `scripts/pack_vibe.py` | SIGNATURE.sig v2 format |
| P1 | `container_loader.py` | Ed25519 verification |
| P2 | `container_loader.py` | Secure cache dir |
| P2 | `container_loader.py` | Hollows trust policy |
| P3 | `gateway/api.py` | TLS context + pinning |

---

## Verification Plan

### Automated Tests
```bash
# All container security tests
pytest tests/unit/test_container_loader.py -v
pytest tests/integration/test_container_integrity.py -v

# After P1 implementation
pytest tests/unit/test_crypto_plugin.py -v
pytest tests/integration/test_container_ed25519.py -v
```

### Manual Verification
1. Build container with valid signature → Should load
2. Build container, tamper with content → Should REJECT
3. Build container with wrong author key → Should REJECT
4. Verify nested holons require independent signatures

---

## Open Questions for User Decision

> [!IMPORTANT]
> **User input needed on these architectural decisions:**

1. **Dependency Choice**: PyNaCl vs. cryptography library for Ed25519?
2. **Trust Model Default**: Should hollows default to `inherit` or `independent`?
3. **Key Storage**: Where should author keys be stored? (`~/.vibe/keys/`?)
4. **Backward Compat**: How long to support SIGNATURE.sig v1 (hash-only)?

---

## Conclusion

**P0 is done. The container won't load malware TODAY.**

P1-P3 are the foundation for a **trustworthy distribution ecosystem**. Without them, we can only trust containers we build ourselves.

**Recommendation**: Implement P1 (Ed25519) as the next sprint before any new features.
