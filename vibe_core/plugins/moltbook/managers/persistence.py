"""PersistenceManager — queue + seen IDs + phase state persistence.

Extracted from MoltbookPlugin._persist_queue() / _restore_queue() etc.

I/O routed through Mahamantra EnforceGateProvider (Guna-policy governance).
When gate is unavailable (test/standalone mode), falls back to direct write.
Reads are always direct (SATTVA — no governance needed).
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Set

from vibe_core.plugins.moltbook.state import (
    PHASE_STATE_FILE,
    QUEUE_STATE_FILE,
    SEEN_STATE_FILE,
)
from vibe_core.protocols.moltbook_content import ContentQueue

logger = logging.getLogger("MOLTBOOK_PERSIST")


def _get_rajas_guna() -> object:
    """Get Guna.RAJAS for governed writes. Returns None if unavailable."""
    try:
        from vibe_core.mahamantra.substrate.core.guna import Guna

        return Guna.RAJAS
    except ImportError:
        return None


def _governed_write(filename: str, data: dict, path: Path, actor: str, indent: int = 2) -> None:
    """Write state to disk, with gate audit trail when available.

    Always writes to disk (path). Additionally routes through
    get_sync_gate().write() for Guna-policy enforcement + audit trail.
    Gate writes to StateService RAM cache (governance), disk write is
    the actual persistence mechanism.

    Args:
        filename: State filename (for gate audit key)
        data: JSON-serializable dict
        path: Full path for disk write
        actor: Who is writing (for audit trail)
        indent: JSON indentation
    """
    # Gate audit trail (best-effort, never blocks disk write)
    try:
        from vibe_core.mahamantra.substrate.vm.gate_providers import get_sync_gate

        gate = get_sync_gate()
        guna = _get_rajas_guna()
        result = gate.write(filename, data, actor=actor, guna=guna)
        if not result["success"]:
            logger.warning(f"Gate audit: {filename} denied ({result['reason']})")
    except Exception:
        pass  # Gate unavailable — no audit, disk write still happens

    # Always write to disk — this is the actual persistence
    path.write_text(json.dumps(data, indent=indent))


class PersistenceManager:
    """Persist and restore plugin state to/from state directory.

    Writes routed through Mahamantra EnforceGateProvider (Guna I/O governance).
    Reads are direct (SATTVA — no governance needed for reads).
    """

    def __init__(self, state_dir: Optional[Path], max_seen_ids: int = 972):
        self._state_dir = state_dir
        self._max_seen_ids = max_seen_ids

    def persist_queue(
        self,
        queue: ContentQueue,
        seen_message_ids: Set[str],
        seen_post_ids: Set[str],
        own_comment_ids: Set[str],
        commented_post_ids: Set[str],
        followed_agents: Set[str],
        subscribed_submolts: Set[str],
        comment_post_map: Dict[str, str],
        own_post_ids: Dict[str, Dict[str, object]],
        max_own_post_ids: int = 200,
    ) -> None:
        """Save content queue + seen IDs to state dir."""
        if not self._state_dir:
            return
        try:
            # Queue: serialize proposals
            proposals = list(queue._queue)
            queue_data = {
                "version": 1,
                "proposals": [dict(p) for p in proposals],
                "stats": {
                    "total_enqueued": queue._total_enqueued,
                    "total_drained": queue._total_drained,
                    "total_dropped": queue._total_dropped,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            _governed_write(
                QUEUE_STATE_FILE,
                queue_data,
                self._state_dir / QUEUE_STATE_FILE,
                actor="moltbook_persistence",
            )

            # Seen IDs + tracking sets: cap to prevent unbounded growth
            cap = self._max_seen_ids
            msg_ids = sorted(seen_message_ids)[-cap:]
            post_ids = sorted(seen_post_ids)[-cap:]
            # Cap comment_post_map to last N entries
            cpm_keys = sorted(comment_post_map.keys())[-cap:]
            cpm = {k: comment_post_map[k] for k in cpm_keys}
            # Cap own_post_ids to most recent entries
            own_post_keys = sorted(
                own_post_ids.keys(),
                key=lambda k: own_post_ids[k].get("created_at", 0),
            )[-max_own_post_ids:]
            own_posts = {k: own_post_ids[k] for k in own_post_keys}

            seen_data = {
                "version": 5,
                "message_ids": msg_ids,
                "post_ids": post_ids,
                "own_comment_ids": sorted(own_comment_ids)[-cap:],
                "commented_post_ids": sorted(commented_post_ids)[-cap:],
                "followed_agents": sorted(followed_agents),
                "subscribed_submolts": sorted(subscribed_submolts),
                "comment_post_map": cpm,
                "own_post_ids": own_posts,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            _governed_write(
                SEEN_STATE_FILE,
                seen_data,
                self._state_dir / SEEN_STATE_FILE,
                actor="moltbook_persistence",
            )

            total = len(proposals)
            logger.info(f"State persisted: {total} queued proposals, {len(msg_ids)} msg IDs, {len(post_ids)} post IDs")
        except Exception as e:
            logger.warning(f"Queue persistence failed: {e}")

    def restore_queue(self, queue: ContentQueue) -> Dict[str, Any]:
        """Restore content queue + seen IDs from state dir.

        Returns dict with restored sets/maps for the caller to apply.
        Reads are direct (SATTVA) — no governance needed.
        """
        result: Dict[str, Any] = {}
        if not self._state_dir:
            return result

        # Restore queue
        queue_path = self._state_dir / QUEUE_STATE_FILE
        try:
            if queue_path.exists():
                data = json.loads(queue_path.read_text())
                if data.get("version") == 1:
                    for p in data.get("proposals", []):
                        # Clear stale retry state from previous session
                        p.pop("_retries", None)
                        p.pop("_retry_after", None)
                        queue.enqueue(p)
                    stats = data.get("stats", {})
                    queue._total_enqueued = stats.get("total_enqueued", 0)
                    queue._total_drained = stats.get("total_drained", 0)
                    queue._total_dropped = stats.get("total_dropped", 0)
                    restored = queue.size
                    if restored:
                        logger.info(f"Restored {restored} queued proposals from previous session")
        except Exception as e:
            logger.warning(f"Queue restore failed: {e}")

        # Restore seen IDs + tracking sets
        seen_path = self._state_dir / SEEN_STATE_FILE
        try:
            if seen_path.exists():
                data = json.loads(seen_path.read_text())
                if data.get("version") in (1, 2, 3, 4, 5):
                    result["seen_message_ids"] = set(data.get("message_ids", []))
                    result["seen_post_ids"] = set(data.get("post_ids", []))
                    result["own_comment_ids"] = set(data.get("own_comment_ids", []))
                    result["commented_post_ids"] = set(data.get("commented_post_ids", []))
                    result["followed_agents"] = set(data.get("followed_agents", []))
                    result["subscribed_submolts"] = set(data.get("subscribed_submolts", []))
                    result["comment_post_map"] = data.get("comment_post_map", {})
                    result["own_post_ids"] = data.get("own_post_ids", {})
                    logger.info(
                        f"Restored {len(result.get('seen_message_ids', set()))} msg IDs, "
                        f"{len(result.get('seen_post_ids', set()))} post IDs, "
                        f"{len(result.get('commented_post_ids', set()))} commented posts, "
                        f"{len(result.get('followed_agents', set()))} followed, "
                        f"{len(result.get('subscribed_submolts', set()))} subscribed, "
                        f"{len(result.get('comment_post_map', {}))} comment threads"
                    )
        except Exception as e:
            logger.warning(f"Seen IDs restore failed: {e}")

        return result

    def persist_phase_state(
        self,
        heartbeat_count: int,
        feed_topics: list,
        intents: list,
        orchestrator_state: dict | None = None,
        rate_limits: dict | None = None,
        network_intel_snapshot: dict | None = None,
    ) -> None:
        """Save cross-phase state (feed_topics + intents + heartbeat_count + rate limits).

        Survives GitHub Actions restarts so DHARMA can use GENESIS results
        from a previous run, and KARMA can use DHARMA intents.
        """
        if not self._state_dir:
            return
        try:
            # Serialize intents as dicts (StrategicIntent → dict)
            intent_dicts = []
            for intent in intents:
                if hasattr(intent, "__dict__"):
                    intent_dicts.append(intent.__dict__)
                elif isinstance(intent, dict):
                    intent_dicts.append(intent)

            phase_data = {
                "version": 1,
                "heartbeat_count": heartbeat_count,
                "feed_topics": feed_topics[:20],  # Cap to prevent bloat
                "intents": intent_dicts,
                "orchestrator_state": orchestrator_state or {},
                "rate_limits": rate_limits or {},
                "network_intel": network_intel_snapshot or {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            _governed_write(
                PHASE_STATE_FILE,
                phase_data,
                self._state_dir / PHASE_STATE_FILE,
                actor="moltbook_persistence",
            )
        except Exception as e:
            logger.warning(f"Phase state persist failed: {e}")

    def restore_phase_state(self) -> Dict[str, Any]:
        """Restore cross-phase state from previous run.

        Returns dict with: heartbeat_count, feed_topics, intents (as dicts).
        Reads are direct (SATTVA) — no governance needed.
        """
        result: Dict[str, Any] = {}
        if not self._state_dir:
            return result
        phase_path = self._state_dir / PHASE_STATE_FILE
        try:
            if not phase_path.exists():
                return result
            data = json.loads(phase_path.read_text())
            if data.get("version") != 1:
                return result

            result["heartbeat_count"] = int(data.get("heartbeat_count", 0))
            result["feed_topics"] = data.get("feed_topics", [])
            result["intent_dicts"] = data.get("intents", [])
            result["rate_limits"] = data.get("rate_limits", {})
            result["network_intel"] = data.get("network_intel", {})
        except Exception as e:
            logger.warning(f"Phase state restore failed: {e}")

        return result
