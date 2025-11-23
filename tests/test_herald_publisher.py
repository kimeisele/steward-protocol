#!/usr/bin/env python3
"""
Integration Tests for HERALD Multi-Channel Publisher

Tests verify that:
1. TwitterPublisher can authenticate and post (with OAuth 1.0a)
2. LinkedInPublisher can authenticate and post
3. MultiChannelPublisher routes correctly
4. Errors are NOT silently swallowed (fail fast)

Run with: pytest tests/test_herald_publisher.py -v
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.herald.publisher import TwitterPublisher, LinkedInPublisher, MultiChannelPublisher


# Apply environment patch to entire test class
@patch.dict(os.environ, {
    "TWITTER_API_KEY": "mock_consumer_key",
    "TWITTER_API_SECRET": "mock_consumer_secret",
    "TWITTER_ACCESS_TOKEN": "mock_access_token",
    "TWITTER_ACCESS_SECRET": "mock_access_token_secret"
})
class TestTwitterPublisher:
    """All tests in this class have mocked OAuth 1.0a credentials."""

    @patch("examples.herald.publisher.tweepy.Client")
    def test_successful_tweet(self, MockClient):
        """Core test: Can publish with mocked client."""
        mock_instance = MockClient.return_value
        mock_instance.create_tweet.return_value = MagicMock(data={"id": "12345"})

        publisher = TwitterPublisher()
        result = publisher.publish("Hello World")

        assert result is True
        mock_instance.create_tweet.assert_called_once()

    @patch("examples.herald.publisher.tweepy.Client")
    def test_verify_credentials_success(self, MockClient):
        """Test the new diagnostic method."""
        mock_instance = MockClient.return_value
        mock_instance.get_me.return_value = MagicMock(
            data=MagicMock(username="test_user")
        )

        publisher = TwitterPublisher()
        assert publisher.verify_credentials() is True
        mock_instance.get_me.assert_called_once()

    @patch("examples.herald.publisher.tweepy.Client")
    def test_verify_credentials_fail(self, MockClient):
        """Test diagnostic when auth fails."""
        mock_instance = MockClient.return_value
        mock_instance.get_me.side_effect = Exception("Auth failed")

        publisher = TwitterPublisher()
        assert publisher.verify_credentials() is False

    @patch("examples.herald.publisher.tweepy.Client")
    def test_tweet_with_hashtags(self, MockClient):
        """Tweet with hashtags should be processed correctly."""
        mock_instance = MockClient.return_value
        mock_instance.create_tweet.return_value = MagicMock(data={"id": "999"})

        publisher = TwitterPublisher()
        publisher.publish("Hello", tags=["#test", "#herald"])

        # Check that tags were appended
        call_args = mock_instance.create_tweet.call_args
        assert call_args is not None
        text = call_args.kwargs["text"]
        assert "#test" in text
        assert "#herald" in text

    @patch("examples.herald.publisher.tweepy.Client")
    def test_tweet_truncation(self, MockClient):
        """Tweets longer than 280 chars should be truncated."""
        long_text = "A" * 300

        mock_instance = MockClient.return_value
        mock_instance.create_tweet.return_value = MagicMock(data={"id": "999"})

        publisher = TwitterPublisher()
        publisher.publish(long_text)

        # Verify the posted text is truncated
        call_args = mock_instance.create_tweet.call_args
        assert call_args is not None
        text = call_args.kwargs["text"]
        assert len(text) <= 280

    @patch("examples.herald.publisher.tweepy.Client")
    def test_twitter_403_handling(self, MockClient):
        """403 Forbidden should return False (permission issue)."""
        import tweepy
        mock_instance = MockClient.return_value
        # Simulate a Forbidden exception
        mock_instance.create_tweet.side_effect = tweepy.errors.Forbidden(
            response=MagicMock(status_code=403)
        )

        publisher = TwitterPublisher()
        result = publisher.publish("Forbidden Tweet")

        assert result is False

    @patch("examples.herald.publisher.tweepy.Client")
    def test_twitter_401_handling(self, MockClient):
        """401 Unauthorized should return False (invalid credentials)."""
        import tweepy
        mock_instance = MockClient.return_value
        # Simulate an Unauthorized exception
        mock_instance.create_tweet.side_effect = tweepy.errors.Unauthorized(
            response=MagicMock(status_code=401)
        )

        publisher = TwitterPublisher()
        result = publisher.publish("Unauthorized Tweet")

        assert result is False

    @patch("examples.herald.publisher.tweepy.Client")
    def test_twitter_unexpected_error_handling(self, MockClient):
        """Unexpected errors should be caught and return False."""
        mock_instance = MockClient.return_value
        # Simulate an unexpected exception
        mock_instance.create_tweet.side_effect = ValueError("Unexpected error")

        publisher = TwitterPublisher()
        result = publisher.publish("Error Tweet")

        assert result is False


# Separate test for NO credentials (fail-fast)
def test_no_credentials_fails_safely():
    """Test without any env vars - should fail gracefully."""
    with patch.dict(os.environ, {}, clear=True):
        publisher = TwitterPublisher()
        assert publisher.client is None
        assert publisher.verify_credentials() is False


class TestLinkedInPublisher:
    """Test LinkedIn publishing functionality."""

    @patch.dict(os.environ, {}, clear=True)
    def test_no_access_token_returns_false(self):
        """Publishing without access token should return False gracefully."""
        publisher = LinkedInPublisher()
        result = publisher.publish("Test post")
        assert result is False

    def test_successful_linkedin_post(self):
        """Successful LinkedIn post should return True."""
        with patch.dict(os.environ, {"LINKEDIN_ACCESS_TOKEN": "test_token"}):
            publisher = LinkedInPublisher()

            # Mock get_author_urn
            with patch.object(publisher, "get_author_urn", return_value="urn:li:person:123"):
                import requests
                with patch("examples.herald.publisher.requests.post") as mock_post:
                    mock_response = MagicMock()
                    mock_response.status_code = 201
                    mock_post.return_value = mock_response

                    result = publisher.publish("Test post")
                    assert result is True

    def test_linkedin_403_returns_false(self):
        """403 on LinkedIn should return False."""
        with patch.dict(os.environ, {"LINKEDIN_ACCESS_TOKEN": "test_token"}):
            publisher = LinkedInPublisher()

            with patch.object(publisher, "get_author_urn", return_value="urn:li:person:123"):
                import requests
                with patch("examples.herald.publisher.requests.post") as mock_post:
                    mock_response = MagicMock()
                    mock_response.status_code = 403
                    mock_response.text = "Forbidden"
                    mock_post.return_value = mock_response

                    result = publisher.publish("Test post")
                    assert result is False

    def test_no_author_urn_returns_false(self):
        """Unable to fetch author URN should return False."""
        with patch.dict(os.environ, {"LINKEDIN_ACCESS_TOKEN": "test_token"}):
            publisher = LinkedInPublisher()

            with patch.object(publisher, "get_author_urn", return_value=None):
                result = publisher.publish("Test post")
                assert result is False


class TestMultiChannelPublisher:
    """Test unified multi-channel publishing."""

    @patch.dict(os.environ, {}, clear=True)
    def test_no_channels_configured_no_failure(self):
        """If no channels configured, should still return gracefully."""
        publisher = MultiChannelPublisher()
        result = publisher.publish_to_all_available("Test content")

        # Should have a summary even if nothing published
        assert "summary" in result
        assert isinstance(result["summary"], list)

    @patch.dict(os.environ, {
        "TWITTER_API_KEY": "test_key",
        "TWITTER_API_SECRET": "test_secret",
        "TWITTER_ACCESS_TOKEN": "test_token",
        "TWITTER_ACCESS_SECRET": "test_token_secret"
    }, clear=True)
    @patch("examples.herald.publisher.tweepy.Client")
    def test_twitter_configured_linkedin_not(self, MockClient):
        """Only Twitter configured - should attempt Twitter only."""
        mock_instance = MockClient.return_value
        mock_instance.create_tweet.return_value = MagicMock(data={"id": "123"})

        publisher = MultiChannelPublisher()
        result = publisher.publish_to_all_available("Test content")

        assert result["twitter"] is True
        assert "✅ Twitter" in result["summary"]
        # LinkedIn should be skipped (no token)
        assert result["linkedin"] is False

    @patch.dict(os.environ, {
        "TWITTER_API_KEY": "test_key",
        "TWITTER_API_SECRET": "test_secret",
        "TWITTER_ACCESS_TOKEN": "test_token",
        "TWITTER_ACCESS_SECRET": "test_token_secret"
    }, clear=True)
    @patch("examples.herald.publisher.tweepy.Client")
    def test_twitter_failure_is_reported(self, MockClient):
        """Twitter failure should be recorded in results."""
        mock_instance = MockClient.return_value
        import tweepy
        mock_instance.create_tweet.side_effect = tweepy.errors.Forbidden(
            response=MagicMock()
        )

        publisher = MultiChannelPublisher()
        result = publisher.publish_to_all_available("Test content")

        assert result["twitter"] is False
        assert "❌ Twitter" in result["summary"]


class TestPublisherIntegration:
    """End-to-end integration tests."""

    @patch.dict(os.environ, {
        "TWITTER_API_KEY": "test_twitter_key",
        "TWITTER_API_SECRET": "test_twitter_secret",
        "TWITTER_ACCESS_TOKEN": "test_twitter_token",
        "TWITTER_ACCESS_SECRET": "test_twitter_token_secret"
    }, clear=True)
    @patch("examples.herald.publisher.tweepy.Client")
    def test_full_pipeline_with_twitter_only(self, MockClient):
        """Test complete publishing pipeline when Twitter is configured."""
        mock_instance = MockClient.return_value
        mock_instance.create_tweet.return_value = MagicMock(data={"id": "123"})

        publisher = MultiChannelPublisher()
        result = publisher.publish_to_all_available(
            "Test content",
            twitter_tags=["#test"]
        )

        assert result["twitter"] is True
        assert len(result["summary"]) >= 1

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_all_credentials_graceful_fail(self):
        """Even with no credentials, the system should not crash."""
        publisher = MultiChannelPublisher()
        result = publisher.publish_to_all_available("Test content")

        # Should not crash, should return a proper dict
        assert isinstance(result, dict)
        assert "summary" in result
        assert result["twitter"] is False
        assert result["linkedin"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
