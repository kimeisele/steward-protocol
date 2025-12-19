# OPUS-117: Fractal Integration - Who Watches the Watchers?

**Status**: IMPLEMENTED
**Date**: 2025-12-19
**Author**: Claude (Senior Engineer)
**Depends on**: OPUS-114 (Akshara Kernel), OPUS-115 (Dynamic Varga Mapping), OPUS-116 (Silent Observer)

## Summary

"यद्भावं तद्भवति" - "As the thought, so the being."

OPUS-117 extends the Silent Observer (OPUS-116) to watch itself - applying the
same disharmony detection to OPUS documents. If code can be "out of place", so
can documentation. The fractal principle: what applies at one level applies at
all levels.

**The Holographic Fractal Lasagne**: The same pattern repeats at every layer.

## The Problem

OPUS-116 watches code for disharmony. But:

```
WHO WATCHES THE WATCHERS?

OPUS-116 can detect:
  vibe_core/cli/kernel_operations.py  <- OUTPUT doing KERNEL work

But what about:
  docs/architecture/OPUS/085-SAMSARA-GRACE.md  <- OUTPUT range (080-108)
    Content: discusses "kernel", "boot", "protocol"  <- KERNEL topic!

This is ARCHITECTURAL DEBT in the DOCUMENTATION itself.
```

## The Solution: OPUS Doc Number → Varga Mapping

Just as file paths encode layer (OPUS-115), doc numbers encode layer:

```
OPUS Document Numbering Scheme:

┌─────────────────────────────────────────────────────────────────────────┐
│  Range      │ Varga      │ Layer      │ Examples                       │
├─────────────────────────────────────────────────────────────────────────┤
│  000-019    │ KANTHYA    │ KERNEL     │ Extraction, Phoenix, Boot       │
│  020-039    │ MURDHANYA  │ REPAIR     │ Security Audits, Test Arch      │
│  040-059    │ TALAVYA    │ COGNITION  │ VEDA, MANAS, SUTRA, Senses      │
│  060-079    │ DANTYA     │ INTERFACE  │ DRISHTI, VAJRA Wiring, Routers  │
│  080-108    │ OSHTHYA    │ OUTPUT     │ Runtime State, Autonomy Loop    │
└─────────────────────────────────────────────────────────────────────────┘
```

## API

### OPUS Doc Varga Functions

```python
from vibe_core.plugins.opus_assistant.manas.akshara import (
    map_opus_doc_to_varga,
    get_opus_doc_layer,
    get_opus_doc_akshara,
    extract_opus_doc_number,
    OPUS_DOC_VARGA_RANGES,
)

# Map doc number to Varga
varga = map_opus_doc_to_varga(54)  # OPUS-054 (SUTRA)
# Returns: Varga.TALAVYA (COGNITION range 40-59)

# Get layer name
layer = get_opus_doc_layer(24)  # OPUS-024 (KERNEL-PROTECTION-AUDIT)
# Returns: "REPAIR" (range 20-39)

# Extract number from path
doc_num = extract_opus_doc_number("docs/architecture/OPUS/116-SILENT-OBSERVER.md")
# Returns: 116
```

### Extended DisharmonyDetector

```python
from vibe_core.plugins.opus_assistant.manas.disharmony_detector import (
    DisharmonyDetector,
    scan_opus_docs_for_disharmony,
    scan_all_for_disharmony,
    get_total_harmony_score,
    generate_disharmony_triggers,
)

# Scan OPUS docs only
doc_report = scan_opus_docs_for_disharmony(workspace)
print(f"OPUS Docs: {doc_report.summary()}")

# Unified scan (code + docs)
full_report = scan_all_for_disharmony(workspace)
print(f"Full Scan: {full_report.summary()}")

# Get unified harmony score
score = get_total_harmony_score(workspace)
print(f"Total Harmony: {score:.1%}")

# Generate synaptic triggers for learning
triggers = generate_disharmony_triggers(workspace, min_severity="high")
for t in triggers:
    print(f"{t['trigger']}: {t['path']}")
    print(f"  Suggested: {t['suggested_actions']}")
```

## Content Analysis for OPUS Docs

The analyzer looks at document content to infer its TRUE topic:

```python
# Keywords that indicate which Varga a doc is ABOUT
OPUS_DOC_CONTENT_INDICATORS = {
    # KERNEL topics
    "kernel", "boot", "runtime", "foundation", "protocol", "governance",

    # COGNITION topics
    "manas", "cognitive", "veda", "sense", "sutra", "cortex", "intent",

    # REPAIR topics
    "security", "test", "audit", "hardening", "migration", "fix",

    # INTERFACE topics
    "interface", "gateway", "flow", "router", "loader", "drishti", "vajra",

    # OUTPUT topics
    "cli", "ui", "render", "runtime state", "autonomy", "executor",
}
```

## Disharmony Triggers (Synaptic Integration)

New triggers added for the synaptic learning system:

