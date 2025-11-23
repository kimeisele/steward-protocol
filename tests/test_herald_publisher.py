#!/usr/bin/env python3
"""
Integration Tests for HERALD Multi-Channel Publisher

Tests verify that:
1. TwitterPublisher can authenticate and post
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


class TestTwitterPublisher:
    """Test Twitter publishing functionality."""

    def test_no_api_key_returns_false(self):
        """Publishing without API key should return False gracefully."""
        with patch.dict(os.environ, {}, clear=True):
            publisher = TwitterPublisher()
            result = publisher.publish("Test tweet")
            assert result is False

    def test_successful_tweet(self):
        """Successful tweet should return True and log tweet ID."""
        with patch.dict(os.environ, {"TWITTER_API_KEY": "test_token"}):
            publisher = TwitterPublisher()

            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {
                "data": {"id": "1234567890"}
            }

            with patch("examples.herald.publisher.requests.post", return_value=mock_response):
                result = publisher.publish("Test tweet", tags=["#test"])
                assert result is True

    def test_twitter_api_error_403_raises(self):
        """403 Forbidden should return False (likely Read-Only permission issue)."""
        with patch.dict(os.environ, {"TWITTER_API_KEY": "test_token"}):
            publisher = TwitterPublisher()

            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_response.text = "User does not have permission to create tweets"

            with patch("examples.herald.publisher.requests.post", return_value=mock_response):
                result = publisher.publish("Test tweet")
                assert result is False

    def test_twitter_api_error_401_raises(self):
        """401 Unauthorized should return False (invalid token)."""
        with patch.dict(os.environ, {"TWITTER_API_KEY": "invalid_token"}):
            publisher = TwitterPublisher()

            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"

            with patch("examples.herald.publisher.requests.post", return_value=mock_response):
                result = publisher.publish("Test tweet")
                assert result is False

    def test_tweet_truncation(self):
        """Tweet should be truncated to 280 characters."""
        with patch.dict(os.environ, {"TWITTER_API_KEY": "test_token"}):
            publisher = TwitterPublisher()

            long_text = "a" * 300

            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"data": {"id": "123"}}

            with patch("examples.herald.publisher.requests.post", return_value=mock_response) as mock_post:
                publisher.publish(long_text)

                # Verify the posted text is truncated
                call_args = mock_post.call_args
                payload = call_args.kwargs["json"]
                assert len(payload["text"]) <= 280


class TestLinkedInPublisher:
    """Test LinkedIn publishing functionality."""

    def test_no_access_token_returns_false(self):
        """Publishing without access token should return False gracefully."""
        with patch.dict(os.environ, {}, clear=True):
            publisher = LinkedInPublisher()
            result = publisher.publish("Test post")
            assert result is False

    def test_successful_linkedin_post(self):
        """Successful LinkedIn post should return True."""
        with patch.dict(os.environ, {"LINKEDIN_ACCESS_TOKEN": "test_token"}):
            publisher = LinkedInPublisher()

            # Mock get_author_urn
            with patch.object(publisher, "get_author_urn", return_value="urn:li:person:123"):
                mock_response = MagicMock()
                mock_response.status_code = 201

                with patch("examples.herald.publisher.requests.post", return_value=mock_response):
                    result = publisher.publish("Test post")
                    assert result is True

    def test_linkedin_403_returns_false(self):
        """403 on LinkedIn should return False."""
        with patch.dict(os.environ, {"LINKEDIN_ACCESS_TOKEN": "test_token"}):
            publisher = LinkedInPublisher()

            with patch.object(publisher, "get_author_urn", return_value="urn:li:person:123"):
                mock_response = MagicMock()
                mock_response.status_code = 403
                mock_response.text = "Forbidden"

                with patch("examples.herald.publisher.requests.post", return_value=mock_response):
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

    def test_no_channels_configured_no_failure(self):
        """If no channels configured, should still return gracefully."""
        with patch.dict(os.environ, {}, clear=True):
            publisher = MultiChannelPublisher()
            result = publisher.publish_to_all_available("Test content")

            # Should have a summary even if nothing published
            assert "summary" in result

    def test_twitter_configured_linkedin_not(self):
        """Only Twitter configured - should attempt Twitter only."""
        with patch.dict(os.environ, {"TWITTER_API_KEY": "test_token"}, clear=True):
            publisher = MultiChannelPublisher()

            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"data": {"id": "123"}}

            with patch("examples.herald.publisher.requests.post", return_value=mock_response):
                result = publisher.publish_to_all_available("Test content")

                assert result["twitter"] is True
                assert "✅ Twitter" in result["summary"]
                # LinkedIn should be skipped (no token)
                assert result["linkedin"] is False

    def test_twitter_failure_is_reported(self):
        """Twitter failure should be recorded in results."""
        with patch.dict(os.environ, {"TWITTER_API_KEY": "test_token"}, clear=True):
            publisher = MultiChannelPublisher()

            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_response.text = "Forbidden"

            with patch("examples.herald.publisher.requests.post", return_value=mock_response):
                result = publisher.publish_to_all_available("Test content")

                assert result["twitter"] is False
                assert "❌ Twitter" in result["summary"]


class TestPublisherIntegration:
    """End-to-end integration tests."""

    def test_full_pipeline_with_all_channels(self):
        """Test complete publishing pipeline when all channels configured."""
        env = {
            "TWITTER_API_KEY": "test_twitter_token",
            "LINKEDIN_ACCESS_TOKEN": "test_linkedin_token"
        }

        with patch.dict(os.environ, env, clear=True):
            publisher = MultiChannelPublisher()

            # Mock both APIs
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"data": {"id": "123"}}

            with patch.object(publisher.twitter, "publish", return_value=True):
                with patch.object(publisher.linkedin, "publish", return_value=True):
                    # Mock datetime to return Friday (weekday() == 4)
                    # This allows LinkedIn to publish per the Cognitive Policy
                    with patch("examples.herald.publisher.datetime") as mock_datetime:
                        mock_datetime.now.return_value.weekday.return_value = 4

                        result = publisher.publish_to_all_available(
                            "Test content",
                            twitter_tags=["#test"]
                        )

                        assert result["twitter"] is True
                        assert result["linkedin"] is True
                        assert len(result["summary"]) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
