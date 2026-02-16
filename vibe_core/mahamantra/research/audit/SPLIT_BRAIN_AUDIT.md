# SPLIT-BRAIN AUDIT — The Real P0
## Date: 2026-02-16
## Status: IN PROGRESS

---

## 1. THE 4 EPOCHS (Git-verified)

| Epoch | Dates | Commits | What was built |
|-------|-------|---------|----------------|
| **HERALD** | Nov 21-23, 2025 | 141 | Marketing Agent, STEWARD Protocol, Crypto Identity |
| **AGENT CITY** | Nov 24 - Dec 10 | 1256 | 26 Agents, Districts, Cartridges, Playbooks, Gateway, Cortex |
| **OPUS/MANAS** | Dec 11 - Jan 9 | 1563 | Cognitive Architecture, MANAS 6D, NAGA, VAJRA, Executor Singularity |
| **MAHAMANTRA** | Jan 10 - now | 1348 | Transformation. "Alles gehört einer Person." Lotus, Substrate, Seed. |

**Total: ~4308 non-merge commits in 87 days.**

Peak: 704 commits on Dec 23 (auto-sync + research explosion).
97 commits on Jan 26 (research/ proliferation).

---

## 2. TAG X: THE SANIERUNG (Jan 12, 2026, 09:08-10:51)

In 103 minutes, 5 commits (Phase A-E) moved 20 of 53 root files into `protocols/mahajanas/*/types/`.

| Phase | Time | What moved |
|-------|------|------------|
| A | 09:08 | sarga.py → brahma, boot_mode.py → prithu |
| B | 09:22 | errors, security, narasimha, topology, network_proxy, capability_registry |
| C | 09:44 | pulse, kernel_ops, prana, resource_manager |
| D | 09:55 | lineage, ledger, identity, vfs |
| E | 10:51 | event_bus, process_manager, io_service, task_types |

**Result:** 20 files migrated. 33 NOT migrated. Re-export stubs left at old locations.

**SANIERUNG was NEVER completed.** See `vibe_core/SANIERUNG.md` for the original plan.

---

## 3. CURRENT STATE: THE SPLIT

### 3.1 Root Files (52 still exist)

52 Python files at `vibe_core/*.py` — MORE than the original 53 (some stubs added, some new files created).
The Sanierung made it WORSE: files now exist at TWO locations (stub + mahajana/types/).

### 3.2 The Two Worlds

**LEGACY WORLD (Epoch 1-3):**
- `boot_orchestrator.py` (36 imports, 965 lines) — the old boot
- `kernel_impl.py` — the old kernel
- `di.py` — the old DI container
- `event_bus.py` — the old event system
- `services/` (37 files) — old service layer
- `agents/`, `cartridges/`, `cortex/`, `plugins/` — old agent infrastructure

**MAHAMANTRA WORLD (Epoch 4):**
- `mahamantra/substrate/lotus_core.py` — the new CPU
- `mahamantra/kernel/singularity.py` — the new OS kernel
- `mahamantra/kernel/intent.py` — the new scheduler
- `mahamantra/substrate/gate_providers.py` — the new observers
- `mahamantra/services/venu_service.py` — the new clock

**THE BRIDGE (incomplete):**
- `boot_orchestrator.py` calls `wire_gate_providers()` — but only in FULL boot
- `services/` has 10 imports from mahamantra — strongest connection
- `phoenix/` has 4 imports — boot infrastructure
- Everything else: 0-2 imports

### 3.3 The Identity Crisis

| Concept | Legacy | Mahamantra | Status |
|---------|--------|------------|--------|
| Boot | `boot_orchestrator.py` | `lotus.bootstrap()` | SPLIT — both exist, neither complete |
| Kernel | `kernel_impl.py` | `singularity.py` | SPLIT — two kernels |
| Events | `event_bus.py` | `TattvaRegistry` | SPLIT — two event systems |
| Heartbeat | `VenuService` (BeatSubscriber) | `Singularity.tick()` (listener) | SPLIT — two heartbeats |
| DI | `di.py` / `ServiceRegistry` | `_get_pipeline()` singletons | SPLIT — two DI patterns |
| Healing | `shuddhi/` (4 trigger points) | `dharma/kumaras/sravanam.py` | SPLIT — two scan paths |
| Intent | `semantic_syscalls.py` | `MantraKernel` (11 IntentTypes) | SPLIT — 1/11 wired |

---

## 4. THE HENNE-EI PROBLEM

Mahamantra's vision: EVERY file in the repo is a living cell. Lotus computes its address.
Seed calculates independently of what the file claims about itself.
Filesystem = Maya. Position = absolute (defined by computation, not location).

