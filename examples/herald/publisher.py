#!/usr/bin/env python3
"""
HERALD Publisher Module
Distributes signed content to LinkedIn (Phase 2: The Hyper-Engine)

This module handles:
- LinkedIn API authentication
- Publishing posts to user's LinkedIn profile
- Error handling and retry logic
- Graceful degradation if token is missing
"""

import os
import requests
from pathlib import Path


class LinkedInPublisher:
    """
    HERALD's "mouth" - publishes content to LinkedIn.

    Usage:
        publisher = LinkedInPublisher()
        success = publisher.publish("Your content here")
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
            print("    To enable: Set LINKEDIN_ACCESS_TOKEN in GitHub Secrets or .env")
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

    def publish_from_file(self, filepath):
        """
        Publish content from a markdown file (like the generated recruitment posts).

        Args:
            filepath (str/Path): Path to markdown file

        Returns:
            bool: True if published successfully
        """
        path = Path(filepath)
        if not path.exists():
            print(f"❌ File not found: {filepath}")
            return False

        # Read the file and extract just the content (before the "---" metadata)
        full_text = path.read_text()
        if "---" in full_text:
            # Split by metadata separator and take only the content part
            content = full_text.split("---")[0].strip()
        else:
            content = full_text.strip()

        print(f"📢 Publishing from {path.name}...")
        return self.publish(content)


# Demo/Test Mode
if __name__ == "__main__":
    print("🧪 HERALD PUBLISHER - Test Mode")
    print("=" * 60)

    publisher = LinkedInPublisher()

    if publisher.access_token:
        print("✅ LINKEDIN_ACCESS_TOKEN found")
        print("   Publisher is ready to publish")
        # In production, uncomment to test:
        # test_content = "Hello from HERALD Agent! Testing STEWARD Protocol integration. #StewardProtocol"
        # publisher.publish(test_content)
    else:
        print("⚠️  LINKEDIN_ACCESS_TOKEN not set")
        print("   To enable publishing, set LINKEDIN_ACCESS_TOKEN in:")
        print("   - GitHub Secrets (for GitHub Actions)")
        print("   - .env file (for local testing)")

    print("=" * 60)
