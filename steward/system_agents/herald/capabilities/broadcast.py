"""
HERALD Broadcast Capability
Multi-channel publishing to Twitter, LinkedIn, etc.
Kernel-compatible module (configured via system.yaml).
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

try:
    import tweepy
except ImportError:
    tweepy = None

logger = logging.getLogger("HERALD_BROADCAST")


class TwitterPublisher:
    """Twitter OAuth 1.0a Publisher."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.enabled = config.get("twitter", {}).get("enabled", True)

        self.consumer_key = os.getenv("TWITTER_API_KEY")
        self.consumer_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")

        if not self.enabled:
            logger.info("⚠️  Twitter: Disabled in config")
            return

        if not all(
            [
                self.consumer_key,
                self.consumer_secret,
                self.access_token,
                self.access_token_secret,
            ]
        ):
            logger.warning("⚠️  TWITTER: Missing OAuth 1.0a credentials")
            return

        if not tweepy:
            logger.warning("⚠️  TWITTER: tweepy not installed")
            return

        try:
            self.client = tweepy.Client(
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
            )
            logger.info("✅ TWITTER: Client initialized (OAuth 1.0a)")
        except Exception as e:
            logger.error(f"❌ TWITTER: Init failed: {e}")

    def verify_credentials(self) -> bool:
        """Verify Twitter OAuth connection."""
        if not self.client:
            return False

        try:
            me = self.client.get_me()
            if me and me.data:
                logger.info(f"✅ TWITTER AUTH VERIFIED: @{me.data.username}")
                return True
        except Exception as e:
            logger.error(f"❌ TWITTER AUTH FAILED: {e}")

        return False

    def publish(self, text: str) -> bool:
        """Publish a tweet."""
        if not self.client:
            logger.error("❌ TWITTER: Client not available")
            return False

        if len(text) > 280:
            logger.warning(f"⚠️  Content too long ({len(text)}), truncating")
            text = text[:277] + "..."

        try:
            response = self.client.create_tweet(text=text)
            if response and response.data and "id" in response.data:
                logger.info(f"🚀 TWEET SENT: ID {response.data['id']}")
                return True
        except Exception as e:
            logger.error(f"❌ TWITTER PUBLISH FAILED: {e}")

        return False

    def publish_with_media(self, text: str, image_path: str) -> bool:
        """Publish a tweet with media."""
        if not self.client or not tweepy:
            logger.error("❌ TWITTER: Client not available")
            return False

        image_file = Path(image_path)
        if not image_file.exists():
            logger.error(f"❌ Image not found: {image_path}")
            return False

        if len(text) > 280:
            text = text[:277] + "..."

        try:
            logger.info("📤 TWITTER: Uploading media...")
            auth = tweepy.OAuth1UserHandler(
                self.consumer_key,
                self.consumer_secret,
                self.access_token,
                self.access_token_secret,
            )
            api_v1 = tweepy.API(auth)
            media = api_v1.media_upload(filename=str(image_file))
            logger.info(f"✅ Media uploaded (ID: {media.media_id})")

            response = self.client.create_tweet(text=text, media_ids=[media.media_id])

            if response and response.data and "id" in response.data:
                logger.info(f"🚀 TWEET SENT WITH MEDIA: ID {response.data['id']}")
                return True

        except Exception as e:
            logger.error(f"❌ TWITTER MEDIA PUBLISH FAILED: {e}")
            logger.info("📝 Attempting text-only fallback...")
            return self.publish(text)

        return False


class BroadcastCapability:
    """
    Multi-channel publishing capability.
    Manages publishing to Twitter, LinkedIn, Discord, etc.

    Configuration via kernel.get_config("capabilities.broadcast")
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize broadcast capability.

        Args:
            config: Broadcast capability config from system.yaml
        """
        self.config = config
        self.twitter = TwitterPublisher(config.get("twitter", {}))
        self.enabled = config.get("enabled", True)

        if not self.enabled:
            logger.info("⚠️  BROADCAST: Disabled in config")

    def publish(self, content: str, platform: str = "twitter", **kwargs) -> bool:
        """
        Publish content to specified platform.

        Args:
            content: Content to publish
            platform: "twitter", "linkedin", etc.
            **kwargs: Platform-specific options

        Returns:
            bool: Success status
        """
        if not self.enabled:
            logger.warning("⚠️  BROADCAST: Disabled, skipping publication")
            return False

        if platform == "twitter":
            return self.twitter.publish(content)
        else:
            logger.error(f"❌ BROADCAST: Unknown platform: {platform}")
            return False

    def publish_with_media(
        self, content: str, media_path: str, platform: str = "twitter"
    ) -> bool:
        """
        Publish content with media attachment.

        Args:
            content: Content to publish
            media_path: Path to media file
            platform: "twitter", etc.

        Returns:
            bool: Success status
        """
        if not self.enabled:
            logger.warning("⚠️  BROADCAST: Disabled, skipping publication")
            return False

        if platform == "twitter":
            return self.twitter.publish_with_media(content, media_path)
        else:
            logger.error(f"❌ BROADCAST: Media not supported for {platform}")
            return False

    def verify_credentials(self, platform: str = "twitter") -> bool:
        """
        Verify credentials for a platform.

        Args:
            platform: "twitter", etc.

        Returns:
            bool: Credentials valid
        """
        if platform == "twitter":
            return self.twitter.verify_credentials()
        else:
            logger.error(f"❌ BROADCAST: Unknown platform: {platform}")
            return False
