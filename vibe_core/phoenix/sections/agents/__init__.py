"""System Agents Configuration Section."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xbb47faa5"  # GenesisByte: parampara % 37 == 0

from .section_main import AgentDefinition, AgentsConfig

__all__ = ["AgentsConfig", "AgentDefinition"]
