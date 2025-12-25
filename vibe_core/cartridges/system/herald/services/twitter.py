"""
HERALD Twitter Service - OPUS-307 D.2

Implementation of TwitterProtocol.
Registered in ServiceRegistry for DI.
"""

import logging
import os
from typing import List, Optional

from vibe_core.protocols import TwitterProtocol

try:
    import tweepy
except ImportError:
    tweepy = None

logger = logging.getLogger("HERALD_TWITTER")


class TwitterService(TwitterProtocol):
    """
    Twitter/X API implementation.

    Uses tweepy library. Operates in simulation mode if:
    - tweepy not installed
    - credentials not configured
    """

    def __init__(self):
        """Initialize Twitter client from environment."""
        self._client = None
        self._init_client()

    def _init_client(self) -> None:
        """Initialize tweepy client from env vars."""
        if not tweepy:
            logger.warning("⚠️ TwitterService: tweepy not installed")
            return

        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_secret = os.getenv("TWITTER_ACCESS_SECRET")

        if all([api_key, api_secret, access_token, access_secret]):
            try:
                self._client = tweepy.Client(
                    consumer_key=api_key,
                    consumer_secret=api_secret,
                    access_token=access_token,
                    access_token_secret=access_secret,
                    wait_on_rate_limit=True,
                )
                logger.info("✅ TwitterService: Authenticated")
            except Exception as e:
                logger.warning(f"⚠️ TwitterService: Auth failed: {e}")
        else:
            logger.warning("⚠️ TwitterService: Credentials incomplete (simulation mode)")

    def publish(self, content: str) -> bool:
        """Publish a tweet."""
        if not self._client:
            logger.info(f"🎭 TwitterService SIMULATION: Would publish: {content[:50]}...")
            return True

        try:
            self._client.create_tweet(text=content)
            logger.info("🚀 TwitterService: Published")
            return True
        except Exception as e:
            logger.error(f"❌ TwitterService: Publish failed: {e}")
            return False

    def scan_mentions(self, since_id: Optional[str] = None) -> List[dict]:
        """Scan for mentions."""
        if not self._client:
            logger.info("🎭 TwitterService SIMULATION: No mentions (offline)")
            return []

        try:
            me = self._client.get_me()
            if not me or not me.data:
                return []

            mentions = self._client.get_users_mentions(
                id=me.data.id,
                since_id=since_id,
                max_results=10,
                tweet_fields=["created_at", "author_id", "text"],
            )

            if not mentions.data:
                return []

            results = []
            for tweet in mentions.data:
                results.append(
                    {
                        "id": str(tweet.id),
                        "text": tweet.text,
                        "author_id": str(tweet.author_id),
                        "created_at": str(tweet.created_at),
                    }
                )

            logger.info(f"✅ TwitterService: Found {len(results)} mentions")
            return results

        except Exception as e:
            logger.error(f"❌ TwitterService: Scan failed: {e}")
            return []

    def reply(self, tweet_id: str, content: str) -> bool:
        """Reply to a tweet."""
        if not self._client:
            logger.info(f"🎭 TwitterService SIMULATION: Would reply to {tweet_id}")
            return True

        try:
            self._client.create_tweet(text=content, in_reply_to_tweet_id=tweet_id)
            logger.info(f"🚀 TwitterService: Replied to {tweet_id}")
            return True
        except Exception as e:
            logger.error(f"❌ TwitterService: Reply failed: {e}")
            return False

    def verify_credentials(self) -> bool:
        """Verify credentials are valid."""
        return self._client is not None
