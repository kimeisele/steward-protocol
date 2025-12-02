"""
THE ANALYST - Repository Analysis & Context Synthesis Agent.
Part of the Steward Protocol Federation.

Role: Context Provider / Intelligence Gatherer
Mission: Analyze repository to provide real-time context for agents.

RAG = Realtime Architecture Guide
(NOT Retrieval Augmented Generation - we redefine it!)

GOLDEN TEMPLATE COMPLIANT:
- Tool Protocol Compliant (tools via kernel)
- Constitutional Oath
- Works FOR SCRIBE to generate RAG.md

4D ANALYSIS (Multi-Dimensional):
- TEMPORAL:    Time-based patterns, velocity trends
- STRUCTURAL:  Dependencies, coupling, architecture
- SEMANTIC:    Work classification, complexity, intent
- PREDICTIVE:  Related files, risk areas, recommendations

VEDA-4 CIRCUIT INTEGRATION:
- SHABDA:   Capture request
- ARTHA:    Extract parameters
- PRATYAYA: Identify data sources
- KARMA:    Execute analysis
- SYNTH:    Synthesize context
"""

import logging
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, Optional

# Constitutional Oath Mixin (Golden Template Pattern)
from steward.oath_mixin import OathMixin

# VibeOS Integration
from vibe_core import Task, VibeAgent

# Multi-Dimensional Analysis Engine
from .dimensions import (
    GitInterface,
    MultiDimensionalSynthesizer,
    PredictiveDimension,
    SemanticDimension,
    StructuralDimension,
    TemporalDimension,
)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ANALYST_AGENT")


# =============================================================================
# VEDA-4 CIRCUIT STATES
# =============================================================================


class Veda4State(Enum):
    """
    VEDA-4 Cognitive States for context synthesis.

    These states represent the semantic progression of analysis:
    - SHABDA:   Sound/Input - Capture the request
    - ARTHA:    Meaning - Extract what's needed
    - PRATYAYA: Cognition - Plan the approach
    - KARMA:    Action - Execute analysis
    - SYNTH:    Synthesis - Combine dimensions
    - SUCCESS:  Completion
    - FAILURE:  Error state
    """

    SHABDA = auto()  # Capture context request
    ARTHA = auto()  # Extract analysis parameters
    PRATYAYA = auto()  # Plan data source access
    KARMA = auto()  # Execute dimensional analysis
    SYNTH = auto()  # Synthesize multi-dimensional context
    SUCCESS = auto()  # Final success state
    FAILURE = auto()  # Error state


