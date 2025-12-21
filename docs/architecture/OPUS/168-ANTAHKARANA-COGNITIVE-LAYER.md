# OPUS-168: ANTAHKARANA - The Inner Instrument

**Status:** PROPOSED
**Priority:** HIGH
**Created:** 2025-12-21
**Depends:** OPUS-167 (Fractal Architecture Restoration)
**Author:** Claude (Opus 4.5)

---

## Executive Summary

MANAS has senses (Jnanendriyas) and actions (Karmendriyas), but is missing the **Antahkarana** - the inner instrument that processes perception before decision. Currently, all 7 senses dump directly into CognitiveKernel, which is both overwhelming and architecturally wrong.

**Problem:** DharmaSense checks ethics at EXECUTION time, not DECISION time.
**Solution:** Introduce Chitta (aggregation) and Buddhi (intellect) layers.

---

## Vedic Cognitive Model

```
                    ATMAN (Pure Consciousness)
                           │
                    ┌──────┴──────┐
                    │   BUDDHI    │ ← Intellect/Decision
                    │  (Viveka)   │   "Should I do this?"
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │  AHAMKARA   │ ← Ego/Identity (future)
                    │  (I-sense)  │   "I am doing this"
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │   MANAS     │ ← Mind/Processing
                    │ (Thinking)  │   "What is this?"
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        JNANENDRIYAS   TANMATRAS   KARMENDRIYAS
        (5 Knowledge)  (5 Subtle)  (5 Action)
```

---

## Current MANAS Architecture (Problem)

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT (BROKEN)                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ALL SENSES (7 types)                                      │
│   ═══════════════════                                       │
│   PrakritiSense    ──┐                                      │
│   ShrutaSense      ──┤                                      │
│   PranaSense       ──┼──► generate_intents() ──┐            │
│   SutraSense       ──┤                         │            │
│   KarmaSense       ──┘ (via Analyzers)         │            │
│   VivekaSense      ──► TriageAnalyzer ─────────┤            │
│   DharmaSense      ──► ??? (too late!)         │            │
│                                                │            │
│                         ┌──────────────────────┘            │
│                         ▼                                   │
│              ┌─────────────────────┐                        │
│              │  CognitiveKernel    │                        │
│              │  ══════════════     │                        │
│              │  _perceive()        │ ← All intents dumped   │
│              │  _orient()          │ ← Just add more        │
│              │  _decide()          │ ← JUST THROTTLE!       │
│              │  _act()             │ ← Narasimha + Buffer   │
│              └──────────┬──────────┘                        │
│                         │                                   │
│                         ▼                                   │
│              ┌─────────────────────┐                        │
│              │  _execute_intent()  │                        │
│              │  ══════════════     │                        │
│              │  DharmaGate HERE!   │ ← TOO LATE!            │
│              └─────────────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Critical Bugs

| Bug | Severity | Location |
|-----|----------|----------|
| Dharma check too late | CRITICAL | `_execute_intent()` not `_decide()` |
| DECIDE phase empty | CRITICAL | Just `intents[:max]` throttling |
| No aggregation | HIGH | 7 senses → all dump to kernel |
| No Sthula/Sukshma split | HIGH | Gross and subtle treated same |

---

## Proposed Architecture: Antahkarana Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    ANTAHKARANA                              │
│               (The Inner Instrument)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   STHULA INDRIYA          SUKSHMA INDRIYA                  │
│   (Gross Senses)          (Subtle Senses)                  │
│   ═══════════════         ═══════════════                  │
│   PrakritiSense           KarmaSense                       │
│   ShrutaSense             VivekaSense                      │
│   PranaSense                                               │
│   SutraSense                                               │
│        │                       │                           │
│        └───────────┬───────────┘                           │
│                    ▼                                        │
│        ┌────────────────────┐                              │
│        │      CHITTA        │  ← NEW: Perception Pool      │
│        │  (Memory/Imprint)  │                              │
│        │                    │                              │
│        │  • Aggregate       │  Combine similar intents     │
│        │  • Deduplicate     │  Remove duplicates           │
│        │  • Classify        │  Sthula vs Sukshma           │
│        │  • Timestamp       │  Track perception time       │
│        └─────────┬──────────┘                              │
│                  ▼                                          │
│        ┌────────────────────┐                              │
│        │      BUDDHI        │  ← NEW: Intellect Layer      │
│        │  (Discrimination)  │                              │
│        │                    │                              │
│        │  VivekaSense.rank()│  → Priority scoring          │
│        │  DharmaSense.allow()│ → Ethical filtering         │
│        │  ResourceCheck()   │  → Capacity check            │
│        │  DependencyCheck() │  → Intent dependencies       │
│        └─────────┬──────────┘                              │
│                  ▼                                          │
│        ┌────────────────────┐                              │
│        │      MANAS         │                              │
│        │  (CognitiveKernel) │  ← SLIM: Just Router         │
│        │                    │                              │
│        │  • Buffer manage   │  Add/approve/reject          │
│        │  • Execute         │  Run approved intents        │
│        │  • Ledger          │  Record to lineage           │
│        └─────────┬──────────┘                              │
│                  ▼                                          │
│           KARMENDRIYAS                                      │
│        (Actions - Silpa, Shell, etc.)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Chitta Class (Perception Pool)

