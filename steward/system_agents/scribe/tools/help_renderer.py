#!/usr/bin/env python3
"""
SCRIBE Help Renderer - Generate HELP.md

3-LAYER CONTROL CENTER:
1. THE PULSE - Background operations (CI/CD, Git)
2. CONTROL ROOM - Tunable parameters
3. DIAGNOSTICS - System health

Dynamic discovery, zero hardcoding.

Tool Protocol Compliant (Kernel-Managed).
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Import from shared base (eliminates DRY violation)
from .base import (
    Tool,
    ToolResult,
    format_auto_docs_box,
    format_auto_docs_nav,
    get_auto_docs,
    get_kernel_status,
    load_template,
)
from .introspector import (
    CartridgeIntrospector,
    ConfigIntrospector,
    ScriptIntrospector,
)
from .operations_introspector import (
    GitActivityIntrospector,
    ParameterIntrospector,
    WorkflowIntrospector,
)


class HelpRenderer(Tool):
    """Render HELP.md as 3-layer control center."""

    def __init__(self, root_dir: str = "."):
        """Initialize renderer."""
        self.root_dir = Path(root_dir)

        # Introspectors
        self.cart_introspector = CartridgeIntrospector(str(self.root_dir))
        self.script_introspector = ScriptIntrospector(str(self.root_dir))
        self.config_introspector = ConfigIntrospector(str(self.root_dir))

        # Operations introspectors
        self.workflow_introspector = WorkflowIntrospector(str(self.root_dir))
        self.git_introspector = GitActivityIntrospector(str(self.root_dir))
        self.param_introspector = ParameterIntrospector(str(self.root_dir))

    @property
    def name(self) -> str:
        return "scribe.help_renderer"

    @property
    def description(self) -> str:
        return "Generate HELP.md as 3-layer control center (pulse, control room, diagnostics)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'generate' to scan and render HELP.md content",
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

    def _scan_and_render(self) -> str:
        """Scan system and render HELP.md using external template."""
        # Discover everything
        workflows = self.workflow_introspector.scan_all()
        git_activity = self.git_introspector.get_activity()
        params = self.param_introspector.scan_all_params()

        agents = self._load_agents_from_registry()
        entry_points = self.script_introspector.discover_entry_points()
        ledger_status = self._check_ledger_status()

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        # Get kernel status for unified header
        kernel_status = get_kernel_status(str(self.root_dir))

        # Auto-docs from circuit (dynamic, not hardcoded)
        auto_docs = get_auto_docs(str(self.root_dir))
        auto_docs_nav = format_auto_docs_nav(auto_docs)
        auto_docs_box = format_auto_docs_box(auto_docs)

        # Pre-render sections for template
        template = load_template("help.jinja2")
        content = template.render(
            # Unified header variables
            timestamp=timestamp,
            generator="SCRIBE",
            kernel_status=kernel_status,
            auto_docs_nav=auto_docs_nav,
            auto_docs_box=auto_docs_box,
            # Help-specific variables
            workflows_section=self._render_workflows(workflows),
            git_section=self._render_git_activity(git_activity),
            economy_section=self._render_economy_params(params.get("economy", {})),
            security_section=self._render_security_params(params.get("security", {})),
            diagnostics_section=self._render_diagnostics(ledger_status, agents),
            agent_status_section=self._render_agent_status(agents),
            scripts_section=self._render_entry_points(entry_points),
        )

        return content

    def _render_workflows(self, workflows: List[Dict[str, Any]]) -> str:
        """Render CI/CD workflows."""
        if not workflows:
            return "⚠️  No GitHub Actions workflows discovered\n"

        output = "**Discovered Workflows:**\n\n"

        for workflow in workflows:
            output += f"**{workflow['name']}** (`{workflow['file']}`)\n"
            output += f"- **Triggers:** {', '.join(workflow['triggers'])}\n"
            if workflow.get("branches"):
                output += f"- **Branches:** {', '.join(workflow['branches'])}\n"
            output += "\n"

        output += "**Transparency:** You can see exactly when automation runs.\n"

        return output

    def _render_git_activity(self, git_activity: Dict[str, Any]) -> str:
        """Render comprehensive Git activity."""
        branch = git_activity.get("current_branch", "unknown")
        status = git_activity.get("status", "unknown")
        recent_commits = git_activity.get("recent_commits", [])
        contributors = git_activity.get("contributors", [])
        stats = git_activity.get("stats", {})

        output = "**Current State:**\n\n"
        output += f"- **Branch:** `{branch}`\n"
        output += f"- **Status:** {status}\n"
        if stats.get("total_commits"):
            output += f"- **Total Commits:** {stats['total_commits']}\n"
        output += "\n"

        # Recent commits table
        if recent_commits:
            output += "**Recent Commits:**\n\n"
            output += "| Hash | Message | Author | Time |\n"
            output += "|------|---------|--------|------|\n"
            for commit in recent_commits[:5]:
                h = commit.get("hash", "?")
                m = commit.get("message", "?")[:40]
                a = commit.get("author", "?")
                t = commit.get("time", "?")
                output += f"| `{h}` | {m} | {a} | {t} |\n"
            output += "\n"

        # Contributors
        if contributors:
            output += "**Top Contributors:**\n\n"
            for c in contributors[:3]:
                output += f"- **{c.get('name', '?')}** ({c.get('commits', 0)} commits)\n"
            output += "\n"

        # Last change summary
        if stats.get("last_change_summary"):
            output += f"**Last Change:** {stats['last_change_summary']}\n"

        return output

    def _render_economy_params(self, economy: Dict[str, Any]) -> str:
        """Render economy parameters."""
        if not economy:
            return "⚠️  Economy parameters not discovered\n"

        output = "**Discovered Parameters:**\n\n"

        if "starting_credits" in economy:
            value = economy["starting_credits"]
            source = economy.get("starting_credits_source", "unknown")
            output += f"- **Initial Credits:** {value} CR per agent\n"
            output += f"  - *Source:* `{source}`\n\n"

        if "transfer_cost" in economy:
            output += f"- **Transfer Cost:** {economy['transfer_cost']} CR\n\n"

        if "note" in economy:
            output += f"⚠️  {economy['note']}\n\n"

        return output

    def _render_security_params(self, security: Dict[str, Any]) -> str:
        """Render security parameters."""
        crimes = security.get("unforgivable_crimes", [])

        if not crimes:
            return "⚠️  Security parameters not discovered\n"

        output = "**Unforgivable Crimes (Instant Termination):**\n\n"

        for i, crime in enumerate(crimes, 1):
            output += f"{i}. `{crime}`\n"

        output += f"\n**Location:** `{security.get('location', 'unknown')}`\n"
        output += "\n**Transparency:** You know exactly what will get you killed.\n"

        return output

    def _render_diagnostics(self, ledger_status: Dict[str, Any], agents: List[str]) -> str:
        """Render diagnostics."""
        output = ""

        # Ledger check
        if not ledger_status.get("exists"):
            output += "🔴 **LEDGER NOT INITIALIZED**\n"
            output += "   → **Action:** Initialize via entry point script\n\n"
        else:
            output += "🟢 **Ledger:** Operational\n"
            if ledger_status.get("total_entries"):
                output += f"   → {ledger_status['total_entries']} entries recorded\n\n"

        # Agents check
        agent_count = len(agents) if agents else 0
        if agent_count > 0:
            output += f"🟢 **Agents:** {agent_count} registered\n\n"
        else:
            output += "🔴 **AGENTS NOT DISCOVERED**\n"
            output += "   → **Action:** Check system installation\n\n"

        return output

    def _render_agent_status(self, agents: List[str]) -> str:
        """Render agent status list."""
        if not agents:
            return "⚠️  No agents discovered\n"

        output = f"**Total:** {len(agents)} agents\n\n"

        for agent in agents:
            output += f"- **{agent}** ✅\n"

        return output

    def _render_entry_points(self, entry_points: List[Dict[str, str]]) -> str:
        """Render entry point scripts."""
        if not entry_points:
            return "No scripts found in `scripts/` directory.\n"

        output = ""

        for script in entry_points:
            desc = f" — {script['description']}" if script["description"] else ""
            output += f"### `{script['name']}`\n"
            output += f"**Location:** `{script['path']}`{desc}\n\n"
            output += f"**Usage:**\n```bash\npython {script['path']}\n```\n\n"

        return output

    def _load_agents_from_registry(self) -> List[str]:
        """Discover agents by scanning cartridge files (data-driven)."""
        agent_names = []

        # System Agents (Devatas)
        system_dir = self.root_dir / "steward" / "system_agents"
        if system_dir.exists():
            for cartridge in system_dir.glob("*/cartridge_main.py"):
                agent_names.append(cartridge.parent.name.upper())

        # Citizen Agents
        citizen_dir = self.root_dir / "agent_city" / "registry"
        if citizen_dir.exists():
            for cartridge in citizen_dir.glob("*/cartridge_main.py"):
                agent_names.append(cartridge.parent.name.upper())

        return sorted(agent_names)

    def _check_ledger_status(self) -> Dict[str, Any]:
        """Check if ledger exists."""
        ledger_file = self.root_dir / ".steward" / "ledger.json"

        if not ledger_file.exists():
            return {
                "exists": False,
                "message": "Ledger not yet initialized. Run `python scripts/summon.py` to start.",
            }

        try:
            data = json.loads(ledger_file.read_text())
            entries = data.get("chain_of_trust", {}).get("entries", [])

            return {
                "exists": True,
                "total_entries": len(entries),
                "initialized": True,
                "last_update": (entries[-1].get("timestamp", "unknown") if entries else "never"),
            }
        except:
            return {"exists": True, "readable": False}

    # Standalone mode method (for generate_docs.py)
    def scan_and_render(self) -> str:
        """Standalone method to scan and generate HELP.md."""
        return self._scan_and_render()
