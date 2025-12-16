"""
OPUS-087: PRANA Orchestrator
============================

Plugin Pulse Architecture for heartbeat macro-cycles.

ARCHITECTURE DECISION: This is SEPARATE from vibe_core/prana.py (config loader).
This module handles orchestration, transactions, and plugin coordination.

Key Components:
    - StateMutation: Typed mutation schema for plugin state changes
    - PulseTransaction: Atomic batch commit with fail-forward strategy
    - PranaOrchestrator: Plugin pulse coordination with isolation wrappers

Units Convention: All time values in SECONDS internally.
"""

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, Tuple

from vibe_core.plugin_protocol import HookResult, KernelPlugin, PluginResult, PulsePhase

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("PRANA_ORCHESTRATOR")


# =============================================================================
# MUTATION SCHEMA
# =============================================================================

# Allowed mutation actions (extensible)
ALLOWED_ACTIONS: Set[str] = {
    "update_doc",  # Update markdown file
    "decay_karma",  # Adjust karma score
    "refresh_state",  # Refresh Prakriti layer
    "log_observation",  # Add to system journal
    "quarantine_plugin",  # Disable misbehaving plugin
}


@dataclass
class StateMutation:
    """
    Single state change request from a plugin.

    OPUS-087: Plugins MUST NOT commit to Git during on_pulse.
    They register mutations with PulseTransaction instead.
    """

    plugin_id: str
    action: str  # e.g., "update_doc", "decay_karma", "refresh_opus"
    target: str  # e.g., "OPUS.md", "karma.json", "agent:envoy"
    payload: Dict[str, Any]
    priority: int = 1  # Lower = execute first within phase

    def validate(self) -> bool:
        """
        Pre-flight validation before commit.

        Validation Rules:
        1. plugin_id MUST be non-empty
        2. action MUST be in allowed actions list
        3. target MUST be non-empty
        4. payload MUST be a dict
        """
        if not self.plugin_id:
            return False
        if not self.action:
            return False
        if self.action not in ALLOWED_ACTIONS:
            return False
        if not self.target:
            return False
        if not isinstance(self.payload, dict):
            return False
        return True


# =============================================================================
# PULSE TRANSACTION
# =============================================================================


class PulseTransaction:
    """
    Collects mutations from all plugins for atomic batch commit.

    FAIL-FORWARD STRATEGY (OPUS-087):
    - If validation fails BEFORE write → Abort entire transaction
    - If error occurs DURING write → Log, continue, don't rollback
    - Git state is too complex for safe rollback
    """

    def __init__(self) -> None:
        self.mutations: List[StateMutation] = []
        self.validation_errors: List[str] = []
        self.execution_errors: List[str] = []
        self.committed: bool = False
        self._mutation_handlers: Dict[str, Callable[[StateMutation], bool]] = {}

    def register(self, mutation: StateMutation) -> bool:
        """
        Register a mutation. Returns False if validation fails.

        Args:
            mutation: The StateMutation to register

        Returns:
            True if mutation was registered, False if validation failed
        """
        if not mutation.validate():
            error_msg = f"{mutation.plugin_id}: Invalid mutation {mutation.action} on {mutation.target}"
            self.validation_errors.append(error_msg)
            logger.warning(f"PulseTransaction: {error_msg}")
            return False

        self.mutations.append(mutation)
        logger.debug(f"PulseTransaction: Registered {mutation.action} on {mutation.target} from {mutation.plugin_id}")
        return True

    def abort(self, reason: str) -> None:
        """Abort transaction before commit. Clears all mutations."""
        logger.warning(f"PulseTransaction ABORT: {reason}")
        self.mutations.clear()
        self.validation_errors.append(f"ABORT: {reason}")

    def register_handler(self, action: str, handler: Callable[[StateMutation], bool]) -> None:
        """
        Register a handler for a specific action type.

        The handler receives a StateMutation and returns True on success, False on failure.
        """
        self._mutation_handlers[action] = handler
        logger.debug(f"PulseTransaction: Registered handler for action '{action}'")

    def commit(self) -> Tuple[int, int]:
        """
        Execute all mutations. Returns (success_count, failure_count).

        FAIL-FORWARD STRATEGY:
        - If validation errors exist → Return immediately (0, N)
        - If error occurs DURING write → Log, continue, don't rollback
        """
        if self.committed:
            logger.warning("PulseTransaction: Already committed, skipping")
            return (0, 0)

        if self.validation_errors:
            logger.error(f"Cannot commit: {len(self.validation_errors)} validation errors")
            return (0, len(self.mutations))

        success, failure = 0, 0
        sorted_mutations = sorted(self.mutations, key=lambda m: m.priority)

        for mutation in sorted_mutations:
            try:
                self._apply_mutation(mutation)
                success += 1
            except Exception as e:
                error_msg = f"Mutation failed: {mutation.plugin_id}/{mutation.action}: {e}"
                logger.error(error_msg)
                self.execution_errors.append(error_msg)
                failure += 1
                # FAIL-FORWARD: Continue with next mutation

        self.committed = True
        logger.info(f"PulseTransaction: Committed {success} mutations, {failure} failures")
        return (success, failure)

    def _apply_mutation(self, mutation: StateMutation) -> None:
        """
        Apply a single mutation.

        Uses registered handlers if available, otherwise logs and skips.
        """
        handler = self._mutation_handlers.get(mutation.action)
        if handler:
            result = handler(mutation)
            if not result:
                raise RuntimeError(f"Handler returned False for {mutation.action}")
        else:
            # No handler registered - log for now
            logger.debug(
                f"PulseTransaction: No handler for '{mutation.action}', "
                f"mutation recorded but not applied: {mutation.target}"
            )


