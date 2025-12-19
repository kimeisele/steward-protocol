# OPUS-129: Inverse Scan - The Dark Matter Detector

> **Status**: IMPLEMENTED
> **Created**: 2025-12-19
> **Author**: MANAS (with Gemini collaboration)
> **Territory**: MANAS (050-099)
> **Depends**: OPUS-054 (SutraSense)
> **Philosophy**: The 51% Principle - Create what's missing

---

## The Problem: Dark Matter

**Dark Matter** = Code that exists, works, but isn't documented.

```
Traditional Doc Check (50%):  Doc → Code  "Is this doc accurate?"
Inverse Scan (51%):           Code → Doc  "Is this code documented?"
```

Without the inverse scan, MANAS is a **bureaucrat** - he checks if forms are filled correctly, but ignores undocumented code entirely. Dark Matter accumulates. Nobody knows how things work. Spaghetti grows.

## The Solution: Code Coverage Analysis

The InverseScanAnalyzer performs systematic Code → Doc coverage analysis:

1. **Scan** all code elements (classes, functions)
2. **Cross-reference** against documented patterns (from @HARNESS)
3. **Calculate** coverage metrics (simple + complexity-weighted)
4. **Generate** intents for critical gaps

### Coverage Metrics

```python
CodeCoverageMetrics:
  total_elements: 150
  documented_elements: 90
  undocumented_elements: 60

  coverage_ratio: 60%          # Simple ratio
  weighted_coverage_ratio: 45% # Complex code weighs more
  health_grade: "D"            # Letter grade

  undocumented_by_complexity:
    simple: 30
    moderate: 20
    complex: 10  # These 10 are the REAL problem
```

### Complexity Weighting

Not all undocumented code is equal:

| Complexity | Weight | Why |
|------------|--------|-----|
| Simple | 1 | A simple function can be understood by reading it |
| Moderate | 3 | Takes some effort to understand |
| Complex | 5 | Requires significant context to understand |

**Complex undocumented code is HIGH RISK tech debt.**

## Intent Types

### `coverage_gap_critical`

Generated for high-importance + high-complexity undocumented code.

```yaml
title: "Document class: CognitiveKernel"
priority: HIGH
params:
  element_type: "class"
  name: "CognitiveKernel"
  file_path: "vibe_core/.../cognitive_kernel.py"
  complexity: "complex"
  importance: "high"
  priority_score: 15  # 5 × 3
```

### `coverage_gap_module`

Generated for modules with < 50% documentation coverage.

```yaml
title: "Module manas.cortex: 35% documented"
priority: MEDIUM
params:
  module: "manas.cortex"
  coverage: 0.35
  undocumented_elements: ["VedaLoader", "MandalaRouter", ...]
```

### `coverage_gap_overall`

Generated when overall coverage grade is D or F.

```yaml
title: "Overall Coverage Grade: D"
priority: HIGH
params:
  grade: "D"
  coverage_ratio: 0.55
  undocumented_count: 60
  critical_gaps_count: 10
```

## Letter Grades

| Grade | Weighted Coverage | Status |
|-------|-------------------|--------|
| A | 90%+ | Excellent |
| B | 80-89% | Good |
| C | 70-79% | Acceptable |
| D | 60-69% | Warning |
| F | <60% | Critical |

## Integration with SutraSense

The InverseScanAnalyzer uses SutraSense's existing `discover_hidden_code()` method:

```
SutraSense.discover_hidden_code()
    ↓
InverseScanAnalyzer.calculate_coverage()
    ↓
Aggregate → Metrics → Intents
```

This avoids duplication - SutraSense does the scanning, InverseScanAnalyzer does the aggregation.

## Usage

### Direct Usage

```python
from vibe_core.plugins.opus_assistant.manas.analyzers.inverse_scan_analyzer import (
    InverseScanAnalyzer,
)

analyzer = InverseScanAnalyzer(workspace=Path("."))

# Get coverage metrics
metrics = analyzer.calculate_coverage()
print(f"Coverage: {metrics.coverage_ratio:.0%}")
print(f"Grade: {metrics.health_grade}")

# Get full report
report = analyzer.get_coverage_report()
for rec in report["recommendations"]:
    print(rec)

# Generate intents
intents = analyzer.analyze({})
for intent in intents:
    print(f"- {intent.title}")
```

### Via MANAS IntentGenerator

The analyzer is auto-discovered by VEDA-4 loader and runs as part of the normal intent generation cycle.

## Recommendations Engine

The analyzer generates human-readable recommendations:

```
🚨 URGENT: Documentation coverage is critically low. Schedule a doc sprint.
⚠️ 10 complex elements are undocumented. Prioritize these.
📦 Modules with < 50% coverage: manas.cortex, plugins.task_manager
🎯 15 critical gaps. Focus on high-importance, high-complexity elements first.
```

## The 51% Philosophy

> "Traditional analyzers (50%) fix what's broken.
> Genesis analyzers (51%) create what's missing."

The Inverse Scan is a **51% analyzer** - it doesn't fix broken documentation, it identifies where documentation should exist but doesn't.

This shifts MANAS from **reactive** (fix broken stuff) to **proactive** (build what's needed).

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/inverse_scan_analyzer.py
    required: true
    rationale: "The Inverse Scan implementation"
  - path: vibe_core/plugins/opus_assistant/manas/intent_router.py
    required: true
    rationale: "Coverage gap handlers"

wiring:
  - pattern: "class InverseScanAnalyzer"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/inverse_scan_analyzer.py
  - pattern: "class CodeCoverageMetrics"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/inverse_scan_analyzer.py
  - pattern: "def calculate_coverage"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/inverse_scan_analyzer.py
  - pattern: "coverage_gap_critical"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
  - pattern: "_handle_coverage_gap"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
-->

---
*OPUS-129: Because code without documentation is invisible code*
