"""
Shuddhi Remedies - Structural healers.

Each remedy is a CST transformer that heals a specific violation.
The remedy is matched to a violation by rule_id.
"""

from vibe_core.shuddhi.remedies.base import CSTRemedy, ShuddhiScopeError
from vibe_core.shuddhi.remedies.silent_except import SilentExceptRemedy
from vibe_core.shuddhi.remedies.subprocess_timeout import SubprocessTimeoutRemedy
from vibe_core.shuddhi.remedies.unsafe_io_write import UnsafeIOWriteRemedy

__all__ = [
    "CSTRemedy",
    "ShuddhiScopeError",
    "UnsafeIOWriteRemedy",
    "SubprocessTimeoutRemedy",
    "SilentExceptRemedy",
]
