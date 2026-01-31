# MAHAMANTRA ARCHITECTURE AUDIT

**Status:** IN PROGRESS
**Files:** 304 Python files in vibe_core/mahamantra/
**Last Updated:** 2026-01-31

---

## PURPOSE

This folder contains RESEARCH TASKS for understanding the mahamantra architecture.
Each file is a self-contained investigation that can be worked on independently.

**Goal:** Create a complete architecture map of 304 files → understand what exists, what's redundant, what's missing.

---

## FOLDER STRUCTURE (DISCOVERED)

```
vibe_core/mahamantra/
├── adapters/          # Adapter layer (routing, compression, etc.)
├── analysis/          # Analysis tools (narada_vina/)
├── cli/               # CLI entry points and protocols
├── data/              # Data files (?)
├── demos/             # Demo scripts
├── dharma/            # Quarter: prithu, kumaras, kapila, manu
├── genesis/           # Quarter: vyasa, brahma, narada, shambhu
├── kama/              # ? (shuka subfolder)
├── karma/             # Quarter: parashurama, prahlada, janaka, bhishma
├── kernel/            # Core kernel (singularity.py?)
├── lila/              # Lila boundaries and logic
├── moksha/            # Quarter: nrisimha, bali, shuka, yamaraja
├── net/               # Networking (vimana?)
├── protocols/         # Interfaces (_seed.py, sankalpa/)
├── reactor/           # Reactor pattern
├── research/          # Research experiments
├── sound/             # Audio/Sonification
├── substrate/         # Core data structures
├── venu/              # Venu (Flute) subsystem
└── [root files]       # orchestrator.py, chamber.py, cell.py, etc.
```

---

## TASK FILES

Each task file follows this format:
- **QUESTION:** What are we trying to understand?
- **FILES TO READ:** Specific paths to investigate
- **CHECKLIST:** Concrete things to verify
- **FINDINGS:** (To be filled in during research)
- **VERDICT:** (Redundant / Essential / Unknown)

---

## TASK INDEX

| # | Task File | Status | Focus Area | Est. Time |
|---|-----------|--------|------------|-----------|
| 1 | `01_ROOT_FILES.md` | TODO | Root-level files (orchestrator, chamber, cell) | 1-2h |
| 2 | `02_SUBSTRATE.md` | TODO | substrate/ folder (~20 files) | 2-3h |
| 3 | `03_PROTOCOLS.md` | TODO | protocols/ folder (interfaces) | 2-3h |
| 4 | `04_ADAPTERS.md` | TODO | adapters/ folder | 1-2h |
| 5 | `05_CLI.md` | TODO | cli/ folder | 2h |
| 6 | `06_QUARTERS.md` | TODO | genesis/, dharma/, karma/, moksha/ | 3-4h |
| 7 | `07_KERNEL.md` | TODO | kernel/ folder | 1-2h |
| 8 | `08_LILA.md` | TODO | lila/ folder | 1h |
| 9 | `09_RESEARCH.md` | TODO | research/ folder | 2h |
| 10 | `10_SOUND_NET_VENU.md` | TODO | sound/, net/, venu/ | 2h |
| 11 | `11_REDUNDANCY_AUDIT.md` | TODO | Cross-folder redundancy check | 3-4h |
| 12 | `12_INTEGRATION_MAP.md` | TODO | How everything connects (FINAL) | 4-6h |

**TOTAL ESTIMATED: 25-35 hours of focused research**

---

## HOW TO WORK ON TASKS

1. Pick a task file (start with 01)
2. Read the FILES TO READ section
3. Fill in FINDINGS as you discover things
4. Mark VERDICT for each file
5. Update Status in this README

**IMPORTANT:** Be honest. If you don't know, write "UNKNOWN - needs more investigation".

---

## KNOWN FACTS (VERIFIED)

From previous sessions:

- `orchestrator.py` - VenuOrchestrator with 19-bit DIW, LUT-based routing ✓
- `chamber.py` - SankirtanChamber with composition pattern ✓
- `cell.py` - MahaCellUnified with Header + Lifecycle ✓
- `protocols/_seed.py` - SSOT for all constants ✓
- `substrate/registry.py` - SiksastakamRegistry with 512 slots ✓

---

## OPEN QUESTIONS

1. What is in `kama/` folder? (Not a standard quarter)
2. What is `research/` vs main folders? (Experiments vs production?)
3. How do `dharma/janaka` and `karma/janaka` relate? (Same guardian in 2 places?)
4. What is `reactor/` for?
5. How does `venu/` relate to root `orchestrator.py`?

---

*"304 files. 1 truth. Find it."*
