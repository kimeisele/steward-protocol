"""
CognitionRenderer: Dynamic COGNITION.md Dashboard

Renders live cognitive cycle data from CycleRegistry into markdown.
Provides visibility into:
- Active orchestration cycles (Boot → Prana → Plugins)
- Completed cycle history (last 50)
- Memory safety status (retention policy enforcement)
- Phase metrics (timing per phase)
- System health (error tracking)

Uses generate_content() pattern with dirty tracking (Law 3).
Sections are config-driven from interface.yaml.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from vibe_core.io_service import DocumentType
from vibe_core.orchestration_cycle import get_cycle_registry

from .base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.loaders import ActionLoader, AnalyzerLoader, SenseLoader, ToolLoader

logger = logging.getLogger("RENDERER_COGNITION")


class CognitionRenderer(BaseRenderer):
    """Renders COGNITION.md with live cycle data from CycleRegistry.

    OPUS-107: The Cognitive Mirror
        - Shows live orchestration cycles (CycleRegistry)
        - Shows Arsenal (VEDA-4 loaders): Tools, Actions, Senses, Analyzers
    """

    def __init__(
        self,
        kernel: "RealVibeKernel",
        tool_loader: Optional["ToolLoader"] = None,
        action_loader: Optional["ActionLoader"] = None,
        sense_loader: Optional["SenseLoader"] = None,
        analyzer_loader: Optional["AnalyzerLoader"] = None,
    ):
        super().__init__(kernel)
        self._registry = None
        # OPUS-107: VEDA-4 loaders for Arsenal section
        self._tool_loader = tool_loader
        self._action_loader = action_loader
        self._sense_loader = sense_loader
        self._analyzer_loader = analyzer_loader
        self._register_data_sources()

    def _register_data_sources(self) -> None:
        """Register data sources for section-based rendering."""
        self.register_data_source("cycles.active", self._get_active_cycles)
        self.register_data_source("cycles.metrics", self._get_cycle_metrics)
        self.register_data_source("cycles.status", self._get_cycle_status)
        self.register_data_source("cycles.completed", self._get_completed_cycles)
        self.register_data_source("cycles.errors", self._get_cycle_errors)

    def _get_active_cycles(self) -> list:
        """Get active cycles for holon_hierarchy section."""
        try:
            registry = get_cycle_registry()
            active = registry.get_active_cycles()
            return (
                [{"Cycle": c.name, "Phase": c.current_phase, "Started": str(c.started_at)[:19]} for c in active[:10]]
                if active
                else [{"Cycle": "_No active cycles_", "Phase": "-", "Started": "-"}]
            )
        except Exception:
            return [{"Cycle": "_Registry unavailable_", "Phase": "-", "Started": "-"}]

    def _get_cycle_metrics(self) -> dict:
        """Get cycle metrics for phase_metrics section."""
        try:
            registry = get_cycle_registry()
            return {
                "total_cycles": registry.total_cycles,
                "active": len(registry.get_active_cycles()),
                "completed": registry.completed_count,
            }
        except Exception:
            return {"total_cycles": 0, "active": 0, "completed": 0}

    def _get_cycle_status(self) -> dict:
        """Get cycle status for memory_safety section."""
        try:
            registry = get_cycle_registry()
            return {"healthy": registry.is_healthy(), "memory_pressure": registry.memory_pressure}
        except Exception:
            return {"healthy": False, "memory_pressure": "unknown"}

    def _get_completed_cycles(self) -> list:
        """Get completed cycles for completed_cycles section."""
        try:
            registry = get_cycle_registry()
            completed = registry.get_completed_cycles(limit=10)
            return (
                [{"Cycle": c.name, "Duration": f"{c.duration_ms:.0f}ms", "Result": c.result} for c in completed]
                if completed
                else [{"Cycle": "_No completed cycles_", "Duration": "-", "Result": "-"}]
            )
        except Exception:
            return [{"Cycle": "_Registry unavailable_", "Duration": "-", "Result": "-"}]

    def _get_cycle_errors(self) -> list:
        """Get cycle errors for error_tracking section."""
        try:
            registry = get_cycle_registry()
            errors = registry.get_recent_errors(limit=10)
            return (
                [{"Cycle": e.cycle_name, "Error": e.message[:50], "Time": str(e.timestamp)[:19]} for e in errors]
                if errors
                else [{"Cycle": "_No errors_", "Error": "-", "Time": "-"}]
            )
        except Exception:
            return [{"Cycle": "_Registry unavailable_", "Error": "-", "Time": "-"}]

    def render(self) -> None:
        """Render COGNITION.md using config-driven sections."""
        config = self.get_config()
        if config and config.sections:
            content = self.render_sections()
            self.merge_and_write(content)
        else:
            content = self.generate_content()
            if content:
                self.merge_and_write(content)

    def set_loaders(
        self,
        tool_loader: Optional["ToolLoader"] = None,
        action_loader: Optional["ActionLoader"] = None,
        sense_loader: Optional["SenseLoader"] = None,
        analyzer_loader: Optional["AnalyzerLoader"] = None,
    ) -> None:
        """Inject VEDA-4 loaders for Arsenal section (OPUS-107).

        Called by kernel_tick.py after MANAS initialization to wire
        the Cognitive Mirror.
        """
        if tool_loader:
            self._tool_loader = tool_loader
        if action_loader:
            self._action_loader = action_loader
        if sense_loader:
            self._sense_loader = sense_loader
        if analyzer_loader:
            self._analyzer_loader = analyzer_loader
        logger.info("🔱 OPUS-107: Arsenal loaders injected into CognitionRenderer")

    @property
    def name(self) -> str:
        return "cognition"

    @property
    def output_file(self) -> str:
        return "COGNITION.md"

    @property
    def doc_type(self) -> DocumentType:
        return DocumentType.READONLY

    def generate_content(self) -> Optional[str]:
        """Generate COGNITION.md content (live from CycleRegistry)."""
        try:
            self._registry = get_cycle_registry()
            return self._generate_markdown()
        except Exception as e:
            logger.error(f"Error generating COGNITION content: {e}", exc_info=True)
            return None

    def _generate_markdown(self) -> str:
        """Build markdown from live CycleRegistry state."""
        lines = [
            "# 🧠 COGNITION DASHBOARD",
            "",
            "_Real-time orchestration cycle monitoring (OPUS-095)_",
            "",
        ]

        # ====================================================================
        # SECTION 1: ARSENAL (OPUS-107 - The Cognitive Mirror)
        # ====================================================================
        lines.extend(self._render_arsenal())

        # ====================================================================
        # SECTION 2: HOLON HIERARCHY (Active Cycles)
        # ====================================================================
        lines.extend(self._render_holon_hierarchy())

        # ====================================================================
        # SECTION 3: PHASE METRICS
        # ====================================================================
        lines.extend(self._render_phase_metrics())

        # ====================================================================
        # SECTION 4: MEMORY SAFETY
        # ====================================================================
        lines.extend(self._render_memory_safety())

        # ====================================================================
        # SECTION 5: RECENT COMPLETED CYCLES
        # ====================================================================
        lines.extend(self._render_completed_cycles())

        # ====================================================================
        # SECTION 6: ERROR TRACKING
        # ====================================================================
        lines.extend(self._render_error_cycles())

        # ====================================================================
        # SECTION 7: MANAS INTENT STREAM (OPUS-108 - Debug Intelligence)
        # ====================================================================
        lines.extend(self._render_intent_stream())

        # ====================================================================
        # SECTION 8: SANKALPA STATUS (Strategic Will)
        # ====================================================================
        lines.extend(self._render_sankalpa_status())

        return "\n".join(lines)

    def _render_arsenal(self) -> list:
        """Render Arsenal section showing VEDA-4 capabilities (OPUS-107).

        THE COGNITIVE MIRROR:
            - Tools (Cartridge tools - external capabilities)
            - Actions (Karmendriyas - execution handlers)
            - Senses (Jnanendriyas - perception modules)
            - Analyzers (Buddhi - analysis modules)

        OPUS-108 FIX: Lazy-load loaders at render time if not injected.
        This fixes boot order issue (InterfacePlugin priority=100 > OpusAssistant=50).
        """
        lines = [
            "## 🔱 Arsenal",
            "",
            "_VEDA-4 Capabilities (As Above, So Below)_",
            "",
        ]

        # OPUS-108 FIX: Lazy-load loaders if not injected
        # InterfacePlugin boots AFTER OpusAssistant, so injection happens too early
        tool_loader = self._tool_loader
        action_loader = self._action_loader
        sense_loader = self._sense_loader
        analyzer_loader = self._analyzer_loader

        if not tool_loader or not action_loader or not sense_loader or not analyzer_loader:
            try:
                from vibe_core.loaders import ActionLoader, AnalyzerLoader, SenseLoader, ToolLoader

                workspace = getattr(self.kernel, "_workspace", None) or Path.cwd()
                if not tool_loader:
                    tool_loader = ToolLoader(scope="opus_private", root_path=workspace)
                if not action_loader:
                    action_loader = ActionLoader(scope="opus_private")
                if not sense_loader:
                    sense_loader = SenseLoader(scope="opus_private")
                if not analyzer_loader:
                    analyzer_loader = AnalyzerLoader(scope="opus_private")
                logger.debug("🔱 OPUS-108: Lazy-loaded Arsenal loaders (fallback)")
            except Exception as e:
                logger.warning(f"Could not lazy-load loaders: {e}")

        # Count totals
        tool_count = 0
        action_count = 0
        sense_count = 0
        analyzer_count = 0
        tool_list = []
        action_list = []
        sense_list = []
        analyzer_list = []

        # === TOOLS (Cartridges) ===
        if tool_loader:
            try:
                tools, meta = tool_loader.load()
                tool_count = len(tools)
                tool_list = sorted(tools.keys())
            except Exception as e:
                logger.warning(f"Error loading tools for Arsenal: {e}")

        # === ACTIONS (Karmendriyas) ===
        if action_loader:
            try:
                actions, meta = action_loader.load()
                action_count = len(actions)
                action_list = sorted(actions.keys())
            except Exception as e:
                logger.warning(f"Error loading actions for Arsenal: {e}")

        # === SENSES (Jnanendriyas) ===
        if sense_loader:
            try:
                senses, meta = sense_loader.load()
                sense_count = len(senses)
                sense_list = sorted(senses.keys())
            except Exception as e:
                logger.warning(f"Error loading senses for Arsenal: {e}")

        # === ANALYZERS (Buddhi) ===
        if analyzer_loader:
            try:
                analyzers, meta = analyzer_loader.load()
                analyzer_count = len(analyzers)
                analyzer_list = sorted(analyzers.keys())
            except Exception as e:
                logger.warning(f"Error loading analyzers for Arsenal: {e}")

        # Total capabilities
        total = tool_count + action_count + sense_count + analyzer_count

        # Summary line
        lines.append(f"**Total Capabilities:** {total}")
        lines.append("")

        # Table
        lines.append("| Category | Count | Modules |")
        lines.append("| :--- | :---: | :--- |")

        # Tools row
        tool_names = ", ".join(tool_list[:10])
        if tool_count > 10:
            tool_names += f" (+{tool_count - 10} more)"
        lines.append(f"| 🔧 **Tools** | {tool_count} | {tool_names or '_None loaded_'} |")

        # Actions row
        action_names = ", ".join(action_list[:5])
        if action_count > 5:
            action_names += f" (+{action_count - 5} more)"
        lines.append(f"| ⚡ **Actions** | {action_count} | {action_names or '_None loaded_'} |")

        # Senses row
        sense_names = ", ".join(sense_list[:5])
        if sense_count > 5:
            sense_names += f" (+{sense_count - 5} more)"
        lines.append(f"| 👁️ **Senses** | {sense_count} | {sense_names or '_None loaded_'} |")

        # Analyzers row
        analyzer_names = ", ".join(analyzer_list[:5])
        if analyzer_count > 5:
            analyzer_names += f" (+{analyzer_count - 5} more)"
        lines.append(f"| 🧠 **Analyzers** | {analyzer_count} | {analyzer_names or '_None loaded_'} |")

        lines.extend(["", ""])

        # Detailed Tools list (collapsed if many)
        if tool_count > 0:
            lines.append("<details>")
            lines.append("<summary>📋 Full Tool List</summary>")
            lines.append("")
            for name in tool_list:
                lines.append(f"- `{name}`")
            lines.append("")
            lines.append("</details>")
            lines.append("")

        return lines

    def _render_holon_hierarchy(self) -> list:
        """Render live Holon hierarchy (parent → child cycles)."""
        lines = [
            "## 📊 Live Holon Hierarchy",
            "",
            "_Active orchestration cycles (current execution path)_",
            "",
        ]

        if not self._registry:
            lines.extend(["_No active cycles_", ""])
            return lines

        active = self._registry.get_active_cycles()

        if not active:
            lines.extend(["_No active cycles (system idle)_", ""])
            return lines

        # Group by parent_cycle_id to show hierarchy
        # Root cycles have parent_cycle_id=None
        root_cycles = [c for c in active if c.parent_cycle_id is None]
        child_cycles_by_parent = {}
        for c in active:
            if c.parent_cycle_id:
                if c.parent_cycle_id not in child_cycles_by_parent:
                    child_cycles_by_parent[c.parent_cycle_id] = []
                child_cycles_by_parent[c.parent_cycle_id].append(c)

        # Render root cycles with children
        for root in root_cycles:
            lines.append(f"**{root.cycle_name}** (ID: `{root.cycle_id[:8]}`)")
            lines.append(f"  - Trace: `{root.trace_id[:8]}`")
            lines.append(f"  - Phase: `{root.phase.value}`")
            lines.append("")

            # Children of this root
            children = child_cycles_by_parent.get(root.cycle_id, [])
            for child in children:
                lines.append(f"  └── **{child.cycle_name}** (ID: `{child.cycle_id[:8]}`)")
                lines.append(f"      - Phase: `{child.phase.value}`")
                lines.append(f"      - Observations: {len(child.observations)}")
                lines.append("")

        return lines

    def _render_phase_metrics(self) -> list:
        """Render phase execution metrics (timing per cycle)."""
        lines = [
            "## ⏱️ Phase Execution Metrics",
            "",
            "_Timing and progress for recent cycles_",
            "",
        ]

        if not self._registry:
            return lines

        completed = self._registry.get_completed_cycles(limit=10)

        if not completed:
            lines.extend(["_No completed cycles yet_", ""])
            return lines

        lines.append("| Cycle | Phase | Observations | Decisions | Errors |")
        lines.append("| :--- | :--- | :---: | :---: | :---: |")

        for cycle in completed[:10]:
            cycle_name = cycle.cycle_name.replace("_", " ").title()
            phase = cycle.phase.value.upper()
            obs_count = len(cycle.observations)
            dec_count = len(cycle.decisions)
            err_count = len(cycle.errors)

            lines.append(f"| {cycle_name} | {phase} | {obs_count} | {dec_count} | {err_count} |")

        lines.extend(["", ""])
        return lines

    def _render_memory_safety(self) -> list:
        """Render retention policy status (memory leak prevention)."""
        lines = [
            "## 🔒 Memory Safety Status",
            "",
            "_Retention policy enforcement_",
            "",
        ]

        if not self._registry:
            return lines

        status = self._registry.get_status()

        completed_count = status["completed_cycles"]
        error_count = status["error_cycles"]
        max_completed = status["retention_policy"]["max_completed"]
        max_errors = status["retention_policy"]["max_errors"]
        enabled = status["retention_policy"]["enabled"]

        lines.append(f"**Retention Policy:** {'✅ ENABLED' if enabled else '❌ DISABLED'}")
        lines.append("")

        lines.append(f"**Completed Cycles:** {completed_count} / {max_completed} (max)")
        if completed_count <= max_completed:
            lines.append("  ✅ Within limits")
        else:
            lines.append(f"  ⚠️ Over limit by {completed_count - max_completed}")

        lines.append("")

        lines.append(f"**Error Cycles:** {error_count} / {max_errors} (max)")
        if error_count <= max_errors:
            lines.append("  ✅ Within limits")
        else:
            lines.append(f"  ⚠️ Over limit by {error_count - max_errors}")

        lines.extend(["", ""])
        return lines

    def _render_completed_cycles(self) -> list:
        """Render recent completed cycles (last 20)."""
        lines = [
            "## ✅ Recently Completed Cycles",
            "",
            "_Last 20 completed orchestration cycles_",
            "",
        ]

        if not self._registry:
            return lines

        completed = self._registry.get_completed_cycles(limit=20)

        if not completed:
            lines.extend(["_No completed cycles yet_", ""])
            return lines

        lines.append("| # | Cycle | ID | Observations | Decisions | Errors |")
        lines.append("| :---: | :--- | :--- | :---: | :---: | :---: |")

        for idx, cycle in enumerate(completed, 1):
            cycle_name = cycle.cycle_name.replace("_", " ").title()
            cycle_id = cycle.cycle_id[:8]
            obs_count = len(cycle.observations)
            dec_count = len(cycle.decisions)
            err_count = len(cycle.errors)

            error_indicator = "❌" if err_count > 0 else "✅"
            lines.append(
                f"| {idx:2d} | {cycle_name} | `{cycle_id}` | {obs_count} | {dec_count} | {error_indicator} {err_count} |"
            )

        lines.extend(["", ""])
        return lines

    def _render_error_cycles(self) -> list:
        """Render error tracking (last 10 failed cycles)."""
        lines = [
            "## 🚨 Error Tracking",
            "",
            "_Last 10 failed cycles_",
            "",
        ]

        if not self._registry:
            return lines

        errors = self._registry.get_error_cycles(limit=10)

        if not errors:
            lines.extend(["✅ No errors recorded", ""])
            return lines

        for idx, cycle in enumerate(errors, 1):
            cycle_name = cycle.cycle_name.replace("_", " ").title()
            cycle_id = cycle.cycle_id[:8]

            lines.append(f"**{idx}. {cycle_name}** (`{cycle_id}`)")

            if cycle.errors:
                for phase, error_msg in cycle.errors.items():
                    lines.append(f"  - **{phase}:** {error_msg}")
            else:
                lines.append("  - _(No detailed errors recorded)_")

            lines.append("")

        return lines

    def _render_intent_stream(self) -> list:
        """Render MANAS intent stream (OPUS-108 Debug Intelligence).

        Shows pending intents from manas_intents.json state file.
        This is the "thought stream" - what MANAS is thinking about doing.
        """
        lines = [
            "## 🎯 Intent Stream",
            "",
            "_MANAS thoughts and pending intents (debug view)_",
            "",
        ]

        try:
            import json

            from vibe_core.plugins.opus_assistant.core.state_paths import get_opus_state_path

            workspace = getattr(self.kernel, "_workspace", None) or Path.cwd()
            intents_file = get_opus_state_path(workspace, "manas_intents.json")

            if not intents_file.exists():
                lines.extend(["_No intents file found_", ""])
                return lines

            with open(intents_file) as f:
                data = json.load(f)

            intents = data.get("pending", [])
            if not intents:
                lines.extend(["_Intent buffer empty (MANAS is idle)_", ""])
                return lines

            lines.append(f"**{len(intents)} pending intent(s)**")
            lines.append("")
            lines.append("| # | Intent | Type | Priority | Risk |")
            lines.append("| :---: | :--- | :--- | :---: | :---: |")

            for idx, intent in enumerate(intents[:10], 1):
                title = intent.get("title", intent.get("id", "Unknown"))[:40]
                intent_type = intent.get("intent_type", "unknown")
                priority = intent.get("priority", "medium")
                risk = intent.get("risk", "unknown")

                # Priority emoji
                priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(
                    priority.lower(), "⚪"
                )

                # Risk emoji
                risk_emoji = {"safe": "✅", "low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(
                    risk.lower(), "⚪"
                )

                lines.append(f"| {idx} | {title} | `{intent_type}` | {priority_emoji} | {risk_emoji} |")

            if len(intents) > 10:
                lines.append(f"| ... | _+{len(intents) - 10} more_ | | | |")

            lines.extend(["", ""])

        except Exception as e:
            logger.warning(f"Could not render intent stream: {e}")
            lines.extend([f"_Error loading intents: {e}_", ""])

        return lines

    def _render_sankalpa_status(self) -> list:
        """Render SANKALPA strategic will status.

        Shows active missions and strategies from sankalpa.json state file.
        This is the "strategic layer" - MANAS's long-term goals.
        """
        lines = [
            "## 🎯 Strategic Will (Sankalpa)",
            "",
            "_Active missions and strategies_",
            "",
        ]

        try:
            import json

            from vibe_core.plugins.opus_assistant.core.state_paths import get_opus_state_path

            workspace = getattr(self.kernel, "_workspace", None) or Path.cwd()
            sankalpa_file = get_opus_state_path(workspace, "sankalpa.json")

            if not sankalpa_file.exists():
                lines.extend(["_No sankalpa file found_", ""])
                return lines

            with open(sankalpa_file) as f:
                data = json.load(f)

            missions = data.get("missions", [])
            strategies = data.get("strategies", [])

            # Active missions
            active_missions = [m for m in missions if m.get("status") == "active"]
            if active_missions:
                lines.append(f"**Active Missions:** {len(active_missions)}")
                for m in active_missions[:5]:
                    name = m.get("name", "Unknown")
                    priority = m.get("priority", "medium")
                    lines.append(f"- **{name}** ({priority})")
                lines.append("")

            # Active strategies
            active_strategies = [s for s in strategies if s.get("status") == "active"]
            if active_strategies:
                lines.append(f"**Active Strategies:** {len(active_strategies)}")
                for s in active_strategies[:5]:
                    name = s.get("name", "Unknown")
                    lines.append(f"- {name}")
                lines.append("")

            if not active_missions and not active_strategies:
                lines.append("_No active missions or strategies_")
                lines.append("")

            # Last thinking timestamp
            last_think = data.get("last_think_timestamp")
            if last_think:
                lines.append(f"**Last Thought:** `{last_think}`")
                lines.append("")

        except Exception as e:
            logger.warning(f"Could not render sankalpa status: {e}")
            lines.extend([f"_Error loading sankalpa: {e}_", ""])

        return lines
