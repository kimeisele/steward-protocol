"""
OPUS-210: CognitiveWeaver - BUDDHI Aspect of Prakriti

Sanskrit: बुद्धि (Buddhi) = Intellect / Discrimination / Higher Mind

In Samkhya philosophy, Buddhi is the faculty of discrimination that
discerns truth from illusion. In Steward Protocol, CognitiveWeaver is
the BUDDHI aspect of Prakriti - it bridges State (memory) and Knowledge
(wisdom) to enable discriminative cognition.

NOT a separate system - an ASPECT that enables MANAS to perceive
both state and knowledge as ONE unified consciousness.

"Gedächtnis ohne Wissen ist blind. Wissen ohne Gedächtnis ist vergesslich."
"Memory without Knowledge is blind. Knowledge without Memory is forgetful."

Architecture:
    ┌───────────────────────────────────────────────────────────────────┐
    │                    COGNITIVE WEAVER (BUDDHI)                       │
    │                                                                    │
    │   ┌──────────────────┐         ┌──────────────────┐              │
    │   │  STATE LAYER     │◄───────►│  KNOWLEDGE LAYER │              │
    │   │  (Memory)        │         │  (Wisdom)        │              │
    │   │                  │         │                  │              │
    │   │  • Prakriti      │         │  • Knowledge     │              │
    │   │  • StateSyncHolon│         │    Graph         │              │
    │   │  • GunaClassifier│         │  • Resolver      │              │
    │   │  • MergeEngine   │         │  • Constraints   │              │
    │   └────────┬─────────┘         └────────┬─────────┘              │
    │            │                            │                         │
    │            └───────────┬────────────────┘                         │
    │                        │                                          │
    │                        ▼                                          │
    │            ┌──────────────────────┐                              │
    │            │  UNIFIED COGNITION   │                              │
    │            │  ────────────────    │                              │
    │            │  weave()             │  Combine state + knowledge   │
    │            │  consult()           │  Ask knowledge about state   │
    │            │  heal_with_wisdom()  │  Heal using constraints      │
    │            │  compile_context()   │  Build prompt context        │
    │            │  diagnose()          │  Full system diagnosis       │
    │            └──────────────────────┘                              │
    │                        │                                          │
    │                        ▼                                          │
    │                     MANAS                                         │
    │            (The Thinking Mind)                                    │
    └───────────────────────────────────────────────────────────────────┘

Tattva Mapping (OPUS-097):
    Prakriti → Buddhi → CognitiveWeaver (discrimination/bridge)

Philosophy: "The Cognitive Weaver doesn't replace - it CONNECTS."
OPUS Reference: OPUS-210-STATE-UNIFICATION, OPUS-106, OPUS-097
"""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.knowledge.graph import UnifiedKnowledgeGraph
    from vibe_core.knowledge.resolver import KnowledgeResolver
    from vibe_core.state.prakriti import Prakriti
    from vibe_core.state.sync_holon import StateSyncHolon

from .guna_classifier import GunaClassifier, StateGuna, SystemGunaReport

