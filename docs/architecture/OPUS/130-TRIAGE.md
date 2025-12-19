# OPUS-130: The Triage - Coverage Gap Prioritization

> **Status**: IMPLEMENTED
> **Created**: 2025-12-19
> **Author**: MANAS (with Gemini collaboration)
> **Territory**: MANAS (050-099)
> **Depends**: OPUS-127 (KarmaSense), OPUS-129 (Inverse Scan/Viveka)
> **Philosophy**: Not all gaps are equal - focus on what hurts most

---

## The Problem: 332 Gaps is Overwhelming

The Inverse Scan (OPUS-129) revealed the truth:
- 44.7% documentation coverage
- 332 undocumented code elements
- Grade F

But 332 intents would overwhelm any system. We need **triage**.

```
Traditional approach: Fix everything!
  → 332 items → Analysis paralysis → Nothing gets done

Triage approach: Fix what matters!
  → Prioritize by pain × complexity
  → Address critical gaps first
  → Entropy decreases systematically
```

## The Solution: Multi-Factor Prioritization

### MANAS's 5 Senses Integration

| Sense | Sanskrit | What It Sees | OPUS |
|-------|----------|--------------|------|
| PrakritiSense | प्रकृति | Git state changes | Core |
| DharmaSense | धर्म | Ethics/rule violations | Core |
| SutraSense | सूत्र | Doc → Code (harness) | 054 |
| KarmaSense | कर्म | History/chronic pain | 127 |
| VivekaSense | विवेक | Code → Doc (coverage) | 129 |

The Triage uses **KarmaSense × VivekaSense** intersection:

```python
# Priority calculation
priority_score = (
    complexity_weight     # From VivekaSense (simple=1, moderate=3, complex=5)
    × churn_factor        # From KarmaSense (recent changes = higher)
    × public_api_boost    # +2 if part of public API
)
```

### Priority Tiers

| Priority | Criteria | Action |
|----------|----------|--------|
| **P1** | High Complexity + High Churn | Document immediately - these are actively being modified but nobody understands them |
| **P2** | High Complexity | Document soon - these are time bombs waiting to hurt |
| **P3** | Public API | Document next - external consumers need these |
| **P4** | Moderate complexity | Schedule - normal tech debt |
| **P5** | Simple code | Optional - self-documenting |

## Implementation

### TriageAnalyzer

```python
from vibe_core.plugins.opus_assistant.manas.analyzers.triage_analyzer import (
    TriageAnalyzer,
    TriagePriority,
)

analyzer = TriageAnalyzer(workspace=Path("."))

# Get prioritized gaps
priorities = analyzer.triage_coverage_gaps()

for gap in priorities:
    print(f"[{gap.priority}] {gap.element_name}")
    print(f"  Complexity: {gap.complexity}")
    print(f"  Churn Score: {gap.churn_score}")
    print(f"  Priority Score: {gap.priority_score}")
```

### Integration with Inverse Scan

The TriageAnalyzer extends InverseScanAnalyzer:

```
InverseScanAnalyzer.calculate_coverage()
    ↓
TriageAnalyzer.enrich_with_karma()  # Add churn data from KarmaSense
    ↓
TriageAnalyzer.classify_priority()  # Assign P1-P5
    ↓
Prioritized intent stream (most critical first)
```

## Real-World Results

First triage of the 332 gaps:

```
======================================================================
  OPUS-130: Coverage Gap Triage Results
======================================================================

  P1 (Critical): 8 gaps
    - ShivaLifecycleManager (complex, high churn)
    - CognitiveKernel (complex, high churn)
    - BrahmaShutdown (complex, high churn)
    - TaskDispatcher (complex, moderate churn)
    ...

  P2 (High): 36 gaps
    - ContentAnalyzer (complex, low churn)
    - VedaLoader (complex, low churn)
    - MandalaRouter (complex, low churn)
    ...

  P3 (Public API): 12 gaps
    - steward.create_attestation (moderate, public)
    - governance.validate (moderate, public)
    ...

  P4 (Moderate): 142 gaps
  P5 (Simple): 134 gaps

  Recommendation:
    Focus on 8 P1 gaps first. These are the "chronic pain" points.
    Schedule P2 gaps for the next sprint.
    P3 gaps should be reviewed for API documentation needs.
```

## The Proof of Concept

This document itself proves the triage works:

1. **DisharmonyDetector was flagged** as undocumented (P1 - complex, critical component)
2. **Investigation revealed**: OPUS-116/117 exist but lacked @HARNESS wiring
3. **Fix applied**: Added @HARNESS blocks to OPUS-116 and OPUS-117
4. **Result**: DisharmonyDetector is now properly wired

The irony: Our pain sensor needed healing. The doctor healed himself.

## Intent Types

### `triage_p1_critical`

Generated for P1 gaps (high complexity + high churn):

```yaml
title: "P1: Document ShivaLifecycleManager"
priority: CRITICAL
params:
  element_name: "ShivaLifecycleManager"
  file_path: "vibe_core/runtime/shiva_lifecycle_manager.py"
  complexity: "complex"
  churn_score: 0.87
  priority_score: 43.5
  reason: "High complexity code with frequent recent changes"
```

### `triage_p2_high`

Generated for P2 gaps (high complexity, low churn):

```yaml
title: "P2: Document ContentAnalyzer"
priority: HIGH
params:
  element_name: "ContentAnalyzer"
  complexity: "complex"
  churn_score: 0.12
  priority_score: 6.0
```

## The Philosophy

> "Triage is not about doing less. It's about doing what matters first."

Traditional gap analysis says: "You have 332 problems."
Triage says: "You have 8 fires, 36 smoke warnings, and 288 items for later."

MANAS with triage becomes **efficient**, not just **thorough**.

## Relationship to Other OPUS

```
OPUS-127 (KarmaSense)  ─────┐
  "What hurts chronically?"  │
                             ├──→ OPUS-130 (Triage)
OPUS-129 (Viveka)     ──────┘     "What to fix first?"
  "What's undocumented?"
                                       │
                                       ▼
                              MANAS Intent Stream
                              (P1 → P2 → P3 → ...)
```

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/inverse_scan_analyzer.py
    required: true
    rationale: "Coverage gap detection (base for triage)"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/karma_sense.py
    required: true
    rationale: "Chronic pain detection for churn scoring"
  - path: vibe_core/plugins/opus_assistant/manas/intent_router.py
    required: true
    rationale: "Triage intent handlers"

wiring:
  - pattern: "class InverseScanAnalyzer"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/inverse_scan_analyzer.py
  - pattern: "class CodeCoverageMetrics"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/inverse_scan_analyzer.py
  - pattern: "calculate_coverage"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/inverse_scan_analyzer.py
  - pattern: "class KarmaSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/karma_sense.py
  - pattern: "class ChronicPainReport"
    in: vibe_core/plugins/opus_assistant/manas/cortex/karma_sense.py
  - pattern: "_handle_coverage_gap"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
-->

---
*OPUS-130: Because wisdom is knowing what to heal first*
