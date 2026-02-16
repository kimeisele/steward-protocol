# TEST ARCHITECTURE AUDIT — Kartographie & Diagnose

> "yasya deve parā bhaktir yathā deve tathā gurau"
> — The system already knows how to test itself. We just forgot to ask.

## 1. Die Zahlen

- **9432** test functions in **tests/**
- **255 seconds** just to COLLECT (not run!)
- **56** test directories
- **~180** test files

## 2. Die zwei Welten (DISCONNECTED)

### Welt A: Lebendes Immunsystem (Production Code)

| Komponente | Datei | Capability |
|---|---|---|
| GADProtocol | `protocols/_gad.py` | `test_daya/satyam/tapas/saucam`, `is_healthy()`, `audit()` |
| ShadowReactor.test_daya() | `reactor/shadow.py` | Self-test: KillerReactor injection, crash handling |
| verify_all_derived() | `research/spiritual_tdd.py` | 7 axioms + 13 derivations verified at import |
| verify_link() | `substrate/prabhupada.py` | Parampara chain at component birth |
| MantraHeartbeat.chant() | `protocols/_gad.py` | State machine: DISCONNECTED → CHANTING → MALA_COMPLETE |
| NagaTestHarness | `naga/testing.py` | Protocol-based DI, NullObjects, ServiceRegistry, NO MagicMock |
| NaradaScanner | `naga/scanner.py` | Auto-discovery: `@naga_service` → ServiceRegistry |
| KulikaRegistry | `naga/kulika.py` | Schema validation: what IS a valid Naga |
| NagaCortex | `naga/cortex/cortex_main.py` | Signal aggregation, correlation, dispatch |
| TÜVService | `naga/services/tuv.py` | Type-audit: Any-leaks, Protocol-alignment |
| NagaBaseService | `naga/services/base.py` | Ouroboros: Sesha(audit) + Chitragupta(profiling) + Takshaka(security) |
| 12 Naga Lords | `naga/services/*.py` | Full CIA: Sesha, Vasuki, Takshaka, Kaliya, Karkotaka, Kulika, Padma, Shankha + 4 Governance |

### Welt B: Tote Skripte (tests/)

Static pytest files. Import the codebase, assert from outside, know nothing about GAD or Nagas.

## 3. Diagnose: Warum die Test Suite krank ist

### 3.1 Import-Bloat (255s collect)
Every test file imports from `vibe_core`. With 180+ files, that's 180+ full import chains.
The codebase has heavy import-time computation (e.g. `spiritual_tdd.py` runs asserts at import).
Result: 255 seconds before a single test runs.

### 3.2 MagicMock statt NagaTestHarness
`test_gad000_compliance.py` line 14: `from unittest.mock import MagicMock`
The system has `NagaTestHarness` with Protocol-compliant NullObjects.
But the tests don't use it. They mock instead.

### 3.3 Dead Tests
`test_living_suite.py`: Entire file skipped — `BalaramaInjector` removed.
Nobody cleaned up. Nobody noticed. Because the suite is a black box.

### 3.4 Duplication
pytest tests assert `CRITERIA_COUNT == 6` from outside.
GADProtocol already verifies this internally via `audit()`.
Same truth, tested twice, connected never.

### 3.5 No Feedback Loop
pytest runs → pass/fail → done. No signal back to the system.
GAD audit runs → health status → could feed Cortex → could trigger healing.
But the two never meet.

## 4. Was GOLD ist (nicht anfassen!)

### 4.1 Hardening Tests (tests/hardening/)
~20 files: Hiranyakashipu attacks, Vritrasura strangulation, Halahala poison, Red team.
These are ADVERSARIAL tests. They try to BREAK the system.
GAD self-tests can't replace these — you can't attack yourself honestly.
**KEEP ALL.**

### 4.2 Substrate Tests (tests/substrate/, tests/mahamantra/substrate/)
~1300+ tests: MahaAlgorithm, RAMA grid, pancha_walk, varnamala_codec, basin_map.
These verify MATHEMATICAL INVARIANTS (bijection, determinism, convergence).
**KEEP ALL.** These are the axiom verification layer.

### 4.3 Naga Test Harness Tests (tests/naga/test_harness.py)
Tests that verify the harness itself works. Meta-tests.
**KEEP.**

### 4.4 Determinism Tests
Any test that verifies: same input → same output.
This is the PARAMPARA principle. Cannot be self-tested.
**KEEP ALL.**

## 5. Was SLOP ist (Kandidaten für Elimination/Migration)

### 5.1 Constant-Assertion Tests
Tests that just assert `X == 42`. If the constant is derived from axioms
and `verify_all_derived()` already checks it, the pytest version is redundant.
**MIGRATE to GAD audit or DELETE.**

### 5.2 MagicMock-Heavy Tests
Tests that mock half the system to test the other half.
`NagaTestHarness` exists for exactly this purpose.
**REWRITE to use NagaTestHarness.**

### 5.3 Skipped Tests
Any `@pytest.mark.skip` with no plan to fix.
`test_living_suite.py` is the poster child.
**DELETE or REWRITE.**

### 5.4 Tautology Tests
`assert True`, `assert isinstance(x, type(x))`, tests that can never fail.
**DELETE.**

## 6. Aktionsplan — Die Bridge

### Phase 1: Triage (DONE — this session)

Concrete numbers from codebase scan:
- **13 skipped tests** across 6 files (mostly cartridge contract tests)
- **7 `assert True` tautologies** across 4 files (test_orchestration, nexus_holon, kernel_tick)
- **22 `unittest.mock` imports** across 21 test files (cartridges, plugins, manas)
- **1 fully dead file**: `test_living_suite.py` (BalaramaInjector removed, entire file skipped)
- **NagaTestHarness** exists but is used ONLY in `tests/naga/test_harness.py` — nowhere else

Fast dirs (verified <10s): `tests/mahamantra/` (67s for 111 tests), `tests/substrate/` + `tests/kernel/` + `tests/reactor/` (48s for 648 tests)
Slow: Full suite 255s just to collect.

### Phase 2: Fast Lane (next session)
- [ ] Create `pytest.ini` markers: `@pytest.mark.gold`, `@pytest.mark.substrate`, `@pytest.mark.hardening`
- [ ] Create `make test-fast` that runs only gold+substrate (<30s)
- [ ] Create `make test-full` for CI (all 9432)

### Phase 3: GAD Bridge (future)
- [ ] `conftest.py` fixture that boots NagaTestHarness for all naga tests
- [ ] Replace MagicMock usage with NullObjects from harness
- [ ] Add `scan_lotus()` as pytest plugin (runs GAD audit as first test)
- [ ] Tests that fail GAD audit → auto-skip with reason

### Phase 4: Living Tests (vision)
- [ ] Components register their own invariants via GADProtocol
- [ ] `scan_lotus()` runs as BeatSubscriber (every MALA = 108 ticks)
- [ ] Failed audits → Cortex signal → ShuddhiEngine healing
- [ ] pytest becomes the ADVERSARIAL layer only (hardening)
- [ ] Everything else lives in RAM via GAD + Nagas

## 7. CRITICAL DISCOVERY: conftest.py (1100 Zeilen)

The bridge is ALREADY BUILT. `tests/conftest.py` has:

| Feature | Lines | Status |
|---|---|---|
| Mahamantra 16-Step Lifecycle | 420-727 | ✅ Wired (every test runs 16 steps) |
| Gene Injection (Entropy/Coherence) | 438-637 | ✅ Wired (fixtures: test_gene, chaos_gene, sattva_gene, guru_gene) |
| TÜV Badges (Bronze/Silver/Gold) | 730-886 | ✅ Wired (auto-issued on pass) |
| NagaTestHarness Fixtures | 344-417 | ✅ Available (naga_harness, naga_harness_minimal, naga_harness_orchestrator) |
| TestableRegistry → pytest Bridge | 888-1000 | ✅ Available (auto-generates tests from registry) |
| Auto-Markers | 96-119 | ✅ Wired (hardening, integration, fractal, e2e auto-tagged) |
| Quality Profiles | 60-94 | ✅ Available (--test-profile=fast/full/ci) |

**The problem is NOT missing infrastructure. The problem is ADOPTION.**

- `naga_harness` fixture: used in **1 of 45** naga test files
- `test_gene` fixture: used in **0** test files (!)
- `MagicMock`: used in **22** test files (should be 0)
- `TestableRegistry` bridge: **0** tests use `registry_test_case`

The conftest.py is a cathedral nobody enters.

## 8. VALIDATION RESULTS (Kritische Prüfung)

### ✅ Mahamantra 16-Step Lifecycle — FUNKTIONIERT
Every test automatically runs 16 steps: Genesis(H-K-H-K) → Dharma(K-K-H-H) → Karma(H-R-H-R) → Moksha(R-R-H-H).
Verified with `--log-cli-level=DEBUG`. Real Mahamantra sequence, correct opcodes.
**Verdict: GOLD. Keep.**

### ✅ TÜV Badges — FUNKTIONIERT
Auto-issued on pass. 19/19 SILVER (Score 0.70 = base 0.5 + speed bonus 0.2).
No GOLD because Gene bonus never fires (see below).
**Verdict: SILVER. Works but capped without Gene fix.**

### ❌ Gene Injection (iGene) — KAPUTT
**BUG: `iGene.is_fatal` compares `entropy_load` (float 0.0-1.0) against `MantraByte.coherence` (int 0-21600).**
`0.3 > 21454` is ALWAYS False. `is_fatal` can NEVER return True.
The entire Gene system is dead code — entropy can never overwhelm coherence.
Root cause: `MantraByte.coherence` returns COSMIC_FRAME scaled int, not float.
Fix: `iGene.is_fatal` should compare `entropy_load > coherence / 21600`.
**Verdict: RED. Do not use until fixed. conftest.py Gene fixtures are decorative.**

### ⚠️ TestableRegistry Bridge — UNTESTED (0 users)
`pytest_generate_tests` hook exists but `registry_test_case` fixture has 0 consumers.
Cannot validate without at least one test using it.
**Verdict: UNKNOWN. Needs adoption to validate.**

### ⚠️ NagaTestHarness — WORKS but LEGACY
Works correctly (verified via test_harness.py). But Naga is outside mahamantra/.
Long-term: Naga capabilities should be assimilated into Mahamantra via adapters.
**Verdict: YELLOW. Works but wrong location for future architecture.**

## 9. Die Vision

```
CURRENT:                              FUTURE:
pytest (9432 dead scripts)            pytest (hardening only, ~500 tests)
  ↓                                     ↓
pass/fail                             ADVERSARIAL attacks
  ↓                                     ↓
nothing                               Cortex signal if attack succeeds
                                        ↓
                                      ShuddhiEngine heals

GAD (unused)                          GAD (immune system)
  ↓                                     ↓
nothing                               scan_lotus() every MALA
                                        ↓
                                      Real-time health dashboard
                                        ↓
                                      Components self-heal
```

The test suite becomes the IMMUNE SYSTEM.
pytest becomes the ADVERSARIAL layer (Kurukshetra).
The Nagas become the CIA that monitors both.