**File:** `vibe_core/plugins/opus_assistant/manas/chitta.py`

```python
@dataclass
class PerceptionEntry:
    """A single perception from a sense."""
    intent: Intent
    source_sense: str
    sense_type: str  # "sthula" or "sukshma"
    timestamp: datetime
    aggregated_with: List[str] = field(default_factory=list)

class Chitta:
    """
    OPUS-168: The Perception Pool (Memory/Subconscious).

    Sanskrit: Chitta = Memory, Subconscious mind, Storehouse of impressions

    Chitta collects perceptions from all senses and prepares them
    for Buddhi (intellect) to process. It does NOT decide - it aggregates.

    Responsibilities:
    1. Receive intents from all senses
    2. Classify as Sthula (gross) or Sukshma (subtle)
    3. Aggregate similar intents (reduce noise)
    4. Deduplicate exact matches
    5. Pass clean perception list to Buddhi
    """

    # Sense classification
    STHULA_SENSES = {"prakriti_sense", "shruta_sense", "prana_sense", "sutra_sense"}
    SUKSHMA_SENSES = {"karma_sense", "viveka_sense"}

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self._pool: List[PerceptionEntry] = []

    def receive(self, intent: Intent, source_sense: str) -> None:
        """Receive a perception from a sense."""
        sense_type = "sthula" if source_sense in self.STHULA_SENSES else "sukshma"
        entry = PerceptionEntry(
            intent=intent,
            source_sense=source_sense,
            sense_type=sense_type,
            timestamp=datetime.utcnow(),
        )
        self._pool.append(entry)

    def process(self) -> List[PerceptionEntry]:
        """
        Process the perception pool.

        1. Deduplicate exact matches
        2. Aggregate similar intents
        3. Return clean list for Buddhi
        """
        # Deduplicate
        seen = set()
        unique = []
        for entry in self._pool:
            key = (entry.intent.intent_type, entry.intent.title)
            if key not in seen:
                seen.add(key)
                unique.append(entry)

        # Aggregate similar (group by intent_type)
        aggregated = self._aggregate_similar(unique)

        # Clear pool after processing
        self._pool = []

        return aggregated

    def _aggregate_similar(self, entries: List[PerceptionEntry]) -> List[PerceptionEntry]:
        """Aggregate similar intents to reduce noise."""
        # Group by intent_type
        by_type: Dict[str, List[PerceptionEntry]] = {}
        for entry in entries:
            by_type.setdefault(entry.intent.intent_type, []).append(entry)

        # For each group, keep highest priority and note aggregation
        result = []
        for intent_type, group in by_type.items():
            if len(group) == 1:
                result.append(group[0])
            else:
                # Keep highest priority, aggregate rest
                sorted_group = sorted(group, key=lambda e: e.intent.priority.value)
                primary = sorted_group[0]
                primary.aggregated_with = [e.intent.id for e in sorted_group[1:]]
                result.append(primary)

        return result
```

### Phase 2: Buddhi Class (Intellect)

**File:** `vibe_core/plugins/opus_assistant/manas/buddhi.py`

