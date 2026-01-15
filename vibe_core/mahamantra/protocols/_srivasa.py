"""
SRIVASA PROTOCOL - The Governance (Config & Standards)
======================================================

"srivasa-pandita dhiman yah krsna-bhakti-dayakah"
"Srivasa Pandita is the intelligent devotee who bestows devotion."

POSITION: Rama Rama (The Organizer)
FUNCTION: Governance, Configuration, Standards.

This protocol defines HOW the system is governed.
It replaces ad-hoc YAML parsers with a structured Protocol.

LOCATION: vibe_core.mahamantra.protocols._srivasa (THE LAW)
"""

from typing import Protocol, List, Any, TypedDict, runtime_checkable
from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol, TattvaDict

class Rule(TypedDict):
    """A single governance rule."""
    id: str
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    validator: str # Name of the validation logic

@runtime_checkable
class SrivasaProtocol(PanchaTattvaProtocol, Protocol):
    """
    The Governance Protocol.
    Defines configuration schemas and validation rules.
    """

    @property
    def __tattva__(self) -> TattvaDict:
        return {
            "chaitanya": "Governance Protocol",
            "nityananda": "Seed Protocol",
            "advaita": "Validation Logic",
            "gadadhara": "Configuration Flow",
            "srivasa": "Self-Governed",
        }

    def get_rules(self) -> List[Rule]:
        """Return the active governance rules."""
        ...

    def validate_config(self, config: Any) -> bool:
        """Validate a configuration object against the rules."""
        ...

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "Rule",
    "SrivasaProtocol",
]
