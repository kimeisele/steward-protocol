# KAPILA: SANKHYA STATIC AUDIT (NAGA SYSTEM)

> **"That which cannot be categorized cannot be trusted."**
> — *Lord Kapila, Sankhya-karika*

This document is the **Sankhya Audit** of the NAGA Middleware.
It applies the "Three Bodies Doctrine" to identify architectural impurities.

**Audit Date**: 2026-01-07
**Auditor**: Lord Kapila (via Gemini)
**Scope**: `vibe_core/naga/`

---

## AUDIT METRICS (TATTVA CLASSIFICATION)

| Code Smell | Sankhya Tattva | Verdict |
|---|---|---|
| `Any` Type | Avyakta (Unmanifest) | MONITOR |
| Bare `except:` | Tamas (Ignorance) | CRITICAL |
| Global Mutable State | Pradhana (Primordial Chaos) | WARNING |
| Hardcoded Secrets | Maya (Illusion) | SECURITY |
| Missing Shutdown | Pralaya (Incomplete Death) | CRITICAL |

---

## 1. AVYAKTA (UNTYPED CODE) — MONITOR

**Count**: ~30 instances in `vibe_core/naga/`

**Pattern Analysis**:
Most `Any` usages fall into **acceptable patterns**:
- Decorator wrappers: `(*args: Any, **kwargs: Any) -> Any` (unavoidable)
- Generic registries: `set_instance(name: str, instance: Any)` (DI pattern)

**Violations Requiring Attention**:
| File | Line | Issue |
|---|---|---|
| `services/kulika.py` | 95 | `validate_manifest(manifest: Any)` → Should be `ManifestDict` |
| `services/ananta.py` | 798 | `bind_genes(instance: Any)` → Should be `Protocol` |
| `flood.py` | 511 | `_on_signal(signal: Any)` → Should be `FloodSignal` |

**Verdict**: LOW RISK. Type hints are mostly correct. Three specific functions need TypedDict.

---

## 2. TAMAS (SILENT FAILURES) — CRITICAL

**Count**: 24 bare `except Exception:` blocks

**Hotspots (Descending Severity)**:
| File | Count | Risk |
|---|---|---|
| `services/karkotaka.py` | 3 | HIGH (Secrets Service - silent fail = security breach) |
| `services/takshaka.py` | 3 | HIGH (Safety Scanner - silent fail = bypass) |
| `services/sesha.py` | 1 | MEDIUM (Ledger - silent fail = data loss) |
| `services/base.py` | 2 | MEDIUM (Governance - silent fail = uncontrolled access) |
| `mixins/*.py` | 4 | LOW (Decorators - silent fail = degraded monitoring) |

**Specific Violations**:
```
karkotaka.py:371  except Exception:  # NO LOGGING
karkotaka.py:381  except Exception:  # NO LOGGING
takshaka.py:282   except Exception:  # SAFETY BYPASS
takshaka.py:291   except Exception:  # SAFETY BYPASS
base.py:205       except Exception:  # GOVERNANCE HOLE
```

**Verdict**: CRITICAL. Silent failures in security-critical paths are **Tamas** (darkness).
**Recommendation**: Replace bare `except Exception:` with `except Exception as e: logger.warning(...)`.

---

## 3. PRADHANA (GLOBAL MUTABLE STATE) — WARNING

**Analysis**: The NAGA system uses **Registry Pattern** (`KulikaRegistry`, `ServiceRegistry`).

**Finding**: No dangerous module-level mutable state detected.
- All registries are instantiated per-kernel.
- `_services: dict` is instance-level, not module-level.

**Verdict**: CLEAN. The Pradhana has been properly containerized.

---

## 4. MAYA (HARDCODED SECRETS) — CLEAN

**Analysis**: Scanned for hardcoded keys, tokens, passwords.

