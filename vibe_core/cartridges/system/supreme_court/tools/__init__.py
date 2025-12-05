"""
Supreme Court Tools Package

All tools are kernel-managed and implement the Tool protocol.
Access via kernel routing: system.execute_tool("supreme_court.tool_name", params)
"""

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
