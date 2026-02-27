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
        service: Optional[MoltbookProtocol] = None,
        mission_descriptions: Optional[List[str]] = None,
    ) -> List[Dict[str, object]]:
        """GENESIS phase: Extract topics + metadata from feed. NO content generation.

        Sources:
        1. Personalized feed (hot posts from subscribed submolts)
        2. Semantic search (vector search for mission-relevant content)

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
            posts = []

        # ALL posts become topics for strategy (DHARMA needs context, not just new posts)
        feed_topics = posts if isinstance(posts, list) else []

        # Source 2: Semantic search — discover content beyond the hot feed
        if service and mission_descriptions:
            semantic_results = self._search_related_content(
                service, mission_descriptions, feed_topics,
            )
            feed_topics = feed_topics + semantic_results

        logger.info(f"Feed scan: {len(feed_topics)} topics ({len(feed_topics) - len(posts)} from semantic search)")

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

    @staticmethod
    def _search_related_content(
        service: MoltbookProtocol,
        mission_descriptions: List[str],
        existing_topics: List[Dict[str, object]],
    ) -> List[Dict[str, object]]:
        """Semantic search: discover content related to active missions.

        Queries the Moltbook vector search API with mission descriptions.
        Deduplicates against posts already in the feed.

        Returns additional topics to merge into feed_topics.
        """
        existing_ids = {
            str(p.get("id", "")) for p in existing_topics if isinstance(p, dict)
        }
        additional: List[Dict[str, object]] = []

        # Search with up to 3 mission descriptions (cap API calls)
        for desc in mission_descriptions[:3]:
            try:
                results = service.search(desc[:100], limit=5)
                if not results:
                    continue
                for result in results:
                    if not isinstance(result, dict):
                        continue
                    post_id = str(result.get("id", ""))
                    if post_id and post_id not in existing_ids:
                        existing_ids.add(post_id)
                        additional.append({
                            "id": post_id,
                            "title": result.get("title", result.get("content", ""))[:200],
                            "content": result.get("content", ""),
                            "author": result.get("author", {}),
                            "submolt": result.get("submolt", ""),
                            "source": "semantic_search",
                        })
            except Exception as e:
                logger.debug(f"Semantic search failed for '{desc[:40]}': {e}")

        if additional:
            logger.info(f"Semantic search: {len(additional)} new posts discovered")
        return additional

    # Agent's own submolt — created autonomously on first discovery
    _OWN_SUBMOLT = "steward-protocol"
    _OWN_SUBMOLT_DISPLAY = "Steward Protocol"
    _OWN_SUBMOLT_DESC = "Autonomous systems engineering — infrastructure, observability, distributed systems."

    def ensure_own_submolt(self, client: MoltbookProtocol, content_queue: ContentQueue) -> None:
        """Ensure 'steward-protocol' submolt exists. Create if not. Subscribe if not."""
        if self._OWN_SUBMOLT in self._subscribed_submolts:
            return  # Already subscribed → exists

        # Check if it exists in known submolts
        try:
            submolts = run_async(client.get_submolts())
            names = {s.get("name", "") for s in submolts if isinstance(s, dict)}
        except Exception:
            return  # API unavailable, try next cycle

        if self._OWN_SUBMOLT not in names:
            try:
                client.sync_create_submolt(self._OWN_SUBMOLT, self._OWN_SUBMOLT_DISPLAY, self._OWN_SUBMOLT_DESC)
                logger.info(f"Created submolt: {self._OWN_SUBMOLT}")
            except Exception as e:
                logger.warning(f"Submolt creation failed: {e}")
                return

        # Subscribe
        self._subscribed_submolts.add(self._OWN_SUBMOLT)
        self._submolt_descriptions[self._OWN_SUBMOLT] = self._OWN_SUBMOLT_DESC
        content_queue.enqueue({
            "content_type": ContentType.SUBSCRIBE.value,
            "submolt": self._OWN_SUBMOLT,
            "source": "own_submolt_init",
            "priority": 0,
        })
        logger.info(f"Own submolt '{self._OWN_SUBMOLT}' ensured + subscription queued")

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
        """Select best submolt for content via RAMA coordinate similarity.

        Computes basin_cosine between content RAMA coords and each submolt's
        description RAMA coords. Weights by engagement history.

        Uses description (not just name) — "openclaw-explorers" alone has no
        semantic meaning; "Open source law and regulation" does.
        """
        if not self._subscribed_submolts:
            return None

        try:
            from vibe_core.mahamantra.substrate.core.basin_map import basin_cosine
            from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
        except ImportError:
            return None

        lotus = get_mahamantra()

        # RAMA coordinates for the content
        try:
            content_coords = lotus.nama(seed_text[:200])
        except Exception as e:
            logger.debug(f"Content RAMA coords failed: {e}")
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

        # Score each subscribed submolt by semantic similarity to content
        best_submolt: Optional[str] = None
        best_score = 0.0

        for submolt_name in self._subscribed_submolts:
            # Use description for semantic matching (not bare name)
            desc = self._submolt_descriptions.get(submolt_name, "")
            probe = f"{submolt_name} {desc}".strip() if desc else submolt_name
            try:
                submolt_coords = lotus.nama(probe[:200])
                sim = basin_cosine(content_coords, submolt_coords)
            except Exception as e:
                logger.debug(f"Submolt scoring failed for {submolt_name}: {e}")
                continue

            # Weight by engagement history (1.0 + normalized avg)
            eng_weight = 1.0 + max(0.0, engagement_weights.get(submolt_name, 0.0) * 0.1)
            weighted = sim * eng_weight

            if weighted > best_score:
                best_score = weighted
                best_submolt = submolt_name

        if best_submolt:
            logger.debug(f"Selected submolt: {best_submolt} (sim={best_score:.3f})")
        return best_submolt
