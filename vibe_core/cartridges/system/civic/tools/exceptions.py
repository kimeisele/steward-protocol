"""
OPUS-098: Canonical Civic Tool Exceptions

Single Source of Truth for all civic tool exceptions.
Import from here, NOT defined locally in each tool.
"""


class InsufficientFundsError(Exception):
    """Raised when an agent lacks sufficient credits for a transaction."""

    pass


class SecretNotFoundError(Exception):
    """Raised when a secret doesn't exist in the vault."""

    pass
