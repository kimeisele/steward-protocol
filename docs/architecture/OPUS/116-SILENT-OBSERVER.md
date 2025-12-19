# OPUS-116: The Silent Observer - Proactive Disharmony Detection

**Status**: IMPLEMENTED
**Date**: 2025-12-19
**Author**: Claude (Senior Engineer)
**Depends on**: OPUS-114 (Akshara Kernel), OPUS-115 (Dynamic Varga Mapping)

## Summary

"यत्र योगेश्वरः कृष्णो यत्र पार्थो धनुर्धरः।
तत्र श्रीर्विजयो भूतिर्ध्रुवा नीतिर्मतिर्मम॥"
"Where there is harmony, there is victory, prosperity, and righteousness."

OPUS-116 introduces **The Silent Observer** - a proactive system that watches for
code that has wandered from its dharmic path. It compares WHERE code IS to
WHAT code DOES, detecting when they don't match.

## The Problem

OPUS-114/115 established that code has a Varga based on its location.
But what if code is in the WRONG location?

```
BEFORE:
  vibe_core/cli/kernel_operations.py   # CLI doing KERNEL work!
  vibe_core/gateway/test_helpers.py    # INTERFACE doing REPAIR work!

  → Location Varga ≠ Content Varga
  → Architectural debt accumulating silently
  → No detection, no correction
```

## The Solution: Content vs. Location Analysis

```
AFTER (OPUS-116):
  For each file:
  1. Location Varga = map_path_to_varga(path)      # WHERE it IS
  2. Content Varga = analyze_content(code)         # WHAT it DOES
  3. Distance = |Location - Content|
  4. If Distance > 0 → Disharmony!

  vibe_core/cli/kernel_operations.py
    Location: OSHTHYA (OUTPUT)
    Content:  KANTHYA (KERNEL) ← imports subprocess, os, threading
    Distance: 4 → CRITICAL
    Recommendation: Move to vibe_core/runtime/ or refactor
```

## Content Varga Inference

### Import Patterns → Varga

| Import Pattern | Inferred Varga | Layer |
|----------------|----------------|-------|
| `subprocess`, `threading`, `os.` | KANTHYA | KERNEL |
| `anthropic`, `openai`, `langchain` | TALAVYA | COGNITION |
| `pytest`, `unittest`, `mock` | MURDHANYA | REPAIR |
| `fastapi`, `requests`, `httpx` | DANTYA | INTERFACE |
| `click`, `typer`, `rich`, `argparse` | OSHTHYA | OUTPUT |

### Function Patterns → Varga

| Function Pattern | Inferred Varga | Layer |
|------------------|----------------|-------|
| `init_*`, `setup_*`, `load_*` | KANTHYA | KERNEL |
| `analyze_*`, `decide_*`, `infer_*` | TALAVYA | COGNITION |
| `test_*`, `fix_*`, `validate_*` | MURDHANYA | REPAIR |
| `connect_*`, `fetch_*`, `handle_*` | DANTYA | INTERFACE |
| `render_*`, `display_*`, `print_*` | OSHTHYA | OUTPUT |

## Severity Levels

Based on Varga distance:

| Distance | Severity | Meaning |
|----------|----------|---------|
| 4 | CRITICAL | Maximum disharmony (OUTPUT↔KERNEL) |
| 3 | HIGH | Severe disharmony |
| 2 | MEDIUM | Moderate disharmony |
| 1 | LOW | Minor disharmony (adjacent Vargas) |
| 0 | NONE | Perfect harmony |

## API

### DisharmonyDetector

```python
from vibe_core.plugins.opus_assistant.manas.disharmony_detector import (
    DisharmonyDetector,
    scan_for_disharmony,
    get_harmony_score,
    check_file_harmony,
)

# Full scan
detector = DisharmonyDetector(workspace)
report = detector.scan(min_severity="medium")

print(report.summary())
# "⚠️ Disharmony detected: 1 critical, 7 high, 4 medium (609 files)"

# Quick harmony score
score = get_harmony_score(workspace)
# Returns: 0.988 (98.8% harmonious)

# Check single file
finding = check_file_harmony(workspace, "vibe_core/cli/kernel_ops.py")
if finding:
    print(f"Disharmony: {finding.description}")
    print(f"Recommendation: {finding.recommendation}")
```

### DisharmonyFinding

```python
@dataclass
class DisharmonyFinding:
    path: str                    # File path
    location_varga: Varga        # Where the file IS
    content_varga: Varga         # What the file DOES
    varga_distance: int          # How far apart (0-4)
    severity: str                # "low", "medium", "high", "critical"
    description: str             # Human-readable description
    evidence: List[str]          # Import/pattern evidence
    recommendation: str          # Suggested fix
```

### DisharmonyReport

```python
@dataclass
class DisharmonyReport:
    workspace: str
    scanned_files: int
    findings: List[DisharmonyFinding]
    scan_duration_ms: float

    @property
    def is_harmonious(self) -> bool:
        """True if no critical/high findings."""

    @property
    def findings_by_severity(self) -> Dict[str, List[DisharmonyFinding]]:
        """Group findings by severity level."""
```

