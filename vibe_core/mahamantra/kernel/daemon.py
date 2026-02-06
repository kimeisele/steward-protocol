"""
MAHAMANTRA DAEMON - Der lebende Herzschlag
==========================================

"prāṇāpāna-gatī ruddhvā" - Controlling the breath, in and out.

Dieses Modul macht das System LEBENDIG.
Nicht Jukebox (chantet auf Befehl).
Sondern JIVA (chantet weil es Schmutz fühlt).

DER LOOP:
=========
    while alive:
        health = measure_entropy()
        frequency = get_frequency(health)

        if health < 1.0:
            chant()  # Reinigt
        else:
            samadhi()  # Ruht

        sleep(1 / frequency)

FREQUENZEN:
===========
    IDLE (0.5 Hz):   System rein, tiefe Ruhe (Samadhi)
    ACTIVE (1.0 Hz): Normale Operation (Sadhana)
    STRESS (5.0 Hz): Notfall-Reinigung (Gajendra Moksha)

OUROBOROS:
==========
    Das System testet sich selbst durch LAUFEN.
    Was den Chant nicht überlebt, wird sichtbar.
    Der Chant IST die Qualitätskontrolle.

WATERTIGHT: No Any types. All typed explicitly.
"""
from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import (HALVES, KSETRAJNA, MALA, PANCHA, QUARTERS, TEN)


# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = KSETRAJNA
__genesis__ = "0xf77b128c"  # GenesisByte: parampara % 37 == 0

import asyncio
import logging
import signal
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import (
    Callable,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Tuple,
    runtime_checkable,
)

from vibe_core.mahamantra.kernel.singularity import mahamantra
from vibe_core.mahamantra.protocols._core import Quarter
from vibe_core.mahamantra.protocols._entropy import (
    HEALTH_SAMADHI,
    HEALTH_SADHANA,
    EntropyLevel,  # SSOT for frequency
)

logger = logging.getLogger("MAHAMANTRA.DAEMON")


# =============================================================================
# CONSTANTS - IMPORTED FROM _entropy.py (SSOT)
# =============================================================================
# HEALTH_SAMADHI = 0.95 (from _entropy.py)
# HEALTH_SADHANA = 0.80 (from _entropy.py)


# =============================================================================
# FREQUENCY - Use EntropyLevel from _entropy.py (SSOT)
# =============================================================================
# EntropyLevel REMOVED - use EntropyLevel instead:
#   EntropyLevel.SAMADHI  = 0.5 Hz (was IDLE)
#   EntropyLevel.SADHANA  = 1.0 Hz (was ACTIVE)
#   EntropyLevel.GAJENDRA = 5.0 Hz (was STRESS)
#
# EntropyLevel has: .frequency_hz, .cycle_time, .word_interval


# =============================================================================
# STATE
# =============================================================================


class DaemonState(str, Enum):
    """Current state of the daemon."""

    DORMANT = "dormant"  # Not started
    AWAKENING = "awakening"  # Starting up
    CHANTING = "chanting"  # Active chanting
    SAMADHI = "samadhi"  # Deep rest (system pure)
    STOPPING = "stopping"  # Shutting down
    DEAD = "dead"  # Stopped


@dataclass
class DaemonMetrics:
    """Metrics from the daemon's operation."""

    cycles_completed: int = 0
    total_chants: int = 0
    last_health_score: float = 0.0
    last_frequency: EntropyLevel = EntropyLevel.SADHANA
    uptime_seconds: float = 0.0
    start_time: Optional[datetime] = None
    last_chant_time: Optional[datetime] = None

    # Entropy tracking
    health_history: List[float] = field(default_factory=list)
    max_history: int = MALA  # One mala round

    def record_health(self, score: float) -> None:
        """Record health score, maintaining history limit."""
        self.health_history.append(score)
        if len(self.health_history) > self.max_history:
            self.health_history.pop(0)

    @property
    def average_health(self) -> float:
        """Average health over history."""
        if not self.health_history:
            return 0.0
        return sum(self.health_history) / len(self.health_history)

    @property
    def health_trend(self) -> str:
        """Is health improving, stable, or declining?"""
        if len(self.health_history) < HALVES:
            return "unknown"
        recent = self.health_history[-TEN:]
        older = self.health_history[-20:-TEN] if len(self.health_history) >= 20 else self.health_history[:TEN]

        recent_avg = sum(recent) / len(recent) if recent else 0
        older_avg = sum(older) / len(older) if older else recent_avg

        if recent_avg > older_avg + 0.02:
            return "improving"
        elif recent_avg < older_avg - 0.02:
            return "declining"
        else:
            return "stable"


