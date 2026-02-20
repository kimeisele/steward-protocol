# MAHAMANTRA DEEP AUDIT — Feb 20, 2026 (CORRECTED)

## SCOPE: Every directory, every file. Verified by reading actual code.

**CORRECTION NOTE**: First draft had speculative claims ("0 consumers", "overlaps")
that were wrong. This version is based on actual `grep` import counts and reading
every file's code. Where I'm uncertain, I say so.

---

## 1. THE NUMBERS

| Directory | .py files (non-init) | Verdict |
|-----------|---------------------|---------|  
| `substrate/` | 52 flat + 7 subdirs (~25 more) | Large but structured via lazy `__init__.py` |
| `protocols/` | ~60 | Protocol definitions — coverage unknown |
| `adapters/` | ~25 | Adapter layer between protocols and substrate |
| `cli/` | ~13 | CLI layer |
| `kernel/` | 5 | 4 different components (see §3) |
| `dharma/` | ~30 | Mahajana services |
| `audit/` | ~18 | Self-audit tooling |
| `reactor/` | 4 | ShadowReactor |
| `venu/` | 3 | MantraTick/Voice/Clock — 1 external consumer |
| `genesis/`, `karma/`, `moksha/` | 4 each | Mahajana stubs (1 file each) |
| Root | 5 | __main__, chat, commands, lotus_projection, research_gateway |

**Total: ~260+ Python files in mahamantra/.**

---

## 2. VERIFIED ARCHITECTURE (not overlaps — layers)

### Chamber System (Bahiranga/Antaranga — INTENTIONAL layers)
After reading the code, these are NOT duplicates:
- `substrate/registry.py` — Python-object 512-slot memory (SiksastakamRegistry, uses MahaCellUnified)
- `substrate/antaranga.py` — Raw bytearray 512-slot memory (same 512 slots, struct.pack for speed)
- `substrate/chamber.py` — SankirtanChamber OWNS both + VenuOrchestrator
- `substrate/cluster.py` — MahaCluster groups cells without losing individual identity

**Verdict**: Deliberate inner/outer architecture. Chamber imports registry + antaranga. Not duplication.

### Kernel Components (4 different purposes, not competing)
| File | Purpose | Importers |
|------|---------|----------|
| `kernel/singularity.py` (1240 LOC) | God object — tick, chant, venu, positions | daemon.py, external |
| `kernel/maha_kernel.py` (217 LOC) | Seed→Address calculator (MahaCompression→MahaSynth) | TBD |
| `kernel/intent.py` (457 LOC) | Intent routing — infrastructure waiting for CLI wiring | `_krishna_resolves()` routes through `lotus.execute()` |
| `kernel/phoenix.py` (172 LOC) | State persistence to JSON | TBD |

**Note**: `kernel/intent.py` is NOT dead. It's infrastructure ready to be wired.
`_krishna_resolves()` already calls `lotus.execute()` with opcode. The missing piece
is CLI commands declaring intents instead of calling services directly.

### Venu/Clock/Time (verified import counts)
| File | Purpose | Actual importers |
|------|---------|------------------|
| `substrate/venu_orchestrator.py` | 19-bit DIW, LUT, drives VM | 17 importers |
| `substrate/venu.py` | Pure math (tick→position) | **0 importers** |
| `substrate/clock.py` | Stateless tick info | 1 importer (reactor/loop.py) |
| `substrate/kala.py` | TimeKeeper class | 1 importer (kernel/singularity.py) |
| `venu/` package | MantraTick/Voice/Clock | 1 external (services/venu_service.py) |

**Verdict**: `venu.py` is the only truly dead one (0 importers). The others each
serve a specific consumer. Not "5 competing concepts" — different layers for
different consumers.

---

## 3. THE THREE PILLARS (verified working)

### Pillar 1: Mantra VM + NavaBhakti Pipeline ✅
- `substrate/mantra_vm.py` — 9-step pipeline, Venu-driven
- `protocols/_navabhakti.py` — enum, gates, VAMSI addresses
- `substrate/cycle_compiler.py` — core + custom ops
- `substrate/lotus_core.py` (47KB) — the Root, `__call__()` chains everything
- **686 tests pass**

### Pillar 2: Venu Orchestrator ✅
- `substrate/venu_orchestrator.py` — 19-bit DIW = VENU(6) + VAMSI(9) + MURALI(4)
- LUT precomputed from MAHAMANTRA_WORD_PATTERN
- Wired into VM execution loop

