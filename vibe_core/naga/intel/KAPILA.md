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
