# OPUS-172: Akshara Feature Comparison - Critical Analysis

> **Status**: ANALYSIS COMPLETE
> **Created**: 2025-12-21
> **Auditor**: Claude (Senior Architect Mode)
> **Result**: manas/akshara.py is NOT a duplicate - it's the CORE phonemic library

---

## Executive Summary

**Gemini's warning was CORRECT**: The 766-line difference between `manas/akshara.py` (1062 lines) and `vibe_core/state/unified_akshara.py` (296 lines) is NOT bloat.

These files serve **completely different purposes** and are **COMPLEMENTARY**, not duplicate.

---

## Dependency Chain (Critical Discovery)

```
vibe_core/state/unified_akshara.py (296 lines)
    │ USES
    └── triggers.SynapticMemory.consult_dharmic()
            │ IMPORTS FROM
            └── manas/akshara.py (1062 lines)
                    provides:
                    - calculate_dharmic_score()
                    - get_trigger_varga()
                    - get_action_varga()
                    - Varga enum
                    - VARGA_LAYERS mapping
```

**unified_akshara.py CANNOT WORK without manas/akshara.py!**

---

## Feature Matrix

### manas/akshara.py (OPUS-114) - The PHONEMIC CORE

| Feature | Lines | Description |
|---------|-------|-------------|
| Varga IntEnum | 10 | 5 articulation classes (Kanthya→Oshthya) |
| VARGA_NAMES, LAYERS, ELEMENTS | 30 | Sanskrit mappings to code layers |
| Akshara dataclass | 60 | Phoneme with devanagari, iast, varga, position |
| Varnamala class (Singleton) | 120 | 5×5 consonant matrix |
| PATH_VARGA_PATTERNS (OPUS-115) | 70 | Maps file paths to Vargas |
| OPUS_DOC_VARGA_RANGES (OPUS-117) | 50 | Maps OPUS doc numbers to Vargas |
| TRIGGER_VARGA_MAP | 40 | Classifies triggers by layer |
| ACTION_VARGA_MAP | 40 | Classifies actions by layer |
| calculate_resonance() | 15 | Core resonance calculation |
| calculate_dharmic_score() | 50 | With SIDDHI enhancement (OPUS-133) |
| AksharaNode, AksharaEdge | 80 | Graph data structures |
| AksharaGraph class | 130 | JSON-persistent visualization |
| Integration helpers | 50 | enhance_recommendations_with_resonance() |
| Debug helpers | 50 | print_varnamala_matrix(), print_resonance_matrix() |
| **TOTAL** | **~1050** | **Essential phonemic computation** |

### vibe_core/state/unified_akshara.py (OPUS-154) - The ROUTING WRAPPER

| Feature | Lines | Description |
|---------|-------|-------------|
| PranaRecommendation dataclass | 20 | Routing result with PRANA factor |
| UnifiedAkshara class | 180 | Thin wrapper adding exploration |
| consult() | 60 | Gets dharmic + adds PRANA |
| route() | 15 | Simple action selection |
| get_exploration_report() | 40 | Crystallization risk analysis |
| Singleton helpers | 30 | get_akshara(), consult_akshara() |
| **TOTAL** | **~296** | **PRANA exploration layer** |

---

## Who Uses manas/akshara.py?

```
grep -rn "from.*akshara import" vibe_core/

1. triggers.py:638        → calculate_dharmic_score, get_trigger_varga, get_action_varga, Varga
2. triggers.py:717        → calculate_dharmic_score
3. shruta_sense.py:308    → Varga, map_path_to_varga
4. viveka_action.py:419   → Varga, get_trigger_varga, get_action_varga
5. viveka_action.py:493   → Varga, VARGA_LAYERS
6. disharmony_detector.py:39 → Full phonemic import
7. code_scanner.py:532    → Path-to-Varga mapping
```

**7 files directly depend on manas/akshara.py for phonemic calculations!**

---

## The True Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTEM LEVEL                                  │
│                    vibe_core/state/                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  unified_akshara.py (OPUS-154)                                 │
│  └── PRANA Layer: Adds exploration to prevent crystallization  │
│      └── Uses triggers.SynapticMemory                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ DEPENDS ON
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MANAS PLUGIN LEVEL                           │
│                    opus_assistant/manas/                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  akshara.py (OPUS-114) - THE PHONEMIC FOUNDATION               │
│  ├── Varga (5 articulation classes)                            │
│  ├── Akshara (25 consonants)                                   │
│  ├── Varnamala (5×5 matrix)                                    │
│  ├── Path-to-Varga mapping (OPUS-115)                          │
│  ├── OPUS doc mapping (OPUS-117)                               │
│  ├── Trigger/Action classification                              │
│  ├── Resonance calculation                                      │
│  ├── Dharmic score with SIDDHI (OPUS-133)                      │
│  └── Graph visualization                                        │
│                                                                 │
│  triggers.py - SynapticMemory                                   │
│  └── Uses akshara.py for dharmic calculations                  │
│                                                                 │
│  disharmony_detector.py                                         │
│  └── Uses akshara.py for layer classification                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Conclusion: NO Deletion, But Potential Refactoring

### What We Should NOT Do:
- ❌ Delete manas/akshara.py (breaks 7+ files)
- ❌ "Big Bang" refactoring (Gemini's warning)
- ❌ Assume unified_akshara.py is a replacement

### What We COULD Do (Future):
- Consider extracting core phonemic types to `vibe_core/phonemes/` (optional)
- But this is cosmetic - the current structure works

### What We SHOULD Focus On (Phase 1):
- The REAL duplication is **_load_synapses()** (4 places!)
- The REAL problem is **schema inconsistency** (v1 vs v2)
- Create **SynapseStore** with unified v3 schema
- This fixes the actual tech debt without breaking anything

---

## OPUS-171 Revision

Based on this analysis, Phase 3 "Remove manas/akshara.py" should be:

**OLD (WRONG):**
| 3.1 | Remove manas/akshara.py (use unified_akshara) | TODO |

**NEW (CORRECT):**
| 3.1 | KEEP manas/akshara.py - it's the phonemic core | N/A |

The focus remains on:
1. Create SynapseStore (consolidate 4x _load_synapses)
2. Unified v3 schema
3. Migration helpers for v1/v2

---

**आत्मनो मोक्षार्थं जगद्धिताय च**
*"For one's own liberation and for the welfare of the world"*