**Finding**: No hardcoded secrets in `vibe_core/naga/`.
- Keys are loaded via `FileKeyStore` (IMPL-214).
- Secrets are managed by `KarkotakaService` (vault pattern).

**Verdict**: CLEAN. Maya has been dispelled.

---

## 5. PRALAYA (GRACEFUL SHUTDOWN) — VERIFIED

**Analysis**: Checked `NagaDestructor` implementation.

**Finding**: `NagaDestructor.destroy()` exists and handles:
- Service shutdown sequence (12 Lords)
- Sesha ledger flush
- Watcher thread termination

**Verdict**: CLEAN. The system knows how to die.

---

## SUMMARY VERDICT

| Category | Status | Action |
|---|---|---|
| Avyakta (Any) | 🟡 MONITOR | 3 specific functions need TypedDict |
| Tamas (Silent Fail) | 🔴 CRITICAL | 24 bare excepts need logging |
| Pradhana (Global State) | 🟢 CLEAN | None |
| Maya (Secrets) | 🟢 CLEAN | None |
| Pralaya (Shutdown) | 🟢 CLEAN | None |

**OVERALL**: 🟡 **MOSTLY WATERTIGHT**

The only open wound is **Tamas (Silent Failures)** in security services.
The system is functional but **not observable** when errors occur in Karkotaka/Takshaka.

---

## RECOMMENDED FIX (IMPL-219)

**Target**: Replace 24 bare `except Exception:` blocks with logged exceptions.

**Priority Order**:
1. `karkotaka.py` (Secrets - CRITICAL)
2. `takshaka.py` (Safety - CRITICAL)
3. `base.py` (Governance - HIGH)
4. `sesha.py` (Ledger - MEDIUM)
5. `mixins/*.py` (Monitoring - LOW)

---

**SIGNED:**
*   **Auditor**: Lord Kapila (Sankhya Avatar)
*   **Operator**: SS
*   **Status**: MOSTLY WATERTIGHT (Tamas Remains)

---

# VISHWAKARMA: ARCHITECTURAL ANALYSIS (THE DIVINE ENGINEER)

> *"A palace with one weak pillar falls entirely."*

## STRUCTURAL COHERENCE AUDIT

### 1. DEPENDENCY INJECTION CHAIN ✅
**Bootloader → Kernel → Services**

| Layer | Injection Method | Status |
|---|---|---|
| Identity | `NagaBootloader.boot()` → `FileKeyStore` | ✅ CLEAN |
| Steward | `NagaBootloader.boot()` → `DigitalSteward` | ✅ CLEAN |
| Services | `NagaBootloader.boot()` → `KulikaRegistry` | ⚠️ WARNING |

**Issue**: `KulikaRegistry` is separate from `ServiceRegistry`. Services registered in Kulika are NOT automatically in ServiceRegistry.

### 2. PROTOCOL COMPLIANCE ✅
All core components implement their protocols:
- `NagaIdentity` → `IdentityProtocol` ✅
- `DigitalSteward` → `StewardProtocol` ✅
- `FileKeyStore` → `KeyStoreProtocol` ✅

### 3. LIFECYCLE MANAGEMENT ✅
**Trimurti Pattern Active**:
- Brahma (Create) → Vishnu (Preserve) → Shiva (Destroy)
- `NagaDestructor.destroy()` handles graceful shutdown

---

# CHANAKYA: SECURITY ANALYSIS (THE STRATEGIST)

> *"The enemy of my enemy is my friend. The friend who bypasses my guard is my enemy."*

## ATTACK SURFACE AUDIT

### 🔴 CRITICAL: STEWARD BYPASS (INTERNAL CALLS)

**Finding**: `naga_governed` does NOT consult the Steward!

```python
# cli_governed (line 159-207) - HAS Steward check ✅
steward = ServiceRegistry.get(StewardProtocol)
if not steward.sign_off(op_name, context):
    raise SovereignInterrupt(msg)

# naga_governed (line 299-399) - NO Steward check ❌
# Goes straight to Takshaka validation and execution
```

