"""Tests for NetworkIntel — agent profile cache + interest alignment."""

from unittest.mock import MagicMock

from vibe_core.cartridges.agent_city.moltbook.core.text_utils import tokenize
from vibe_core.plugins.moltbook.managers.network_intel import NetworkIntel


class TestTokenize:
    def test_basic_tokenization(self):
        tokens = tokenize("AI governance and transparent systems")
        assert "governance" in tokens
        assert "transparent" in tokens
        assert "systems" in tokens
        assert "and" not in tokens  # stop word

    def test_stop_words_removed(self):
        tokens = tokenize("the a an and or in on at to for of")
        assert len(tokens) == 0

    def test_short_words_removed(self):
        tokens = tokenize("AI is ok but ML works")
        assert "works" in tokens
        # "ai", "is", "ok", "ml" are <=2 chars → removed
        assert "ai" not in tokens
        assert "ok" not in tokens


class TestNetworkIntelInit:
    def test_default_init(self):
        ni = NetworkIntel()
        assert ni._max_profiles == 50
        assert ni._profiles == {}
        assert ni._agent_topics == {}

    def test_custom_max_profiles(self):
        ni = NetworkIntel(max_profiles=10)
        assert ni._max_profiles == 10


class TestEnrichFromFeed:
    def test_fetches_uncached_authors(self):
        ni = NetworkIntel()
        service = MagicMock()
        service.get_profile.return_value = {
            "name": "alice",
            "description": "AI safety researcher focused on alignment",
            "karma": 42,
        }

        topics = [
            {"id": "p1", "title": "Test", "author": {"name": "alice"}},
            {"id": "p2", "title": "Other", "author": {"name": "bob"}},
        ]
        ni.enrich_from_feed(service, topics, set(), own_name="steward-protocol")

        # Should have fetched alice and bob (2 uncached authors)
        assert service.get_profile.call_count == 2
        assert "alice" in ni._profiles
        assert "safety" in ni._agent_topics.get("alice", set())

    def test_skips_self(self):
        ni = NetworkIntel()
        service = MagicMock()
        topics = [{"id": "p1", "title": "X", "author": {"name": "steward-protocol"}}]
        ni.enrich_from_feed(service, topics, set(), own_name="steward-protocol")
        service.get_profile.assert_not_called()

    def test_skips_already_cached(self):
        ni = NetworkIntel()
        ni._profiles["alice"] = {"name": "alice"}
        ni._agent_topics["alice"] = {"safety"}

        service = MagicMock()
        topics = [{"id": "p1", "title": "X", "author": {"name": "alice"}}]
        ni.enrich_from_feed(service, topics, set())
        service.get_profile.assert_not_called()

    def test_max_3_api_calls(self):
        ni = NetworkIntel()
        service = MagicMock()
        service.get_profile.return_value = {"name": "x", "description": "test agent"}

        topics = [{"id": f"p{i}", "title": "X", "author": {"name": f"agent_{i}"}} for i in range(10)]
        ni.enrich_from_feed(service, topics, set())
        assert service.get_profile.call_count == 3  # Budget: max 3

    def test_enriches_topics_with_author_interests(self):
        ni = NetworkIntel()
        ni._agent_topics["alice"] = {"safety", "alignment", "research"}

        topics = [{"id": "p1", "title": "X", "author": {"name": "alice"}}]
        service = MagicMock()
        ni.enrich_from_feed(service, topics, set())

        assert "author_interests" in topics[0]
        assert set(topics[0]["author_interests"]) == {"safety", "alignment", "research"}

    def test_handles_api_failure_gracefully(self):
        ni = NetworkIntel()
        service = MagicMock()
        service.get_profile.side_effect = ConnectionError("timeout")

        topics = [{"id": "p1", "title": "X", "author": {"name": "alice"}}]
        ni.enrich_from_feed(service, topics, set())
        assert "alice" not in ni._profiles  # Not cached on failure

    def test_evicts_oldest_when_over_capacity(self):
        ni = NetworkIntel(max_profiles=2)
        ni._profiles = {"old1": {}, "old2": {}}
        ni._agent_topics = {"old1": set(), "old2": set()}
        ni._last_fetched = {"old1": 1.0, "old2": 2.0}

        service = MagicMock()
        service.get_profile.return_value = {"name": "new", "description": "fresh agent"}

        topics = [{"id": "p1", "title": "X", "author": {"name": "new"}}]
        ni.enrich_from_feed(service, topics, set())

        # old1 (oldest) should be evicted
        assert "old1" not in ni._profiles
        assert "new" in ni._profiles


