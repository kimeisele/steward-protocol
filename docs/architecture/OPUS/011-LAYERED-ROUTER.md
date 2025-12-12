# OPUS-011: LayeredRouter Architecture

> **Status**: ✅ IMPLEMENTED
> **Created**: 2025-12-07
> **Last Updated**: 2025-12-09
> **Implementation**: `vibe_core/runtime/layered_router.py`
> **Philosophy**: LLM is a crutch. Intelligence comes from architecture.

<!-- @HARNESS
files:
  - path: vibe_core/runtime/layered_router.py
    required: true
  - path: vibe_core/runtime/unified_execution.py
    required: true
  - path: tests/unit/test_layered_router.py
    required: true
  - path: vibe_core/knowledge/graph.py
    required: true
  - path: vibe_core/playbook/ephemeral_storage.py
    required: true
tests:
  - tests/unit/test_layered_router.py
wiring:
  - pattern: "LayeredRouter"
    in: vibe_core/runtime/layered_router.py
  - pattern: "RouteResult"
    in: vibe_core/runtime/layered_router.py
  - pattern: "UnifiedRouter"
    in: vibe_core/runtime/unified_execution.py
  - pattern: "layer1_exact"
    in: vibe_core/runtime/layered_router.py
  - pattern: "layer2_semantic"
    in: vibe_core/runtime/layered_router.py
absent:
  - pattern: "TODO.*routing"
    in: vibe_core/runtime/layered_router.py
config:
  - section: routing
semantic:
  - type: method_exists
    name: "layered_router_route"
    class: LayeredRouter
    method: route
    in: vibe_core/runtime/layered_router.py
-->

---

## Executive Summary

The current `UnifiedRouter` is broken:
- Uses `if pattern in input` (substring match) instead of regex
- Only looks at `circuit.intent_patterns`, misses `semantic_grounding.intent_patterns`
- All natural language routes to `SIMPLE_QUERY` fallback

This document specifies a **LayeredRouter** that provides "verblüffend intelligent" routing WITHOUT LLM dependency through a 3-layer cascade architecture.

---

## Core Principle: Graceful Degradation

```
┌─────────────────────────────────────────────────────────────────┐
│  ENVIRONMENT          │  AVAILABLE LAYERS                      │
├───────────────────────┼─────────────────────────────────────────┤
│  Offline/Embedded     │  Layer 1 + Layer 2 (deterministic)     │
│  Standard Runtime     │  Layer 1 + Layer 2 + Layer 3           │
│  With Local LLM       │  Layer 1 + Layer 2 + Layer 3 + LLM     │
│  Quantum Computer     │  All layers + future extensions        │
└───────────────────────┴─────────────────────────────────────────┘
```

**No LLM required for core functionality. Ever.**

---

## Architecture Overview

```
                         USER INPUT
                    "implement api logging"
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LAYERED ROUTER                             │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  LAYER 1: EXACT MATCH (circuit.intent_patterns)          │  │
│  │  ─────────────────────────────────────────────────────── │  │
│  │  • Source: circuit.intent_patterns (simple keywords)      │  │
│  │  • Method: Exact string match (case-insensitive)          │  │
│  │  • Speed: O(n) where n = total keywords                   │  │
│  │  • Confidence: 1.0 (deterministic)                        │  │
│  │  • Example: "status" → SYSTEM_STATUS_V2                   │  │
│  └─────────────────────────┬─────────────────────────────────┘  │
│                            │ no match                           │
│                            ▼                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  LAYER 2: SEMANTIC MATCH (semantic_grounding)            │  │
│  │  ─────────────────────────────────────────────────────── │  │
│  │  • Source: semantic_grounding.intent_patterns (regex)     │  │
│  │  • Method: re.search() with compiled patterns             │  │
│  │  • Speed: O(n) where n = total regex patterns             │  │
│  │  • Confidence: 0.7-0.95 (based on pattern specificity)    │  │
│  │  • Bonus: param_extraction for automatic argument parse   │  │
│  │  • Example: "implement api logging" → FEATURE_IMPLEMENT   │  │
│  └─────────────────────────┬─────────────────────────────────┘  │
│                            │ no match                           │
│                            ▼                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  LAYER 3: CONTEXT-AWARE (Ephemeral + Knowledge Graph)    │  │
│  │  ─────────────────────────────────────────────────────── │  │
│  │  • Source: Session history, recent patterns, KG concepts  │  │
│  │  • Method: Weighted scoring based on context signals      │  │
│  │  • Speed: O(1) lookup + O(k) scoring                      │  │
│  │  • Confidence: 0.5-0.8 (contextual)                       │  │
│  │  • Example: After 3 feature requests → bias to FEATURE_*  │  │
│  └─────────────────────────┬─────────────────────────────────┘  │
│                            │ no match                           │
│                            ▼                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  FALLBACK: SIMPLE_QUERY circuit                          │  │
│  │  Confidence: 0.3                                          │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer Specifications

### Layer 1: Exact Match

**Purpose**: Zero-ambiguity commands that must always work.

**Data Source**:
```yaml
# In circuit YAML files - TOP LEVEL of circuit block
circuit:
  id: "SYSTEM_STATUS_V2"
  intent_patterns:      # <-- Layer 1 reads THIS
    - "status"
    - "system status"
    - "show status"
    - "health"
    - "agents"
