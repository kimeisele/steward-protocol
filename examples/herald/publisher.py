#!/usr/bin/env python3
"""
HERALD Multi-Channel Publisher
Distributes signed content across social platforms (Phase 2: The Hyper-Engine)

Supported Platforms:
- Twitter (Daily engagement, hot takes, community building)
- LinkedIn (Weekly authority, business insights, announcements)

This module handles:
- Multi-platform API authentication
- Unified publishing interface
- Error handling and graceful degradation
- Per-platform strategy optimization
"""

import os
import requests
from requests_oauthlib import OAuth1
from pathlib import Path
from datetime import datetime


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
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        # Twitter API v2 endpoint for posting tweets
        self.api_url = "https://api.twitter.com/2/tweets"

    def publish(self, text_content, tags=None):
        """
        Publish a tweet to Twitter using OAuth 1.0a User Context.

        Args:
            text_content (str): The tweet text (max 280 chars)
            tags (list): Optional hashtags to append (e.g., ["#StewardProtocol"])

        Returns:
            bool: True if published successfully, False otherwise
        """
        # Fail fast: Check if all 4 OAuth 1.0a keys are present
        if not all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            print("⚠️  TWITTER: Missing OAuth 1.0a credentials.")
            print("   Required: TWITTER_API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET")
            return False

        # Truncate to Twitter limits (280 chars)
        # If tags provided, reserve space for them
        max_length = 280
        if tags:
            tag_string = " " + " ".join(tags)
            max_length -= len(tag_string)

        tweet = text_content[:max_length].strip()
        if tags:
            tweet += " " + " ".join(tags)

        # Setup OAuth 1.0a authentication (Range Rover Motor)
        auth = OAuth1(
            self.api_key,
            self.api_secret,
            self.access_token,
            self.access_secret
        )

        # Prepare payload
        payload = {"text": tweet}

        try:
            response = requests.post(
                self.api_url,
                auth=auth,
                json=payload,
                timeout=10
            )

            if response.status_code == 201:
                tweet_data = response.json()
                tweet_id = tweet_data.get("data", {}).get("id")
                print(f"✅ SUCCESS: Tweet posted to Twitter!")
                print(f"   Tweet ID: {tweet_id}")
                return True
            else:
                print(f"❌ Twitter API Error: {response.status_code}")
                print(f"   Details: {response.text[:200]}")
                return False

        except requests.RequestException as e:
            print(f"❌ Network error publishing to Twitter: {e}")
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
        except requests.RequestException as e:
            print(f"⚠️  Failed to fetch LinkedIn user ID: {e}")
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
            print("⚠️  No LINKEDIN_ACCESS_TOKEN found. Skipping LinkedIn publication.")
            return False

        # Fetch author URN
        author_urn = self.get_author_urn()
        if not author_urn:
            print("❌ Failed to determine LinkedIn User ID. Check your access token.")
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
            response = requests.post(
                self.api_url,
                headers=headers,
                json=post_data,
                timeout=10
            )

            if response.status_code == 201:
                print("✅ SUCCESS: Post published to LinkedIn!")
                print(f"   Response: {response.status_code}")
                return True
            else:
                print(f"❌ LinkedIn API Error: {response.status_code}")
                print(f"   Details: {response.text[:200]}")
                return False

        except requests.RequestException as e:
            print(f"❌ Network error publishing to LinkedIn: {e}")
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
        print("📢 Attempting Twitter publication...")
        return self.twitter.publish(content, tags=tags)

    def publish_to_linkedin(self, content):
        """
        Publish to LinkedIn.

        Args:
            content (str): Post content

        Returns:
            bool: Success status
        """
        print("📋 Attempting LinkedIn publication...")
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
        if self.twitter.api_key:
            print("\n🐦 [TWITTER]")
            if self.publish_to_twitter(content, tags=twitter_tags):
                results["twitter"] = True
                results["summary"].append("✅ Twitter")
            else:
                results["summary"].append("❌ Twitter")
        else:
            print("⚠️  Twitter: Token not configured")
            results["summary"].append("⊘ Twitter (no token)")

        # LinkedIn: Only on Fridays (weekly strategy)
        is_friday = datetime.now().weekday() == 4
        if self.linkedin.access_token:
            print("\n🔗 [LINKEDIN]")
            if is_friday:
                if self.publish_to_linkedin(content):
                    results["linkedin"] = True
                    results["summary"].append("✅ LinkedIn")
                else:
                    results["summary"].append("❌ LinkedIn")
            else:
                print("⏸️  LinkedIn: Saved for Friday publication (weekly strategy)")
                results["summary"].append("⏸️  LinkedIn (weekly)")
        else:
            print("⚠️  LinkedIn: Token not configured")
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
            print(f"❌ File not found: {filepath}")
            return {"error": "File not found"}

        # Read the file and extract just the content (before the "---" metadata)
        full_text = path.read_text()
        if "---" in full_text:
            content = full_text.split("---")[0].strip()
        else:
            content = full_text.strip()

        print(f"📄 Publishing from {path.name}...")
        return self.publish_to_all_available(content, twitter_tags=twitter_tags)


# Demo/Test Mode
if __name__ == "__main__":
    print("🧪 HERALD MULTI-CHANNEL PUBLISHER - Test Mode")
    print("=" * 60)

    publisher = MultiChannelPublisher()

    twitter_ready = publisher.twitter.api_key is not None
    linkedin_ready = publisher.linkedin.access_token is not None

    print(f"✅ Twitter: {'READY' if twitter_ready else 'NOT CONFIGURED'}")
    print(f"✅ LinkedIn: {'READY' if linkedin_ready else 'NOT CONFIGURED'}")
    print("=" * 60)

    if twitter_ready or linkedin_ready:
        print("\n🚀 Multi-Channel Publisher is ready to rock!")
        # In production, uncomment to test:
        # test_content = "Testing HERALD multi-channel publisher! #StewardProtocol #AI"
        # publisher.publish_to_all_available(test_content, twitter_tags=["#StewardProtocol", "#AI"])
    else:
        print("\n⚠️  No publishing tokens configured")
        print("To enable multi-channel publishing:")
        print("  1. TWITTER_API_KEY - Set for Twitter publishing")
        print("  2. LINKEDIN_ACCESS_TOKEN - Set for LinkedIn publishing")
        print("\nConfigure in:")
        print("  - GitHub Secrets (for GitHub Actions)")
        print("  - .env file (for local testing)")

    print("=" * 60)
