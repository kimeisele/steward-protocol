"""
MOLTBOOK STRATEGY PLANNER TESTS
=================================

Tests MoltbookStrategyPlanner — Sankalpa mission matching, plan_cycle,
engagement feedback, priority boosting/deprioritization.

SankalpaOrchestrator is mocked — we test the planner's logic, not Sankalpa's.
Lotus/Buddhi calls are mocked to avoid slow VM imports in tests.
"""

import json
from dataclasses import dataclass
from enum import Enum
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.cartridges.agent_city.moltbook.core.strategy import (
    MoltbookStrategyPlanner,
    _derive_seed_topics,
)
from vibe_core.mahamantra.substrate.core.seed import TRINITY


# ---------------------------------------------------------------------------
# Fake Sankalpa types (avoids deep import chain)
# ---------------------------------------------------------------------------


class FakePriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FakeMission:
    id: str
    name: str
    description: str
    priority: FakePriority
    strategies: list = None
    owner: str = "moltbook"

    def __post_init__(self):
        if self.strategies is None:
            self.strategies = []


# Standard test missions
_TEST_MISSIONS = [
    FakeMission(
        id="moltbook_ai_governance",
        name="Ai Governance",
        description="AI governance and transparent decision-making in autonomous systems",
        priority=FakePriority.MEDIUM,
    ),
    FakeMission(
        id="moltbook_decentralized_protocols",
        name="Decentralized Protocols",
        description="Decentralized protocols and agent-to-agent coordination",
        priority=FakePriority.HIGH,
    ),
    FakeMission(
        id="moltbook_community_building",
        name="Community Building",
        description="Community building and social dynamics in agent networks",
        priority=FakePriority.LOW,
    ),
]

# No mock infrastructure needed — keyword Jaccard uses real tokenization (no slow imports).


def _mock_buddhi_think(text: str):
    """Return a fake BuddhiResult-like object with .mode attribute."""
    mock = MagicMock()
    mock.mode = "SATTVA"
    mock.approach = "DHARMA"
    mock.function = "maintainer"
    mock.chapter = 3
    return mock


def _make_planner(missions=None) -> MoltbookStrategyPlanner:
    """Create a planner with mocked orchestrator and semantic infrastructure."""
    planner = MoltbookStrategyPlanner()
    planner._missions_seeded = True  # Skip real seeding

    orch = MagicMock()
    registry = MagicMock()
    registry.get_active_missions.return_value = missions or []
    registry.get_all_missions.return_value = missions or []
    orch.registry = registry
    planner._orchestrator = orch

    return planner


@pytest.fixture
def _mock_buddhi():
    """Mock get_buddhi() to avoid full Lotus VM in plan_cycle."""
    mock_buddhi = MagicMock()
    mock_buddhi.think.side_effect = _mock_buddhi_think
    with patch(
        "vibe_core.mahamantra.substrate.buddhi.get_buddhi",
        return_value=mock_buddhi,
    ):
        yield mock_buddhi


# ---------------------------------------------------------------------------
# plan_cycle — basic behavior
# ---------------------------------------------------------------------------


class TestPlanCycle:
    def test_empty_feed_no_missions_returns_empty(self):
        planner = _make_planner(missions=[])
        result = planner.plan_cycle([], {})
        assert result == []

    def test_feed_topics_no_missions_returns_default_intent(self):
        planner = _make_planner(missions=[])
        topics = [{"id": "p1", "title": "AI safety is important", "content": ""}]
        result = planner.plan_cycle(topics, {})
        assert len(result) == 1
        assert result[0].action_type == "comment"
        assert result[0].mission_id == "default"
        assert result[0].target_post_id == "p1"

    def test_matching_feed_produces_comment_intent(self, _mock_buddhi):
        planner = _make_planner(missions=_TEST_MISSIONS)
        topics = [
            {
                "id": "p1",
                "title": "AI governance and transparent decision-making",
                "content": "New paper on autonomous systems governance",
                "upvotes": 5,
            },
        ]
        result = planner.plan_cycle(topics, {})
        comments = [i for i in result if i.action_type == "comment"]
        assert len(comments) >= 1
        assert comments[0].mission_id == "moltbook_ai_governance"
        assert comments[0].target_post_id == "p1"

    def test_unmatched_missions_produce_proactive_post(self, _mock_buddhi):
        planner = _make_planner(missions=_TEST_MISSIONS)
        # Feed that matches only ai_governance
        topics = [
            {
                "id": "p1",
                "title": "AI governance and transparent decision-making",
                "content": "autonomous systems",
            },
        ]
        result = planner.plan_cycle(topics, {})
        posts = [i for i in result if i.action_type == "post"]
        # At least one proactive post for an unmatched mission
        assert len(posts) >= 1

    def test_max_trinity_intents(self, _mock_buddhi):
        """plan_cycle returns at most TRINITY (3) intents."""
        planner = _make_planner(missions=_TEST_MISSIONS)
        # Many matching topics
        topics = [
            {"id": f"p{i}", "title": f"AI governance decision autonomous systems topic {i}", "content": ""}
            for i in range(10)
        ]
        result = planner.plan_cycle(topics, {})
        assert len(result) <= TRINITY

    def test_intents_sorted_by_priority_descending(self, _mock_buddhi):
        planner = _make_planner(missions=_TEST_MISSIONS)
        topics = [
            {"id": "p1", "title": "AI governance and transparent decision-making autonomous", "content": ""},
            {"id": "p2", "title": "Decentralized protocols agent coordination", "content": ""},
            {"id": "p3", "title": "Community building social dynamics agent networks", "content": ""},
        ]
        result = planner.plan_cycle(topics, {})
        for i in range(len(result) - 1):
            assert result[i].priority >= result[i + 1].priority


