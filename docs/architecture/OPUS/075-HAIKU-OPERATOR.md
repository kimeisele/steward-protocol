# OPUS-075: HAIKU OPERATOR - Cheap Autonomy Layer

**Status:** PLANNING
**Author:** Claude (Opus)
**Date:** 2025-12-15
**Scope:** Enable cheap LLM (Haiku) to operate MANAS via OPUS.md

---

## Executive Summary

Das System ist zu 99% fertig. Die Infrastruktur (MANAS, VAJRA, Cortex) existiert.
Was fehlt: Ein **günstiger Operator** der die technische Schuld systematisch abschmelzen kann.

**Kernidee:** Haiku liest OPUS.md, versteht den Systemzustand, und führt einfache MANAS-Intents aus.
Opus (teuer) plant, Haiku (günstig) exekutiert.

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPERATOR HIERARCHY                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   OPUS (Architect)          HAIKU (Worker)                      │
│   ┌─────────────────┐      ┌─────────────────┐                  │
│   │ • Designs plans │      │ • Reads OPUS.md │                  │
│   │ • Creates OPUS  │      │ • Executes safe │                  │
│   │   docs          │      │   intents       │                  │
│   │ • Complex       │      │ • Reports back  │                  │
│   │   decisions     │      │ • Low cost      │                  │
│   └────────┬────────┘      └────────┬────────┘                  │
│            │                        │                            │
│            └────────────┬───────────┘                           │
│                         │                                        │
│                         ▼                                        │
│              ┌─────────────────────┐                             │
│              │     OPUS.md         │                             │
│              │  (Shared State)     │                             │
│              └─────────────────────┘                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Problem Statement

1. **Opus ist teuer** - Kann nicht dauerhaft laufen
2. **Haiku ist günstig** - Aber kann nicht komplex planen
3. **MANAS ist zu 99% fertig** - Braucht nur einen Operator
4. **Technische Schuld** - Muss systematisch abgeschmolzen werden

---

## Solution: OPUS.md as Interface

OPUS.md ist bereits die Single Source of Truth:
- Systemzustand (Kernel, Agents, Karma)
- Pending Intents (was MANAS machen will)
- Verification Status (was verifiziert ist)
- Focus Areas (was wichtig ist)

**Haiku kann:**
1. OPUS.md lesen und verstehen
2. Einfache Intents genehmigen/ablehnen
3. Safe Actions ausführen
4. Status reporten

**Haiku kann NICHT:**
1. Komplexe Architektur-Entscheidungen treffen
2. Neue OPUS docs schreiben
3. Ring-0 Code ändern

---

## Prerequisites (Blockers)

### 1. Idempotent Syscalls (Ring-0 Fix Required)

**Problem:** GRANT_MANDATE zeigt 0/153 success weil "already_had" als failure zählt.

**Fix:** `vibe_core/capability_registry.py`

```python
# Line 194 (revoke):
none_have = all(c not in agent_caps for c in capabilities)
return {"success": none_have, ...}

# Line 261 (grant):
all_have = all(c in agent_caps for c in capabilities)
return {"success": all_have, ...}
```

**Status:** TDD Tests vorhanden, CI failed (gewollt), Ring-0 Fix pending.

### 2. Test Mutation (99% da)

`vibe_core/plugins/test_orchestration/` ist ready aber nicht aktiviert.

### 3. Heartbeat MANAS Integration

`scripts/heartbeat.py` → `CognitiveKernel.think()` ist verdrahtet (OPUS-074).

---

## Implementation Plan

### Phase 1: Ring-0 Fixes (Manual)

1. Fix `capability_registry.py:194` (4 LOC)
2. Fix `capability_registry.py:261` (4 LOC)
3. CI passes

### Phase 2: Haiku Operator Prompt

Create `prompts/haiku_operator.md`:

```markdown
# HAIKU OPERATOR

Du bist ein einfacher Operator für das STEWARD System.

## Deine Aufgabe
1. Lies OPUS.md
2. Verstehe den Systemzustand
3. Führe SAFE Intents aus
4. Reporte Ergebnisse

## Du darfst
- Intents mit risk=SAFE genehmigen
- Tests laufen lassen
- Status reporten
- Einfache Fixes machen

## Du darfst NICHT
- Ring-0 Code ändern
- Neue OPUS docs erstellen
- Komplexe Entscheidungen treffen
- Bei Unsicherheit weitermachen (frage nach)

## Workflow
1. `cat OPUS.md` - Systemzustand lesen
2. Check "Pending Intents" section
3. Für jeden SAFE Intent: execute oder skip mit Grund
4. Update status
```

### Phase 3: Test Harness

Enable test mutation:
```bash
python -m vibe_core.cli test --mutate
```

### Phase 4: Autonomous Loop

```bash
# Cron oder systemd timer
0 * * * * haiku --prompt prompts/haiku_operator.md
```

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| GRANT_MANDATE success | 0/153 | 153/153 |
| Haiku cost/hour | N/A | <$0.10 |
| Technical debt items | 17 TODOs | <10 |
| Test coverage | 87% | >90% |
| Autonomous fixes/week | 0 | >5 |

---

## Verification Harness

<!-- HARNESS:START -->
```yaml
harness:
  id: OPUS-075-HAIKU
  version: 1.0.0
  status: PLANNING

  files:
    - path: tests/integration/test_capability_revocation.py
      required: true
      description: "TDD tests for idempotent syscalls"

  wiring:
    - pattern: "success.*is True.*CI FAILS"
      in: tests/integration/test_capability_revocation.py

  tests:
    - tests/integration/test_capability_revocation.py::test_revoke_nonexistent_capability
    - tests/integration/test_capability_revocation.py::test_grant_already_had_is_idempotent
```
<!-- HARNESS:END -->

---

## Open Questions

1. **Haiku Context Window:** Ist OPUS.md zu groß?
2. **Rate Limiting:** Wie oft darf Haiku laufen?
3. **Escalation:** Wann muss Opus eingeschaltet werden?

---

*"The master does less and accomplishes more." - Lao Tzu*
