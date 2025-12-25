"""
EXTERNAL SERVICE PROTOCOLS - OPUS-307 Phase D.2

Defines interfaces for external services (Twitter, Reddit, etc.).
Implementations are registered via ServiceRegistry by plugins.

SSOT: Tools get these from ServiceRegistry, never create their own.
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class TwitterProtocol(ABC):
    """Protocol for Twitter/X API integration."""

    @abstractmethod
    def publish(self, content: str) -> bool:
        """
        Publish a tweet.

        Args:
            content: Tweet content (max 280 chars)

        Returns:
            True if published successfully
        """
        pass

    @abstractmethod
    def scan_mentions(self, since_id: Optional[str] = None) -> List[dict]:
        """
        Scan for mentions.

        Args:
            since_id: Last processed tweet ID (optional)

        Returns:
            List of mention dicts with id, text, author_id, created_at
        """
        pass

    @abstractmethod
    def reply(self, tweet_id: str, content: str) -> bool:
        """
        Reply to a tweet.

        Args:
            tweet_id: ID of tweet to reply to
            content: Reply content

        Returns:
            True if replied successfully
        """
        pass

    @abstractmethod
    def verify_credentials(self) -> bool:
        """
        Verify Twitter credentials are valid.

        Returns:
            True if authenticated
        """
        pass


class RedditProtocol(ABC):
    """Protocol for Reddit API integration."""

    @abstractmethod
    def post(self, subreddit: str, title: str, content: str) -> bool:
        """
        Post to a subreddit.

        Args:
            subreddit: Subreddit name (without r/)
            title: Post title
            content: Post body

        Returns:
            True if posted successfully
        """
        pass

    @abstractmethod
    def verify_credentials(self) -> bool:
        """
        Verify Reddit credentials are valid.

        Returns:
            True if authenticated
        """
        pass
