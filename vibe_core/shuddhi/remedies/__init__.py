"""
Shuddhi Remedies - Structural healers.

Each remedy is a CST transformer that heals a specific violation.
The remedy is matched to a violation by rule_id.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x810dcb7f"  # GenesisByte: parampara % 37 == 0

from vibe_core.shuddhi.remedies.base import CSTRemedy, ShuddhiScopeError
from vibe_core.shuddhi.remedies.silent_except import SilentExceptRemedy
from vibe_core.shuddhi.remedies.subprocess_timeout import SubprocessTimeoutRemedy
from vibe_core.shuddhi.remedies.unsafe_io_write import UnsafeIOWriteRemedy
from vibe_core.shuddhi.remedies.null_signature import (
    NullSignatureRemedy,
    heal_null_signatures,
    heal_all_null_signatures,
)

__all__ = [
    "CSTRemedy",
    "ShuddhiScopeError",
    "UnsafeIOWriteRemedy",
    "SubprocessTimeoutRemedy",
    "SilentExceptRemedy",
    "NullSignatureRemedy",
    "heal_null_signatures",
    "heal_all_null_signatures",
]