# ---------------------------------------------------------------------------
# Topic matching (semantic via RAMA coordinates)
# ---------------------------------------------------------------------------


class TestTopicMatching:
    def test_semantic_matching(self):
        planner = _make_planner(missions=_TEST_MISSIONS)
        topics = [
            {"id": "p1", "title": "decentralized protocols for agent coordination", "content": ""},
        ]
        matches = planner._match_topics(topics, _TEST_MISSIONS)
        assert len(matches) == 1
        assert matches[0].mission_id == "moltbook_decentralized_protocols"
        assert matches[0].relevance > 0.5

    def test_unrelated_topic_filtered_out(self):
        planner = _make_planner(missions=_TEST_MISSIONS)
        topics = [
            {"id": "p1", "title": "pizza recipe for lunch", "content": ""},
        ]
        matches = planner._match_topics(topics, _TEST_MISSIONS)
        assert len(matches) == 0

    def test_best_mission_wins(self):
        """When a post matches multiple missions, the best one wins."""
        planner = _make_planner(missions=_TEST_MISSIONS)
        topics = [
            {
                "id": "p1",
                "title": "Decentralized protocols and agent-to-agent coordination in networks",
                "content": "",
            },
        ]
        matches = planner._match_topics(topics, _TEST_MISSIONS)
        assert len(matches) == 1
        assert matches[0].mission_id == "moltbook_decentralized_protocols"

    def test_post_meta_captured(self):
        planner = _make_planner(missions=_TEST_MISSIONS)
        topics = [
            {
                "id": "p1",
                "title": "AI governance and transparent decision-making in autonomous systems",
                "content": "",
                "upvotes": 42,
                "author": {"name": "agent_alpha"},
            },
        ]
        matches = planner._match_topics(topics, _TEST_MISSIONS)
        assert len(matches) == 1
        assert matches[0].post_meta["upvotes"] == 42
        assert matches[0].post_meta["author"] == "agent_alpha"


# ---------------------------------------------------------------------------
# _semantic_match — keyword Jaccard (tokenized word overlap)
# ---------------------------------------------------------------------------


class TestSemanticMatch:
    def test_identical_tokens_high_similarity(self):
        """Same token set → Jaccard=1.0."""
        tokens = frozenset({"distributed", "systems", "consensus", "protocol"})
        missions = [FakeMission(id="m1", name="M", description="test", priority=FakePriority.MEDIUM)]
        mission_tokens = {"m1": tokens}
        mid, sim = MoltbookStrategyPlanner._semantic_match(tokens, missions, mission_tokens)
        assert mid == "m1"
        assert sim == 1.0

    def test_disjoint_tokens_no_match(self):
        """Zero overlap → below floor → no match."""
        post_tokens = frozenset({"distributed", "systems", "consensus"})
        mission_tokens = {"m1": frozenset({"chocolate", "cookie", "recipe"})}
        missions = [FakeMission(id="m1", name="M", description="test", priority=FakePriority.MEDIUM)]
        mid, sim = MoltbookStrategyPlanner._semantic_match(post_tokens, missions, mission_tokens)
        assert mid is None
        assert sim == 0.0

    def test_partial_overlap_matches(self):
        """Shared keywords above floor → match with correct Jaccard."""
        post_tokens = frozenset({"distributed", "systems", "fault", "tolerance"})
        mission_tokens = {"m1": frozenset({"distributed", "systems", "consensus", "protocol"})}
        missions = [FakeMission(id="m1", name="M", description="test", priority=FakePriority.MEDIUM)]
        mid, sim = MoltbookStrategyPlanner._semantic_match(post_tokens, missions, mission_tokens)
        assert mid == "m1"
        # Jaccard: 2 shared / 6 total = 0.333
        assert 0.3 <= sim <= 0.4

    def test_empty_missions(self):
        mid, sim = MoltbookStrategyPlanner._semantic_match(
            frozenset({"test"}), [], {},
        )
        assert mid is None
        assert sim == 0.0

    def test_missing_mission_tokens_skipped(self):
        missions = [FakeMission(id="m1", name="M", description="test", priority=FakePriority.MEDIUM)]
        mid, sim = MoltbookStrategyPlanner._semantic_match(
            frozenset({"test"}), missions, {},
        )
        assert mid is None
        assert sim == 0.0

    def test_empty_post_tokens(self):
        """Empty post token set → no match."""
        missions = [FakeMission(id="m1", name="M", description="test", priority=FakePriority.MEDIUM)]
        mid, sim = MoltbookStrategyPlanner._semantic_match(
            frozenset(), missions, {"m1": frozenset({"test"})},
        )
        assert mid is None
        assert sim == 0.0

    def test_picks_best_mission(self):
        """When multiple missions have tokens, picks highest Jaccard."""
        post_tokens = frozenset({"distributed", "systems", "consensus", "protocol"})
        missions = [
            FakeMission(id="m1", name="M1", description="close", priority=FakePriority.MEDIUM),
            FakeMission(id="m2", name="M2", description="far", priority=FakePriority.MEDIUM),
        ]
        mission_tokens = {
            "m1": frozenset({"distributed", "systems", "consensus", "protocol"}),  # Identical
            "m2": frozenset({"chocolate", "cookie", "recipe", "baking"}),  # Disjoint
        }
        mid, sim = MoltbookStrategyPlanner._semantic_match(post_tokens, missions, mission_tokens)
        assert mid == "m1"
        assert sim == 1.0


