"""
Runtime Configuration - Timeouts, intervals, limits.

VEDA-4 Pattern:
    SHABDA: Auto-discovered from vibe_core/phoenix/sections/runtime/
    ARTHA: Parsed from config/runtime.yaml
    PRATYAYA: Validated
    KARMA: Instantiated as RuntimeConfig dataclass
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xf2c72b19"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class TimeoutsConfig:
    """Timeout configuration."""

    operator_timeout: float = 300.0
    action_timeout: int = 300
    test_timeout_ms: int = 5000
    ritual_interval: float = 300.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimeoutsConfig":
        return cls(
            operator_timeout=data.get("operator_timeout", 300.0),
            action_timeout=data.get("action_timeout", 300),
            test_timeout_ms=data.get("test_timeout_ms", 5000),
            ritual_interval=data.get("ritual_interval", 300.0),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operator_timeout": self.operator_timeout,
            "action_timeout": self.action_timeout,
            "test_timeout_ms": self.test_timeout_ms,
            "ritual_interval": self.ritual_interval,
        }


@dataclass
class LimitsConfig:
    """System limits configuration."""

    max_recursion_depth: int = 5
    max_circuit_transitions: int = 20
    max_message_size: int = 1048576  # 1MB
    max_agent_restarts: int = 3
    event_history_size: int = 1000
    pulse_threshold: float = 10.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LimitsConfig":
        return cls(
            max_recursion_depth=data.get("max_recursion_depth", 5),
            max_circuit_transitions=data.get("max_circuit_transitions", 20),
            max_message_size=data.get("max_message_size", 1048576),
            max_agent_restarts=data.get("max_agent_restarts", 3),
            event_history_size=data.get("event_history_size", 1000),
            pulse_threshold=data.get("pulse_threshold", 10.0),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_recursion_depth": self.max_recursion_depth,
            "max_circuit_transitions": self.max_circuit_transitions,
            "max_message_size": self.max_message_size,
            "max_agent_restarts": self.max_agent_restarts,
            "event_history_size": self.event_history_size,
            "pulse_threshold": self.pulse_threshold,
        }


@dataclass
class CircuitRecoveryConfig:
    """Circuit recovery configuration."""

    reflection_interval: int = 3
    stuck_threshold: int = 3
    max_retry_attempts: int = 5

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CircuitRecoveryConfig":
        return cls(
            reflection_interval=data.get("reflection_interval", 3),
            stuck_threshold=data.get("stuck_threshold", 3),
            max_retry_attempts=data.get("max_retry_attempts", 5),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reflection_interval": self.reflection_interval,
            "stuck_threshold": self.stuck_threshold,
            "max_retry_attempts": self.max_retry_attempts,
        }


@dataclass
class ActionDefaultsConfig:
    """Default action configuration."""

    retry_count: int = 3

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActionDefaultsConfig":
        return cls(
            retry_count=data.get("retry_count", 3),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "retry_count": self.retry_count,
        }


@dataclass
class OrchestrationConfig:
    """Kernel tick/process coordination configuration."""

    health_check_interval: float = 2.0  # vibe_launcher supervisor loop
    discovery_interval: float = 60.0  # Discoverer cartridge scan interval
    pulse_sleep: float = 1.0  # Pulse async sleep between updates
    file_poll_interval: float = 2.0  # FileOperator polling delay
    monitoring_interval: float = 10.0  # Gateway monitoring start interval
    heartbeat_max_tasks_per_pulse: int = 5  # Max tasks per heartbeat cycle
    heartbeat_commit_changes: bool = True  # Auto-commit task progress

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrchestrationConfig":
        return cls(
            health_check_interval=data.get("health_check_interval", 2.0),
            discovery_interval=data.get("discovery_interval", 60.0),
            pulse_sleep=data.get("pulse_sleep", 1.0),
            file_poll_interval=data.get("file_poll_interval", 2.0),
            monitoring_interval=data.get("monitoring_interval", 10.0),
            heartbeat_max_tasks_per_pulse=data.get("heartbeat_max_tasks_per_pulse", 5),
            heartbeat_commit_changes=data.get("heartbeat_commit_changes", True),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "health_check_interval": self.health_check_interval,
            "discovery_interval": self.discovery_interval,
            "pulse_sleep": self.pulse_sleep,
            "file_poll_interval": self.file_poll_interval,
            "monitoring_interval": self.monitoring_interval,
            "heartbeat_max_tasks_per_pulse": self.heartbeat_max_tasks_per_pulse,
            "heartbeat_commit_changes": self.heartbeat_commit_changes,
        }


@dataclass
class RuntimeConfig:
    """
    Runtime Configuration.

    Auto-discovered by SectionLoader -> loads from config/runtime.yaml
    """

    section_id: str = "runtime"
    source_file: str = "runtime.yaml"

    timeouts: TimeoutsConfig = field(default_factory=TimeoutsConfig)
    limits: LimitsConfig = field(default_factory=LimitsConfig)
    circuit_recovery: CircuitRecoveryConfig = field(default_factory=CircuitRecoveryConfig)
    action_defaults: ActionDefaultsConfig = field(default_factory=ActionDefaultsConfig)
    orchestration: OrchestrationConfig = field(default_factory=OrchestrationConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RuntimeConfig":
        return cls(
            timeouts=TimeoutsConfig.from_dict(data.get("timeouts", {})),
            limits=LimitsConfig.from_dict(data.get("limits", {})),
            circuit_recovery=CircuitRecoveryConfig.from_dict(data.get("circuit_recovery", {})),
            action_defaults=ActionDefaultsConfig.from_dict(data.get("action_defaults", {})),
            orchestration=OrchestrationConfig.from_dict(data.get("orchestration", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timeouts": self.timeouts.to_dict(),
            "limits": self.limits.to_dict(),
            "circuit_recovery": self.circuit_recovery.to_dict(),
            "action_defaults": self.action_defaults.to_dict(),
            "orchestration": self.orchestration.to_dict(),
        }

    def validate(self) -> List[str]:
        errors = []
        if self.limits.max_recursion_depth < 1:
            errors.append("limits.max_recursion_depth must be >= 1")
        if self.limits.max_message_size < 1024:
            errors.append("limits.max_message_size must be >= 1024")
        return errors
