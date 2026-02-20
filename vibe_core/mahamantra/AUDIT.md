# MAHAMANTRA DEEP AUDIT — Feb 20, 2026

## SCOPE: Every directory, every file. No sugarcoating.

---

## 1. THE NUMBERS

| Directory | .py files (non-init) | Size | Verdict |
|-----------|---------------------|------|---------|
| `substrate/` | ~75 | ~900KB | **THE BLOB** — half the codebase lives here |
| `protocols/` | ~60 | ~400KB | Protocol definitions, many without living implementations |
| `adapters/` | 25 | ~300KB | Adapter layer between protocols and substrate |
| `cli/` | 13 | ~200KB | Multiple overlapping entry points |
| `kernel/` | 5 | ~100KB | 4 different "kernel" concepts competing |
| `dharma/` | ~30 | ~150KB | Mahajana services (kapila, kumaras, components) |
| `audit/` | ~18 | ~100KB | Self-audit tooling, partially broken |
| `reactor/` | 4 | ~100KB | ShadowReactor (complex, working) |
| `analysis/` | 3 | ~60KB | Derivation graph, universal generator |
| `lila/` | 5 | ~55KB | Adhikara, adoption, jiva_shadow, migration, registry |
| `venu/` | 3 | ~9KB | MantraTick/Voice/Clock — **UNUSED** |
| `genesis/` | 4 | ~10KB | Brahma, Narada, Shambhu, Vyasa stubs |
| `karma/` | 4 | ~10KB | Bhishma, Janaka, Parashurama, Prahlada stubs |
| `moksha/` | 4 | ~10KB | Bali, Nrisimha, Shuka, Yamaraja stubs |
| `namarupa/` | 2 | ~12KB | akshara.py, atom.py |
| `demos/` | 2 | ~29KB | bio_indexer, log_sentinel |
| `net/` | 1 | ~5KB | vimana.py |
| `sound/` | 1 | ~4KB | audio_engine.py |
| `seed/` | 1 | ~6KB | types.py |
| `research/` | 1 | ~1KB | __init__.py only, all subdirs empty |
| Root | 5 | ~90KB | __main__, chat, commands, lotus_projection, research_gateway |

**Total: ~260+ Python files, ~2.5MB of code in mahamantra/ alone.**

---

## 2. THE OVERLAPS (Same concept, multiple implementations)

### OVERLAP A: "Kernel" (4 competing concepts)

| File | What it does | Who uses it |
|------|-------------|-------------|
| `kernel/singularity.py` (1240 LOC) | The "Mahamantra" god object — tick, chant, venu, governance, positions | daemon.py, external consumers |
| `kernel/maha_kernel.py` (217 LOC) | "Military Grade" — MahaCompression → MahaSynth → Address | Few consumers |
| `kernel/intent.py` (457 LOC) | MantraKernel — intent routing with 0 registered resolvers | **NOBODY calls it from CLI** |
| `substrate/maha_llm_kernel.py` (460 LOC) | "Deterministic Language Model" — RAMA coords, resonance, expansion | lotus_core pipeline |

**Problem**: 4 things called "kernel", none of them is THE kernel. Singularity is the closest but it delegates computation to Lotus. MahaKernel is a seed→address calculator. MantraKernel is intent infrastructure with 0 wiring. MahaLLMKernel is the language processing engine.

### OVERLAP B: "Venu/Clock/Time" (5 competing concepts)

| File | What it does | Who uses it |
|------|-------------|-------------|
| `substrate/venu_orchestrator.py` (573 LOC) | **THE REAL ONE** — 19-bit DIW, LUT, drives VM | VM, lotus_core |
| `substrate/venu.py` (364 LOC) | Pure math functions for tick→position | Some consumers |
| `substrate/clock.py` (266 LOC) | Stateless tick library | **UNWIRED** |
| `substrate/kala.py` (75 LOC) | TimeKeeper (ticks→mantras→malas) | Singularity |
| `venu/` package (3 files, ~9KB) | MantraTick, MantraVoice, MantraClock | **NOBODY** (per SPLIT_BRAIN_DIAGNOSIS) |

**Problem**: 5 time/rhythm concepts. Only `venu_orchestrator.py` actually drives anything. The rest are either pure math libraries (fine but overlapping) or dead infrastructure.

### OVERLAP C: "Phonetics/Encoding" (4+ files)

