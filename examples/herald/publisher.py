#!/usr/bin/env python3
"""
HERALD Multi-Channel Publisher
Distributes signed content across social platforms (Phase 2: The Hyper-Engine)

Supported Platforms:
- Twitter (Daily engagement, hot takes, community building)
- LinkedIn (Weekly authority, business insights, announcements)

This module handles:
- Multi-platform API authentication (OAuth 1.0a for Twitter)
- Unified publishing interface
- Error handling and graceful degradation
- Per-platform strategy optimization
- Structured logging for GAD-000 compliance
"""

import os
import logging
import tweepy
from pathlib import Path
from datetime import datetime

# GAD-000: Structured Logging for traceability
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HERALD_PUBLISHER")


class TwitterPublisher:
    """
    HERALD's Twitter Publisher (OAuth 1.0a User Context)
    Posts daily hot takes and community engagement to AI/Crypto Twitter.

    Requires OAuth 1.0a credentials (4 keys) for write access:
    - TWITTER_API_KEY (Consumer Key)
    - TWITTER_API_SECRET (Consumer Secret)
    - TWITTER_ACCESS_TOKEN (Access Token)
    - TWITTER_ACCESS_SECRET (Access Token Secret)

    Note: App-Only Bearer Tokens do NOT support write operations.
    Use OAuth 1.0a User Context for bot posting.
    """

    def __init__(self):
        """Initialize with OAuth 1.0a credentials."""
        self.client = None

        # 1. Credentials laden (Fail Fast Check)
        # Für WRITE Access (Tweets senden) brauchen wir zwingend OAuth 1.0a (alle 4 Keys)
        self.consumer_key = os.getenv("TWITTER_API_KEY")
        self.consumer_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")

        # 2. Initialisierung versuchen
        if not all([self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret]):
            logger.warning("⚠️  TWITTER: Missing OAuth 1.0a credentials. Write access will fail.")
            # Wir lassen self.client auf None, damit publish() sofort abbricht
        else:
            try:
                self.client = tweepy.Client(
                    consumer_key=self.consumer_key,
                    consumer_secret=self.consumer_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret
                )
                logger.info("✅ TWITTER: Client initialized with OAuth 1.0a context.")
            except Exception as e:
                logger.error(f"❌ TWITTER: Client initialization crashed: {e}")

    def verify_credentials(self) -> bool:
        """
        Diagnostic Method: Checks if we can talk to Twitter using OAuth 1.0a User Context.
        Uses client.get_me() - a simple read call that proves auth works.
        Returns: True if connected, False otherwise
        """
        if not self.client:
            logger.error("❌ TWITTER: No client initialized (Missing Credentials)")
            return False
        try:
            # get_me() proves we have valid OAuth 1.0a User Context
            me = self.client.get_me()
            if me and me.data:
                logger.info(f"✅ TWITTER AUTH VERIFIED: Connected as @{me.data.username}")
                return True
            else:
                logger.error("❌ TWITTER: get_me() returned no data")
                return False
        except Exception as e:
            logger.error(f"❌ TWITTER AUTH CHECK FAILED: {type(e).__name__}: {e}")
            return False

    def publish(self, text_content, tags=None):
        """
        Publish a tweet to Twitter using OAuth 1.0a User Context.

        Args:
            text_content (str): The tweet text (max 280 chars)
            tags (list): Optional hashtags to append (e.g., ["#StewardProtocol"])

        Returns:
            bool: True if published successfully, False otherwise
        """
        if not self.client:
            logger.error("❌ TWITTER: Cannot publish. Client not initialized (Missing Credentials).")
            return False

        # Safety Check: Twitter Limit ist 280 Zeichen
        tweet = text_content
        if tags:
            tag_string = " " + " ".join(tags)
            if len(tweet) + len(tag_string) > 280:
                tweet = tweet[:280 - len(tag_string)].strip()
            tweet += tag_string

        if len(tweet) > 280:
            logger.warning(f"⚠️  TWITTER: Content too long ({len(tweet)}). Truncating...")
            tweet = tweet[:277] + "..."

        try:
            # Der eigentliche Call
            response = self.client.create_tweet(text=tweet)

            # Prüfung der Response
            if response and response.data and 'id' in response.data:
                logger.info(f"🚀 TWEET SENT: ID {response.data['id']}")
                return True
            else:
                logger.error(f"❌ TWITTER: API call returned unexpected data: {response}")
                return False

        except tweepy.errors.Forbidden as e:
            logger.critical(f"⛔ TWITTER 403 FORBIDDEN: {e}")
            logger.critical("HINT: Check 'User authentication settings' in Dev Portal -> OAuth 1.0a turned ON? Read/Write permissions?")
            return False
        except tweepy.errors.Unauthorized as e:
            logger.critical(f"⛔ TWITTER 401 UNAUTHORIZED: Check your keys/tokens. {e}")
            return False
        except Exception as e:
            logger.error(f"❌ TWITTER UNKNOWN ERROR: {type(e).__name__} - {str(e)}")
            return False