```python
@dataclass
class BuddhiVerdict:
    """Result of Buddhi's discrimination."""
    intent: Intent
    approved: bool
    priority_score: float
    dharmic: bool
    dharma_reason: str
    resource_ok: bool
    dependencies_met: bool
    final_reason: str

class Buddhi:
    """
    OPUS-168: The Intellect (Discrimination/Decision).

    Sanskrit: Buddhi = Intellect, Wisdom, Discriminative faculty

    Buddhi receives processed perceptions from Chitta and decides
    which intents should proceed to Manas for execution.

    This is where DharmaSense and VivekaSense do their REAL work:
    - VivekaSense: Priority scoring (P1→P5)
    - DharmaSense: Ethical filtering (dharmic/adharmic)

    Responsibilities:
    1. Score each intent with VivekaSense
    2. Check ethical alignment with DharmaSense
    3. Check resource availability
    4. Check intent dependencies
    5. Return approved intents only
    """

    def __init__(
        self,
        workspace: Path,
        dharma_sense: Optional[DharmaSense] = None,
        viveka_sense: Optional[VivekaSense] = None,
    ):
        self._workspace = workspace
        self._dharma = dharma_sense
        self._viveka = viveka_sense

    def discriminate(
        self,
        perceptions: List[PerceptionEntry],
        max_intents: int = 5,
    ) -> List[BuddhiVerdict]:
        """
        Discriminate which intents should proceed.

        This is the DECIDE phase done RIGHT:
        1. VivekaSense ranks by priority
        2. DharmaSense filters by ethics (BEFORE execution!)
        3. Resource check
        4. Dependency check
        5. Return top N approved
        """
        verdicts = []

        for entry in perceptions:
            intent = entry.intent

            # 1. Priority scoring with VivekaSense
            priority_score = self._score_priority(intent)

            # 2. Ethical check with DharmaSense (EARLY!)
            dharmic, dharma_reason = self._check_dharma(intent)

            # 3. Resource check
            resource_ok = self._check_resources(intent)

            # 4. Dependency check
            deps_met = self._check_dependencies(intent)

            # Final verdict
            approved = dharmic and resource_ok and deps_met
            final_reason = self._build_reason(dharmic, resource_ok, deps_met, dharma_reason)

            verdicts.append(BuddhiVerdict(
                intent=intent,
                approved=approved,
                priority_score=priority_score,
                dharmic=dharmic,
                dharma_reason=dharma_reason,
                resource_ok=resource_ok,
                dependencies_met=deps_met,
                final_reason=final_reason,
            ))

        # Sort by priority score, filter approved, limit
        approved_verdicts = [v for v in verdicts if v.approved]
        approved_verdicts.sort(key=lambda v: v.priority_score, reverse=True)

        return approved_verdicts[:max_intents]

    def _check_dharma(self, intent: Intent) -> Tuple[bool, str]:
        """Check ethical alignment with DharmaSense."""
        if not self._dharma:
            return True, "No DharmaSense - permissive mode"

        verdict = self._dharma.check_dharmic_alignment(intent, agent_id="manas")
        return verdict.is_dharmic, verdict.reason

    def _score_priority(self, intent: Intent) -> float:
        """Score priority using VivekaSense logic."""
        # Base score from intent priority
        base_scores = {
            IntentPriority.CRITICAL: 100,
            IntentPriority.HIGH: 75,
            IntentPriority.MEDIUM: 50,
            IntentPriority.LOW: 25,
        }
        return base_scores.get(intent.priority, 50)

    def _check_resources(self, intent: Intent) -> bool:
        """Check if resources are available for this intent."""
        # TODO: Implement resource checking
        return True

    def _check_dependencies(self, intent: Intent) -> bool:
        """Check if intent dependencies are met."""
        # TODO: Implement dependency checking
        return True

    def _build_reason(
        self,
        dharmic: bool,
        resource_ok: bool,
        deps_met: bool,
        dharma_reason: str,
    ) -> str:
        """Build human-readable reason."""
        if not dharmic:
            return f"BLOCKED: {dharma_reason}"
        if not resource_ok:
            return "BLOCKED: Insufficient resources"
        if not deps_met:
            return "BLOCKED: Dependencies not met"
        return "APPROVED"
```

### Phase 3: Integrate into CognitiveKernel

**File:** `vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py`

