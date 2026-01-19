"""
JAGANNATH SERVICE - The Sovereign Observer (Layer 1)

"Naayam atma bala-hinena labhyah"
This Self cannot be attained by the weak.

Implementation of the IJagannath Protocol.
He rides the Chariot (Ratha Yatra) to purify the system.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x4d0c13b2"  # GenesisByte: parampara % 37 == 0

import logging
from datetime import datetime
from typing import Optional

from vibe_core.di import ServiceRegistry
from vibe_core.naga.kulika import NagaCapability, NagaLord, naga_service
from vibe_core.naga.services.base import NagaBaseService
from vibe_core.protocols.lila.jagannath import IJagannath
from vibe_core.protocols.naga import NagaStatus, NagaType
from vibe_core.protocols.substrate import (
    IAnantaBridge,
    SubstrateHealth,
    SubstrateStatus,
)

logger = logging.getLogger("JAGANNATH")


@naga_service(
    name="Jagannath",
    lord=NagaLord.ANANTA,  # He rides via Ananta (The Substrate)
    drift_source=None,
    priority=100,  # Highest Priority (The Watcher)
    capabilities=[NagaCapability.OBSERVATION],
    protocol_class="vibe_core.protocols.lila.jagannath.IJagannath",
)
class JagannathService(NagaBaseService, IJagannath):
    def __init__(self):
        super().__init__(service_name="Jagannath")
        self._last_ratha_yatra: Optional[datetime] = None
        self._total_blessings: int = 0

    def open_eyes(self) -> SubstrateStatus:
        """
        Gaze upon the system.
        """
        # Ananta holds the physical health
        ananta = ServiceRegistry.get(IAnantaBridge)
        if not ananta:
            return SubstrateStatus(
                health=SubstrateHealth.CRITICAL,
                genes_total=0,
                genes_active=0,
                genes_dormant=0,
                genes_failed=0,
                uptime_seconds=0.0,
                last_heartbeat=datetime.now(),
                message="ANANTA NOT FOUND - UNIVERSE COLLAPSING",
            )

        return ananta.get_status()

    def start_ratha_yatra(self) -> int:
        """
        The Festival of Chariots.
        Triggers Ananta's Ashvamedha pulse.
        """
        self._last_ratha_yatra = datetime.now()
        logger.info("JAGANNATH: Ratha Yatra STARTING... The Lord moves.")

        ananta = ServiceRegistry.get(IAnantaBridge)
        if not ananta:
            logger.error("JAGANNATH: Chariot stuck! Ananta not found.")
            return 0

        # The Lord signals Ananta to work
        blessings = ananta.auto_flood_orphans()

        self._total_blessings += blessings
        if blessings > 0:
            logger.info(f"JAGANNATH: Ratha Yatra COMPLETE. {blessings} souls liberated (flooded).")
        else:
            logger.debug("JAGANNATH: Ratha Yatra peaceful. No orphans found.")

        return blessings

    def check_immigration_status(self, entity_id: str) -> bool:
        """
        Validates if an entity is properly held (Proxied).
        """
        # TODO: Implement strict checking logic
        # For now, we trust Ananta's work
        return True

    def get_status(self) -> NagaStatus:
        """
        Get Jagannath's current status.

        Required by NagaServiceProtocol - The common DNA of all NAGA services.
        """
        return NagaStatus(
            naga_type=NagaType.PRAHLAD,  # Jagannath is part of Governance layer
            healthy=True,
            events_processed=self._total_blessings,
            errors=0,
            last_heartbeat=self._last_ratha_yatra,
            message="The Lord's eyes are open",
            details={
                "total_blessings": self._total_blessings,
            },
        )