class Veda4Circuit:
    """
    VEDA-4 Circuit Implementation for ANALYST.

    Provides semantic state machine for context synthesis.
    Each state transition carries invariants and validation.
    """

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.state = Veda4State.SHABDA
        self.context: Dict[str, Any] = {}
        self.params: Dict[str, Any] = {}
        self.errors: list = []

        # Initialize git interface
        self.git = GitInterface(str(self.root_dir))

    def transition(self, target: Veda4State, **kwargs) -> bool:
        """
        Transition to target state.

        Returns True if transition successful, False otherwise.
        """
        logger.info(f"📊 VEDA-4: {self.state.name} → {target.name}")
        self.state = target
        return True

    # -------------------------------------------------------------------------
    # State Handlers
    # -------------------------------------------------------------------------

    def execute_shabda(
        self,
        scope: str = "full",
        depth: str = "comprehensive",
        focus_areas: Optional[list] = None,
    ) -> bool:
        """
        SHABDA: Capture context request and scope.

        Invariants:
        - Scope must be valid
        - Request must be captured
        """
        logger.info("🔊 SHABDA: Capturing context request...")

        valid_scopes = ["short_term", "mid_term", "long_term", "full"]
        if scope not in valid_scopes:
            self.errors.append(f"Invalid scope: {scope}")
            return self.transition(Veda4State.FAILURE)

        self.params = {
            "scope": scope,
            "depth": depth,
            "focus_areas": focus_areas or [],
            "request_time": datetime.utcnow().isoformat(),
        }

        return self.transition(Veda4State.ARTHA)

    def execute_artha(self) -> bool:
        """
        ARTHA: Extract analysis parameters.

        Invariants:
        - Analysis parameters must be configured
        - Time ranges must be set
        """
        logger.info("📖 ARTHA: Extracting analysis parameters...")

        scope = self.params.get("scope", "full")

        # Configure time ranges based on scope
        if scope == "short_term":
            self.params["git_depth_days"] = 7
        elif scope == "mid_term":
            self.params["git_depth_days"] = 30
        elif scope == "long_term":
            self.params["git_depth_days"] = 90
        else:  # full
            self.params["git_depth_days"] = 90

        # Configure analysis targets
        self.params["analysis_config"] = {
            "temporal": True,
            "structural": True,
            "semantic": True,
            "predictive": True,
            "churn_limit": 20,
            "dependency_depth": 3,
        }

        return self.transition(Veda4State.PRATYAYA)

    def execute_pratyaya(self) -> bool:
        """
        PRATYAYA: Identify data sources and plan analysis.

        Invariants:
        - Git repository must be accessible
        - Analysis plan must be complete
        """
        logger.info("🧠 PRATYAYA: Planning analysis approach...")

        # Verify git access
        try:
            self.git.run("status")
        except Exception as e:
            self.errors.append(f"Git access failed: {e}")
            return self.transition(Veda4State.FAILURE)

        # Verify repository structure
        if not self.root_dir.exists():
            self.errors.append(f"Root directory not found: {self.root_dir}")
            return self.transition(Veda4State.FAILURE)

        # Plan analysis stages
        self.params["analysis_plan"] = [
            "temporal_dimension",
            "structural_dimension",
            "semantic_dimension",
            "predictive_dimension",
        ]

        return self.transition(Veda4State.KARMA)

    def execute_karma(self) -> bool:
        """
        KARMA: Execute multi-dimensional analysis.

        This is where the actual work happens.
        Each dimension is analyzed independently.

        Invariants:
        - Analysis must complete successfully
        - Results must contain all dimensions
        """
        logger.info("⚡ KARMA: Executing multi-dimensional analysis...")

        config = self.params.get("analysis_config", {})

        try:
            # Temporal Dimension
            if config.get("temporal", True):
                logger.info("  📅 Analyzing temporal dimension...")
                temporal = TemporalDimension(self.git)
                self.context["temporal"] = temporal.synthesize()

            # Structural Dimension
            if config.get("structural", True):
                logger.info("  🏗️ Analyzing structural dimension...")
                structural = StructuralDimension(self.git, str(self.root_dir))
                self.context["structural"] = structural.synthesize()

            # Semantic Dimension
            if config.get("semantic", True):
                logger.info("  📝 Analyzing semantic dimension...")
                semantic = SemanticDimension(self.git, str(self.root_dir))
                self.context["semantic"] = semantic.synthesize()

            # Predictive Dimension (uses other dimensions)
            if config.get("predictive", True):
                logger.info("  🔮 Analyzing predictive dimension...")
                predictive = PredictiveDimension(self.git, str(self.root_dir))
                self.context["predictive"] = predictive.synthesize(self.context)

        except Exception as e:
            self.errors.append(f"Analysis failed: {e}")
            return self.transition(Veda4State.FAILURE)

        return self.transition(Veda4State.SYNTH)

    def execute_synth(self) -> bool:
        """
        SYNTH: Synthesize multi-dimensional context for RAG.md.

        Combines all dimensions into unified output.

        Invariants:
        - Context must be formatted
        - Output must be ready for SCRIBE
        """
        logger.info("🔬 SYNTH: Synthesizing multi-dimensional context...")

        # Add metadata
        self.context["metadata"] = {
            "synthesized_at": datetime.utcnow().isoformat(),
            "veda4_circuit": "CONTEXT_SYNTH",
            "scope": self.params.get("scope", "full"),
            "depth": self.params.get("depth", "comprehensive"),
            "dimensions": list(self.context.keys()),
            "root_dir": str(self.root_dir),
        }

        # Generate executive summary
        self.context["executive_summary"] = self._generate_summary()

        # Legacy compatibility fields (for existing template)
        self._add_legacy_fields()

        return self.transition(Veda4State.SUCCESS)

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate executive summary from all dimensions."""
        summary = {}

        # From temporal
        if "temporal" in self.context:
            velocity = self.context["temporal"].get("velocity_trend", {})
            summary["velocity_trend"] = velocity.get("trend", "UNKNOWN")
            summary["momentum"] = velocity.get("momentum", "")
            summary["average_weekly"] = velocity.get("average_weekly", 0)

        # From semantic
        if "semantic" in self.context:
            commits = self.context["semantic"].get("commit_types", {})
            summary["dominant_work"] = commits.get("dominant_type", "unknown")
            summary["work_distribution"] = commits.get("percentages", {})

            debt = self.context["semantic"].get("technical_debt", {})
            summary["debt_level"] = debt.get("debt_level", "UNKNOWN")

        # From predictive
        if "predictive" in self.context:
            stability = self.context["predictive"].get("stability", {})
            summary["stability"] = stability.get("stability", "UNKNOWN")
            summary["stability_indicator"] = stability.get("indicator", "")

            focus = self.context["predictive"].get("focus_suggestions", {})
            summary["suggestions"] = focus.get("suggestions", [])
            summary["priorities"] = focus.get("priorities", [])

        return summary

    def _add_legacy_fields(self) -> None:
        """Add legacy fields for backward compatibility with existing template."""
        # Get git data for legacy format
        try:
            total_commits = int(self.git.run("rev-list --count HEAD") or "0")
        except Exception:
            total_commits = 0

        # Build legacy timeline structure from temporal dimension
        temporal = self.context.get("temporal", {})
        velocity = temporal.get("velocity_trend", {})
        bursts = temporal.get("activity_bursts", {})

        self.context["total_commits"] = total_commits

        # Legacy timeline (simplified view)
        self.context["timeline"] = {
            "short_term": {
                "period_days": 7,
                "total_commits": velocity.get("weekly_counts", [0])[0] if velocity.get("weekly_counts") else 0,
                "recent_commits": [],  # Would need additional fetch
                "hot_files": {},
                "module_activity": {},
            },
            "mid_term": {
                "period_days": 30,
                "total_commits": sum(velocity.get("weekly_counts", [])[:4]),
                "module_activity": {},
            },
            "long_term": {
                "period_days": 90,
                "total_commits": total_commits,  # Approximation
                "module_activity": {},
            },
        }

        # Legacy summary (from executive summary)
        exec_summary = self.context.get("executive_summary", {})
        self.context["summary"] = {
            "velocity_7d": velocity.get("weekly_counts", [0])[0] if velocity.get("weekly_counts") else 0,
            "velocity_30d": sum(velocity.get("weekly_counts", [])[:4]),
            "active_modules": [],
            "focus_areas": exec_summary.get("priorities", []),
        }

        # Legacy hot_files (from structural)
        structural = self.context.get("structural", {})
        coupling = structural.get("co_changes", {}).get("coupling_hotspots", [])
        self.context["hot_files"] = {file: score for file, score in coupling[:10]}

        # Legacy connections (simplified)
        self.context["connections"] = []

    # -------------------------------------------------------------------------
    # Main Execution
    # -------------------------------------------------------------------------

    def run(
        self,
        scope: str = "full",
        depth: str = "comprehensive",
        focus_areas: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Run the full VEDA-4 circuit.

        Returns synthesized multi-dimensional context.
        """
        logger.info("🚀 VEDA-4 Circuit: CONTEXT_SYNTH starting...")

        # Execute state machine
        if not self.execute_shabda(scope, depth, focus_areas):
            return {"status": "error", "errors": self.errors, "state": self.state.name}

        if not self.execute_artha():
            return {"status": "error", "errors": self.errors, "state": self.state.name}

        if not self.execute_pratyaya():
            return {"status": "error", "errors": self.errors, "state": self.state.name}

        if not self.execute_karma():
            return {"status": "error", "errors": self.errors, "state": self.state.name}

        if not self.execute_synth():
            return {"status": "error", "errors": self.errors, "state": self.state.name}

        logger.info("✅ VEDA-4 Circuit: CONTEXT_SYNTH complete")

        return {
            "status": "success",
            "state": self.state.name,
            "context": self.context,
        }


