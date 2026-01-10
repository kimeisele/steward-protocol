"""
OM PROTOCOL - The Unified Field (Layer 1)

"Om Purnamadah Purnamidam" - The Whole is Complete.

WARNING: ANTI-MAYAVAD CLAUSE
============================
"brahmaṇo hi pratiṣṭhāham" - Gita 14.27
"I (Krishna) am the source of the impersonal Brahman (Om)."

Om is NOT the ultimate. Om emanates FROM Krishna (Level -2).
In Kali Yuga, Om alone is insufficient - the Holy Name (Mahamantra)
is the direct connection to Krishna.

This protocol exists for structural purposes (interface unification),
NOT as the "top" of the hierarchy. The REAL hierarchy:
- Level -2: KRISHNA (acintya - always present, ±∞)
- Level -1: MANTRA (Holy Name - not different from Krishna)
- Level 0+: All else (including OmProtocol)

See: substrate/mantra/acintya.py for the true foundation.
See: mahajanas/router.py for Mahamantra-based routing.

This protocol unifies the Trimurti (Creation, Preservation, Destruction)
into a single interface. It represents the "Vibe" of a complete Holon.

DIKSHA GATE (KALI YUGA ENFORCEMENT)
===================================
Om access requires BRAHMINICAL diksha (2nd initiation).
Without diksha, Om redirects to Mahamantra (Prabhupada's mercy).

See: substrate/mantra/diksha.py for the DikshaCertificate protocol.
"""

from typing import Protocol, runtime_checkable

from vibe_core.protocols.substrate import MantraProtocol

from .enforce import EnforceProtocol

# Phase 2: The Intellect (Buddhi & Dharma)
from .infer import InferProtocol

# Phase 1: The Divine (Identity & Time)
from .krishna import KrishnaProtocol
from .rama import RamaProtocol

# Phase 3: The Record (Akasha & Smriti)
from .read_write import ReadWriteProtocol
from .store_recall import StoreRecallProtocol
from .sync import SyncProtocol


@runtime_checkable
class OmProtocol(
    KrishnaProtocol,  # Consciousness (Who)
    RamaProtocol,  # Action (What)
    MantraProtocol,  # Time (When)
    InferProtocol,  # Thought (Why)
    EnforceProtocol,  # Law (How)
    ReadWriteProtocol,  # State (Where)
    StoreRecallProtocol,  # Memory (Whence)
    SyncProtocol,  # Cycle (Whither)
    Protocol,
):
    """
    THE OM PROTOCOL.

    A Unification of all Universal Protocols.
    Any entity implementing this is a Sovereign Holon.

    Structure:
    - Layer -1: Substrate (Ananta) - The Foundation
    - Layer 0:  Naga Loka (Services) - The Infrastructure
    - Layer 1:  Om Protocol (Universal) - The Interface
    - Layer 2:  Kernel (Vishnu) - The Implementation
    """

    pass