```

**Algorithm**:
```python
def layer1_match(self, user_input: str) -> Optional[RouteResult]:
    """
    Exact keyword matching. O(n) where n = total keywords.

    Returns RouteResult with confidence=1.0 on match.
    Returns None if no match (falls through to Layer 2).
    """
    normalized = user_input.strip().lower()

    for circuit_id, circuit_data in self._circuits.items():
        circuit_def = circuit_data.get("circuit", {})
        patterns = circuit_def.get("intent_patterns", [])

        for pattern in patterns:
            # Exact match (case-insensitive)
            if normalized == pattern.lower():
                return RouteResult(
                    circuit_id=circuit_id,
                    confidence=1.0,
                    layer="exact",
                    extracted_params={}
                )
            # Prefix match for commands with args: "status verbose"
            if normalized.startswith(pattern.lower() + " "):
                return RouteResult(
                    circuit_id=circuit_id,
                    confidence=0.95,
                    layer="exact_prefix",
                    extracted_params={"args": normalized[len(pattern)+1:]}
                )

    return None  # Fall through to Layer 2
```

**Characteristics**:
- **Deterministic**: Same input always produces same output
- **Fast**: Simple string comparison
- **No dependencies**: Works offline, embedded, anywhere
- **Confidence**: Always 1.0 (or 0.95 for prefix match)

---

### Layer 2: Semantic Match

**Purpose**: Natural language understanding via regex patterns with parameter extraction.

**Data Source**:
```yaml
# In circuit YAML files - SEMANTIC_GROUNDING block
semantic_grounding:
  syscall_type: "DISPATCH_TASK"
  target_agent: "engineer"
  intent_patterns:      # <-- Layer 2 reads THIS
    - 'implement\s+(?:a\s+)?(?:new\s+)?feature'
    - 'add\s+(?:a\s+)?(?:new\s+)?(?:feature|functionality)'
    - 'write\s+code\s+(?:for|to)'
  param_extraction:     # <-- Layer 2 uses THIS for argument extraction
    feature_description:
      patterns:
        - 'implement\s+(.+)'
        - 'add\s+(?:a\s+)?(?:feature\s+)?(?:that\s+)?(.+)'
      required: true
```

**Algorithm**:
```python
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class RouteResult:
    circuit_id: str
    confidence: float
    layer: str
    extracted_params: Dict[str, str]
    syscall_type: Optional[str] = None
    target_agent: Optional[str] = None

