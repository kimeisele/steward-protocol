"""
VISHNU: The Sustainer (Kernel)

"I am the source of all spiritual and material worlds. Everything emanates from Me."
- Bhagavad Gita 10.8

The NagaKernel holds the state of the universe (the services).
It does not create (Brahma/Bootloader).
It does not destroy (Shiva/Destructor).
It simply IS.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x3a531e84"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from vibe_core.naga.commit_watcher import NagaCommitWatcher as CommitWatcher
    from vibe_core.naga.cortex.cortex_main import NagaCortex
    from vibe_core.naga.flood import NagaFloodManager
    from vibe_core.naga.kulika import KulikaRegistry
    from vibe_core.naga.ouroboros import NagaOuroboros
    from vibe_core.naga.services.chitragupta import ChitraguptaService
    from vibe_core.naga.services.kaliya import KaliyaService
    from vibe_core.naga.services.karkotaka import KarkotakaService
    from vibe_core.naga.services.sesha import SeshaService
    from vibe_core.naga.services.takshaka import TakshakaService
    from vibe_core.naga.services.vasuki import VasukiService
    from vibe_core.protocols.identity import IdentityProtocol


@dataclass(frozen=True)
class NagaKernel:
    """
    The Immutable Core of NAGA.

    Holds references to all living services.
    Acts as the single source of truth for the system's runtime state.
    """

    # Identity (Atman)
    identity: "IdentityProtocol"

    # Core Infrastructure
    registry: "KulikaRegistry"

    # The 8 Naga Kings (Services)
    sesha: Optional["SeshaService"] = None
    vasuki: Optional["VasukiService"] = None
    takshaka: Optional["TakshakaService"] = None
    karkotaka: Optional["KarkotakaService"] = None
    kaliya: Optional["KaliyaService"] = None
    chitragupta: Optional["ChitraguptaService"] = None

    # Governance & Intelligence
    cortex: Optional["NagaCortex"] = None

    # Stability & Observability
    ouroboros: Optional["NagaOuroboros"] = None
    flood_manager: Optional["NagaFloodManager"] = None
    commit_watcher: Optional["CommitWatcher"] = None

    def get_status(self) -> Dict[str, str]:
        """Get the implementation status of the NAGA system."""
        return {
            "sesha": self._get_service_status(self.sesha),
            "vasuki": self._get_service_status(self.vasuki),
            "takshaka": self._get_service_status(self.takshaka),
            "karkotaka": self._get_service_status(self.karkotaka),
            "kaliya": self._get_service_status(self.kaliya),
            "chitragupta": self._get_service_status(self.chitragupta),
            "cortex": self._get_service_status(self.cortex),
            "ouroboros": self._get_service_status(self.ouroboros),
            "flood_manager": self._get_service_status(self.flood_manager),
        }

    def _get_service_status(self, service: Optional[object]) -> str:
        """Helper to get status string."""
        return "ACTIVE" if service else "DISABLED"
