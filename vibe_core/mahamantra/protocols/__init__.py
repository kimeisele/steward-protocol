"""
MAHAMANTRA PROTOCOLS - The Protocols That Define Protocols
==========================================================

"aham sarvasya prabhavo mattah sarvam pravartate"
"I am the source of all. Everything emanates from Me." (BG 10.8)

This module contains the META-PROTOCOLS:
- _core.py: What IS a protocol? (self-referential)
- _declaration.py: How does something declare itself?
- _level.py: What IS a level?
- _fractal.py: How does something grow fractally?
- _holographic.py: How does each part contain the whole?

ACINTYA PRINCIPLE:
    These protocols define themselves.
    The Protocol Protocol IS a protocol.
    Krishna knowing Krishna through Krishna.

USAGE:
    from vibe_core.mahamantra.protocols import MahamantraProtocol

    class MyProtocol(MahamantraProtocol):
        __mahajana__ = "brahma"
        __position__ = 1
        ...
"""

from vibe_core.mahamantra.protocols._core import (
    # The root protocol
    MahamantraProtocol,
    # Identity
    ProtocolIdentity,
    # Capability
    ProtocolCapability,
    # The 37 formula
    KSETRA_COUNT,
    MAHAJANA_COUNT,
    KSETRAJNA_COUNT,
    PARAMPARA,
)

__all__ = [
    # Core Protocol
    "MahamantraProtocol",
    # Identity
    "ProtocolIdentity",
    # Capability
    "ProtocolCapability",
    # Constants
    "KSETRA_COUNT",
    "MAHAJANA_COUNT",
    "KSETRAJNA_COUNT",
    "PARAMPARA",
]
