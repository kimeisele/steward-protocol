"""
Supreme Court Tools Package

All tools are kernel-managed and implement the Tool protocol.
Access via kernel routing: system.execute_tool("supreme_court.tool_name", params)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xeb38c285"  # GenesisByte: parampara % 37 == 0

from .appeals_tool import Appeal, AppealStatus, AppealsTool
from .justice_ledger import JusticeLedger
from .precedent_tool import PrecedentCase, PrecedentTool
from .verdict_tool import Verdict, VerdictTool, VerdictType

__all__ = [
    # Tool classes (kernel-managed)
    "AppealsTool",
    "VerdictTool",
    "PrecedentTool",
    "JusticeLedger",
    # Data classes and enums
    "Appeal",
    "AppealStatus",
    "Verdict",
    "VerdictType",
    "PrecedentCase",
]
