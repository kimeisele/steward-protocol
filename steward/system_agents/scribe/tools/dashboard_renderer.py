#!/usr/bin/env python3
"""
SCRIBE Dashboard Renderer - Generate DASHBOARD.md

SINGLE-PAGE OPERATIONAL VIEW:
- System Health (at-a-glance)
- Agent Status Grid
- CI/CD Pipeline Status
- Git Activity
- Economic Metrics
- Security Alerts
- Quick Actions

Tool Protocol Compliant (Kernel-Managed).
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Import from shared base (eliminates DRY violation)
from .base import Tool, ToolResult, get_kernel_status, load_template
from .introspector import CartridgeIntrospector
from .operations_introspector import (
    GitActivityIntrospector,
    WorkflowIntrospector,
)
from .runtime_inspector import RuntimeInspector


class DashboardRenderer(Tool):
    """Render DASHBOARD.md as single-page operational view."""

    def __init__(self, root_dir: str = "."):
        """Initialize renderer."""
        self.root_dir = Path(root_dir)

        # Introspectors
        self.cart_introspector = CartridgeIntrospector(str(self.root_dir))
        self.git_introspector = GitActivityIntrospector(str(self.root_dir))
        self.workflow_introspector = WorkflowIntrospector(str(self.root_dir))
        self.runtime_inspector = RuntimeInspector(str(self.root_dir))

    @property
    def name(self) -> str:
        return "scribe.dashboard_renderer"

    @property
    def description(self) -> str:
        return "Generate DASHBOARD.md as single-page operational view"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'generate' to scan and render DASHBOARD.md content",
            }
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate renderer parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")
        if parameters["action"] not in ["generate"]:
            raise ValueError(f"Invalid action: {parameters['action']}. Must be 'generate'")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute renderer operation."""
        try:
            action = parameters["action"]
            if action == "generate":
                content = self._scan_and_render()
                return ToolResult(success=True, output=content)
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _scan_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """Scan ALL agents (System + Citizens) - data-driven."""
        all_agents = {}

        # System Agents (Devatas)
        system_dir = self.root_dir / "steward" / "system_agents"
        if system_dir.exists():
            system_agents = self.cart_introspector.scan_all(system_dir)
            all_agents.update(system_agents)

        # Citizen Agents
        citizen_dir = self.root_dir / "agent_city" / "registry"
        if citizen_dir.exists():
            citizen_introspector = CartridgeIntrospector(str(self.root_dir))
            citizen_agents = citizen_introspector.scan_all(citizen_dir)
            all_agents.update(citizen_agents)

        return all_agents

    def _count_agents(self) -> Dict[str, int]:
        """Count agents by category."""
        system_dir = self.root_dir / "steward" / "system_agents"
        citizen_dir = self.root_dir / "agent_city" / "registry"

        system_count = len(list(system_dir.glob("*/cartridge_main.py"))) if system_dir.exists() else 0
        citizen_count = len(list(citizen_dir.glob("*/cartridge_main.py"))) if citizen_dir.exists() else 0

        return {
            "system": system_count,
            "citizen": citizen_count,
            "total": system_count + citizen_count,
        }

    def _check_system_health(self) -> Dict[str, Any]:
        """Check overall system health."""
        health = {
            "status": "GREEN",
            "issues": [],
        }

        # Check ledger
        ledger_file = self.root_dir / ".steward" / "ledger.json"
        if not ledger_file.exists():
            health["status"] = "YELLOW"
            health["issues"].append("Ledger not initialized")

        # Check constitution
        constitution_file = self.root_dir / "CONSTITUTION.md"
        if not constitution_file.exists():
            health["status"] = "RED"
            health["issues"].append("CONSTITUTION.md missing!")

        # Check vibe_core
        vibe_core = self.root_dir / "vibe_core"
        if not vibe_core.exists():
            health["status"] = "RED"
            health["issues"].append("vibe_core kernel missing!")

        return health

    def _scan_and_render(self) -> str:
        """Scan system and render DASHBOARD.md using external template."""
        # Gather all data
        agents = self._scan_all_agents()
        agent_counts = self._count_agents()
        health = self._check_system_health()
        git_activity = self.git_introspector.get_activity()
        workflows = self.workflow_introspector.scan_all()
        runtime = self.runtime_inspector.get_system_status()

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        # Determine health indicator
        if health["status"] == "GREEN":
            health_icon = "🟢"
            health_text = "ALL SYSTEMS OPERATIONAL"
        elif health["status"] == "YELLOW":
            health_icon = "🟡"
            health_text = "MINOR ISSUES DETECTED"
        else:
            health_icon = "🔴"
            health_text = "CRITICAL ISSUES"

        # Prepare health dict for template
        health_data = {
            "status": health["status"],
            "icon": health_icon,
            "text": health_text,
            "issues": health["issues"],
        }

        # Determine kernel/ledger status (for dashboard-specific display)
        kernel_dir_status = "ACTIVE" if (self.root_dir / "vibe_core").exists() else "MISSING"
        ledger_status = "INITIALIZED" if (self.root_dir / ".steward" / "ledger.json").exists() else "NOT READY"

        # Get kernel status for unified header
        kernel_status = get_kernel_status(str(self.root_dir))

        # Pre-render using template
        template = load_template("dashboard.jinja2")
        content = template.render(
            # Unified header variables
            timestamp=timestamp,
            generator="SCRIBE",
            kernel_status=kernel_status,
            # Dashboard-specific variables
            health=health_data,
            agent_counts=agent_counts,
            agents=agents,
            git_activity=git_activity,
            workflows=workflows,
            runtime=runtime,
            kernel_dir_status=kernel_dir_status,
            ledger_status=ledger_status,
        )

        return content

    def _render_issues(self, issues: List[str]) -> str:
        """Render health issues if any."""
        if not issues:
            return ""

        output = "### Issues Detected\n\n"
        for issue in issues:
            output += f"- {issue}\n"
        return output + "\n"

    def _render_agent_grid(self, agents: Dict[str, Dict[str, Any]]) -> str:
        """Render agent status as compact grid."""
        if not agents:
            return "No agents discovered.\n"

        # Group by first letter for compact display
        output = "| Agent | Status | Domain |\n"
        output += "|-------|--------|--------|\n"

        for agent_name in sorted(agents.keys()):
            agent = agents[agent_name]
            domain = agent.get("domain", "UNKNOWN")[:12]
            output += f"| **{agent_name.upper()}** | {self._get_agent_status_icon(agent)} | {domain} |\n"

        return output

    def _get_agent_status_icon(self, agent: Dict[str, Any]) -> str:
        """Get status icon for agent."""
        # For now, all discovered agents are operational
        # Future: Check ledger for actual status
        return "ACTIVE"

    def _render_git_status(self, git_activity: Dict[str, Any]) -> str:
        """Render git status."""
        branch = git_activity.get("current_branch", "unknown")
        status = git_activity.get("status", "unknown")
        last_commit = git_activity.get("last_commit", {})

        output = f"**Branch:** `{branch}`\n"
        output += f"**Status:** {status}\n\n"

        output += "**Last Commit:**\n"
        output += f"- Hash: `{last_commit.get('hash', 'unknown')}`\n"
        output += f"- Message: {last_commit.get('message', 'unknown')}\n"
        output += f"- Author: {last_commit.get('author', 'unknown')}\n"
        output += f"- Time: {last_commit.get('time', 'unknown')}\n"

        return output

    def _render_workflows(self, workflows: List[Dict[str, Any]]) -> str:
        """Render CI/CD workflows."""
        if not workflows:
            return "No GitHub Actions workflows discovered.\n"

        output = "| Workflow | Triggers |\n"
        output += "|----------|----------|\n"

        for wf in workflows[:5]:  # Top 5 only for dashboard
            triggers = ", ".join(wf.get("triggers", []))[:30] or "manual"
            output += f"| {wf['name']} | {triggers} |\n"

        if len(workflows) > 5:
            output += f"\n*...and {len(workflows) - 5} more workflows*\n"

        return output

    def _render_runtime(self, runtime: Dict[str, Any]) -> str:
        """Render runtime metrics."""
        boot = runtime.get("boot_status", {})
        security = runtime.get("security_status", {})
        economy = runtime.get("economic_status", {})

        output = "| Metric | Value |\n"
        output += "|--------|-------|\n"
        output += f"| Boot Cycle | {boot.get('current_cycle', 'N/A')} |\n"
        output += f"| Security Level | {security.get('threat_level', 'N/A')} |\n"
        output += f"| Economy Status | {economy.get('status', 'N/A')} |\n"

        return output

    # Standalone mode method (for generate_docs.py)
    def scan_and_render(self) -> str:
        """Standalone method to scan and generate DASHBOARD.md."""
        return self._scan_and_render()