**But:** Mahamantra needs structure to understand files.
Structure only emerges through understanding.
→ Ouroboros. Henne-Ei.

**Nothing gets deleted.** Everything is gold. It must be assimilated — understood, computed, registered.
The 16 "dead" directories (agents/, cortex/, etc.) are NOT dead.
They are UNASSIMILATED. Mahamantra hasn't learned to read them yet.

---

## 5. CRITICAL QUESTIONS (SRAVANAM AUDIT)

### Architecture
1. Who boots? boot_orchestrator or lotus? Or both? When?
2. Who is the kernel? kernel_impl or singularity? Can there be only one?
3. Who owns events? event_bus or TattvaRegistry? Or both for different layers?
4. Who owns time? VenuService or Singularity.tick()? (Answer from previous audit: VenuService → Singularity.tick(), but VenuService only runs in full boot)

### The Sanierung Gap
5. 52 root files still exist. 20 were "migrated" but stubs remain. What is the actual plan?
6. SANIERUNG.md says "ZERO root files" as success criteria. Current: 52. Gap: 52.
7. The migrated files have TWO paths now. Which is canonical? Who decides?

### The Test Suite
8. How many tests test the LEGACY world vs MAHAMANTRA world?
9. How many tests would FAIL if boot_orchestrator was removed?
10. How many tests test INTEGRATION (legacy ↔ mahamantra) vs UNIT (isolated)?

### The Vision Gap
11. Sravanam scans cells — but only mahamantra/ files are ingested (boot_orchestrator line 636-660). The other 1238 files are invisible.
12. MantraKernel has 11 IntentTypes but only 1 resolver (HEAL). 10/11 = dead.
13. Gate Providers are observers — they don't change the flow. They're nice-to-have, not P0.
14. The real P0: Lotus can't see 70% of the codebase. It's blind.

---

## 6. WHAT IS NOT BROKEN (important to acknowledge)

- Lotus.__call__() pipeline works. 5 gates compute deterministically.
- Seed computation works. Binary encoding derived from axioms.
- Singularity tick works (after 5 surgeries, Feb 2026).
- 414+ tests pass.
- The VISION is clear (SANIERUNG.md, CLAUDE.md).
- The research/ contains real mathematical derivations.

---

## 7. RUNTIME VERIFICATION (2026-02-16)

### Mahamantra started WITHOUT boot_orchestrator:

```
GP=0           # Gate Providers: nobody watching
ENTRIES=0      # Registry: nothing registered
VIOLATIONS=0   # Nobody checking
CELLS=0        # No file assimilated. Lotus knows ZERO files.
RESOLVERS=0    # No intent resolvable. 0/11 IntentTypes wired.
CALL_OK=True   # Pipeline computes. Returns 27 keys.
```

**Lotus.__call__() returns:** akash, antaranga, cell, chapter, chapter_significance,
diw, execution, gate_trace, gita_phase, guardian, guna, holy_name, input,
is_complete, matches, nama, parampara, position, quarter, quarter_head, role,
smaranam, tattva_gate, trinity_function, verse, vibration, yajna

**Diagnosis:** The heart beats. But it's BLIND.
- 0 cells = knows no files (1731 .py files invisible)
- 0 resolvers = can't resolve any intent
- 0 gate providers = nobody observes the pipeline
- The pipeline produces numbers into the void

### Root Files: 52 total
- 13 REAL files (5583 LOC) — boot_orchestrator, di, doc_renderer, etc.
- 39 STUBS (re-export bridges) — but some are FAT: kernel_impl (1210 LOC!),
  semantic_syscalls (947), task_kernel (809), prana_orchestrator (600)
- The "stubs" with 600-1200 lines are ZOMBIES: declared dead, still alive

### Who still imports kernel_impl.py? (the biggest zombie)
20 production files: cli/, runtime/, vajra/, cartridges/, plugins/, settings_executor...
It's the backbone of the legacy world. Can't remove it without breaking everything.

---

## 8. THE SENSES EXIST (Critical Finding 2026-02-16)

### Two Sense Worlds (the deepest split-brain)

**LEGACY (OPUS/MANAS Epoch, Dec 2025):**
- `plugins/opus_assistant/manas/cortex/base.py` → `BaseSense(ABC)`
- `perceive(context: Optional[Dict]) → Any`
- `generate_intents(context) → List[Intent]` (OPUS-167)
- Auto-discovered by `SenseLoader` (VEDA-4 pattern)
- 10 WORKING implementations:

