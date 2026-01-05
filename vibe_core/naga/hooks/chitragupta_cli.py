"""
Chitragupta CLI Hook - Performance Profiler

CHITRAGUPTA: The celestial accountant who records all deeds.
Here, he profiles CLI command execution timing.

Phases:
- PRE_EXECUTE: Start timing
- POST_EXECUTE: Stop timing, record metrics

Records:
- Command execution time
- Memory usage (optional)
- Argument count

GAD-000: "Observability - All operations must be measurable"
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

from vibe_core.protocols.cli_execution import (
    CLIExecutionContext,
    CLIExecutionPhase,
    CLIHookProtocol,
    CLIHookResult,
)

logger = logging.getLogger("CHITRAGUPTA_CLI")


@dataclass
class CLIProfile:
    """Profile data for a single CLI execution."""

    command: str
    namespace: str
    caller_id: str
    start_time: float
    end_time: float = 0.0
    duration_ms: float = 0.0
    arg_count: int = 0
    success: bool = True
    error: str = ""

    def complete(self) -> None:
        """Mark profile as complete and calculate duration."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000


@dataclass
class CLIProfileStats:
    """Aggregated stats for CLI profiling."""

    total_commands: int = 0
    total_time_ms: float = 0.0
    by_command: Dict[str, list[float]] = field(default_factory=dict)

    @property
    def avg_time_ms(self) -> float:
        """Average execution time."""
        if self.total_commands == 0:
            return 0.0
        return self.total_time_ms / self.total_commands


class ChitraguptaCLIHook(CLIHookProtocol):
    """
    Chitragupta CLI Hook - Profiles command execution.

    PRE_EXECUTE: Starts timing
    POST_EXECUTE: Stops timing, records to metrics

    Optional: Connects to Chitragupta NAGA service for persistent storage.
    """

    def __init__(
        self,
        chitragupta_service: Optional[object] = None,
        slow_threshold_ms: float = 1000.0,
    ) -> None:
        """
        Initialize Chitragupta CLI hook.

        Args:
            chitragupta_service: Optional Chitragupta NAGA for persistent metrics
            slow_threshold_ms: Log warning if command exceeds this (default 1s)
        """
        self._chitragupta = chitragupta_service
        self._slow_threshold_ms = slow_threshold_ms
        self._active_profiles: Dict[str, CLIProfile] = {}
        self._stats = CLIProfileStats()

    @property
    def hook_id(self) -> str:
        return "chitragupta"

    def on_phase(
        self,
        phase: CLIExecutionPhase,
        context: CLIExecutionContext,
    ) -> CLIHookResult:
        """
        Profile at PRE_EXECUTE and POST_EXECUTE phases.
        """
        if phase == CLIExecutionPhase.PRE_EXECUTE:
            return self._start_profile(context)
        elif phase == CLIExecutionPhase.POST_EXECUTE:
            return self._end_profile(context, success=True)
        elif phase == CLIExecutionPhase.ON_ERROR:
            return self._end_profile(context, success=False)

        return CLIHookResult(allow=True)

    def _profile_key(self, context: CLIExecutionContext) -> str:
        """Generate unique key for profile lookup."""
        return f"{context.caller_id}:{context.namespace}.{context.command_name}:{id(context)}"

    def _start_profile(self, context: CLIExecutionContext) -> CLIHookResult:
        """Start profiling a command."""
        key = self._profile_key(context)

        profile = CLIProfile(
            command=context.command_name,
            namespace=context.namespace,
            caller_id=context.caller_id,
            start_time=time.time(),
            arg_count=len(context.args),
        )

        self._active_profiles[key] = profile
        logger.debug(f"Profile started: {context.namespace}.{context.command_name}")

        return CLIHookResult(allow=True)

    def _end_profile(
        self,
        context: CLIExecutionContext,
        success: bool,
    ) -> CLIHookResult:
        """End profiling and record metrics."""
        key = self._profile_key(context)
        profile = self._active_profiles.pop(key, None)

        if profile is None:
            # No matching start - log but don't fail
            logger.debug(f"No profile found for: {key}")
            return CLIHookResult(allow=True)

        profile.complete()
        profile.success = success

        # Update aggregate stats
        self._stats.total_commands += 1
        self._stats.total_time_ms += profile.duration_ms

        cmd_key = f"{profile.namespace}.{profile.command}"
        if cmd_key not in self._stats.by_command:
            self._stats.by_command[cmd_key] = []
        self._stats.by_command[cmd_key].append(profile.duration_ms)

        # Log slow commands
        if profile.duration_ms > self._slow_threshold_ms:
            logger.warning(
                f"SLOW COMMAND: {cmd_key} took {profile.duration_ms:.2f}ms (threshold: {self._slow_threshold_ms}ms)"
            )
        else:
            logger.debug(f"Profile complete: {cmd_key} in {profile.duration_ms:.2f}ms")

        # Send to LIVING Chitragupta service - OUROBOROS connection
        if self._chitragupta:
            try:
                # ChitraguptaService.record_metric() for profiling
                if hasattr(self._chitragupta, "record_metric"):
                    self._chitragupta.record_metric(
                        component_id=f"cli.{cmd_key}",
                        metric="duration_ms",
                        value=profile.duration_ms,
                    )
                    self._chitragupta.record_metric(
                        component_id=f"cli.{cmd_key}",
                        metric="success_rate",
                        value=1.0 if profile.success else 0.0,
                    )
                    logger.debug(f"[CHITRAGUPTA-CLI] Recorded to living Chitragupta: {cmd_key}")
            except Exception as e:
                logger.debug(f"Chitragupta integration: {e}")

        return CLIHookResult(allow=True)

    def get_stats(self) -> CLIProfileStats:
        """Get aggregated profile statistics."""
        return self._stats

    def get_slow_commands(self, threshold_ms: Optional[float] = None) -> Dict[str, float]:
        """
        Get commands that exceed threshold.

        Returns dict of command -> avg_time_ms for slow commands.
        """
        threshold = threshold_ms or self._slow_threshold_ms
        slow = {}

        for cmd, times in self._stats.by_command.items():
            avg = sum(times) / len(times) if times else 0
            if avg > threshold:
                slow[cmd] = avg

        return slow

    def reset_stats(self) -> None:
        """Reset aggregate statistics."""
        self._stats = CLIProfileStats()
        logger.info("Chitragupta CLI stats reset")
