"""
OPUS-155: AkashaSense - The 8th Jnanendriya (Knowledge Perception)

Sanskrit: आकाश (Akasha) = Ether, Space, the cosmic container of all.

This sense wraps the existing Akasha components (AkashaPort, AkashaQuery, AkashaContext)
into a VEDA-4 compliant sense that is auto-discovered by SenseLoader.

Philosophy:
    "Akasha is the space where all knowledge flows - the ether that connects."
    "Akasha must FEEL before Manas THINKS."

Unlike other senses that perceive external state:
- PrakritiSense perceives system health
- DharmaSense perceives ethical alignment
- PranaSense perceives agent lifecycle

AkashaSense perceives KNOWLEDGE itself:
- What does the system know about a topic?
- What are the dependencies between components?
- What constraints exist in the domain?

Integration:
    - Discovered by SenseLoader (VEDA-4)
    - Used in perceive phase for pre-cognitive context
    - Answers graph queries for decision support

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/akasha_sense.py
    required: true
    rationale: "VEDA-4 compliant wrapper for Akasha knowledge context"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/akasha.py
    required: true
    rationale: "Underlying Akasha components (Port, Query, Context)"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/base.py
    required: true
    rationale: "BaseSense interface"

wiring:
  - pattern: "class AkashaSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/akasha_sense.py
  - pattern: "class AkashaPerception"
    in: vibe_core/plugins/opus_assistant/manas/cortex/akasha_sense.py

tests:
  - tests/manas/cortex/test_akasha_sense.py
-->
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import BaseSense

logger = logging.getLogger("MANAS.Cortex.AkashaSense")


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class AkashaPerception:
    """Result of AkashaSense perception."""

    # Graph status
    is_loaded: bool = False
    node_count: int = 0
    edge_count: int = 0

    # Context for current focus
    focus: Optional[str] = None
    related_nodes: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)

    # Summary
    summary: str = ""

    def to_context_dict(self) -> Dict[str, Any]:
        """Convert to context dict for cognitive kernel."""
        return {
            "akasha_loaded": self.is_loaded,
            "knowledge_nodes": self.node_count,
            "knowledge_edges": self.edge_count,
            "focus": self.focus,
            "related": self.related_nodes,
            "dependencies": self.dependencies,
            "constraints": self.constraints,
        }


# =============================================================================
# AkashaSense Implementation
# =============================================================================


class AkashaSense(BaseSense):
    """
    The 8th Jnanendriya - Knowledge Graph Perception.

    Perceives the knowledge graph state and provides pre-cognitive context.

    "Before Manas thinks, Akasha feels the vibrations of knowledge."

    Usage:
        sense = AkashaSense(workspace=Path.cwd())

        # Perceive current knowledge state
        perception = sense.perceive()
        print(f"Knowledge: {perception.node_count} nodes")

        # Perceive with focus
        perception = sense.perceive(context={"focus": "dharma"})
        print(f"Related to dharma: {perception.related_nodes}")
    """

    name = "akasha_sense"

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(workspace, config)

        # Lazy initialization of Akasha components
        self._port = None
        self._query = None

        logger.info("[AKASHA_SENSE] Initialized - The Eye of Knowledge")

    # =========================================================================
    # Lazy Initialization
    # =========================================================================

    @property
    def port(self):
        """Lazy-load AkashaPort."""
        if self._port is None:
            from .akasha import AkashaPort

            self._port = AkashaPort(workspace=self._workspace)
        return self._port

    @property
    def query(self):
        """Lazy-load AkashaQuery."""
        if self._query is None:
            from .akasha import AkashaQuery

            self._query = AkashaQuery(port=self.port)
        return self._query

    # =========================================================================
    # BaseSense Implementation
    # =========================================================================

    def perceive(self, context: Optional[Dict[str, Any]] = None) -> AkashaPerception:
        """
        Perceive the knowledge graph state.

        Args:
            context: Optional context with:
                - focus: Topic to focus on
                - depth: How deep to traverse dependencies

        Returns:
            AkashaPerception with knowledge state
        """
        context = context or {}
        focus = context.get("focus")
        depth = context.get("depth", 2)

        perception = AkashaPerception(
            is_loaded=self.port.is_loaded(),
            node_count=self.port.get_node_count(),
            edge_count=self.port.get_edge_count(),
            focus=focus,
        )

        # If focus provided, query for related knowledge
        if focus and self.port.is_loaded():
            try:
                result = self.query.what_is(focus)
                if result.found:
                    perception.related_nodes = [n.name for n in result.nodes]
                    perception.dependencies = [f"{d.source} -> {d.target}" for d in result.dependencies]
                    perception.constraints = result.constraints
                    perception.summary = f"Found {len(result.nodes)} nodes related to '{focus}'"
                else:
                    perception.summary = f"No knowledge found for '{focus}'"
            except Exception as e:
                logger.warning(f"[AKASHA_SENSE] Query failed: {e}")
                perception.summary = f"Query error: {e}"
        else:
            perception.summary = f"Knowledge graph: {perception.node_count} nodes, {perception.edge_count} edges"

        return perception

    def generate_intents(self, context: Optional[Dict[str, Any]] = None) -> List:
        """
        Generate knowledge-related intents.

        Currently returns empty list. Future: could generate intents like:
        - "Knowledge gap detected: no info about X"
        - "Stale knowledge: Y hasn't been updated in N days"
        """
        # Import here to avoid circular imports
        from vibe_core.plugins.opus_assistant.manas.intent_generator import (
            Intent,
            IntentPriority,
            IntentRisk,
        )

        intents: List[Intent] = []

        # Check if knowledge is loaded
        if not self.port.is_loaded():
            # Could generate intent to populate knowledge
            pass

        return intents

    # =========================================================================
    # Convenience Methods (Delegate to AkashaQuery)
    # =========================================================================

    def what_is(self, concept: str):
        """Query: What is X?"""
        return self.query.what_is(concept)

    def what_depends_on(self, node: str):
        """Query: What depends on X?"""
        return self.query.what_depends_on(node)

    def what_does_depend_on(self, node: str):
        """Query: What does X depend on?"""
        return self.query.what_does_depend_on(node)

    def get_constraints_for(self, domain: str):
        """Query: What constraints exist for domain X?"""
        return self.query.get_constraints_for(domain)


# =============================================================================
# Module-Level Convenience
# =============================================================================

_global_akasha_sense: Optional[AkashaSense] = None


def get_akasha_sense(workspace: Optional[Path] = None) -> AkashaSense:
    """Get or create global AkashaSense instance."""
    global _global_akasha_sense
    if _global_akasha_sense is None:
        _global_akasha_sense = AkashaSense(workspace=workspace)
    return _global_akasha_sense
