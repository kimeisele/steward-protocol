#!/usr/bin/env python3
"""
SCRIBE Citymap Renderer - Generate CITYMAP.md

3-LAYER ARCHITECTURE:
1. KERNEL LAYER (vibe_core) - Boot, Security, Topology
2. ROUTING LAYER (tools) - Milk Ocean, Universal Provider
3. AGENT LAYER (cartridges) - The 13 agents

Dynamic discovery + Runtime state = Complete city map

Tool Protocol Compliant (Kernel-Managed).
"""

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Import from shared base (eliminates DRY violation)
from .base import Tool, ToolResult, load_template
from .introspector import CartridgeIntrospector
from .runtime_inspector import RuntimeInspector
from .vibe_introspector import ToolsIntrospector, VibeCoreIntrospector


class CitymapRenderer(Tool):
    """Render comprehensive CITYMAP.md with 3-layer architecture."""

    def __init__(self, root_dir: str = "."):
        """Initialize renderer."""
        self.root_dir = Path(root_dir)

        # Dynamic introspectors
        self.cart_introspector = CartridgeIntrospector(str(self.root_dir))
        self.vibe_introspector = VibeCoreIntrospector(str(self.root_dir))
        self.tools_introspector = ToolsIntrospector(str(self.root_dir))
        self.runtime_inspector = RuntimeInspector(str(self.root_dir))

        # Data storage
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.vibe_modules: Dict[str, Dict[str, Any]] = {}
        self.tools: Dict[str, List[Dict[str, Any]]] = {}
        self.domains: Dict[str, List[str]] = defaultdict(list)

    @property
    def name(self) -> str:
        return "scribe.citymap_renderer"

    @property
    def description(self) -> str:
        return "Generate CITYMAP.md with 3-layer architecture (kernel, routing, agents)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'generate' to scan and render CITYMAP.md content",
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
        """Scan all layers and render complete CITYMAP.md using external template."""
        # Layer 1: Kernel (vibe_core)
        self.vibe_modules = self.vibe_introspector.scan_all()

        # Layer 2: Routing (tools)
        self.tools = self.tools_introspector.scan_all()

        # Layer 3: Agents (cartridges) - scan BOTH directories
        # System Agents (Devatas) - core system functionality
        system_agents = self.cart_introspector.scan_all(self.root_dir / "steward" / "system_agents")

        # Citizen Agents - application-level agents
        citizen_agents = {}
        citizen_path = self.root_dir / "agent_city" / "registry"
        if citizen_path.exists():
            citizen_agents = CartridgeIntrospector(str(self.root_dir)).scan_all(citizen_path)

        # Merge both agent types
        self.agents = {**system_agents, **citizen_agents}

        # Track agent categories for rendering
        self.system_agent_names = set(system_agents.keys())
        self.citizen_agent_names = set(citizen_agents.keys())

        # Runtime state
        system_status = self.runtime_inspector.get_system_status()

        # Use ACTUAL scanned count (data-driven, not stale runtime inspector)
        system_count = len(self.system_agent_names)
        citizen_count = len(self.citizen_agent_names)
        total_count = len(self.agents)

        # Track agent domains
        for agent_name, metadata in self.agents.items():
            domain = metadata.get("domain", "INFRASTRUCTURE")
            self.domains[domain].append(agent_name)

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        # Pre-render sections for template
        template = load_template("citymap.jinja2")
        content = template.render(
            timestamp=timestamp,
            total_count=total_count,
            system_count=system_count,
            citizen_count=citizen_count,
            boot_cycle=system_status["boot_status"]["current_cycle"],
            threat_level=system_status["security_status"]["threat_level"],
            economy_status=system_status["economic_status"].get("status", "N/A"),
            topology_desc=system_status["topology_status"]["description"],
            kernel_section=self._render_kernel_layer(),
            routing_section=self._render_routing_layer(),
            agents_by_domain_section=self._render_agents_by_domain(),
            agent_table=self._render_agent_table(),
            economic_section=self._render_economic_status(system_status["economic_status"]),
            security_section=self._render_security_status(system_status["security_status"]),
            # Dynamic diagrams
            domain_diagram=self._render_domain_diagram(),
            governance_diagram=self._render_governance_diagram(),
            topology_diagram=self._render_topology_diagram(),
        )

        return content

    def _render_kernel_layer(self) -> str:
        """Render Layer 1: Kernel modules from vibe_core."""
        if not self.vibe_modules:
            return "⚠️  No vibe_core modules discovered\n"

        output = "### 🌌 Discovered Kernel Modules\n\n"

        for module_name, metadata in sorted(self.vibe_modules.items()):
            output += f"**{module_name}** (`{metadata['file']}` - {metadata['lines']} lines)\n"
            output += f"- {metadata['purpose']}\n"
            if metadata.get("features"):
                output += f"- Key components: {', '.join(metadata['features'][:3])}\n"
            output += "\n"

        return output

    def _render_routing_layer(self) -> str:
        """Render Layer 2: Routing tools."""
        if not self.tools:
            return "⚠️  No agent tools discovered\n"

        output = ""

        # Highlight key routing agents
        key_agents = ["envoy", "civic"]

        for agent_name in key_agents:
            if agent_name not in self.tools:
                continue

            output += f"### 🔧 {agent_name.upper()} Tools\n\n"

            for tool in self.tools[agent_name]:
                output += f"**{tool['name']}** (`{tool['file']}` - {tool['lines']} lines)\n"
                output += f"- {tool['purpose']}\n\n"

        return output

    def _render_agents_by_domain(self) -> str:
        """Render agents organized by domain."""
        output = ""

        for domain in sorted(self.domains.keys()):
            agents = self.domains[domain]
            output += f"\n#### {domain}\n\n"

            for agent_name in agents:
                agent = self.agents[agent_name]
                output += f"- **{agent_name.upper()}** ({agent['class_name']}) — {agent['description']}\n"

        return output

    def _render_agent_table(self) -> str:
        """Render complete agent registry table."""
        output = ""

        for agent_name in sorted(self.agents.keys()):
            agent = self.agents[agent_name]
            output += (
                f"| **{agent_name.upper()}** | {agent['domain']} | `{agent['class_name']}` | {agent['description']} |\n"
            )

        return output

    def _render_economic_status(self, econ_status: Dict[str, Any]) -> str:
        """Render economic system status."""
        output = f"- **Status:** {econ_status.get('status', 'Unknown')}\n"

        if econ_status.get("status") == "OPERATIONAL":
            output += f"- **Credits in Circulation:** {econ_status.get('total_credits', 0)} CR\n"
            output += f"- **Transactions Recorded:** {econ_status.get('transaction_count', 0)}\n"
            output += f"- **Ledger Entries:** {econ_status.get('ledger_entries', 0)}\n"
        else:
            output += f"- **Note:** {econ_status.get('description', 'N/A')}\n"

        return output

    def _render_security_status(self, sec_status: Dict[str, Any]) -> str:
        """Render security system status."""
        output = f"- **Threat Level:** {sec_status.get('threat_level', 'Unknown')}\n"
        output += f"- **Status:** {sec_status.get('status', 'Unknown')}\n"
        output += f"- **Threats Detected:** {sec_status.get('threats_detected', 0)}\n"
        output += f"- **Description:** {sec_status.get('description', 'No information')}\n"

        return output

    def _render_domain_diagram(self) -> str:
        """Generate Mermaid pie chart of agents by domain."""
        if not self.domains:
            return ""

        output = "```mermaid\npie showData\n"
        output += "    title Agent Distribution by Domain\n"

        for domain, agents in sorted(self.domains.items()):
            domain_label = domain if domain else "UNKNOWN"
            output += f'    "{domain_label}" : {len(agents)}\n'

        output += "```\n"
        return output

    def _render_governance_diagram(self) -> str:
        """Generate Mermaid diagram of governance flow (dynamic from domain data)."""
        # Find key governance agents
        gov_agents = self.domains.get("GOVERNANCE", [])
        sec_agents = self.domains.get("SECURITY", [])

        output = "```mermaid\ngraph TD\n"
        output += '    CONST["📜 CONSTITUTION<br/>(Immutable Law)"]\n'

        # Add governance agents
        for agent in gov_agents[:2]:
            output += f'    {agent.upper()}["{agent.upper()}"]\n'

        # Add security agents
        for agent in sec_agents[:1]:
            output += f'    {agent.upper()}["{agent.upper()}"]\n'

        # Add connections
        if gov_agents:
            output += f"    CONST --> {gov_agents[0].upper()}\n"
        if sec_agents:
            output += f"    CONST --> {sec_agents[0].upper()}\n"
            if gov_agents:
                output += f"    {sec_agents[0].upper()} -.->|monitors| {gov_agents[0].upper()}\n"

        # Add all agents node
        output += '    AGENTS["👥 ALL AGENTS"]\n'
        if gov_agents:
            output += f"    {gov_agents[0].upper()} -->|manages| AGENTS\n"
        if len(gov_agents) > 1:
            output += f"    AGENTS -->|submit proposals| {gov_agents[1].upper()}\n"

        output += "```\n"
        return output

    def _render_topology_diagram(self) -> str:
        """Generate ASCII topology diagram (dynamic from agent count)."""
        total = len(self.agents)
        sys_count = len(self.system_agent_names)
        citizen_count = len(self.citizen_agent_names)

        output = "```\n"
        output += "         🏔️ MOUNT MERU (Center)\n"
        output += "              CIVIC\n"
        output += "               │\n"
        output += "    ┌──────────┼──────────┐\n"
        output += "  INNER      MIDDLE      OUTER\n"
        output += "  (Core)    (Services)  (Citizens)\n"
        output += "    │          │           │\n"
        output += f"  {sys_count} Devatas  {total - sys_count - citizen_count} Routing  {citizen_count} Citizens\n"
        output += "```\n"
        return output

    # Standalone mode method (for generate_docs.py)
    def scan_and_render(self) -> str:
        """Standalone method to scan and generate CITYMAP.md."""
        return self._scan_and_render()
