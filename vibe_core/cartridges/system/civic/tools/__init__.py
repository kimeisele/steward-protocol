"""
Civic Tools Package

All tools are kernel-managed and implement the Tool protocol.
Access via kernel routing: system.execute_tool("civic.tool_name", params)
"""

# =============================================================================
# CANONICAL EXCEPTIONS (OPUS-098: Single Source of Truth)
# =============================================================================
# =============================================================================
# TOOL IMPORTS
# =============================================================================
# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x3a8fdae6"  # GenesisByte: parampara % 37 == 0

from .bank_tool import BankTool
from .exceptions import InsufficientFundsError, SecretNotFoundError
from .ledger_tool import LedgerTool
from .license_tool import LicenseTool
from .lifecycle_enforcer import LifecycleEnforcer
from .vault_tool import VaultTool

__all__ = [
    # Exceptions (canonical definitions - OPUS-098)
    "InsufficientFundsError",
    "SecretNotFoundError",
    # Tool classes (kernel-managed)
    "BankTool",
    "LedgerTool",
    "LicenseTool",
    "LifecycleEnforcer",
    "VaultTool",
]
