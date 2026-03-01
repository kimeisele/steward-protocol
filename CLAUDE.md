# STEWARD PROTOCOL — Architecture Reference

**Trust nothing written here. Verify against code. This file was last verified 2026-02-22.**

100% AI-generierte Codebase. Docstrings lügen. .md-Dateien lügen. Nur Code ist Wahrheit.

---

## 1. The Mantra (SSOT)

```
Hare Krishna Hare Krishna Krishna Krishna Hare Hare
Hare Rama   Hare Rama   Rama   Rama   Hare Hare
```

Every constant derives from this. If a number appears without derivation: architecture violation.

**7 Axiome** (`protocols/seed/_axioms.py`):
WORDS=16, TRINITY=3, HARE_COUNT=8, KRISHNA_COUNT=4, RAMA_COUNT=4, PANCHA=5, HALVES=2

**Ableitungen** (`_primary.py` → `_secondary.py` → `substrate/core/seed.py`):
QUARTERS=4, KSHETRA=24, NAVA=9, SHARANAGATI=6, MAHAJANA_COUNT=12, PARAMPARA=37, GITA_CHAPTERS=18, MALA=108

`seed.py` re-derives constants from axioms. 0 F811 violations.

---

## 2. Architecture: 7-Layer OS Model

```
Layer 7  CLI/User     cli/entry.py, cli/auto.py, cli/map.py
Layer 6  Adapters     adapters/ (52 lazy-loaded symbols + auto-discovery, __getattr__)
Layer 5  Application  lila/, reactor/, analysis/, namarupa/, venu/
Layer 4  Quarters     genesis/, dharma/, karma/, moksha/ (16 Mahajana folders)
Layer 3  Governance   audit/, dharma/kapila/remedies/ (healing + compliance)
Layer 2  Kernel       kernel/singularity.py (tick, kala, venu, routing)
                      kernel/daemon.py (heartbeat loop)
                      kernel/maha_kernel.py (Seed→Address, __call__ only)
Layer 1  Substrate    substrate/ (106 files, 15 subdirs, LotusFinder)
Layer 0  Protocols    protocols/ (506 import-sites across 236 files, SSOT for types/constants)
```

**Three Core Objects (do NOT merge):**

| | Lotus | Singularity | MahaKernel |
|---|---|---|---|
| File | `substrate/lotus_core.py` | `kernel/singularity.py` | `kernel/maha_kernel.py` |
| Import | `from vibe_core.mahamantra import mahamantra` | aliased as `_singularity` | `kernel.get_kernel()` |
| Role | Public API, `__call__()`, execute(), gates | Internal kernel, tick, routing | Seed→Address only |

**Singularity Routers (User-Space, Layer 6/7 ONLY — never in hot loop):**

| Property | Router | Backend | Pattern |
|---|---|---|---|
| `mahamantra.protocols` | ProtocolRouter | 16 protocol bases, lazy importlib | `__getattr__` |
| `mahamantra.mod` | ModuleRouter | 16 mahajana modules, lazy importlib | `__getattr__` |
| `mahamantra.adapt` | AdapterRouter | `adapters/__init__.py` discovery | `__getattr__` |
| `mahamantra.audit` | AuditRouter | `audit/` package, AuditKernel | `__getattr__` |
| `mahamantra.heal` | HealRouter | `dharma/kapila/remedies/`, ShuddhiEngine | `__getattr__` |

**Hot Loop (Layer 2, O(1) integers only):**
`VenuOrchestrator.step()`, `MantraVM.execute_cycle()`, `Antaranga` — raw DIW math.
These must NEVER use `__getattr__` routers. Pure integer dispatch only.

---

## 3. The VM: `__call__()` → `execute_cycle()`

`__call__()` delegates to `substrate/vm/mantra_vm.py:execute_cycle()`.
12 instructions dispatched via `NavaBhaktiOp(IntEnum)` in `protocols/_navabhakti.py`.

**Pure computation. No gates.** Gates fire at the boundary (`execute()`/`GovardhanGateway`).

