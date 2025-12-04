"""
EphemeralCityPlugin - UI for 4D Hypercube Operations

Renders EPHEMERAL.md to provide visibility into:
- Active ephemeral child kernels
- Merge history with proofs
- Harvested artifacts
- Kernel family tree
"""

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from vibe_core.plugin_protocol import KernelPlugin

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

EPHEMERAL_MD_PATH = Path("EPHEMERAL.md")


class EphemeralCityPlugin(KernelPlugin):
    """
    Plugin for EPHEMERAL.md - 4D Hypercube Dashboard.

    Shows:
    - Currently active ephemeral cities
    - Recent merge operations with proofs
    - Harvested artifacts
    """

    @property
    def plugin_id(self) -> str:
        return "ephemeral_ui"

    @property
    def priority(self) -> int:
        return 90  # Late in tick cycle (after spawn operations)

    def __init__(self):
        self.merge_history: List[Dict[str, Any]] = []
        self.max_history = 50

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """Initialize ephemeral tracking on boot."""
        # Load existing merge history from ledger if available
        self._load_merge_history(kernel)
        # Render initial state
        self._render_ephemeral_md(kernel)

    def on_tick_pre(self, kernel: "RealVibeKernel") -> None:
        """Check for new merge events before tick."""
        pass

    def on_tick_post(self, kernel: "RealVibeKernel") -> None:
        """Render EPHEMERAL.md after tick."""
        self._render_ephemeral_md(kernel)

    def _load_merge_history(self, kernel: "RealVibeKernel") -> None:
        """Load merge history from ledger."""
        try:
            if hasattr(kernel, "_ledger") and kernel._ledger:
                # Query ledger for EPHEMERAL_CITY_MERGE events
                events = kernel._ledger.query_events(
                    event_type="EPHEMERAL_CITY_MERGE",
                    limit=self.max_history,
                )
                for event in events:
                    self.merge_history.append(
                        {
                            "timestamp": event.get("timestamp", ""),
                            "child_id": event.get("details", {}).get("child_id", ""),
                            "proof": event.get("details", {}).get("child_ledger_hash", "")[:12],
                            "result": event.get("details", {}).get("result", "")[:100],
                        }
                    )
        except Exception:
            # Ledger may not support query_events
            pass

    def record_merge(self, merge_record: Dict[str, Any]) -> None:
        """Record a merge operation (called from spawn_city)."""
        self.merge_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "child_id": str(merge_record.get("child_id", ""))[:8],
                "proof": str(merge_record.get("child_ledger_hash", ""))[:12],
                "result": str(merge_record.get("result", ""))[:100],
            }
        )
        # Keep history bounded
        if len(self.merge_history) > self.max_history:
            self.merge_history = self.merge_history[-self.max_history :]

    def _render_ephemeral_md(self, kernel: "RealVibeKernel") -> None:
        """Render EPHEMERAL.md with current state."""
        lines = [
            "# 🌀 EPHEMERAL CITIES DASHBOARD",
            "",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
        ]

        # Active Cities Section
        lines.extend(self._render_active_cities(kernel))

        # Merge History Section
        lines.extend(self._render_merge_history())

        # Kernel Family Tree
        lines.extend(self._render_family_tree(kernel))

        # Actions Section (for future bidirectional support)
        lines.extend(self._render_actions())

        # Write to file
        EPHEMERAL_MD_PATH.write_text("\n".join(lines))

    def _render_active_cities(self, kernel: "RealVibeKernel") -> List[str]:
        """Render active ephemeral cities table."""
        lines = [
            "## 🏙️ Active Ephemeral Cities",
            "",
        ]

        child_kernels = getattr(kernel, "_child_kernels", [])

        if not child_kernels:
            lines.append("*No active ephemeral cities*")
            lines.append("")
        else:
            lines.extend(
                [
                    "| ID | Config | Agents | Status |",
                    "|:---|:-------|:-------|:-------|",
                ]
            )
            for child in child_kernels:
                child_id = hex(id(child))[:10]
                config_name = getattr(child.config, "city", {})
                if hasattr(config_name, "name"):
                    config_name = config_name.name
                else:
                    config_name = "custom"
                agent_count = len(getattr(child, "agent_registry", {}))
                status = "🟢 RUNNING" if not getattr(child, "_is_ephemeral", True) else "🔵 EPHEMERAL"
                lines.append(f"| `{child_id}` | {config_name} | {agent_count} | {status} |")
            lines.append("")

        lines.append(f"**Total Active:** {len(child_kernels)}")
        lines.append("")
        return lines

    def _render_merge_history(self) -> List[str]:
        """Render merge history table."""
        lines = [
            "## 📜 Recent Merges",
            "",
        ]

        if not self.merge_history:
            lines.append("*No merge history yet*")
            lines.append("")
        else:
            lines.extend(
                [
                    "| Timestamp | Child ID | Proof | Result |",
                    "|:----------|:---------|:------|:-------|",
                ]
            )
            # Show most recent first
            for merge in reversed(self.merge_history[-10:]):
                ts = merge.get("timestamp", "")[:19]
                child_id = merge.get("child_id", "")[:8]
                proof = merge.get("proof", "")[:12]
                result = merge.get("result", "")[:40]
                if len(merge.get("result", "")) > 40:
                    result += "..."
                lines.append(f"| {ts} | `{child_id}` | `{proof}` | {result} |")
            lines.append("")

        lines.append(f"**Total Merges:** {len(self.merge_history)}")
        lines.append("")
        return lines

    def _render_family_tree(self, kernel: "RealVibeKernel") -> List[str]:
        """Render kernel family tree."""
        lines = [
            "## 🌳 Kernel Family Tree",
            "",
            "```",
        ]

        # Check if this kernel has a parent
        parent = getattr(kernel, "_parent", None)
        is_ephemeral = getattr(kernel, "_is_ephemeral", False)

        if is_ephemeral and parent:
            lines.append(f"PARENT: {hex(id(parent))[:10]}")
            lines.append("  │")
            lines.append(f"  └── THIS KERNEL: {hex(id(kernel))[:10]} (ephemeral)")
        else:
            lines.append(f"ROOT KERNEL: {hex(id(kernel))[:10]}")

            child_kernels = getattr(kernel, "_child_kernels", [])
            for i, child in enumerate(child_kernels):
                prefix = "  └──" if i == len(child_kernels) - 1 else "  ├──"
                child_id = hex(id(child))[:10]
                lines.append(f"{prefix} CHILD: {child_id}")

        lines.extend(
            [
                "```",
                "",
            ]
        )
        return lines

    def _render_actions(self) -> List[str]:
        """Render actions section (future: bidirectional)."""
        lines = [
            "## ⚡ Actions",
            "",
            "<!-- Future: bidirectional control -->",
            "```",
            "# Spawn new city (not yet implemented via markdown)",
            '# spawn_city task="Build feature" config="fast_code"',
            "```",
            "",
            "---",
            "",
            "*Generated by EphemeralCityPlugin | 4D Hypercube Visibility Layer*",
        ]
        return lines