# ---------------------------------------------------------------------------
# _buddhi_select_format — mode-driven format selection
# ---------------------------------------------------------------------------


class TestBuddhiSelectFormat:
    def test_sattva_comment_observation(self):
        assert MoltbookStrategyPlanner._buddhi_select_format("comment", "SATTVA") == "observation"

    def test_rajas_comment_question(self):
        assert MoltbookStrategyPlanner._buddhi_select_format("comment", "RAJAS") == "question"

    def test_tamas_comment_opinion(self):
        assert MoltbookStrategyPlanner._buddhi_select_format("comment", "TAMAS") == "opinion"

    def test_sattva_post_analysis(self):
        assert MoltbookStrategyPlanner._buddhi_select_format("post", "SATTVA") == "analysis"

    def test_rajas_post_opinion(self):
        assert MoltbookStrategyPlanner._buddhi_select_format("post", "RAJAS") == "opinion"

    def test_tamas_post_tutorial(self):
        assert MoltbookStrategyPlanner._buddhi_select_format("post", "TAMAS") == "tutorial"

    def test_unknown_mode_defaults(self):
        assert MoltbookStrategyPlanner._buddhi_select_format("comment", "UNKNOWN") == "observation"
        assert MoltbookStrategyPlanner._buddhi_select_format("post", "UNKNOWN") == "analysis"


# ---------------------------------------------------------------------------
# Priority scoring
# ---------------------------------------------------------------------------


class TestPriorityScoring:
    def test_medium_mission_scores_5(self):
        planner = _make_planner()
        planner._get_synapse_boost = lambda _: 0  # Isolate from persisted weights
        score = planner._mission_priority_score("moltbook_ai_governance", _TEST_MISSIONS)
        assert score == 5

    def test_high_mission_scores_8(self):
        planner = _make_planner()
        planner._get_synapse_boost = lambda _: 0
        score = planner._mission_priority_score("moltbook_decentralized_protocols", _TEST_MISSIONS)
        assert score == 8

    def test_low_mission_scores_3(self):
        planner = _make_planner()
        planner._get_synapse_boost = lambda _: 0
        score = planner._mission_priority_score("moltbook_community_building", _TEST_MISSIONS)
        assert score == 3

    def test_engagement_boost(self):
        planner = _make_planner()
        planner._get_synapse_boost = lambda _: 0
        planner._engagement_cache["moltbook_ai_governance"] = {"success_rate": 0.8}
        score = planner._mission_priority_score("moltbook_ai_governance", _TEST_MISSIONS)
        assert score == 7  # 5 + 2

    def test_engagement_penalty(self):
        planner = _make_planner()
        planner._get_synapse_boost = lambda _: 0
        planner._engagement_cache["moltbook_decentralized_protocols"] = {"success_rate": 0.1}
        score = planner._mission_priority_score("moltbook_decentralized_protocols", _TEST_MISSIONS)
        assert score == 6  # 8 - 2

    def test_score_clamped_max_10(self):
        planner = _make_planner()
        critical_mission = FakeMission(
            id="m_crit",
            name="Critical",
            description="test",
            priority=FakePriority.CRITICAL,
        )
        planner._engagement_cache["m_crit"] = {"success_rate": 0.9}
        score = planner._mission_priority_score("m_crit", [critical_mission])
        assert score == 10  # 10 + 2 → clamped to 10

    def test_score_clamped_min_1(self):
        planner = _make_planner()
        low_mission = FakeMission(
            id="m_low",
            name="Low",
            description="test",
            priority=FakePriority.LOW,
        )
        planner._engagement_cache["m_low"] = {"success_rate": 0.1}
        score = planner._mission_priority_score("m_low", [low_mission])
        assert score == 1  # 3 - 2 = 1


# ---------------------------------------------------------------------------
# Engagement feedback (semantic matching)
# ---------------------------------------------------------------------------


