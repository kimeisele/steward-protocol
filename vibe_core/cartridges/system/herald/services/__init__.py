"""
HERALD Services - External API Implementations

OPUS-307 D.2: Concrete implementations of external protocols.
Registered via ServiceRegistry for DI.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xbb12ac70"  # GenesisByte: parampara % 37 == 0

from .reddit import RedditService
from .twitter import TwitterService

__all__ = ["TwitterService", "RedditService"]
