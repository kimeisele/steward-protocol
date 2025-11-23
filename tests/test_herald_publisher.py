import os
import pytest
from unittest.mock import MagicMock, patch

# Stelle sicher, dass der Pfad zu deinem Code stimmt
from examples.herald.publisher import TwitterPublisher, MultiChannelPublisher

class TestTwitterPublisher:

    # Der NATIVE Pytest Fix. Das funktioniert garantiert.
    @pytest.fixture(autouse=True)
    def setup_env(self, monkeypatch):
        monkeypatch.setenv("TWITTER_API_KEY", "fake_consumer_key")
        monkeypatch.setenv("TWITTER_API_SECRET", "fake_consumer_secret")
        monkeypatch.setenv("TWITTER_ACCESS_TOKEN", "fake_access_token")
        monkeypatch.setenv("TWITTER_ACCESS_SECRET", "fake_access_secret")

    def test_init_success(self):
        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            pub = TwitterPublisher()
            assert pub.client is not None

    def test_successful_tweet(self):
        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.create_tweet.return_value = MagicMock(data={"id": "12345"})

            publisher = TwitterPublisher()
            result = publisher.publish("Hello World")
            assert result is True

    def test_error_handling_403(self):
        import tweepy
        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.create_tweet.side_effect = tweepy.errors.Forbidden(response=MagicMock())

            publisher = TwitterPublisher()
            result = publisher.publish("Forbidden")
            assert result is False

class TestMultiChannelPublisher:
    @pytest.fixture(autouse=True)
    def setup_env(self, monkeypatch):
        monkeypatch.setenv("TWITTER_API_KEY", "key")
        monkeypatch.setenv("TWITTER_API_SECRET", "secret")
        monkeypatch.setenv("TWITTER_ACCESS_TOKEN", "token")
        monkeypatch.setenv("TWITTER_ACCESS_SECRET", "secret")

    def test_twitter_only_pipeline(self):
        with patch("examples.herald.publisher.tweepy.Client") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.create_tweet.return_value = MagicMock(data={"id": "123"})

            mp = MultiChannelPublisher()
            res = mp.publish_to_all_available("Test")
            assert res["twitter"] is True
