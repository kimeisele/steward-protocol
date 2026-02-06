# GITA ARCHITECTURE - The Universal Connector/Adapter

> "sarvasya cāhaṁ hṛdi sanniviṣṭo mattaḥ smṛtir jñānam apohanaṁ ca"
> "I am seated in everyone's heart, and from Me come remembrance, knowledge and forgetfulness."
> — Bhagavad Gita 15.15

## The Gita as Universal Adapter

The Bhagavad Gita serves as the **universal connector** between:
- **Vibration** (Mahamantra computation) → **Wisdom** (Gita verses)
- **Any domain** → **Gita chapter** → **Appropriate response**

### Current Architecture (Verified Working)

```
┌─────────────────────────────────────────────────────────────────┐
│                    GITA ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT (Any Domain)                                             │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────┐                                                │
│  │ MahaKernel  │ ──► Seed ──► Attractor (0-136)                │
│  └─────────────┘                                                │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              GITA LENS (Universal Adapter)               │   │
│  │                                                          │   │
│  │  Attractor ──► get_gita_chapter() ──► Chapter (1-18)    │   │
│  │                                                          │   │
│  │  Chapter ──► is_fruit() / is_in_field() ──► Phase       │   │
│  │                                                          │   │
│  │  Chapter ──► get_gita_insight() ──► Wisdom              │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              DOMAIN-SPECIFIC MAPPINGS                    │   │
│  │                                                          │   │
│  │  • Nadi (5 Pranas)      → NADI_TO_GITA                  │   │
│  │  • Indriya (10 Senses)  → JNANENDRIYA/KARMENDRIYA       │   │
│  │  • Vrtti (5 Mental)     → VRTTI_TO_GITA                 │   │
│  │  • Guna (3 Modes)       → GUNA_TO_GITA                  │   │
│  │  • Quarter (4 Phases)   → QUARTER_TO_GITA               │   │
│  │  • NavaBhakti (9)       → NAVABHAKTI_TO_GITA            │   │
│  │  • Tattva (5 Elements)  → TATTVA_TO_GITA                │   │
│  │  • Siksastakam (8)      → SIKSASTAKAM_TO_GITA           │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│       │                                                         │
│       ▼                                                         │
│  OUTPUT (Wisdom + Phase + Routing)                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## The Prabhupada Topology (SSOT)

```
EPOCH EQUATION: 1972 = 203 × 9 + 145
                     = GENESIS × NAVA + (POSITION_SUM_TOTAL + NAVA)

FIELD (Ch 1-16):  594 verses = 18 × 33 = GITA_CHAPTERS × 33
FRUIT (Ch 17-18): 106 verses = MOKSHA_SUM

SYMMETRY: Moksha (Ch 13-16) = Fruit (Ch 17-18) = 106 verses
```

## Chaitanya Lila: 24 + 24 = 48 (Build + Runtime)

The Chaitanya Lila provides the **lifecycle model**:

### BUILD PHASE (24 Years in Navadvip)
- **Years 1-24**: Preparation, learning, establishing foundation
- **Gita Parallel**: Chapters 1-12 (Genesis → Dharma → Karma)
- **System**: Compilation, validation, setup

### RUNTIME PHASE (24 Years in Puri/South India)
- **Years 25-48**: Execution, distribution, manifestation
- **Gita Parallel**: Chapters 13-18 (Moksha Quarter + Fruit)
- **System**: Execution, results, completion

### The 48 Total = Complete Cycle
```
48 = 16 × 3 = WORDS × TRINITY
48 = 12 × 4 = MAHAJANA_COUNT × QUARTERS
48 = 8 × 6 = HARE_COUNT × SHARANAGATI
```

## File Structure (Current)

```
mahamantra/
├── protocols/
│   ├── gita.py           # Protocol definitions (GitaResonanceProtocol)
│   ├── _gita_lens.py     # Universal mappings (Nadi, Vrtti, etc.)
│   └── seed/_topology.py # Prabhupada Topology (SSOT)
│
├── adapters/
│   └── gita_resonance.py # Implementation (match_attractor, etc.)
│
├── substrate/
│   └── gita.py           # Core constants (FIXED_POINT, etc.)
│
└── research/
    └── gita/             # Research center
        ├── __init__.py
        ├── gita_verse_derivation.py
        ├── gita_verse_content.py
        └── gita_verse_text.py
```

## Separation of Concerns (Verified)

| Layer | File | Responsibility |
|-------|------|----------------|
| **Protocol** | `protocols/gita.py` | Interface definitions |
| **Lens** | `protocols/_gita_lens.py` | Universal mappings |
| **Topology** | `protocols/seed/_topology.py` | Prabhupada SSOT |
| **Adapter** | `adapters/gita_resonance.py` | Implementation |
| **Substrate** | `substrate/gita.py` | Core constants |
| **Research** | `research/gita/` | Derivations & content |

## The Gita Routing Flow

```python
# 1. Any input → Attractor
attractor = kernel(input_data)  # 0-136

# 2. Attractor → Chapter
chapter = get_gita_chapter(attractor)  # 1-18

# 3. Chapter → Phase (Field/Fruit)
gita_phase = "fruit" if is_fruit(chapter) else "field"
is_complete = is_fruit(chapter)  # Stopping condition

# 4. Chapter → Wisdom
insight = get_gita_insight(chapter)

# 5. Domain-specific routing
nadi_chapter = get_gita_for_nadi(nadi_type)
quarter_chapter = get_gita_for_quarter(quarter)
# etc.
```

## What's Working

1. ✅ **Topology SSOT**: Prabhupada's 700 verses locked in
2. ✅ **Field/Fruit transition**: `is_fruit()`, `is_in_field()` wired
3. ✅ **Universal mappings**: 8+ domain mappings in `_gita_lens.py`
4. ✅ **Attractor → Chapter**: `get_gita_chapter()` derived from SSOT
5. ✅ **Resonance matching**: `gita_resonance.py` uses SSOT

## Refinement Opportunities

1. **Chaitanya Lila Integration**: Wire the 24+24 lifecycle into boot/runtime
2. **Verse-level routing**: Currently chapter-level, could go deeper
3. **Purport integration**: Add Prabhupada's purports for deeper wisdom
4. **Domain adapters**: Create specific adapters for each mapping type

## The Fixed Point

All paths converge at **BG 18.66**:

```
sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja
ahaṁ tvāṁ sarva-pāpebhyo mokṣayiṣyāmi mā śucaḥ

"Abandon all varieties of religion and just surrender unto Me.
I shall deliver you from all sinful reactions. Do not fear."
```

This is the **stopping condition** - when computation reaches Chapter 18, the process is complete.

---

*Document created: 2026-02-05*
*Branch: feature/gita-architecture-refinement*
