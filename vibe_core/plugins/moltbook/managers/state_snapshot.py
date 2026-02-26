"""Moltbook State Snapshot — Plugin state capture and restore."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Protocol

logger = logging.getLogger("MOLTBOOK.SNAPSHOT")


class StateSnapshotCallbacks(Protocol):
    """Callbacks that MoltbookPlugin provides to StateSnapshot."""

    _client: object  # MoltbookClient | None
    _heartbeat: object  # HeartbeatOrchestrator
    _content_queue: object  # ContentQueue
    _seen_message_ids: set
    _seen_post_ids: set
    _own_comment_ids: set
    _comment_post_map: dict
    _own_post_ids: dict
    _followed_agents: set
    _subscribed_submolts: set
    _feed_interval: int
    _post_interval: int
    _reply_check_interval: int
    _profile_update_interval: int


class StateSnapshot:
    """Capture and restore plugin state for persistence and recovery.

    Responsibilities:
    - Snapshot plugin state: client limits, queue stats, intervals, seen IDs
    - Include orchestrator state for recovery across restarts
    - Restore client limits from snapshot
    - Validate snapshot version compatibility

    YANTRA Discipline:
    - ONE format: version 7 (current)
    - Explicit state fields, no arbitrary dicts
    - ISO timestamp for all snapshots
    - Graceful restore for version compatibility (1-7)
    """

    CURRENT_VERSION = 7

    def __init__(self, plugin: "StateSnapshotCallbacks") -> None:
        """Initialize with parent plugin callbacks.

        Args:
            plugin: MoltbookPlugin instance providing callbacks
        """
        self._plugin: "StateSnapshotCallbacks" = plugin

    def snapshot(self) -> Dict[str, Any]:
        """Capture plugin state snapshot for persistence.

        Returns:
            Dict with version, client state, orchestrator state, metrics, and timestamp
        """
        # Fast path: client not active
        if not self._plugin._client:
            return {
                "version": self.CURRENT_VERSION,
                "client_active": False,
                "heartbeat_count": self._plugin._heartbeat.current_heartbeat_count,
                "orchestrator_state": self._plugin._heartbeat.snapshot(),
            }

        # Full path: capture all state for recovery
        limits = self._plugin._client.limits
        return {
            "version": self.CURRENT_VERSION,
            "client_active": True,
            "heartbeat_count": self._plugin._heartbeat.current_heartbeat_count,
            "orchestrator_state": self._plugin._heartbeat.snapshot(),
            # Rate limit state
            "requests_this_minute": limits.requests_this_minute,
            "posts_this_30m": limits.posts_this_30m,
            "comments_this_hour": limits.comments_this_hour,
            "last_minute_reset": limits.last_minute_reset,
            "last_30m_reset": limits.last_30m_reset,
            "last_hour_reset": limits.last_hour_reset,
            # Queue metrics
            "queue_size": self._plugin._content_queue.size,
            "queue_stats": self._plugin._content_queue.stats,
            # Deduplication tracking
            "seen_message_count": len(self._plugin._seen_message_ids),
            "seen_post_count": len(self._plugin._seen_post_ids),
            "own_comment_count": len(self._plugin._own_comment_ids),
            "comment_thread_count": len(self._plugin._comment_post_map),
            "own_post_count": len(self._plugin._own_post_ids),
            # Social graph
            "followed_agent_count": len(self._plugin._followed_agents),
            "subscribed_submolt_count": len(self._plugin._subscribed_submolts),
            # Intervals (diagnostic)
            "intervals": {
                "feed": self._plugin._feed_interval,
                "post": self._plugin._post_interval,
                "reply_check": self._plugin._reply_check_interval,
                "profile_update": self._plugin._profile_update_interval,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def restore(self, snapshot: Dict[str, Any]) -> None:
        """Restore plugin state from snapshot.

        Args:
            snapshot: State dict from previous snapshot() call

        Restores only client limits if version is compatible and client is active.
        """
        # Version compatibility check (1-7 supported)
        if snapshot.get("version") not in (1, 2, 3, 4, 5, 6, 7):
            logger.debug(f"Snapshot version {snapshot.get('version')} not compatible")
            return

        # Restore orchestrator state for recovery across restarts
        orch_state = snapshot.get("orchestrator_state", {})
        if orch_state:
            self._plugin._heartbeat.restore(orch_state)

        # Restore client limits only if client is active
        if not snapshot.get("client_active") or not self._plugin._client:
            return

        limits = self._plugin._client.limits
        limits.requests_this_minute = snapshot.get("requests_this_minute", 0)
        limits.posts_this_30m = snapshot.get("posts_this_30m", 0)
        limits.comments_this_hour = snapshot.get("comments_this_hour", 0)
        limits.last_minute_reset = snapshot.get("last_minute_reset", 0.0)
        limits.last_30m_reset = snapshot.get("last_30m_reset", 0.0)
        limits.last_hour_reset = snapshot.get("last_hour_reset", 0.0)
        logger.info("Plugin state restored from snapshot")