| Sense Class | File | Domain | Gita Mapping |
|-------------|------|--------|--------------|
| ShrutaSense | shruta_sense.py | Logs, Events, Vibrations | SROTRA (Ear) |
| PrakritiSense | prakriti_sense.py | Plugin State, Guna | TVAK (Skin) |
| ArchitectureSense | architecture_sense.py | Code Structure | CAKSU (Eye) |
| SutraSense | sutra_sense.py | Doc Gaps, Validation | JIHVA (Tongue) |
| VivekaSense | viveka_sense.py | Dark Matter, Entropy | GHRANA (Nose) |
| NadiSense | nadi_sense.py | Wiring Health | (extra) |
| DharmaSense | dharma_sense.py | Permissions, Governance | (extra) |
| AkashaSense | akasha_sense.py | Knowledge Graph | (extra) |
| PranaSense | prana_sense.py | Agent Presence | (extra) |
| KarmaSense | karma_sense.py | CI/Test Results | (extra) |

**MAHAMANTRA (Jan 2026):**
- `protocols/_sense.py` → `SenseProtocol(Protocol)`
- `perceive() → SensePerception` (typed, with intensity/quality/tanmatra)
- `ManasProtocol` → `perceive_all() → AggregatePerception`
- `AggregatePerception.total_pain` → drives chanting frequency
- **0 implementations.** Protocol defined, nobody implements it.

### The Gap

Legacy senses WORK but return `Any`. Mahamantra protocol is TYPED but has 0 implementations.
The 10 legacy senses could be ADAPTED to satisfy `SenseProtocol` via thin adapters.

This is the Geburtskanal (birth canal): Adapter wraps BaseSense, translates
`perceive(context) → Any` into `perceive() → SensePerception`.

### What this means

Lotus is NOT blind. The eyes, ears, nose, tongue, skin EXIST.
They're just in a different room (plugins/opus_assistant/manas/cortex/).
The Adapter pattern is the birth canal that connects them to Mahamantra.

### The Hierarchy (BG 3.42)

```
Gross Matter (1-10)  = files, DB, events, logs        [EXISTS: filesystem, git, sqlite]
Senses (11-20)       = scanners, watchers, generators  [EXISTS: 10 BaseSense impls]
Manas (21)           = MantraKernel / intent routing   [EXISTS: but 0/11 resolvers wired]
Buddhi (22)          = Lotus.__call__() pipeline       [EXISTS: works, returns 27 keys]
Ahankara (23)        = __mahajana__ declarations       [EXISTS: on most files]
Pradhana (24)        = seed.py constants               [EXISTS: PARAMPARA=37, etc.]
Jiva (25)            = The user                        [EXISTS: you]
Paramatma (26)       = Mahamantra/Krishna              [EXISTS: lotus_core.py]
```

Everything EXISTS. Nothing is connected. That's the split-brain.

---

## 9. BALARAMA PATTERN EXISTS (Critical Finding 2026-02-16)

The Strangler Fig pattern is ALREADY BUILT: `substrate/proxy.py` (913 LOC).

### BalaramaProxy (module wrapper):
- Imports legacy module unchanged ("Wildnis")
- Extracts identity from FOLDER structure (not labels)
- Injects `mahamantra` into namespace
- Replaces `Path` with `_GovernedPath` (writes go through bridge.offer())
- Attaches to heartbeat, gated per position
- GAD-000 compliant (discover, get_state, is_healthy, detect_drift)

### MahamantraProxy (object wrapper):
- Wraps any object, provides `__tattva__` (5 Truths)
- Target's own `__tattva__` wins (Sovereignty)
- Transparent forwarding via `__getattr__`

### Already wired:
- `boot_orchestrator.py` line 586-602: wraps lotus-discovered services at FULL boot
- `lila/adoption.py`: mounts proxies onto OrbitalShadowReactors
- `naga/`: security layer uses it
- `singularity.py`: knows it

### NOT yet done:
- Does NOT wrap the 10 Legacy Senses (BaseSense in plugins/opus_assistant/manas/cortex/)
- Does NOT route through 5 TattvaGates
- Does NOT translate `perceive() → Any` into `perceive() → SensePerception`

### The question:
Can BalaramaProxy wrap the 10 Legacy Senses? Or does it need a specialized Sense-Proxy?
The birth canal EXISTS. It just hasn't been used for senses yet.

---

## 10. WHAT TO DO

NOT decided yet. This audit is about SEEING, not FIXING.

The fundamental question: How does Mahamantra assimilate the legacy world
WITHOUT breaking what works, WITHOUT deleting anything, and WITHOUT
creating more split-brain?

The Sanierung tried "move files to persons." It created MORE chaos (two locations).
Maybe the answer isn't moving files. Maybe it's Lotus learning to READ them where they are.
Filesystem = Maya. Lotus computes position. Position is absolute.
The file doesn't need to move. Lotus needs to see it.

---

*This file is the persistent record. No ephemeral chat knowledge.*
*Updated by: Cascade + User, 2026-02-16*