class LinkedInPublisher:
    """
    HERALD's LinkedIn Publisher
    Posts weekly business insights and announcements for enterprise audiences.

    Requires:
    - LINKEDIN_ACCESS_TOKEN (OAuth 2.0 token with write access)
    """

    def __init__(self):
        """Initialize with LinkedIn access token from environment."""
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        # LinkedIn API v2 endpoint for user profile posts (UGC Posts)
        self.api_url = "https://api.linkedin.com/v2/ugcPosts"
        self.userinfo_url = "https://api.linkedin.com/v2/userinfo"

    def get_author_urn(self):
        """
        Fetch LinkedIn User ID (URN) using the access token.

        Returns:
            str: LinkedIn URN in format "urn:li:person:XXXXX" or None if failed
        """
        if not self.access_token:
            return None

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

        try:
            import requests
            response = requests.get(
                self.userinfo_url,
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                user_info = response.json()
                user_id = user_info.get("sub")  # LinkedIn uses 'sub' for user ID
                if user_id:
                    return f"urn:li:person:{user_id}"
            return None
        except Exception as e:
            logger.warning(f"⚠️  Failed to fetch LinkedIn user ID: {e}")
            return None

    def publish(self, text_content):
        """
        Publish a post to LinkedIn.

        Args:
            text_content (str): The text to publish (max ~3000 chars for best results)

        Returns:
            bool: True if published successfully, False otherwise
        """
        if not self.access_token:
            logger.warning("⚠️  No LINKEDIN_ACCESS_TOKEN found. Skipping LinkedIn publication.")
            return False

        # Fetch author URN
        author_urn = self.get_author_urn()
        if not author_urn:
            logger.error("❌ Failed to determine LinkedIn User ID. Check your access token.")
            return False

        # Prepare post data (LinkedIn UGC Post format)
        post_data = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text_content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        # Send POST request
        try:
            import requests
            response = requests.post(
                self.api_url,
                headers=headers,
                json=post_data,
                timeout=10
            )

            if response.status_code == 201:
                logger.info("✅ SUCCESS: Post published to LinkedIn!")
                return True
            else:
                logger.error(f"❌ LinkedIn API Error: {response.status_code}")
                logger.error(f"   Details: {response.text[:200]}")
                return False

        except Exception as e:
            logger.error(f"❌ Network error publishing to LinkedIn: {e}")
            return False


class MultiChannelPublisher:
    """
    HERALD's unified publishing interface.
    Manages publishing to multiple platforms with consistent API.

    Strategy:
    - Twitter: High frequency (daily), hot takes
    - LinkedIn: Low frequency (weekly), big announcements
    """

    def __init__(self):
        """Initialize all publishers."""
        self.twitter = TwitterPublisher()
        self.linkedin = LinkedInPublisher()

    def publish_to_twitter(self, content, tags=None):
        """
        Publish to Twitter.

        Args:
            content (str): Tweet content (will be truncated to 280 chars)
            tags (list): Optional hashtags

        Returns:
            bool: Success status
        """
        logger.info("📢 Attempting Twitter publication...")
        return self.twitter.publish(content, tags=tags)

    def publish_to_linkedin(self, content):
        """
        Publish to LinkedIn.

        Args:
            content (str): Post content

        Returns:
            bool: Success status
        """
        logger.info("📋 Attempting LinkedIn publication...")
        return self.linkedin.publish(content)

    def publish_to_all_available(self, content, twitter_tags=None):
        """
        Publish to all configured platforms.
        Follows Cognitive Policy strategy:
        - Twitter: Always (if configured)
        - LinkedIn: Only on Fridays (weekly authority)

        Args:
            content (str): Content to publish
            twitter_tags (list): Optional tags for Twitter

        Returns:
            dict: Publishing results per platform
        """
        results = {
            "twitter": False,
            "linkedin": False,
            "summary": []
        }

        # Twitter: Always publish (if token configured)
        if self.twitter.consumer_key:
            logger.info("\n🐦 [TWITTER]")
            if self.publish_to_twitter(content, tags=twitter_tags):
                results["twitter"] = True
                results["summary"].append("✅ Twitter")
            else:
                results["summary"].append("❌ Twitter")
        else:
            logger.info("⚠️  Twitter: Token not configured")
            results["summary"].append("⊘ Twitter (no token)")

        # LinkedIn: Only on Fridays (weekly strategy)
        is_friday = datetime.now().weekday() == 4
        if self.linkedin.access_token:
            logger.info("\n🔗 [LINKEDIN]")
            if is_friday:
                if self.publish_to_linkedin(content):
                    results["linkedin"] = True
                    results["summary"].append("✅ LinkedIn")
                else:
                    results["summary"].append("❌ LinkedIn")
            else:
                logger.info("⏸️  LinkedIn: Saved for Friday publication (weekly strategy)")
                results["summary"].append("⏸️  LinkedIn (weekly)")
        else:
            logger.info("⚠️  LinkedIn: Token not configured")
            results["summary"].append("⊘ LinkedIn (no token)")

        return results

    def publish_from_file(self, filepath, twitter_tags=None):
        """
        Publish content from a markdown file.

        Args:
            filepath (str/Path): Path to markdown file
            twitter_tags (list): Optional tags for Twitter

        Returns:
            dict: Publishing results
        """
        path = Path(filepath)
        if not path.exists():
            logger.error(f"❌ File not found: {filepath}")
            return {"error": "File not found"}

        # Read the file and extract just the content (before the "---" metadata)
        full_text = path.read_text()
        if "---" in full_text:
            content = full_text.split("---")[0].strip()
        else:
            content = full_text.strip()

        logger.info(f"📄 Publishing from {path.name}...")
        return self.publish_to_all_available(content, twitter_tags=twitter_tags)


# Demo/Test Mode
if __name__ == "__main__":
    logger.info("🧪 HERALD MULTI-CHANNEL PUBLISHER - Test Mode")
    logger.info("=" * 60)

    publisher = MultiChannelPublisher()

    twitter_ready = publisher.twitter.consumer_key is not None
    linkedin_ready = publisher.linkedin.access_token is not None

    logger.info(f"✅ Twitter: {'READY' if twitter_ready else 'NOT CONFIGURED'}")
    logger.info(f"✅ LinkedIn: {'READY' if linkedin_ready else 'NOT CONFIGURED'}")
    logger.info("=" * 60)

    if twitter_ready or linkedin_ready:
        logger.info("\n🚀 Multi-Channel Publisher is ready to rock!")
        # In production, uncomment to test:
        # test_content = "Testing HERALD multi-channel publisher! #StewardProtocol #AI"
        # publisher.publish_to_all_available(test_content, twitter_tags=["#StewardProtocol", "#AI"])
    else:
        logger.warning("\n⚠️  No publishing tokens configured")
        logger.warning("To enable multi-channel publishing:")
        logger.warning("  1. TWITTER_API_KEY - Set for Twitter publishing")
        logger.warning("  2. TWITTER_API_SECRET - Set for Twitter publishing")
        logger.warning("  3. TWITTER_ACCESS_TOKEN - Set for Twitter publishing")
        logger.warning("  4. TWITTER_ACCESS_SECRET - Set for Twitter publishing")
        logger.warning("  5. LINKEDIN_ACCESS_TOKEN - Set for LinkedIn publishing")
        logger.warning("\nConfigure in:")
        logger.warning("  - GitHub Secrets (for GitHub Actions)")
        logger.warning("  - .env file (for local testing)")

    logger.info("=" * 60)
