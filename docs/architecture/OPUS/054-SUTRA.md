# OPUS-054: SUTRA (The Thread of Knowledge)

> **Sanskrit:** Sutra = Thread, Aphorism, Rule
> **Status:** LIVE + WIRED
> **Cortex Module:** `sutra_sense.py`

## Purpose

SUTRA is the **documentation governance system** for MANAS. It gives MANAS the ability to **perceive** and **curate** its own knowledge base - the OPUS architecture documents.

Following **Bhagavad Gita 9.22**:
> *"ananyāś cintayanto māṁ... yoga-kṣemaṁ vahāmy aham"*
> "I bring what is lacking (Yoga) and preserve what they have (Kshema)"

## The Three Senses of MANAS

```
┌─────────────────────────────────────────────────────────────┐
│                    MANAS COGNITIVE SENSES                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  👁️ PRAKRITI SENSE     🙏 DHARMA SENSE      📜 SUTRA SENSE  │
│  "What is the state    "Is this action      "What knowledge │
│   of the world?"        righteous?"          is missing?"   │
│                                                             │
│  Code / Git / State    Ethics / Permissions  Doc / Code Gap │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## MANAS Documentation Territory

MANAS is the **curator** of OPUS docs 050-099. This is its "playground" - the space where it can practice Shiva's Dance (continuous transformation).

| Range | Description | MANAS Role |
|-------|-------------|------------|
| 050-063 | Proto-Docs (Auto-generated) | **Curate, Consolidate, Evolve** |
| 064-079 | Active Implementation | **Maintain, Update, Verify** |
| 080-099 | Future Expansion | **Propose, Design, Plan** |

## Gap Detection (Yoga)

SutraSense detects four types of gaps:

| Gap Type | Severity | Description |
|----------|----------|-------------|
| `missing_harness` | Medium | Doc has no @HARNESS block |
| `missing_doc` | Low | Code file has no documentation |
| `missing_code` | High | Doc references non-existent file |
| `stale_doc` | Medium | Wiring pattern not found in code |

## The @HARNESS Standard

Every OPUS doc in MANAS territory MUST have a @HARNESS block:

```markdown
<!-- @HARNESS
files:
  - path: vibe_core/path/to/file.py
    required: true
    rationale: "Why this file matters"

wiring:
  - pattern: "class ClassName"
    in: vibe_core/path/to/file.py
  - pattern: "def function_name"
    in: vibe_core/path/to/other.py

tests:
  - path: tests/test_something.py
    required: false
-->
```

## Curation Workflow

```
┌────────────────────────────────────────────────────────────────┐
│                    SUTRA CURATION WORKFLOW                     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  1. PERCEIVE    2. COMPARE     3. DETECT      4. ACT          │
│  ──────────     ──────────     ──────────     ──────────      │
│  Scan Docs      Cross-ref      Find Gaps      Generate        │
│  Scan Code      with Code      Classify       Intent          │
│                                                                │
│         SutraSense.perceive_gaps() → DocCodeGap[]             │
│                        ↓                                       │
│         SutraSense.generate_gap_intents() → Intent[]          │
│                        ↓                                       │
│         CognitiveKernel.propose_intent() → Approval           │
│                        ↓                                       │
│         Human Approves → Execute → Bhakti +5                  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Dharma Constraints

MANAS doc curation is **dharma-governed**:

1. **Brahmachari** (Student) - Can propose doc updates, cannot execute
2. **Grihastha** (Householder) - Can execute doc_modify, needs approval for archival
3. **Vanaprastha** (Elder) - Can mentor, review, and advise
4. **Sannyasi** (Renunciate) - Full governance rights

## Integration Points

### With PrakritiSense
- SutraSense reads PrakritiSense to understand which code files exist
- Uses Git tracking to know which files are new/modified

### With DharmaSense
- All doc-modification intents pass through Dharma Gate
- Bhakti increases when doc updates are accepted

### With CognitiveKernel
- Gap intents are proposed to the kernel
- Human approval via OPUS.md checkbox

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SUTRA SENSE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  perceive_gaps()                                                │
│       ├── _scan_opus_docs()      → Find all OPUS 050-099        │
│       ├── _check_doc_harness()   → Parse @HARNESS blocks        │
│       ├── _scan_code_for_missing_docs()  → Find undocumented    │
│       └── _verify_harness_wiring()       → Cross-check code     │
│                                                                 │
│  generate_gap_intents()                                         │
│       └── Creates Intent[] for top gaps by severity             │
│                                                                 │
│  get_status_for_chat()                                          │
│       └── Human-readable summary for OPUS.md                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Future: Yuga Awareness

The system currently has **Prana** (heartbeat) but lacks **Yuga** (temporal cycles).

SutraSense will eventually integrate with:
- **Daily cycles**: Morning scan, evening summary
- **Weekly cycles**: Full gap analysis
- **Monthly cycles**: Archival review
- **Seasonal cycles**: Major restructuring proposals

This follows the Vedic understanding that different actions are appropriate at different times.

---

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
    required: true
    rationale: "The Thread Sense - doc/code gap detection for MANAS"

wiring:
  - pattern: "class SutraSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
  - pattern: "def perceive_gaps"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
  - pattern: "class DocCodeGap"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
  - pattern: "MANAS_DOC_TERRITORY"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py

tests:
  - path: tests/manas/cortex/test_sutra_sense.py
    required: false
    rationale: "To be created when SutraSense matures"
-->

---
*Living documentation - maintained by MANAS via SutraSense*