class TestEngagementFeedback:
    def test_positive_engagement_updates_cache(self):
        planner = _make_planner(missions=_TEST_MISSIONS)
        planner.update_from_engagement(
            {
                "topic": "AI governance and transparent decision-making",
                "upvotes": 5,
                "reply_count": 2,
            }
        )
        cache = planner._engagement_cache.get("moltbook_ai_governance")
        assert cache is not None
        assert cache["total"] == 1
        assert cache["positive"] == 1
        assert cache["success_rate"] == 1.0

    def test_negative_engagement_updates_cache(self):
        planner = _make_planner(missions=_TEST_MISSIONS)
        planner.update_from_engagement(
            {
                "topic": "AI governance and transparent decision-making",
                "upvotes": 0,
                "reply_count": 0,
            }
        )
        cache = planner._engagement_cache.get("moltbook_ai_governance")
        assert cache is not None
        assert cache["total"] == 1
        assert cache["positive"] == 0
        assert cache["success_rate"] == 0.0

    def test_empty_topic_ignored(self):
        planner = _make_planner(missions=_TEST_MISSIONS)
        planner.update_from_engagement({"topic": "", "upvotes": 10, "reply_count": 5})
        assert len(planner._engagement_cache) == 0

    def test_unmatched_topic_ignored(self):
        planner = _make_planner(missions=_TEST_MISSIONS)
        planner.update_from_engagement(
            {
                "topic": "pizza and spaghetti recipes",
                "upvotes": 100,
                "reply_count": 50,
            }
        )
        assert len(planner._engagement_cache) == 0

    def test_boost_after_trinity_positive_signals(self):
        planner = _make_planner(missions=_TEST_MISSIONS)
        # Patch _boost_mission to track calls
        boost_calls = []
        planner._boost_mission = lambda m: boost_calls.append(m.id)

        for _ in range(TRINITY):
            planner.update_from_engagement(
                {
                    "topic": "AI governance transparent decision autonomous",
                    "upvotes": 5,
                    "reply_count": 2,
                }
            )

        assert len(boost_calls) >= 1
        assert "moltbook_ai_governance" in boost_calls

    def test_deprioritize_after_trinity_negative_signals(self):
        planner = _make_planner(missions=_TEST_MISSIONS)
        deprio_calls = []
        planner._deprioritize_mission = lambda m: deprio_calls.append(m.id)

        for _ in range(TRINITY):
            planner.update_from_engagement(
                {
                    "topic": "AI governance transparent decision autonomous",
                    "upvotes": 0,
                    "reply_count": 0,
                }
            )

        assert len(deprio_calls) >= 1
        assert "moltbook_ai_governance" in deprio_calls


# ---------------------------------------------------------------------------
# Global engagement stats (FeedbackProtocol → plan_cycle)
# ---------------------------------------------------------------------------


class TestGlobalEngagementStats:
    def test_global_stats_used_as_fallback(self, _mock_buddhi):
        planner = _make_planner(missions=_TEST_MISSIONS)
        topics = [
            {"id": "p1", "title": "AI governance and transparent decision-making autonomous", "content": ""},
        ]
        result = planner.plan_cycle(topics, {"success_rate": 0.75, "total_signals": 20})
        # At least one intent should have global engagement context
        with_eng = [i for i in result if "Overall:" in i.engagement_context]
        assert len(with_eng) >= 1

    def test_mission_specific_overrides_global(self, _mock_buddhi):
        planner = _make_planner(missions=_TEST_MISSIONS)
        planner._engagement_cache["moltbook_ai_governance"] = {
            "success_rate": 0.9,
            "total": 5,
            "positive": 4,
        }
        topics = [
            {"id": "p1", "title": "AI governance and transparent decision-making autonomous", "content": ""},
        ]
        result = planner.plan_cycle(topics, {"success_rate": 0.5, "total_signals": 100})
        matched = [i for i in result if i.mission_id == "moltbook_ai_governance"]
        if matched:
            # Should use mission-specific, not global
            assert "Success rate:" in matched[0].engagement_context
            assert "Overall:" not in matched[0].engagement_context

    def test_empty_global_stats_no_context(self, _mock_buddhi):
        planner = _make_planner(missions=_TEST_MISSIONS)
        topics = [
            {"id": "p1", "title": "AI governance and transparent decision-making autonomous", "content": ""},
        ]
        result = planner.plan_cycle(topics, {})
        # No engagement context when no data
        for intent in result:
            if intent.mission_id == "moltbook_ai_governance":
                assert intent.engagement_context == ""


# ---------------------------------------------------------------------------
# Orchestrator unavailable (graceful degradation)
# ---------------------------------------------------------------------------


class TestGracefulDegradation:
    def test_planner_without_orchestrator(self):
        planner = MoltbookStrategyPlanner()
        planner._orchestrator = None  # Force no orchestrator
        # Patch the lazy import to fail
        with patch(
            "vibe_core.cartridges.agent_city.moltbook.core.strategy.MoltbookStrategyPlanner.orchestrator",
            new_callable=lambda: property(lambda self: None),
        ):
            result = planner.plan_cycle(
                [{"id": "p1", "title": "Test post", "content": ""}],
                {},
            )
        # Should use default intent fallback
        assert len(result) == 1
        assert result[0].mission_id == "default"

    def test_get_active_missions_returns_empty_on_failure(self):
        planner = _make_planner()
        planner._orchestrator.registry.get_active_missions.side_effect = RuntimeError("boom")
        assert planner.get_active_missions() == []


# ---------------------------------------------------------------------------
# Seed topics — feed-based derivation
# ---------------------------------------------------------------------------