class Layer2Matcher:
    """Semantic pattern matching with param extraction."""

    def __init__(self):
        self._compiled_patterns: Dict[str, List[Tuple[re.Pattern, str]]] = {}
        self._param_extractors: Dict[str, Dict] = {}
        self._semantic_metadata: Dict[str, Dict] = {}

    def build_index(self, circuits: Dict[str, Dict]) -> None:
        """
        Pre-compile all regex patterns at boot time.
        Called once during kernel initialization.
        """
        for circuit_id, circuit_data in circuits.items():
            semantic = circuit_data.get("semantic_grounding", {})
            if not semantic:
                continue

            patterns = semantic.get("intent_patterns", [])
            compiled = []
            for pattern in patterns:
                try:
                    # Compile with IGNORECASE for natural language
                    compiled.append((
                        re.compile(pattern, re.IGNORECASE),
                        pattern  # Keep original for debugging
                    ))
                except re.error as e:
                    logger.warning(f"Invalid regex in {circuit_id}: {pattern} - {e}")

            if compiled:
                self._compiled_patterns[circuit_id] = compiled
                self._param_extractors[circuit_id] = semantic.get("param_extraction", {})
                self._semantic_metadata[circuit_id] = {
                    "syscall_type": semantic.get("syscall_type"),
                    "target_agent": semantic.get("target_agent"),
                }

    def match(self, user_input: str) -> Optional[RouteResult]:
        """
        Match input against all semantic patterns.
        Returns best match with extracted parameters.
        """
        best_match: Optional[RouteResult] = None
        best_specificity = 0

        for circuit_id, patterns in self._compiled_patterns.items():
            for compiled_re, original_pattern in patterns:
                match = compiled_re.search(user_input)
                if match:
                    # Calculate specificity score based on pattern complexity
                    specificity = self._calculate_specificity(original_pattern, match)

                    if specificity > best_specificity:
                        best_specificity = specificity

                        # Extract parameters
                        params = self._extract_params(
                            circuit_id,
                            user_input,
                            match
                        )

                        metadata = self._semantic_metadata.get(circuit_id, {})

                        best_match = RouteResult(
                            circuit_id=circuit_id,
                            confidence=min(0.95, 0.7 + (specificity * 0.05)),
                            layer="semantic",
                            extracted_params=params,
                            syscall_type=metadata.get("syscall_type"),
                            target_agent=metadata.get("target_agent"),
                        )

        return best_match

    def _calculate_specificity(self, pattern: str, match: re.Match) -> float:
        """
        Calculate pattern specificity score.
        More specific patterns = higher confidence.

        Factors:
        - Pattern length (longer = more specific)
        - Number of capture groups
        - Match coverage (what % of input matched)
        """
        pattern_length_score = min(len(pattern) / 50, 1.0)
        group_score = min(match.lastindex or 0, 3) / 3
        coverage = len(match.group(0)) / len(match.string)

        return (pattern_length_score + group_score + coverage) / 3

    def _extract_params(
        self,
        circuit_id: str,
        user_input: str,
        intent_match: re.Match
    ) -> Dict[str, str]:
        """
        Extract parameters using param_extraction patterns.
        """
        params = {}
        extractors = self._param_extractors.get(circuit_id, {})

        for param_name, extractor_config in extractors.items():
            patterns = extractor_config.get("patterns", [])

            for pattern in patterns:
                try:
                    match = re.search(pattern, user_input, re.IGNORECASE)
                    if match and match.groups():
                        params[param_name] = match.group(1).strip()
                        break
                except re.error:
                    continue

            # Apply default if no match and default exists
            if param_name not in params:
                default = extractor_config.get("default")
                if default:
                    params[param_name] = default

        return params
```

**Characteristics**:
- **Regex-powered**: Full regex support for flexible matching
- **Parameter extraction**: Automatically extracts arguments from natural language
- **Specificity scoring**: Prefers more specific patterns over generic ones
- **Pre-compiled**: Patterns compiled at boot, not per-request
- **No LLM needed**: Pure deterministic regex matching

---

### Layer 3: Context-Aware

**Purpose**: Use session context and knowledge graph to improve routing when Layers 1+2 don't match confidently.

**Data Sources**:
1. **Ephemeral Storage**: Recent requests, session state, user patterns
2. **Knowledge Graph**: Concept relationships, agent domains

**Algorithm**:
```python
@dataclass
class ContextSignal:
    """A weighted signal from context analysis."""
    circuit_id: str
    weight: float
    reason: str

