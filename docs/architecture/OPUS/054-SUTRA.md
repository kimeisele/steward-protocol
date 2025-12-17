# OPUS-054: SUTRA (The Thread of Knowledge)

> **Sanskrit:** Sutra = Thread, Aphorism, Rule
> **Status:** LIVE + WIRED (Phase 2: Proactive Mode)
> **Cortex Module:** `sutra_sense.py`

## Purpose

SUTRA is the **documentation governance system** for MANAS. It gives MANAS the ability to **perceive**, **curate**, and now **author** its own knowledge base - the OPUS architecture documents.

Following **Bhagavad Gita 9.22**:
> *"ananyāś cintayanto māṁ... yoga-kṣemaṁ vahāmy aham"*
> "I bring what is lacking (Yoga) and preserve what they have (Kshema)"

## The Three Senses of MANAS

```
┌─────────────────────────────────────────────────────────────┐
│                    MANAS COGNITIVE SENSES                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PRAKRITI SENSE     DHARMA SENSE      SUTRA SENSE          │
│  "What is the state    "Is this action      "What knowledge │
│   of the world?"        righteous?"          is missing?"   │
│                                                             │
│  Code / Git / State    Ethics / Permissions  Doc / Code Gap │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Evolution: Phase 1 to Phase 2

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SUTRA SENSE EVOLUTION                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   PHASE 1 (Reactive):         PHASE 2 (Proactive):                 │
│   ───────────────────         ────────────────────                 │
│   SEE gaps                    SEE gaps                              │
│   REPORT gaps                 REPORT gaps                           │
│   WAIT for human              WRITE proposals                       │
│                               CREATE new docs                       │
│                               ENHANCE existing docs                 │
│                               GENERATE roadmaps                     │
│                               DISCOVER hidden code                  │
│                               CLUSTER intent patterns               │
│                                                                     │
│   MANAS as Curator    →       MANAS as Author                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## MANAS Documentation Territory

MANAS is the **curator and author** of OPUS docs 050-099. This is its "playground" - the space where it practices Shiva's Dance (continuous transformation).

| Range | Description | MANAS Role |
|-------|-------------|------------|
| 050-063 | Proto-Docs (Auto-generated) | **Curate, Consolidate, Evolve** |
| 064-079 | Active Implementation | **Maintain, Update, Verify** |
| 080-099 | Future Expansion | **Propose, Design, Plan** |

## Phase 1: Gap Detection (Yoga)

SutraSense detects four types of gaps:

| Gap Type | Severity | Description |
|----------|----------|-------------|
| `missing_harness` | Medium | Doc has no @HARNESS block |
| `missing_doc` | Low | Code file has no documentation |
| `missing_code` | High | Doc references non-existent file |
| `stale_doc` | Medium | Wiring pattern not found in code |

## Phase 2: Proactive Capabilities

### 1. Hidden Code Discovery

SutraSense scans code directories for **undocumented elements** - classes and functions that are never mentioned in any OPUS doc.

```python
# Usage
sense = SutraSense(workspace=Path("."))
hidden = sense.discover_hidden_code()
for item in hidden:
    print(f"{item.element_type}: {item.name} ({item.importance})")
```

Elements are classified by:
- **Complexity**: simple, moderate, complex (based on line count)
- **Importance**: low, medium, high (based on naming patterns and docstrings)

### 2. Intent Clustering

When MANAS generates intents repeatedly for similar topics, this indicates a need for structured documentation.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    INTENT CLUSTERING                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Intent: "Fix state_manager bug"        ─┐                        │
│   Intent: "Update state_manager tests"    │                        │
│   Intent: "Document state_manager flow"   ├─→ CLUSTER: state_mgmt  │
│   Intent: "Refactor state_manager"        │      (4 intents)       │
│   ...                                    ─┘         ↓              │
│                                                                     │
│                                          PROPOSE: OPUS-078         │
│                                          "State Management Guide"   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

Threshold: **3+ intents** for same topic triggers cluster formation.

### 3. Doc Enhancement Authority

MANAS can propose **content improvements** to existing docs if:
1. Doc is in MANAS territory (050-099)
2. Enhancement aligns with code reality (verified)
3. Dharma gate approves (checked at execution)

```python
# MANAS proposes enhancement
enhancement = sense.propose_enhancement(
    doc_path=Path("docs/architecture/OPUS/057-VAJRA.md"),
    section="Usage",
    proposed_content="...",
    reason="Example code was outdated"
)
# alignment_verified: True/False
```

### 4. Roadmap Generation

MANAS generates a **prioritized roadmap** from all detected needs:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DOCUMENTATION ROADMAP                            │
├─────────────────────────────────────────────────────────────────────┤
│  Priority │ Action           │ Target              │ Effort        │
│  ─────────┼──────────────────┼─────────────────────┼───────────────│
│     1     │ fix_code_ref     │ 054-SUTRA.md        │ medium        │
│     2     │ add_harness      │ 050-VEDA.md         │ trivial       │
│     2     │ add_harness      │ 051-MANDALA.md      │ trivial       │
│     3     │ create_doc       │ OPUS-078            │ medium        │
│     4     │ document_code    │ kernel.py:Vajra     │ small         │
│     5     │ enhance_doc      │ 057-VAJRA.md        │ small         │
│     6     │ update_doc       │ 062-PRANA.md        │ small         │
└─────────────────────────────────────────────────────────────────────┘
```