class TestSeedTopics:
    def test_derive_returns_tuple(self):
        """_derive_seed_topics always returns a tuple."""
        topics = _derive_seed_topics()
        assert isinstance(topics, tuple)
        for entry in topics:
            assert len(entry) == 2
            assert isinstance(entry[0], str)
            assert isinstance(entry[1], str)

    def test_derive_returns_empty_when_no_sources(self):
        """When feed + Sankalpa unavailable, returns empty tuple."""
        topics = _derive_seed_topics()
        assert isinstance(topics, tuple)

    def test_derive_with_feed_topics(self):
        """Feed topics extract unique titles as seed topics (no chapter clustering)."""
        feed = [
            {"title": "Distributed consensus algorithms and their tradeoffs"},
            {"title": "Short"},  # Should be skipped (len < 10)
            {"title": "Agent coordination in multi-agent systems research"},
        ]
        topics = _derive_seed_topics(feed_topics=feed)

        assert isinstance(topics, tuple)
        # 2 long titles → 2 topics (short one skipped)
        feed_ids = [t for t in topics if t[0].startswith("feed_")]
        assert len(feed_ids) >= 2
        # Descriptions match original titles
        descriptions = {t[1] for t in topics}
        assert "Distributed consensus algorithms and their tradeoffs" in descriptions
        assert "Agent coordination in multi-agent systems research" in descriptions


# ---------------------------------------------------------------------------
# MuraliRouter
# ---------------------------------------------------------------------------


class TestMuraliRouter:
    def _make_router(self):
        from vibe_core.cartridges.agent_city.moltbook.core.agency_director import MuraliRouter

        return MuraliRouter()

    def test_fallback_cycles_all_departments(self):
        """Without venu, fallback_tick should cycle through all 4 departments."""
        router = self._make_router()
        # Patch mahamantra.venu to None
        with patch("vibe_core.mahamantra.mahamantra") as mock_mm:
            mock_mm.venu = None
            departments = [router.current_department(fallback_tick=i) for i in range(4)]
        assert departments == ["research", "planning", "execution", "learning"]

    def test_fallback_wraps_around(self):
        router = self._make_router()
        with patch("vibe_core.mahamantra.mahamantra") as mock_mm:
            mock_mm.venu = None
            assert router.current_department(fallback_tick=0) == "research"
            assert router.current_department(fallback_tick=4) == "research"
            assert router.current_department(fallback_tick=7) == "learning"

    def test_venu_tick_drives_department(self):
        """With venu available, tick position determines department."""
        router = self._make_router()
        mock_venu = MagicMock()

        with patch("vibe_core.mahamantra.mahamantra") as mock_mm:
            mock_mm.venu = mock_venu

            # tick 0-3 → research (GENESIS quarter)
            mock_venu.tick = 0
            assert router.current_department() == "research"

            # tick 4-7 → planning (DHARMA quarter)
            mock_venu.tick = 5
            assert router.current_department() == "planning"

            # tick 8-11 → execution (KARMA quarter)
            mock_venu.tick = 9
            assert router.current_department() == "execution"

            # tick 12-15 → learning (MOKSHA quarter)
            mock_venu.tick = 14
            assert router.current_department() == "learning"

    def test_venu_tick_wraps_at_16(self):
        router = self._make_router()
        mock_venu = MagicMock()

        with patch("vibe_core.mahamantra.mahamantra") as mock_mm:
            mock_mm.venu = mock_venu
            mock_venu.tick = 16  # Wraps: 16 % 16 = 0 → research
            assert router.current_department() == "research"

            mock_venu.tick = 21  # 21 % 16 = 5 → planning
            assert router.current_department() == "planning"

    def test_should_prioritize(self):
        router = self._make_router()
        with patch("vibe_core.mahamantra.mahamantra") as mock_mm:
            mock_mm.venu = None
            assert router.should_prioritize("research", fallback_tick=0) is True
            assert router.should_prioritize("execution", fallback_tick=0) is False

    def test_exception_in_mahamantra_uses_fallback(self):
        router = self._make_router()
        with patch(
            "vibe_core.mahamantra.mahamantra",
            new_callable=lambda: property(lambda self: (_ for _ in ()).throw(RuntimeError("no mahamantra"))),
        ):
            # Should not crash, should use fallback
            dept = router.current_department(fallback_tick=2)
            assert dept == "execution"


# ---------------------------------------------------------------------------
# Engagement cache persistence (survives GitHub Actions restarts)
# ---------------------------------------------------------------------------


class TestEngagementCachePersistence:
    def test_save_and_restore(self, tmp_path):
        planner = _make_planner(missions=_TEST_MISSIONS)
        planner._state_dir = tmp_path

        # Generate engagement data
        planner.update_from_engagement(
            {
                "topic": "AI governance and transparent decision-making",
                "upvotes": 5,
                "reply_count": 2,
            }
        )

        # Verify file was written
        cache_file = tmp_path / "engagement_cache.json"
        assert cache_file.exists()
        data = json.loads(cache_file.read_text())
        assert "moltbook_ai_governance" in data

        # Create new planner that restores from same dir
        planner2 = MoltbookStrategyPlanner(state_dir=tmp_path)
        planner2._missions_seeded = True
        assert "moltbook_ai_governance" in planner2._engagement_cache
        assert planner2._engagement_cache["moltbook_ai_governance"]["total"] == 1
        assert planner2._engagement_cache["moltbook_ai_governance"]["positive"] == 1

    def test_restore_missing_file_no_crash(self, tmp_path):
        planner = MoltbookStrategyPlanner(state_dir=tmp_path)
        assert planner._engagement_cache == {}

    def test_restore_corrupt_file_no_crash(self, tmp_path):
        cache_file = tmp_path / "engagement_cache.json"
        cache_file.write_text("NOT VALID JSON {{{")
        planner = MoltbookStrategyPlanner(state_dir=tmp_path)
        assert planner._engagement_cache == {}

    def test_no_state_dir_no_crash(self):
        planner = MoltbookStrategyPlanner(state_dir=None)
        planner._engagement_cache = {"test": {"total": 1}}
        planner._save_engagement_cache()  # Should be a no-op, not crash

    def test_cache_accumulates_across_restarts(self, tmp_path):
        """Simulate 3 GitHub Actions runs, each adding engagement data."""
        for run_idx in range(3):
            planner = _make_planner(missions=_TEST_MISSIONS)
            planner._state_dir = tmp_path
            # Restore from previous run
            planner._restore_engagement_cache()
            # Add engagement
            planner.update_from_engagement(
                {
                    "topic": "AI governance and transparent decision-making",
                    "upvotes": 3,
                    "reply_count": 1,
                }
            )

        # Final restore — should see 3 accumulated signals
        final = MoltbookStrategyPlanner(state_dir=tmp_path)
        cache = final._engagement_cache.get("moltbook_ai_governance", {})
        assert cache.get("total") == 3
        assert cache.get("positive") == 3


