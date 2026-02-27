"""
Moltbook Strategy Planner — Sankalpa → Strategic Intents.

Wires the existing SankalpaOrchestrator to drive Moltbook content decisions.
Instead of commenting on ALL posts or concatenating random feed titles,
the agent plans missions, evaluates topics, and produces prioritized intents.

Uses:
    - SankalpaOrchestrator (substrate/sankalpa/will.py) — mission registry + planner
    - MahaBuddhi (substrate/buddhi.py) — cognitive frame for format selection
    - Lotus RAMA coordinates + basin_cosine/hkr_similarity — semantic matching
    - FeedbackProtocol (protocols/feedback.py) — engagement stats for priority adjustment
"""

import json
import logging
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.mahamantra.substrate.core.seed import TRINITY

logger = logging.getLogger("MOLTBOOK.STRATEGY")



def _derive_seed_topics(feed_topics: Optional[List[Dict[str, Any]]] = None) -> tuple:
    """Derive mission topics from feed content + existing Sankalpa missions.

    Priority order:
    1. Feed topics → BG chapter clustering via Lotus VM (what the community discusses)
    2. Existing Sankalpa missions (persisted from previous runs)

    No hardcoded query strings. No KG queries. Feed is truth.
    Returns tuple of (topic_id, description) pairs.
    """
    topics: list = []

    # Source 1: Feed topics → cluster by BG chapter via Lotus VM
    if feed_topics:
        try:
            from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra

            lotus = get_mahamantra()
            chapter_posts: Dict[int, List[str]] = {}
            for post in feed_topics[:20]:
                title = str(post.get("title", ""))
                if not title or len(title) < 10:
                    continue
                vm_result = lotus(title)
                chapter = int(vm_result.get("chapter", 0))
                if chapter > 0:
                    chapter_posts.setdefault(chapter, []).append(title[:200])

            for chapter, titles in chapter_posts.items():
                if titles:
                    slug = titles[0][:30].replace(" ", "_").lower()
                    topic_id = f"ch{chapter}_{slug}"
                    topics.append((topic_id, titles[0]))
        except Exception as e:
            logger.warning(f"Feed topic clustering failed: {e}")

    # Source 2: Existing Sankalpa missions — only NON-moltbook missions.
    # Skip moltbook_ missions (already seeded) and moltbook_kg_ (API descriptions).
    try:
        from vibe_core.mahamantra.substrate.sankalpa.will import SankalpaOrchestrator

        orch = SankalpaOrchestrator()
        existing = orch.registry.get_all_missions()
        seen_ids = {t[0] for t in topics}
        for mission in existing:
            mid = mission.id
            desc = mission.description
            if mid.startswith("moltbook_"):
                continue  # Skip all moltbook missions (avoid nesting + KG garbage)
            if desc and mid not in seen_ids:
                topics.append((mid, desc[:200]))
    except Exception as e:
        logger.warning(f"Sankalpa topic derivation failed: {e}")

    if topics:
        logger.info(f"Derived {len(topics)} seed topics from feed + Sankalpa")
        return tuple(topics)

    logger.warning("No seed topics: feed + Sankalpa both empty. Agent will wait.")
    return ()


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
    content_format: str = ""  # "question", "observation", "opinion", "analysis", "tutorial"


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

    Uses MahaAttention for O(1) topic→mission matching (replaces keyword overlap).
    """

    _CACHE_FILE = "engagement_cache.json"

    def __init__(self, event_log=None, state_dir: Optional[Path] = None):
        self._event_log = event_log
        self._orchestrator = None
        self._missions_seeded = False
        self._state_dir = state_dir
        self._attention = None  # MahaAttention instance (lazy)
        self._attention_mission_ids: set = set()  # Missions already memorized
        # Semantic matching caches (RAMA coordinates)
        self._mission_coords: Dict[str, tuple] = {}  # mission_id → RAMA coords
        self._coord_cache: Dict[str, tuple] = {}  # text[:200] → RAMA coords
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
                # Seeding deferred to plan_cycle() where feed_topics are available
            except Exception as e:
                logger.warning(f"SankalpaOrchestrator unavailable: {e}")
        return self._orchestrator

    def _seed_missions(
        self, feed_topics: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Load missions from feed-derived topics.

        Sources: Feed topics (BG chapter clusters) → Sankalpa missions.
        Creates missions for each topic area.

        On first call, purges stale KG-generated missions (moltbook_kg_*)
        that describe the Moltbook API itself — these cause self-referential posts.
        Re-seeds from feed on subsequent calls when new topics appear.
        """
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

            # FIRST CALL: purge KG-generated garbage missions
            if not self._missions_seeded:
                self._purge_kg_missions(orch)

            existing = {m.id for m in orch.registry.get_all_missions()}
            seed_topics = _derive_seed_topics(feed_topics)

            if not seed_topics:
                self._missions_seeded = True
                return

            added = 0
            for topic_id, description in seed_topics:
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
                added += 1
                logger.info(f"Seeded mission: {mission_id}")

            # Persist seeded missions to disk
            if added > 0 and hasattr(orch.registry, "_save"):
                orch.registry._save()

            self._missions_seeded = True
        except Exception as e:
            logger.warning(f"Mission seeding failed: {e}")
            self._missions_seeded = True  # Don't retry on failure

    @staticmethod
    def _purge_kg_missions(orch: object) -> None:
        """Remove KG auto-generated missions that describe the Moltbook API.

        These missions (moltbook_kg_*) cause self-referential posts about
        "Moltbook voting system" and "DM request flows" instead of real content.
        They were seeded by querying the Knowledge Graph for Moltbook platform
        concepts — useful as internal documentation, garbage as content strategy.
        """
        if not hasattr(orch, "registry") or not hasattr(orch.registry, "_missions"):
            return
        kg_ids = [
            mid for mid in orch.registry._missions
            if mid.startswith("moltbook_kg_")
        ]
        for mid in kg_ids:
            del orch.registry._missions[mid]
        if kg_ids:
            if hasattr(orch.registry, "_save"):
                orch.registry._save()
            logger.info(f"Purged {len(kg_ids)} KG-generated missions: {', '.join(kg_ids)}")

    def get_active_missions(self) -> List[Any]:
        """Return active missions from registry."""
        orch = self.orchestrator
        if not orch:
            return []
        try:
            return orch.registry.get_active_missions()
        except Exception as e:
            logger.warning(f"Active missions query failed: {e}")
            return []

    @staticmethod
    def _buddhi_select_format(action_type: str, mode: str) -> str:
        """Select content format from BuddhiResult cognitive mode.

        SATTVA (contemplative) → analysis/observation
        RAJAS  (active)        → opinion/question
        TAMAS  (transformative) → tutorial/opinion
        """
        if action_type == "comment":
            return {
                "SATTVA": "observation",
                "RAJAS": "question",
                "TAMAS": "opinion",
            }.get(mode, "observation")
        return {
            "SATTVA": "analysis",
            "RAJAS": "opinion",
            "TAMAS": "tutorial",
        }.get(mode, "analysis")

    def plan_cycle(
        self,
        feed_topics: List[Dict[str, Any]],
        engagement_stats: Dict[str, Any],
        own_post_ids: Optional[Dict[str, Dict[str, object]]] = None,
    ) -> List[StrategicIntent]:
        """DHARMA phase: evaluate missions → prioritized action list.

        1. SravanamCheck: listen-before-speak gate (input ≥ 2× output)
        2. Seed missions from feed (first call)
        3. Match feed_topics against missions (semantic via RAMA coords)
        4. Buddhi.think() on top matches → format selection
        5. Weight by engagement_stats
        6. Engagement threshold: 0 engagement → comments only
        7. Return top-3 prioritized intents (comment-first)
        """
        # SravanamCheck: entropy law — must consume enough feed before producing
        input_count = len(feed_topics) if feed_topics else 0
        output_count = len(own_post_ids) if own_post_ids else 0
        can_post = self._sravanam_check(input_count, output_count)

        # Seed missions from feed (first call, or re-seed after purge left no moltbook missions)
        if feed_topics:
            if not self._missions_seeded:
                self._seed_missions(feed_topics=feed_topics)
            elif not any(
                m.id.startswith("moltbook_") for m in self.get_active_missions()
            ):
                # All moltbook missions were purged — re-seed from feed
                self._missions_seeded = False
                self._seed_missions(feed_topics=feed_topics)

        missions = self.get_active_missions()
        if not missions:
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

        # Global engagement context
        global_eng = ""
        if engagement_stats:
            rate = engagement_stats.get("success_rate", 0)
            total = engagement_stats.get("total_signals", 0)
            if total > 0:
                global_eng = f"Overall: {rate:.0%} success ({total} signals)"

        # Match feed topics against missions (semantic)
        matches = self._match_topics(feed_topics, missions)

        # Buddhi.think() on top matches for cognitive format selection
        match_cognitions: Dict[str, str] = {}  # post_id → mode
        try:
            from vibe_core.mahamantra.substrate.buddhi import get_buddhi

            buddhi = get_buddhi()
            shuffled = list(matches)
            random.shuffle(shuffled)
            for match in shuffled[:TRINITY]:
                cognition = buddhi.think(match.topic)
                match_cognitions[match.post_id] = cognition.mode
        except Exception as e:
            logger.warning(f"Buddhi format selection failed: {e}")
            shuffled = list(matches)
            random.shuffle(shuffled)

        # Build comment intents from matches
        for match in shuffled:
            eng = self._engagement_cache.get(match.mission_id, {})
            eng_context = ""
            if eng:
                eng_context = f"Success rate: {eng.get('success_rate', 0):.0%}"
            elif global_eng:
                eng_context = global_eng

            mode = match_cognitions.get(match.post_id, "SATTVA")
            intents.append(
                StrategicIntent(
                    action_type="comment",
                    topic=match.topic,
                    reasoning=f"Matches mission '{match.mission_name}' (relevance={match.relevance:.2f})",
                    priority=self._mission_priority_score(match.mission_id, missions),
                    mission_id=match.mission_id,
                    target_post_id=match.post_id,
                    engagement_context=eng_context,
                    content_format=self._buddhi_select_format("comment", mode),
                )
            )

        # COMMENT-FIRST: Only add a post when:
        # 1. There's an unmatched mission
        # 2. SravanamCheck passed (consumed enough feed)
        # 3. Topic doesn't semantically overlap recent posts
        # 4. Engagement threshold: skip posts if 0 engagement on recent posts
        matched_mission_ids = {m.mission_id for m in matches}
        highest_prio = max((i.priority for i in intents), default=5)

        if not can_post:
            logger.info("SravanamCheck: insufficient input — comments only this cycle")
            intents.sort(key=lambda i: i.priority, reverse=True)
            return intents[:TRINITY]

        # Engagement threshold: if we've posted ≥3 times with 0 engagement, comments only
        if own_post_ids and self._zero_engagement_streak(own_post_ids):
            logger.info("Engagement threshold: 0 engagement on recent posts — comments only")
            intents.sort(key=lambda i: i.priority, reverse=True)
            return intents[:TRINITY]

        for mission in missions:
            if mission.id not in matched_mission_ids:
                post_topic = ""
                if feed_topics:
                    top_by_engagement = sorted(
                        feed_topics, key=lambda t: t.get("upvotes", 0), reverse=True
                    )
                    theme_titles = [
                        str(t.get("title", "")) for t in top_by_engagement[:3] if t.get("title")
                    ]
                    if theme_titles:
                        post_topic = "; ".join(theme_titles)[:300]
                if not post_topic:
                    logger.info(f"No feed topics for post — staying silent (mission '{mission.name}')")
                    continue

                # Semantic dedup via basin_cosine against own recent posts
                if own_post_ids and self._semantic_dedup(post_topic, own_post_ids):
                    logger.info(f"Semantic dedup: '{post_topic[:60]}' similar to recent post")
                    continue

                eng = self._engagement_cache.get(mission.id, {})
                eng_context = ""
                if eng:
                    eng_context = f"Success rate: {eng.get('success_rate', 0):.0%}"
                elif global_eng:
                    eng_context = global_eng

                # Buddhi-driven format for post
                post_mode = "SATTVA"
                try:
                    from vibe_core.mahamantra.substrate.buddhi import get_buddhi
                    post_mode = get_buddhi().think(post_topic).mode
                except Exception as e:
                    logger.warning(f"Post Buddhi unavailable, using SATTVA: {e}")

                intents.append(
                    StrategicIntent(
                        action_type="post",
                        topic=post_topic,
                        reasoning=f"Mission '{mission.name}' — proactive post, themes from feed",
                        priority=highest_prio + 1,
                        mission_id=mission.id,
                        engagement_context=eng_context,
                        content_format=self._buddhi_select_format("post", post_mode),
                    )
                )
                logger.info(f"Post from unmatched mission '{mission.name}'")
                break

        intents.sort(key=lambda i: i.priority, reverse=True)
        return intents[:TRINITY]

    @staticmethod
    def _sravanam_check(input_count: int, output_count: int) -> bool:
        """SravanamCheck gate: listen before speak.

        Uses the entropy law from harmonics.py: input ≥ IO_RATIO × output.
        If agent hasn't consumed enough feed relative to posts produced, block new posts.
        Comments still allowed (lower cost, higher engagement).

        Returns True if posting is allowed.
        """
        try:
            from vibe_core.mahamantra.substrate.encoding.harmonics import SravanamCheck

            can, reason = SravanamCheck.can_emit(
                input_tokens=input_count,
                output_tokens=output_count,
                resonance=0.5,  # Neutral — only entropy law matters here
                strict=False,
            )
            if not can:
                logger.info(f"SravanamCheck blocked: {reason}")
            return can
        except Exception as e:
            logger.debug(f"SravanamCheck unavailable: {e}")
            return True  # Fail open if infrastructure missing

    @staticmethod
    def _zero_engagement_streak(
        own_post_ids: Dict[str, Dict[str, object]],
    ) -> bool:
        """Check if recent posts have zero engagement.

        Returns True if agent should stop posting (≥3 posts, all with 0 engagement).
        """
        recent_posts = sorted(
            (v for v in own_post_ids.values() if isinstance(v, dict)),
            key=lambda v: v.get("created_at", 0),
            reverse=True,
        )[:TRINITY]
        if len(recent_posts) < TRINITY:
            return False  # Not enough posts to judge
        # Check if any recent post has engagement data
        return all(
            int(p.get("upvotes", 0)) == 0 and int(p.get("replies", 0)) == 0
            for p in recent_posts
        )

    def _semantic_dedup(
        self, topic: str, own_post_ids: Dict[str, Dict[str, object]],
    ) -> bool:
        """Check if topic semantically overlaps with recent posts.

        Uses combined metric (basin_cosine + hkr_similarity) — basin_cosine alone
        has only 0.03 spread, making any threshold meaningless. The combined metric
        with 0.10-0.18 spread can actually discriminate.
        """
        from vibe_core.mahamantra.substrate.core.basin_map import (
            basin_cosine,
            hkr_similarity,
        )

        topic_coords = self._get_coords(topic.lower())
        for post_info in own_post_ids.values():
            if not isinstance(post_info, dict):
                continue
            prev_title = post_info.get("title", "")
            if not prev_title or not isinstance(prev_title, str):
                continue
            prev_coords = self._get_coords(prev_title.lower())
            bc = basin_cosine(topic_coords, prev_coords)
            hkr = hkr_similarity(topic_coords, prev_coords)
            combined = 0.6 * bc + 0.4 * hkr
            if combined > 0.95:
                return True
        return False

    def _ensure_attention(self, missions: List[Any]) -> None:
        """Lazy-init MahaAttention and memorize mission descriptions.

        Only registers missions not already memorized (idempotent).
        """
        if self._attention is None:
            try:
                from vibe_core.mahamantra.adapters.attention import MahaAttention

                self._attention = MahaAttention()
            except Exception as e:
                logger.warning(f"MahaAttention unavailable: {e}")
                return

        for mission in missions:
            if mission.id not in self._attention_mission_ids:
                self._attention.memorize(mission.description.lower(), mission.id)
                self._attention_mission_ids.add(mission.id)

    def _match_topics(
        self,
        feed_topics: List[Dict[str, Any]],
        missions: List[Any],
    ) -> List[TopicMatch]:
        """Match feed topics against missions.

        1. MahaAttention O(1) hash lookup (exact semantic address)
        2. Semantic fallback via RAMA coordinates + basin_cosine + hkr_similarity
        """
        self._ensure_attention(missions)
        self._ensure_mission_coords(missions)
        mission_map = {m.id: m for m in missions}
        matches: List[TopicMatch] = []

        for post in feed_topics:
            title = str(post.get("title", "")).lower()
            content = str(post.get("content", "")).lower()
            post_text = f"{title} {content}".strip()
            post_id = str(post.get("id", ""))

            if not post_text:
                continue

            matched_mission_id = None
            relevance = 0.0

            # O(1) attention lookup
            if self._attention is not None:
                result = self._attention.attend(post_text)
                if result.found and result.handler in mission_map:
                    matched_mission_id = result.handler
                    relevance = 1.0

            # Semantic fallback via RAMA coordinates
            if matched_mission_id is None:
                post_coords = self._get_coords(post_text)
                matched_mission_id, relevance = self._semantic_match(
                    post_coords, missions, self._mission_coords,
                )

            if matched_mission_id and matched_mission_id in mission_map:
                mission = mission_map[matched_mission_id]
                matches.append(TopicMatch(
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
                ))

        matches.sort(key=lambda m: m.relevance, reverse=True)
        return matches

    def _get_coords(self, text: str) -> tuple:
        """Get RAMA coordinates for text. Cached by first 200 chars."""
        key = text[:200]
        if key not in self._coord_cache:
            from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra

            lotus = get_mahamantra()
            self._coord_cache[key] = lotus.nama(key)
        return self._coord_cache[key]

    def _ensure_mission_coords(self, missions: List[Any]) -> None:
        """Precompute RAMA coordinates for mission descriptions. Cached."""
        for mission in missions:
            if mission.id not in self._mission_coords:
                self._mission_coords[mission.id] = self._get_coords(
                    mission.description.lower()
                )

    @staticmethod
    def _semantic_match(
        post_coords: tuple,
        missions: List[Any],
        mission_coords: Dict[str, tuple],
    ) -> tuple:
        """Semantic matching via RAMA coordinates. Returns (mission_id, similarity).

        Combined metric: 60% basin_cosine (coarse field) + 40% hkr_similarity (fine fingerprint).

        Rank-based selection: picks the BEST match and requires a minimum margin
        over the second-best. basin_cosine alone has only ~0.03 spread across all
        texts — the combined metric has 0.10-0.18 spread. A flat threshold (0.75)
        is useless when ALL scores exceed 0.89.

        Selection criteria:
        1. Absolute floor: combined similarity must exceed 0.5 (filters truly
           unrelated content like "pizza" vs "distributed systems" = 0.38)
        2. Margin: best match must have margin > 0.02 over second-best
           (if all missions equally close, no discriminating signal → None)
        """
        from vibe_core.mahamantra.substrate.core.basin_map import (
            basin_cosine,
            hkr_similarity,
        )

        scores: List[tuple] = []  # (mission_id, combined_sim)
        for mission in missions:
            m_coords = mission_coords.get(mission.id)
            if not m_coords:
                continue
            bc = basin_cosine(post_coords, m_coords)
            hkr = hkr_similarity(post_coords, m_coords)
            sim = 0.6 * bc + 0.4 * hkr
            scores.append((mission.id, sim))

        if not scores:
            return None, 0.0

        scores.sort(key=lambda x: x[1], reverse=True)
        best_id, best_sim = scores[0]

        # Floor: reject truly unrelated content
        if best_sim < 0.5:
            return None, 0.0

        # Rank-based: require margin over second-best
        if len(scores) > 1:
            second_sim = scores[1][1]
            margin = best_sim - second_sim
            if margin < 0.02:
                # All missions equally close — no discriminating signal
                return None, 0.0

        return best_id, best_sim

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

        # SynapseStore: cross-session learned weight (persistent memory)
        synapse_boost = self._get_synapse_boost(mission_id)
        base = max(1, min(10, base + synapse_boost))

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

        # Find matching mission by semantic similarity (combined RAMA metric)
        missions = self.get_active_missions()
        self._ensure_mission_coords(missions)
        topic_coords = self._get_coords(topic.lower())

        from vibe_core.mahamantra.substrate.core.basin_map import (
            basin_cosine,
            hkr_similarity,
        )

        best_mission = None
        best_sim = 0.0
        for mission in missions:
            m_coords = self._mission_coords.get(mission.id)
            if not m_coords:
                continue
            bc = basin_cosine(topic_coords, m_coords)
            hkr = hkr_similarity(topic_coords, m_coords)
            combined = 0.6 * bc + 0.4 * hkr
            if combined > best_sim:
                best_sim = combined
                best_mission = mission

        if best_mission and best_sim >= 0.5:
            mission = best_mission
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

            # SynapseStore: persistent cross-session learning
            self._update_synapse_weight(mission.id, net_score > 0)

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
        except Exception as e:
            logger.warning(f"Mission boost failed: {e}")

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
        except Exception as e:
            logger.warning(f"Mission deprioritize failed: {e}")

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
            logger.warning(f"Engagement cache save failed: {e}")

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
            logger.warning(f"Engagement cache restore failed: {e}")

    # -----------------------------------------------------------------------
    # SynapseStore — persistent cross-session learning
    # -----------------------------------------------------------------------

    def _update_synapse_weight(self, mission_id: str, positive: bool) -> None:
        """Learn from engagement: adjust synapse weights for mission strategies."""
        try:
            from vibe_core.state.synapse_store import get_synapse_store

            store = get_synapse_store()
            trigger = f"moltbook:{mission_id}"
            action = "engage"
            if positive:
                w = store.increment_weight(trigger, action, delta=0.05)
            else:
                w = store.decrement_weight(trigger, action, delta=0.03)
            store.flush()  # Persist immediately — defer_save=True leaves weights in memory only
            logger.debug(f"Synapse weight {trigger}→{action}: {w:.2f} (flushed)")
        except Exception as e:
            logger.warning(f"SynapseStore update failed: {e}")

    def _get_synapse_boost(self, mission_id: str) -> int:
        """Read learned synapse weight → priority boost (-2 to +2)."""
        try:
            from vibe_core.state.synapse_store import get_synapse_store

            store = get_synapse_store()
            weight = store.get_weight(f"moltbook:{mission_id}", "engage")
            if weight is None:
                return 0
            # weight 0.1-0.95 → boost -2 to +2 (centered at 0.5)
            return round((weight - 0.5) * 4)
        except Exception as e:
            logger.warning(f"SynapseStore read failed: {e}")
            return 0
