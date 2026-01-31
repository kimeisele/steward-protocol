# TASK 12: INTEGRATION MAP

**Status:** TODO
**Estimated Time:** 4-6 hours (after completing tasks 1-11)
**Priority:** CRITICAL (final synthesis)

---

## QUESTION

How does everything connect?
This is the FINAL task - create the architecture map.

---

## PREREQUISITES

Complete tasks 1-11 first. This task synthesizes all findings.

---

## LAYERS

After audit, categorize every folder into layers:

```
LAYER 0: SSOT (Truth)
├── protocols/_seed.py

LAYER 1: SUBSTRATE (Foundation)
├── substrate/

LAYER 2: PROTOCOLS (Interfaces)
├── protocols/

LAYER 3: KERNEL (Core Logic)
├── kernel/
├── orchestrator.py
├── chamber.py
├── cell.py

LAYER 4: ADAPTERS (Bridges)
├── adapters/

LAYER 5: QUARTERS (Guardians)
├── genesis/
├── dharma/
├── karma/
├── moksha/

LAYER 6: FEATURES (Subsystems)
├── cli/
├── sound/
├── net/
├── lila/

LAYER 7: EXPERIMENTAL
├── research/
```

---

## DATA FLOW

Draw how data flows through the system:

```
User Input
    ↓
CLI (cli/entry.py)
    ↓
Bridge/Auto (cli/bridge.py or cli/auto.py)
    ↓
Compression (adapters/compression.py)
    ↓
Orchestrator (orchestrator.py)
    ↓
DIW (19-bit Divine Instruction Word)
    ↓
    ├── MURALI (4 bits) → Position (0-15)
    ├── VAMSI (9 bits) → Capability Slot (0-511)
    └── VENU (6 bits) → Variant (0-63)
    ↓
Registry (substrate/registry.py)
    ↓
Protocol Dispatch (substrate/protocol.py)
    ↓
Guardian Method
    ↓
Result
```

---

## COMPONENT RELATIONSHIPS

Draw connections:

```
                    ┌─────────────────────┐
                    │   protocols/_seed   │
                    │       (SSOT)        │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ↓                     ↓                     ↓
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   substrate/    │   │   protocols/    │   │    adapters/    │
│  (Data Structs) │   │  (Interfaces)   │   │   (Bridges)     │
└────────┬────────┘   └────────┬────────┘   └────────┬────────┘
         │                     │                     │
         └──────────┬──────────┴──────────┬──────────┘
                    ↓                     ↓
            ┌─────────────────┐   ┌─────────────────┐
            │     kernel/     │   │   orchestrator  │
            │  (Singularity)  │   │   chamber, cell │
            └────────┬────────┘   └────────┬────────┘
                     │                     │
                     └──────────┬──────────┘
                                ↓
                        ┌─────────────────┐
                        │    cli/entry    │
                        │  (User Input)   │
                        └─────────────────┘
```

---

## FILE COUNT BY LAYER

| Layer | Folder | File Count | Essential | Redundant | Unknown |
|-------|--------|------------|-----------|-----------|---------|
| 0 | protocols/_seed.py | 1 | 1 | 0 | 0 |
| 1 | substrate/ | ? | ? | ? | ? |
| 2 | protocols/ | ? | ? | ? | ? |
| 3 | kernel/ + root | ? | ? | ? | ? |
| 4 | adapters/ | ? | ? | ? | ? |
| 5 | quarters | ? | ? | ? | ? |
| 6 | cli/ + others | ? | ? | ? | ? |
| 7 | research/ | ? | ? | ? | ? |
| **TOTAL** | | **304** | | | |

---

## SSOT VERIFICATION

All constants should trace back to _seed.py:

```
WORDS = 16 (axiom)
    ↓
MURALI_HOLES = 4 (derived)
    ↓
VenuOrchestrator.MURALI_BITS = MURALI_HOLES
    ↓
(murali << 15) in DIW
```

Verify no file has hardcoded 16, 4, 9, 6, etc.

---

## FINAL ARCHITECTURE MAP

After completing all tasks, create the definitive map:

```
MAHAMANTRA ARCHITECTURE (304 files → N essential)

┌────────────────────────────────────────────────────────┐
│                        LAYER 0                          │
│                    protocols/_seed.py                   │
│                      (THE SSOT)                         │
│  WORDS=16, MALA=108, PARAMPARA=37, FLUTE_HOLES_SUM=19  │
└────────────────────────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────┐
│                        LAYER 1                          │
│                       substrate/                        │
│  registry.py, nadi.py, protocol.py, position.py, ...   │
└────────────────────────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────┐
│                        LAYER 2                          │
│                       protocols/                        │
│  _sankirtan.py, _lila.py, _pancha.py, sankalpa/, ...   │
└────────────────────────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────┐
│                        LAYER 3                          │
│               kernel/ + orchestrator.py                 │
│        VenuOrchestrator, SankirtanChamber, Cell        │
└────────────────────────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────┐
│                        LAYER 4                          │
│                       adapters/                         │
│   HolographicRouter, MahaCompression, RamaPhonetic     │
└────────────────────────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────┐
│                        LAYER 5                          │
│        genesis/ dharma/ karma/ moksha/ (Quarters)       │
│                   16 Guardian Folders                   │
└────────────────────────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────┐
│                        LAYER 6                          │
│                  cli/ sound/ net/ lila/                 │
│                     Feature Modules                     │
└────────────────────────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────┐
│                        LAYER 7                          │
│                       research/                         │
│                    Experimental Code                    │
└────────────────────────────────────────────────────────┘
```

---

## ACTION ITEMS

After completing map:

1. **Document essential files** (create ESSENTIAL.md)
2. **List deprecated files** (create DEPRECATED.md)
3. **Create migration plan** (for legacy code outside mahamantra/)
4. **Update PRIORITY.md** with new understanding

---

*Last updated: ____*
