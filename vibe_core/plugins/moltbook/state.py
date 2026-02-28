"""
MoltbookState — Centralized state container for the Moltbook plugin.
====================================================================

All mutable plugin state lives here. Managers access fields on this
object instead of reaching into the plugin God Object.

Constants derived from SSOT (protocols/seed/_axioms.py) are also here
to keep plugin_main.py thin.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from vibe_core.mahamantra.substrate.core.seed import (
    COSMIC_FRAME,
    HARE_COUNT,
    KSHETRA,
    LILA,
    MALA,
    NAVA,
    QUARTERS,
    WORDS,
)
from vibe_core.protocols.moltbook_content import ContentProposalProtocol, ContentQueue

# =========================================================================
# Constants (derived from SSOT, used across the moltbook plugin)
# =========================================================================

#: One full mantra = WORDS ticks. Poll Moltbook once per chant cycle.
TICKS_PER_HEARTBEAT: int = WORDS  # 16 words in Mahamantra

#: Default heartbeat intervals — all derived from SEED constants.
DEFAULT_FEED_INTERVAL: int = QUARTERS  # 4 phases
DEFAULT_POST_INTERVAL: int = KSHETRA  # 24 field elements
DEFAULT_REPLY_CHECK_INTERVAL: int = HARE_COUNT  # 8 Hare
DEFAULT_PROFILE_UPDATE_INTERVAL: int = LILA  # 48 Chaitanya's manifest

#: Capacity cap for seen-ID sets. 108 beads × 9 processes = 972.
MAX_SEEN_IDS: int = MALA * NAVA

#: Maximum tracked own posts. 21600 / 108 = 200.
MAX_OWN_POST_IDS: int = COSMIC_FRAME // MALA

#: State file names.
QUEUE_STATE_FILE: str = "content_queue.json"
SEEN_STATE_FILE: str = "seen_ids.json"
PHASE_STATE_FILE: str = "phase_state.json"
ACTIVITY_LOG_FILE: str = "activity.jsonl"


class MoltbookState:
    """Container for all mutable moltbook plugin state.

    Created once by MoltbookPlugin.__init__(), passed to managers
    that need access to shared state. Each field has a clear type
    and default — no more 30+ untyped self._ scattered across __init__.
    """

    __slots__ = (
        "client",
        "service",
        "offline_mode",
        "standalone_mode",
        "last_heartbeat_error",
        "state_dir",
        "tick_count",
        "feed_interval",
        "post_interval",
        "reply_check_interval",
        "profile_update_interval",
        "listener_wired",
        "content_queue",
        "proposer",
        "seen_message_ids",
        "seen_post_ids",
        "own_comment_ids",
        "commented_post_ids",
        "last_post_heartbeat",
        "followed_agents",
        "subscribed_submolts",
        "submolt_descriptions",
        "comment_post_map",
        "last_profile_heartbeat",
        "activity_log_path",
        "agent_name",
        "bank",
        "agora",
        "agora_sequence",
        "current_intents",
        "current_feed_topics",
        "own_post_ids",
    )

    def __init__(self) -> None:
        # --- Connection ---
        self.client: Any = None  # MoltbookClient, set at boot
        self.service: Any = None  # MoltbookService, created lazily
        self.offline_mode: bool = True
        self.standalone_mode: bool = False

        # --- Health ---
        self.last_heartbeat_error: Optional[str] = None

        # --- Paths ---
        self.state_dir: Optional[Path] = None
        self.activity_log_path: Optional[Path] = None

        # --- Counters ---
        self.tick_count: int = 0
        self.last_post_heartbeat: int = 0
        self.last_profile_heartbeat: int = 0
        self.agora_sequence: int = 0

        # --- Intervals (adaptive, diagnostic) ---
        self.feed_interval: int = DEFAULT_FEED_INTERVAL
        self.post_interval: int = DEFAULT_POST_INTERVAL
        self.reply_check_interval: int = DEFAULT_REPLY_CHECK_INTERVAL
        self.profile_update_interval: int = DEFAULT_PROFILE_UPDATE_INTERVAL

        # --- Wiring flags ---
        self.listener_wired: bool = False

        # --- Content pipeline ---
        self.content_queue: ContentQueue = ContentQueue()
        self.proposer: Optional[ContentProposalProtocol] = None

        # --- Deduplication sets ---
        self.seen_message_ids: Set[str] = set()
        self.seen_post_ids: Set[str] = set()
        self.own_comment_ids: Set[str] = set()
        self.commented_post_ids: Set[str] = set()
        self.followed_agents: Set[str] = set()
        self.subscribed_submolts: Set[str] = set()

        # --- Tracking dicts ---
        self.submolt_descriptions: Dict[str, str] = {}
        self.comment_post_map: Dict[str, str] = {}
        self.own_post_ids: Dict[str, Dict[str, object]] = {}

        # --- Agent identity ---
        self.agent_name: str = "steward-protocol"

        # --- External integrations (lazy) ---
        self.bank: Any = None  # CivicBank
        self.agora: Any = None  # AgoraCartridge

        # --- Strategy ---
        self.current_intents: List[Any] = []
        self.current_feed_topics: List[Dict[str, object]] = []