# =============================================================================
# ANALYST CARTRIDGE
# =============================================================================


class AnalystCartridge(VibeAgent, OathMixin):
    """
    The Analyst Agent Cartridge.
    Specialized in repository analysis and context synthesis.

    RAG = Realtime Architecture Guide

    Provides 4D Analysis:
    - TEMPORAL:    Time-based patterns, velocity trends
    - STRUCTURAL:  Dependencies, coupling, architecture
    - SEMANTIC:    Work classification, complexity, intent
    - PREDICTIVE:  Related files, risk areas, recommendations

    Uses VEDA-4 Circuit for semantic state machine execution.
    """

    def __init__(self, root_dir: str = "."):
        """Initialize the Analyst as a VibeAgent."""
        super().__init__(
            agent_id="analyst",
            name="ANALYST",
            version="2.0.0",
            author="Steward Protocol",
            description="4D Repository Analysis & Context Synthesis",
            domain="RESEARCH",
            capabilities=[
                "git_analysis",
                "dependency_analysis",
                "context_synthesis",
                "temporal_analysis",
                "structural_analysis",
                "semantic_analysis",
                "predictive_analysis",
            ],
        )

        self.root_dir = Path(root_dir).resolve()
        logger.info("🔍 THE ANALYST v2.0 is online (4D Analysis Engine)")

        # Golden Template Pattern: Initialize Constitutional Oath
        self.oath_mixin_init(self.agent_id)
        self.oath_sworn = True
        logger.info("✅ ANALYST has sworn the Constitutional Oath")

        # Initialize multi-dimensional synthesizer
        self.synthesizer = MultiDimensionalSynthesizer(str(self.root_dir))

        logger.info("✅ ANALYST: Ready for 4D context synthesis")

    # =========================================================================
    # MAIN SYNTHESIS (VEDA-4 Circuit)
    # =========================================================================

    def synthesize_context(
        self,
        scope: str = "full",
        depth: str = "comprehensive",
        focus_areas: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Synthesize full multi-dimensional context for RAG.md.

        Uses VEDA-4 Circuit for semantic state machine execution.

        Args:
            scope: Analysis scope (short_term, mid_term, long_term, full)
            depth: Analysis depth (quick, standard, comprehensive)
            focus_areas: Optional list of areas to focus on

        Returns:
            Complete 4D context dictionary ready for SCRIBE
        """
        logger.info("🔍 ANALYST: Starting 4D context synthesis...")

        # Execute VEDA-4 circuit
        circuit = Veda4Circuit(str(self.root_dir))
        result = circuit.run(scope=scope, depth=depth, focus_areas=focus_areas)

        if result["status"] == "success":
            logger.info("✅ ANALYST: 4D context synthesis complete")
            return result["context"]
        else:
            logger.error(f"❌ ANALYST: Synthesis failed at {result['state']}")
            return {
                "error": result.get("errors", ["Unknown error"]),
                "state": result["state"],
            }

    def quick_insights(self) -> Dict[str, Any]:
        """
        Generate quick high-level insights.

        For rapid context without full analysis.
        """
        return self.synthesizer.quick_insights()

    # =========================================================================
    # DIMENSIONAL ACCESS (Direct access to individual dimensions)
    # =========================================================================

    def analyze_temporal(self) -> Dict[str, Any]:
        """Direct access to temporal dimension."""
        return self.synthesizer.temporal.synthesize()

    def analyze_structural(self) -> Dict[str, Any]:
        """Direct access to structural dimension."""
        return self.synthesizer.structural.synthesize()

    def analyze_semantic(self) -> Dict[str, Any]:
        """Direct access to semantic dimension."""
        return self.synthesizer.semantic.synthesize()

    def analyze_predictive(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Direct access to predictive dimension."""
        if context is None:
            context = {}
        return self.synthesizer.predictive.synthesize(context)

    # =========================================================================
    # TASK HANDLER (VibeAgent Protocol)
    # =========================================================================

    def handle_task(self, task: Task) -> Dict[str, Any]:
        """
        Handle incoming tasks (VibeAgent protocol).

        Supported actions:
        - synthesize:  Full 4D context synthesis (VEDA-4 circuit)
        - quick:       Quick insights only
        - temporal:    Temporal dimension only
        - structural:  Structural dimension only
        - semantic:    Semantic dimension only
        - predictive:  Predictive dimension only
        """
        action = task.payload.get("action", "synthesize")
        logger.info(f"🔍 ANALYST received task: {action}")

        try:
            if action == "synthesize":
                scope = task.payload.get("scope", "full")
                depth = task.payload.get("depth", "comprehensive")
                focus = task.payload.get("focus_areas", None)
                return {
                    "status": "success",
                    "result": self.synthesize_context(scope=scope, depth=depth, focus_areas=focus),
                }

            elif action == "quick":
                return {
                    "status": "success",
                    "result": self.quick_insights(),
                }

            elif action == "temporal":
                return {
                    "status": "success",
                    "result": self.analyze_temporal(),
                }

            elif action == "structural":
                return {
                    "status": "success",
                    "result": self.analyze_structural(),
                }

            elif action == "semantic":
                return {
                    "status": "success",
                    "result": self.analyze_semantic(),
                }

            elif action == "predictive":
                return {
                    "status": "success",
                    "result": self.analyze_predictive(),
                }

            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}",
                }

        except Exception as e:
            logger.error(f"❌ ANALYST task failed: {e}")
            return {
                "status": "error",
                "error": str(e),
            }