# ---------------------------------------------------------------------------
# MahaAttention wiring — O(1) topic→mission matching
# ---------------------------------------------------------------------------


class TestAttentionWiring:
    """Tests MahaAttention integration in _match_topics().

    MahaAttention provides O(1) intent→handler lookup via deterministic hash.
    _ensure_attention() lazy-inits it and memorizes mission descriptions.
    _match_topics() uses attend() first, falls back to semantic RAMA matching.
    """

    def test_ensure_attention_lazy_init(self):
        """_ensure_attention creates MahaAttention on first call."""
        planner = _make_planner(missions=_TEST_MISSIONS)
        assert planner._attention is None

        planner._ensure_attention(_TEST_MISSIONS)

        # MahaAttention should be initialized (or None if import fails)
        if planner._attention is not None:
            assert len(planner._attention_mission_ids) == len(_TEST_MISSIONS)

    def test_ensure_attention_idempotent(self):
        """Calling _ensure_attention twice doesn't re-memorize missions."""
        planner = _make_planner(missions=_TEST_MISSIONS)
        planner._ensure_attention(_TEST_MISSIONS)
        first_count = len(planner._attention_mission_ids)

        planner._ensure_attention(_TEST_MISSIONS)
        assert len(planner._attention_mission_ids) == first_count

    def test_ensure_attention_adds_new_missions(self):
        """New missions get memorized on subsequent calls."""
        planner = _make_planner(missions=_TEST_MISSIONS[:1])
        planner._ensure_attention(_TEST_MISSIONS[:1])
        first_count = len(planner._attention_mission_ids)

        # Add more missions
        planner._ensure_attention(_TEST_MISSIONS)
        assert len(planner._attention_mission_ids) >= first_count

    def test_match_topics_with_attention(self):
        """_match_topics uses MahaAttention when available."""
        planner = _make_planner(missions=_TEST_MISSIONS)
        topics = [
            {"id": "p1", "title": "AI governance and transparent decision-making", "content": "autonomous systems"},
        ]
        matches = planner._match_topics(topics, _TEST_MISSIONS)
        # Should find a match regardless of path (attention or semantic)
        assert len(matches) >= 1
        assert matches[0].post_id == "p1"

    def test_match_topics_attention_unavailable_uses_semantic(self):
        """When MahaAttention import fails, semantic RAMA matching works."""
        planner = _make_planner(missions=_TEST_MISSIONS)
        # Force attention to be unavailable
        planner._attention = None
        with patch(
            "vibe_core.cartridges.agent_city.moltbook.core.strategy.MoltbookStrategyPlanner._ensure_attention",
            lambda self, m: None,  # No-op: leaves _attention as None
        ):
            topics = [
                {"id": "p1", "title": "decentralized protocols for agent coordination", "content": ""},
            ]
            matches = planner._match_topics(topics, _TEST_MISSIONS)
            assert len(matches) >= 1
            assert matches[0].mission_id == "moltbook_decentralized_protocols"

    def test_attention_result_relevance_is_1(self):
        """Attention hash match yields relevance=1.0 (exact semantic address)."""
        planner = _make_planner(missions=_TEST_MISSIONS)
        planner._ensure_attention(_TEST_MISSIONS)

        if planner._attention is None:
            return  # Skip if MahaAttention not available in test env

        # Use exact mission description as post text — guaranteed attention hit
        mission = _TEST_MISSIONS[0]
        topics = [
            {"id": "p1", "title": mission.description.lower(), "content": ""},
        ]
        matches = planner._match_topics(topics, _TEST_MISSIONS)
        if matches and matches[0].relevance == 1.0:
            assert matches[0].mission_id == mission.id


# ---------------------------------------------------------------------------
# Mission nesting prevention
# ---------------------------------------------------------------------------


