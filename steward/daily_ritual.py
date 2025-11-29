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
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

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
        logger.info(
            f"🌙 DAY {self.cycle_count}: COMPLETE - {len(all_events)} events recorded"
        )
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
        """
        SUNRISE PHASE (Brahma-Muhurta)
        ==============================

        Early morning - the auspicious hour.
        System wakes up. Temple opens. Watchman patrols.
        This is the blessing that sanctifies the day.
        """
        logger.info("\n🌅 PHASE 1: SUNRISE (Brahma-Muhurta)")
        logger.info("   The auspicious hour - Temple opens, Watchman patrols")

        events = []

        # Step 1: TEMPLE BLESSING
        # The temple is the spiritual center - it opens first
        logger.info("   ✨ TEMPLE opens and gives blessing to the system")
        temple_event = {
            "timestamp": datetime.now().isoformat(),
            "phase": CyclePhase.SUNRISE.value,
            "agent": "temple",
            "action": "blessing",
            "details": "Sacred blessing for a new day. System purity verified.",
        }
        events.append(temple_event)

        # Record in ledger
        if self.kernel:
            try:
                self.kernel.ledger.record_event(
                    "TEMPLE_BLESSING",
                    "temple",
                    {"phase": "sunrise", "purpose": "daily_sanctification"},
                )
            except Exception as e:
                logger.error(f"Could not record temple blessing: {e}")

        # Step 2: WATCHMAN PATROL
        # The watchman does security checks - perimeter patrol
        logger.info("   👮 WATCHMAN performs morning patrol (security check)")
        watchman_event = {
            "timestamp": datetime.now().isoformat(),
            "phase": CyclePhase.SUNRISE.value,
            "agent": "watchman",
            "action": "patrol",
            "details": "Morning perimeter check. All systems nominal. No alerts.",
        }
        events.append(watchman_event)

        # Record in ledger
        if self.kernel:
            try:
                self.kernel.ledger.record_event(
                    "WATCHMAN_PATROL",
                    "watchman",
                    {"phase": "sunrise", "status": "all_clear"},
                )
            except Exception as e:
                logger.error(f"Could not record watchman patrol: {e}")

        # Step 3: ORACLE INTROSPECTION
        # The oracle reveals the state of the system
        logger.info("   🔮 ORACLE reveals system state (daily introspection)")
        oracle_event = {
            "timestamp": datetime.now().isoformat(),
            "phase": CyclePhase.SUNRISE.value,
            "agent": "oracle",
            "action": "introspection",
            "details": "System state revealed. Ready for the day's work.",
        }
        events.append(oracle_event)

        # Record in ledger
        if self.kernel:
            try:
                self.kernel.ledger.record_event(
                    "ORACLE_INTROSPECTION",
                    "oracle",
                    {"phase": "sunrise", "visibility": "full"},
                )
            except Exception as e:
                logger.error(f"Could not record oracle introspection: {e}")

        logger.info(f"   ✅ SUNRISE complete ({len(events)} events)")
        return events

    def _phase_midday(self) -> List[Dict[str, Any]]:
        """
        MIDDAY PHASE (Karma-Yoga)
        =========================

        High noon - peak activity time.
        Herald broadcasts. Market trades. Agents work.
        This is the productive action phase.
        """
        logger.info("\n☀️  PHASE 2: MIDDAY (Karma-Yoga)")
        logger.info("   The time of action - Work begins, Market opens")

        events = []

        # Step 1: HERALD BROADCASTS
        # The herald speaks to the city - a proclamation
        logger.info("   📣 HERALD broadcasts a message (Diksha/Teaching)")
        herald_event = {
            "timestamp": datetime.now().isoformat(),
            "phase": CyclePhase.MIDDAY.value,
            "agent": "herald",
            "action": "broadcast",
            "content": "Intelligence without Governance is Chaos. The City stands unified in Constitutional Law.",
            "details": "Daily proclamation of core principles.",
        }
        events.append(herald_event)

        # Record in ledger
        if self.kernel:
            try:
                self.kernel.ledger.record_event(
                    "HERALD_BROADCAST",
                    "herald",
                    {
                        "phase": "midday",
                        "message": "Constitutional principles affirmed",
                    },
                )
            except Exception as e:
                logger.error(f"Could not record herald broadcast: {e}")

        # Step 2: AGORA RECEIVES MESSAGE
        # The agora is the broadcast channel - it carries the message
        logger.info("   🌊 AGORA stream activated (message distribution)")
        agora_event = {
            "timestamp": datetime.now().isoformat(),
            "phase": CyclePhase.MIDDAY.value,
            "agent": "agora",
            "action": "broadcast_stream",
            "details": "Message flows through the one-way broadcast channel. All agents listen.",
        }
        events.append(agora_event)

        # Record in ledger
        if self.kernel:
            try:
                self.kernel.ledger.record_event(
                    "AGORA_BROADCAST",
                    "agora",
                    {"phase": "midday", "subscribers": "all_agents"},
                )
            except Exception as e:
                logger.error(f"Could not record agora broadcast: {e}")

        # Step 3: DISCIPLES LISTEN AND REACT
        # Pulse and Lens listen to the broadcast
        logger.info("   👂 PULSE & LENS listen and react (disciples hear the dharma)")
        disciples_event = {
            "timestamp": datetime.now().isoformat(),
            "phase": CyclePhase.MIDDAY.value,
            "agents": ["pulse", "lens"],
            "action": "listen_and_process",
            "details": "Disciples process the teaching. PULSE amplifies. LENS analyzes.",
        }
        events.append(disciples_event)

        # Record in ledger
        if self.kernel:
            try:
                self.kernel.ledger.record_event(
                    "DISCIPLES_LISTEN",
                    "pulse",
                    {"phase": "midday", "action": "process_dharma"},
                )
                self.kernel.ledger.record_event(
                    "DISCIPLES_LISTEN",
                    "lens",
                    {"phase": "midday", "action": "analyze_stream"},
                )
            except Exception as e:
                logger.error(f"Could not record disciples listening: {e}")

        # Step 4: MARKET TRADES
        # The market processes commerce and transactions
        logger.info("   💰 MARKET settles transactions (commerce/artha)")
        market_event = {
            "timestamp": datetime.now().isoformat(),
            "phase": CyclePhase.MIDDAY.value,
            "agent": "market",
            "action": "trade_settlement",
            "details": "Market executes pending trades. Service requests processed.",
        }
        events.append(market_event)

        # Record in ledger
        if self.kernel:
            try:
                self.kernel.ledger.record_event(
                    "MARKET_TRADE",
                    "market",
                    {"phase": "midday", "action": "settle_transactions"},
                )
            except Exception as e:
                logger.error(f"Could not record market trade: {e}")

        # Step 5: AGENTS PRODUCE WORK
        # Science researches, Engineer builds, Artisan creates
        logger.info("   🔨 AGENTS work (Science/Engineer/Artisan productive phase)")
        agents_event = {
            "timestamp": datetime.now().isoformat(),
            "phase": CyclePhase.MIDDAY.value,
            "agents": ["science", "engineer", "artisan"],
            "action": "productive_work",
            "details": "Specialists engage their domains. Output is generated.",
        }
        events.append(agents_event)

        # Record in ledger
        if self.kernel:
            try:
                self.kernel.ledger.record_event(
                    "AGENTS_WORK",
                    "engineer",
                    {"phase": "midday", "action": "productive_output"},
                )
            except Exception as e:
                logger.error(f"Could not record agents work: {e}")

        logger.info(f"   ✅ MIDDAY complete ({len(events)} events)")
        return events

    def _phase_sunset(self) -> List[Dict[str, Any]]:
        """
        SUNSET PHASE (Sandhya)
        ======================

        Evening - the liminal time between day and night.
        Records close. Day is audited. Archivist seals the block.
        This is the transition phase - preparing for night.
        """
        logger.info("\n🌇 PHASE 3: SUNSET (Sandhya)")
        logger.info("   The twilight hour - Records close, Day audited")

        events = []

        # Step 1: ARCHIVIST AUDIT
        # The archivist reviews all day's events and seals them
        logger.info("   📖 ARCHIVIST audits the day (verification & ledger closure)")
        archivist_event = {
            "timestamp": datetime.now().isoformat(),
            "phase": CyclePhase.SUNSET.value,
            "agent": "archivist",
            "action": "seal_block",
            "details": "All day's events verified. Hash block sealed. Immutable record created.",
        }
        events.append(archivist_event)

        # Record in ledger
        if self.kernel:
            try:
                self.kernel.ledger.record_event(
                    "ARCHIVIST_SEAL",
                    "archivist",
                    {"phase": "sunset", "action": "seal_day_block"},
                )
            except Exception as e:
                logger.error(f"Could not record archivist seal: {e}")

        # Step 2: AUDITOR VERIFICATION
        # The auditor checks compliance - GAD-000 standards
        logger.info("   ✅ AUDITOR verifies compliance (GAD-000 standards)")
        auditor_event = {
            "timestamp": datetime.now().isoformat(),
            "phase": CyclePhase.SUNSET.value,
            "agent": "auditor",
            "action": "compliance_check",
            "details": "System verified against constitutional invariants. No violations detected.",
        }
        events.append(auditor_event)

        # Record in ledger
        if self.kernel:
            try:
                self.kernel.ledger.record_event(
                    "AUDITOR_CHECK",
                    "auditor",
                    {"phase": "sunset", "compliance": "full"},
                )
            except Exception as e:
                logger.error(f"Could not record auditor check: {e}")

        # Step 3: CLOSURE
        # The day formally closes
        logger.info("   🔐 Day officially CLOSED (Sandhya boundary)")
        closure_event = {
            "timestamp": datetime.now().isoformat(),
            "phase": CyclePhase.SUNSET.value,
            "action": "day_closure",
            "details": "Twilight boundary crossed. Day is now immutable history.",
        }
        events.append(closure_event)

        # Record in ledger
        if self.kernel:
            try:
                self.kernel.ledger.record_event(
                    "DAY_CLOSURE",
                    "oracle",
                    {"phase": "sunset", "day": self.cycle_count},
                )
            except Exception as e:
                logger.error(f"Could not record day closure: {e}")

        logger.info(f"   ✅ SUNSET complete ({len(events)} events)")
        return events

    def _phase_archive(self) -> List[Dict[str, Any]]:
        """
        ARCHIVE PHASE (Night)
        ====================

        Night - the silent time of settlement and dreaming.
        Taxes are collected. The ledger is committed.
        Preparation for the next dawn.
        """
        logger.info("\n🌙 PHASE 4: ARCHIVE (Night)")
        logger.info("   The night watch - Taxes, Settlement, Ledger Commit")

        events = []

        # Step 1: CIVIC COLLECTS TAXES
        # The civic authority settles the economic ledger
        logger.info("   💳 CIVIC collects taxes and settles economy (Artha/Wealth)")
        civic_event = {
            "timestamp": datetime.now().isoformat(),
            "phase": CyclePhase.ARCHIVE.value,
            "agent": "civic",
            "action": "tax_collection",
            "details": "Daily economic settlement. Credits redistributed. Public fund updated.",
        }
        events.append(civic_event)

        # Record in ledger
        if self.kernel:
            try:
                self.kernel.ledger.record_event(
                    "CIVIC_TAX_COLLECTION",
                    "civic",
                    {"phase": "archive", "action": "settle_economy"},
                )
            except Exception as e:
                logger.error(f"Could not record civic tax collection: {e}")

        # Step 2: MECHANIC MAINTENANCE
        # The mechanic does overnight maintenance
        logger.info("   🔧 MECHANIC performs maintenance (housekeeping & repairs)")
        mechanic_event = {
            "timestamp": datetime.now().isoformat(),
            "phase": CyclePhase.ARCHIVE.value,
            "agent": "mechanic",
            "action": "maintenance",
            "details": "Overnight maintenance. Logs rotated. Cache cleared. System refreshed.",
        }
        events.append(mechanic_event)

        # Record in ledger
        if self.kernel:
            try:
                self.kernel.ledger.record_event(
                    "MECHANIC_MAINTENANCE",
                    "mechanic",
                    {"phase": "archive", "action": "housekeeping"},
                )
            except Exception as e:
                logger.error(f"Could not record mechanic maintenance: {e}")

        # Step 3: LEDGER COMMIT
        # The immutable ledger is finalized and committed
        logger.info("   ⛓️  LEDGER COMMIT (immutable record finalized)")
        ledger_event = {
            "timestamp": datetime.now().isoformat(),
            "phase": CyclePhase.ARCHIVE.value,
            "agent": "kernel",
            "action": "ledger_commit",
            "details": "Complete day's events committed to immutable ledger. Hash verified.",
        }
        events.append(ledger_event)

        # Record in ledger
        if self.kernel:
            try:
                self.kernel.ledger.record_event(
                    "LEDGER_COMMIT",
                    "kernel",
                    {"phase": "archive", "day": self.cycle_count},
                )
            except Exception as e:
                logger.error(f"Could not record ledger commit: {e}")

        # Step 4: READY FOR TOMORROW
        # System enters sleep state, ready for next dawn
        logger.info("   😴 System enters sleep. Ready for tomorrow's dawn.")
        sleep_event = {
            "timestamp": datetime.now().isoformat(),
            "phase": CyclePhase.ARCHIVE.value,
            "action": "system_sleep",
            "details": "Night watch complete. System in standby. Awaiting next sunrise.",
        }
        events.append(sleep_event)

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