class Layer3ContextRouter:
    """Context-aware routing using Ephemeral and Knowledge Graph."""

    def __init__(self, ephemeral: EphemeralStorage, knowledge_graph: UnifiedKnowledgeGraph):
        self._ephemeral = ephemeral
        self._kg = knowledge_graph

    def match(self, user_input: str, layer2_candidates: List[RouteResult]) -> Optional[RouteResult]:
        """
        Apply context signals to boost or filter candidates.

        If layer2_candidates is empty, attempt concept-based routing.
        If layer2_candidates has multiple matches, use context to pick best.
        """
        signals = self._gather_signals(user_input)

        if not layer2_candidates:
            # No Layer 2 match - try concept-based routing
            return self._concept_route(user_input, signals)

        if len(layer2_candidates) == 1:
            # Single candidate - boost confidence if context supports it
            candidate = layer2_candidates[0]
            boost = self._calculate_boost(candidate.circuit_id, signals)
            candidate.confidence = min(0.95, candidate.confidence + boost)
            return candidate

        # Multiple candidates - pick best based on context
        return self._pick_best(layer2_candidates, signals)

    def _gather_signals(self, user_input: str) -> List[ContextSignal]:
        """Gather context signals from various sources."""
        signals = []

        # Signal 1: Recent circuit usage
        recent = self._ephemeral.get("recent_circuits", [])
        for circuit_id in recent[-5:]:  # Last 5 circuits
            signals.append(ContextSignal(
                circuit_id=circuit_id,
                weight=0.1,
                reason="recently_used"
            ))

        # Signal 2: Session phase
        phase = self._ephemeral.get("session_phase", "UNKNOWN")
        phase_circuits = {
            "CODING": ["FEATURE_IMPLEMENT_V2", "DEBUG_FIX_V2"],
            "RESEARCH": ["RESEARCH_SYNTH_V2"],
            "PLANNING": ["SYSTEM_DESIGN_V2", "PROJECT_SCAFFOLD_V2"],
        }
        for circuit_id in phase_circuits.get(phase, []):
            signals.append(ContextSignal(
                circuit_id=circuit_id,
                weight=0.15,
                reason=f"session_phase_{phase}"
            ))

        # Signal 3: Knowledge graph concepts
        concepts = self._extract_concepts(user_input)
        for concept in concepts:
            agent = self._kg.resolver.get_agent_for_concept(concept)
            if agent:
                # Map agent to circuits
                agent_circuits = self._get_circuits_for_agent(agent)
                for circuit_id in agent_circuits:
                    signals.append(ContextSignal(
                        circuit_id=circuit_id,
                        weight=0.2,
                        reason=f"concept_{concept}_agent_{agent}"
                    ))

        return signals

    def _extract_concepts(self, user_input: str) -> List[str]:
        """Extract knowledge graph concepts from input."""
        # Simple keyword extraction - could be enhanced
        concept_keywords = {
            "security": ["security", "auth", "permission", "access"],
            "content": ["content", "publish", "article", "post"],
            "governance": ["vote", "policy", "approve", "governance"],
            "development": ["code", "implement", "feature", "bug", "fix"],
        }

        found = []
        lower_input = user_input.lower()
        for concept, keywords in concept_keywords.items():
            if any(kw in lower_input for kw in keywords):
                found.append(concept)

        return found

    def _concept_route(self, user_input: str, signals: List[ContextSignal]) -> Optional[RouteResult]:
        """
        Route based purely on concepts when no pattern matches.
        Last resort before fallback.
        """
        if not signals:
            return None

        # Aggregate signals by circuit
        scores: Dict[str, float] = {}
        for signal in signals:
            scores[signal.circuit_id] = scores.get(signal.circuit_id, 0) + signal.weight

        if not scores:
            return None

        # Pick highest scoring circuit
        best_circuit = max(scores.items(), key=lambda x: x[1])

        if best_circuit[1] >= 0.3:  # Minimum threshold
            return RouteResult(
                circuit_id=best_circuit[0],
                confidence=min(0.7, 0.5 + best_circuit[1]),
                layer="context",
                extracted_params={},
            )

        return None

    def _calculate_boost(self, circuit_id: str, signals: List[ContextSignal]) -> float:
        """Calculate confidence boost from signals."""
        boost = 0.0
        for signal in signals:
            if signal.circuit_id == circuit_id:
                boost += signal.weight
        return min(0.2, boost)  # Cap at 0.2 boost

    def _pick_best(
        self,
        candidates: List[RouteResult],
        signals: List[ContextSignal]
    ) -> RouteResult:
        """Pick best candidate when multiple match."""
        for candidate in candidates:
            candidate.confidence += self._calculate_boost(candidate.circuit_id, signals)

        return max(candidates, key=lambda c: c.confidence)

    def _get_circuits_for_agent(self, agent: str) -> List[str]:
        """Map agent to related circuits."""
        agent_circuit_map = {
            "engineer": ["FEATURE_IMPLEMENT_V2", "DEBUG_FIX_V2"],
            "herald": ["CONTENT_GENERATION_V2"],
            "science": ["RESEARCH_SYNTH_V2"],
            "watchman": ["WIRING_AUDIT_V2"],
        }
        return agent_circuit_map.get(agent, [])
```

**Characteristics**:
- **Context-aware**: Uses session history to improve routing
- **Knowledge-backed**: Leverages concept-to-agent mappings
- **Boost, not replace**: Enhances Layer 2 results, doesn't override
- **Fallback route**: Can route based on concepts alone when patterns fail
- **Still no LLM**: All deterministic, all local

---

## Unified LayeredRouter Implementation

```python
"""
vibe_core/runtime/layered_router.py

LayeredRouter - 3-layer routing cascade.
Replaces UnifiedRouter._match_circuit().
"""

import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.ephemeral import EphemeralStorage
    from vibe_core.knowledge.graph import UnifiedKnowledgeGraph

logger = logging.getLogger("LAYERED_ROUTER")


@dataclass
class RouteResult:
    """Result of routing decision."""
    circuit_id: str
    confidence: float
    layer: str  # "exact", "exact_prefix", "semantic", "context", "fallback"
    extracted_params: Dict[str, str] = field(default_factory=dict)
    syscall_type: Optional[str] = None
    target_agent: Optional[str] = None


