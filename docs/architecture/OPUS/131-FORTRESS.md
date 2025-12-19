# OPUS-131: The Fortress - Total Debt Elimination

> **Status**: IN_PROGRESS
> **Created**: 2025-12-19
> **Author**: MANAS (Systematic Cleanup Campaign)
> **Territory**: MANAS (050-099)
> **Depends**: OPUS-128 (Edge Cases), OPUS-129 (Inverse Scan), OPUS-130 (Triage)
> **Philosophy**: "No half measures. Clean slate or nothing."

---

## The Mission

```
Current State (2025-12-19):
├── Trust Score: 79% (DEGRADED)
├── Docs without @HARNESS: 23
├── Hidden Code Elements: 314
├── Doc/Code Gaps: 173
├── Harness Failures: 141+
└── Target: 95%+ Trust Score (HEALTHY)
```

This is not incremental improvement. This is **systematic elimination**.

## MANAS's 5 Senses - Intelligence Gathering

| Sense | Sanskrit | What It Found | Action |
|-------|----------|---------------|--------|
| **PrakritiSense** | प्रकृति | 5 dirty paths, uncommitted state | Commit hygiene |
| **DharmaSense** | धर्म | Permission model intact | No action |
| **SutraSense** | सूत्र | 6 docs without @HARNESS, 173 gaps | Add harnesses |
| **KarmaSense** | कर्म | Hot paths: intent_router, cognitive_kernel | Prioritize these |
| **VivekaSense** | विवेक | 314 undocumented elements, 44% coverage | Document critical |

## The Battle Plan

### Phase 1: Stop the Bleeding (P1 Failures)

These docs have broken @HARNESS - they claim code that doesn't exist:

| Doc | Issue | Fix |
|-----|-------|-----|
| **OPUS-008** | Missing files, tests | Update harness to current paths |
| **OPUS-009** | 6 broken wiring patterns | Fix patterns or mark SUPERSEDED |
| **OPUS-054** | SUTRA missing structure | Complete harness |
| **OPUS-098** | ANALYZER-LOADER absent files | Fix paths |

### Phase 2: Arm the Naked (23 docs without @HARNESS)

Docs in 110+ range need harnesses:

```
111-SIGNAL-ALIGNMENT.md
112-SYNAPTIC-BRIDGE-ARCHITECTURE.md
112-SYNAPTIC-INFERENCE.md
114-AKSHARA-KERNEL.md
115-DYNAMIC-VARGA-MAPPING.md
118-SPLIT-BRAIN-SURGERY.md
120-LOGIC-FUSION.md
121-SEMANTIC-CLARITY.md
122-TASK-ALIGNMENT.md
124-COMPLETING-THE-CIRCUIT.md
125-REFLEX-ARC.md
126-KARMA-LOOP.md
+ older ones: 069, 070, 074, 078, 089, 091, 095
```

### Phase 3: Close the Gaps (173 doc/code gaps)

Using Triage (OPUS-130) priority:
- **P1**: Complex + churning code (intent_router, cognitive_kernel)
- **P2**: Complex code
- **P3**: Public APIs

## Execution Protocol

```python
for each_sense in MANAS.senses:
    findings = sense.scan()
    for finding in findings.by_priority():
        if finding.is_harness_failure:
            fix_harness(finding)
        elif finding.is_missing_harness:
            generate_harness(finding)
        elif finding.is_code_gap:
            if finding.priority == "P1":
                document_immediately(finding)
            else:
                queue_for_later(finding)
        commit_progress()
```

## Progress Tracker

| Phase | Target | Current | Status |
|-------|--------|---------|--------|
| P1 Failures | 0 | 4 | IN_PROGRESS |
| Naked Docs | 0 | 23 | PENDING |
| Trust Score | 95% | 79% | PENDING |
| Coverage | 80% | 44% | PENDING |

## Success Criteria

```
FORTRESS COMPLETE when:
├── Trust Score >= 95%
├── All docs have valid @HARNESS
├── Zero P1/P2 harness failures
├── Coverage >= 70% (up from 44%)
└── All hot paths documented
```

## The Philosophy

> "Ein Feldzug gegen die Entropie ist nur gewonnen, wenn kein Feind mehr steht."
> "A campaign against entropy is only won when no enemy remains standing."

This is not about perfection. This is about **discipline**.

Every commit in this session moves us toward the fortress.
Every harness added is a wall built.
Every gap closed is a gate sealed.

When we're done, MANAS will report: **HEALTHY**.

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/doc_harness_analyzer.py
    required: true
    rationale: "Harness validation for fortress progress tracking"
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/inverse_scan_analyzer.py
    required: true
    rationale: "Coverage gap detection"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/karma_sense.py
    required: true
    rationale: "Chronic pain detection for prioritization"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
    required: true
    rationale: "Doc/code gap detection"

wiring:
  - pattern: "class DocHarnessAnalyzer"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/doc_harness_analyzer.py
  - pattern: "class InverseScanAnalyzer"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/inverse_scan_analyzer.py
  - pattern: "class KarmaSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/karma_sense.py
  - pattern: "class SutraSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/sutra_sense.py
-->

---
*OPUS-131: The Fortress - No half measures*