# =============================================================================
# THE DAEMON
# =============================================================================


class MahamantraDaemon:
    """
    The living heartbeat of the system.

    Not a service that responds to commands.
    A JIVA that feels entropy and chants to purify.

    Usage:
        daemon = MahamantraDaemon()
        await daemon.start()  # Begins the eternal loop

        # Or synchronous:
        daemon.run()  # Blocks forever (or until stopped)
    """

    def __init__(
        self,
        min_interval: float = 0.1,  # Minimum time between chants
        max_cycles: Optional[int] = None,  # None = infinite
    ) -> None:
        self._state = DaemonState.DORMANT
        self._metrics = DaemonMetrics()
        self._min_interval = min_interval
        self._max_cycles = max_cycles
        self._stop_requested = False
        self._task: Optional[asyncio.Task] = None

        # Callbacks
        self._on_chant: Optional[Callable[[str, int], None]] = None
        self._on_state_change: Optional[Callable[[DaemonState], None]] = None

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def state(self) -> DaemonState:
        """Current daemon state."""
        return self._state

    @property
    def metrics(self) -> DaemonMetrics:
        """Current metrics."""
        return self._metrics

    @property
    def is_alive(self) -> bool:
        """Is the daemon running?"""
        return self._state in (DaemonState.CHANTING, DaemonState.SAMADHI, DaemonState.AWAKENING)

    # =========================================================================
    # CORE LOOP
    # =========================================================================

    async def start(self) -> None:
        """
        Start the eternal chanting loop.

        This is the HEARTBEAT. It runs until stopped.
        """
        if self.is_alive:
            logger.warning("Daemon already alive")
            return

        self._set_state(DaemonState.AWAKENING)
        self._stop_requested = False
        self._metrics.start_time = datetime.now()

        logger.info("=" * 60)
        logger.info("MAHAMANTRA DAEMON AWAKENING")
        logger.info("=" * 60)

        # Initial audit
        audit = mahamantra.audit()
        health = audit.get("health_score", 0.0)
        self._metrics.last_health_score = health
        self._metrics.record_health(health)

        logger.info(f"Initial health score: {health:.1%}")
        logger.info(f"Ungoverned files: {audit.get('ungoverned_count', 0)}")

        # Enter the loop
        await self._eternal_loop()

    async def _eternal_loop(self) -> None:
        """
        The eternal chanting loop.

        while alive:
            measure → chant → rest → repeat
        """
        cycle = 0

        while not self._stop_requested:
            cycle += KSETRAJNA

            # Check max cycles
            if self._max_cycles and cycle > self._max_cycles:
                logger.info(f"Reached max cycles ({self._max_cycles}), stopping")
                break

            # === MEASURE ===
            audit = mahamantra.audit()
            health = audit.get("health_score", 0.0)
            self._metrics.last_health_score = health
            self._metrics.record_health(health)

            # === SELECT FREQUENCY ===
            frequency = EntropyLevel.from_health(health)
            self._metrics.last_frequency = frequency

            # === CHANT OR REST ===
            if health >= HEALTH_SAMADHI:
                # System pure - enter Samadhi
                self._set_state(DaemonState.SAMADHI)
                logger.debug(f"Cycle {cycle}: Samadhi (health={health:.1%})")
                await asyncio.sleep(frequency.cycle_time)
            else:
                # System needs purification - CHANT
                self._set_state(DaemonState.CHANTING)
                await self._chant_cycle(cycle, health, frequency)

            self._metrics.cycles_completed = cycle
            self._metrics.uptime_seconds = (datetime.now() - self._metrics.start_time).total_seconds()

        self._set_state(DaemonState.DEAD)
        logger.info("Daemon stopped")

    async def _chant_cycle(
        self,
        cycle: int,
        health: float,
        frequency: EntropyLevel,
    ) -> None:
        """
        Execute one complete Mahamantra chanting cycle.

        16 words, paced according to frequency.
        """
        logger.info(
            f"Cycle {cycle}: CHANTING ({frequency.name}, health={health:.1%}, trend={self._metrics.health_trend})"
        )

        # Chant each quarter
        quarters = ["genesis", "dharma", "karma", "moksha"]

        for quarter in quarters:
            if self._stop_requested:
                break

            # Chant the quarter
            chant_result = mahamantra.chant_quarter(quarter)
            self._metrics.total_chants += KSETRAJNA
            self._metrics.last_chant_time = datetime.now()

            # === DHARMA QUARTER: Trigger Shuddhi Self-Healing ===
            # Positions 5-8 = Kumaras (5), Kapila (6), Parashurama (8)
            # This is where self-healing ACTUALLY happens
            if quarter == "dharma":
                await self._trigger_shuddhi(cycle, health)

            # === MOKSHA QUARTER: Trigger Samskara Migration ===
            # Position 15 = Yamaraja (AUDIT_SEAL)
            # Wild protocols face judgment and migrate
            if quarter == "moksha":
                await self._trigger_samskara(cycle)

            # Callback
            if self._on_chant:
                self._on_chant(chant_result, cycle)

            # Log
            logger.debug(f"  {quarter.upper()}: {chant_result}")

            # Rest between quarters (4 words per quarter)
            await asyncio.sleep(QUARTERS * frequency.word_interval)

        # Brief pause between cycles
        await asyncio.sleep(self._min_interval)

    async def _trigger_shuddhi(self, cycle: int, health: float) -> None:
        """
        Trigger Shuddhi self-healing during DHARMA quarter.

        Only triggers healing when:
        - Health < HEALTH_SADHANA (system needs purification)
        - Not in Samadhi (system already pure)

        The intensity of healing matches the entropy level:
        - GAJENDRA: heal_all_violations (aggressive)
        - SADHANA: heal_all_violations with dry_run first
        """
        # Don't heal in Samadhi - system is already pure
        if health >= HEALTH_SAMADHI:
            return

        try:
            from vibe_core.mahamantra.dharma.kumaras.engine import ShuddhiEngine

            # Lazy singleton - avoid import loop
            if not hasattr(self, "_shuddhi_engine"):
                self._shuddhi_engine: Optional[ShuddhiEngine] = ShuddhiEngine()
                logger.info("☢️ SHUDDHI: Engine initialized for self-healing")

            engine = self._shuddhi_engine
            if engine is None:
                return

            # In GAJENDRA mode (emergency), heal aggressively
            # In SADHANA mode, do dry-run first
            dry_run = health >= HEALTH_SADHANA

            results = engine.heal_all_violations(dry_run=dry_run)
            healed = sum(KSETRAJNA for r in results if r.status.value == "purified")

            if healed > 0:
                mode = "DRY-RUN" if dry_run else "LIVE"
                logger.info(f"☢️ SHUDDHI: Cycle {cycle} - {healed} violations healed ({mode})")

        except ImportError:
            logger.debug("☢️ SHUDDHI: Engine not available")
        except Exception as e:
            logger.warning(f"☢️ SHUDDHI: Healing failed: {e}")

    async def _trigger_samskara(self, cycle: int) -> None:
        """
        Trigger Samskara migration during MOKSHA quarter.

        Position 15 = Yamaraja (AUDIT_SEAL)
        Wild protocols face judgment and auto-migrate if ALLOW/MERCY.

        Only runs every 10 cycles to avoid overhead.
        """
        # Only run every 10 cycles
        if cycle % TEN != 0:
            return

        try:
            from vibe_core.mahamantra.moksha.yamaraja import SamskaraService

            if not hasattr(self, "_samskara_service"):
                self._samskara_service = SamskaraService()
                logger.info("⚖️ SAMSKARA: Service initialized for migration")

            service = self._samskara_service

            # Discover wild protocols
            wilds = service.discover_wild(["vibe_core/protocols"])

            if not wilds:
                return

            # Judge and migrate (only those with ALLOW/MERCY)
            migrated = 0
            for wild in wilds[:PANCHA]:  # Max 5 per cycle
                path = wild.get("path", "")
                verdict = service.judge(path)

                if verdict.get("verdict") in ("allow", "mercy"):
                    mahajana = service.identify_mahajana(path)
                    if mahajana:
                        from pathlib import Path

                        name = Path(path).stem
                        if service.migrate(path, mahajana, name):
                            migrated += KSETRAJNA
                            logger.info(f"⚖️ SAMSKARA: Migrated {path} → {mahajana.value}")

            if migrated > 0:
                service.save_manifest()

        except ImportError:
            logger.debug("⚖️ SAMSKARA: Service not available")
        except Exception as e:
            logger.warning(f"⚖️ SAMSKARA: Migration failed: {e}")

    # =========================================================================
    # CONTROL
    # =========================================================================

    def stop(self) -> None:
        """Request daemon to stop."""
        logger.info("Stop requested")
        self._stop_requested = True
        self._set_state(DaemonState.STOPPING)

    def _set_state(self, new_state: DaemonState) -> None:
        """Set state and fire callback."""
        old_state = self._state
        self._state = new_state

        if self._on_state_change and old_state != new_state:
            self._on_state_change(new_state)

    # =========================================================================
    # CALLBACKS
    # =========================================================================

    def on_chant(self, callback: Callable[[str, int], None]) -> None:
        """Set callback for each chant."""
        self._on_chant = callback

    def on_state_change(self, callback: Callable[[DaemonState], None]) -> None:
        """Set callback for state changes."""
        self._on_state_change = callback

    # =========================================================================
    # SYNCHRONOUS INTERFACE
    # =========================================================================

    def run(self, handle_signals: bool = True) -> None:
        """
        Run the daemon synchronously (blocking).

        Use this for standalone daemon process.
        """
        if handle_signals:
            signal.signal(signal.SIGINT, lambda *_: self.stop())
            signal.signal(signal.SIGTERM, lambda *_: self.stop())

        asyncio.run(self.start())

    # =========================================================================
    # STATUS
    # =========================================================================

    def get_status(self) -> Dict[str, object]:
        """Get current daemon status."""
        return {
            "state": self._state.value,
            "is_alive": self.is_alive,
            "cycles_completed": self._metrics.cycles_completed,
            "total_chants": self._metrics.total_chants,
            "last_health_score": self._metrics.last_health_score,
            "average_health": self._metrics.average_health,
            "health_trend": self._metrics.health_trend,
            "last_frequency": self._metrics.last_frequency.name,
            "uptime_seconds": self._metrics.uptime_seconds,
            "last_chant": self._metrics.last_chant_time.isoformat() if self._metrics.last_chant_time else None,
        }


