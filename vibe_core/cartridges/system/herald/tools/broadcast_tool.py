"""
HERALD Broadcast Tool - Social media publishing (Twitter, Reddit) (Tool Protocol).

Handles publishing to multiple platforms with graceful fallback.
Offline-capable with dry-run modes for safety.

This tool implements the Tool Protocol for kernel-managed execution.

OPUS-307 D.1: Updated to support dependency injection via ServiceRegistry.
"""

import logging
import os
from typing import TYPE_CHECKING, Any, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

try:
    import tweepy
except ImportError:
    tweepy = None

try:
    import praw
except ImportError:
    praw = None

logger = logging.getLogger("HERALD_BROADCAST")


class BroadcastTool(Tool):
    """
    Multi-platform content distribution.

    Supports:
    - Twitter/X: Real-time announcements
    - Reddit: Long-form technical discussions (draft_only mode by default)

    Graceful fallback when API keys unavailable.
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None):
        """
        Initialize broadcast tool with optional DI support.

        OPUS-307 D.1: Accepts ServiceRegistry for dependency injection.
        Falls back to legacy initialization if services not provided.

        Args:
            services: ServiceRegistry for dependency injection (optional)
        """
        super().__init__(services)
        self.twitter_client = None
        self.reddit_client = None

        # OPUS-307 D.1: Future - get clients from ServiceRegistry
        # if self.services:
        #     self.twitter_client = self.services.get(TwitterProtocol)
        #     self.reddit_client = self.services.get(RedditProtocol)
        # else:
        #     self._init_legacy()

        # Legacy init (until TwitterProtocol/RedditProtocol are created)
        self._init_twitter()
        self._init_reddit()

    @property
    def name(self) -> str:
        return "herald.broadcast"  # Namespaced: agent_id.tool_name

    @property
    def description(self) -> str:
        return "Publish content, scan mentions, and reply on social media platforms (Twitter, Reddit)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action to perform: 'publish', 'scan_mentions', 'reply', 'verify_credentials'",
            },
            "content": {
                "type": "string",
                "required": False,
                "description": "Content to publish/reply (required for publish and reply actions)",
            },
            "platform": {
                "type": "string",
                "required": False,
                "description": "Platform: 'twitter' or 'reddit' (default: twitter)",
            },
            "tweet_id": {
                "type": "string",
                "required": False,
                "description": "Tweet ID for replies (required for reply action)",
            },
            "since_id": {
                "type": "string",
                "required": False,
                "description": "Last processed mention ID for scanning",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """
        Validate broadcast parameters.

        Args:
            parameters: Tool parameters

        Raises:
            ValueError: If required parameter missing or invalid
            TypeError: If parameter has wrong type
        """
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        if action not in ["publish", "scan_mentions", "reply", "verify_credentials"]:
            raise ValueError(
                f"Invalid action: {action}. Must be 'publish', 'scan_mentions', 'reply', or 'verify_credentials'"
            )

        # Validate action-specific parameters
        if action == "publish":
            if "content" not in parameters:
                raise ValueError("publish action requires 'content' parameter")
            if not isinstance(parameters["content"], str):
                raise TypeError("content must be a string")

        elif action == "reply":
            if "content" not in parameters:
                raise ValueError("reply action requires 'content' parameter")
            if "tweet_id" not in parameters:
                raise ValueError("reply action requires 'tweet_id' parameter")
            if not isinstance(parameters["content"], str):
                raise TypeError("content must be a string")
            if not isinstance(parameters["tweet_id"], str):
                raise TypeError("tweet_id must be a string")

        # Validate platform if specified
        if "platform" in parameters:
            platform = parameters["platform"]
            if platform not in ["twitter", "reddit"]:
                raise ValueError(f"Invalid platform: {platform}. Must be 'twitter' or 'reddit'")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute broadcast operation.

        Args:
            parameters: Validated tool parameters

        Returns:
            ToolResult with operation results
        """
        try:
            action = parameters["action"]
            platform = parameters.get("platform", "twitter")

            if action == "publish":
                content = parameters["content"]
                success = self._publish_twitter(content) if platform == "twitter" else self._publish_reddit(content)

                return ToolResult(
                    success=success,
                    output={
                        "published": success,
                        "platform": platform,
                        "content_preview": content[:80] + "..." if len(content) > 80 else content,
                    },
                    metadata={
                        "action": "publish",
                        "platform": platform,
                    },
                )

            elif action == "scan_mentions":
                since_id = parameters.get("since_id")
                mentions = self._scan_twitter_mentions(since_id) if platform == "twitter" else []

                return ToolResult(
                    success=True,
                    output={
                        "mentions": mentions,
                        "count": len(mentions),
                        "platform": platform,
                    },
                    metadata={
                        "action": "scan_mentions",
                        "platform": platform,
                        "mention_count": len(mentions),
                    },
                )

            elif action == "reply":
                tweet_id = parameters["tweet_id"]
                content = parameters["content"]
                success = self._reply_twitter(tweet_id, content)

                return ToolResult(
                    success=success,
                    output={
                        "replied": success,
                        "tweet_id": tweet_id,
                        "content_preview": content[:80] + "..." if len(content) > 80 else content,
                    },
                    metadata={
                        "action": "reply",
                        "tweet_id": tweet_id,
                    },
                )

            elif action == "verify_credentials":
                verified = self.verify_credentials(platform)

                return ToolResult(
                    success=True,
                    output={
                        "verified": verified,
                        "platform": platform,
                        "status": "authenticated" if verified else "offline",
                    },
                    metadata={
                        "action": "verify_credentials",
                        "platform": platform,
                    },
                )

        except Exception as e:
            error_msg = f"Broadcast operation failed: {type(e).__name__}: {e!s}"
            logger.error(f"BroadcastTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

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
        Internal method: Verify platform credentials are available.

        Args:
            platform: "twitter" or "reddit"

        Returns:
            bool: True if authenticated, False otherwise
        """
        if platform == "twitter":
            available = self.twitter_client is not None
            logger.info("✅ Twitter credentials verified" if available else "❌ Twitter offline")
            return available
        elif platform == "reddit":
            available = self.reddit_client is not None
            logger.info("✅ Reddit credentials verified" if available else "❌ Reddit offline")
            return available
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
