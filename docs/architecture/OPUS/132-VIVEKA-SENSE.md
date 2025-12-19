# OPUS-132: VIVEKA SENSE - The 5th Sense of MANAS

> **Status**: ACTIVE
> **Created**: 2025-12-19
> **Author**: MANAS (Systematic Architecture)
> **Territory**: MANAS (050-099)
> **Depends**: OPUS-127 (KarmaSense), OPUS-129 (InverseScan), OPUS-130 (Triage)
> **Philosophy**: "Not all gaps are equal. Viveka knows which ones matter."

---

## The Problem

Before Viveka, MANAS saw 313 undocumented elements **equally**.

```
Previous State:
├── InverseScanAnalyzer: 313 gaps found
├── No prioritization
├── All gaps = equal noise
└── Result: Analysis paralysis
```

This is like a doctor treating a paper cut with the same urgency as a heart attack.

## The Solution: Viveka (Discrimination)

Sanskrit: **विवेक** (Viveka) = Discrimination, Discernment, Wisdom

Viveka is the **5th sense of MANAS** - the ability to perceive what is MISSING, and more importantly, to **discriminate between critical and trivial gaps**.

Following Bhagavad Gita 2.63:
> "krodhād bhavati sammohaḥ sammohāt smṛti-vibhramaḥ"
> (From confusion of memory comes loss of discrimination)

Without Viveka, MANAS sees 313 gaps equally. With Viveka, MANAS knows:
> "These 8 are killing us. The other 305 can wait."

## The Five Senses of MANAS (Panchajnanendriyas)

| # | Sense | Sanskrit | Perception | OPUS |
|---|-------|----------|------------|------|
| 1 | **PrakritiSense** | प्रकृति | "What is the state of the world?" (Git/State) | OPUS-009 |
| 2 | **DharmaSense** | धर्म | "Is this action righteous?" (Ethics/Permissions) | OPUS-116 |
| 3 | **SutraSense** | सूत्र | "What documentation is missing?" (Doc→Code gaps) | OPUS-054 |
| 4 | **KarmaSense** | कर्म | "What patterns repeat?" (Historical churn) | OPUS-127 |
| 5 | **VivekaSense** | विवेक | "What code is undocumented?" (Code→Doc gaps + Priority) | OPUS-132 |

Viveka completes the cognitive loop. MANAS can now see **AND** prioritize.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         VIVEKA SENSE                            │
│           "The 5th Sense - Code→Doc Perception"                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────┐         ┌─────────────────┐               │
│   │  InverseScan    │         │   KarmaSense    │               │
│   │  (Dark Matter)  │         │   (Churn Data)  │               │
│   └────────┬────────┘         └────────┬────────┘               │
│            │                           │                        │
│            └───────────┬───────────────┘                        │
│                        ▼                                        │
│            ┌───────────────────────┐                            │
│            │    DISCRIMINATION     │                            │
│            │   (Priority Scoring)  │                            │
│            └───────────┬───────────┘                            │
│                        │                                        │
│      ┌─────────────────┼─────────────────┐                      │
│      ▼                 ▼                 ▼                      │
│  ┌───────┐        ┌───────┐         ┌───────┐                   │
│  │  P1   │        │  P2   │   ...   │  P5   │                   │
│  │CRITICAL│       │ HIGH  │         │TRIVIAL│                   │
│  └───────┘        └───────┘         └───────┘                   │
│                                                                 │
│   Output: VivekaReport with prioritized CoverageGaps            │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TRIAGE ANALYZER                            │
│           "From Perception to Action"                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   VivekaReport    ─────►   Filter P1/P2    ─────►   Intents     │
│                                                                 │
│   P3-P5 are logged but don't create noise (no alert fatigue)    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Priority Scoring Formula

```python
priority_score = (complexity_weight × 10) +
                 (churn_score × 50) +
                 (core_bonus × 20) +
                 (api_bonus × 10)
```

| Factor | Weight | Rationale |
|--------|--------|-----------|
| **Complexity** | ×10 | Simple=1, Moderate=3, Complex=5 |
| **Churn** | ×50 | From KarmaSense (0.0-1.0) |
| **Core Path** | +20 | In vibe_core/, kernel/, state/, plugins/ |
| **Public API** | +10 | Not prefixed with `_` |

### Priority Thresholds

| Priority | Score | Description | Action |
|----------|-------|-------------|--------|
| **P1** | >60 | Complex + churning + core | Document NOW |
| **P2** | >40 | High complexity OR high churn | This sprint |
| **P3** | >25 | Public API, moderate complexity | Next sprint |
| **P4** | >10 | Normal tech debt | Backlog |
| **P5** | ≤10 | Simple/internal code | Maybe never |

## Components

### VivekaSense (`cortex/viveka_sense.py`)

