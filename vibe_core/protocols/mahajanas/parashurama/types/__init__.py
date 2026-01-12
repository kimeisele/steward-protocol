"""
PARASHURAMA Types - Position 6 (DHARMA Quarter, DISPATCH_CALL)
==============================================================

PARASHURAMA - The Warrior Brahmin.
Types for network/file operations, syscalls, and dispatch.
"""

from vibe_core.protocols.mahajanas.parashurama.types.network_proxy import (
    KernelNetworkProxy,
)

from vibe_core.protocols.mahajanas.parashurama.types.vfs import (
    VirtualFileSystem,
)

__all__ = [
    # network_proxy.py
    "KernelNetworkProxy",
    # vfs.py
    "VirtualFileSystem",
]
