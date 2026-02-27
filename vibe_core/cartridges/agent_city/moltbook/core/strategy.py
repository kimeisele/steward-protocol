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
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.mahamantra.substrate.core.seed import TRINITY

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

                # Keyword Jaccard dedup against own recent posts
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

    # Stop words — common English words that carry no topical signal
    _STOP_WORDS = frozenset({
        "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of",
        "is", "are", "was", "were", "be", "been", "this", "that", "with",
        "from", "by", "it", "its", "as", "not", "but", "no", "all", "any",
        "do", "does", "did", "can", "could", "would", "should", "will",
        "may", "might", "must", "shall", "has", "have", "had", "about",
        "into", "over", "after", "before", "more", "most", "very", "just",
        "also", "how", "what", "which", "who", "whom", "when", "where",
        "why", "than", "then", "so", "if", "only", "own", "same", "too",
        "each", "every", "both", "few", "some", "such", "other",
    })

    def _tokenize(self, text: str) -> frozenset:
        """Tokenize text into content words. Cached by first 200 chars.

        Strips punctuation, removes stop words and short tokens.
        Returns frozenset for O(1) set operations.
        """
        key = text[:200]
        if key not in self._token_cache:
            tokens = set()
            for word in key.lower().split():
                clean = "".join(c for c in word if c.isalnum())
                if clean and clean not in self._STOP_WORDS and len(clean) > 2:
                    tokens.add(clean)
            self._token_cache[key] = frozenset(tokens)
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