class TestGetAgentInterests:
    def test_returns_cached_interests(self):
        ni = NetworkIntel()
        ni._agent_topics["alice"] = {"safety", "alignment"}
        assert ni.get_agent_interests("alice") == {"safety", "alignment"}

    def test_returns_empty_for_unknown(self):
        ni = NetworkIntel()
        assert ni.get_agent_interests("unknown") == set()


class TestFindComplementaryAgents:
    def test_finds_overlapping_agents(self):
        ni = NetworkIntel()
        ni._agent_topics = {
            "alice": {"safety", "alignment", "research"},
            "bob": {"trading", "markets", "finance"},
            "carol": {"safety", "governance", "alignment"},
        }
        results = ni.find_complementary_agents({"safety", "alignment"}, exclude=set())
        # carol and alice should match, bob should not
        names = [r[0] for r in results]
        assert "carol" in names or "alice" in names
        assert "bob" not in names

    def test_excludes_specified_agents(self):
        ni = NetworkIntel()
        ni._agent_topics = {
            "alice": {"safety", "alignment"},
            "bob": {"safety", "alignment"},
        }
        results = ni.find_complementary_agents({"safety", "alignment"}, exclude={"alice"})
        names = [r[0] for r in results]
        assert "alice" not in names
        assert "bob" in names

    def test_empty_keywords_returns_empty(self):
        ni = NetworkIntel()
        ni._agent_topics = {"alice": {"safety"}}
        assert ni.find_complementary_agents(set(), exclude=set()) == []

    def test_low_overlap_filtered_out(self):
        ni = NetworkIntel()
        ni._agent_topics = {
            "alice": {
                "safety",
                "alignment",
                "research",
                "governance",
                "policy",
                "ethics",
                "transparency",
                "accountability",
            },
        }
        # Only 1 shared word out of many → Jaccard < 0.15
        results = ni.find_complementary_agents({"safety"}, exclude=set())
        # Jaccard = 1/8 = 0.125 < 0.15 → filtered
        assert len(results) == 0


class TestFindLonelyPosts:
    def test_finds_lonely_posts(self):
        ni = NetworkIntel()
        posts = [
            {"id": "p1", "comment_count": 0, "upvotes": 0, "content": "A" * 60, "title": "Lonely post"},
            {"id": "p2", "comment_count": 5, "upvotes": 10, "content": "Popular", "title": "Popular"},
            {"id": "p3", "comment_count": 0, "upvotes": 1, "content": "B" * 60, "title": "Also lonely"},
        ]
        lonely = ni.find_lonely_posts(posts)
        ids = [p["id"] for p in lonely]
        assert "p1" in ids
        assert "p3" in ids
        assert "p2" not in ids

    def test_filters_short_content(self):
        ni = NetworkIntel()
        posts = [
            {"id": "p1", "comment_count": 0, "upvotes": 0, "content": "Short", "title": "X"},
        ]
        assert ni.find_lonely_posts(posts) == []

    def test_filters_posts_with_comments(self):
        ni = NetworkIntel()
        posts = [
            {"id": "p1", "comment_count": 1, "upvotes": 0, "content": "A" * 60, "title": "Has reply"},
        ]
        assert ni.find_lonely_posts(posts) == []

    def test_filters_high_upvotes(self):
        ni = NetworkIntel()
        posts = [
            {"id": "p1", "comment_count": 0, "upvotes": 5, "content": "A" * 60, "title": "Already noticed"},
        ]
        assert ni.find_lonely_posts(posts) == []


class TestSnapshotRestore:
    def test_roundtrip(self):
        ni = NetworkIntel()
        ni._profiles = {"alice": {"name": "alice", "karma": 42}}
        ni._agent_topics = {"alice": {"safety", "alignment"}}
        ni._last_fetched = {"alice": 1000.0}

        snap = ni.snapshot()

        ni2 = NetworkIntel()
        ni2.restore(snap)

        assert ni2._profiles == {"alice": {"name": "alice", "karma": 42}}
        assert ni2._agent_topics == {"alice": {"safety", "alignment"}}
        assert ni2._last_fetched == {"alice": 1000.0}

    def test_restore_invalid_data(self):
        ni = NetworkIntel()
        ni.restore("not a dict")
        assert ni._profiles == {}

    def test_restore_empty_dict(self):
        ni = NetworkIntel()
        ni.restore({})
        assert ni._profiles == {}