class LayeredRouter:
    """
    3-layer routing cascade for intelligent request routing.

    Layer 1: Exact match (circuit.intent_patterns)
    Layer 2: Semantic match (semantic_grounding.intent_patterns + param_extraction)
    Layer 3: Context-aware (Ephemeral + Knowledge Graph)

    Graceful degradation: Works without Layer 3 dependencies.
    """

    def __init__(
        self,
        kernel: Optional["RealVibeKernel"] = None,
        ephemeral: Optional["EphemeralStorage"] = None,
        knowledge_graph: Optional["UnifiedKnowledgeGraph"] = None,
    ):
        self._kernel = kernel
        self._ephemeral = ephemeral
        self._kg = knowledge_graph

        # Circuit data (loaded at boot)
        self._circuits: Dict[str, Dict[str, Any]] = {}

        # Layer 1: Exact match index
        # Maps lowercase keyword -> circuit_id
        self._exact_index: Dict[str, str] = {}

        # Layer 2: Compiled semantic patterns
        # Maps circuit_id -> [(compiled_regex, original_pattern)]
        self._semantic_patterns: Dict[str, List[tuple]] = {}
        self._param_extractors: Dict[str, Dict] = {}
        self._semantic_metadata: Dict[str, Dict] = {}

        # Fallback circuit
        self._fallback_circuit = "SIMPLE_QUERY"

    def inject_kernel(self, kernel: "RealVibeKernel") -> None:
        """Inject kernel and load circuits."""
        self._kernel = kernel

        # Load circuits from EnvoyPlugin
        if hasattr(kernel, "envoy"):
            self._circuits = getattr(kernel.envoy, "_circuits", {})

        # Load Ephemeral if available
        if hasattr(kernel, "ephemeral"):
            self._ephemeral = kernel.ephemeral

        # Load Knowledge Graph if available
        if hasattr(kernel, "knowledge"):
            self._kg = kernel.knowledge

        # Build indexes
        self._build_indexes()

        logger.info(
            f"[LAYERED_ROUTER] Initialized: "
            f"{len(self._exact_index)} exact patterns, "
            f"{len(self._semantic_patterns)} semantic circuits"
        )

    def _build_indexes(self) -> None:
        """Build all routing indexes at boot time."""
        for circuit_id, circuit_data in self._circuits.items():
            # Layer 1: Exact patterns
            circuit_def = circuit_data.get("circuit", {})
            exact_patterns = circuit_def.get("intent_patterns", [])
            for pattern in exact_patterns:
                self._exact_index[pattern.lower()] = circuit_id

            # Layer 2: Semantic patterns
            semantic = circuit_data.get("semantic_grounding", {})
            if semantic:
                regex_patterns = semantic.get("intent_patterns", [])
                compiled = []
                for pattern in regex_patterns:
                    try:
                        compiled.append((
                            re.compile(pattern, re.IGNORECASE),
                            pattern
                        ))
                    except re.error as e:
                        logger.warning(f"Invalid regex in {circuit_id}: {pattern} - {e}")

                if compiled:
                    self._semantic_patterns[circuit_id] = compiled
                    self._param_extractors[circuit_id] = semantic.get("param_extraction", {})
                    self._semantic_metadata[circuit_id] = {
                        "syscall_type": semantic.get("syscall_type"),
                        "target_agent": semantic.get("target_agent"),
                    }

    def route(self, user_input: str, context: Optional[Dict] = None) -> RouteResult:
        """
        Route user input through the 3-layer cascade.

        Args:
            user_input: The user's request string
            context: Optional context dict (session info, etc.)

        Returns:
            RouteResult with circuit_id, confidence, and extracted params
        """
        normalized = user_input.strip().lower()

        # Layer 1: Exact match
        result = self._layer1_exact(normalized, user_input)
        if result:
            logger.debug(f"[L1] Exact match: {result.circuit_id}")
            self._record_route(result)
            return result

        # Layer 2: Semantic match
        result = self._layer2_semantic(user_input)
        if result:
            logger.debug(f"[L2] Semantic match: {result.circuit_id} (conf={result.confidence:.2f})")

            # Layer 3: Context boost (if available)
            if self._ephemeral or self._kg:
                result = self._layer3_context_boost(result, user_input)

            self._record_route(result)
            return result

        # Layer 3: Context-only routing (last resort)
        if self._ephemeral or self._kg:
            result = self._layer3_context_only(user_input)
            if result:
                logger.debug(f"[L3] Context route: {result.circuit_id}")
                self._record_route(result)
                return result

        # Fallback
        logger.debug(f"[FALLBACK] No match, using {self._fallback_circuit}")
        return RouteResult(
            circuit_id=self._fallback_circuit,
            confidence=0.3,
            layer="fallback",
            extracted_params={"user_input": user_input},
        )

    def _layer1_exact(self, normalized: str, original: str) -> Optional[RouteResult]:
        """Layer 1: Exact keyword match."""
        # Direct match
        if normalized in self._exact_index:
            return RouteResult(
                circuit_id=self._exact_index[normalized],
                confidence=1.0,
                layer="exact",
                extracted_params={},
            )

        # Prefix match (command with args)
        for pattern, circuit_id in self._exact_index.items():
            if normalized.startswith(pattern + " "):
                return RouteResult(
                    circuit_id=circuit_id,
                    confidence=0.95,
                    layer="exact_prefix",
                    extracted_params={"args": original[len(pattern)+1:]},
                )

        return None

    def _layer2_semantic(self, user_input: str) -> Optional[RouteResult]:
        """Layer 2: Regex semantic match with param extraction."""
        best_match: Optional[RouteResult] = None
        best_score = 0.0

        for circuit_id, patterns in self._semantic_patterns.items():
            for compiled_re, original_pattern in patterns:
                match = compiled_re.search(user_input)
                if match:
                    score = self._calc_specificity(original_pattern, match)
                    if score > best_score:
                        best_score = score
                        params = self._extract_params(circuit_id, user_input)
                        metadata = self._semantic_metadata.get(circuit_id, {})

                        best_match = RouteResult(
                            circuit_id=circuit_id,
                            confidence=min(0.95, 0.7 + (score * 0.25)),
                            layer="semantic",
                            extracted_params=params,
                            syscall_type=metadata.get("syscall_type"),
                            target_agent=metadata.get("target_agent"),
                        )

        return best_match

    def _calc_specificity(self, pattern: str, match: re.Match) -> float:
        """Calculate pattern specificity for confidence scoring."""
        pattern_score = min(len(pattern) / 50, 1.0)
        coverage = len(match.group(0)) / len(match.string)
        return (pattern_score + coverage) / 2

    def _extract_params(self, circuit_id: str, user_input: str) -> Dict[str, str]:
        """Extract parameters using param_extraction patterns."""
        params = {}
        extractors = self._param_extractors.get(circuit_id, {})

        for param_name, config in extractors.items():
            for pattern in config.get("patterns", []):
                try:
                    match = re.search(pattern, user_input, re.IGNORECASE)
                    if match and match.groups():
                        params[param_name] = match.group(1).strip()
                        break
                except re.error:
                    continue

            if param_name not in params and config.get("default"):
                params[param_name] = config["default"]

        return params

    def _layer3_context_boost(self, result: RouteResult, user_input: str) -> RouteResult:
        """Layer 3: Boost confidence based on context signals."""
        boost = 0.0

        # Recent circuit usage
        if self._ephemeral:
            recent = self._ephemeral.get("recent_circuits", [])
            if result.circuit_id in recent[-5:]:
                boost += 0.05

        # Knowledge graph concept match
        if self._kg:
            concepts = self._extract_concepts(user_input)
            for concept in concepts:
                agent = self._kg.resolver.get_agent_for_concept(concept)
                if agent and agent == result.target_agent:
                    boost += 0.1
                    break

        result.confidence = min(0.98, result.confidence + boost)
        return result

    def _layer3_context_only(self, user_input: str) -> Optional[RouteResult]:
        """Layer 3: Route based on context when patterns fail."""
        scores: Dict[str, float] = {}

        # Knowledge graph concepts
        if self._kg:
            concepts = self._extract_concepts(user_input)
            for concept in concepts:
                agent = self._kg.resolver.get_agent_for_concept(concept)
                if agent:
                    circuits = self._agent_to_circuits(agent)
                    for circuit_id in circuits:
                        scores[circuit_id] = scores.get(circuit_id, 0) + 0.2

        # Recent patterns from ephemeral
        if self._ephemeral:
            recent = self._ephemeral.get("recent_circuits", [])
            for circuit_id in recent[-3:]:
                scores[circuit_id] = scores.get(circuit_id, 0) + 0.1

        if scores:
            best = max(scores.items(), key=lambda x: x[1])
            if best[1] >= 0.3:
                return RouteResult(
                    circuit_id=best[0],
                    confidence=min(0.7, 0.5 + best[1]),
                    layer="context",
                    extracted_params={},
                )

        return None

    def _extract_concepts(self, user_input: str) -> List[str]:
        """Simple concept extraction for Layer 3."""
        concept_keywords = {
            "security": ["security", "auth", "permission"],
            "content": ["content", "publish", "article"],
            "development": ["code", "implement", "feature", "bug"],
        }

        found = []
        lower = user_input.lower()
        for concept, keywords in concept_keywords.items():
            if any(kw in lower for kw in keywords):
                found.append(concept)
        return found

    def _agent_to_circuits(self, agent: str) -> List[str]:
        """Map agent to circuits."""
        mapping = {
            "engineer": ["FEATURE_IMPLEMENT_V2", "DEBUG_FIX_V2"],
            "herald": ["CONTENT_GENERATION_V2"],
            "science": ["RESEARCH_SYNTH_V2"],
        }
        return mapping.get(agent, [])

    def _record_route(self, result: RouteResult) -> None:
        """Record route to ephemeral for future context."""
        if self._ephemeral:
            recent = self._ephemeral.get("recent_circuits", [])
            recent.append(result.circuit_id)
            self._ephemeral.set("recent_circuits", recent[-10:])  # Keep last 10
