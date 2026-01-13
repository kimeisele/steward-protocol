# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = 7
__genesis__ = "0xcd881939"  # GenesisByte: parampara % 37 == 0

from .agent_metadata import AgentBiology, get_metadata_registry
from .ashrama import Ashrama, AshramaTransition, get_ashrama_description
from .plugin_main import VedicGovernancePlugin
from .varna import Varna, categorize_agent_by_function, get_varna_description

__all__ = [
    "VedicGovernancePlugin",
    # Agent Metadata (classification registry)
    "AgentBiology",
    "get_metadata_registry",
    # Ashrama (lifecycle)
    "Ashrama",
    "AshramaTransition",
    "get_ashrama_description",
    # Varna (classification)
    "Varna",
    "categorize_agent_by_function",
    "get_varna_description",
]
