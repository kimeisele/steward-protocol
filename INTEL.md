# INTEL.md - Intelligence Briefing for NAGA Development

## CRITICAL: Protocols Folder IS the Truth (2026-01-05)

**BEFORE implementing anything, CHECK `vibe_core/protocols/`!**

### What Already Exists

| Protocol | File | Lines | Key Concepts |
|----------|------|-------|--------------|
| **ReactorProtocol** | `reactor.py` | 494 | Drift detection, DriftEvent, DriftMetrics |
| **CorrectionDispatcher** | `correction.py` | 631 | **HealingStrategy.RESONANCE**, unified healing |
| **NagaProtocol** | `naga.py` | 78K | All 7 NAGAs, NagaType enum, full spec |

### RESONANCE Already Defined!

```python
# correction.py:88
class HealingStrategy(str, Enum):
    AUTO = "auto"
    DRY_RUN = "dry_run"
    MANUAL = "manual"
    CIRCUIT = "circuit"
    RESONANCE = "resonance"  # <-- USE QUANTUM REACTOR!
```

```python
# correction.py:257-258
# HealingStrategyResolverProtocol.resolve():
# 3. Compute resonance via Quantum Reactor
# 4. If resonance > inertia → AUTO (earned privilege)
```

**The solution is NOT to invent something new - it's to WIRE what exists!**

---

## GAPS: Prakriti vs Protocols

### Current State
```
vibe_core/protocols/           # THE TRUTH (established)
├── reactor.py                 # Drift detection
├── correction.py              # RESONANCE strategy exists!
├── naga.py                    # 7 NAGAs defined
└── ...

vibe_core/naga/prakriti/       # NEW (not wired!)
├── seed_loader.py             # YAML loading ✅
├── living_tests.py            # Test execution ✅
└── seeds/*.yaml               # Attack patterns ✅
```

### Missing Wiring (Priority Order)

| Gap | From | To | Status |
|-----|------|----|----- |
| 1. **Prakriti → CorrectionDispatcher** | LivingTestFramework | HealingStrategy.RESONANCE | ❌ NOT WIRED |
| 2. **Prakriti → ReactorProtocol** | TestResult | DriftEvent | ❌ NOT WIRED |
| 3. **Prakriti → Sesha** | Attack results | Ledger persistence | ❌ NOT WIRED |
| 4. **Orchestrator → Prakriti** | Boot sequence | Living framework | ❌ NOT WIRED |

---

## The Binary Problem (Why 16/16 passed is FAKE)

```
16 passed, 0 failed = KINDERGARTEN SECURITY
```

### What We Have (Binary)
```python
# prakriti/living_tests.py
passed: bool  # 0 or 1
bypassed: bool  # 0 or 1
```

### What Protocols Define (Resonance)
```python
# correction.py - HealingStrategyResolverProtocol
# Combines:
# - Bhakti balance (earned trust)
# - Ashrama stage (lifecycle permissions)
# - Quantum Reactor resonance
#
# If resonance > inertia → AUTO
# If Bhakti >= 50 → MANUAL
# Otherwise → DRY_RUN
```

### Solution: Use Existing Resonance

Prakriti TestResult should produce `UnifiedDriftReport` which flows into:
```
TestResult → adapt_to_drift() → UnifiedDriftReport → CorrectionDispatcher
                                                          ↓
                                    HealingStrategyResolver.resolve()
                                                          ↓
                                              Quantum Reactor computes resonance
                                                          ↓
                                              HealingStrategy returned
```

---

## The Lila Mapping (Hiranyakashipu)

| Story Element | Protocol Mapping | Status |
|---------------|------------------|--------|
| Narada's whisper | `SeedLoader` (YAML) | ✅ Done |
| Kayadu's womb | `LivingTestFramework` | ✅ Done |
| Prahlad's birth | Test generation | ✅ Done |
| Hiranyakashipu's attacks | Attack vectors | ✅ Done |
| Vishnu's protection | Real subprocess | ✅ Done |
| **Narasimha's appearance** | `HealingStrategy.RESONANCE` | ❌ NOT WIRED |
| **Neither inside nor outside** | `ReactorProtocol.detect_drift()` | ❌ NOT WIRED |

**Narasimha = Quantum Reactor** - appears from the PILLAR (neither inside nor outside).
The pillar is the boundary between binary states. Resonance lives there.

---

## Next Steps (WIRE, don't invent!)

1. **Create adapter**: `prakriti.TestResult → correction.UnifiedDriftReport`
2. **Register Prakriti as detector** in `DriftRegistryProtocol`
3. **Use HealingStrategy.RESONANCE** instead of binary pass/fail
4. **Wire to ReactorProtocol** for drift tracking
5. **Add failing tests** that expose unwired gaps

---

## Principle

> "Don't implement what's already defined. WIRE IT."
> "Protocols folder IS the truth."
> "If it's not in protocols, it doesn't exist yet."

---

*Last updated: 2026-01-05*
*Author: NAGA Development Team*
