# VERIFIED DELTA PLAN - SINGLE SOURCE OF TRUTH

> **WARNUNG:** Dies ist der EINZIGE gueltige Plan. Alle anderen Reports wurden geloescht.
> **Methode:** Live Code Verification am 2025-12-07
> **Status:** Verifiziert gegen aktuellen HEAD

---

## AUDIT ERGEBNIS: WAS IST BEREITS GEFIXT?

| Issue | SOLID_HARDENING (Nov 30) | LIVE CODE STATUS |
|-------|--------------------------|------------------|
| Signature Verification in `ConstitutionalOath` | OPEN | **FIXED** (constitution.py:145-151) |
| Genesis Hash Bypass | OPEN | **FIXED** (env-gated, Line 138) |
| DailyRitual Tests | "Missing" | **EXISTS** (test_prana_init.py:155) |

---

## OPEN ISSUES (VERIFIZIERT OFFEN)

### PRIORITY 0: CRITICAL

#### 1. StewardProtocolPlugin TODOs (NICHT ConstitutionalOath!)

**File:** `vibe_core/plugins/steward_protocol/plugin_main.py`

| Line | Code | Status |
|------|------|--------|
| 376 | `"signature_valid": None,  # TODO: implement` | OPEN |
| 417 | `"valid_until": None,  # TODO: implement expiry` | OPEN |

**Erklaerung:** `ConstitutionalOath.verify_oath()` ist GEFIXT. Aber `StewardProtocolPlugin.verify_agent()` gibt IMMER `signature_valid: None` zurueck - das sind ZWEI VERSCHIEDENE Code-Paths!

**Fix:**
```python
# Line 376: Nutze existierende ConstitutionalOath
from vibe_core.steward.constitution import ConstitutionalOath

def verify_agent(self, agent_id: str) -> dict:
    # ... existing code ...

    # STATT: "signature_valid": None
    # NUTZE:
    oath_event = self._get_oath_event(agent_id)
    if oath_event:
        is_valid, _ = ConstitutionalOath.verify_oath(oath_event)
        result["signature_valid"] = is_valid
    else:
        result["signature_valid"] = False
```

---

#### 2. State Persistence (IN-MEMORY ONLY)

**File:** `vibe_core/plugins/vedic_governance/plugin_main.py`

| Line | Code |
|------|------|
| 64 | `# TODO: Persist to Ledger (currently in-memory)` |
| 68 | `# TODO: Persist to Ledger (currently in-memory)` |

**File:** `vibe_core/plugins/steward_protocol/plugin_main.py`

| Line | Code |
|------|------|
| 79 | `self._manifests: Dict[str, Dict[str, Any]] = {}` |
| 82 | `self._trust_scores: Dict[str, float] = {}` |
| 85 | `self._attestations: Dict[str, Dict[str, Any]] = {}` |

**Impact:** Kernel restart = Total Amnesia. Alle Oaths, Trust Scores, Attestations verloren.

---

### PRIORITY 1: HIGH

#### 3. Stub Code in Production

**File:** `vibe_core/cartridges/system/envoy/deterministic_executor.py`

| Line | Code | Impact |
|------|------|--------|
| 204 | `logger.warning("Action handlers not available (using stubs)")` | Warnung aber weiter |
| 796-797 | `logger.info(f"  State check passed (stub): {resolved_target}")` | CHECK_STATE = immer True |
| 818-819 | `logger.info(f"  Script executed (stub): {resolved_target}")` | EXECUTE_SCRIPT = fake success |

**Impact:** Playbooks erscheinen erfolgreich, tun aber NICHTS.

---

#### 4. MilkOcean Silent Fail

**File:** `vibe_core/cartridges/system/envoy/tools/milk_ocean.py`

| Line | Code |
|------|------|
| 620 | `pass  # Silently fail - don't disrupt routing` |

**Impact:** Security checks scheitern still, unsichere Operationen werden durchgelassen.

---

### PRIORITY 2: MEDIUM

#### 5. UniversalProvider Tests (ARCHIVE ONLY)

**Location:** `tests/archive/broken_async/test_playbook_system.py:255`

Tests existieren, aber in `archive/broken_async/` - nicht aktiv!

---

## WAS WURDE BEREITS GEFIXT? (NICHT NOCHMAL ANFASSEN!)

1. **ConstitutionalOath.verify_oath()** - Zeilen 145-151 in `constitution.py` rufen `identity_tool.verify_signature()` auf
2. **Genesis Hash Bypass** - Zeile 138 rejected in production mode
3. **DailyRitual Tests** - `tests/test_prana_init.py:155-166` hat TestDailyRitual

---

## EXECUTION ORDER

```
PHASE 1: Plugin TODOs fixen (2h)
  1.1 verify_agent() -> ConstitutionalOath.verify_oath() nutzen
  1.2 attest() -> valid_until mit datetime setzen

PHASE 2: Persistence (4h)
  2.1 vedic_governance -> Ledger.record_event()
  2.2 steward_protocol -> Ledger.record_event()
  2.3 Boot-time restore

PHASE 3: Stub Elimination (4h)
  3.1 deterministic_executor Stubs -> RuntimeError
  3.2 milk_ocean silent fail -> log warning + return blocked

PHASE 4: Test Restore (2h)
  4.1 Move UniversalProvider tests from archive
```

---

## VERIFICATION COMMANDS

```bash
# Nach jeder Aenderung ausfuehren:
python -m pytest tests/hardening/test_governance_security.py -v
python -m pytest tests/test_prana_init.py -v
python -m pytest tests/ -k "steward" -v
```

---

## DATEIEN DIE GEAENDERT WERDEN

```
PHASE 1:
  vibe_core/plugins/steward_protocol/plugin_main.py [376, 417]

PHASE 2:
  vibe_core/plugins/vedic_governance/plugin_main.py [64, 68]
  vibe_core/plugins/steward_protocol/plugin_main.py [79-91]

PHASE 3:
  vibe_core/cartridges/system/envoy/deterministic_executor.py [796-797, 818-819]
  vibe_core/cartridges/system/envoy/tools/milk_ocean.py [620]

PHASE 4:
  tests/archive/broken_async/test_playbook_system.py -> tests/integration/
```

---

**Signed:** Opus 4.5
**Date:** 2025-12-07
**Method:** Live `grep` gegen HEAD, keine Archive-Annahmen
