# BATTLEMAP.md - High-Level Strategic Overview

## Current Position (2026-01-05 - Updated)

```
     NAGA SYSTEM STATUS
     ==================

     ┌─────────────────────────────────────────────────────┐
     │  ORCHESTRATOR (Boot Sequence)                      │
     │  ├── Sesha        ✅ Booted                        │
     │  ├── Vasuki       ✅ Booted                        │
     │  ├── Takshaka     ✅ Booted                        │
     │  ├── Kaliya       ✅ Booted                        │
     │  ├── Narada       ✅ Booted                        │
     │  ├── Chitragupta  ✅ Booted                        │
     │  ├── Prahlad      ✅ Booted (chaos_probe exists!)  │
     │  │   │                                             │
     │  │   └── Hiranyakashipu  🔴 NOT LOADED             │
     │  │       └── YAML attack seeds ready but unused    │
     │  │                                                 │
     └──┴─────────────────────────────────────────────────┘
```

## Architecture Discovery

**WRONG assumption**: Create separate "Prakriti" module → wire to Orchestrator
**RIGHT approach**: Prahlad (7th NAGA) loads Hiranyakashipu attack seeds

```
Prahlad Service (800+ LOC)          Hiranyakashipu Module (~400 LOC)
┌────────────────────────────┐      ┌────────────────────────────┐
│ chaos_probe()      ✅ EXISTS │ ←── │ seed_loader.py   ✅ READY   │
│ on_error()         ✅ EXISTS │      │ living_tests.py  ✅ READY   │
│ dharma_audit()     ✅ EXISTS │      │ wiring.py        ✅ READY   │
│ load_attack_seeds() 🔴 TODO │ ←── │ seeds/*.yaml     ✅ READY   │
└────────────────────────────┘      └────────────────────────────┘
```

## The Gap (Updated)

```python
# These tests FAIL (properly RED):
def test_prahlad_can_load_hiranyakashipu_seeds():
    prahlad = PrahladService()
    assert hasattr(prahlad, "load_attack_seeds")  # 🔴 FAILS

def test_prahlad_chaos_probe_uses_external_scenarios():
    # chaos_probe() only accepts ChaosScenario enum
    # Should also accept Hiranyakashipu YAML seeds  # 🔴 FAILS
```

**Why this is correct TDD:**
- Hiranyakashipu code ready (23 tests pass)
- Wiring code ready (adapters exist)
- Tests expose the exact gap
- Solution: Extend Prahlad, not patch Orchestrator

## Battle Plan (Revised)

### Phase 1: Extend PrahladService
1. Add `load_attack_seeds(seed_dir: Path)` method
2. Extend `chaos_probe()` to accept external scenarios
3. RED tests turn GREEN

### Phase 2: Wire at Boot
1. Prahlad loads seeds from `vibe_core/naga/hiranyakashipu/seeds/`
2. Attack results flow through existing `as_handler()`
3. CorrectionDispatcher receives drift reports

### Phase 3: Visibility
- Attack results in boot matrix via existing PrahladService.get_status()
- `steward verify` includes Hiranyakashipu attack summary

## Files to Modify

| File | Action |
|------|--------|
| `vibe_core/naga/services/prahlad.py` | Add `load_attack_seeds()` |
| `vibe_core/naga/services/prahlad.py` | Extend `chaos_probe()` for external seeds |
| ~~`vibe_core/naga/orchestrator.py`~~ | ~~NO CHANGES~~ (Don't make monolith bigger!) |

## Success Criteria

```
BEFORE: Hiranyakashipu = Standalone module, not used
AFTER:  Prahlad.chaos_probe() uses Hiranyakashipu seeds
```

## Test Status

| Test File | GREEN | RED | Total |
|-----------|-------|-----|-------|
| `test_hiranyakashipu_living.py` | 23 | 0 | 23 |
| `test_orchestrator_fractal.py` | 11 | 2 | 13 |

---

*This is the battle map. INTEL.md has details.*