```python
class CognitiveKernel:
    def __init__(self, ...):
        # ...existing init...

        # OPUS-168: Antahkarana components
        self._chitta = Chitta(workspace=self._workspace)
        self._buddhi = Buddhi(
            workspace=self._workspace,
            dharma_sense=self._dharma_sense,
            viveka_sense=None,  # Created per-request in TriageAnalyzer
        )

    async def _perceive(self, ...) -> Tuple[List[Any], Dict[str, Any]]:
        """PERCEIVE: Senses feed Chitta."""
        # Each sense feeds Chitta, not the kernel directly
        if self._prakriti_sense:
            for intent in self._prakriti_sense.generate_intents():
                self._chitta.receive(intent, "prakriti_sense")

        if self._prana_sense:
            for intent in self._prana_sense.generate_intents():
                self._chitta.receive(intent, "prana_sense")

        # ... other senses ...

        # Return raw observation count for metadata
        return [], {"chitta_pool_size": len(self._chitta._pool)}

    async def _orient(self, ...) -> Tuple[List[Any], Dict[str, Any]]:
        """ORIENT: Chitta processes perceptions."""
        processed = self._chitta.process()
        return processed, {"processed_count": len(processed)}

    async def _decide(self, orientations: List[PerceptionEntry]) -> Tuple[List[Any], Dict[str, Any]]:
        """DECIDE: Buddhi discriminates."""
        verdicts = self._buddhi.discriminate(
            perceptions=orientations,
            max_intents=self._config.max_intents_per_tick,
        )

        # Only approved intents proceed
        approved_intents = [v.intent for v in verdicts]

        return approved_intents, {
            "total_considered": len(orientations),
            "approved_count": len(approved_intents),
            "blocked_count": len(orientations) - len(approved_intents),
        }

    async def _act(self, decisions: List[Intent]) -> ...:
        """ACT: Only pre-approved intents reach here."""
        # No more DharmaGate here - already checked in Buddhi!
        # Just buffer and execute
        ...
```

---

## Relationship to Existing Components

### CognitiveWeaver (vibe_core/state/)
- **Location:** System level (vibe_core/state/)
- **Purpose:** Bridges State ↔ Knowledge
- **Relationship:** Chitta may CONSULT CognitiveWeaver for context
- **No conflict:** Different layer, different purpose

### Dojo (opus_assistant/manas/dojo/)
- **Purpose:** Ephemeral training (`:memory:`)
- **Relationship:** Separate from Antahkarana
- **No change:** Dojo stays as training system
- **Trigger:** Still via `enter_dojo` intent

### VivekaSense / TriageAnalyzer
- **Current:** Used in ORIENT phase via Analyzer
- **Future:** VivekaSense logic moves to Buddhi
- **TriageAnalyzer:** May become deprecated or simplified

### DharmaSense
- **Current:** Checked at EXECUTION time (too late!)
- **Future:** Checked in Buddhi DECIDE phase (correct!)

---

## Migration Path

1. **Create Chitta class** - Perception pool
2. **Create Buddhi class** - Intellect/decision
3. **Update _perceive()** - Senses → Chitta
4. **Update _orient()** - Chitta.process()
5. **Update _decide()** - Buddhi.discriminate()
6. **Remove DharmaGate from _execute_intent()** - Already checked
7. **Tests** - All 43 must pass

---

## Success Criteria

| Metric | Before | After |
|--------|--------|-------|
| DharmaSense check location | _execute_intent() | _decide() via Buddhi |
| _decide() logic | Just throttle | Full discrimination |
| Sense → Kernel coupling | Direct | Via Chitta |
| Duplicate intents | Possible | Deduplicated in Chitta |

---

## @HARNESS

```yaml
files:
  - path: vibe_core/plugins/opus_assistant/manas/chitta.py
    required: true
    rationale: "Perception pool - aggregates sense data"
  - path: vibe_core/plugins/opus_assistant/manas/buddhi.py
    required: true
    rationale: "Intellect layer - decision making"
  - path: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    required: true
    rationale: "Updated OODA cycle"

verification:
  - type: grep
    pattern: "Buddhi"
    file: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    expected: "> 0"

  - type: grep
    pattern: "_check_dharma_gate"
    file: vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py
    context: "_execute_intent"
    expected: 0  # Should be removed from execute

  - type: test
    command: pytest vibe_core/plugins/opus_assistant/manas/tests/ -v
    expected: all_pass
```

---

## References

- OPUS-167: Fractal Architecture Restoration
- OPUS-032: MANAS Awakening
- OPUS-009: Prakriti Sense
- OPUS-132: VivekaSense
- Bhagavad Gita 2.41: "Those whose minds are established in this wisdom..."