# For direct testing
if __name__ == "__main__":
    analyst = AnalystCartridge()

    print("\n" + "=" * 60)
    print("🔍 ANALYST 4D CONTEXT SYNTHESIS")
    print("=" * 60)

    # Quick insights first
    print("\n📊 QUICK INSIGHTS:")
    quick = analyst.quick_insights()
    for key, value in quick.items():
        print(f"  {key}: {value}")

    # Full synthesis
    print("\n🔬 FULL 4D SYNTHESIS:")
    context = analyst.synthesize_context()

    if "error" not in context:
        summary = context.get("executive_summary", {})
        print(f"\n  Velocity: {summary.get('velocity_trend', 'N/A')} {summary.get('momentum', '')}")
        print(f"  Stability: {summary.get('stability', 'N/A')} {summary.get('stability_indicator', '')}")
        print(f"  Debt Level: {summary.get('debt_level', 'N/A')}")
        print(f"  Dominant Work: {summary.get('dominant_work', 'N/A')}")

        if summary.get("suggestions"):
            print("\n  💡 Suggestions:")
            for s in summary["suggestions"]:
                print(f"    - {s}")

        if summary.get("priorities"):
            print("\n  🎯 Priorities:")
            for p in summary["priorities"]:
                print(f"    - {p}")
    else:
        print(f"  ❌ Error: {context.get('error')}")

    print("\n" + "=" * 60)
