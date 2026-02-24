"""
Moltbook Strategy Planner — Sankalpa → Strategic Intents.

Wires the existing SankalpaOrchestrator to drive Moltbook content decisions.
Instead of commenting on ALL posts or concatenating random feed titles,
the agent plans missions, evaluates topics, and produces prioritized intents.

Uses:
    - SankalpaOrchestrator (substrate/sankalpa/will.py) — mission registry + planner
    - KnowledgeResolver (knowledge/resolver.py) — topic seeding from KG
    - FeedbackProtocol (protocols/feedback.py) — engagement stats for priority adjustment
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.mahamantra.substrate.core.seed import TRINITY

logger = logging.getLogger("MOLTBOOK.STRATEGY")

# Domain topics for initial mission seeding (from knowledge/moltbook/platform.yaml domain)
_SEED_TOPICS = (
    ("ai_governance", "AI governance and transparent decision-making in autonomous systems"),
    ("decentralized_protocols", "Decentralized protocols and agent-to-agent coordination"),
    ("open_source_ai", "Open source AI development and collaborative tooling"),
    ("community_building", "Community building and social dynamics in agent networks"),
    ("agent_autonomy", "Agent autonomy, identity, and self-directed action"),
)


@dataclass
class StrategicIntent:
    """A single prioritized action for the agent to execute."""

    action_type: str  # "post", "comment", "dm_reply", "skip"
    topic: str  # The actual topic to write about
    reasoning: str  # Why this topic (for LLM context)
    priority: int  # 0=low, 10=critical
    mission_id: str  # Which mission this serves
    target_post_id: str = ""  # If commenting on a specific post
    engagement_context: str = ""  # What we know about topic performance
    submolt_context: str = ""  # Target submolt if known


@dataclass
class TopicMatch:
    """A feed topic matched against a mission."""

    post_id: str
    topic: str
    mission_id: str
    mission_name: str
    relevance: float  # 0.0-1.0 keyword overlap
    post_meta: Dict[str, Any] = field(default_factory=dict)


class MoltbookStrategyPlanner:
    """Plans content strategy using Sankalpa missions.

    DHARMA phase: evaluate missions → prioritized action list.
    MOKSHA phase: engagement data → mission priority adjustments.
    """

    _CACHE_FILE = "engagement_cache.json"

    def __init__(self, event_log=None, state_dir: Optional[Path] = None):
        self._event_log = event_log
        self._orchestrator = None
        self._missions_seeded = False
        self._state_dir = state_dir
        # Cache: mission_id → engagement stats
        self._engagement_cache: Dict[str, Dict[str, float]] = {}
        # Restore from disk
        self._restore_engagement_cache()

    @property
    def orchestrator(self):
        """Lazy-init SankalpaOrchestrator."""
        if self._orchestrator is None:
            try:
                from vibe_core.mahamantra.substrate.sankalpa.will import SankalpaOrchestrator

                self._orchestrator = SankalpaOrchestrator()
                if not self._missions_seeded:
                    self._seed_missions()
            except Exception as e:
                logger.warning(f"SankalpaOrchestrator unavailable: {e}")
        return self._orchestrator

    def _seed_missions(self) -> None:
        """Load initial missions from domain topics.

        Creates missions for each core topic area. Only seeds once —
        subsequent calls are no-ops (missions persist in registry).
        """
        if self._missions_seeded:
            return

        orch = self._orchestrator
        if not orch:
            return

        try:
            from vibe_core.mahamantra.protocols.sankalpa.types import (
                MissionPriority,
                MissionStatus,
                SankalpaMission,
                SankalpaStrategy,
                SankalpaTrigger,
                StrategyFrequency,
                TriggerType,
            )
            from datetime import datetime, timezone

            existing = {m.id for m in orch.registry.get_all_missions()}

            for topic_id, description in _SEED_TOPICS:
                mission_id = f"moltbook_{topic_id}"
                if mission_id in existing:
                    continue

                mission = SankalpaMission(
                    id=mission_id,
                    name=topic_id.replace("_", " ").title(),
                    description=description,
                    priority=MissionPriority.MEDIUM,
                    status=MissionStatus.ACTIVE,
                    strategies=[
                        SankalpaStrategy(
                            id=f"{mission_id}_engage",
                            name=f"Engage on {topic_id}",
                            description=f"Comment on posts related to {description}",
                            trigger=SankalpaTrigger(
                                trigger_type=TriggerType.IDLE_BASED,
                                idle_minutes=0,
                            ),
                            frequency=StrategyFrequency.CONTINUOUS,
                            intent_type="moltbook_comment",
                            intent_template={"topic": topic_id},
                            requires_ci_green=False,
                            requires_no_pending_intents=False,
                            max_executions_per_day=TRINITY * 2,  # 6
                        ),
                    ],
                    created_at=datetime.now(timezone.utc),
                    owner="moltbook",
                )
                orch.registry._missions[mission.id] = mission
                logger.info(f"Seeded mission: {mission_id}")

            # Persist seeded missions to disk
            if hasattr(orch.registry, "_save"):
                orch.registry._save()

            self._missions_seeded = True
        except Exception as e:
            logger.warning(f"Mission seeding failed: {e}")
            self._missions_seeded = True  # Don't retry on failure

    def get_active_missions(self) -> List[Any]:
        """Return active missions from registry."""
        orch = self.orchestrator
        if not orch:
            return []
        try:
            return orch.registry.get_active_missions()
        except Exception:
            return []

    def plan_cycle(
        self,
        feed_topics: List[Dict[str, Any]],
        engagement_stats: Dict[str, Any],
    ) -> List[StrategicIntent]:
        """DHARMA phase: evaluate missions → prioritized action list.

        1. Get active missions from registry
        2. Match feed_topics against mission goals
        3. Weight by engagement_stats (what worked)
        4. Return top-3 prioritized intents
        """
        missions = self.get_active_missions()
        if not missions:
            # No missions available — generate a single default post intent
            if feed_topics:
                best = feed_topics[0]
                return [
                    StrategicIntent(
                        action_type="comment",
                        topic=str(best.get("title", best.get("content", "")))[:200],
                        reasoning="Feed topic (no active missions)",
                        priority=5,
                        mission_id="default",
                        target_post_id=str(best.get("id", "")),
                    )
                ]
            return []

        intents: List[StrategicIntent] = []

        # Global engagement fallback (from FeedbackProtocol)
        global_eng = ""
        if engagement_stats:
            rate = engagement_stats.get("success_rate", 0)
            total = engagement_stats.get("total_signals", 0)
            if total > 0:
                global_eng = f"Overall: {rate:.0%} success ({total} signals)"

        # Match feed topics against missions
        matches = self._match_topics(feed_topics, missions)

        # Build intents from matches (comments on matching posts)
        for match in matches:
            eng = self._engagement_cache.get(match.mission_id, {})
            eng_context = ""
            if eng:
                eng_context = f"Success rate: {eng.get('success_rate', 0):.0%}"
            elif global_eng:
                eng_context = global_eng

            intents.append(
                StrategicIntent(
                    action_type="comment",
                    topic=match.topic,
                    reasoning=f"Matches mission '{match.mission_name}' (relevance={match.relevance:.2f})",
                    priority=self._mission_priority_score(match.mission_id, missions),
                    mission_id=match.mission_id,
                    target_post_id=match.post_id,
                    engagement_context=eng_context,
                )
            )

        # Add a post intent from highest-priority mission without feed match
        matched_mission_ids = {m.mission_id for m in matches}
        for mission in missions:
            if mission.id not in matched_mission_ids:
                eng = self._engagement_cache.get(mission.id, {})
                eng_context = ""
                if eng:
                    eng_context = f"Success rate: {eng.get('success_rate', 0):.0%}"
                elif global_eng:
                    eng_context = global_eng

                intents.append(
                    StrategicIntent(
                        action_type="post",
                        topic=mission.description,
                        reasoning=f"Mission '{mission.name}' — proactive post",
                        priority=self._mission_priority_score(mission.id, missions),
                        mission_id=mission.id,
                        engagement_context=eng_context,
                    )
                )
                break  # Only one proactive post per cycle

        # Sort by priority (descending), take top 3
        intents.sort(key=lambda i: i.priority, reverse=True)
        return intents[:TRINITY]

    def _match_topics(
        self,
        feed_topics: List[Dict[str, Any]],
        missions: List[Any],
    ) -> List[TopicMatch]:
        """Match feed topics against mission descriptions via keyword overlap."""
        matches: List[TopicMatch] = []

        for post in feed_topics:
            title = str(post.get("title", "")).lower()
            content = str(post.get("content", "")).lower()
            post_text = f"{title} {content}"
            post_words = set(post_text.split())
            post_id = str(post.get("id", ""))

            best_match: Optional[TopicMatch] = None
            best_relevance = 0.0

            for mission in missions:
                desc_words = set(mission.description.lower().split())
                # Keyword overlap: |intersection| / |mission_words|
                overlap = len(post_words & desc_words)
                if not desc_words:
                    continue
                relevance = overlap / len(desc_words)

                if relevance > best_relevance and relevance > 0.1:
                    best_relevance = relevance
                    best_match = TopicMatch(
                        post_id=post_id,
                        topic=title[:200] or content[:200],
                        mission_id=mission.id,
                        mission_name=mission.name,
                        relevance=relevance,
                        post_meta={
                            "upvotes": post.get("upvotes", 0),
                            "author": post.get("author", {}).get("name", "")
                            if isinstance(post.get("author"), dict)
                            else "",
                        },
                    )

            if best_match:
                matches.append(best_match)

        # Sort by relevance (descending)
        matches.sort(key=lambda m: m.relevance, reverse=True)
        return matches

    def _mission_priority_score(self, mission_id: str, missions: List[Any]) -> int:
        """Convert mission priority enum to integer score (0-10).

        Engagement cache boosts/reduces score.
        """
        base = 5  # Default medium
        for m in missions:
            if m.id == mission_id:
                prio = getattr(m.priority, "value", str(m.priority))
                base = {"critical": 10, "high": 8, "medium": 5, "low": 3}.get(prio, 5)
                break

        # Engagement adjustment: +2 for high success, -2 for low
        eng = self._engagement_cache.get(mission_id, {})
        rate = eng.get("success_rate", 0.5)
        if rate > 0.7:
            base = min(10, base + 2)
        elif rate < 0.3:
            base = max(1, base - 2)

        return base

    def update_from_engagement(self, engagement_data: Dict[str, Any]) -> None:
        """MOKSHA phase: topic performance → mission priority adjustments.

        High engagement → boost. Low engagement → deprioritize.
        """
        topic = str(engagement_data.get("topic", ""))
        upvotes = int(engagement_data.get("upvotes", 0))
        reply_count = int(engagement_data.get("reply_count", 0))
        net_score = upvotes + reply_count

        if not topic:
            return

        # Find matching mission by keyword overlap
        missions = self.get_active_missions()
        topic_words = set(topic.lower().split())

        for mission in missions:
            desc_words = set(mission.description.lower().split())
            overlap = len(topic_words & desc_words)
            if overlap >= 2 or (desc_words and overlap / len(desc_words) > 0.2):
                # Update engagement cache
                cache = self._engagement_cache.setdefault(
                    mission.id,
                    {
                        "total": 0,
                        "positive": 0,
                        "success_rate": 0.5,
                    },
                )
                cache["total"] += 1
                if net_score > 0:
                    cache["positive"] += 1
                total = cache["total"]
                cache["success_rate"] = cache["positive"] / total if total > 0 else 0.5

                # Adjust mission priority if strong signal
                if total >= TRINITY and cache["success_rate"] > 0.7:
                    self._boost_mission(mission)
                elif total >= TRINITY and cache["success_rate"] < 0.2:
                    self._deprioritize_mission(mission)

                logger.debug(
                    f"Engagement update for {mission.id}: "
                    f"rate={cache['success_rate']:.2f} ({cache['positive']}/{total})"
                )
                self._save_engagement_cache()
                break

    def _persist_registry(self) -> None:
        """Persist registry to disk if available."""
        orch = self._orchestrator
        if orch and hasattr(orch.registry, "_save"):
            orch.registry._save()

    def _boost_mission(self, mission) -> None:
        """Boost mission priority (medium → high, high → critical)."""
        try:
            from vibe_core.mahamantra.protocols.sankalpa.types import MissionPriority

            prio = mission.priority
            if prio == MissionPriority.LOW:
                mission.priority = MissionPriority.MEDIUM
            elif prio == MissionPriority.MEDIUM:
                mission.priority = MissionPriority.HIGH
            logger.info(f"Mission boosted: {mission.id} → {mission.priority.value}")
            self._persist_registry()
        except Exception:
            pass

    def _deprioritize_mission(self, mission) -> None:
        """Deprioritize mission (high → medium, medium → low)."""
        try:
            from vibe_core.mahamantra.protocols.sankalpa.types import MissionPriority

            prio = mission.priority
            if prio == MissionPriority.CRITICAL:
                mission.priority = MissionPriority.HIGH
            elif prio == MissionPriority.HIGH:
                mission.priority = MissionPriority.MEDIUM
            elif prio == MissionPriority.MEDIUM:
                mission.priority = MissionPriority.LOW
            logger.info(f"Mission deprioritized: {mission.id} → {mission.priority.value}")
            self._persist_registry()
        except Exception:
            pass

    # -----------------------------------------------------------------------
    # Engagement cache persistence (survives GitHub Actions restarts)
    # -----------------------------------------------------------------------

    def _save_engagement_cache(self) -> None:
        """Persist engagement cache to JSON file."""
        if not self._state_dir:
            return
        try:
            cache_path = self._state_dir / self._CACHE_FILE
            cache_path.write_text(json.dumps(self._engagement_cache, indent=2))
        except Exception as e:
            logger.debug(f"Engagement cache save failed: {e}")

    def _restore_engagement_cache(self) -> None:
        """Restore engagement cache from JSON file on init."""
        if not self._state_dir:
            return
        try:
            cache_path = self._state_dir / self._CACHE_FILE
            if cache_path.exists():
                data = json.loads(cache_path.read_text())
                if isinstance(data, dict):
                    self._engagement_cache = data
                    logger.info(f"Engagement cache restored: {len(data)} missions")
        except Exception as e:
            logger.debug(f"Engagement cache restore failed: {e}")
