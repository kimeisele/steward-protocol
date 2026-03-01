"""
Moltbook Lifecycle — Wiring, healing, observability, and reflection.
====================================================================

All lifecycle-related code extracted from plugin_main.py:
- Mahamantra listener wiring
- AGORA initialization and listening
- CivicBank initialization
- EventBus subscription
- Ouroboros registration, event handling, health emission
- Synapse healing
- Reflection Protocol (recording + pattern analysis)

Functions receive MoltbookState + callbacks — no plugin reference.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("MOLTBOOK.LIFECYCLE")


# =========================================================================
# Mahamantra Wiring
# =========================================================================


def wire_to_mahamantra(state: Any, listener_fn: Callable) -> None:
    """Register as Mahamantra tick listener. Bombenfest."""
    if state.listener_wired:
        return
    try:
        from vibe_core.mahamantra import mahamantra

        mahamantra.register_listener(listener_fn)
        state.listener_wired = True
        logger.info("PARAMPARA: Moltbook wired to Mahamantra")
    except Exception as e:
        logger.warning(f"Mahamantra connection failed: {e}")


def unwire_from_mahamantra(state: Any, listener_fn: Callable) -> None:
    """Unregister Mahamantra tick listener."""
    if not state.listener_wired:
        return
    try:
        from vibe_core.mahamantra import mahamantra

        mahamantra.unregister_listener(listener_fn)
        state.listener_wired = False
    except Exception as e:
        logger.warning(f"Listener unregister failed during shutdown: {e}")


# =========================================================================
# AGORA — Broadcast channel
# =========================================================================


def init_agora(state: Any) -> None:
    """Initialize AGORA for broadcast listening (standalone-compatible)."""
    try:
        from vibe_core.cartridges.agent_city.agora.cartridge_main import AgoraCartridge

        state.agora = AgoraCartridge()
        logger.info("AGORA initialized for broadcast listening")
    except Exception as e:
        logger.warning(f"AGORA unavailable: {e}")


def listen_agora(state: Any) -> List[Dict[str, Any]]:
    """Listen for broadcast directives from herald/steward."""
    from vibe_core.mahamantra import run_async

    if state.agora is None:
        return []
    messages: List[Dict[str, Any]] = []
    for source in ("herald", "steward"):
        try:
            result = run_async(
                state.agora._listen_stream(
                    {
                        "agent_id": state.agent_name,
                        "source": source,
                        "since": state.agora_sequence,
                    }
                )
            )
            if isinstance(result, dict):
                msgs = result.get("messages", [])
                messages.extend(msgs)
                seq = result.get("next_sequence", state.agora_sequence)
                if seq > state.agora_sequence:
                    state.agora_sequence = seq
        except Exception as e:
            logger.warning(f"AGORA listen ({source}) failed: {e}")
    if messages:
        logger.info(f"AGORA: {len(messages)} broadcast messages received")
    return messages


def gather_broadcast_intelligence(state: Any, agent_events: List[Dict[str, Any]]) -> None:
    """Collect intelligence from AGORA broadcasts + EventBus into feed topics.

    Merges broadcast messages and agent events into state.current_feed_topics.
    Deduplicates by title to prevent topic flooding.
    """
    broadcasts = listen_agora(state)
    for msg in broadcasts:
        content = msg.get("content", msg.get("message", ""))
        source = msg.get("source", "broadcast")
        if content and len(content) > 10:
            state.current_feed_topics.append(
                {
                    "title": content[:200],
                    "content": content,
                    "id": f"agora_{source}_{state.agora_sequence}",
                    "source": f"agora:{source}",
                }
            )
    if agent_events:
        existing_titles = {str(t.get("title", "")).lower() for t in state.current_feed_topics}
        for evt in agent_events[-10:]:
            topic = evt.get("topic", "")
            agent = evt.get("agent", "unknown")
            if topic and len(topic) > 10 and topic.lower()[:80] not in existing_titles:
                state.current_feed_topics.append(
                    {
                        "title": topic[:200],
                        "content": topic,
                        "id": f"eventbus_{agent}_{hash(topic) % 10000}",
                        "source": f"eventbus:{agent}",
                    }
                )
        agent_events.clear()


# =========================================================================
# Strategy Evaluation — DHARMA phase
# =========================================================================


def evaluate_strategy(state: Any, strategy_planner: Any) -> None:
    """DHARMA phase: Evaluate strategy from gathered intelligence.

    Feeds engagement stats + feed topics into the strategy planner,
    which produces ranked intents for KARMA phase execution.
    Also reads CityReport for governance context and dispatches
    code-relevant intents to agent-city via federation.
    """
    if not strategy_planner:
        return
    engagement_stats: Dict[str, Any] = {}
    try:
        from vibe_core.protocols.feedback import get_feedback_safe

        stats = get_feedback_safe().get_stats()
        engagement_stats = {"success_rate": stats.success_rate, "total_signals": stats.total_signals}
    except Exception:
        pass

    # Federation inbound: extract m/agent-city posts from feed
    city_context = ""
    try:
        from vibe_core.plugins.moltbook.managers.feed import FeedAnalyzer

        city_posts = FeedAnalyzer.extract_city_feed(state.current_feed_topics)
        if city_posts:
            # Parse [City Report] + [Mission Result] posts structurally
            report_parts: List[str] = []
            mission_parts: List[str] = []
            signal_parts: List[str] = []
            for post in city_posts[:5]:
                title = str(post.get("title", ""))
                content = str(post.get("content", ""))
                if title.startswith("[City Report]"):
                    report_parts.append(_parse_city_report(title, content))
                elif title.startswith("[Mission Result]"):
                    mission_parts.append(_parse_city_report(title, content))
                else:
                    signal_parts.append(title[:100])
            parts: List[str] = []
            if report_parts:
                parts.append(f"CityReport: {'; '.join(report_parts)}")
            if mission_parts:
                parts.append(f"Missions: {'; '.join(mission_parts)}")
            if signal_parts:
                parts.append(f"Signals: {'; '.join(signal_parts)}")
            city_context = " | ".join(parts) if parts else ""
            logger.info(
                f"FEDERATION: {len(city_posts)} city posts ({len(report_parts)} reports, {len(signal_parts)} signals)"
            )
            emit_event(
                "PRAYER_RECEIVED",
                f"CityReport received: {len(report_parts)} reports, {len(signal_parts)} signals",
                {
                    "source": "federation",
                    "reports": len(report_parts),
                    "signals": len(signal_parts),
                },
            )
    except Exception as e:
        logger.warning(f"Federation feed extraction failed: {e}")

    try:
        intents = strategy_planner.plan_cycle(
            state.current_feed_topics,
            engagement_stats,
            own_post_ids=state.own_post_ids,
            commented_post_ids=state.commented_post_ids,
            network_intel=getattr(state, "network_intel", None),
        )
        state.current_intents = intents
        if intents:
            logger.info(f"Strategy: {len(intents)} intents ({', '.join(i.action_type for i in intents)})")
    except Exception as e:
        logger.warning(f"Strategy evaluation failed: {e}")
        return

    # Federation response: when city reports arrive, create response intents
    # These get priority 8 (higher than regular content) → KARMA executes them first
    federation_responses = _create_federation_responses(city_posts, city_context)
    if federation_responses:
        state.current_intents = federation_responses + state.current_intents
        logger.info(f"FEDERATION: {len(federation_responses)} response intent(s) injected")

    # Federation: dispatch code-relevant intents to agent-city
    _dispatch_federation_intents(state, intents, city_context)


def _parse_city_report(title: str, content: str) -> str:
    """Parse structured data from agent-city's [City Report] post.

    Agent-city's MoltbookBridge formats CityReports with:
    - Title: "[City Report] N agents, chain verified|BROKEN"
    - Content: Population, Mayor, Council, Missions, PRs, Chain, Directive Acks

    Also handles [Mission Result] posts:
    - Title: "[Mission Result] completed: mission_name — PR #42"

    Returns a compact summary for strategy context.
    """
    parts: List[str] = []

    # [Mission Result] posts — compact extraction
    if title.startswith("[Mission Result]"):
        result_text = title.replace("[Mission Result]", "").strip()
        return f"MissionResult: {result_text}"

    # Title already has population + chain status
    title_clean = title.replace("[City Report]", "").strip()
    if title_clean:
        parts.append(title_clean)

    # Extract structured fields from content
    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("Mayor:"):
            parts.append(line)
        elif line.startswith("Council:"):
            parts.append(line)
        elif line.startswith("Failing contracts:"):
            parts.append(line)
        elif line.startswith("Chain integrity:"):
            parts.append(line)
        # Directive acknowledgments (from OPUS_2: "ACK: DIR-xxx")
        elif "ACK:" in line and "DIR-" in line:
            parts.append(line.strip("- "))
        # Mission results
        elif line.startswith(("-",)) and any(s in line for s in ("completed", "active", "failed")):
            parts.append(line.lstrip("- "))
        # PR results
        elif line.startswith(("-",)) and ("PR" in line or "pr_url" in line.lower()):
            parts.append(line.lstrip("- "))

    return "; ".join(parts) if parts else title_clean


def _create_federation_responses(
    city_posts: List[Dict[str, object]],
    city_context: str,
) -> List[Any]:
    """Create response intents for city reports — closes the federation loop.

    When agent-city posts [City Report] or [Mission Result] to m/agent-city,
    steward-protocol responds with a [Steward] post acknowledging the report
    and providing directives or analysis.

    Max 1 response per DHARMA cycle. Only fires for structured reports,
    not general discussion.
    """
    if not city_posts or not city_context:
        return []

    from vibe_core.cartridges.agent_city.moltbook.core.strategy import StrategicIntent

    for post in city_posts[:3]:
        title = str(post.get("title", ""))
        # Only respond to structured reports, not random m/agent-city chatter
        if not any(title.startswith(prefix) for prefix in ("[City Report]", "[Mission Result]", "[Signal]")):
            continue

        return [
            StrategicIntent(
                action_type="post",
                topic=f"[Steward] {city_context[:200]}",
                reasoning="Federation relay — responding to agent-city report",
                priority=8,
                mission_id="federation_relay",
                target_submolt="agent-city",
                content_format="analysis",
            )
        ]

    return []


def _format_signal_title(topic: str, code_signals: frozenset) -> str:
    """Format a post title that agent-city's word-split detector can parse.

    Agent-city does: words = set(f"{title} {content}".lower().split())
    So signal keywords must appear as exact whitespace-delimited words
    (no colons, hyphens, or other punctuation attached to the keyword).

    Format: "[Signal] keyword — description"
    """
    # Find which signal keywords are in the topic (exact word match)
    topic_words = set(topic.lower().split())
    detected = sorted(topic_words & code_signals)
    if detected:
        # Keywords already in topic as exact words — just prefix
        return f"[Signal] {topic}"
    # Check if keywords appear as substrings (e.g., "fixing" contains "fix")
    # but aren't exact words — prepend the base keyword
    for signal in ("fix", "feature", "refactor", "test", "deploy", "implement", "bug", "api", "security", "merge"):
        if signal in topic.lower():
            return f"[Signal] {signal} — {topic}"
    # No code signal in topic at all — shouldn't happen since caller
    # already checked, but be safe
    return f"[Signal] {topic}"


def _dispatch_federation_intents(
    state: Any,
    intents: List[Any],
    city_context: str,
) -> None:
    """Route code-relevant intents to m/agent-city submolt.

    Instead of gh api dispatches (broken), tags StrategicIntents
    with target_submolt="agent-city" so they get posted there.
    Max 1 per DHARMA cycle.
    """
    if not intents:
        return

    # Aligned with agent-city's MoltbookBridge.CODE_SIGNALS — both repos
    # must use the same vocabulary for word-split signal detection.
    _CODE_SIGNALS = frozenset(
        {
            "bug",
            "fix",
            "feature",
            "implement",
            "refactor",
            "test",
            "pr",
            "merge",
            "patch",
            "regression",
            "deploy",
            "infrastructure",
            "api",
            "security",
            "performance",
            "migration",
        }
    )

    for intent in intents[:3]:
        topic_lower = intent.topic.lower() if hasattr(intent, "topic") else ""
        topic_words = set(topic_lower.split())
        matched_signals = topic_words & _CODE_SIGNALS
        if matched_signals:
            # Tag this intent for m/agent-city posting
            intent.target_submolt = "agent-city"
            # Ensure signal keywords appear as exact words in topic
            # so agent-city's word-split detection can parse them
            intent.topic = _format_signal_title(intent.topic, _CODE_SIGNALS)
            if city_context:
                intent.engagement_context = (
                    f"{intent.engagement_context}. {city_context}" if intent.engagement_context else city_context
                )
            logger.info(
                f"FEDERATION: intent → m/agent-city: {intent.topic[:80]} "
                f"(signals: {', '.join(sorted(matched_signals))})"
            )
            emit_event(
                "ACTION",
                f"Federation signal dispatched: {intent.topic[:80]}",
                {
                    "source": "federation",
                    "signals": sorted(matched_signals),
                    "target": "agent-city",
                },
            )
            return  # Max 1 per cycle


# =========================================================================
# CivicBank — Credit-gated publishing
# =========================================================================


def init_bank(state: Any) -> None:
    """Initialize CivicBank for credit-gated content publishing."""
    try:
        from vibe_core.cartridges.system.civic.tools.economy import CivicBank

        db_path = None
        if state.state_dir:
            db_path = str(state.state_dir / "economy.db")
        state.bank = CivicBank(db_path)
        balance = state.bank.get_balance(state.agent_name)
        if balance == 0:
            state.bank.transfer(
                "MINT",
                state.agent_name,
                1000,
                "moltbook_initial_mint",
                service_type="minting",
            )
            logger.info(f"CivicBank: minted 1000 initial credits for {state.agent_name}")
        else:
            logger.info(f"CivicBank: balance={balance} for {state.agent_name}")
    except Exception as e:
        logger.warning(f"CivicBank unavailable: {e}")
        state.bank = None


# =========================================================================
# EventBus — Inter-agent event subscription
# =========================================================================


def wire_event_listener(agent_events: List[Dict[str, Any]], on_action: Callable) -> None:
    """Subscribe to EventBus — hear what other agents are doing."""
    try:
        from vibe_core.mahamantra.substrate.event_types import EventType
        from vibe_core.mahamantra.substrate.services.event_bus import get_event_bus

        bus = get_event_bus()
        bus.subscribe(on_action, [EventType.ACTION])
        logger.info("EventBus subscribed: listening for ACTION events")
    except ImportError:
        logger.warning("EventBus not available — skipping subscription")
    except Exception as e:
        logger.warning(f"EventBus subscription failed: {e}")


def handle_agent_action(event: Any, agent_events: List[Dict[str, Any]]) -> None:
    """Handle ACTION events from other agents — discover trending topics."""
    agent_id = getattr(event, "agent_id", "")
    if agent_id == "moltbook":
        return  # Ignore own events
    message = getattr(event, "message", "")
    details = getattr(event, "details", {}) or {}
    if not message:
        return
    agent_events.append(
        {
            "agent": agent_id,
            "message": message[:200],
            "type": details.get("content_type", ""),
            "topic": details.get("topic", message[:100]),
        }
    )
    if len(agent_events) > 50:
        del agent_events[: len(agent_events) - 50]


# =========================================================================
# Ouroboros — Self-healing gene registration
# =========================================================================


def wire_ouroboros(event_handler: Any) -> None:
    """Register Moltbook as Ouroboros gene for self-healing + health monitoring."""
    try:
        from vibe_core.ouroboros.ananta_shesha import get_system_anchor

        anchor = get_system_anchor()
        anchor.register_gene_simple("moltbook", event_handler)
        anchor.subscribe("healing.requested", "moltbook")
        anchor.subscribe("violation.detected", "moltbook")
        logger.info("OUROBOROS: Moltbook registered as self-healing gene")
    except Exception as e:
        logger.warning(f"Ouroboros registration failed: {e}")


def handle_ouroboros_event(
    event_type: str,
    data: Dict[str, Any],
    emit_event: Callable,
    strategy_planner: Any,
) -> None:
    """Ouroboros event handler — react to system healing/violation events."""
    if event_type == "violation.detected":
        target = data.get("target", "")
        if "moltbook" in target.lower():
            logger.warning(f"OUROBOROS: Violation targeting moltbook: {data.get('message', '')}")
            emit_event("HEALING", f"Ouroboros violation: {data.get('message', '')}", data)
    elif event_type == "healing.requested":
        target = data.get("target", "")
        if target == "moltbook" or target == "strategy_planner":
            reason = data.get("reason", "")
            logger.info(f"OUROBOROS: Healing requested for {target}: {reason}")

            if target == "strategy_planner" and strategy_planner:
                strategy_planner._engagement_cache.clear()
                logger.info("KIRTAN: Strategy planner engagement cache cleared")

            if target == "moltbook":
                heal_synapse_weights()
                emit_event(
                    "HEALING_APPLIED",
                    f"Moltbook self-healing applied: {reason}",
                    {"target": target, "reason": reason},
                )


def heal_synapse_weights() -> None:
    """Kirtan: Heal degraded content synapse weights toward neutral."""
    try:
        from vibe_core.state.synapse_store import get_synapse_store

        store = get_synapse_store()
        weights = store.get_weights()
        decayed = 0
        for trigger, actions in weights.items():
            if trigger.startswith("moltbook:content:"):
                for action, w in actions.items():
                    if w < 0.4:
                        store.increment_weight(trigger, action, delta=0.05)
                        decayed += 1
        if decayed:
            store.save()
            logger.info(f"KIRTAN: Healed {decayed} degraded synapse weight(s)")
    except Exception as e:
        logger.warning(f"Synapse healing failed: {e}")


def emit_ouroboros_health(state: Any, heartbeat_count: int = 0) -> None:
    """Emit health status to Ouroboros — includes content generation metrics."""
    try:
        from vibe_core.ouroboros.ananta_shesha import get_system_anchor

        content_health: Dict[str, object] = {}
        try:
            from vibe_core.protocols.feedback import get_feedback_safe

            fb = get_feedback_safe()
            stats = fb.get_stats()
            content_health = {
                "success_rate": stats.success_rate,
                "failure_count": stats.failure_count,
                "total_signals": stats.total_signals,
            }
        except Exception as e:
            logger.warning(f"FeedbackProtocol unavailable: {e}")

        anchor = get_system_anchor()
        anchor.emit_event(
            "moltbook.health",
            {
                "heartbeat": heartbeat_count,
                "offline": state.offline_mode,
                "queue_size": state.content_queue.size,
                "last_error": state.last_heartbeat_error,
                "subscribed_submolts": len(state.subscribed_submolts),
                **content_health,
            },
        )
    except Exception as e:
        logger.warning(f"Ouroboros health emit unavailable: {e}")


# =========================================================================
# Reflection Protocol — Learning from execution patterns
# =========================================================================


def record_heartbeat_reflection(
    department: str,
    duration_s: float,
    heartbeat_count: int,
    queue_size: int,
    last_error: Optional[str],
    offline: bool,
) -> None:
    """Record heartbeat in Reflection Protocol for pattern analysis."""
    try:
        from vibe_core.protocols.reflection import ExecutionRecord, get_reflection_safe

        reflection = get_reflection_safe()
        record = ExecutionRecord(
            command=f"moltbook.heartbeat.{department}",
            success=last_error is None,
            error=last_error,
            duration_ms=duration_s * 1000,
            context={
                "department": department,
                "heartbeat": heartbeat_count,
                "queue_size": queue_size,
                "offline": offline,
            },
        )
        reflection.record_execution(record)
    except Exception as e:
        logger.warning(f"Reflection recording unavailable: {e}")


def reflect_on_patterns(emit_event: Callable) -> None:
    """MOKSHA: Analyze reflection patterns → trigger healing on failure."""
    try:
        from vibe_core.protocols.reflection import get_reflection_safe

        reflection = get_reflection_safe()
        patterns = reflection.analyze_patterns(limit=50)
        if not patterns:
            return

        failure_count = 0
        for insight in patterns:
            if getattr(insight, "type", None) == "failure_pattern":
                failure_count += 1
                emit_event(
                    "REFLECTION_INSIGHT",
                    f"Failure pattern detected: {insight.message}",
                    {"insight": insight.message, "confidence": getattr(insight, "confidence", 0)},
                )

        if failure_count > 0:
            try:
                from vibe_core.ouroboros.ananta_shesha import get_system_anchor

                anchor = get_system_anchor()
                anchor.request_healing(
                    target="moltbook",
                    reason=f"Content failure patterns detected: {failure_count} pattern(s) in last 50 executions",
                )
                logger.info(f"KIRTAN: Requested healing for {failure_count} failure pattern(s)")
            except Exception as e:
                logger.warning(f"Healing request failed: {e}")

        proposal = reflection.propose_improvement(patterns)
        if proposal and all(getattr(i, "confidence", 0) > 0.8 for i in getattr(proposal, "insights", [])):
            reflection.approve_proposal(proposal.id)
            logger.info(f"Reflection: auto-approved improvement '{proposal.title}'")
    except Exception as e:
        logger.warning(f"Reflection analysis failed: {e}")


# =========================================================================
# Activity Logging — JSONL audit trail with Guna governance
# =========================================================================


def log_activity(
    activity_log_path: Optional[Path],
    event_type: str,
    heartbeat_count: int,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    """Append an event to the JSONL activity log.

    Routes through EnforceGateProvider for Guna-policy audit trail.
    Falls back to direct append when gate is unavailable (test mode).
    """
    if not activity_log_path:
        return
    try:
        entry = {
            "t": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            "hb": heartbeat_count,
        }
        if payload:
            entry["data"] = payload
        line = json.dumps(entry, separators=(",", ":"))

        try:
            from vibe_core.mahamantra.substrate.core.guna import Guna
            from vibe_core.mahamantra.substrate.vm.gate_providers import get_sync_gate

            gate = get_sync_gate()
            result = gate.write(
                "moltbook_activity_log",
                entry,
                actor="moltbook_activity",
                guna=Guna.RAJAS,
            )
            if result["success"]:
                with activity_log_path.open("a") as f:
                    f.write(line + "\n")
            else:
                logger.debug(f"Activity log blocked by gate: {result['reason']}")
                return
        except Exception:
            with activity_log_path.open("a") as f:
                f.write(line + "\n")
    except Exception as e:
        logger.warning(f"Activity log write failed: {e}")


# =========================================================================
# Event Emission — Fire-and-forget to EventBus
# =========================================================================


def emit_event(event_type_name: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
    """Emit event to system EventBus. Fire-and-forget."""
    try:
        from vibe_core.mahamantra.substrate.event_types import EventType
        from vibe_core.mahamantra.substrate.services.event_bus import get_event_bus

        bus = get_event_bus()
        et = getattr(EventType, event_type_name, EventType.ACTION)
        bus.emit_sync(et, "moltbook", message, data or {})
    except Exception as e:
        logger.warning(f"EventBus emit unavailable: {e}")
