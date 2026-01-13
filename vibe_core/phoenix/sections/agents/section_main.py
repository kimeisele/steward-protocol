"""
System Agents Configuration - Wiring of agent names to implementation classes.

Extracted from phoenix.yaml `agents` section.
Loaded from config/agents.yaml via Phoenix auto-discovery.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x86f78e2d"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class AgentDefinition:
    """Single agent wiring definition."""

    name: str
    class_path: str  # e.g., "vibe_core.cartridges.system.herald.cartridge_main:HeraldCartridge"
    protocol: str = "VibeAgent"
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentDefinition":
        """Create from YAML dict."""
        return cls(
            name=data.get("name", ""),
            class_path=data.get("class", ""),
            protocol=data.get("protocol", "VibeAgent"),
            enabled=data.get("enabled", True),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "name": self.name,
            "class": self.class_path,
            "protocol": self.protocol,
            "enabled": self.enabled,
        }


@dataclass
class AgentsConfig:
    """
    System Agents Configuration.

    Auto-discovered by SectionLoader -> loads from config/agents.yaml

    This section defines the wiring between agent names and their
    implementation classes. Previously lived in phoenix.yaml under
    the `agents` key.

    Required attributes:
    - section_id: str - Unique identifier (must match manifest.json id)
    - source_file: str - YAML filename in config/

    Required methods:
    - from_dict(data) -> Self - Create instance from YAML data
    - to_dict() -> dict - Serialize to dict
    - validate() -> List[str] - Return list of errors (empty = valid)
    """

    # Required: Must match manifest.json "id"
    section_id: str = "agents"
    source_file: str = "agents.yaml"

    # Agent definitions
    system_agents: List[AgentDefinition] = field(default_factory=list)
    custom_agents: List[AgentDefinition] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentsConfig":
        """Create config from YAML dictionary."""
        system_agents_data = data.get("system_agents", [])
        custom_agents_data = data.get("custom_agents", [])

        return cls(
            system_agents=[AgentDefinition.from_dict(a) for a in system_agents_data],
            custom_agents=[AgentDefinition.from_dict(a) for a in custom_agents_data],
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary (for saving/export)."""
        return {
            "system_agents": [a.to_dict() for a in self.system_agents],
            "custom_agents": [a.to_dict() for a in self.custom_agents],
        }

    def validate(self) -> List[str]:
        """
        Validate configuration.

        Returns:
            List of error messages (empty = valid)
        """
        errors = []

        # Check for duplicate agent names
        names = [a.name for a in self.system_agents + self.custom_agents]
        duplicates = [n for n in names if names.count(n) > 1]
        if duplicates:
            errors.append(f"Duplicate agent names: {set(duplicates)}")

        # Check class paths are non-empty
        for agent in self.system_agents + self.custom_agents:
            if not agent.class_path:
                errors.append(f"Agent '{agent.name}' has empty class path")
            if not agent.name:
                errors.append("Agent has empty name")

        return errors

    def get_enabled_agents(self) -> List[AgentDefinition]:
        """Return only enabled agents."""
        return [a for a in self.system_agents + self.custom_agents if a.enabled]

    def get_agent(self, name: str) -> AgentDefinition | None:
        """Get agent by name."""
        for agent in self.system_agents + self.custom_agents:
            if agent.name == name:
                return agent
        return None