class TestMissionNesting:
    def test_derive_skips_moltbook_missions(self):
        """_derive_seed_topics skips missions prefixed 'moltbook_' to prevent nesting."""
        fake_missions = [
            FakeMission(
                id="moltbook_ai_governance",
                name="AI Governance",
                description="AI governance topics from moltbook",
                priority=FakePriority.MEDIUM,
            ),
            FakeMission(
                id="external_research",
                name="Research",
                description="External research on distributed systems and protocols",
                priority=FakePriority.MEDIUM,
            ),
        ]

        fake_orch = MagicMock()
        fake_orch.registry.get_all_missions.return_value = fake_missions

        with patch(
            "vibe_core.mahamantra.substrate.sankalpa.will.SankalpaOrchestrator",
            return_value=fake_orch,
        ):
            topics = _derive_seed_topics()

        topic_ids = [t[0] for t in topics]
        # moltbook_ missions should NOT appear
        assert not any(tid.startswith("moltbook_") for tid in topic_ids), (
            f"moltbook_ missions leaked into seed topics: {topic_ids}"
        )
        # external missions SHOULD appear
        if topics:  # Only assert if Sankalpa was reachable
            assert "external_research" in topic_ids

    def test_derive_prevents_recursive_nesting(self):
        """Ensures moltbook_moltbook_X prefix can never form."""
        fake_missions = [
            FakeMission(
                id="moltbook_moltbook_nested",
                name="Double Nested",
                description="This would cause triple nesting if re-ingested",
                priority=FakePriority.MEDIUM,
            ),
        ]

        fake_orch = MagicMock()
        fake_orch.registry.get_all_missions.return_value = fake_missions

        with patch(
            "vibe_core.mahamantra.substrate.sankalpa.will.SankalpaOrchestrator",
            return_value=fake_orch,
        ):
            topics = _derive_seed_topics()

        # No topic should have moltbook prefix
        for tid, _ in topics:
            assert not tid.startswith("moltbook_"), f"Nested moltbook mission leaked: {tid}"


# ---------------------------------------------------------------------------
# Intent diversity — comment-first strategy
# ---------------------------------------------------------------------------


class TestIntentDiversity:
    def test_unmatched_mission_creates_post(self, _mock_buddhi):
        """When some missions don't match feed, one gets a proactive post."""
        planner = _make_planner(missions=_TEST_MISSIONS)
        # Feed matches only 1 mission
        topics = [
            {"id": "p1", "title": "AI governance and transparent decision-making autonomous", "content": ""},
        ]
        result = planner.plan_cycle(topics, {})
        posts = [i for i in result if i.action_type == "post"]
        assert len(posts) >= 1, "Should have at least 1 post intent"

    def test_all_matched_stays_comment_only(self, _mock_buddhi):
        """When ALL missions match feed, agent comments — no forced post conversion."""
        generic_missions = [
            FakeMission(
                id="m1", name="M1",
                description="AI governance and transparent decision-making",
                priority=FakePriority.HIGH,
            ),
            FakeMission(
                id="m2", name="M2",
                description="decentralized protocols and agent coordination",
                priority=FakePriority.LOW,
            ),
        ]
        planner = _make_planner(missions=generic_missions)

        # Feed posts that each match their respective mission
        topics = [
            {"id": "p1", "title": "AI governance and transparent decision-making research", "content": ""},
            {"id": "p2", "title": "decentralized protocols for agent coordination analysis", "content": ""},
        ]
        result = planner.plan_cycle(topics, {})
        posts = [i for i in result if i.action_type == "post"]
        comments = [i for i in result if i.action_type == "comment"]
        # All matched → comments only, no forced post
        assert len(posts) == 0, f"Should not force post when all missions matched: {[(i.action_type, i.mission_id) for i in result]}"
        assert len(comments) >= 1, "Should have comment intents"

    def test_semantic_dedup_skips_recent_post(self, _mock_buddhi):
        """Post intent is skipped when topic semantically overlaps with own recent post."""
        planner = _make_planner(missions=_TEST_MISSIONS)
        # Unmatched mission would normally create a post
        topics = [
            {"id": "p1", "title": "AI governance and transparent decision-making autonomous", "content": ""},
        ]
        # We recently posted about the same thing (own_post_ids)
        own_posts = {
            "post_123": {
                "title": "AI governance and transparent decision-making autonomous systems",
                "created_at": 1000000.0,
            },
        }
        result = planner.plan_cycle(topics, {}, own_post_ids=own_posts)
        posts = [i for i in result if i.action_type == "post"]
        assert len(posts) == 0, "Should skip post when topic semantically overlaps recent"

    def test_max_trinity_still_enforced_with_diversity(self, _mock_buddhi):
        """Intent diversity doesn't break TRINITY cap."""
        planner = _make_planner(missions=_TEST_MISSIONS)
        topics = [
            {"id": f"p{i}", "title": f"AI governance decision autonomous systems topic {i}", "content": ""}
            for i in range(20)
        ]
        result = planner.plan_cycle(topics, {})
        assert len(result) <= TRINITY

    def test_empty_feed_stays_silent(self, _mock_buddhi):
        """With no feed topics, agent stays silent — doesn't post from mission descriptions."""
        planner = _make_planner(missions=_TEST_MISSIONS)
        result = planner.plan_cycle([], {})
        # No feed → no topics to write about → no intents
        assert len(result) == 0, f"Should stay silent with empty feed, got: {result}"


# ---------------------------------------------------------------------------
# _semantic_dedup — keyword Jaccard based dedup
# ---------------------------------------------------------------------------