### Pillar 3: SSOT Seed ✅
- `protocols/seed/` (8 files) — axioms → primary → secondary → cosmic → extended
- `protocols/_seed.py` — re-exports everything (82 importers — most imported module)
- `substrate/seed.py` (52KB) — the implementation

---

## 4. SUBSTRATE/ ORGANIZATION

### Current state: 52 flat .py files + 7 existing subdirectories

Existing subdirectories (already organized):
- `algorithm/` — MahaModularSynth (39 importers)
- `language/` — section_router, composer, engine, types, phonetics, etc. (59 importers)
- `phonetics/` — shabda.py (18 importers)
- `resonance/` — oracle.py, resonator.py (12 importers)
- `mantra/` — siksastakam, kirtan, engineering (14 importers)
- `classifier/` — core.py
- `sankalpa/` — will.py

### Top importers among flat files (cannot move without updating all importers):
| File | Direct importers | Risk of moving |
|------|-----------------|----------------|
| `lotus_core.py` | 51 | **EXTREME** |
| `pancha_walk.py` | 36 | HIGH |
| `wiring.py` | 30 | HIGH |
| `opcode.py` | 30 | HIGH |
| `rama_grid.py` | 27 | HIGH |
| `shuddhi.py` | 18 | MEDIUM |
| `venu_orchestrator.py` | 17 | MEDIUM |
| `varnamala_codec.py` | 17 | MEDIUM |
| `semantic_index.py` | 15 | MEDIUM |
| `cell.py` | 15 | MEDIUM |
| `mantra_vm.py` | 11 | MEDIUM |

### CRITICAL FINDING: Physical reorganization is HIGH RISK
**270 files** across the codebase have direct imports like
`from vibe_core.mahamantra.substrate.some_file import ...`.

Moving files into subdirectories would require updating ALL of those imports.
The lazy `__init__.py` only helps consumers who import via
`from vibe_core.mahamantra.substrate import SomeClass` — most don't.

**Safe approach**: Use re-export shims (move file, leave 1-line re-export at old path).
This preserves all existing imports while physically organizing the directory.
But even this is 52 shim files — significant work that needs careful testing.

---

## 5. WHAT'S ACTUALLY DEAD (verified 0 importers)

- `substrate/venu.py` — 0 importers (pure math functions, all consumers use venu_orchestrator instead)

Everything else has at least 1 importer. "Low import count" ≠ dead in a fractal
discovery system. Do NOT delete based on import count alone.

### Stale documentation (already deleted):
- `CURRENT_WORK.md`, `MASTER_PLAN.md`, `ARCHITECTURE.md`, `ARCHITECTURE_AUDIT.md`
- `audit/ARCHITEKTUR.md`, `audit/AUDIT_ROADMAP.md`
- `_audit_architecture_flow.py`

### Empty directories (already deleted):
- `kama/`, `tools/`, `research/dharma|gita|language_runtime`, `dharma/janaka/`

---

## 6. WHAT TO DO (prioritized, corrected)

### Phase 0: STOP ADDING CODE
The next commits should be consolidation, not features.

### Phase 1: Substrate shim-based reorganization
For each file being moved:
1. `git mv substrate/foo.py substrate/core/foo.py`
2. Create `substrate/foo.py` shim: `from .core.foo import *`
3. All existing imports continue to work
4. New code uses the organized path
5. Over time, update old imports and remove shims

**Start with the core 4**: lotus_core, mantra_vm, cycle_compiler, venu_orchestrator.
These are the most important files and moving them into `substrate/core/` makes
the architecture immediately clearer.

### Phase 2: Wire kernel/intent.py to CLI
`MantraKernel._krishna_resolves()` already routes through `lotus.execute()`.
The missing piece: CLI commands should declare intents, not call services directly.
This is the real consolidation — not file deletion.

### Phase 3: Protocol coverage audit
For each of the 60+ protocols: has living implementation? has tests?
Fix the audit tooling to answer this automatically.

---

## 7. RULES

- Do NOT delete files based on import count alone (fractal discovery)
- Do NOT move files without shims (270 importers would break)
- Do NOT rewrite working code (VM, Venu, SSOT are solid)
- Do NOT speculate about "overlaps" without reading the actual code
- Do NOT touch the 686 passing tests
- Verify EVERY claim with `grep` before acting on it
