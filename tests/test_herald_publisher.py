import os
import pytest
from unittest.mock import MagicMock, patch
from examples.herald.publisher import TwitterPublisher, MultiChannelPublisher

class TestTwitterPublisher:
    @pytest.fixture(autouse=True)
    def setup_env(self, monkeypatch):
        monkeypatch.setenv("TWITTER_API_KEY", "fake")
        monkeypatch.setenv("TWITTER_API_SECRET", "fake")
        monkeypatch.setenv("TWITTER_ACCESS_TOKEN", "fake")
        monkeypatch.setenv("TWITTER_ACCESS_SECRET", "fake")

    def test_init_success(self):
        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            TwitterPublisher()

    def test_successful_tweet(self):
        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            mock = MockClient.return_value
            mock.create_tweet.return_value = MagicMock(data={"id": "123"})
            assert TwitterPublisher().publish("Test") is True