| File | What it does |
|------|-------------|
| `substrate/phonetic_encoder.py` (9KB) | Text → RAMA coordinates |
| `substrate/phonetic_bridge.py` (29KB) | Bridge between phonetic systems |
| `substrate/varnamala_codec.py` (9KB) | Sanskrit alphabet codec |
| `substrate/rama_grid.py` (17KB) | RAMA coordinate grid (SVARAS, SPARSHA) |
| `substrate/pancha_walk.py` (13KB) | 4D coordinate walking |
| `substrate/phonetics/` (subpackage) | Additional phonetic modules |

**Problem**: Phonetic encoding is spread across 5-6 files. Some may be layers (encoder uses grid uses codec), but the boundaries are unclear.

### OVERLAP D: "State/Persistence" (3 competing concepts)

| File | What it does | Who uses it |
|------|-------------|-------------|
| `substrate/maha_state.py` (28KB) | Sovereign state — MahaState singleton | Active, multiple consumers |
| `kernel/phoenix.py` (5KB) | State persistence to JSON | **0 consumers** (maha_state reimplemented it) |
| `substrate/memory.py` (6KB) | Key-value memory to JSON | Unknown |

### OVERLAP E: "CLI Entry" (5+ entry points)

| File | What it does |
|------|-------------|
| `__main__.py` (9KB) | `python -m vibe_core.mahamantra` — goes through VM ✅ |
| `cli/entry.py` (10KB) | `steward <command>` — partially wired |
| `cli/steward.py` (19KB) | Steward resonance router — goes through VM ✅ |
| `cli/auto.py` (24KB) | Protocol introspection — **BYPASSES VM** |
| `cli/engine.py` (15KB) | CLI engine |
| `cli/protocol.py` (24KB) | CLI protocol definitions |
| `commands.py` (25KB) | Root-level CLI commands |
| `chat.py` (31KB) | Guardian chat — **BYPASSES VM entirely** |

---

## 3. THE DEAD WEIGHT

### Confirmed empty/skeleton:
- `kama/` — empty (deleted in cleanup)
- `tools/` — empty (deleted in cleanup)
- `research/dharma/`, `research/gita/`, `research/language_runtime/` — empty (deleted)
- `dharma/janaka/` — empty (deleted)
- `genesis/brahma/`, `genesis/narada/`, `genesis/shambhu/`, `genesis/vyasa/` — 1-file stubs each
- `karma/bhishma/`, `karma/janaka/`, `karma/parashurama/`, `karma/prahlada/` — 1-file stubs each
- `moksha/bali/`, `moksha/nrisimha/`, `moksha/shuka/`, `moksha/yamaraja/` — 1-file stubs each

### Confirmed unused infrastructure:
- `venu/` package (MantraTick, MantraVoice, MantraClock) — 0 consumers
- `kernel/phoenix.py` — 0 consumers (maha_state.py reimplemented persistence)
- `kernel/intent.py` MantraKernel — infrastructure ready, 0 callers from CLI
- `substrate/clock.py` — unwired
- `substrate/lipta.py` — unwired (48 LOC, degree↔lipta conversion)

### Stale documentation (deleted in cleanup):
- `CURRENT_WORK.md` (empty), `MASTER_PLAN.md`, `ARCHITECTURE.md`, `ARCHITECTURE_AUDIT.md`
- `audit/ARCHITEKTUR.md`, `audit/AUDIT_ROADMAP.md`
- `_audit_architecture_flow.py` (one-off script)

---

## 4. THE THREE PILLARS (what's actually working)

### Pillar 1: Mantra VM + NavaBhakti Pipeline ✅
- `substrate/mantra_vm.py` — 9-step pipeline, Venu-driven, 686 tests pass
- `protocols/_navabhakti.py` — enum, gates, VAMSI addresses
- `substrate/cycle_compiler.py` — core + custom ops
- `substrate/lotus_core.py` (47KB) — the Root, `__call__()` chains everything

### Pillar 2: Venu Orchestrator ✅
- `substrate/venu_orchestrator.py` — 19-bit DIW = VENU(6) + VAMSI(9) + MURALI(4)
- LUT precomputed from MAHAMANTRA_WORD_PATTERN
- Now wired into VM execution loop
- `protocols/diw.py` — bit layout protocol
- `protocols/_venu.py` — DIWEvent, subscriber protocol

### Pillar 3: SSOT Seed ✅
- `protocols/seed/` (8 files) — axioms → primary → secondary → cosmic → extended
- `protocols/_seed.py` — re-exports everything
- `substrate/seed.py` (52KB) — the implementation (ALL_GUARDIANS, MAHAMANTRA_SEQUENCE, etc.)

