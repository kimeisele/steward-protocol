"""
OPUS-174: NadiSense - Wiring Health Awareness

Sanskrit: नाडी (Nadi) = Energy channel, nerve, subtle pathway

In Vedic philosophy, Nadis are the channels through which prana (life force)
flows. When a Nadi is blocked, energy cannot flow and illness results.

This sense monitors the "Nadis" of the system - the EventBus wiring.
It detects:
1. Dead letter events (subscribed but never received)
2. Phantom emitters (events emitted with no subscribers)
3. Stale state files (> threshold age)
4. Broken wiring patterns

"When the channels are blocked, the system cannot breathe.
 NadiSense detects the blockages before the system dies."

GAD-000 Compliance:
- OBSERVABILITY: Makes EventBus health visible
- DISCOVERABILITY: Surfaces broken wiring that was previously silent

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/nadi_sense.py
    required: true
    rationale: "Wiring health detection for MANAS"
  - path: vibe_core/event_bus.py
    required: true
    rationale: "EventBus provides subscription/emission data"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/base.py
    required: true
    rationale: "Base class for all senses"

wiring:
  - pattern: "class NadiSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/nadi_sense.py
  - pattern: "class NadiPerception"
    in: vibe_core/plugins/opus_assistant/manas/cortex/nadi_sense.py
  - pattern: "def perceive"
    in: vibe_core/plugins/opus_assistant/manas/cortex/nadi_sense.py
  - pattern: "def generate_intents"
    in: vibe_core/plugins/opus_assistant/manas/cortex/nadi_sense.py

tests:
  - tests/manas/cortex/test_nadi_sense.py
  - tests/integration/test_wiring_health.py
-->
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# OPUS-167: Intent imports for generate_intents()
from vibe_core.plugins.opus_assistant.manas.intent_generator import (
    Intent,
    IntentPriority,
    IntentRisk,
)

from .base import BaseSense

logger = logging.getLogger("MANAS.Cortex.NadiSense")


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class WiringAnomaly:
    """A detected wiring anomaly."""

    anomaly_type: str  # "dead_letter", "phantom_emitter", "stale_state", "never_emitted"
    event_type: str  # The event type involved
    severity: str  # "critical", "warning", "info"
    message: str  # Human-readable description
    subscribers: int = 0  # Number of subscribers
    emissions: int = 0  # Number of emissions
    last_emission: Optional[str] = None  # Timestamp of last emission
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StaleStateFile:
    """A detected stale state file."""

    path: str
    last_modified: str
    age_hours: float
    expected_max_age_hours: float


@dataclass
class NadiPerception:
    """Result of NadiSense perception."""

    # EventBus health
    total_event_types_subscribed: int
    total_event_types_emitted: int
    total_emissions: int

    # Anomalies
    anomalies: List[WiringAnomaly]
    critical_count: int
    warning_count: int

    # Stale state
    stale_files: List[StaleStateFile]

    # Health score (0-100)
    health_score: int

    # Timestamp
    timestamp: str

    def is_healthy(self) -> bool:
        """Check if wiring is healthy."""
        return self.critical_count == 0


# =============================================================================
# Expected Wiring Configuration
# =============================================================================

# Events that SHOULD be emitted regularly
EXPECTED_EMISSIONS = {
    "KERNEL_TICK": {
        "max_age_seconds": 120,  # Should emit every 60s at least
        "critical_if_missing": True,
        "description": "Kernel heartbeat - triggers MANAS and circuits",
    },
    "KERNEL_BOOT": {
        "max_age_seconds": None,  # Only on boot
        "critical_if_missing": False,
        "description": "Kernel boot event",
    },
}

# State files that should not be stale
EXPECTED_STATE_FILES = {
    ".opus_state/manas_intents.json": {
        "max_age_hours": 2,  # Should update at least every 2 hours if MANAS is running
        "description": "MANAS intent buffer",
    },
    ".opus_state/prakriti.json": {
        "max_age_hours": 1,  # Should update every hour
        "description": "Prakriti state (3 layers)",
    },
    "vibe_snapshot.json": {
        "max_age_hours": 0.5,  # Should update every 30 min
        "description": "Kernel pulse snapshot",
    },
}


# =============================================================================
# NadiSense Implementation
# =============================================================================


class NadiSense(BaseSense):
    """
    Wiring Health Awareness - The Nadi Inspector.

    Monitors the EventBus "channels" to detect:
    1. Dead letter events - subscribed but never received
    2. Phantom emitters - emitted but no subscribers
    3. Critical missing events - expected but never seen
    4. Stale state files - system not updating

    Philosophy:
    - Nadis are the subtle channels in the body
    - When blocked, prana cannot flow
    - NadiSense detects blocked channels in the system
    - Prevention > Cure: Find blockages before failure

    GAD-000:
    - This sense exists because KERNEL_TICK failing silently
      for 3 days is a GAD-000 OBSERVABILITY violation
    - Never again should wiring fail without detection
    """

    name = "nadi_sense"

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(workspace, config)

        # Reference to EventBus (injected on first perceive)
        self._event_bus = None

        # Track what we've seen
        self._last_perception: Optional[NadiPerception] = None

        logger.info("[NADI_SENSE] Initialized - Watching the channels")

    def _get_event_bus(self):
        """Get reference to the global EventBus."""
        if self._event_bus is None:
            try:
                # OPUS-175: Use get_event_bus() instead of kernel import
                from vibe_core.event_bus import get_event_bus

                self._event_bus = get_event_bus()
            except Exception:
                pass

        return self._event_bus

    def perceive(self, context: Optional[Dict[str, Any]] = None) -> NadiPerception:
        """
        Perceive the current wiring health.

        Checks:
        1. EventBus subscriptions vs emissions
        2. Expected events that are missing
        3. Stale state files

        Returns:
            NadiPerception with detected anomalies
        """
        anomalies: List[WiringAnomaly] = []
        stale_files: List[StaleStateFile] = []

        bus = self._get_event_bus()

        total_subscribed = 0
        total_emitted_types = 0
        total_emissions = 0

        # =================================================================
        # 1. Check EventBus State
        # =================================================================
        if bus:
            status = bus.get_status()
            subscriptions = status["subscribers"]["by_type"]
            type_counts = status.get("type_counts", {})
            total_emissions = status["total_events"]

            total_subscribed = len(subscriptions)

            # Count emitted event types
            emitted_types = set(type_counts.keys())
            total_emitted_types = len(emitted_types)

            # ---------------------------------------------------------
            # Check for dead letter events (subscribed but never received)
            # ---------------------------------------------------------
            for event_type, subs_count in subscriptions.items():
                if event_type not in emitted_types and subs_count > 0:
                    # This event type has subscribers but no emissions!
                    expected = EXPECTED_EMISSIONS.get(event_type, {})
                    is_critical = expected.get("critical_if_missing", False)

                    anomalies.append(
                        WiringAnomaly(
                            anomaly_type="dead_letter",
                            event_type=event_type,
                            severity="critical" if is_critical else "warning",
                            message=f"{event_type} has {subs_count} subscribers but 0 emissions",
                            subscribers=subs_count,
                            emissions=0,
                            details={
                                "expected_description": expected.get("description", "Unknown"),
                            },
                        )
                    )

            # ---------------------------------------------------------
            # Check expected emissions that are missing
            # ---------------------------------------------------------
            for event_type, config in EXPECTED_EMISSIONS.items():
                if event_type not in emitted_types:
                    if config.get("critical_if_missing", False):
                        anomalies.append(
                            WiringAnomaly(
                                anomaly_type="never_emitted",
                                event_type=event_type,
                                severity="critical",
                                message=f"CRITICAL: {event_type} expected but NEVER emitted!",
                                subscribers=subscriptions.get(event_type, 0),
                                emissions=0,
                                details={
                                    "description": config.get("description", ""),
                                    "max_age_seconds": config.get("max_age_seconds"),
                                },
                            )
                        )
        else:
            # No EventBus accessible - that's a critical anomaly
            anomalies.append(
                WiringAnomaly(
                    anomaly_type="no_bus",
                    event_type="*",
                    severity="critical",
                    message="EventBus not accessible - cannot monitor wiring health",
                    details={},
                )
            )

        # =================================================================
        # 2. Check Stale State Files
        # =================================================================
        for file_path, config in EXPECTED_STATE_FILES.items():
            full_path = self._workspace / file_path
            if full_path.exists():
                try:
                    mtime = full_path.stat().st_mtime
                    age_hours = (datetime.now().timestamp() - mtime) / 3600
                    max_age = config["max_age_hours"]

                    if age_hours > max_age:
                        stale_files.append(
                            StaleStateFile(
                                path=file_path,
                                last_modified=datetime.fromtimestamp(mtime).isoformat(),
                                age_hours=round(age_hours, 2),
                                expected_max_age_hours=max_age,
                            )
                        )

                        anomalies.append(
                            WiringAnomaly(
                                anomaly_type="stale_state",
                                event_type="STATE_FILE",
                                severity="warning",
                                message=f"Stale: {file_path} is {age_hours:.1f}h old (max: {max_age}h)",
                                details={
                                    "path": file_path,
                                    "age_hours": age_hours,
                                    "description": config.get("description", ""),
                                },
                            )
                        )
                except Exception as e:
                    logger.warning(f"[NADI_SENSE] Could not check {file_path}: {e}")

        # =================================================================
        # 3. Calculate Health Score
        # =================================================================
        critical_count = sum(1 for a in anomalies if a.severity == "critical")
        warning_count = sum(1 for a in anomalies if a.severity == "warning")

        # Health score: 100 - (critical * 30) - (warning * 10)
        health_score = max(0, 100 - (critical_count * 30) - (warning_count * 10))

        # =================================================================
        # 4. Build Perception
        # =================================================================
        perception = NadiPerception(
            total_event_types_subscribed=total_subscribed,
            total_event_types_emitted=total_emitted_types,
            total_emissions=total_emissions,
            anomalies=anomalies,
            critical_count=critical_count,
            warning_count=warning_count,
            stale_files=stale_files,
            health_score=health_score,
            timestamp=datetime.utcnow().isoformat(),
        )

        self._last_perception = perception

        # Log summary
        if critical_count > 0:
            logger.error(f"[NADI_SENSE] 🔴 CRITICAL: {critical_count} wiring failures detected!")
        elif warning_count > 0:
            logger.warning(f"[NADI_SENSE] 🟡 WARNING: {warning_count} wiring issues detected")
        else:
            logger.debug(f"[NADI_SENSE] 🟢 Wiring health: {health_score}%")

        return perception

    def generate_intents(self, context: Optional[Dict[str, Any]] = None) -> List[Intent]:
        """
        Generate intents for detected wiring anomalies.

        OPUS-167: Senses generate their own intents.
        """
        intents: List[Intent] = []

        # Get fresh perception
        perception = self.perceive(context)

        # Generate intent for each critical anomaly
        for anomaly in perception.anomalies:
            if anomaly.severity == "critical":
                intent = Intent(
                    id=f"nadi_{anomaly.anomaly_type}_{anomaly.event_type.lower()}",
                    intent_type="wiring_repair",
                    title=f"🔴 Broken Wiring: {anomaly.event_type}",
                    description=anomaly.message,
                    reasoning=(
                        f"NadiSense detected a critical wiring failure. "
                        f"Type: {anomaly.anomaly_type}. "
                        f"This violates GAD-000 Observability principle."
                    ),
                    priority=IntentPriority.CRITICAL,
                    risk=IntentRisk.MEDIUM,
                    related_files=["vibe_core/event_bus.py", "vibe_core/kernel_impl.py"],
                    related_docs=["docs/architecture/GAD-0XX/GAD-000.md"],
                    params={
                        "anomaly_type": anomaly.anomaly_type,
                        "event_type": anomaly.event_type,
                        "details": anomaly.details,
                    },
                )
                intents.append(intent)

        # Generate intent for stale MANAS intents specifically
        for stale in perception.stale_files:
            if "manas_intents" in stale.path:
                intent = Intent(
                    id="nadi_manas_stale",
                    intent_type="manas_health",
                    title=f"🟡 MANAS not ticking: intents {stale.age_hours:.1f}h stale",
                    description=(
                        f"manas_intents.json has not been updated for {stale.age_hours:.1f} hours. "
                        f"Expected max age: {stale.expected_max_age_hours}h. "
                        f"MANAS cognitive loop may be broken."
                    ),
                    reasoning=(
                        "If MANAS is running, it should update intents regularly. "
                        "Stale intents indicate MANAS tick() is not being called."
                    ),
                    priority=IntentPriority.HIGH,
                    risk=IntentRisk.LOW,
                    related_files=[".opus_state/manas_intents.json"],
                    related_docs=["docs/architecture/OPUS/108-AUTONOMY-LOOP.md"],
                    params={
                        "age_hours": stale.age_hours,
                        "path": stale.path,
                    },
                )
                intents.append(intent)

        return intents

    def get_boot_summary(self) -> Dict[str, Any]:
        """
        Get standardized boot summary for SenseManager.

        OPUS-172: Polymorphic Boot Summary.
        """
        perception = self.perceive()

        status_emoji = "🟢" if perception.is_healthy() else "🔴"
        status_text = (
            f"{status_emoji} Wiring Health: {perception.health_score}% | "
            f"{perception.critical_count} critical, {perception.warning_count} warnings"
        )

        return {
            "message": status_text,
            "data": {
                "health_score": perception.health_score,
                "critical_count": perception.critical_count,
                "warning_count": perception.warning_count,
                "anomalies": [
                    {"type": a.anomaly_type, "event": a.event_type, "severity": a.severity}
                    for a in perception.anomalies[:5]  # Top 5
                ],
            },
            "emoji": status_emoji,
        }

    def get_critical_anomalies(self) -> List[WiringAnomaly]:
        """Get only critical anomalies."""
        if self._last_perception:
            return [a for a in self._last_perception.anomalies if a.severity == "critical"]
        return []

    def check_event_wiring(self, event_type: str) -> Dict[str, Any]:
        """
        Check wiring health for a specific event type.

        Args:
            event_type: Event type to check (e.g., "KERNEL_TICK")

        Returns:
            Dict with wiring status
        """
        bus = self._get_event_bus()
        if not bus:
            return {"error": "EventBus not accessible"}

        status = bus.get_status()
        type_counts = status.get("type_counts", {})
        subscriptions = status["subscribers"]["by_type"]
        history = bus.get_history()

        # Count emissions of this type
        emission_count = type_counts.get(event_type, 0)
        subscribers_count = subscriptions.get(event_type, 0)

        # Last emission from history (if still there)
        emissions_in_history = [e for e in history if getattr(e, "event_type", "") == event_type]

        return {
            "event_type": event_type,
            "subscriber_count": subscribers_count,
            "emission_count": emission_count,
            "last_emission": emissions_in_history[-1].timestamp if emissions_in_history else None,
            "is_wired": subscribers_count > 0 and emission_count > 0,
            "status": (
                "healthy" if emission_count > 0 else "dead_letter" if subscribers_count > 0 else "not_subscribed"
            ),
        }


# =============================================================================
# Module-Level Export
# =============================================================================

__all__ = [
    "NadiSense",
    "NadiPerception",
    "WiringAnomaly",
    "StaleStateFile",
]
