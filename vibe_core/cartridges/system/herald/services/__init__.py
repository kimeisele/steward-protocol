"""
HERALD Services - External API Implementations

OPUS-307 D.2: Concrete implementations of external protocols.
Registered via ServiceRegistry for DI.
"""

from .reddit import RedditService
from .twitter import TwitterService

__all__ = ["TwitterService", "RedditService"]