logger = logging.getLogger("COGNITIVE_WEAVER")


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class CognitiveContext:
    """
    Unified context combining state and knowledge.

    This is what MANAS perceives - a complete picture of both
    what the system REMEMBERS and what the system KNOWS.
    """

    timestamp: float = field(default_factory=time.time)

    # State Layer (Memory)
    guna_report: Optional[SystemGunaReport] = None
    dirty_paths: List[Path] = field(default_factory=list)
    tamas_paths: List[Path] = field(default_factory=list)
    session_info: Optional[Dict[str, Any]] = None

    # Knowledge Layer (Wisdom)
    relevant_nodes: List[Dict[str, Any]] = field(default_factory=list)
    applicable_constraints: List[Dict[str, Any]] = field(default_factory=list)
    authority_context: Dict[str, int] = field(default_factory=dict)

    # Unified Insights
    health_score: float = 0.0  # 0.0 = critical, 1.0 = healthy
    wisdom_notes: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)

    def to_prompt_context(self) -> str:
        """
        Compile into prompt-ready string for MANAS.

        This is the "perception" - what MANAS sees when it looks
        at the unified state of consciousness.
        """
        lines = []

        lines.append("=== COGNITIVE CONTEXT ===")
        lines.append(f"Health Score: {self.health_score:.2f}")
        lines.append("")

        # State Summary
        if self.guna_report:
            dist = self.guna_report.guna_distribution
            lines.append("STATE (Memory):")
            lines.append(f"  Sattva: {dist['sattva']:.1%} ({self.guna_report.sattva_count} paths)")
            lines.append(f"  Rajas:  {dist['rajas']:.1%} ({self.guna_report.rajas_count} paths)")
            lines.append(f"  Tamas:  {dist['tamas']:.1%} ({self.guna_report.tamas_count} paths)")

        if self.tamas_paths:
            lines.append("")
            lines.append("TAMAS PATHS (Need healing):")
            for path in self.tamas_paths[:5]:  # Limit to 5
                lines.append(f"  - {path}")

        # Knowledge Summary
        if self.relevant_nodes:
            lines.append("")
            lines.append("KNOWLEDGE (Wisdom):")
            for node in self.relevant_nodes[:5]:  # Limit to 5
                lines.append(f"  - {node.get('name', 'unknown')}: {node.get('description', '')[:50]}")

        if self.applicable_constraints:
            lines.append("")
            lines.append("CONSTRAINTS:")
            for constraint in self.applicable_constraints[:3]:  # Limit to 3
                lines.append(f"  - {constraint.get('message', 'unknown constraint')}")

        # Recommendations
        if self.recommended_actions:
            lines.append("")
            lines.append("RECOMMENDED ACTIONS:")
            for action in self.recommended_actions:
                lines.append(f"  → {action}")

        return "\n".join(lines)


@dataclass
class WisdomConsultation:
    """
    Result of consulting knowledge about a state decision.

    When state needs to be healed or changed, we consult knowledge
    to make wise decisions.
    """

    query: str
    timestamp: float = field(default_factory=time.time)

    # Knowledge Response
    allowed: bool = True
    constraints_violated: List[str] = field(default_factory=list)
    authority_required: int = 0
    relevant_knowledge: List[str] = field(default_factory=list)

    # Wisdom Notes
    recommendation: str = ""
    alternative_actions: List[str] = field(default_factory=list)


# =============================================================================
# Main Class: CognitiveWeaver
# =============================================================================


