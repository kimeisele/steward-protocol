"""
HERALD Reddit Service - OPUS-307 D.2

Implementation of RedditProtocol.
Registered in ServiceRegistry for DI.
"""

import logging
import os

from vibe_core.protocols import RedditProtocol

try:
    import praw
except ImportError:
    praw = None

logger = logging.getLogger("HERALD_REDDIT")


class RedditService(RedditProtocol):
    """
    Reddit API implementation.

    Uses praw library. Operates in simulation mode if:
    - praw not installed
    - credentials not configured
    """

    def __init__(self):
        """Initialize Reddit client from environment."""
        self._client = None
        self._init_client()

    def _init_client(self) -> None:
        """Initialize praw client from env vars."""
        if not praw:
            logger.warning("⚠️ RedditService: praw not installed")
            return

        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        username = os.getenv("REDDIT_USERNAME")
        password = os.getenv("REDDIT_PASSWORD")

        if all([client_id, client_secret, username, password]):
            try:
                self._client = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    username=username,
                    password=password,
                    user_agent="HERALD_AGENT/3.0",
                )
                logger.info("✅ RedditService: Authenticated")
            except Exception as e:
                logger.warning(f"⚠️ RedditService: Auth failed: {e}")
        else:
            logger.warning("⚠️ RedditService: Credentials incomplete (simulation mode)")

    def post(self, subreddit: str, title: str, content: str) -> bool:
        """Post to a subreddit."""
        if not self._client:
            logger.info(f"🎭 RedditService SIMULATION: Would post to r/{subreddit}")
            return True

        try:
            sub = self._client.subreddit(subreddit)
            sub.submit(title=title, selftext=content)
            logger.info(f"🚀 RedditService: Posted to r/{subreddit}")
            return True
        except Exception as e:
            logger.error(f"❌ RedditService: Post failed: {e}")
            return False

    def verify_credentials(self) -> bool:
        """Verify credentials are valid."""
        return self._client is not None
