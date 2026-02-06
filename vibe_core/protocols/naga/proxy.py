"""
LEGACY PROXY - KILLED (foundation-surgery)
==========================================

This file contained a legacy iGene-based NagaProxy that conflicted with
the real NagaProxy in vibe_core.naga.proxy (the Balarama Pattern).

Two classes, same name, incompatible signatures:
  - naga/proxy.py: NagaProxy(wrapped) — used by DI auto-flood (THE REAL ONE)
  - protocols/naga/proxy.py: NagaProxy(target, gene) — legacy iGene (THIS FILE)

Killed to eliminate name collision. Zero external imports at time of removal.

CANONICAL PROXY: vibe_core.naga.proxy.NagaProxy
"""

# Re-export from canonical location so any stale import gets the real one
from vibe_core.naga.proxy import NagaProxy

__all__ = ["NagaProxy"]