## The @HARNESS Standard

Every OPUS doc in MANAS territory MUST have a @HARNESS block:

```markdown
<!-- @HARNESS
files:
  - path: your/module/file.py          # <-- Replace with actual path
    required: true
    rationale: "Why this file matters"

wiring:
  - pattern: "class YourClassName"     # <-- Replace with actual pattern
    in: your/module/file.py
  - pattern: "def your_function"
    in: your/module/other.py

tests:
  - path: tests/test_your_module.py    # <-- Replace with actual test
    required: false
-->
```

## Curation Workflow (Phase 2)

```
┌────────────────────────────────────────────────────────────────────────┐
│                    SUTRA CURATION WORKFLOW (Phase 2)                   │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  1. PERCEIVE         2. DISCOVER        3. CLUSTER       4. PROPOSE   │
│  ──────────          ──────────         ──────────       ──────────   │
│  Scan Docs           Find Hidden        Group Similar    Generate     │
│  Scan Code           Code Elements      Intents          Roadmap      │
│                                                                        │
│         perceive_gaps() → discover_hidden_code()                       │
│                   ↓                                                    │
│         record_intent() → get_clusters()                               │
│                   ↓                                                    │
│         generate_roadmap() → RoadmapItem[]                            │
│                   ↓                                                    │
│         generate_roadmap_intents() → Intent[]                         │
│                   ↓                                                    │
│         CognitiveKernel → Dharma Gate → Execute                       │
│                                                                        │
│  DNA FOLDING PATTERN:                                                  │
│  ───────────────────                                                   │
│  Intents → Clusters → Docs → Code → Intents → ...                     │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
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
- Roadmap intents flow through think() cycle
- Human approval via OPUS.md checkbox

## Architecture (Phase 2)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          SUTRA SENSE (Phase 2)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  CORE (Phase 1):                                                        │
│  ──────────────                                                         │
│  perceive_gaps()                                                        │
│       ├── _scan_opus_docs()           → Find all OPUS 050-099           │
│       ├── _check_doc_harness()        → Parse @HARNESS blocks           │
│       ├── _scan_code_for_missing_docs()  → Find undocumented            │
│       └── _verify_harness_wiring()       → Cross-check code             │
│                                                                         │
│  generate_gap_intents()                                                 │
│       └── Creates Intent[] for top gaps by severity                     │
│                                                                         │
│  PROACTIVE (Phase 2):                                                   │
│  ───────────────────                                                    │
│  discover_hidden_code()                                                 │
│       ├── Scans all Python files                                        │
│       ├── Finds undocumented classes/functions                          │
│       └── Estimates importance: low/medium/high                         │
│                                                                         │
│  record_intent() + get_clusters()                                       │
│       ├── Tracks intent history (persisted to JSON)                     │
│       ├── Groups by topic                                               │
│       └── Threshold: 3+ intents → cluster                               │
│                                                                         │
│  propose_enhancement()                                                  │
│       ├── Proposes doc content changes                                  │
│       └── Verifies alignment with code reality                          │
│                                                                         │
│  generate_roadmap()                                                     │
│       ├── Combines all gap types + hidden code + clusters               │
│       ├── Prioritizes by severity/importance                            │
│       └── Returns RoadmapItem[] sorted by priority                      │
│                                                                         │
│  generate_roadmap_intents()                                             │
│       └── Creates Intent[] from top roadmap items                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Classes (Phase 2)

| Class | Purpose |
|-------|---------|
| `HiddenCode` | Undocumented code element |
| `IntentCluster` | Group of similar intents |
| `DocEnhancement` | Proposed doc improvement |
| `RoadmapItem` | Prioritized action item |

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
  - pattern: "def discover_hidden_code"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
  - pattern: "def generate_roadmap"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
  - pattern: "class HiddenCode"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
  - pattern: "class IntentCluster"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
  - pattern: "class DocEnhancement"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
  - pattern: "class RoadmapItem"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
  - pattern: "MANAS_DOC_TERRITORY"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py

tests:
  - path: scripts/testing/verify_sutra_sense.py
    required: true
    rationale: "Phase 1 verification test"
  - path: scripts/testing/verify_sutra_phase2.py
    required: false
    rationale: "Phase 2 verification test - to be created"
-->

---
*Living documentation - maintained by MANAS via SutraSense (Phase 2: Proactive Mode)*