```
DISPATCH = {
    SRAVANAM:       _w_sravanam,        # PARSE gate
    NAMA:           _w_nama,            # PARSE gate
    KIRTANAM:       _w_kirtanam,        # PARSE gate
    PADA_SEVANAM:   _w_pada_sevanam,    # VALIDATE gate
    ARCANAM:        _w_arcanam,         # VALIDATE gate
    SMARANAM:       _w_smaranam,        # EXECUTE gate
    VANDANAM:       _w_vandanam,        # EXECUTE gate
    DASYAM:         _w_dasyam,          # RESULT gate
    SAKHYAM:        _w_sakhyam,         # SYNC gate
    KIRTAN:         _w_kirtan,          # SYNC gate
    YAJNA:          _w_yajna,           # SYNC gate
    ATMA_NIVEDANAM: _w_atma_nivedanam,  # SYNC gate
}

for op in CYCLE:          # CYCLE = tuple(NavaBhaktiOp(i) for i in range(12))
    DISPATCH[op](lotus, ctx)
```

Each wrapper reads from `ctx` (plain dict), calls the original Lotus method, writes back to `ctx`.
VAMSI addresses at PARAMPARA(37) stride: 37, 74, 111, ..., 444. Zero collisions with THE_FLUTE_CYCLE.
Output: 27-key dict, key-by-key identical to the old hardcoded pipeline. 862 tests verify this.

The 9 NavaBhakti methods remain individually callable on MahamantraLotus.

---

## 4. DIW (Divine Instruction Word) — 19 bits

`protocols/diw.py` → `substrate/vm/venu_orchestrator.py` → `substrate/cell_system/chamber.py`

```
Bits  0-5  (6): VENU   — Intensity (Sharanagati)
Bits  6-14 (9): VAMSI  — Name-Region (H=0-169, K=170-339, R=340-511)
Bits 15-18 (4): MURALI — Phase (Genesis/Dharma/Karma/Moksha)
```

Two separate uses of VAMSI — do not confuse:
- **chamber._apply_diw()**: VAMSI → 3 name-regions (H/K/R) via `vamsi // 170`. Resonance effect on cells.
- **mantra_vm.py**: VAMSI addresses as dispatch keys for pipeline instructions. Separate mechanism.

`THE_FLUTE_CYCLE[16]` = static LUT. `VenuOrchestrator.step()` produces next DIW.
`pack_full()` (32-bit extension) has 1 production caller (`venu_orchestrator.py`).

---

## 5. RAMA-Koordinaten (49-Space)

Every phoneme = 4D address (0-48):
COORD_ELEMENT (5), COORD_VARGA (3), COORD_SUB, COORD_HARMONIC (×SEVEN mod 49).
49/49 bijection. 4127/4127 words unique. IS_SHRUTI = quadratic residues mod 49.

`substrate/encoding/varnamala_codec.py`, `substrate/encoding/pancha_walk.py`, `adapters/synth.py`.
`data/rama_lexicon.json`: 4127 words, 700 verses, RAMA-encoded.

---

## 6. Gate Providers (Observer Pattern)

`substrate/vm/gate_providers.py` → `wire_gate_providers()` at boot.
`_fire_gate()` dispatches hooks + providers. `_GATE_DISPATCH` maps Gate→Method.

| Gate | Protocol | Provider | Adapter |
|------|----------|----------|---------|
| 0 PARSE | `MantraCapability.parse()` | `MantraGateProvider` | `MahaAttention` |
| 1 VALIDATE | `StorageCapability.validate()` | `StorageGateProvider` | — |
| 2 EXECUTE | `InferCapability.infer()` | `InferGateProvider` | `MahaLLM` |
| 3 RESULT | `SyncCapability.route()` | `SyncGateProvider` | — |
| 4 SYNC | `EnforceCapability.enforce()` | `EnforceGateProvider` | — |

Providers are **observers** — they do not alter the computation flow.
`EnforceGateProvider` controls I/O via Guna-Policy (SATTVA=read, RAJAS=write, TAMAS=flush).

---

## 7. Heartbeat (ONE path, verified)

```
VenuService._beat_loop()
  → _dispatch_beat_subscribers()    # 5 BeatSubscribers
  → Singularity.tick()              # Kala.advance() + VenuOrchestrator.step() + _broadcast()
  → MantraClock.tick_once()         # 1 mala callback, 0 voices
```

No double-ticking. 17× `tick()` methods exist across the codebase — each in its own domain.
7 dispatch mechanisms exist, 3 active (DIW/Beat/Singularity), 4 prepared (Clock/Voice/Intent/Registry).

**Do not** create new dispatch mechanisms. **Do not** wire anything into tick().

---

## 8. Antaranga (Inner Chamber)