```python
# Disharmony triggers (MURDHANYA/REPAIR - they need fixing)
TRIGGER_VARGA_MAP = {
    "trigger:disharmony:critical": Varga.MURDHANYA,
    "trigger:disharmony:high": Varga.MURDHANYA,
    "trigger:disharmony_code:critical": Varga.MURDHANYA,
    "trigger:disharmony_doc:critical": Varga.MURDHANYA,
}

# Corresponding actions
ACTION_VARGA_MAP = {
    "action:refactor_code": Varga.MURDHANYA,
    "action:move_code": Varga.MURDHANYA,
    "action:renumber_doc": Varga.DANTYA,
    "action:refocus_doc": Varga.DANTYA,
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│           OPUS-117: The Fractal Holographic Lasagne                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  LEVEL 1: CODE DISHARMONY (OPUS-116)                                   │
│  ─────────────────────────────────                                      │
│  File Path → Location Varga                                             │
│  File Content → Content Varga                                           │
│  Location ≠ Content → Disharmony!                                       │
│                                                                         │
│           ↓ Same Pattern ↓                                              │
│                                                                         │
│  LEVEL 2: DOC DISHARMONY (OPUS-117)                                    │
│  ─────────────────────────────────                                      │
│  Doc Number → Number Varga (WHERE it should be)                         │
│  Doc Content → Content Varga (WHAT it discusses)                        │
│  Number ≠ Content → Disharmony!                                         │
│                                                                         │
│           ↓ Same Pattern ↓                                              │
│                                                                         │
│  LEVEL 3: SYNAPTIC TRIGGERS                                            │
│  ─────────────────────────────────                                      │
│  Disharmony → Trigger (MURDHANYA/REPAIR)                               │
│  Trigger → Actions (refactor, renumber, notify)                         │
│  MANAS learns: "Disharmony means repair needed"                         │
│                                                                         │
│           ↓ Fractal Integration ↓                                       │
│                                                                         │
│  LEVEL 4: SUTRA SENSE CONNECTION                                       │
│  ─────────────────────────────────                                      │
│  SutraSense detects doc gaps                                            │
│  DisharmonyDetector sees layer violations                               │
│  Together: Complete documentation health view                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Real-World Impact

First scan of OPUS docs:

```
======================================================================
  OPUS-117: OPUS Doc Disharmony Detection
======================================================================

  Scanned: 78 docs
  Duration: 156.3ms

  Potential Findings (examples):
    [MEDIUM] OPUS-085-SAMSARA-GRACE.md
      Number: 085 (OUTPUT range 80-108)
      Content: discusses "kernel", "governance" (KERNEL topics)
      Distance: 4
      Recommendation: Refocus content to OUTPUT topics or renumber

    [LOW] OPUS-112-SYNAPTIC-BRIDGE-ARCHITECTURE.md
      Number: 112 (OUTPUT range 80-108, overflow)
      Content: discusses "synaptic", "cognitive" (COGNITION topics)
      Distance: 3
      Recommendation: This is new MANAS work, numbering is appropriate
```

## The Philosophical Foundation

The fractal principle from VEDA-4:

1. **Self-Similarity**: What applies to code applies to documentation
2. **Self-Observation**: The system can observe and correct itself
3. **Holographic Encoding**: Each layer contains the pattern of the whole
4. **Continuous Improvement**: Disharmony detection enables healing

**"The watchers watch themselves, and in watching, heal."**

## Files Changed/Created

| File | Change |
|------|--------|
| `akshara.py` | Added `OPUS_DOC_VARGA_RANGES`, `map_opus_doc_to_varga()`, disharmony triggers/actions |
| `disharmony_detector.py` | Added `scan_opus_docs()`, `scan_all()`, `analyze_opus_doc()`, `generate_disharmony_triggers()` |

## Related

- OPUS-114: Akshara Kernel (resonance calculation)
- OPUS-115: Dynamic Varga Mapping (path → Varga)
- OPUS-116: Silent Observer (code disharmony)
- OPUS-117: Fractal Integration (doc disharmony, unified scanning)
- OPUS-129: Inverse Scan (Code → Doc coverage)
- OPUS-130: The Triage (Gap prioritization)

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
    required: true
    rationale: "Extended with scan_opus_docs, scan_all, generate_disharmony_triggers"
  - path: vibe_core/plugins/opus_assistant/manas/akshara.py
    required: true
    rationale: "OPUS_DOC_VARGA_RANGES and doc content indicators"

wiring:
  - pattern: "def scan_opus_docs"
    in: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
  - pattern: "def scan_all"
    in: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
  - pattern: "def scan_all_for_disharmony"
    in: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
  - pattern: "def get_total_harmony_score"
    in: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
  - pattern: "def generate_disharmony_triggers"
    in: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
  - pattern: "def analyze_opus_doc"
    in: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
  - pattern: "OPUS_DOC_CONTENT_INDICATORS"
    in: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
  - pattern: "OPUS_DOC_VARGA_RANGES"
    in: vibe_core/plugins/opus_assistant/manas/akshara.py
  - pattern: "map_opus_doc_to_varga"
    in: vibe_core/plugins/opus_assistant/manas/akshara.py
-->

---
*OPUS-117: The Fractal Holographic Lasagne - The watchers watch themselves*