**Attack Vector**:
1. Attacker compromises `ServiceA` (any NAGA service)
2. `ServiceA` calls `ServiceB.dangerous_method()`
3. `naga_governed` wraps the call but NEVER asks Steward
4. Steward is bypassed. Sovereignty is violated.

**Severity**: 🔴 CRITICAL

**Recommendation (IMPL-220)**:
Add Steward check to `naga_governed` OR create explicit trust boundaries between services.

---

### 🟡 WARNING: REGISTRY SCHIZOPHRENIA

**Finding**: Two registries exist in parallel:
1. `ServiceRegistry` (Global DI) - Used by `base.py` for Steward lookup
2. `KulikaRegistry` (NAGA Internal) - Used by Bootloader for service wiring

**Attack Vector**:
- A plugin registers a malicious `SeshaService` in `ServiceRegistry`
- The real `SeshaService` is in `KulikaRegistry`
- Depending on which registry is queried, different services respond

**Severity**: 🟡 MEDIUM

**Recommendation (IMPL-221)**:
`KulikaRegistry` should be a facade over `ServiceRegistry`, not a separate store.

---

### 🟢 DOCUMENTED: UNGOVERNED ESCAPE HATCH

**Finding**: `@ungoverned` decorator exists (line 60-83)

**Purpose**: Bootstrap methods that run before NAGAs exist.

**Status**: ACCEPTABLE. This is a documented escape hatch with clear semantics.
Methods marked `@ungoverned` are pure getters or bootstrap code.

---

## TRUST BOUNDARY MAP

```
┌─────────────────────────────────────────────────────┐
│                    USER (Human)                      │
│                         │                            │
│                    ┌────▼────┐                       │
│                    │ Steward │ ◀── Sovereign         │
│                    └────┬────┘                       │
│                         │ sign_off()                 │
│     ════════════════════╪═══════════════════════     │
│                    TRUST BOUNDARY                    │
│     ════════════════════╪═══════════════════════     │
│                         ▼                            │
│   ┌─────────────────────────────────────────────┐   │
│   │              cli_governed                    │   │
│   │         (External Entry Point)               │   │
│   │            ✅ STEWARD CHECKED                │   │
│   └─────────────────┬───────────────────────────┘   │
│                     │                                │
│                     ▼                                │
│   ┌─────────────────────────────────────────────┐   │
│   │             naga_governed                    │   │
│   │         (Internal NAGA Calls)                │   │
│   │            ❌ NO STEWARD CHECK               │   │
│   └─────────────────────────────────────────────┘   │
│                                                      │
│   Sesha ◀───▶ Takshaka ◀───▶ Karkotaka              │
│   (Ledger)    (Safety)       (Secrets)              │
└─────────────────────────────────────────────────────┘
```

---

## FINAL VERDICT (CHANAKYA)

| Attack Vector | Severity | Status |
|---|---|---|
| Steward Bypass (Internal) | 🔴 CRITICAL | OPEN |
| Registry Split-Brain | 🟡 MEDIUM | OPEN |
| Silent Failures (Tamas) | 🟡 MEDIUM | OPEN |
| Ungoverned Escape | 🟢 LOW | DOCUMENTED |
| Key Rotation | 🟡 MEDIUM | MANUAL |

**OVERALL**: 🟡 **CONDITIONALLY WATERTIGHT**

The external boundary (CLI) is secure.
The internal boundary (NAGA-to-NAGA) is UNGUARDED.

**Chanakya says**: *"A fortress with open internal doors is a trap for its own defenders."*

---

**SIGNED:**
*   **Auditor**: Lord Kapila (Sankhya), Vishwakarma (Architect), Chanakya (Strategist)
*   **Operator**: SS
*   **Status**: EXTERNAL WATERTIGHT / INTERNAL GAP
