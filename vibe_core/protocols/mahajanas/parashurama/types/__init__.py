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

from vibe_core.protocols.mahajanas.parashurama.types.io_service import (
    DocumentType,
    WriteResult,
    KernelIOService,
)

__all__ = [
    # network_proxy.py
    "KernelNetworkProxy",
    # vfs.py
    "VirtualFileSystem",
    # io_service.py
    "DocumentType",
    "WriteResult",
    "KernelIOService",
]
