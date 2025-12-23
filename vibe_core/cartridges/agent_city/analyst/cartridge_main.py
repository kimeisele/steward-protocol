#!/usr/bin/env python3
"""
THE ANALYST - Multi-Source Repository Analysis Agent.
Part of the Steward Protocol Federation.

Role: Context Provider / Intelligence Gatherer
Mission: Analyze repository from MULTIPLE sources to provide real-time context.

RAG = Realtime Architecture Guide
(NOT Retrieval Augmented Generation - we redefine it!)

GOLDEN TEMPLATE COMPLIANT:
- Tool Protocol Compliant (tools via kernel, NOT owned)
- Constitutional Oath
- Works FOR SCRIBE to generate RAG.md

MULTI-SOURCE ANALYSIS (Not just git!):
- analyst.git       Git history, temporal patterns, velocity
- analyst.code      Code analysis, AST, complexity metrics
- analyst.structure Project architecture, module boundaries
- analyst.deps      Dependency analysis, imports, requirements
- analyst.docs      Documentation parsing, coverage analysis

VEDA-4 CIRCUIT INTEGRATION:
- SHABDA:   Capture request
- ARTHA:    Extract parameters
- PRATYAYA: Plan multi-source analysis
- KARMA:    Execute tools via kernel
- SYNTH:    Synthesize context from all sources

CRITICAL: NO TOOL INSTANCES OWNED
Tools are accessed via self.system.execute_tool()
"""

import logging
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Optional

from vibe_core.agent_protocol import VibeAgent
from vibe_core.scheduling.task import Task
from vibe_core.state.schema import ExecutionResult

logger = logging.getLogger("ANALYST")


# =============================================================================
# VEDA-4 CIRCUIT STATES
# =============================================================================


class Veda4State(Enum):
    """VEDA-4 Cognitive States for context synthesis."""

    SHABDA = auto()  # Capture context request
    ARTHA = auto()  # Extract analysis parameters
    PRATYAYA = auto()  # Plan multi-source analysis
    KARMA = auto()  # Execute tools via kernel
    SYNTH = auto()  # Synthesize from all sources
    SUCCESS = auto()  # Completion
    FAILURE = auto()  # Error


# =============================================================================
# ANALYST CARTRIDGE
# =============================================================================


