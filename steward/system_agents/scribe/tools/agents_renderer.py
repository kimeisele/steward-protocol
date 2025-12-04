#!/usr/bin/env python3
"""
SCRIBE Agents Renderer - Generate AGENTS.md

Tool Protocol Compliant (Kernel-Managed).
Uses external Jinja2 template for maintainability.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from steward.system_agents.scribe.tools.base import (
    Tool,
    ToolResult,
    get_kernel_status,
    load_template,
)
from steward.system_agents.scribe.tools.introspector import CartridgeIntrospector


class AgentsRenderer(Tool):
    """Render AGENTS.md from cartridge metadata."""

    def __init__(self, root_dir: str = "."):
        """Initialize renderer."""
        self.root_dir = Path(root_dir)
        self.introspector = CartridgeIntrospector(str(self.root_dir))
        self.agents = {}

    @property
    def name(self) -> str:
        return "scribe.agents_renderer"

    @property
    def description(self) -> str:
        return "Generate AGENTS.md from cartridge metadata introspection"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'generate' to scan and render AGENTS.md content",
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
        """Scan cartridges and render AGENTS.md using external template."""
        # Discover all agents from BOTH directories (data-driven)
        # System Agents (Devatas) - core system functionality
        system_agents = self.introspector.scan_all(self.root_dir / "steward" / "system_agents")

        # Citizen Agents - application-level agents
        citizen_agents = {}
        citizen_path = self.root_dir / "agent_city" / "registry"
        if citizen_path.exists():
            citizen_agents = CartridgeIntrospector(str(self.root_dir)).scan_all(citizen_path)

        # Merge both
        self.agents = {**system_agents, **citizen_agents}
        system_count = len(system_agents)
        citizen_count = len(citizen_agents)

        # Prepare template data
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        total_tools = sum(len(a["tools"]) for a in self.agents.values())

        # Sort agents by name for consistent output
        sorted_agents = sorted(self.agents.values(), key=lambda a: a["agent_name_pretty"])

        # Get kernel status for unified header
        kernel_status = get_kernel_status(str(self.root_dir))

        # Load and render template
        template = load_template("agents.jinja2")
        content = template.render(
            # Unified header variables
            timestamp=timestamp,
            generator="SCRIBE",
            kernel_status=kernel_status,
            # Agents-specific variables
            agents=sorted_agents,
            system_count=system_count,
            citizen_count=citizen_count,
            total_tools=total_tools,
        )

        return content

    # Standalone mode method (for generate_docs.py)
    def scan_and_render(self) -> str:
        """Standalone method to scan and generate AGENTS.md."""
        return self._scan_and_render()
