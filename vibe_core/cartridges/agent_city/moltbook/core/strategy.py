"""
Moltbook Strategy Planner — Sankalpa → Strategic Intents.

Wires the existing SankalpaOrchestrator to drive Moltbook content decisions.
Instead of commenting on ALL posts or concatenating random feed titles,
the agent plans missions, evaluates topics, and produces prioritized intents.

Uses:
    - SankalpaOrchestrator (substrate/sankalpa/will.py) — mission registry + planner
    - MahaBuddhi (substrate/buddhi.py) — cognitive frame for format selection
    - Keyword Jaccard similarity (stop-word removal) — topic-to-mission matching
    - FeedbackProtocol (protocols/feedback.py) — engagement stats for priority adjustment
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.mahamantra.substrate.core.seed import HALVES, TRINITY

logger = logging.getLogger("MOLTBOOK.STRATEGY")



def _derive_seed_topics(feed_topics: Optional[List[Dict[str, Any]]] = None) -> tuple:
    """Derive mission topics from feed content + existing Sankalpa missions.

    Priority order:
    1. Feed topics — use each unique post title as a potential topic
    2. Existing Sankalpa missions (persisted from previous runs)

    No hardcoded query strings. No KG queries. Feed is truth.
    Returns tuple of (topic_id, description) pairs.
    """
    topics: list = []

    # Source 1: Feed topics — extract unique titles as potential mission seeds
    if feed_topics:
        seen_titles: set = set()
        for post in feed_topics[:20]:
            title = str(post.get("title", ""))
            if not title or len(title) < 10:
                continue
            title_key = title[:60].lower()
            if title_key in seen_titles:
                continue
            seen_titles.add(title_key)
            slug = title[:30].replace(" ", "_").lower()
            topic_id = f"feed_{slug}"
            topics.append((topic_id, title[:200]))

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
    buddhi_function: str = ""  # BRAHMA/VISHNU/SHIVA
    buddhi_approach: str = ""  # GENESIS/DHARMA/KARMA/MOKSHA
    buddhi_chapter: int = 0  # BG chapter 1-18
    buddhi_prana: int = 0  # energy 0-21600
    buddhi_integrity: float = 0.0  # membrane 0.0-1.0


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
        # Semantic matching caches (tokenized keywords)
        self._mission_tokens: Dict[str, frozenset] = {}  # mission_id → token set
        self._token_cache: Dict[str, frozenset] = {}  # text[:200] → token set
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
        """Seed missions from FEED content — what the community discusses.

        Always purges stale non-feed missions (moltbook_kg_*, moltbook_mission_*,
        mission_code_health). Then seeds new missions from feed titles.

        Called every DHARMA cycle when feed has topics. New feed topics → new missions.
        """
        orch = self.orchestrator  # Property — lazy-inits if None
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

            # ALWAYS purge stale missions — they come back if not cleaned
            self._purge_stale_missions(orch)

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
    def _purge_stale_missions(orch: object) -> None:
        """Remove stale missions that don't derive from feed content.

        Purges:
        - moltbook_kg_* — KG-generated (self-referential API posts)
        - moltbook_mission_* — cloned from non-moltbook missions (generic garbage)
        - mission_code_health — dharma mission leaked into content strategy

        Only moltbook_feed_* and moltbook_ch* survive — these come from real feed.
        """
        if not hasattr(orch, "registry") or not hasattr(orch.registry, "_missions"):
            return
        stale_ids = [
            mid for mid in orch.registry._missions
            if (
                mid.startswith("moltbook_kg_")
                or mid.startswith("moltbook_mission_")
                or mid == "mission_code_health"
            )
        ]
        for mid in stale_ids:
            del orch.registry._missions[mid]
        if stale_ids:
            if hasattr(orch.registry, "_save"):
                orch.registry._save()
            logger.info(f"Purged {len(stale_ids)} stale missions: {', '.join(stale_ids)}")

    def get_active_missions(self) -> List[Any]:
        """Return active MOLTBOOK missions (owner='moltbook') from registry.

        Filters out non-moltbook missions (e.g. 'mission_code_health' with
        owner='dharma') that leak generic topics into content strategy.
        """
        orch = self.orchestrator
        if not orch:
            return []
        try:
            all_missions = orch.registry.get_active_missions()
            return [
                m for m in all_missions
                if getattr(m, "owner", "") == "moltbook"
            ]
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
        commented_post_ids: Optional[set] = None,
    ) -> List[StrategicIntent]:
        """DHARMA phase: evaluate missions → prioritized action list.

        1. SravanamCheck: listen-before-speak gate (input ≥ 2× output)
        2. Seed missions from feed (first call)
        3. Match feed_topics against missions (keyword Jaccard)
        4. Buddhi.think() on top matches → format selection
        5. Weight by engagement_stats
        6. Engagement threshold: 0 engagement → comments only
        7. Return top-3 prioritized intents (comment-first)
        """
        # SravanamCheck: entropy law — must consume enough feed before producing
        input_count = len(feed_topics) if feed_topics else 0
        output_count = len(own_post_ids) if own_post_ids else 0
        can_post = self._sravanam_check(input_count, output_count)

        # Seed missions from feed — EVERY cycle with feed topics.
        # New feed titles → new missions. Stale missions purged on every seed call.
        if feed_topics:
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

        # Keyword Jaccard matching — first filter
        matches = self._match_topics(feed_topics, missions)
        _commented = commented_post_ids or set()

        # MahaManas drives ALL remaining decisions
        intents = self._manas_evaluate_matches(
            matches, missions, _commented, can_post, own_post_ids,
        )
        intents.sort(key=lambda i: i.priority, reverse=True)
        return intents[:TRINITY]

    def _manas_evaluate_matches(
        self,
        matches: List[TopicMatch],
        missions: List[Any],
        commented: set,
        can_post: bool,
        own_post_ids: Optional[Dict[str, Dict[str, object]]],
    ) -> List[StrategicIntent]:
        """Cognitive core: MahaManas perceive → decide → intents.

        Each match becomes a PerceptionEntry. Manas deduplicates,
        Buddhi discriminates, Viveka scores, then we build intents
        with full cognitive provenance.
        """
        from vibe_core.mahamantra.protocols._manas import PerceptionEntry
        from vibe_core.mahamantra.substrate.manas import get_manas

        manas = get_manas()

        # Build perception entries from matches (skip already-commented)
        entries = [
            PerceptionEntry(
                content=m.topic,
                source="feed_scan",
                category="sthula",
                context={"mission_id": m.mission_id, "post_id": m.post_id},
            )
            for m in matches
            if m.post_id not in commented
        ]

        if not entries:
            return []

        clean = manas.perceive(entries)
        verdicts = manas.decide(clean, max_verdicts=TRINITY * HALVES)

        # Build intents from verdicts with chapter dedup
        seen_chapters: set = set()
        intents: List[StrategicIntent] = []
        own_chapters = self._get_own_chapters(own_post_ids)
        zero_streak = bool(own_post_ids and self._zero_engagement_streak(own_post_ids))
        mission_map = {m.id: m for m in missions}

        for v in verdicts:
            cognition = v.buddhi
            if cognition is None:
                continue
            chapter = cognition.chapter
            if chapter in seen_chapters:
                continue
            seen_chapters.add(chapter)

            mission_id = v.perception.context.get("mission_id", "default")
            post_id = v.perception.context.get("post_id", "")
            mission = mission_map.get(mission_id)
            mission_name = mission.name if mission else "unknown"

            action_type = self._function_to_action(
                cognition.function, can_post, zero_streak, chapter, own_chapters,
            )

            eng = self._engagement_cache.get(mission_id, {})
            eng_context = ""
            if eng:
                eng_context = f"Success rate: {eng.get('success_rate', 0):.0%}"

            intents.append(StrategicIntent(
                action_type=action_type,
                topic=v.perception.content,
                reasoning=f"Manas verdict: {cognition.function}/{cognition.approach} ch.{chapter} (p={v.priority_score:.0f}, c={v.confidence:.2f})",
                priority=int(v.priority_score / 10),  # 0-100 → 0-10
                mission_id=mission_id,
                target_post_id=post_id,
                engagement_context=eng_context,
                content_format=self._buddhi_select_format(action_type, cognition.mode),
                buddhi_function=cognition.function,
                buddhi_approach=cognition.approach,
                buddhi_chapter=chapter,
                buddhi_prana=cognition.prana,
                buddhi_integrity=cognition.integrity,
            ))

        return intents

    @staticmethod
    def _function_to_action(
        function: str,
        can_post: bool,
        zero_streak: bool,
        chapter: int,
        own_chapters: set,
    ) -> str:
        """Map Buddhi trinity function to action type.

        BRAHMA (creation) + can_post + novel chapter → "post"
        Everything else → "comment"
        """
        if function == "BRAHMA" and can_post and not zero_streak:
            if chapter not in own_chapters:
                return "post"
        return "comment"

    @staticmethod
    def _get_own_chapters(
        own_post_ids: Optional[Dict[str, Dict[str, object]]],
    ) -> set:
        """Extract BG chapters from own recent posts (for dedup)."""
        chapters: set = set()
        if not own_post_ids:
            return chapters
        for post_info in own_post_ids.values():
            if isinstance(post_info, dict):
                ch = post_info.get("buddhi_chapter", 0)
                if ch:
                    chapters.add(int(ch))
        return chapters

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
        """Check if topic overlaps with recent posts via keyword Jaccard.

        Jaccard > 0.4 means >40% keyword overlap = too similar to post again.
        """
        topic_tokens = self._tokenize(topic.lower())
        if not topic_tokens:
            return False
        for post_info in own_post_ids.values():
            if not isinstance(post_info, dict):
                continue
            prev_title = post_info.get("title", "")
            if not prev_title or not isinstance(prev_title, str):
                continue
            prev_tokens = self._tokenize(prev_title.lower())
            if not prev_tokens:
                continue
            intersection = len(topic_tokens & prev_tokens)
            union = len(topic_tokens | prev_tokens)
            jaccard = intersection / union if union > 0 else 0.0
            if jaccard > 0.4:
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
        2. Keyword Jaccard fallback (tokenized word overlap, stop-words removed)
        """
        self._ensure_attention(missions)
        self._ensure_mission_tokens(missions)
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

            # Keyword Jaccard fallback — tokenized word overlap
            if matched_mission_id is None:
                post_tokens = self._tokenize(post_text)
                matched_mission_id, relevance = self._semantic_match(
                    post_tokens, missions, self._mission_tokens,
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

    def _tokenize(self, text: str) -> frozenset:
        """Tokenize text into content words. Cached by first 200 chars.

        Delegates to text_utils.tokenize() for stop-word removal.
        Returns frozenset for O(1) set operations.
        """
        from vibe_core.cartridges.agent_city.moltbook.core.text_utils import tokenize

        key = text[:200]
        if key not in self._token_cache:
            self._token_cache[key] = tokenize(key)
        return self._token_cache[key]

    def _ensure_mission_tokens(self, missions: List[Any]) -> None:
        """Precompute token sets for mission descriptions. Cached."""
        for mission in missions:
            if mission.id not in self._mission_tokens:
                self._mission_tokens[mission.id] = self._tokenize(
                    mission.description.lower()
                )

    @staticmethod
    def _semantic_match(
        post_tokens: frozenset,
        missions: List[Any],
        mission_tokens: Dict[str, frozenset],
    ) -> tuple:
        """Keyword Jaccard matching — tokenized word overlap.

        Compares content words (stop words removed) between post and missions.
        This provides real discrimination:
        - Same topic: 0.40-0.70 (shared domain keywords)
        - Related: 0.10-0.30 (some shared vocabulary)
        - Unrelated: 0.00 (no shared words)

        Previous approach (RAMA coordinates / basin_cosine) had 0.03 spread
        across ALL text pairs — useless for discrimination.

        Returns (mission_id, jaccard_similarity).
        Floor: Jaccard >= 0.1 (at least 1 shared content word).
        """
        if not post_tokens:
            return None, 0.0

        scores: List[tuple] = []  # (mission_id, jaccard)
        for mission in missions:
            m_tokens = mission_tokens.get(mission.id)
            if not m_tokens:
                continue
            intersection = len(post_tokens & m_tokens)
            union = len(post_tokens | m_tokens)
            jaccard = intersection / union if union > 0 else 0.0
            scores.append((mission.id, jaccard))

        if not scores:
            return None, 0.0

        scores.sort(key=lambda x: x[1], reverse=True)
        best_id, best_sim = scores[0]

        # Floor: at least 1 shared content word
        if best_sim < 0.1:
            return None, 0.0

        return best_id, best_sim

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

        # Find matching mission by keyword Jaccard overlap
        missions = self.get_active_missions()
        self._ensure_mission_tokens(missions)
        topic_tokens = self._tokenize(topic.lower())

        best_mission = None
        best_sim = 0.0
        for mission in missions:
            m_tokens = self._mission_tokens.get(mission.id)
            if not m_tokens or not topic_tokens:
                continue
            intersection = len(topic_tokens & m_tokens)
            union = len(topic_tokens | m_tokens)
            jaccard = intersection / union if union > 0 else 0.0
            if jaccard > best_sim:
                best_sim = jaccard
                best_mission = mission

        if best_mission and best_sim >= 0.1:
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

            # MahaManas: Hebbian learning from engagement outcome
            try:
                from vibe_core.mahamantra.protocols._manas import ManaVerdict, PerceptionEntry
                from vibe_core.mahamantra.substrate.manas import get_manas

                manas = get_manas()
                perception = PerceptionEntry(
                    content=topic, source="engagement", category="sthula",
                    context={"mission_id": mission.id},
                )
                verdict = ManaVerdict(
                    perception=perception, approved=True,
                    priority_score=50.0, confidence=0.5,
                    dharma_ok=True, dharma_reason="engagement",
                    reason="engagement feedback",
                )
                manas.record_outcome(verdict, success=(net_score > 0))
            except Exception as e:
                logger.warning(f"Manas learn failed: {e}")

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
