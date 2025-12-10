# OPUS-017: Security Audit & Technical Debt Consolidation

> **Status**: 🚨 CRITICAL
> **Date**: 2025-12-10
> **Author**: Antigravity (Senior Audit Mode)
> **Trigger**: User escalation - "too many half-baked features"

---

## 🔴 Critical Finding: Container Integrity NOT VERIFIED

### The Gap
| Component | What It Does | What It Should Do |
|-----------|--------------|-------------------|
| `scripts/pack_vibe.py:102` | Creates `SIGNATURE.sig` with SHA256 hash | ✅ Correct |
| `vibe_core/loaders/container_loader.py:87` | **Only checks if file EXISTS** | ❌ MUST verify hash matches |

### The Code (BROKEN)
```python
# container_loader.py:81-91
@classmethod
def _verify_signature(cls, container_path: Path) -> None:
    """
    Verify container integrity.
    Currently a strict check for development: warns if missing.
    """
    # TODO: Implement real crypto verification  <-- THIS IS THE BUG
    with zipfile.ZipFile(container_path, "r") as z:
        if "SIGNATURE.sig" not in z.namelist():
            logger.warning(f"Unsigned container: {container_path}")
```

### The Fix Required
1. Read `SIGNATURE.sig` from container
2. Recalculate hash of all files (same algorithm as `pack_vibe.py`)
3. Compare hashes - REJECT container if mismatch
4. Optional: Add cryptographic signature (RSA/Ed25519) for publisher verification

---

## 📋 Full TODO Audit (vibe_core/)

| Priority | File | Line | Issue |
|----------|------|------|-------|
| 🔴 CRITICAL | `loaders/container_loader.py` | 87 | Crypto verification stub |
| 🟠 HIGH | `gateway/api.py` | 164 | SSL verification disabled |
| 🟠 HIGH | `cartridges/system/archivist/audit_tool.py` | 78 | Real verification missing |
| 🟡 MEDIUM | `cli/unified_cli.py` | 56 | Delegate not migrated to plugin |
| 🟡 MEDIUM | `store/sqlite_store.py` | 10 | Session artifacts not implemented |
| 🟡 MEDIUM | `runtime/prompt_composer.py` | 237 | Project root from context |
| 🟡 MEDIUM | `task_management/task_manager.py` | 341 | UnifiedRouter integration |
| ⚪ LOW | `plugins/envoy/plugin_main.py` | 517 | Config section creation |
| ⚪ LOW | `plugins/doctor/plugin_main.py` | 86 | Offline mode clarification |
| ⚪ LOW | `config/__init__.py` | 21 | v2.0 removal |
| ⚪ LOW | `playbook/__init__.py` | 22 | v2.0 removal |
| ⚪ LOW | `cortex/engines/__init__.py` | 8 | Playbook engine migration |
| ⚪ LOW | `cartridges/system/engineer/cartridge_main.py` | 465 | Agent-specific logic |

**Total: 13+ TODOs requiring attention**

---

## 🎯 Mandatory Actions Before New Features

### Phase A: Container Security (IMMEDIATE)
- [ ] Fix `_verify_signature()` to actually verify hash
- [ ] Add integration test: tampered container must be rejected
- [ ] Document container integrity protocol in OPUS docs

### Phase B: SSL/Network Security
- [ ] Enable SSL verification in federation forwarding
- [ ] Add `verify_ssl` config option to phoenix.yaml

### Phase C: Technical Debt Cleanup
- [ ] Migrate `delegate` command to plugin
- [ ] Implement session artifacts in sqlite_store

---

## 📜 Decision Required

**No new features until Phase A is complete.**

The binary works. The architecture is sound. But if we ship containers that can be tampered with, we've built a system that can be compromised.

**Next Step**: Implement real hash verification in `container_loader.py`.