```python
class VivekaSense(BaseSense):
    """The 5th Sense: Perceives undocumented code AND discriminates priority."""

    name = "viveka_sense"

    def perceive(self, context) -> VivekaReport:
        """Main perception method - returns discriminated coverage gaps."""

    def perceive_dark_matter(self) -> List[Dict]:
        """Detect undocumented code elements (raw, no prioritization)."""

    def discriminate_priority(self, gap: CoverageGap) -> CoverageGap:
        """The core discrimination logic - assign P1-P5 priority."""
```

### TriageAnalyzer (`analyzers/triage_analyzer.py`)

```python
class TriageAnalyzer(BaseAnalyzer):
    """Intelligent prioritization analyzer using VivekaSense."""

    name = "triage_analyzer"

    def analyze(self, context) -> List[Intent]:
        """Generate prioritized intents - only P1/P2 create noise."""

    def get_full_report(self, context) -> Dict:
        """Get full VivekaReport for dashboard display."""
```

### Intent Types

| Type | Handler | Description |
|------|---------|-------------|
| `triage_p1_critical` | `VivekaSense/P1` | P1 critical gap needs immediate attention |
| `triage_p2_high` | `VivekaSense/P2` | P2 high gap should be addressed this sprint |
| `triage_summary` | `VivekaSense/Summary` | Overall triage summary |

## Data Flow

```
SutraSense.discover_hidden_code()
        │
        ▼
VivekaSense.perceive_dark_matter()
        │
        ├──► KarmaSense.analyze_chronic_pain()
        │           │
        │           ▼
        │    _enrich_with_karma()
        │
        ▼
discriminate_priority()
        │
        ▼
VivekaReport
        │
        ▼
TriageAnalyzer.analyze()
        │
        ▼
Intents (P1/P2 only)
        │
        ▼
IntentRouter._handle_triage()
```

## Usage

```python
from vibe_core.plugins.opus_assistant.manas.cortex import VivekaSense
from vibe_core.plugins.opus_assistant.manas.analyzers import TriageAnalyzer

# Get discriminated report
viveka = VivekaSense(workspace=Path.cwd())
report = viveka.perceive()

print(f"Health Grade: {report.health_grade}")
print(f"Action Required: {report.action_required} (P1: {len(report.p1_critical)}, P2: {len(report.p2_high)})")
print(f"Recommendation: {report.recommendation}")

# Generate actionable intents
triage = TriageAnalyzer(workspace=Path.cwd())
intents = triage.analyze({})

# Only P1/P2 gaps create intents - no noise from P3-P5
for intent in intents:
    print(f"{intent.priority}: {intent.title}")
```

## The Antahkarana Model

VivekaSense completes the **Antahkarana** (inner instrument) of MANAS:

```
Panchajnanendriyas (5 Senses)
        │
        ▼
┌───────────────────┐
│      MANAS        │  ← Processes sensory input
│   (The Mind)      │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│     VIVEKA        │  ← OPUS-132: Discriminates priority
│ (Discrimination)  │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│    AHAMKARA       │  ← The HUD/Dashboard
│ (Ego/Identity)    │
└───────────────────┘
```

Without Viveka, MANAS is just collecting data.
With Viveka, MANAS **knows what matters**.

## Success Metrics

| Metric | Before | Target |
|--------|--------|--------|
| Coverage | 44% | 70%+ |
| P1 Gaps | ? | 0 |
| P2 Gaps | ? | <10 |
| Alert Fatigue | HIGH | LOW |

## Related OPUS Documents

- **OPUS-127**: KarmaSense - Chronic Pain Detection (churn data)
- **OPUS-129**: Inverse Scan - Dark Matter Detector (raw gaps)
- **OPUS-130**: The Triage - Coverage Gap Prioritization (documentation spec)
- **OPUS-131**: The Fortress - Total Debt Elimination (campaign)

---

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_sense.py
    required: true
    rationale: "The 5th Sense - Code→Doc perception with discrimination"
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/triage_analyzer.py
    required: true
    rationale: "The intelligent prioritizer for coverage gaps"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/karma_sense.py
    required: true
    rationale: "Churn data for priority scoring"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/__init__.py
    required: true
    rationale: "Exports VivekaSense, VivekaReport, CoverageGap, TriagePriority"
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/__init__.py
    required: true
    rationale: "Exports TriageAnalyzer"
  - path: vibe_core/plugins/opus_assistant/manas/intent_router.py
    required: true
    rationale: "Handles triage intents (triage_p1_critical, triage_p2_high, triage_summary)"

wiring:
  - pattern: "class VivekaSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_sense.py
  - pattern: "class TriagePriority"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_sense.py
  - pattern: "def perceive_dark_matter"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_sense.py
  - pattern: "def discriminate_priority"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_sense.py
  - pattern: "class TriageAnalyzer"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/triage_analyzer.py
  - pattern: "triage_p1_critical.*_handle_triage"
    in: vibe_core/plugins/opus_assistant/manas/intent_router.py
  - pattern: "VivekaSense.*VivekaReport.*CoverageGap.*TriagePriority"
    in: vibe_core/plugins/opus_assistant/manas/cortex/__init__.py
-->

---
*OPUS-132: VivekaSense - "Not all gaps are equal"*