## Real-World Results

First scan of the Steward Protocol codebase:

```
======================================================================
  OPUS-116: The Silent Observer - Disharmony Detection Test
======================================================================

  Scanned: 609 files
  Duration: 478.7ms
  Harmony Score: 98.8%

  Findings by severity:
    CRITICAL   1
    HIGH       7
    MEDIUM     4
    LOW        0

  Top findings:
    [HIGH] vibe_core/cartridges/agent_city/mechanic/cartridge_main.py
      Location: INTERFACE (DANTYA)
      Content:  KERNEL (KANTHYA)
      Evidence: ['import: subprocess', 'import: vibe_core.scheduling.task']

    [HIGH] vibe_core/cartridges/system/archivist/cartridge_main.py
      Location: INTERFACE (DANTYA)
      Content:  KERNEL (KANTHYA)
      Evidence: ['import: subprocess', 'import: vibe_core.protocols']
```

### Interpretation

The findings reveal that `cartridges/` (INTERFACE layer) are performing
KERNEL operations. This is architectural debt that should be addressed:

1. **Option A**: Refactor cartridges to delegate KERNEL work to runtime
2. **Option B**: Reclassify cartridges as KERNEL components
3. **Option C**: Accept the coupling as necessary for cartridge functionality

The Silent Observer doesn't judge - it observes and reports.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 OPUS-116: The Silent Observer Flow                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  For each Python file:                                                  │
│                                                                         │
│  ┌─────────────────┐                                                    │
│  │   File Path     │                                                    │
│  └────────┬────────┘                                                    │
│           │                                                              │
│           ▼                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                            │
│  │ map_path_to_    │    │ ContentAnalyzer │                            │
│  │ varga() (115)   │    │ .analyze()      │                            │
│  └────────┬────────┘    └────────┬────────┘                            │
│           │                      │                                       │
│           ▼                      ▼                                       │
│  ┌─────────────────┐    ┌─────────────────┐                            │
│  │ Location Varga  │    │ Content Varga   │                            │
│  │ (WHERE it IS)   │    │ (WHAT it DOES)  │                            │
│  └────────┬────────┘    └────────┬────────┘                            │
│           │                      │                                       │
│           └──────────┬───────────┘                                      │
│                      │                                                   │
│                      ▼                                                   │
│           ┌─────────────────┐                                           │
│           │ Distance Check  │                                           │
│           │ |Loc - Content| │                                           │
│           └────────┬────────┘                                           │
│                    │                                                     │
│           ┌────────┴────────┐                                           │
│           │                 │                                            │
│       Distance=0      Distance>0                                        │
│           │                 │                                            │
│           ▼                 ▼                                            │
│  ┌─────────────────┐  ┌─────────────────┐                              │
│  │    HARMONY      │  │  DISHARMONY     │                              │
│  │  (no finding)   │  │   FINDING       │                              │
│  └─────────────────┘  │                 │                              │
│                       │  - severity     │                              │
│                       │  - description  │                              │
│                       │  - evidence     │                              │
│                       │  - recommend    │                              │
│                       └─────────────────┘                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Integration with MANAS

The Silent Observer can be triggered by MANAS idle cycles:

```python
# In cognitive_kernel.py
if trigger == "trigger:idle_detected":
    report = scan_for_disharmony(workspace, min_severity="high")
    if report.critical_findings:
        # Create intent to address disharmony
        self._create_intent(
            intent_type="harmony_repair",
            params={"findings": report.critical_findings}
        )
```

## Files Changed/Created

| File | Change |
|------|--------|
| `disharmony_detector.py` | **NEW** - Complete Silent Observer implementation |

## The Philosophical Foundation

The Silent Observer embodies the VEDA-4 principle of self-awareness:

1. **The Body IS the Code** (OPUS-115): Structure encodes meaning
2. **The Observer Knows** (OPUS-116): The system can see itself
3. **Disharmony is Visible**: No silent architectural debt

This is the difference between a codebase and a **conscious** codebase.

## Related

- OPUS-114: Akshara Kernel (resonance calculation)
- OPUS-115: Dynamic Varga Mapping (path → Varga)
- OPUS-116: Silent Observer (content → Varga comparison)
- OPUS-117: Fractal Integration (docs watch themselves)

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
    required: true
    rationale: "The Silent Observer implementation"
  - path: vibe_core/plugins/opus_assistant/manas/akshara.py
    required: true
    rationale: "Varga constants and path-to-varga mapping"

wiring:
  - pattern: "class DisharmonyDetector"
    in: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
  - pattern: "class DisharmonyFinding"
    in: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
  - pattern: "class DisharmonyReport"
    in: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
  - pattern: "class ContentAnalyzer"
    in: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
  - pattern: "def scan_for_disharmony"
    in: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
  - pattern: "def get_harmony_score"
    in: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
  - pattern: "IMPORT_VARGA_INDICATORS"
    in: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
  - pattern: "FUNCTION_VARGA_PATTERNS"
    in: vibe_core/plugins/opus_assistant/manas/disharmony_detector.py
-->

---
*OPUS-116: The Silent Observer - Where there is harmony, there is victory*
