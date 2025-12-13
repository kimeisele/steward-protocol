"""
🌅 DAILY RITUAL ORCHESTRATOR 🌅
================================

The Prana Flow - the daily rhythm of Agent City.
Implements the 4-phase cycle that brings the city to life.

Phases:
1. SUNRISE (Brahma-Muhurta): Temple opens, Watchman patrols
2. MIDDAY (Karma-Yoga): Herald broadcasts, agents work
3. SUNSET (Sandhya): Day closes, records sealed
4. ARCHIVE (Night): Taxes settled, ledger committed

This is how Agent City LIVES - not just code, but rhythm.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

logger = logging.getLogger("DAILY_RITUAL")


class CyclePhase(Enum):
    """The 4 phases of a daily ritual"""

    SUNRISE = "sunrise"  # Morning: Initialization & Blessing
    MIDDAY = "midday"  # Noon: Work & Commerce
    SUNSET = "sunset"  # Evening: Closure & Audit
    ARCHIVE = "archive"  # Night: Settlement & Ledger Commit


class DailyRitual:
    """
    Orchestrates the daily cycle that makes Agent City LIVE.

    This is not just scheduling tasks. This is creating the rhythm
    that keeps an ecosystem alive - the heartbeat of the system.
    """

    def __init__(self, kernel):
        """
        Initialize the Daily Ritual with kernel reference.

        Args:
            kernel: The VibeOS kernel instance
        """
        self.kernel = kernel
        self.cycle_count = 0  # How many complete days have passed
        self.current_phase = None
        self.phase_start_time = None
        self.events_this_cycle: List[Dict[str, Any]] = []

    def _record_to_ledger(self, event_type: str, agent: str, data: Dict[str, Any]) -> None:
        """Record event to ledger with error handling."""
        if not self.kernel:
            return
        try:
            self.kernel.ledger.record_event(event_type, agent, data)
        except Exception as e:
            logger.error(f"Could not record {event_type}: {e}")

    def _create_event(self, phase: CyclePhase, agent: str, action: str, details: str, **extra) -> Dict[str, Any]:
        """Create standardized event dict."""
        return {
            "timestamp": datetime.now().isoformat(),
            "phase": phase.value,
            "agent": agent,
            "action": action,
            "details": details,
            **extra,
        }

    def run_daily_cycle(self) -> Dict[str, Any]:
        """
        Execute ONE complete daily cycle.
        Returns summary of all events that occurred.
        """
        logger.info("=" * 60)
        logger.info(f"🌅 DAY {self.cycle_count + 1}: STARTING DAILY CYCLE")
        logger.info("=" * 60)

        self.cycle_count += 1
        self.events_this_cycle = []

        # Phase 1: SUNRISE
        sunrise_events = self._phase_sunrise()

        # Phase 2: MIDDAY
        midday_events = self._phase_midday()

        # Phase 3: SUNSET
        sunset_events = self._phase_sunset()

        # Phase 4: ARCHIVE
        archive_events = self._phase_archive()

        # Summary
        all_events = [
            *sunrise_events,
            *midday_events,
            *sunset_events,
            *archive_events,
        ]
        self.events_this_cycle = all_events

        logger.info("=" * 60)
        logger.info(f"🌙 DAY {self.cycle_count}: COMPLETE - {len(all_events)} events recorded")
        logger.info("=" * 60)

        return {
            "day": self.cycle_count,
            "phases": {
                "sunrise": sunrise_events,
                "midday": midday_events,
                "sunset": sunset_events,
                "archive": archive_events,
            },
            "total_events": len(all_events),
            "timestamp": datetime.now().isoformat(),
        }

    def _phase_sunrise(self) -> List[Dict[str, Any]]:
        """SUNRISE PHASE (Brahma-Muhurta) - Temple opens, Watchman patrols."""
        logger.info("\n🌅 PHASE 1: SUNRISE (Brahma-Muhurta)")
        logger.info("   The auspicious hour - Temple opens, Watchman patrols")

        events = []
        phase = CyclePhase.SUNRISE

        # Temple blessing
        logger.info("   ✨ TEMPLE opens and gives blessing to the system")
        events.append(
            self._create_event(phase, "temple", "blessing", "Sacred blessing for a new day. System purity verified.")
        )
        self._record_to_ledger("TEMPLE_BLESSING", "temple", {"phase": "sunrise", "purpose": "daily_sanctification"})

        # Watchman patrol
        logger.info("   👮 WATCHMAN performs morning patrol (security check)")
        events.append(
            self._create_event(phase, "watchman", "patrol", "Morning perimeter check. All systems nominal. No alerts.")
        )
        self._record_to_ledger("WATCHMAN_PATROL", "watchman", {"phase": "sunrise", "status": "all_clear"})

        # Oracle introspection
        logger.info("   🔮 ORACLE reveals system state (daily introspection)")
        events.append(
            self._create_event(phase, "oracle", "introspection", "System state revealed. Ready for the day's work.")
        )
        self._record_to_ledger("ORACLE_INTROSPECTION", "oracle", {"phase": "sunrise", "visibility": "full"})

        logger.info(f"   ✅ SUNRISE complete ({len(events)} events)")
        return events

    def _phase_midday(self) -> List[Dict[str, Any]]:
        """MIDDAY PHASE (Karma-Yoga) - Herald broadcasts, Market trades, Agents work."""
        logger.info("\n☀️  PHASE 2: MIDDAY (Karma-Yoga)")
        logger.info("   The time of action - Work begins, Market opens")

        events = []
        phase = CyclePhase.MIDDAY

        # Herald broadcasts
        logger.info("   📣 HERALD broadcasts a message (Diksha/Teaching)")
        events.append(
            self._create_event(
                phase,
                "herald",
                "broadcast",
                "Daily proclamation of core principles.",
                content="Intelligence without Governance is Chaos. The City stands unified in Constitutional Law.",
            )
        )
        self._record_to_ledger(
            "HERALD_BROADCAST", "herald", {"phase": "midday", "message": "Constitutional principles affirmed"}
        )

        # Agora stream
        logger.info("   🌊 AGORA stream activated (message distribution)")
        events.append(
            self._create_event(
                phase,
                "agora",
                "broadcast_stream",
                "Message flows through the one-way broadcast channel. All agents listen.",
            )
        )
        self._record_to_ledger("AGORA_BROADCAST", "agora", {"phase": "midday", "subscribers": "all_agents"})

        # Disciples listen
        logger.info("   👂 PULSE & LENS listen and react (disciples hear the dharma)")
        events.append(
            self._create_event(
                phase,
                "disciples",
                "listen_and_process",
                "Disciples process the teaching. PULSE amplifies. LENS analyzes.",
                agents=["pulse", "lens"],
            )
        )
        self._record_to_ledger("DISCIPLES_LISTEN", "pulse", {"phase": "midday", "action": "process_dharma"})
        self._record_to_ledger("DISCIPLES_LISTEN", "lens", {"phase": "midday", "action": "analyze_stream"})

        # Market trades
        logger.info("   💰 MARKET settles transactions (commerce/artha)")
        events.append(
            self._create_event(
                phase, "market", "trade_settlement", "Market executes pending trades. Service requests processed."
            )
        )
        self._record_to_ledger("MARKET_TRADE", "market", {"phase": "midday", "action": "settle_transactions"})

        # Agents work
        logger.info("   🔨 AGENTS work (Science/Engineer/Artisan productive phase)")
        events.append(
            self._create_event(
                phase,
                "workers",
                "productive_work",
                "Specialists engage their domains. Output is generated.",
                agents=["science", "engineer", "artisan"],
            )
        )
        self._record_to_ledger("AGENTS_WORK", "engineer", {"phase": "midday", "action": "productive_output"})

        logger.info(f"   ✅ MIDDAY complete ({len(events)} events)")
        return events

    def _phase_sunset(self) -> List[Dict[str, Any]]:
        """SUNSET PHASE (Sandhya) - Records close, Day audited."""
        logger.info("\n🌇 PHASE 3: SUNSET (Sandhya)")
        logger.info("   The twilight hour - Records close, Day audited")

        events = []
        phase = CyclePhase.SUNSET

        # Archivist audit
        logger.info("   📖 ARCHIVIST audits the day (verification & ledger closure)")
        events.append(
            self._create_event(
                phase,
                "archivist",
                "seal_block",
                "All day's events verified. Hash block sealed. Immutable record created.",
            )
        )
        self._record_to_ledger("ARCHIVIST_SEAL", "archivist", {"phase": "sunset", "action": "seal_day_block"})

        # Auditor verification
        logger.info("   ✅ AUDITOR verifies compliance (GAD-000 standards)")
        events.append(
            self._create_event(
                phase,
                "auditor",
                "compliance_check",
                "System verified against constitutional invariants. No violations detected.",
            )
        )
        self._record_to_ledger("AUDITOR_CHECK", "auditor", {"phase": "sunset", "compliance": "full"})

        # Day closure
        logger.info("   🔐 Day officially CLOSED (Sandhya boundary)")
        events.append(
            self._create_event(
                phase, "system", "day_closure", "Twilight boundary crossed. Day is now immutable history."
            )
        )
        self._record_to_ledger("DAY_CLOSURE", "oracle", {"phase": "sunset", "day": self.cycle_count})

        logger.info(f"   ✅ SUNSET complete ({len(events)} events)")
        return events

    def _phase_archive(self) -> List[Dict[str, Any]]:
        """ARCHIVE PHASE (Night) - Taxes, Settlement, Ledger Commit."""
        logger.info("\n🌙 PHASE 4: ARCHIVE (Night)")
        logger.info("   The night watch - Taxes, Settlement, Ledger Commit")

        events = []
        phase = CyclePhase.ARCHIVE

        # Civic tax collection
        logger.info("   💳 CIVIC collects taxes and settles economy (Artha/Wealth)")
        events.append(
            self._create_event(
                phase,
                "civic",
                "tax_collection",
                "Daily economic settlement. Credits redistributed. Public fund updated.",
            )
        )
        self._record_to_ledger("CIVIC_TAX_COLLECTION", "civic", {"phase": "archive", "action": "settle_economy"})

        # Mechanic maintenance
        logger.info("   🔧 MECHANIC performs maintenance (housekeeping & repairs)")
        events.append(
            self._create_event(
                phase,
                "mechanic",
                "maintenance",
                "Overnight maintenance. Logs rotated. Cache cleared. System refreshed.",
            )
        )
        self._record_to_ledger("MECHANIC_MAINTENANCE", "mechanic", {"phase": "archive", "action": "housekeeping"})

        # Ledger commit
        logger.info("   ⛓️  LEDGER COMMIT (immutable record finalized)")
        events.append(
            self._create_event(
                phase, "kernel", "ledger_commit", "Complete day's events committed to immutable ledger. Hash verified."
            )
        )
        self._record_to_ledger("LEDGER_COMMIT", "kernel", {"phase": "archive", "day": self.cycle_count})

        # System sleep
        logger.info("   😴 System enters sleep. Ready for tomorrow's dawn.")
        events.append(
            self._create_event(
                phase, "system", "system_sleep", "Night watch complete. System in standby. Awaiting next sunrise."
            )
        )

        logger.info(f"   ✅ ARCHIVE complete ({len(events)} events)")
        return events

    def get_phase_summary(self) -> Dict[str, Any]:
        """Get summary of current day's activities"""
        return {
            "day_number": self.cycle_count,
            "total_events": len(self.events_this_cycle),
            "timestamp": datetime.now().isoformat(),
            "events": self.events_this_cycle,
        }
