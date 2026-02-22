"""
DEPRECATED: Use vibe_core.mahamantra import.
SSOT PROXY: Redirects to vibe_core.mahamantra.substrate.shuddhi
"""

from vibe_core.mahamantra import ShuddhiProtocol, ShuddhiStatus, ShuddhiResult, RemedyProtocol, NullShuddhi

# Base is also needed for some imports
from vibe_core.mahamantra.substrate.shuddhi import ShuddhiProtocolBase

__all__ = [
    "ShuddhiProtocol",
    "ShuddhiStatus",
    "ShuddhiResult",
    "RemedyProtocol",
    "NullShuddhi",
    "ShuddhiProtocolBase",
]