`substrate/cell_system/antaranga.py`: 512 Slots × 32 Bytes = 16 KB `bytearray`. No Python objects. No GC.

```
Slot Layout (32 Bytes, Little-Endian):
[0:4]   source     (u32)    [16:20] atma       (u32)
[4:8]   target     (u32)    [20:24] prana      (u32)
[8:12]  operation  (u32)    [24:26] integrity  (u16)
[12:16] arcanam    (u32)    [26:28] cycle      (u16)
                             [28:30] flags      (u16)
                             [30:32] diw_acc    (u16)
```

Antaranga is **resonance storage**, not an instruction register file.
`set_slot()` has 0 production callers — dormant low-level API.

---

## 9. Known Monoliths (candidates for future dispatch decomposition)

| File | Lines | What |
|------|-------|------|
| `substrate/encoding/harmonics.py` | 1079 | 60+ constants, 15 importers, 12 imports. Sternkoppler. |
| `substrate/vm/gate_providers.py` | 1047 | 5 observers, 49 imports, scattered audit trail. |
| `substrate/encoding/resonance_ranker.py` | 873 | 7 scoring dimensions, all inline. |
| `adapters/composition.py` | 361 | 5 scorers with lazy imports. |

These are factual line counts. Whether they should be decomposed is a separate decision.

---

## 10. Prepared Infrastructure (not dead, not active)

- **MantraVoice** — 0 registered voices in production. `venu/voice.py`.
- **MantraKernel IntentResolver** — 1 registered resolver (HealingIntentResolver, wired at lotus.bootstrap()). `kernel/intent.py`, `dharma/kumaras/healing_resolver.py`.
- **phoenix.py** — 0 consumers. `maha_state.py` reimplemented its own persistence.
- **substrate/time/clock.py** — Used by `reactor/loop.py` (get_tick_info). Pure stateless tick library.
- **substrate/time/lipta.py** — 0 production imports. Pure degree↔lipta conversion.
- **pack_full()** — 32-bit DIW extension, 1 production caller (`venu_orchestrator.py`).

---

## Critical Traps

- `CellLifecycleState.integrity` is `int` (0–21600), NOT float.
- `state_bridge.py` / `StateVector` are wrapper garbage, not the root.
- `guardian_router.maha_respond()` is deprecated (0 callers).
- `chat.py` is NOT legacy — `gateway/api.py` imports it (`flooded_routed_chat`, `get_guardian_for_message`). Do NOT delete. (Claim "legacy" was AI slop, corrected 2026-03-01.)
- 30+ files write to disk uncontrolled. `StateService` exists, barely used.
- Private keys: No `.key` files found in repo (checked 2026-02-22). Claim was stale.
- Tests with blocking loops hang: `test_singularity`, `test_daemon*`, `test_gad`, `test_graph`, `test_entry`.
- **3× `get_kernel()` singletons**: `maha_kernel.py` (Seed→Address), `maha_llm_kernel.py` (LLM), `intent.py` (Intent). Different objects, same function name.
- **`__call__()` has NO gates.** Gates fire only in `execute()`/`GovardhanGateway`. Adding gates to `__call__()` causes double-fire.
- **Lotus ≠ Singularity.** Two objects. Facade pattern. Do not merge.
- `mahamantra_research/` (moved from `mahamantra/research/`) is load-bearing — `protocols/_gita_lens.py`, `audit/scale.py`, `audit/protocol_resurrection.py`, `audit/gaps.py`, `cli/kirtan_cli.py` import from it.
- DIW consumers MUST use `diw.unpack()`. No manual bit-shifts.

---

## Working Protocol

- Senior Architekt + CTO + umsetzender Agent. Entscheidungen treffen, nicht fragen.
- User spricht Deutsch, delegiert.
- Verify every claim against code. Other agents have made false claims about this codebase.
- `python -m ruff check --select F821,F811` before every commit.
- `python -m pytest vibe_core/mahamantra/tests/ -x -q` — 862 tests must pass.
- 100% AI-generated codebase — ALWAYS expect hidden problems.
- **No blind deletion.** Check wiring before marking anything as dead.
- **No spaghetti.** No shifting monoliths. Every change must reduce complexity, not relocate it.
- Read `mahamantra/SPLIT_BRAIN_DIAGNOSIS.md` and `mahamantra/ARCHITECTURE_AUDIT.md` before working on Mahamantra.