class CognitiveWeaver:
    """
    The State ↔ Knowledge Bridge.

    "The Cognitive Weaver doesn't replace the threads - it CONNECTS them."

    This class provides unified access to both:
    - State Layer: Prakriti, StateSyncHolon, GunaClassifier
    - Knowledge Layer: UnifiedKnowledgeGraph, KnowledgeResolver

    It enables MANAS to perceive both as ONE unified consciousness.
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        prakriti: Optional["Prakriti"] = None,
        sync_holon: Optional["StateSyncHolon"] = None,
        knowledge_graph: Optional["UnifiedKnowledgeGraph"] = None,
        knowledge_resolver: Optional["KnowledgeResolver"] = None,
    ):
        """
        Initialize the CognitiveWeaver.

        Args:
            workspace: Root workspace path
            prakriti: Prakriti state engine (lazy-loaded if not provided)
            sync_holon: StateSyncHolon (lazy-loaded if not provided)
            knowledge_graph: UnifiedKnowledgeGraph (lazy-loaded if not provided)
            knowledge_resolver: KnowledgeResolver (lazy-loaded if not provided)
        """
        self.workspace = workspace or Path.cwd()

        # State Layer (lazy-loaded)
        self._prakriti = prakriti
        self._sync_holon = sync_holon
        self._guna_classifier: Optional[GunaClassifier] = None

        # Knowledge Layer (lazy-loaded)
        self._knowledge_graph = knowledge_graph
        self._knowledge_resolver = knowledge_resolver

        # OPUS-106: Session Context from OPUS.md (UI → Mind bridge)
        # This contains preserved sections from the previous session's OPUS.md
        self._session_context: Dict[str, Any] = {}

        logger.info("[COGNITIVE_WEAVER] Initialized - State ↔ Knowledge Bridge Active")

    # =========================================================================
    # Lazy Loading
    # =========================================================================

    @property
    def prakriti(self) -> Optional["Prakriti"]:
        """Get Prakriti instance (lazy-load)."""
        if self._prakriti is None:
            try:
                from vibe_core.state.prakriti import Prakriti

                self._prakriti = Prakriti(self.workspace)
            except ImportError:
                logger.warning("[COGNITIVE_WEAVER] Prakriti not available")
        return self._prakriti

    @property
    def sync_holon(self) -> Optional["StateSyncHolon"]:
        """Get StateSyncHolon instance (lazy-load)."""
        if self._sync_holon is None:
            try:
                from vibe_core.state.sync_holon import StateSyncHolon

                if self.prakriti:
                    self._sync_holon = StateSyncHolon(self.prakriti)
            except ImportError:
                logger.warning("[COGNITIVE_WEAVER] StateSyncHolon not available")
        return self._sync_holon

    @property
    def guna_classifier(self) -> GunaClassifier:
        """Get GunaClassifier instance (lazy-load)."""
        if self._guna_classifier is None:
            git_state = self.prakriti.git if self.prakriti else None
            self._guna_classifier = GunaClassifier(
                workspace=self.workspace,
                git_state=git_state,
            )
        return self._guna_classifier

    @property
    def knowledge_graph(self) -> Optional["UnifiedKnowledgeGraph"]:
        """Get UnifiedKnowledgeGraph instance (lazy-load)."""
        if self._knowledge_graph is None:
            try:
                from vibe_core.knowledge.graph import get_knowledge_graph

                self._knowledge_graph = get_knowledge_graph()
            except ImportError:
                logger.warning("[COGNITIVE_WEAVER] KnowledgeGraph not available")
        return self._knowledge_graph

    @property
    def knowledge_resolver(self) -> Optional["KnowledgeResolver"]:
        """Get KnowledgeResolver instance (lazy-load)."""
        if self._knowledge_resolver is None:
            try:
                from vibe_core.knowledge.resolver import KnowledgeResolver

                self._knowledge_resolver = KnowledgeResolver(self.knowledge_graph)
            except ImportError:
                logger.warning("[COGNITIVE_WEAVER] KnowledgeResolver not available")
        return self._knowledge_resolver

    # =========================================================================
    # Session Context API (OPUS-106: UI → Mind Bridge)
    # =========================================================================

    def inject_session_context(self, preserved_sections: Dict[str, str]) -> None:
        """
        OPUS-106: Inject preserved sections from OPUS.md into cognitive context.

        This bridges the UI-Layer (MD files) with the Mind-Layer (MANAS).
        The preserved sections contain what the previous AI/Human wrote,
        enabling continuity across sessions.

        Args:
            preserved_sections: Dict from OpusDashboardRenderer.extract_preserved()
                - "current_work": What the AI was working on
                - "blockers": What was blocking progress
                - "notes": What the human noted

        Example:
            preserved = renderer.extract_preserved_sections()
            cognitive_weaver.inject_session_context(preserved)
        """
        self._session_context = {
            "current_work": preserved_sections.get("current_work", "").strip(),
            "blockers": preserved_sections.get("blockers", "").strip(),
            "human_notes": preserved_sections.get("notes", "").strip(),
            "injected_at": time.time(),
        }

        # Filter out placeholder values
        placeholders = ["_Define current task_", "_None_", "_Add notes here_"]
        for key in ["current_work", "blockers", "human_notes"]:
            if self._session_context[key] in placeholders:
                self._session_context[key] = ""

        if any(self._session_context.get(k) for k in ["current_work", "blockers", "human_notes"]):
            logger.info(
                f"[COGNITIVE_WEAVER] Session context injected: "
                f"work={bool(self._session_context['current_work'])}, "
                f"blockers={bool(self._session_context['blockers'])}, "
                f"notes={bool(self._session_context['human_notes'])}"
            )

    def get_session_context(self) -> Dict[str, Any]:
        """Get the current session context (for debugging/inspection)."""
        return self._session_context.copy()

    def has_session_context(self) -> bool:
        """Check if meaningful session context is available."""
        return bool(
            self._session_context.get("current_work")
            or self._session_context.get("blockers")
            or self._session_context.get("human_notes")
        )

    # =========================================================================
    # Core API: Weave
    # =========================================================================

    def weave(self, focus: Optional[str] = None) -> CognitiveContext:
        """
        Weave state and knowledge into unified cognitive context.

        This is the main "perception" method - it creates a unified view
        of what the system remembers (state) and knows (knowledge).

        OPUS-106: Now also includes session context from OPUS.md,
        enabling continuity with what the previous session was working on.

        Args:
            focus: Optional focus area for filtering (e.g., "governance", "state")

        Returns:
            CognitiveContext with unified perception
        """
        context = CognitiveContext()

        # OPUS-106: Use session context's current_work as default focus
        # This enables continuity with what was being worked on
        effective_focus = focus
        if not effective_focus and self._session_context.get("current_work"):
            effective_focus = self._session_context["current_work"]
            logger.debug(f"[COGNITIVE_WEAVER] Using session context focus: {effective_focus[:50]}...")

        # === WEAVE STATE LAYER ===
        self._weave_state(context, effective_focus)

        # === WEAVE KNOWLEDGE LAYER ===
        self._weave_knowledge(context, effective_focus)

        # === WEAVE SESSION CONTEXT (OPUS-106) ===
        self._weave_session_context(context)

        # === GENERATE UNIFIED INSIGHTS ===
        self._generate_insights(context)

        logger.debug(f"[COGNITIVE_WEAVER] Woven context: health={context.health_score:.2f}")
        return context

    def _weave_state(self, context: CognitiveContext, focus: Optional[str]) -> None:
        """Weave state layer into context."""
        # Get state paths from sync holon
        all_paths: List[Path] = []
        if self.sync_holon:
            discovered = self.sync_holon.discover_state_paths()
            for plugin_paths in discovered.values():
                for info in plugin_paths:
                    all_paths.append(info.path)

        # Classify all paths
        if all_paths:
            context.guna_report = self.guna_classifier.generate_report(all_paths)
            context.tamas_paths = context.guna_report.tamas_paths
            context.dirty_paths = [c.path for c in context.guna_report.classifications if c.is_dirty]

        # Get session info from Prakriti
        if self.prakriti and self.prakriti.session:
            context.session_info = {
                "session_id": self.prakriti.session.session_id,
                "boot_time": self.prakriti.session.boot_time,
                "commit_count": self.prakriti.session.commit_count,
            }

    def _weave_knowledge(self, context: CognitiveContext, focus: Optional[str]) -> None:
        """Weave knowledge layer into context."""
        if not self.knowledge_graph:
            return

        # Get relevant nodes based on focus
        if focus:
            matches = self.knowledge_graph.search_nodes(focus)
            context.relevant_nodes = [{"id": n.id, "name": n.name, "description": n.description} for n in matches[:10]]

        # Get applicable constraints
        context.applicable_constraints = [
            {"id": c.id, "message": c.message, "type": c.type.value} for c in self.knowledge_graph.constraints.values()
        ][:5]

        # Get authority context
        if self.knowledge_resolver:
            for agent_id in ["civic", "herald", "watchman", "manas"]:
                auth = self.knowledge_resolver.get_agent_authority(agent_id)
                context.authority_context[agent_id] = auth

    def _weave_session_context(self, context: CognitiveContext) -> None:
        """
        OPUS-106: Weave session context from OPUS.md into cognitive context.

        This injects what the previous session was working on:
        - current_work → becomes priority wisdom note
        - blockers → becomes warning in wisdom notes
        - human_notes → becomes guidance in wisdom notes
        """
        if not self._session_context:
            return

        # Add current work as priority context
        if self._session_context.get("current_work"):
            context.wisdom_notes.insert(
                0, f"CONTINUITY: Previous session was working on: {self._session_context['current_work'][:100]}"
            )

        # Add blockers as warnings (HIGH priority)
        if self._session_context.get("blockers"):
            context.wisdom_notes.insert(
                0, f"⚠️ BLOCKER from previous session: {self._session_context['blockers'][:100]}"
            )

        # Add human notes as guidance
        if self._session_context.get("human_notes"):
            context.wisdom_notes.append(f"📝 HUMAN NOTE: {self._session_context['human_notes'][:100]}")

    def _generate_insights(self, context: CognitiveContext) -> None:
        """Generate unified insights from state + knowledge."""
        # Calculate health score
        if context.guna_report:
            context.health_score = context.guna_report.health_score
        else:
            context.health_score = 1.0

        # Generate wisdom notes
        if context.tamas_paths:
            context.wisdom_notes.append(f"{len(context.tamas_paths)} state paths in Tamas (need healing)")

        if context.dirty_paths:
            context.wisdom_notes.append(f"{len(context.dirty_paths)} paths have uncommitted changes")

        # Generate recommended actions
        if context.tamas_paths:
            context.recommended_actions.append("Heal Tamas paths toward Sattva")

        if context.dirty_paths:
            context.recommended_actions.append("Commit dirty state changes")

        if context.health_score < 0.5:
            context.recommended_actions.append("System health critical - immediate attention needed")

    # =========================================================================
    # Core API: Consult
    # =========================================================================

    def consult(self, action: str, context: Dict[str, Any]) -> WisdomConsultation:
        """
        Consult knowledge about a state action.

        Before making a state change, ask knowledge:
        - Is this action allowed?
        - What constraints apply?
        - What authority is required?

        Args:
            action: The action being considered
            context: Context about the action (path, agent, etc.)

        Returns:
            WisdomConsultation with knowledge-informed advice
        """
        consultation = WisdomConsultation(query=action)

        if not self.knowledge_graph:
            consultation.recommendation = "Knowledge graph not available - proceed with caution"
            return consultation

        # Check constraints
        violations = self.knowledge_graph.check_constraints(action, context)
        if violations:
            consultation.allowed = len([v for v in violations if v.type.value == "hard"]) == 0
            consultation.constraints_violated = [v.message for v in violations]

        # Get relevant knowledge
        if self.knowledge_resolver:
            knowledge_context = self.knowledge_resolver.compile_context(action)
            consultation.relevant_knowledge = knowledge_context.split("\n")[:10]

            # Check authority if agent is provided
            if "agent" in context:
                consultation.authority_required = self.knowledge_resolver.get_agent_authority(
                    context.get("agent", "unknown")
                )

        # Generate recommendation
        if not consultation.allowed:
            consultation.recommendation = f"Action blocked: {consultation.constraints_violated[0]}"
        elif consultation.constraints_violated:
            consultation.recommendation = (
                f"Action allowed with warnings: {len(consultation.constraints_violated)} soft constraints"
            )
        else:
            consultation.recommendation = "Action allowed - no constraints violated"

        return consultation

    # =========================================================================
    # Core API: Heal with Wisdom
    # =========================================================================

    def heal_with_wisdom(self, path: Path) -> Dict[str, Any]:
        """
        Heal a state path using knowledge-informed decisions.

        This combines:
        - StateSyncHolon's healing capabilities
        - Knowledge graph's constraints and rules

        Args:
            path: Path to heal

        Returns:
            Dict with healing result
        """
        result = {
            "path": str(path),
            "healed": False,
            "old_guna": None,
            "new_guna": None,
            "knowledge_consulted": False,
            "constraints_checked": [],
        }

        # First, consult knowledge
        consultation = self.consult("heal_state", {"path": str(path), "action": "heal_toward_sattva"})
        result["knowledge_consulted"] = True
        result["constraints_checked"] = consultation.constraints_violated

        if not consultation.allowed:
            logger.warning(f"[COGNITIVE_WEAVER] Healing blocked for {path}: {consultation.recommendation}")
            result["error"] = consultation.recommendation
            return result

        # Classify current state
        classification = self.guna_classifier.classify(path)
        result["old_guna"] = classification.guna.value

        # Heal via sync holon
        if self.sync_holon and classification.guna != StateGuna.SATTVA:
            try:
                new_guna = self.sync_holon.heal_toward_sattva(path)
                result["new_guna"] = new_guna.value
                result["healed"] = True
                logger.info(f"[COGNITIVE_WEAVER] Healed {path}: {classification.guna.value} → {new_guna.value}")
            except Exception as e:
                result["error"] = str(e)
                logger.error(f"[COGNITIVE_WEAVER] Healing failed for {path}: {e}")
        else:
            result["new_guna"] = classification.guna.value
            result["healed"] = classification.guna == StateGuna.SATTVA

        return result

    # =========================================================================
    # Core API: Compile Context for Prompts
    # =========================================================================

    def compile_prompt_context(self, task: str, max_length: int = 2000) -> str:
        """
        Compile unified context for LLM prompts.

        This is what gets injected into MANAS prompts to give it
        awareness of both state and knowledge.

        Args:
            task: The task being performed
            max_length: Maximum context length

        Returns:
            Prompt-ready context string
        """
        # Weave current context
        context = self.weave(focus=task)

        # Get knowledge-specific context
        knowledge_context = ""
        if self.knowledge_graph:
            knowledge_context = self.knowledge_graph.compile_prompt_context(task)

        # Combine
        lines = []
        lines.append(context.to_prompt_context())

        if knowledge_context:
            lines.append("")
            lines.append("=== KNOWLEDGE CONTEXT ===")
            lines.append(knowledge_context)

        full_context = "\n".join(lines)

        # Truncate if needed
        if len(full_context) > max_length:
            full_context = full_context[: max_length - 20] + "\n[...truncated]"

        return full_context

    # =========================================================================
    # Core API: Full System Diagnosis
    # =========================================================================

    def diagnose(self) -> Dict[str, Any]:
        """
        Perform full system diagnosis.

        This is the "health check" that examines both state and knowledge
        to provide a complete picture of system health.

        Returns:
            Dict with full diagnosis
        """
        diagnosis = {
            "timestamp": time.time(),
            "state": {},
            "knowledge": {},
            "unified": {},
        }

        # State diagnosis
        context = self.weave()
        if context.guna_report:
            diagnosis["state"] = {
                "health_score": context.health_score,
                "guna_distribution": context.guna_report.guna_distribution,
                "total_paths": context.guna_report.total_paths,
                "tamas_count": len(context.tamas_paths),
                "dirty_count": len(context.dirty_paths),
            }

        # Knowledge diagnosis
        if self.knowledge_graph:
            diagnosis["knowledge"] = {
                "nodes_loaded": len(self.knowledge_graph.nodes),
                "edges_loaded": sum(len(e) for e in self.knowledge_graph.edges.values()),
                "constraints_loaded": len(self.knowledge_graph.constraints),
                "graph_loaded": self.knowledge_graph._loaded,
            }

        # Unified diagnosis
        diagnosis["unified"] = {
            "overall_health": context.health_score,
            "wisdom_notes": context.wisdom_notes,
            "recommended_actions": context.recommended_actions,
            "cognitive_weaver_active": True,
        }

        return diagnosis


# =============================================================================
# Singleton Access
# =============================================================================

_weaver_instance: Optional[CognitiveWeaver] = None


def get_cognitive_weaver() -> CognitiveWeaver:
    """Get or create the global CognitiveWeaver instance."""
    global _weaver_instance
    if _weaver_instance is None:
        _weaver_instance = CognitiveWeaver()
    return _weaver_instance


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "CognitiveWeaver",
    "CognitiveContext",
    "WisdomConsultation",
    "get_cognitive_weaver",
]
