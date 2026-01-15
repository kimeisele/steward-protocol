"""
ADOPTION - The Mounting of the Golden Orbits
============================================

"ye yathā māṁ prapadyante"
"As they surrender unto Me, I reward them accordingly."
— Bhagavad Gita 4.11

This module handles the "Mounting" (Adoption) of legacy services into Orbital Reactors.
It takes a BalaramaProxy (The Passenger) and mounts it onto a ShadowReactor (The Vehicle).

MECHANICS:
    1. Spawn a UNIQUE OrbitalReactor for each service.
    2. Reactor ID is derived from Service Name → Deterministic Lagna.
    3. Proxy is registered as a listener on the Reactor.
    4. Reactor drives the Proxy via on_bhoga/on_prasadam interfaces.

"""

import logging
from typing import Dict, List

from vibe_core.mahamantra.substrate.proxy import BalaramaProxy
# Import OrbitalShadowReactor via convenience factory or direct
from vibe_core.mahamantra.reactor.shadow import OrbitalShadowReactor, ShadowReactor

logger = logging.getLogger("MAHAMANTRA.ADOPTION")

def adopt_services(proxies: Dict[str, BalaramaProxy]) -> List[ShadowReactor]:
    """
    HARD ENGINEERING: Mounts legacy services into Orbital Reactors.
    
    1. Iterates all wrapped proxies (Jagai/Madhai/etc).
    2. Spawns a UNIQUE OrbitalReactor for each.
    3. Calculates LAGNA (Phase Shift) based on Service Name.
    4. Connects Service to Reactor.
    """
    reactors: List[ShadowReactor] = []
    
    for name, proxy in proxies.items():
        # 1. Spawn Reactor (The Container)
        # reactor_id derived from name ensures consistent Orbit!
        # Use simple name hash for ID to guarantee stability
        # 1. Spawn Reactor (The Container)
        # reactor_id derived from name ensures consistent Orbit!
        # Use simple name hash for ID to guarantee stability
        reactor = OrbitalShadowReactor(
            auto_discover=False, # We are manually wiring
            initial_position=0,  # Everyone starts at "Global 0" (but shifted by Lagna)
            reactor_id=name      # Cleanly inject ID for deterministic Lagna
        )
        
        # 2. Mount Service (The Passenger)
        # We inject the Reactor into the Proxy so the Proxy knows where it lives.
        proxy.set_reactor(reactor)
        
        # 3. Register Listeners (The Wire)
        # When the Reactor ticks, it calls the Proxy.
        # WICHTIG: Reactor ticks RELATIV (Lagna), not ABSOLUT.
        # We register on "effective position" 0?
        # No, we register on the Proxy's declared position.
        # If Prithu is Position 0, we register at 0.
        # The OrbitalReactor only fires Position 0 when (Global - Lagna) == 0.
        # So Prithu only runs when it is HIS time.
        
        if proxy.has_identity:
            reactor.register_listener(proxy.position, proxy)
            logger.info(f"🚀 ORBIT: {name.split('.')[-1]} mounted on Reactor[{reactor.lagna}] (Phase {reactor.lagna})")
            reactors.append(reactor)
        else:
             logger.debug(f"⚠️ {name} has no identity, skipping orbital mount.")
        
    return reactors