# =============================================================================
# ORCHESTRATOR CONFIG
# =============================================================================


@dataclass
class PranaOrchestratorConfig:
    """
    Configuration for the PRANA Orchestrator.

    CRITICAL: All time values in SECONDS (OPUS-087 Units Convention).
    """

    min_pulse_interval_seconds: int = 60  # NEVER faster than 60s
    default_interval_seconds: int = 900  # 15 min default
    quarantine_threshold: int = 3  # Failures before quarantine


# =============================================================================
# PRANA ORCHESTRATOR
# =============================================================================


class PranaOrchestrator:
    """
    Plugin Pulse Coordination with Isolation Wrappers.

    OPUS-087 Safety Features:
    1. Isolation Wrappers (Bad Apple Problem) - One crash doesn't kill others
    2. Deterministic Sequence (Varna System) - Plugins declare execution phase
    3. Adrenaline Governor (Rate Limiting) - Conservative voting for frequency
    4. Best Effort Batching (Fail-Forward Strategy) - No rollback on partial failure
    """

    def __init__(
        self,
        kernel: Optional["RealVibeKernel"] = None,
        config: Optional[PranaOrchestratorConfig] = None,
    ) -> None:
        self.kernel = kernel
        self.config = config or PranaOrchestratorConfig()
        self._quarantined_plugins: Set[str] = set()
        self._manual_plugins: List[KernelPlugin] = []
        self._failure_counts: Dict[str, int] = {}
        self._pulse_results: Dict[str, Any] = {}

    def register_plugin(self, plugin: KernelPlugin) -> None:
        """
        Manually register a plugin (for headless mode).

        Useful when running Prana without a full kernel boot.
        """
        self._manual_plugins.append(plugin)
        logger.debug(f"PranaOrchestrator: Manually registered plugin '{plugin.plugin_id}'")

    def get_plugins(self) -> List[KernelPlugin]:
        """Get all registered kernel plugins (kernel + manual), excluding quarantined ones."""
        kernel_plugins = []
        if self.kernel:
            kernel_plugins = getattr(self.kernel, "_plugins", [])

        all_plugins = self._manual_plugins + kernel_plugins

        # Deduplicate by plugin_id (prefer kernel instances if duplicate)
        seen_ids = set()
        unique_plugins = []

        for p in all_plugins:
            if p.plugin_id not in seen_ids and p.plugin_id not in self._quarantined_plugins:
                unique_plugins.append(p)
                seen_ids.add(p.plugin_id)

        return unique_plugins

    def run_pulse_cycle(self) -> Dict[str, Any]:
        """
        Execute one complete pulse cycle.

        Returns:
            Dict with results including success/failure counts
        """
        logger.info("🫀 PRANA: Starting pulse cycle...")

        # Create transaction for this cycle
        transaction = PulseTransaction()

        # Register default mutation handlers
        self._register_default_handlers(transaction)

        # Get plugins sorted by phase
        plugins = self.get_plugins()
        plugins_by_phase = self._sort_plugins_by_phase(plugins)

        total_success = 0
        total_failure = 0
        phase_results: Dict[str, Dict[str, Any]] = {}

        # Execute plugins in phase order
        for phase in PulsePhase:
            phase_plugins = plugins_by_phase.get(phase, [])
            if not phase_plugins:
                continue

            logger.info(f"  → Phase {phase.name}: {len(phase_plugins)} plugins")
            phase_result = self._execute_phase(phase, phase_plugins, transaction)
            phase_results[phase.name] = phase_result
            total_success += phase_result["success"]
            total_failure += phase_result["failure"]

        # Commit all mutations atomically
        logger.info("  → Committing mutations...")
        commit_success, commit_failure = transaction.commit()

        result = {
            "status": "completed",
            "plugins_executed": total_success,
            "plugins_failed": total_failure,
            "mutations_committed": commit_success,
            "mutations_failed": commit_failure,
            "validation_errors": len(transaction.validation_errors),
            "execution_errors": len(transaction.execution_errors),
            "quarantined_plugins": list(self._quarantined_plugins),
            "phase_results": phase_results,
        }

        logger.info(
            f"🫀 PRANA: Pulse complete - "
            f"{total_success} plugins OK, {total_failure} failed, "
            f"{commit_success} mutations committed"
        )

        self._pulse_results = result
        return result

    def _sort_plugins_by_phase(self, plugins: List[KernelPlugin]) -> Dict[PulsePhase, List[KernelPlugin]]:
        """Sort plugins into phase buckets."""
        by_phase: Dict[PulsePhase, List[KernelPlugin]] = {phase: [] for phase in PulsePhase}

        for plugin in plugins:
            phase = plugin.pulse_phase
            by_phase[phase].append(plugin)

        return by_phase

    def _execute_phase(
        self,
        phase: PulsePhase,
        plugins: List[KernelPlugin],
        transaction: PulseTransaction,
    ) -> Dict[str, Any]:
        """
        Execute all plugins in a single phase with isolation wrappers.

        BAD APPLE PROBLEM: One crash doesn't kill others.
        """
        success = 0
        failure = 0
        results: Dict[str, Any] = {}

        for plugin in plugins:
            plugin_id = plugin.plugin_id

            try:
                # Call plugin's on_pulse with transaction
                result = plugin.on_pulse(self.kernel, transaction)

                if result.status == PluginResult.OK:
                    success += 1
                    results[plugin_id] = {"status": "ok", "data": result.data}
                    self._reset_failure_count(plugin_id)
                elif result.status == PluginResult.ERROR:
                    failure += 1
                    results[plugin_id] = {"status": "error", "error": result.error_message}
                    self._record_failure(plugin_id)
                else:  # FATAL
                    failure += 1
                    results[plugin_id] = {"status": "fatal", "error": result.error_message}
                    self._quarantine_plugin(plugin_id, result.error_message or "FATAL error")

            except Exception as e:
                # Isolation wrapper: catch and log, don't propagate
                failure += 1
                error_msg = f"{type(e).__name__}: {e}"
                results[plugin_id] = {"status": "exception", "error": error_msg}
                logger.error(f"PRANA: Plugin {plugin_id} crashed: {error_msg}")
                self._record_failure(plugin_id)
                # Loop continues! Heart keeps beating.

        return {
            "phase": phase.name,
            "success": success,
            "failure": failure,
            "results": results,
        }

    def _record_failure(self, plugin_id: str) -> None:
        """Record a plugin failure. Quarantine if threshold exceeded."""
        self._failure_counts[plugin_id] = self._failure_counts.get(plugin_id, 0) + 1

        if self._failure_counts[plugin_id] >= self.config.quarantine_threshold:
            self._quarantine_plugin(plugin_id, f"Exceeded failure threshold ({self.config.quarantine_threshold})")

    def _reset_failure_count(self, plugin_id: str) -> None:
        """Reset failure count on success."""
        self._failure_counts[plugin_id] = 0

    def _quarantine_plugin(self, plugin_id: str, reason: str) -> None:
        """Quarantine a misbehaving plugin."""
        if plugin_id not in self._quarantined_plugins:
            self._quarantined_plugins.add(plugin_id)
            logger.warning(f"⚠️ PRANA: Plugin '{plugin_id}' QUARANTINED: {reason}")

    def unquarantine_plugin(self, plugin_id: str) -> bool:
        """Remove a plugin from quarantine. Returns True if it was quarantined."""
        if plugin_id in self._quarantined_plugins:
            self._quarantined_plugins.discard(plugin_id)
            self._failure_counts[plugin_id] = 0
            logger.info(f"✅ PRANA: Plugin '{plugin_id}' removed from quarantine")
            return True
        return False

    def resolve_frequency(self, votes: List[int]) -> int:
        """
        Conservative voting: use max(votes, min_limit).

        Plugins can REQUEST faster pulses. PRANA decides based on safety limits.

        Args:
            votes: List of requested intervals in seconds

        Returns:
            Final interval in seconds (never below min_pulse_interval_seconds)
        """
        if not votes:
            return self.config.default_interval_seconds

        requested = min(votes)
        return max(requested, self.config.min_pulse_interval_seconds)

    @property
    def quarantined_plugins(self) -> Set[str]:
        """Get set of currently quarantined plugin IDs."""
        return self._quarantined_plugins.copy()

    def _register_default_handlers(self, transaction: PulseTransaction) -> None:
        """
        Register default mutation handlers.

        These handlers actually apply the mutations to the filesystem.
        CRITICAL: Without these, mutations are recorded but never applied!
        """
        from pathlib import Path

        workspace = Path.cwd()

        def handle_update_doc(mutation: StateMutation) -> bool:
            """Write content to a markdown file."""
            target_path = workspace / mutation.target
            content = mutation.payload.get("content")

            if not content:
                logger.warning(f"update_doc: No content in payload for {mutation.target}")
                return False

            try:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(content)
                logger.info(f"✏️ PRANA: Updated {mutation.target} ({len(content)} chars)")
                return True
            except Exception as e:
                logger.error(f"update_doc failed for {mutation.target}: {e}")
                return False

        def handle_log_observation(mutation: StateMutation) -> bool:
            """Append observation to system journal."""
            journal_path = workspace / "data" / "system_journal.jsonl"

            try:
                import json
                from datetime import datetime

                journal_path.parent.mkdir(parents=True, exist_ok=True)

                entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "plugin": mutation.plugin_id,
                    "target": mutation.target,
                    **mutation.payload,
                }

                with open(journal_path, "a") as f:
                    f.write(json.dumps(entry) + "\n")

                logger.debug(f"📝 PRANA: Logged observation from {mutation.plugin_id}")
                return True
            except Exception as e:
                logger.error(f"log_observation failed: {e}")
                return False

        def handle_decay_karma(mutation: StateMutation) -> bool:
            """Apply karma decay (placeholder - implement when karma system ready)."""
            agent_id = mutation.payload.get("agent_id")
            delta = mutation.payload.get("delta", 0)
            logger.info(f"⚖️ PRANA: Karma decay for {agent_id}: {delta}")
            # TODO: Wire to actual karma system when ready
            return True

        def handle_refresh_state(mutation: StateMutation) -> bool:
            """Refresh Prakriti layer state."""
            logger.info(f"🔄 PRANA: State refresh requested for {mutation.target}")
            # Prakriti refresh is handled elsewhere - just acknowledge
            return True

        def handle_quarantine_plugin(mutation: StateMutation) -> bool:
            """Quarantine a misbehaving plugin."""
            plugin_id = mutation.payload.get("plugin_id")
            reason = mutation.payload.get("reason", "Quarantine requested via mutation")
            if plugin_id:
                self._quarantine_plugin(plugin_id, reason)
            return True

        # Register all handlers
        transaction.register_handler("update_doc", handle_update_doc)
        transaction.register_handler("log_observation", handle_log_observation)
        transaction.register_handler("decay_karma", handle_decay_karma)
        transaction.register_handler("refresh_state", handle_refresh_state)
        transaction.register_handler("quarantine_plugin", handle_quarantine_plugin)

        logger.debug("PRANA: Registered 5 default mutation handlers")

    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status."""
        return {
            "min_pulse_interval_seconds": self.config.min_pulse_interval_seconds,
            "default_interval_seconds": self.config.default_interval_seconds,
            "quarantine_threshold": self.config.quarantine_threshold,
            "quarantined_plugins": list(self._quarantined_plugins),
            "failure_counts": dict(self._failure_counts),
            "last_pulse_results": self._pulse_results,
        }


__all__ = [
    "StateMutation",
    "PulseTransaction",
    "PranaOrchestratorConfig",
    "PranaOrchestrator",
    "ALLOWED_ACTIONS",
]
