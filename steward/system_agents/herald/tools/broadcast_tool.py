"""
HERALD Broadcast Tool - Social media publishing (Twitter, Reddit).

Handles publishing to multiple platforms with graceful fallback.
Offline-capable with dry-run modes for safety.
"""

import logging
import os
from typing import Optional

try:
    import tweepy
except ImportError:
    tweepy = None

try:
    import praw
except ImportError:
    praw = None

logger = logging.getLogger("HERALD_BROADCAST")


class BroadcastTool:
    """
    Multi-platform content distribution.

    Supports:
    - Twitter/X: Real-time announcements
    - Reddit: Long-form technical discussions (draft_only mode by default)

    Graceful fallback when API keys unavailable.
    """

    def __init__(self):
        """Initialize broadcast tool."""
        self.twitter_client = None
        self.reddit_client = None
        self._init_twitter()
        self._init_reddit()

    def _init_twitter(self) -> None:
        """Initialize Twitter client."""
        if not tweepy:
            logger.warning("⚠️  Broadcast: tweepy not installed")
            return

        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_secret = os.getenv("TWITTER_ACCESS_SECRET")

        if all([api_key, api_secret, access_token, access_secret]):
            try:
                self.twitter_client = tweepy.Client(
                    consumer_key=api_key,
                    consumer_secret=api_secret,
                    access_token=access_token,
                    access_token_secret=access_secret,
                    wait_on_rate_limit=True,
                )
                logger.info("✅ Broadcast: Twitter authenticated")
            except Exception as e:
                logger.warning(f"⚠️  Broadcast: Twitter auth failed: {e}")
        else:
            logger.warning("⚠️  Broadcast: Twitter credentials incomplete (simulation mode)")

    def _init_reddit(self) -> None:
        """Initialize Reddit client."""
        if not praw:
            logger.warning("⚠️  Broadcast: praw not installed")
            return

        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        username = os.getenv("REDDIT_USERNAME")
        password = os.getenv("REDDIT_PASSWORD")

        if all([client_id, client_secret, username, password]):
            try:
                self.reddit_client = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    username=username,
                    password=password,
                    user_agent="HERALD_AGENT/3.0",
                )
                logger.info("✅ Broadcast: Reddit authenticated")
            except Exception as e:
                logger.warning(f"⚠️  Broadcast: Reddit auth failed: {e}")
        else:
            logger.warning("⚠️  Broadcast: Reddit credentials incomplete (simulation mode)")

    def verify_credentials(self, platform: str = "twitter") -> bool:
        """
        Verify platform credentials are available.

        Args:
            platform: "twitter" or "reddit"

        Returns:
            bool: True if authenticated, False otherwise
        """
        if platform == "twitter":
            available = self.twitter_client is not None
            logger.info(f"✅ Twitter credentials verified" if available else "❌ Twitter offline")
            return available
        elif platform == "reddit":
            available = self.reddit_client is not None
            logger.info(f"✅ Reddit credentials verified" if available else "❌ Reddit offline")
            return available
        return False

    def publish(self, content: str, platform: str = "twitter") -> bool:
        """
        Publish content to platform.

        Args:
            content: Text to publish
            platform: "twitter" or "reddit"

        Returns:
            bool: True if successful, False otherwise
        """
        if platform == "twitter":
            return self._publish_twitter(content)
        elif platform == "reddit":
            return self._publish_reddit(content)
        return False

    def _publish_twitter(self, content: str) -> bool:
        """Publish to Twitter."""
        if not self.twitter_client:
            logger.warning("🛑 Twitter offline (would publish in real deployment)")
            return True  # Success simulation

        try:
            self.twitter_client.create_tweet(text=content)
            logger.info("🚀 Published to Twitter")
            return True
        except Exception as e:
            logger.error(f"❌ Twitter publish error: {e}")
            return False

    def _publish_reddit(self, content: str) -> bool:
        """Publish to Reddit (simulation mode by default)."""
        logger.warning("🛑 Reddit: Simulation mode (draft_only)")
        logger.info(f"   Would post to r/LocalLLaMA: {content[:80]}...")
        return True  # Success simulation

    def scan_mentions(self, since_id: Optional[str] = None, platform: str = "twitter") -> list:
        """
        Scan for mentions on platform.

        Args:
            since_id: ID of last processed mention
            platform: "twitter"

        Returns:
            list: List of mention objects (dict)
        """
        if platform == "twitter":
            return self._scan_twitter_mentions(since_id)
        return []

    def reply_to_tweet(self, tweet_id: str, content: str) -> bool:
        """
        Reply to a specific tweet.

        Args:
            tweet_id: ID of tweet to reply to
            content: Reply text

        Returns:
            bool: True if successful
        """
        return self._reply_twitter(tweet_id, content)

    def _scan_twitter_mentions(self, since_id: Optional[str]) -> list:
        """Fetch mentions from Twitter."""
        if not self.twitter_client:
            logger.warning("🛑 Twitter offline (simulation: no mentions)")
            return []

        try:
            # Get user ID first
            me = self.twitter_client.get_me()
            if not me or not me.data:
                return []

            my_id = me.data.id

            # Fetch mentions
            mentions = self.twitter_client.get_users_mentions(
                id=my_id,
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

            logger.info(f"✅ Found {len(results)} new mentions")
            return results

        except Exception as e:
            logger.error(f"❌ Twitter scan failed: {e}")
            return []

    def _reply_twitter(self, tweet_id: str, content: str) -> bool:
        """Post reply on Twitter."""
        if not self.twitter_client:
            logger.warning(f"🛑 Twitter offline (would reply to {tweet_id}: {content[:50]}...)")
            return True

        try:
            self.twitter_client.create_tweet(text=content, in_reply_to_tweet_id=tweet_id)
            logger.info(f"🚀 Replied to {tweet_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Twitter reply failed: {e}")
            return False
