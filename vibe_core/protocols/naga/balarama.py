"""
BALARAMA PROTOCOL - The Strength / The Wrapper
===============================================

FOUNDATION SURGERY: Legacy iGene-based BalaramaInjector removed.
The real Balarama Pattern lives in vibe_core.naga.proxy.NagaProxy.

BalaramaProxy is now an alias to the canonical NagaProxy.

CANONICAL: vibe_core.naga.proxy.NagaProxy
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xd03d5a78"  # GenesisByte: parampara % 37 == 0

from vibe_core.naga.proxy import NagaProxy

# Alias for backward compatibility
BalaramaProxy = NagaProxy

__all__ = ["BalaramaProxy", "NagaProxy"]
