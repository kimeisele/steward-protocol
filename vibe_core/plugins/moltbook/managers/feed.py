"""FeedAnalyzer — feed scanning, submolt discovery, submolt selection.

Extracted from MoltbookPlugin._scan_feed(), _discover_submolts(), _select_submolt().
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Set

from vibe_core.mahamantra import run_async
from vibe_core.mahamantra.substrate.core.seed import (
    COSMIC_FRAME,
    PANCHA,
    QUARTERS,
    SHARANAGATI,
)
from vibe_core.protocols.moltbook_content import (
    ContentProposal,
    ContentQueue,
    ContentType,
)

if TYPE_CHECKING:
    from vibe_core.protocols.moltbook import MoltbookProtocol
    from vibe_core.protocols.moltbook_content import ContentProposalProtocol

logger = logging.getLogger("MOLTBOOK_FEED")

# Resonance threshold scaled to COSMIC_FRAME — integer comparison, no floats
_SUBMOLT_RESONANCE_CF = COSMIC_FRAME * SHARANAGATI // (QUARTERS * PANCHA)  # 6480


class FeedAnalyzer:
    """Feed scanning, submolt discovery, and submolt selection.

    Args:
        seen_post_ids: Shared ref to plugin's seen post ID set.
        subscribed_submolts: Shared ref to plugin's subscribed submolts set.
        submolt_descriptions: Shared ref to plugin's submolt description dict.
    """

    def __init__(
        self,
        seen_post_ids: Set[str],
        subscribed_submolts: Set[str],
        submolt_descriptions: Dict[str, str],
    ):
        self._seen_post_ids = seen_post_ids
        self._subscribed_submolts = subscribed_submolts
        self._submolt_descriptions = submolt_descriptions

    def scan_feed(
        self,
        client: MoltbookProtocol,
        proposer: Optional[ContentProposalProtocol],
        content_queue: ContentQueue,
    ) -> List[Dict[str, object]]:
        """GENESIS phase: Extract topics + metadata from feed. NO content generation.

        Stores ALL feed posts as topics for strategy evaluation (not just unseen).
        Only engagement actions (upvotes) are filtered by seen status.

        Returns the feed topics list.
        """
        if not proposer:
            return []

        try:
            posts = run_async(client.get_personalized_feed(sort="hot", limit=10))
        except Exception as e:
            logger.warning(f"Feed fetch failed: {e}")
            return []

        if not posts:
            return []

        # ALL posts become topics for strategy (DHARMA needs context, not just new posts)
        feed_topics = posts if isinstance(posts, list) else []
        logger.info(f"Feed scan: {len(feed_topics)} topics available")

        # Engagement: upvote UNSEEN high-quality posts (dedup prevents double-engage)
        for post in posts[:5]:
            post_id = post.get("id", "") if isinstance(post, dict) else ""
            if post_id and post_id in self._seen_post_ids:
                continue  # Already engaged
            post_content = post.get("content", post.get("title", "")) if isinstance(post, dict) else ""
            author_data = post.get("author", {}) if isinstance(post, dict) else {}
            author = author_data.get("name", "unknown") if isinstance(author_data, dict) else "unknown"
            if post_id and post_content:
                self._seen_post_ids.add(post_id)
                try:
                    engage_proposal = proposer.should_engage(post_id, post_content, author)
                    if engage_proposal:
                        content_queue.enqueue(engage_proposal)
                except Exception as e:
                    logger.debug(f"Engagement proposal failed for {post_id}: {e}")

        return feed_topics

    def analyze_feed(
        self,
        client: MoltbookProtocol,
        proposer: Optional[ContentProposalProtocol],
        content_queue: ContentQueue,
        director_propose: Callable,
    ) -> None:
        """Read personalized feed, score via proposer, generate via AgencyDirector."""
        if not proposer:
            return

        try:
            posts = run_async(client.get_personalized_feed(sort="hot", limit=10))
        except Exception as e:
            logger.warning(f"Feed fetch failed: {e}")
            return

        if not posts:
            return

        # Filter already-seen posts
        unseen = []
        for post in posts:
            post_id = post.get("id", "") if isinstance(post, dict) else ""
            if post_id and post_id not in self._seen_post_ids:
                self._seen_post_ids.add(post_id)
                unseen.append(post)

        if not unseen:
            return

        scored = proposer.analyze_feed(unseen)

        for post, ranked, score in scored:
            post_id = post.get("id", "") if isinstance(post, dict) else ""
            post_content = post.get("content", post.get("title", "")) if isinstance(post, dict) else ""
            author_data = post.get("author", {}) if isinstance(post, dict) else {}
            author = author_data.get("name", "unknown") if isinstance(author_data, dict) else "unknown"

            if not post_id or not post_content:
                continue

            # Engagement (upvote)
            try:
                engage_proposal = proposer.should_engage(post_id, post_content, author)
                if engage_proposal:
                    content_queue.enqueue(engage_proposal)
            except Exception as e:
                logger.warning(f"Engagement proposal failed: {e}")

            # Comment on high-resonance posts via Agency Director (I-P-V-O)
            try:
                comment_proposal = director_propose(
                    content_type="comment",
                    raw_input=post_content,
                    proposal_type=ContentType.COMMENT.value,
                    post_id=post_id,
                    trigger="feed_analysis",
                )
                if comment_proposal:
                    content_queue.enqueue(comment_proposal)
                    logger.info(f"Feed comment queued for {post_id} (score={score:.2f})")
            except Exception as e:
                logger.warning(f"Comment proposal failed: {e}")

    def discover_submolts(self, client: MoltbookProtocol, content_queue: ContentQueue) -> None:
        """Discover and subscribe to relevant submolts via resonance scoring.

        Uses resonate() to score each submolt by name+description.
        Only subscribes if score > threshold OR fewer than 3 subscriptions (cold start).
        """
        try:
            submolts = run_async(client.get_submolts())
        except Exception as e:
            logger.debug(f"Submolt discovery failed: {e}")
            return

        if not submolts:
            return

        try:
            from vibe_core.mahamantra.substrate.encoding.resonance_ranker import resonate
        except ImportError:
            # Fallback: subscribe to all (original behavior)
            for submolt in submolts:
                if not isinstance(submolt, dict):
                    continue
                name = submolt.get("name", "")
                if name and name not in self._subscribed_submolts:
                    self._subscribed_submolts.add(name)
                    desc = submolt.get("description", "")
                    if desc:
                        self._submolt_descriptions[name] = desc
                    content_queue.enqueue(
                        {
                            "content_type": ContentType.SUBSCRIBE.value,
                            "submolt": name,
                            "source": "submolt_discovery",
                            "priority": 0,
                        }
                    )
            return

        cold_start = len(self._subscribed_submolts) < 3

        for submolt in submolts:
            if not isinstance(submolt, dict):
                continue
            name = submolt.get("name", "")
            if not name or name in self._subscribed_submolts:
                continue

            # Score by resonance: name + description
            desc = submolt.get("description", "")
            probe = f"{name} {desc}".strip()
            try:
                ranked = resonate(probe, top_n=3)
                score = sum(w.total_score for w in ranked) / len(ranked) if ranked else 0.0
            except Exception as e:
                logger.debug(f"Resonance scoring failed for {name}: {e}")
                score = 0.0

            if int(score * COSMIC_FRAME) > _SUBMOLT_RESONANCE_CF or cold_start:
                self._subscribed_submolts.add(name)
                if desc:
                    self._submolt_descriptions[name] = desc
                proposal: ContentProposal = {
                    "content_type": ContentType.SUBSCRIBE.value,
                    "submolt": name,
                    "source": "submolt_discovery",
                    "priority": 0,
                }
                content_queue.enqueue(proposal)
                logger.info(f"Submolt subscription queued: {name} (score={score:.3f})")
            else:
                logger.debug(
                    f"Submolt skipped: {name} (score_cf={int(score * COSMIC_FRAME)} < {_SUBMOLT_RESONANCE_CF})"
                )

    def select_submolt(self, seed_text: str, event_log_getter: Callable) -> Optional[str]:
        """Select best submolt for content via resonance cross-scoring.

        For each subscribed submolt, compute resonance between content words
        and submolt name. Weight by engagement history if available.
        """
        if not self._subscribed_submolts:
            return None

        try:
            from vibe_core.mahamantra.substrate.encoding.resonance_ranker import resonate
        except ImportError:
            return None

        # Get content resonance profile
        try:
            content_ranked = resonate(seed_text, top_n=3)
            content_score = sum(w.total_score for w in content_ranked) if content_ranked else 0.0
        except Exception as e:
            logger.debug(f"Content resonance scoring failed: {e}")
            return None

        if content_score == 0.0:
            return None

        # Build engagement history lookup (submolt → avg net_score)
        engagement_weights: Dict[str, float] = {}
        try:
            event_log = event_log_getter()
            metrics = event_log.get_events_by_type("engagement_metric", limit=50)
            submolt_scores: Dict[str, List[int]] = {}
            for e in metrics:
                s = e.payload.get("submolt", "")
                if s:
                    ns = e.payload.get("net_score", 0)
                    submolt_scores.setdefault(s, []).append(ns)
            for s, scores in submolt_scores.items():
                engagement_weights[s] = sum(scores) / len(scores) if scores else 0.0
        except Exception as e:
            logger.debug(f"Engagement history unavailable: {e}")

        # Cross-score each subscribed submolt
        best_submolt: Optional[str] = None
        best_score = 0.0

        for submolt_name in self._subscribed_submolts:
            try:
                submolt_ranked = resonate(submolt_name, top_n=3)
                submolt_total = sum(w.total_score for w in submolt_ranked) if submolt_ranked else 0.0
            except Exception as e:
                logger.debug(f"Resonance scoring failed for {submolt_name}: {e}")
                continue

            # Cross-score: product of content and submolt resonance
            cross = content_score * submolt_total

            # Weight by engagement history (1.0 + normalized avg)
            eng_weight = 1.0 + max(0.0, engagement_weights.get(submolt_name, 0.0) * 0.1)
            weighted = cross * eng_weight

            if weighted > best_score:
                best_score = weighted
                best_submolt = submolt_name

        if best_submolt:
            logger.debug(f"Selected submolt: {best_submolt} (score={best_score:.3f})")
        return best_submolt