```

---

## Integration Points

### 1. Replace UnifiedRouter in unified_execution.py

```python
# OLD (in unified_execution.py)
from vibe_core.runtime.unified_execution import UnifiedRouter

# NEW
from vibe_core.runtime.layered_router import LayeredRouter, RouteResult

class UnifiedRouter:
    """Thin wrapper around LayeredRouter for backwards compatibility."""

    def __init__(self, kernel=None):
        self._layered = LayeredRouter(kernel=kernel)
        self._fast_commands = {}  # Migrated to Layer 1

    def inject_kernel(self, kernel):
        self._layered.inject_kernel(kernel)

    def route(self, user_input: str, source: str = "envoy") -> ExecutionRequest:
        """Route via LayeredRouter, return ExecutionRequest."""
        result = self._layered.route(user_input)

        request = ExecutionRequest(user_input=user_input, source=source)

        if result.layer in ("exact", "exact_prefix"):
            request.mark_routed(ExecutionPath.FAST_COMMAND, result.circuit_id, result.confidence)
        elif result.layer in ("semantic", "context"):
            request.mark_routed(ExecutionPath.CIRCUIT, result.circuit_id, result.confidence)
        else:
            request.mark_routed(ExecutionPath.FALLBACK, result.circuit_id, result.confidence)

        # Store extracted params for executor
        request.phase_results["extracted_params"] = result.extracted_params

        return request
