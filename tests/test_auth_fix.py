#!/usr/bin/env python3
"""
HERALD OAuth 1.0a Authentication Tests

Uses pytest monkeypatch fixture for robust environment variable injection.
This ensures env vars are set BEFORE TwitterPublisher.__init__() is called.

This file replaces test_herald_publisher.py to force CI to pick up new code.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from examples.herald.publisher import (
    TwitterPublisher,
    LinkedInPublisher,
    MultiChannelPublisher,
)


class TestTwitterPublisher:
    """Test Twitter publishing with OAuth 1.0a credentials."""

    @pytest.fixture(autouse=True)
    def setup_oauth_env(self, monkeypatch):
        """
        Fixture that runs before each test in this class.
        Uses pytest's monkeypatch - the robust way to set env vars.
        Guarantees env vars exist BEFORE TwitterPublisher() is instantiated.
        """
        monkeypatch.setenv("TWITTER_API_KEY", "fake_consumer_key")
        monkeypatch.setenv("TWITTER_API_SECRET", "fake_consumer_secret")
        monkeypatch.setenv("TWITTER_ACCESS_TOKEN", "fake_access_token")
        monkeypatch.setenv("TWITTER_ACCESS_SECRET", "fake_access_secret")

    def test_client_initializes_with_credentials(self):
        """With env vars set, TwitterPublisher should initialize tweepy.Client."""
        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            publisher = TwitterPublisher()
            # Client must be initialized (not None)
            assert publisher.client is not None
            # Verify tweepy.Client was called with correct args
            MockClient.assert_called_once()

    def test_successful_tweet_publication(self):
        """Happy path: tweet publishes successfully."""
        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            # Mock the response structure
            mock_instance = MockClient.return_value
            mock_instance.create_tweet.return_value = MagicMock(data={"id": "12345"})

            publisher = TwitterPublisher()
            result = publisher.publish("Hello World")

            assert result is True
            mock_instance.create_tweet.assert_called_once_with(text="Hello World")

    def test_tweet_with_hashtags(self):
        """Tweet can include hashtags."""
        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.create_tweet.return_value = MagicMock(data={"id": "999"})

            publisher = TwitterPublisher()
            publisher.publish("Hello", tags=["#AI", "#Crypto"])

            call_args = mock_instance.create_tweet.call_args
            text = call_args.kwargs["text"]
            assert "#AI" in text
            assert "#Crypto" in text

    def test_tweet_truncation_to_280_chars(self):
        """Tweets longer than 280 chars are truncated."""
        long_text = "A" * 300
        expected_text = "A" * 277 + "..."

        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.create_tweet.return_value = MagicMock(data={"id": "999"})

            publisher = TwitterPublisher()
            publisher.publish(long_text)

            call_args = mock_instance.create_tweet.call_args
            actual_text = call_args.kwargs["text"]
            assert len(actual_text) <= 280
            assert actual_text == expected_text

    def test_error_handling_403_forbidden(self):
        """403 Forbidden (permission error) returns False."""
        import tweepy

        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.create_tweet.side_effect = tweepy.errors.Forbidden(
                response=MagicMock()
            )

            publisher = TwitterPublisher()
            result = publisher.publish("Forbidden Tweet")

            assert result is False

    def test_error_handling_401_unauthorized(self):
        """401 Unauthorized (bad credentials) returns False."""
        import tweepy

        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.create_tweet.side_effect = tweepy.errors.Unauthorized(
                response=MagicMock()
            )

            publisher = TwitterPublisher()
            result = publisher.publish("Unauthorized Tweet")

            assert result is False

    def test_unexpected_error_handling(self):
        """Unexpected errors are caught and return False."""
        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.create_tweet.side_effect = ValueError("Network error")

            publisher = TwitterPublisher()
            result = publisher.publish("Error Tweet")

            assert result is False

    def test_verify_credentials_success(self):
        """verify_credentials() returns True when auth succeeds."""
        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.get_me.return_value = MagicMock(
                data=MagicMock(username="steward_bot")
            )

            publisher = TwitterPublisher()
            result = publisher.verify_credentials()

            assert result is True
            mock_instance.get_me.assert_called_once()

    def test_verify_credentials_failure(self):
        """verify_credentials() returns False when auth fails."""
        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.get_me.side_effect = Exception("Auth failed")

            publisher = TwitterPublisher()
            result = publisher.verify_credentials()

            assert result is False


class TestTwitterPublisherNoCredentials:
    """Test behavior when NO OAuth 1.0a credentials are provided."""

    def test_client_not_initialized_without_credentials(self, monkeypatch):
        """Without env vars, client should be None (fail-fast)."""
        # Clear all Twitter env vars
        monkeypatch.delenv("TWITTER_API_KEY", raising=False)
        monkeypatch.delenv("TWITTER_API_SECRET", raising=False)
        monkeypatch.delenv("TWITTER_ACCESS_TOKEN", raising=False)
        monkeypatch.delenv("TWITTER_ACCESS_SECRET", raising=False)

        publisher = TwitterPublisher()
        assert publisher.client is None

    def test_publish_fails_without_client(self, monkeypatch):
        """publish() returns False if client is None."""
        monkeypatch.delenv("TWITTER_API_KEY", raising=False)
        monkeypatch.delenv("TWITTER_API_SECRET", raising=False)
        monkeypatch.delenv("TWITTER_ACCESS_TOKEN", raising=False)
        monkeypatch.delenv("TWITTER_ACCESS_SECRET", raising=False)

        publisher = TwitterPublisher()
        result = publisher.publish("Test")

        assert result is False

    def test_verify_credentials_fails_without_client(self, monkeypatch):
        """verify_credentials() returns False if client is None."""
        monkeypatch.delenv("TWITTER_API_KEY", raising=False)
        monkeypatch.delenv("TWITTER_API_SECRET", raising=False)
        monkeypatch.delenv("TWITTER_ACCESS_TOKEN", raising=False)
        monkeypatch.delenv("TWITTER_ACCESS_SECRET", raising=False)

        publisher = TwitterPublisher()
        result = publisher.verify_credentials()

        assert result is False


class TestLinkedInPublisher:
    """Test LinkedIn publishing functionality."""

    def test_no_token_returns_false(self, monkeypatch):
        """Without LINKEDIN_ACCESS_TOKEN, publish returns False."""
        monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)
        publisher = LinkedInPublisher()
        result = publisher.publish("Test post")
        assert result is False

    def test_successful_post(self, monkeypatch):
        """Successful LinkedIn post returns True."""
        monkeypatch.setenv("LINKEDIN_ACCESS_TOKEN", "test_token")
        publisher = LinkedInPublisher()

        # Mock get_author_urn to return a valid URN
        with patch.object(
            publisher, "get_author_urn", return_value="urn:li:person:123"
        ):
            with patch("examples.herald.publisher.requests.post") as mock_post:
                mock_response = MagicMock()
                mock_response.status_code = 201
                mock_post.return_value = mock_response

                result = publisher.publish("Test post")
                assert result is True

    def test_failed_author_urn_returns_false(self, monkeypatch):
        """If get_author_urn fails, publish returns False."""
        monkeypatch.setenv("LINKEDIN_ACCESS_TOKEN", "test_token")
        publisher = LinkedInPublisher()

        with patch.object(publisher, "get_author_urn", return_value=None):
            result = publisher.publish("Test post")
            assert result is False


class TestMultiChannelPublisher:
    """Test unified multi-channel publishing."""

    def test_no_channels_graceful_fail(self, monkeypatch):
        """With no credentials, system still returns a valid result dict."""
        monkeypatch.delenv("TWITTER_API_KEY", raising=False)
        monkeypatch.delenv("TWITTER_API_SECRET", raising=False)
        monkeypatch.delenv("TWITTER_ACCESS_TOKEN", raising=False)
        monkeypatch.delenv("TWITTER_ACCESS_SECRET", raising=False)
        monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)

        publisher = MultiChannelPublisher()
        result = publisher.publish_to_all_available("Test content")

        assert isinstance(result, dict)
        assert "summary" in result
        assert result["twitter"] is False
        assert result["linkedin"] is False

    def test_twitter_only_configured(self, monkeypatch):
        """Only Twitter configured - only Twitter gets published to."""
        monkeypatch.setenv("TWITTER_API_KEY", "key")
        monkeypatch.setenv("TWITTER_API_SECRET", "secret")
        monkeypatch.setenv("TWITTER_ACCESS_TOKEN", "token")
        monkeypatch.setenv("TWITTER_ACCESS_SECRET", "token_secret")
        monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)

        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.create_tweet.return_value = MagicMock(data={"id": "123"})

            publisher = MultiChannelPublisher()
            result = publisher.publish_to_all_available("Test content")

            assert result["twitter"] is True
            assert "✅ Twitter" in result["summary"]
            assert result["linkedin"] is False

    def test_twitter_failure_reported(self, monkeypatch):
        """Twitter failure is recorded in the result."""
        monkeypatch.setenv("TWITTER_API_KEY", "key")
        monkeypatch.setenv("TWITTER_API_SECRET", "secret")
        monkeypatch.setenv("TWITTER_ACCESS_TOKEN", "token")
        monkeypatch.setenv("TWITTER_ACCESS_SECRET", "token_secret")

        import tweepy

        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.create_tweet.side_effect = tweepy.errors.Forbidden(
                response=MagicMock()
            )

            publisher = MultiChannelPublisher()
            result = publisher.publish_to_all_available("Test content")

            assert result["twitter"] is False
            assert "❌ Twitter" in result["summary"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