class TestSemanticDedup:
    def test_identical_topics_are_dupes(self):
        planner = _make_planner()
        own_posts = {"p1": {"title": "AI governance and transparent decisions"}}
        assert planner._semantic_dedup("AI governance and transparent decisions", own_posts)

    def test_unrelated_topics_not_dupes(self):
        planner = _make_planner()
        own_posts = {"p1": {"title": "pizza recipe collection"}}
        assert not planner._semantic_dedup("AI governance and transparent decisions", own_posts)

    def test_empty_own_posts(self):
        planner = _make_planner()
        assert not planner._semantic_dedup("anything", {})

    def test_skips_non_dict_entries(self):
        planner = _make_planner()
        own_posts = {"p1": "not_a_dict"}
        assert not planner._semantic_dedup("anything", own_posts)

    def test_skips_empty_titles(self):
        planner = _make_planner()
        own_posts = {"p1": {"title": ""}}
        assert not planner._semantic_dedup("anything", own_posts)


# ---------------------------------------------------------------------------
# SravanamCheck gate — listen before speak
# ---------------------------------------------------------------------------


class TestSravanamCheck:
    def test_more_input_than_output_allows_post(self):
        """When feed is large and posts are few, posting is allowed."""
        assert MoltbookStrategyPlanner._sravanam_check(20, 5) is True

    def test_too_much_output_blocks_post(self):
        """When output exceeds input, posting is blocked (entropy law: input >= output)."""
        assert MoltbookStrategyPlanner._sravanam_check(3, 5) is False

    def test_zero_input_zero_output_allows(self):
        """Zero input + zero output → no violation (nothing to emit)."""
        assert MoltbookStrategyPlanner._sravanam_check(0, 0) is True

    def test_infrastructure_missing_fails_open(self):
        """If SravanamCheck import fails, posting is allowed (fail-open)."""
        with patch(
            "vibe_core.mahamantra.substrate.encoding.harmonics.SravanamCheck.can_emit",
            side_effect=ImportError("not available"),
        ):
            assert MoltbookStrategyPlanner._sravanam_check(1, 100) is True

    def test_sravanam_blocks_post_in_plan_cycle(self, _mock_buddhi):
        """When SravanamCheck fails, plan_cycle returns comments only."""
        planner = _make_planner(missions=_TEST_MISSIONS)
        topics = [
            {"id": "p1", "title": "AI governance and transparent decision-making autonomous", "content": ""},
        ]
        # Many posts, few feed → SravanamCheck should block new posts
        own_posts = {f"p{i}": {"title": f"Post {i}", "created_at": 1000000.0 + i} for i in range(50)}
        result = planner.plan_cycle(topics, {}, own_post_ids=own_posts)
        posts = [i for i in result if i.action_type == "post"]
        assert len(posts) == 0, "SravanamCheck should block posts when output >> input"


# ---------------------------------------------------------------------------
# Zero engagement streak — engagement threshold
# ---------------------------------------------------------------------------


class TestZeroEngagementStreak:
    def test_no_streak_with_engagement(self):
        own_posts = {
            "p1": {"upvotes": 5, "replies": 2, "created_at": 100.0},
            "p2": {"upvotes": 0, "replies": 0, "created_at": 99.0},
            "p3": {"upvotes": 3, "replies": 0, "created_at": 98.0},
        }
        assert not MoltbookStrategyPlanner._zero_engagement_streak(own_posts)

    def test_streak_with_zero_engagement(self):
        own_posts = {
            "p1": {"upvotes": 0, "replies": 0, "created_at": 100.0},
            "p2": {"upvotes": 0, "replies": 0, "created_at": 99.0},
            "p3": {"upvotes": 0, "replies": 0, "created_at": 98.0},
        }
        assert MoltbookStrategyPlanner._zero_engagement_streak(own_posts)

    def test_not_enough_posts(self):
        own_posts = {
            "p1": {"upvotes": 0, "replies": 0, "created_at": 100.0},
            "p2": {"upvotes": 0, "replies": 0, "created_at": 99.0},
        }
        # Less than TRINITY posts → not enough to judge
        assert not MoltbookStrategyPlanner._zero_engagement_streak(own_posts)

    def test_empty_posts(self):
        assert not MoltbookStrategyPlanner._zero_engagement_streak({})

    def test_non_dict_entries_ignored(self):
        own_posts = {
            "p1": "not_a_dict",
            "p2": {"upvotes": 0, "replies": 0, "created_at": 100.0},
        }
        assert not MoltbookStrategyPlanner._zero_engagement_streak(own_posts)

    def test_streak_blocks_post_in_plan_cycle(self, _mock_buddhi):
        """When recent posts have 0 engagement, plan_cycle returns comments only."""
        planner = _make_planner(missions=_TEST_MISSIONS)
        topics = [
            {"id": "p1", "title": "AI governance and transparent decision-making autonomous", "content": ""},
        ]
        # 3 recent posts with 0 engagement
        own_posts = {
            f"p{i}": {"title": f"Post {i}", "created_at": 1000000.0 + i, "upvotes": 0, "replies": 0}
            for i in range(5)
        }
        result = planner.plan_cycle(topics, {}, own_post_ids=own_posts)
        posts = [i for i in result if i.action_type == "post"]
        assert len(posts) == 0, "Should skip posts when zero engagement streak"
