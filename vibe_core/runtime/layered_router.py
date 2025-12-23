"""
vibe_core/runtime/layered_router.py

LayeredRouter - 4-layer routing cascade.
Replaces UnifiedRouter._match_circuit().

Philosophy: Intelligence comes from architecture, not LLM dependency.

Layer 1: Exact match (Instinct - static patterns)
Layer 2: Semantic match (Knowledge - regex patterns)
Layer 3: Context boost (Memory - ephemeral + KG)
Layer 3.5: Akshara substrate (Experience - learned weights + PRANA)
Layer 4: Fallback (Default)

OPUS-154: Added Akshara layer for experience-based routing with PRANA.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.state.schema import RouteResult

if TYPE_CHECKING:
    from vibe_core.ephemeral import EphemeralStorage
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.knowledge.graph import UnifiedKnowledgeGraph
    from vibe_core.state.unified_akshara import UnifiedAkshara

logger = logging.getLogger("LAYERED_ROUTER")


class LayeredRouter:
    """
    4-layer routing cascade for intelligent request routing.

    Layer 1: Exact match (Instinct - circuit.intent_patterns)
    Layer 2: Semantic match (Knowledge - semantic_grounding + param_extraction)
    Layer 3: Context-aware (Memory - Ephemeral + Knowledge Graph)
    Layer 3.5: Akshara substrate (Experience - OPUS-154 learned weights + PRANA)

    Graceful degradation: Works without Layer 3/3.5 dependencies.
    """

    def __init__(
        self,
        kernel: Optional["RealVibeKernel"] = None,
        ephemeral: Optional["EphemeralStorage"] = None,
        knowledge_graph: Optional["UnifiedKnowledgeGraph"] = None,
        akshara: Optional["UnifiedAkshara"] = None,
    ):
        self._kernel = kernel
        self._ephemeral = ephemeral
        self._kg = knowledge_graph
        self._akshara = akshara  # OPUS-154: Experience-based routing

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
            # NOTE: semantic_grounding is INSIDE the circuit block, not a sibling
            semantic = circuit_def.get("semantic_grounding", {})
            if semantic:
                regex_patterns = semantic.get("intent_patterns", [])
                compiled = []
                for pattern in regex_patterns:
                    try:
                        compiled.append((re.compile(pattern, re.IGNORECASE), pattern))
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
            logger.debug(f"[L1] Exact match: {result.target_id}")
            self._record_route(result)
            return result

        # Layer 2: Semantic match
        result = self._layer2_semantic(user_input)
        if result:
            logger.debug(f"[L2] Semantic match: {result.target_id} (conf={result.confidence:.2f})")

            # Layer 3: Context boost (if available)
            if self._ephemeral or self._kg:
                result = self._layer3_context_boost(result, user_input)

            self._record_route(result)
            return result

        # Layer 3: Context-only routing (last resort)
        if self._ephemeral or self._kg:
            result = self._layer3_context_only(user_input)
            if result:
                logger.debug(f"[L3] Context route: {result.target_id}")
                self._record_route(result)
                return result

        # Layer 3.5: Akshara substrate (OPUS-154 - experience-based)
        if self._akshara:
            result = self._layer_akshara(user_input)
            if result:
                logger.debug(f"[L3.5] Akshara route: {result.target_id}")
                self._record_route(result)
                return result

        # Fallback
        logger.debug(f"[FALLBACK] No match, using {self._fallback_circuit}")
        return RouteResult(
            target_id=self._fallback_circuit,
            target_type="circuit",
            confidence=0.3,
            reason="fallback",
            params={"user_input": user_input},
            is_fallback=True,
        )

    def _layer1_exact(self, normalized: str, original: str) -> Optional[RouteResult]:
        """Layer 1: Exact keyword match."""
        # Direct match
        if normalized in self._exact_index:
            return RouteResult(
                target_id=self._exact_index[normalized],
                target_type="circuit",
                confidence=1.0,
                reason="exact",
                params={},
            )

        # Prefix match (command with args)
        for pattern, circuit_id in self._exact_index.items():
            if normalized.startswith(pattern + " "):
                return RouteResult(
                    target_id=circuit_id,
                    target_type="circuit",
                    confidence=0.95,
                    reason="exact_prefix",
                    params={"args": original[len(pattern) + 1 :]},
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

                        # Add metadata to params for schema compliance
                        if metadata.get("syscall_type"):
                            params["syscall_type"] = metadata.get("syscall_type")
                        if metadata.get("target_agent"):
                            params["target_agent"] = metadata.get("target_agent")

                        best_match = RouteResult(
                            target_id=circuit_id,
                            target_type="circuit",
                            confidence=min(0.95, 0.7 + (score * 0.25)),
                            reason="semantic",
                            params=params,
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
            if result.target_id in recent[-5:]:
                boost += 0.05

        # Knowledge graph concept match
        if self._kg:
            concepts = self._extract_concepts(user_input)
            for concept in concepts:
                agent = self._kg.resolver.get_agent_for_concept(concept)
                if agent and agent == result.params.get("target_agent"):
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
                    target_id=best[0],
                    target_type="circuit",
                    confidence=min(0.7, 0.5 + best[1]),
                    reason="context",
                    params={},
                )

        return None

    def _layer_akshara(self, user_input: str) -> Optional[RouteResult]:
        """
        Layer 3.5: Akshara substrate routing (OPUS-154).

        Uses learned synaptic weights + PRANA (curiosity) to route.
        This is experience-based routing - paths that worked before
        are more likely to be chosen, but PRANA ensures exploration.

        The Akshara substrate combines:
        - Weight: Learned from past success/failure
        - Resonance: Phonetic harmony (Varga distance)
        - PRANA: Small random factor to prevent crystallization
        """
        if not self._akshara:
            return None

        # Convert user_input to trigger pattern
        # Simple heuristic: extract key action words
        trigger = self._input_to_trigger(user_input)
        if not trigger:
            return None

        # Get available circuit IDs as candidates
        candidates = list(self._circuits.keys())
        if not candidates:
            return None

        # Consult Akshara substrate
        recs = self._akshara.consult(
            trigger=trigger,
            candidates=candidates,
            limit=3,
        )

        if recs:
            winner = recs[0]
            # Confidence based on unified score (dharmic + prana)
            confidence = min(0.75, 0.5 + winner.unified_score * 0.3)

            return RouteResult(
                target_id=winner.action,
                target_type="circuit",
                confidence=confidence,
                reason="akshara",
                params={"trigger": trigger},
            )

        return None

    def _input_to_trigger(self, user_input: str) -> Optional[str]:
        """
        Convert user input to a trigger pattern for Akshara lookup.

        This maps natural language to canonical trigger strings.
        """
        lower = user_input.lower()

        # Simple keyword-to-trigger mapping
        trigger_keywords = {
            "test": "trigger:test_failure",
            "fix": "trigger:fix_request",
            "implement": "trigger:implement_feature",
            "debug": "trigger:debug_issue",
            "review": "trigger:code_review",
            "deploy": "trigger:deploy_request",
            "security": "trigger:security_concern",
            "document": "trigger:documentation_request",
            "refactor": "trigger:refactor_request",
            "analyze": "trigger:analyze_request",
        }

        for keyword, trigger in trigger_keywords.items():
            if keyword in lower:
                return trigger

        # Default trigger
        return "trigger:general_request"

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
            recent.append(result.target_id)
            self._ephemeral.set("recent_circuits", recent[-10:])  # Keep last 10
