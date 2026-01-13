"""
PARASHURAMA Types - Position 6 (DHARMA Quarter, DISPATCH_CALL)
==============================================================

PARASHURAMA - The Warrior Brahmin.
Types for network/file operations, syscalls, and dispatch.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "parashurama"
__position__ = 8
__genesis__ = "0x81a3c40e"  # GenesisByte: parampara % 37 == 0

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

from vibe_core.protocols.mahajanas.parashurama.types.file_operator import (
    FileBasedOperator,
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
    # file_operator.py
    "FileBasedOperator",
]
