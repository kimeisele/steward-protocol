"""
Moltbook Plugin — Thin Shell
=============================

Lifecycle hooks (boot/pulse/shutdown) + manager wiring.
All business logic lives in managers/, service.py, lifecycle.py.

Architecture:
    mahamantra.tick() → _on_mahamantra_tick → HeartbeatOrchestrator
    on_pulse()        → same heartbeat path (backward compat)
    on_boot()         → BootManager
    on_shutdown()     → persist + cleanup

State is centralized in MoltbookState (state.py).
Service is MoltbookService (service.py).
Lifecycle wiring is in lifecycle.py.
PromptContext resolvers are in context_resolvers.py.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

from vibe_core.plugin_protocol import HookResult, KernelPlugin, PulsePhase
from vibe_core.plugins.moltbook.service import MoltbookService
from vibe_core.plugins.moltbook.state import (
    MAX_OWN_POST_IDS,
    MAX_SEEN_IDS,
    TICKS_PER_HEARTBEAT,
    MoltbookState,
)
from vibe_core.protocols.moltbook import MoltbookProtocol
from vibe_core.protocols.moltbook_content import ContentProposal, ContentProposalProtocol, ContentType

if TYPE_CHECKING:
    from pathlib import Path

    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("MOLTBOOK")


class MoltbookPlugin(KernelPlugin):
    """
    Moltbook membrane wired to Mahamantra via register_listener().

    Thin shell: all state in MoltbookState, all logic in managers.
    """

    plugin_id = "moltbook"

    # State field names for __getattr__/__setattr__ delegation.
    # Access to plugin._xxx delegates to plugin._s.xxx when xxx is a state field.
    _STATE_FIELDS: frozenset = frozenset(MoltbookState.__slots__)

    def __init__(self):
        super().__init__()
        # Centralized state — one object, not 30+ scattered fields
        self._s = MoltbookState()

        # Manager instances (lazy-init via properties)
        self._drainer_inst = None
        self._persistence_inst = None
        self._feed_inst = None
        self._engagement_inst = None
        self._dm_inst = None
        self._post_inst = None
        self._intent_inst = None
        self._heartbeat_inst = None
        self._boot_inst = None
        self._state_restorer_inst = None
        self._proposal_builder_inst = None
        self._vault_inst = None
        self._circuit_inst = None
        self._snapshot_inst = None
        self._wiring_inst = None

        # Agency Director + Strategy (lazy-init)
        self._agency_director_inst = None
        self._strategy_planner_inst = None

        # Agent events buffer for EventBus trending topics
        self._agent_events: List[Dict[str, Any]] = []

    # =========================================================================
    # Backward-compat: delegate plugin._xxx to plugin._s.xxx for state fields.
    # Tests and external code access plugin._content_queue, plugin._client, etc.
    # =========================================================================

    def __getattr__(self, name: str) -> Any:
        """Delegate plugin._xxx → plugin._s.xxx for MoltbookState fields."""
        if name.startswith("_") and not name.startswith("__"):
            field = name[1:]
            if field in MoltbookPlugin._STATE_FIELDS:
                return getattr(self._s, field)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        """Delegate plugin._xxx = val → plugin._s.xxx for MoltbookState fields."""
        if name.startswith("_") and not name.startswith("__"):
            field = name[1:]
            if field in MoltbookPlugin._STATE_FIELDS:
                # Guard: _s might not exist yet during __init__
                try:
                    s = object.__getattribute__(self, "_s")
                    setattr(s, field, value)
                    return
                except AttributeError:
                    pass
        super().__setattr__(name, value)

    # =========================================================================
    # Dependencies
    # =========================================================================

    @property
    def dependencies(self) -> Set[str]:
        return {"economy"}

    # =========================================================================
    # Backward-compat aliases for direct attribute access (tests)
    # =========================================================================

    @property
    def _strategy_planner(self):
        return self._strategy_planner_inst

    @_strategy_planner.setter
    def _strategy_planner(self, value):
        self._strategy_planner_inst = value

    @property
    def _agency_director(self):
        return self._agency_director_inst

    @_agency_director.setter
    def _agency_director(self, value):
        self._agency_director_inst = value

    # =========================================================================
    # Manager Lazy Properties — each manager is created once on first access
    # =========================================================================

    @property
    def agency_director(self):
        if self._agency_director_inst is None:
            from vibe_core.cartridges.agent_city.moltbook.core.agency_director import AgencyDirector

            self._agency_director_inst = AgencyDirector(plugin=self)
        return self._agency_director_inst

    @property
    def strategy_planner(self):
        if self._strategy_planner_inst is None:
            try:
                from vibe_core.cartridges.agent_city.moltbook.core.strategy import MoltbookStrategyPlanner

                self._strategy_planner_inst = MoltbookStrategyPlanner(
                    event_log=self.agency_director.event_log,
                    state_dir=self._s.state_dir,
                )
            except Exception as e:
                logger.warning(f"Strategy planner unavailable: {e}")
        return self._strategy_planner_inst

    @property
    def _content_drainer(self):
        if self._drainer_inst is None:
            from vibe_core.plugins.moltbook.managers.drainer import ContentDrainer

            self._drainer_inst = ContentDrainer(
                service_getter=self._ensure_service,
                log_activity=self._log_activity,
                broadcast_to_agora=self._broadcast_to_agora,
                emit_event=self._emit_event,
                own_post_ids=self._s.own_post_ids,
                own_comment_ids=self._s.own_comment_ids,
                comment_post_map=self._s.comment_post_map,
                followed_agents=self._s.followed_agents,
                subscribed_submolts=self._s.subscribed_submolts,
                bank=self._s.bank,
                agent_id=self._s.agent_name,
            )
        return self._drainer_inst

    @property
    def _persistence(self):
        if self._persistence_inst is None:
            from vibe_core.plugins.moltbook.managers.persistence import PersistenceManager

            self._persistence_inst = PersistenceManager(
                state_dir=self._s.state_dir,
                max_seen_ids=MAX_SEEN_IDS,
            )
        return self._persistence_inst

    @property
    def _feed(self):
        if self._feed_inst is None:
            from vibe_core.plugins.moltbook.managers.feed import FeedAnalyzer

            self._feed_inst = FeedAnalyzer(
                seen_post_ids=self._s.seen_post_ids,
                subscribed_submolts=self._s.subscribed_submolts,
                submolt_descriptions=self._s.submolt_descriptions,
            )
        return self._feed_inst

    @property
    def _engagement(self):
        if self._engagement_inst is None:
            from vibe_core.plugins.moltbook.managers.engagement import EngagementTracker

            self._engagement_inst = EngagementTracker(
                log_activity=self._log_activity,
                bank=self._s.bank,
                agent_id=self._s.agent_name,
            )
        return self._engagement_inst

    @property
    def _heartbeat(self):
        if self._heartbeat_inst is None:
            from vibe_core.plugins.moltbook.managers.heartbeat import HeartbeatOrchestrator

            self._heartbeat_inst = HeartbeatOrchestrator(state=self._s, actions=self)
        return self._heartbeat_inst

    @property
    def _dm(self):
        if self._dm_inst is None:
            from vibe_core.plugins.moltbook.managers.dm_processor import DMProcessor

            self._dm_inst = DMProcessor(
                state=self._s,
                director_propose=self._director_propose,
                follow_back=self._follow_back,
            )
        return self._dm_inst

    @property
    def _post(self):
        if self._post_inst is None:
            from vibe_core.plugins.moltbook.managers.post_orchestrator import PostOrchestrator

            self._post_inst = PostOrchestrator(state=self._s, actions=self)
        return self._post_inst

    @property
    def _intent(self):
        if self._intent_inst is None:
            from vibe_core.plugins.moltbook.managers.intent_executor import IntentExecutor

            self._intent_inst = IntentExecutor(
                state=self._s,
                director_propose=self._director_propose,
                select_submolt=self._select_submolt,
                emit_event=self._emit_event,
                heartbeat_count_getter=lambda: self._heartbeat.current_heartbeat_count,
            )
        return self._intent_inst

    @property
    def _boot(self):
        if self._boot_inst is None:
            from vibe_core.plugins.moltbook.managers.boot_manager import BootManager

            self._boot_inst = BootManager(state=self._s, actions=self)
        return self._boot_inst

    @property
    def _restorer(self):
        if self._state_restorer_inst is None:
            from vibe_core.plugins.moltbook.managers.state_restorer import StateRestorer

            self._state_restorer_inst = StateRestorer(
                state=self._s,
                persistence_getter=lambda: self._persistence,
                heartbeat_getter=lambda: self._heartbeat,
            )
        return self._state_restorer_inst

    @property
    def _builder(self):
        if self._proposal_builder_inst is None:
            from vibe_core.plugins.moltbook.managers.proposal_builder import ProposalBuilder

            self._proposal_builder_inst = ProposalBuilder(emit_event=self._emit_event)
        return self._proposal_builder_inst

    @property
    def _vault(self):
        if self._vault_inst is None:
            from vibe_core.plugins.moltbook.managers.vault_resolver import VaultResolver

            self._vault_inst = VaultResolver()
        return self._vault_inst

    @property
    def _circuit(self):
        if self._circuit_inst is None:
            from vibe_core.plugins.moltbook.managers.content_circuit import ContentCircuitExecutor

            self._circuit_inst = ContentCircuitExecutor(
                agency_director_getter=lambda: self.agency_director,
                emit_event=self._emit_event,
            )
        return self._circuit_inst

    @property
    def _snapshot(self):
        if self._snapshot_inst is None:
            from vibe_core.plugins.moltbook.managers.state_snapshot import StateSnapshot

            self._snapshot_inst = StateSnapshot(
                state=self._s,
                heartbeat_getter=lambda: self._heartbeat,
            )
        return self._snapshot_inst

    @property
    def _wiring_module(self):
        if self._wiring_inst is None:
            from vibe_core.plugins.moltbook.managers.wiring import WiringModule

            self._wiring_inst = WiringModule()
        return self._wiring_inst

    # HeartbeatOrchestrator tick counter delegation
    @property
    def _heartbeat_count(self) -> int:
        return self._heartbeat.current_heartbeat_count

    @property
    def _genesis_tick(self) -> int:
        return self._heartbeat._genesis_tick

    @_genesis_tick.setter
    def _genesis_tick(self, value: int):
        self._heartbeat._genesis_tick = value

    @property
    def _karma_tick(self) -> int:
        return self._heartbeat._karma_tick

    @_karma_tick.setter
    def _karma_tick(self, value: int):
        self._heartbeat._karma_tick = value

    @property
    def _moksha_tick(self) -> int:
        return self._heartbeat._moksha_tick

    @_moksha_tick.setter
    def _moksha_tick(self, value: int):
        self._heartbeat._moksha_tick = value

    # =========================================================================
    # Service Factory
    # =========================================================================

    def _ensure_service(self):
        """Ensure MoltbookService exists, create if needed."""
        if self._s.service is None:
            self._s.service = MoltbookService(self._s.client)
        return self._s.service

    # =========================================================================
    # Content Pipeline — ONE path through AgencyDirector
    # =========================================================================

    def _director_propose(
        self,
        content_type: str,
        raw_input: str,
        proposal_type: str,
        **extra,
    ) -> Optional[ContentProposal]:
        """Content generation: circuit state machine → ContentProposal."""
        extra_context = extra.get("context", {})
        circuit_result = self.execute_content_circuit(
            raw_input,
            content_type,
            post_id=extra.get("post_id", ""),
            sender=extra.get("sender", ""),
            trigger=extra.get("trigger", "heartbeat"),
            context=extra_context if isinstance(extra_context, dict) else {},
        )
        return self._builder.build_proposal(circuit_result, content_type, proposal_type, **extra)

    def execute_content_circuit(
        self,
        raw_input: str,
        content_type: str = "comment",
        post_id: str = "",
        sender: str = "",
        trigger: str = "heartbeat",
        auto_approve: bool = True,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """MOLTBOOK_CONTENT_V1 — ONE path through AgencyDirector."""
        return self._circuit.execute(
            raw_input=raw_input,
            content_type=content_type,
            post_id=post_id,
            sender=sender,
            trigger=trigger,
            context=context,
        )

    # =========================================================================
    # Persistence (delegates to PersistenceManager)
    # =========================================================================

    def _persist_queue(self) -> None:
        self._persistence.persist_queue(
            queue=self._s.content_queue,
            seen_message_ids=self._s.seen_message_ids,
            seen_post_ids=self._s.seen_post_ids,
            own_comment_ids=self._s.own_comment_ids,
            commented_post_ids=self._s.commented_post_ids,
            followed_agents=self._s.followed_agents,
            subscribed_submolts=self._s.subscribed_submolts,
            comment_post_map=self._s.comment_post_map,
            own_post_ids=self._s.own_post_ids,
            max_own_post_ids=MAX_OWN_POST_IDS,
        )
        self._persist_phase_state()

    def _restore_queue(self) -> None:
        restored = self._persistence.restore_queue(self._s.content_queue)
        if restored:
            for key in (
                "seen_message_ids",
                "seen_post_ids",
                "own_comment_ids",
                "commented_post_ids",
                "followed_agents",
                "subscribed_submolts",
                "comment_post_map",
                "own_post_ids",
            ):
                if key in restored:
                    setattr(self._s, key, restored[key])
        self._restorer.restore_phase_state()

    def _persist_phase_state(self) -> None:
        self._persistence.persist_phase_state(
            heartbeat_count=self._heartbeat.current_heartbeat_count,
            feed_topics=self._s.current_feed_topics,
            intents=self._s.current_intents,
            orchestrator_state=self._heartbeat.snapshot(),
        )

    # =========================================================================
    # PluginStateContract
    # =========================================================================

    def get_state_paths(self) -> List["Path"]:
        if self._s.state_dir:
            return [self._s.state_dir]
        return []

    def snapshot_state(self) -> Dict[str, Any]:
        return self._snapshot.snapshot()

    def restore_state(self, snapshot: Dict[str, Any]) -> None:
        self._snapshot.restore(snapshot)

    # =========================================================================
    # Lifecycle — Boot / Pulse / Shutdown
    # =========================================================================

    def on_boot(self, kernel: "RealVibeKernel", config: Optional[Dict[str, object]] = None) -> HookResult:
        return self._boot.execute_boot(kernel, config)

    @property
    def pulse_phase(self) -> PulsePhase:
        return PulsePhase.SENSORS

    def on_pulse(self, kernel: "RealVibeKernel", transaction: object) -> HookResult:
        """Backward compat: delegates to same heartbeat logic."""
        if not self._s.client:
            return HookResult.error("Client not initialized")
        try:
            heartbeat = self._s.client.sync_check_heartbeat()
            self._s.last_heartbeat_error = None
        except Exception as e:
            self._s.last_heartbeat_error = f"[{type(e).__name__}] {e!r}"
            heartbeat = {}
        self._heartbeat.dispatch_heartbeat(heartbeat)
        return HookResult.ok(
            data={
                "heartbeat": "ok" if not self._s.last_heartbeat_error else "failed",
                "error": self._s.last_heartbeat_error,
                "offline": self._s.offline_mode,
                "listener_wired": self._s.listener_wired,
                "ticks_seen": self._s.tick_count,
            }
        )

    def _on_mahamantra_tick(self, tick_state: object) -> None:
        """Called on every mahamantra.tick(). Polls once per full mantra cycle."""
        if not self._s.client:
            return
        self._s.tick_count += 1
        if self._s.tick_count % TICKS_PER_HEARTBEAT != 0:
            return
        try:
            heartbeat = self._s.client.sync_check_heartbeat()
            self._s.last_heartbeat_error = None
        except Exception as e:
            self._s.last_heartbeat_error = f"[{type(e).__name__}] {e!r}"
            logger.warning(f"DM check failed [{type(e).__name__}]: {e!r} — continuing heartbeat")
            heartbeat = {}
        self._heartbeat.dispatch_heartbeat(heartbeat)

    def on_shutdown(self, kernel: "RealVibeKernel") -> HookResult:
        self._persist_queue()
        from vibe_core.plugins.moltbook import lifecycle

        lifecycle.unwire_from_mahamantra(self._s, self._on_mahamantra_tick)
        self._s.client = None
        logger.info("Moltbook shutdown")
        return HookResult.ok()

    # =========================================================================
    # Phase-Aware Methods — MURALI routing (called by HeartbeatOrchestrator)
    # =========================================================================

    def _process_inbound_dms(self) -> None:
        self._dm.process_inbound_dms()

    def _process_dm_requests(self) -> None:
        self._dm.process_dm_requests()

    def _scan_feed(self) -> None:
        self._s.current_feed_topics = self._feed.scan_feed(
            client=self._s.client,
            proposer=self._s.proposer,
            content_queue=self._s.content_queue,
            service=self._s.service,
            strategy_planner=self.strategy_planner,
        )

    def _gather_broadcast_intelligence(self) -> None:
        from vibe_core.plugins.moltbook import lifecycle

        lifecycle.gather_broadcast_intelligence(self._s, self._agent_events)

    def _evaluate_strategy(self) -> None:
        from vibe_core.plugins.moltbook import lifecycle

        lifecycle.evaluate_strategy(self._s, self.strategy_planner)

    def _execute_intents(self) -> None:
        self._intent.execute_intents()

    def _check_own_comment_replies(self) -> None:
        self._post.check_own_comment_replies()

    def _update_profile(self) -> None:
        self._post.update_profile()

    def _track_engagement(self) -> None:
        self._engagement.track(
            service=self._s.service,
            own_post_ids=self._s.own_post_ids,
            own_comment_ids=self._s.own_comment_ids,
            comment_post_map=self._s.comment_post_map,
            event_log=self.agency_director.event_log,
            strategy_planner=self.strategy_planner,
        )

    def _adjust_intervals(self) -> None:
        self._s.feed_interval, self._s.post_interval = self._engagement.adjust_intervals(
            feed_interval=self._s.feed_interval,
            post_interval=self._s.post_interval,
        )

    def _monitor_queue_health(self) -> None:
        self._content_drainer.monitor_queue_health(self._s.content_queue, self._heartbeat_count)

    def _drain_content_queue(self) -> None:
        self._content_drainer.drain(self._s.content_queue, self._s.offline_mode)
        self._persist_queue()

    # =========================================================================
    # Lifecycle Wiring (delegates to lifecycle.py)
    # =========================================================================

    def _register_service(self) -> None:
        try:
            from vibe_core.di import ServiceRegistry

            self._s.service = MoltbookService(self._s.client)
            ServiceRegistry.register_factory(MoltbookProtocol, lambda: self._s.service)
            logger.info("MoltbookProtocol registered in ServiceRegistry")
        except Exception as e:
            logger.warning(f"ServiceRegistry registration failed: {e}")

    def _register_feedback(self) -> None:
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.feedback import FeedbackProtocol, InMemoryFeedback

            if not ServiceRegistry.is_registered(FeedbackProtocol):
                ServiceRegistry.register_factory(FeedbackProtocol, InMemoryFeedback)
                logger.info("FeedbackProtocol registered in ServiceRegistry")
        except Exception as e:
            logger.warning(f"FeedbackProtocol registration failed: {e}")

    def _wire_to_mahamantra(self) -> None:
        from vibe_core.plugins.moltbook import lifecycle

        lifecycle.wire_to_mahamantra(self._s, self._on_mahamantra_tick)

    def _init_agora(self) -> None:
        from vibe_core.plugins.moltbook import lifecycle

        lifecycle.init_agora(self._s)

    def _listen_agora(self) -> List[Dict[str, Any]]:
        from vibe_core.plugins.moltbook import lifecycle

        return lifecycle.listen_agora(self._s)

    def _init_bank(self) -> None:
        from vibe_core.plugins.moltbook import lifecycle

        lifecycle.init_bank(self._s)

    def _wire_event_listener(self) -> None:
        from vibe_core.plugins.moltbook import lifecycle

        lifecycle.wire_event_listener(self._agent_events, self._on_agent_action)

    def _on_agent_action(self, event: Any) -> None:
        from vibe_core.plugins.moltbook import lifecycle

        lifecycle.handle_agent_action(event, self._agent_events)

    def _wire_ouroboros(self) -> None:
        from vibe_core.plugins.moltbook import lifecycle

        lifecycle.wire_ouroboros(self)

    def on_event(self, event_type: str, data: Dict[str, Any]) -> None:
        from vibe_core.plugins.moltbook import lifecycle

        lifecycle.handle_ouroboros_event(
            event_type,
            data,
            self._emit_event,
            self.strategy_planner,
        )

    def _emit_ouroboros_health(self) -> None:
        from vibe_core.plugins.moltbook import lifecycle

        lifecycle.emit_ouroboros_health(self._s, self._heartbeat_count)

    def _record_heartbeat_reflection(self, department: str, duration_s: float) -> None:
        from vibe_core.plugins.moltbook import lifecycle

        lifecycle.record_heartbeat_reflection(
            department,
            duration_s,
            self._heartbeat_count,
            self._s.content_queue.size,
            self._s.last_heartbeat_error,
            self._s.offline_mode,
        )

    def _reflect_on_patterns(self) -> None:
        from vibe_core.plugins.moltbook import lifecycle

        lifecycle.reflect_on_patterns(self._emit_event)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def _safe_call(self, fn: object, label: str) -> None:
        try:
            fn()  # type: ignore[operator]
        except Exception as e:
            self._log_activity("heartbeat_error", {"phase": label, "error": str(e)[:200]})
            logger.warning(f"Heartbeat phase '{label}' failed: {e}")

    def _trim_memory(self) -> None:
        cap = MAX_SEEN_IDS
        if len(self._s.seen_message_ids) > cap:
            self._s.seen_message_ids = set(sorted(self._s.seen_message_ids)[-cap:])
        if len(self._s.seen_post_ids) > cap:
            self._s.seen_post_ids = set(sorted(self._s.seen_post_ids)[-cap:])
        if len(self._s.own_comment_ids) > cap:
            self._s.own_comment_ids = set(sorted(self._s.own_comment_ids)[-cap:])
        if len(self._s.comment_post_map) > cap:
            keys = sorted(self._s.comment_post_map.keys())[-cap:]
            self._s.comment_post_map = {k: self._s.comment_post_map[k] for k in keys}
        if len(self._s.own_post_ids) > MAX_OWN_POST_IDS:
            sorted_keys = sorted(
                self._s.own_post_ids.keys(),
                key=lambda k: self._s.own_post_ids[k].get("created_at", 0),
            )[-MAX_OWN_POST_IDS:]
            self._s.own_post_ids = {k: self._s.own_post_ids[k] for k in sorted_keys}
        if self._s.proposer and hasattr(self._s.proposer, "flush_cache"):
            self._s.proposer.flush_cache()

    def _follow_back(self, sender: str) -> None:
        if not sender or sender == "unknown" or sender in self._s.followed_agents:
            return
        self._s.followed_agents.add(sender)
        proposal: ContentProposal = {
            "content_type": ContentType.FOLLOW.value,
            "to_agent": sender,
            "source": "follow_back",
            "priority": 0,
        }
        self._s.content_queue.enqueue(proposal)
        logger.info(f"Follow-back queued for {sender}")

    def _log_activity(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        from vibe_core.plugins.moltbook import lifecycle

        lifecycle.log_activity(self._s.activity_log_path, event_type, self._heartbeat_count, payload)

    def _emit_event(self, event_type_name: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        from vibe_core.plugins.moltbook import lifecycle

        lifecycle.emit_event(event_type_name, message, data)

    def _discover_submolts(self) -> None:
        self._feed.ensure_own_submolt(self._s.client, self._s.content_queue)
        self._feed.discover_submolts(self._s.client, self._s.content_queue)

    def _select_submolt(self, seed_text: str) -> Optional[str]:
        return self._feed.select_submolt(seed_text, lambda: self.agency_director.event_log)

    def _check_rate_limit(self, content_type: str) -> bool:
        return self._content_drainer.check_rate_limit(content_type)

    def _record_rate_limit(self, content_type: str) -> None:
        self._content_drainer.record_rate_limit(content_type)

    def _wire_circuit_executor(self, kernel: "RealVibeKernel") -> None:
        self._wiring_module.wire_circuit_executor(kernel)

    def _wire_agora(self, kernel: "RealVibeKernel") -> None:
        self._wiring_module.wire_agora(kernel)

    def _broadcast_to_agora(self, content_type: str, content: str, metadata: Dict[str, Any]) -> None:
        metadata["agent_name"] = self._s.agent_name
        self._wiring_module.broadcast_to_agora(content_type, content, metadata)

    def _try_vault(self, kernel: "RealVibeKernel") -> str:
        return self._vault.resolve(kernel)

    # =========================================================================
    # Boot helpers
    # =========================================================================

    def _boot_proposer(self) -> None:
        from vibe_core.plugins.moltbook.resonance_proposer import ResonanceProposer

        self._s.proposer = ResonanceProposer(agent_name=self._s.agent_name)
        from vibe_core.plugins.moltbook import context_resolvers

        context_resolvers.register_all(self._s)
        logger.info("Content proposer: ResonanceProposer v3 (engine-wired)")

    def _register_proposer(self) -> None:
        try:
            from vibe_core.di import ServiceRegistry

            ServiceRegistry.register_factory(ContentProposalProtocol, lambda: self._s.proposer)
            logger.info("ContentProposalProtocol registered in ServiceRegistry")
        except Exception as e:
            logger.warning(f"ContentProposalProtocol registration failed: {e}")

    def _register_moltbook_context(self) -> None:
        from vibe_core.plugins.moltbook import context_resolvers

        context_resolvers.register_all(self._s)

    # =========================================================================
    # API — exposed to other plugins via kernel.api("moltbook")
    # =========================================================================

    def get_api(self) -> Optional[Dict[str, Any]]:
        return {
            "client": self._s.client,
            "offline": self._s.offline_mode,
            "last_error": self._s.last_heartbeat_error,
            "listener_wired": self._s.listener_wired,
            "ticks_seen": self._s.tick_count,
            "heartbeats": self._heartbeat_count,
            "content_queue": self._s.content_queue.stats,
            "intervals": {
                "feed": self._s.feed_interval,
                "post": self._s.post_interval,
                "reply_check": self._s.reply_check_interval,
                "profile_update": self._s.profile_update_interval,
            },
            "circuit_executor": bool(self._circuit_inst),
            "agora_wired": bool(self._s.agora),
            "execute_content_circuit": self.execute_content_circuit,
        }