```

### 2. EnvoyPlugin Boot Integration

```python
# In EnvoyPlugin.on_boot()
def on_boot(self, kernel):
    # ... existing code ...

    # Initialize LayeredRouter
    from vibe_core.runtime.layered_router import LayeredRouter
    self._router = LayeredRouter(
        kernel=kernel,
        ephemeral=getattr(kernel, 'ephemeral', None),
        knowledge_graph=getattr(kernel, 'knowledge', None),
    )
    self._router._circuits = self._circuits
    self._router._build_indexes()
```

### 3. Phoenix Config Extension (Optional)

```yaml
# config/routing.yaml (NEW FILE - OPTIONAL)
routing:
  # Layer behavior configuration
  layers:
    exact:
      enabled: true
    semantic:
      enabled: true
      min_confidence: 0.7
    context:
      enabled: true
      min_confidence: 0.5

  # Fallback configuration
  fallback:
    circuit: "SIMPLE_QUERY"
    confidence: 0.3

  # Custom fast commands (merged with circuit.intent_patterns)
  fast_commands:
    "q": "SIMPLE_QUERY"
    "?": "HELP_COMMAND"
```

---

## Test Cases

```python
"""tests/unit/test_layered_router.py"""

import pytest
from vibe_core.runtime.layered_router import LayeredRouter, RouteResult


@pytest.fixture
def router_with_circuits():
    """Router with test circuits loaded."""
    router = LayeredRouter()
    router._circuits = {
        "SYSTEM_STATUS_V2": {
            "circuit": {
                "id": "SYSTEM_STATUS_V2",
                "intent_patterns": ["status", "system status", "health"],
            }
        },
        "FEATURE_IMPLEMENT_V2": {
            "circuit": {"id": "FEATURE_IMPLEMENT_V2"},
            "semantic_grounding": {
                "syscall_type": "DISPATCH_TASK",
                "target_agent": "engineer",
                "intent_patterns": [
                    r"implement\s+(?:a\s+)?(?:new\s+)?feature",
                    r"add\s+(?:a\s+)?(?:new\s+)?(?:feature|functionality)",
                ],
                "param_extraction": {
                    "feature_description": {
                        "patterns": [r"implement\s+(.+)", r"add\s+(?:feature\s+)?(.+)"],
                        "required": True,
                    }
                },
            },
        },
        "DEBUG_FIX_V2": {
            "circuit": {"id": "DEBUG_FIX_V2"},
            "semantic_grounding": {
                "intent_patterns": [
                    r"fix\s+(?:the\s+)?(?:bug|error|issue)",
                    r"debug\s+(?:the\s+)?(?:error|failure)",
                ],
            },
        },
    }
    router._build_indexes()
    return router


class TestLayer1Exact:
    """Layer 1: Exact match tests."""

    def test_exact_match(self, router_with_circuits):
        result = router_with_circuits.route("status")
        assert result.circuit_id == "SYSTEM_STATUS_V2"
        assert result.confidence == 1.0
        assert result.layer == "exact"

    def test_exact_match_case_insensitive(self, router_with_circuits):
        result = router_with_circuits.route("STATUS")
        assert result.circuit_id == "SYSTEM_STATUS_V2"
        assert result.confidence == 1.0

    def test_exact_prefix_with_args(self, router_with_circuits):
        result = router_with_circuits.route("status verbose")
        assert result.circuit_id == "SYSTEM_STATUS_V2"
        assert result.confidence == 0.95
        assert result.extracted_params.get("args") == "verbose"


