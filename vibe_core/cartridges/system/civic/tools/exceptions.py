"""
OPUS-098: Canonical Civic Tool Exceptions

Single Source of Truth for all civic tool exceptions.
Import from here, NOT defined locally in each tool.
"""


# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xfec26532"  # GenesisByte: parampara % 37 == 0

class InsufficientFundsError(Exception):
    """Raised when an agent lacks sufficient credits for a transaction."""

    pass


class SecretNotFoundError(Exception):
    """Raised when a secret doesn't exist in the vault."""

    pass