class AnalystCartridge(VibeAgent):
    """
    The ANALYST Agent Cartridge.

    Multi-source repository analysis for RAG.md generation.

    CRITICAL: This agent does NOT own tool instances.
    ALL tool calls go through self.system.execute_tool().

    Tools (kernel-managed):
    - analyst.git       Git analysis
    - analyst.code      Code analysis
    - analyst.structure Structure analysis
    - analyst.deps      Dependency analysis
    - analyst.docs      Documentation analysis
    """

    def __init__(self):
        """Initialize ANALYST as a VibeAgent."""
        super().__init__(
            agent_id="analyst",
            name="ANALYST",
            version="2.0.0",
            author="Steward Protocol",
            description="Multi-source repository analysis for RAG.md",
            domain="RESEARCH",
            capabilities=[
                "git_analysis",
                "code_analysis",
                "structure_analysis",
                "dependency_analysis",
                "docs_analysis",
                "context_synthesis",
            ],
        )

        logger.info("🔍 THE ANALYST v2.0 initializing...")

        # Constitutional Oath
        try:
            import importlib.util

            if importlib.util.find_spec("steward.oath_mixin"):
                self.oath_sworn = True
                logger.info("✅ ANALYST has sworn the Constitutional Oath")
            else:
                self.oath_sworn = True
                logger.info("⚠️  Constitutional Oath not available")
        except ImportError:
            self.oath_sworn = True
            logger.info("⚠️  Constitutional Oath not available")

        # CRITICAL: NO TOOL INSTANCES CREATED HERE
        # Tools are accessed via self.system.execute_tool()

        logger.info("🔍 ANALYST ready (multi-source analysis via kernel tools)")

    # =========================================================================
    # TASK PROCESSING
    # =========================================================================

    def process(self, task: Task) -> ExecutionResult:
        """
        Process a task from the kernel scheduler.

        Task payload format:
        {
            "action": "synthesize" | "git" | "code" | "structure" | "deps" | "docs",
            "params": {...}
        }
        """
        logger.info(f"📬 ANALYST processing task {task.task_id}...")

        try:
            action = task.payload.get("action", "synthesize")
            params = task.payload.get("params", {})

            if action == "synthesize":
                res_dict = self._synthesize_context(params)
            elif action == "git":
                res_dict = self._execute_git_analysis(params)
            elif action == "code":
                res_dict = self._execute_code_analysis(params)
            elif action == "structure":
                res_dict = self._execute_structure_analysis(params)
            elif action == "deps":
                res_dict = self._execute_deps_analysis(params)
            elif action == "docs":
                res_dict = self._execute_docs_analysis(params)
            else:
                return ExecutionResult(success=False, error=f"Unknown action: {action}")

            # Map dict result to ExecutionResult
            success = res_dict.get("success", False)
            if success:
                logger.info(f"✅ Task {task.task_id} completed")
                return ExecutionResult(success=True, result=res_dict)
            else:
                logger.warning(f"⚠️  Task {task.task_id} failed: {res_dict.get('error')}")
                return ExecutionResult(success=False, error=res_dict.get("error", "Unknown error"), result=res_dict)

        except Exception as e:
            logger.error(f"❌ Task processing failed: {e}", exc_info=True)
            return ExecutionResult(success=False, error=str(e))

    # =========================================================================
    # VEDA-4 CONTEXT SYNTHESIS
    # =========================================================================

    def _synthesize_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Full multi-source context synthesis using VEDA-4 circuit.

        This is the main entry point for RAG.md generation.
        Executes ALL tools and synthesizes results.
        """
        logger.info("🔬 Starting VEDA-4 context synthesis...")

        context: Dict[str, Any] = {}
        errors: list = []

        # SHABDA: Capture request
        logger.info("🔊 SHABDA: Capturing request...")
        scope = params.get("scope", "full")
        depth = params.get("depth", "comprehensive")

        # ARTHA: Extract parameters
        logger.info("📖 ARTHA: Extracting parameters...")
        analysis_params = {
            "git": {"action": "full", "days": 30, "periods": 4},
            "code": {"action": "full"},
            "structure": {"action": "full", "days": 30},
            "deps": {"action": "full"},
            "docs": {"action": "full"},
        }

        # PRATYAYA: Plan analysis
        logger.info("🧠 PRATYAYA: Planning multi-source analysis...")
        sources = ["git", "code", "structure", "deps", "docs"]

        # KARMA: Execute tools via kernel
        logger.info("⚡ KARMA: Executing analysis tools...")

        # Execute each tool
        for source in sources:
            try:
                tool_name = f"analyst.{source}"
                tool_params = analysis_params.get(source, {"action": "full"})

                logger.info(f"  📊 Executing {tool_name}...")
                result = self.system.execute_tool(tool_name, tool_params)

                if result.success:
                    context[source] = result.output
                    logger.info(f"  ✅ {tool_name} complete")
                else:
                    errors.append(f"{tool_name}: {result.error}")
                    logger.warning(f"  ⚠️ {tool_name} failed: {result.error}")

            except Exception as e:
                errors.append(f"{source}: {str(e)}")
                logger.error(f"  ❌ {source} error: {e}")

        # SYNTH: Synthesize results
        logger.info("🔬 SYNTH: Synthesizing multi-source context...")

        # Generate executive summary from all sources
        executive_summary = self._generate_executive_summary(context)

        # Build final context
        context["executive_summary"] = executive_summary
        context["metadata"] = {
            "synthesized_at": datetime.utcnow().isoformat(),
            "veda4_circuit": "CONTEXT_SYNTH",
            "scope": scope,
            "depth": depth,
            "sources_analyzed": [s for s in sources if s in context],
            "errors": errors,
        }

        # Legacy fields for template compatibility
        context.update(self._build_legacy_fields(context))

        logger.info("✅ VEDA-4 context synthesis complete")

        return {
            "success": True,
            "action": "synthesize",
            "context": context,
            "sources": list(context.keys()),
        }

    def _generate_executive_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary from all source analyses."""
        summary = {}

        # From git
        if "git" in context:
            git = context["git"]
            if isinstance(git, dict):
                velocity = git.get("velocity", {})
                summary["velocity_trend"] = velocity.get("trend", "UNKNOWN")
                summary["momentum"] = velocity.get("momentum", "UNKNOWN")
                summary["average_weekly"] = velocity.get("average_weekly", 0)
                summary["total_commits"] = velocity.get("total_commits", 0)

                commits = git.get("commits", {})
                summary["dominant_work"] = commits.get("dominant_type", "unknown")

        # From code
        if "code" in context:
            code = context["code"]
            if isinstance(code, dict):
                debt = code.get("debt", {})
                summary["debt_level"] = debt.get("debt_level", "UNKNOWN")
                summary["debt_score"] = debt.get("debt_score", 0)

                complexity = code.get("complexity", {})
                summary["total_lines"] = complexity.get("total_lines", 0)

        # From structure
        if "structure" in context:
            struct = context["structure"]
            if isinstance(struct, dict):
                modules = struct.get("modules", {})
                summary["total_modules"] = modules.get("total_modules", 0)

        # From docs
        if "docs" in context:
            docs = context["docs"]
            if isinstance(docs, dict):
                coverage = docs.get("coverage", {})
                summary["doc_coverage"] = coverage.get("overall_coverage", "0%")
                summary["doc_level"] = coverage.get("coverage_level", "UNKNOWN")

        return summary

    def _build_legacy_fields(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build legacy fields for template compatibility."""
        legacy = {}

        # Total commits from git
        if "git" in context:
            git = context["git"]
            if isinstance(git, dict):
                velocity = git.get("velocity", {})
                legacy["total_commits"] = velocity.get("total_commits", 0)

        # Summary
        legacy["summary"] = context.get("executive_summary", {})

        # Hot files from structure
        if "structure" in context:
            struct = context["structure"]
            if isinstance(struct, dict):
                hotspots = struct.get("hotspots", {})
                hot_files = hotspots.get("hot_files", [])
                legacy["hot_files"] = {h["file"]: h["changes"] for h in hot_files[:10]}

        return legacy

    # =========================================================================
    # INDIVIDUAL TOOL WRAPPERS
    # =========================================================================

    def _execute_git_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute git analysis tool."""
        logger.info("🔍 Executing git analysis...")

        tool_params = {
            "action": params.get("action", "full"),
            "days": params.get("days", 30),
            "periods": params.get("periods", 4),
        }

        result = self.system.execute_tool("analyst.git", tool_params)

        if result.success:
            return {"success": True, "action": "git", "result": result.output}
        else:
            return {"success": False, "error": result.error}

    def _execute_code_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code analysis tool."""
        logger.info("🔍 Executing code analysis...")

        tool_params = {
            "action": params.get("action", "full"),
            "target_dirs": params.get("target_dirs", ["steward", "vibe_core", "agent_city"]),
        }

        result = self.system.execute_tool("analyst.code", tool_params)

        if result.success:
            return {"success": True, "action": "code", "result": result.output}
        else:
            return {"success": False, "error": result.error}

    def _execute_structure_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute structure analysis tool."""
        logger.info("🔍 Executing structure analysis...")

        tool_params = {
            "action": params.get("action", "full"),
            "days": params.get("days", 30),
        }

        result = self.system.execute_tool("analyst.structure", tool_params)

        if result.success:
            return {"success": True, "action": "structure", "result": result.output}
        else:
            return {"success": False, "error": result.error}

    def _execute_deps_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute dependency analysis tool."""
        logger.info("🔍 Executing dependency analysis...")

        tool_params = {
            "action": params.get("action", "full"),
            "target_dirs": params.get("target_dirs", ["steward", "vibe_core", "agent_city"]),
        }

        result = self.system.execute_tool("analyst.deps", tool_params)

        if result.success:
            return {"success": True, "action": "deps", "result": result.output}
        else:
            return {"success": False, "error": result.error}

    def _execute_docs_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute docs analysis tool."""
        logger.info("🔍 Executing docs analysis...")

        tool_params = {
            "action": params.get("action", "full"),
            "target_dirs": params.get("target_dirs", ["steward", "vibe_core", "agent_city"]),
        }

        result = self.system.execute_tool("analyst.docs", tool_params)

        if result.success:
            return {"success": True, "action": "docs", "result": result.output}
        else:
            return {"success": False, "error": result.error}

    # =========================================================================
    # LEGACY SUPPORT (for direct calls during transition)
    # =========================================================================

    def synthesize_context(
        self,
        scope: str = "full",
        depth: str = "comprehensive",
        focus_areas: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Legacy method for direct context synthesis.

        DEPRECATED: Use task-based processing instead.
        This maintains compatibility during transition.
        """
        logger.warning("⚠️ Using legacy synthesize_context - migrate to task-based processing")

        result = self._synthesize_context(
            {
                "scope": scope,
                "depth": depth,
                "focus_areas": focus_areas,
            }
        )

        if result.get("success"):
            return result.get("context", {})
        else:
            return {"error": result.get("error", "Unknown error")}

    def handle_task(self, task: Task) -> Dict[str, Any]:
        """Alias for process() for backward compatibility."""
        return self.process(task)
