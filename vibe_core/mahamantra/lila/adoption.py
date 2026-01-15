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

from vibe_core.mahamantra.reactor.shadow import OrbitalShadowReactor, ShadowReactor
from vibe_core.mahamantra.substrate.mahajana import Mahajana, Avatara

logger = logging.getLogger("MAHAMANTRA.ADOPTION")


# =============================================================================
# OP-CODE REGISTRY (The Scanner's Lens)
# =============================================================================

OP_CODES: Dict[str, List[str]] = {
    # GENESIS (0-3)
    "prithu": ["write", "disk", "path", "db", "file", "mount", "infra", "foundation"],
    "brahma": ["create", "spawn", "init", "new", "factory", "construct", "allocate"],
    "narada": ["msg", "send", "api", "http", "request", "broadcast", "notify", "event"],
    "shambhu": ["delete", "kill", "clean", "remove", "destroy", "gc", "garbage", "close"],
    
    # DHARMA (4-7)
    "vyasa": ["log", "record", "history", "document", "compile", "version", "meta"],
    "kumaras": ["knowledge", "learn", "wisdom", "context", "observe", "read"],
    "kapila": ["analyze", "analysis", "train", "loop", "calc", "math", "matrix", "stat"],
    "manu": ["rule", "policy", "law", "govern", "permit", "allow", "deny", "config"],
    
    # KARMA (8-11)
    "parashurama": ["execute", "run", "action", "perform", "do", "enforce", "task"],
    "prahlada": ["serve", "service", "devotion", "client", "connect", "await", "listen"],
    "janaka": ["duty", "job", "responsibility", "maintain", "sync", "state"],
    "bhishma": ["commit", "vow", "ledger", "persist", "transaction", "store", "save"],
    
    # MOKSHA (12-15)
    "nrisimha": ["protect", "secure", "auth", "login", "guard", "defend", "encrypt"],
    "bali": ["yield", "give", "dedicate", "resource", "offer", "provider"],
    "shuka": ["see", "vision", "view", "render", "display", "show", "narrate", "ui"],
    "yamaraja": ["judge", "audit", "verify", "check", "test", "fail", "pass", "verdict"]
}

def analyze_source(source_code: str) -> Dict[str, object]:
    """
    Analyze source code to infer Mahajana identity.
    
    THE CENSUS MECHANISM:
    ---------------------
    Counts "OpCode" occurrences to guess the soul of the code.
    
    Args:
        source_code: The Python source code string.
        
    Returns:
        Dict with keys:
            - identity: str (e.g. "brahma")
            - score: float (confidence 0.0-1.0)
            - top_candidates: Dict[str, int] (scores by mahajana)
    """
    # Normalize
    text = source_code.lower()
    scores: Dict[str, int] = {k: 0 for k in OP_CODES.keys()}
    
    # Count OpCodes
    for mahajana, keywords in OP_CODES.items():
        for keyword in keywords:
            count = text.count(keyword)
            # Weight shorter words less to avoid noise? 
            # For now, simple count + slight boost for exact matches (hard in raw string)
            # Just plain count for robustness.
            scores[mahajana] += count
            
    # Find winner
    if not scores:
        return {"identity": "unknown", "score": 0.0, "top_candidates": {}}
        
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    winner, win_score = sorted_scores[0]
    
    # Calculate confidence (win_score / total_score)
    total_score = sum(scores.values())
    confidence = (win_score / total_score) if total_score > 0 else 0.0
    
    # Normalize identity name to Enum
    # Check if Avatara or Mahajana
    return {
        "identity": winner,
        "score": confidence,
        "count": win_score,
        "top_candidates": dict(sorted_scores[:3])
    }


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
