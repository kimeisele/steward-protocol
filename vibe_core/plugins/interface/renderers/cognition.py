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

        return "\n".join(lines)

    def _render_arsenal(self) -> list:
        """Render Arsenal section showing VEDA-4 capabilities (OPUS-107).

        THE COGNITIVE MIRROR:
            - Tools (Cartridge tools - external capabilities)
            - Actions (Karmendriyas - execution handlers)
            - Senses (Jnanendriyas - perception modules)
            - Analyzers (Buddhi - analysis modules)
        """
        lines = [
            "## 🔱 Arsenal",
            "",
            "_VEDA-4 Capabilities (As Above, So Below)_",
            "",
        ]

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
        if self._tool_loader:
            try:
                tools, meta = self._tool_loader.load()
                tool_count = len(tools)
                tool_list = sorted(tools.keys())
            except Exception as e:
                logger.warning(f"Error loading tools for Arsenal: {e}")

        # === ACTIONS (Karmendriyas) ===
        if self._action_loader:
            try:
                actions, meta = self._action_loader.load()
                action_count = len(actions)
                action_list = sorted(actions.keys())
            except Exception as e:
                logger.warning(f"Error loading actions for Arsenal: {e}")

        # === SENSES (Jnanendriyas) ===
        if self._sense_loader:
            try:
                senses, meta = self._sense_loader.load()
                sense_count = len(senses)
                sense_list = sorted(senses.keys())
            except Exception as e:
                logger.warning(f"Error loading senses for Arsenal: {e}")

        # === ANALYZERS (Buddhi) ===
        if self._analyzer_loader:
            try:
                analyzers, meta = self._analyzer_loader.load()
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