---

## 5. THE REAL PROBLEMS (not markdown)

### Problem 1: substrate/ is a 75-file dumping ground
Everything that isn't a protocol or adapter got thrown into substrate/. It contains:
- Core computation (lotus_core, mantra_vm, venu_orchestrator)
- Data structures (cell, cell_router, lotus_radix)
- Encoding (phonetic_encoder, phonetic_bridge, varnamala_codec, rama_grid)
- Services (shuddhi, sankirtan, samana_bridge, guardian_router)
- State (maha_state, ledger, config)
- Infrastructure (event_bus, process_manager, proxy, registry)
- Math libraries (harmonics, resonance_ranker, basin_map, nadi)
- Bridge layers (bridge, samana_bridge, phonetic_bridge, wordnet_bridge)
- Legacy (lila_chronology at 55KB alone)

**This is not a "substrate" — it's everything.**

### Problem 2: No clear build vs runtime separation
The system claims to have "build phase" and "runtime phase" but:
- `lotus.bootstrap()` does build-time work (gate providers, cycle compiler)
- `execute_cycle()` does runtime work (VM dispatch)
- But `singularity.tick()` is a separate runtime loop
- And `daemon.py` is yet another runtime loop
- And `venu/clock.py` is yet another (unused) runtime loop

### Problem 3: 60+ protocol files, unknown implementation coverage
`protocols/` has 60+ files defining interfaces. How many have living implementations?
Nobody knows. The audit tooling in `audit/` was supposed to check this but is "fundamentally broken" per its own documentation.

### Problem 4: CLI is a maze
5+ entry points, each building its own world. Some go through VM, some don't.
`cli/auto.py` (24KB) does protocol introspection to discover commands — clever but bypasses the VM.

---

## 6. WHAT TO DO (prioritized)

### Phase 0: STOP ADDING CODE
The codebase is at ~260 files / 2.5MB in mahamantra/ alone. Every new file makes it worse.
The next 10 commits should be consolidation, not features.

### Phase 1: Organize substrate/ (the biggest win)
Split the 75-file blob into clear subdirectories:
```
substrate/
  core/          ← lotus_core, mantra_vm, cycle_compiler, venu_orchestrator
  encoding/      ← phonetic_encoder, phonetic_bridge, varnamala_codec, rama_grid, pancha_walk
  data/          ← cell, cell_router, lotus_radix, seed, seed_to_words
  services/      ← shuddhi, sankirtan, guardian_router, samana_bridge
  state/         ← maha_state, ledger, config, memory
  infra/         ← event_bus, process_manager, proxy, registry, io_sentinel
  math/          ← harmonics, resonance_ranker, basin_map, nadi, guna
  bridge/        ← bridge, phonetic_bridge, wordnet_bridge, samana_bridge
  legacy/        ← _legacy, lila_chronology, acintya, tattva
```
This is a RENAME operation — no logic changes, just `git mv`. Imports update via the lazy `__init__.py`.

### Phase 2: Kill confirmed dead code
- Delete `venu/` package (MantraTick, MantraVoice, MantraClock) — 0 consumers
- Delete `kernel/phoenix.py` — 0 consumers, maha_state reimplemented it
- Delete `substrate/clock.py` — unwired, overlaps with venu.py and kala.py
- Delete `research/` — empty subdirs, 1-file __init__.py

### Phase 3: Consolidate kernel/
- Singularity = the god object (tick, governance)
- MahaKernel = seed→address (fold into lotus_core or singularity)
- MantraKernel = intent routing (keep, but WIRE IT to CLI)
- MahaLLMKernel = language engine (rename to something that doesn't say "kernel")

### Phase 4: Wire CLI through MantraKernel
- All CLI commands become intent declarations
- MantraKernel resolves intents through VM
- cli/auto.py stops calling services directly
- chat.py routes through VM

### Phase 5: Protocol audit
- For each of the 60+ protocols, verify: has living implementation? has tests?
- Delete ghost protocols (no implementation, no tests, no consumers)
- This is the audit/ folder's job — fix the audit tooling first

---

## 7. WHAT NOT TO DO

- Do NOT delete files just because they have low import counts (fractal discovery)
- Do NOT rewrite working code (VM, Venu, SSOT are solid)
- Do NOT add more .md files (this is the ONLY audit doc now)
- Do NOT add features until substrate/ is organized
- Do NOT touch the 686 passing tests