class TestLayer2Semantic:
    """Layer 2: Semantic pattern match tests."""

    def test_semantic_match_basic(self, router_with_circuits):
        result = router_with_circuits.route("implement a new feature for logging")
        assert result.circuit_id == "FEATURE_IMPLEMENT_V2"
        assert result.layer == "semantic"
        assert result.confidence >= 0.7

    def test_semantic_match_variation(self, router_with_circuits):
        result = router_with_circuits.route("add functionality to track users")
        assert result.circuit_id == "FEATURE_IMPLEMENT_V2"

    def test_semantic_param_extraction(self, router_with_circuits):
        result = router_with_circuits.route("implement api call logging")
        assert "feature_description" in result.extracted_params
        assert "api call logging" in result.extracted_params["feature_description"]

    def test_semantic_debug_match(self, router_with_circuits):
        result = router_with_circuits.route("fix the bug in auth module")
        assert result.circuit_id == "DEBUG_FIX_V2"

    def test_semantic_syscall_metadata(self, router_with_circuits):
        result = router_with_circuits.route("implement new feature")
        assert result.syscall_type == "DISPATCH_TASK"
        assert result.target_agent == "engineer"


class TestLayer3Context:
    """Layer 3: Context-aware routing tests."""

    def test_context_boost_recent(self, router_with_circuits):
        # Simulate recent circuit usage
        router_with_circuits._ephemeral = MockEphemeral({
            "recent_circuits": ["FEATURE_IMPLEMENT_V2", "FEATURE_IMPLEMENT_V2"]
        })

        result = router_with_circuits.route("implement something")
        # Should have boosted confidence due to recent usage
        assert result.confidence > 0.7


class TestFallback:
    """Fallback behavior tests."""

    def test_fallback_on_no_match(self, router_with_circuits):
        result = router_with_circuits.route("xyzzy random gibberish")
        assert result.circuit_id == "SIMPLE_QUERY"
        assert result.layer == "fallback"
        assert result.confidence == 0.3


class MockEphemeral:
    """Mock ephemeral storage for tests."""
    def __init__(self, data):
        self._data = data
    def get(self, key, default=None):
        return self._data.get(key, default)
    def set(self, key, value):
        self._data[key] = value
```

---

## Migration Checklist

### Phase 1: Create LayeredRouter
- [ ] Create `vibe_core/runtime/layered_router.py` with full implementation
- [ ] Add `RouteResult` dataclass
- [ ] Implement `_layer1_exact()`
- [ ] Implement `_layer2_semantic()` with param extraction
- [ ] Implement `_layer3_context_boost()` and `_layer3_context_only()`

### Phase 2: Integration
- [ ] Update `UnifiedRouter` to use `LayeredRouter` internally
- [ ] Update `EnvoyPlugin.on_boot()` to initialize router
- [ ] Ensure `_circuits` dict is passed to router

### Phase 3: Testing
- [ ] Run existing router tests (should still pass)
- [ ] Add Layer 1 tests (exact match)
- [ ] Add Layer 2 tests (semantic match)
- [ ] Add Layer 3 tests (context boost)
- [ ] Add param extraction tests
- [ ] Integration test: ENVOY.md → Circuit execution

### Phase 4: Cleanup
- [ ] Remove old `_match_circuit()` from `UnifiedRouter`
- [ ] Remove hardcoded `_fast_commands` dict (now in Layer 1)
- [ ] Update documentation

---

## Success Metrics

| Metric | Before | After |
|--------|--------|-------|
| "implement feature X" routes correctly | NO | YES |
| "fix the bug" routes to DEBUG_FIX | NO | YES |
| "status" still works | YES | YES |
| Parameter extraction works | NO | YES |
| Offline routing works | YES | YES |
| LLM required | NO | NO |

---

## Appendix: Circuit Pattern Inventory

Current circuits and their pattern locations:

| Circuit | Layer 1 (circuit.intent_patterns) | Layer 2 (semantic_grounding) |
|---------|-----------------------------------|------------------------------|
| SYSTEM_STATUS_V2 | "status", "health", "agents" | - |
| FEATURE_IMPLEMENT_V2 | - | `implement\s+.*feature` |
| DEBUG_FIX_V2 | - | `fix\s+.*bug`, `debug\s+.*error` |
| RESEARCH_SYNTH_V2 | - | `research\s+.*`, `learn about` |
| PROJECT_SCAFFOLD_V2 | - | `create\s+.*project`, `scaffold` |
| SYSTEM_DESIGN_V2 | - | `design\s+.*system`, `architect` |

This dual-location approach is INTENTIONAL:
- Layer 1 patterns are for deterministic commands
- Layer 2 patterns are for natural language variations
