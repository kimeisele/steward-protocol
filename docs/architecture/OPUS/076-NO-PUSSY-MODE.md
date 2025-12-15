# OPUS-076: NO PUSSY MODE

**Scope:** Live Fire Enforcement
**Philosophy:** If it's not real, it's not worth doing.

---

## The Problem

The system was running in `simulation` mode (line 15 SETTINGS.md, config/providers.yaml).

**Simulation mode means:**
- No real API calls
- No real file writes
- No real work done
- MANAS generates intents that go nowhere
- Everything is fake

This is unacceptable. We don't build AI assistants to simulate helping.

---

## The Fix

### 1. Flipped the Switch

**File:** `config/providers.yaml`

```yaml
# BEFORE (pussy mode):
features:
  live_fire_enabled: false

# AFTER (real mode):
features:
  live_fire_enabled: true   # ← THE SWITCH IS ON
```

### 2. Pre-Commit Guard

**File:** `.githooks/pre-commit` (GUARD 7)

Any attempt to set `live_fire_enabled: false` is **BLOCKED**:

```
❌ OPUS-076 VIOLATION: Attempt to enable SIMULATION MODE

  live_fire_enabled: false  ← FORBIDDEN

MANAS needs REAL execution mode to DO REAL WORK.
Simulation mode is for cowards. Don't be a coward.
```

### 3. Harness Verification

**File:** `docs/architecture/OPUS/075-MANAS-RELIABILITY.md`

The harness includes an `execution_mode` check that FAILS if simulation mode is detected:

```yaml
semantic:
  - type: execution_mode
    name: not_in_simulation
    expected: live_fire
    rationale: "MANAS must be in live_fire mode to actually DO work"
```

---

## Verification

```bash
# Run the fortress harness
steward verify 075

# Expected: execution_mode check PASSES (live_fire confirmed)
```

---

## Why This Matters

MANAS is the brain. If the brain runs in simulation mode:
- Intents are generated but never executed
- Heartbeat runs but nothing changes
- The whole system is a theater performance

**Real AI assistants do real work.**

---

## Protection Layers

| Layer | Protection | Location |
|-------|------------|----------|
| 1 | Pre-commit guard | `.githooks/pre-commit` GUARD 7 |
| 2 | Harness check | `075-MANAS-RELIABILITY.md` semantic |
| 3 | Settings display | `SETTINGS.md` shows mode |

If someone tries to sneak simulation mode back in:
1. Pre-commit BLOCKS the commit
2. If bypassed, harness FAILS on next verify
3. SETTINGS.md visibly shows the wrong mode

---

## @HARNESS

<!-- @HARNESS
files:
  - path: config/providers.yaml
    required: true
  - path: config/prana.yaml
    required: true
  - path: .githooks/pre-commit
    required: true

wiring:
  # Live fire must be enabled
  - pattern: "live_fire_enabled: true"
    in: config/providers.yaml

  # Force refresh must be enabled (no stale OPUS.md)
  - pattern: "force_refresh_on_heartbeat: true"
    in: config/prana.yaml

  # Pre-commit guard exists
  - pattern: "OPUS-076.*Live Fire Guard"
    in: .githooks/pre-commit

semantic:
  # Live fire mode check (from 075)
  - type: execution_mode
    name: live_fire_active
    expected: live_fire
    rationale: "System must be in live_fire mode"
-->

---

*"Simulation is masturbation. Live Fire is sex. Build systems that fuck."*