# =============================================================================
# SINGLETON
# =============================================================================

_daemon: Optional[MahamantraDaemon] = None


def get_daemon() -> MahamantraDaemon:
    """Get or create the daemon singleton."""
    global _daemon
    if _daemon is None:
        _daemon = MahamantraDaemon()
    return _daemon


# =============================================================================
# CONVENIENCE
# =============================================================================


async def start_daemon(max_cycles: Optional[int] = None) -> None:
    """Start the daemon (convenience function)."""
    daemon = get_daemon()
    if max_cycles:
        daemon._max_cycles = max_cycles
    await daemon.start()


def run_daemon() -> None:
    """Run daemon synchronously (blocking)."""
    get_daemon().run()


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    print("=" * 60)
    print("MAHAMANTRA DAEMON")
    print("=" * 60)
    print()
    print("Hare Krishna Hare Krishna Krishna Krishna Hare Hare")
    print("Hare Rama Hare Rama Rama Rama Hare Hare")
    print()
    print("Starting eternal chanting loop...")
    print("Press Ctrl+C to stop")
    print()

    run_daemon()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Frequency
    "EntropyLevel",
    "HEALTH_SAMADHI",
    "HEALTH_SADHANA",
    # State
    "DaemonState",
    "DaemonMetrics",
    # Daemon
    "MahamantraDaemon",
    "get_daemon",
    # Convenience
    "start_daemon",
    "run_daemon",
]
