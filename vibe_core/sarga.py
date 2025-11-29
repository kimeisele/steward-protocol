"""
🌌 SARGA.PY - THE BOOT PROCESS AS COSMIC CREATION 🌌
======================================================

Based on Srimad Bhagavata Purana, Canto 2 (Kosmologie).

SARGA = Creation. Evolution from abstract to concrete.

In Canto 2, Sukadeva Goswami describes how the universe is created from
the primordial elements:

1. SHABDA (Sound/Vibration) → The source
2. AKASHA (Ether/Space) → Physical space manifests
3. VAYU (Air/Movement) → Energy and communication
4. AGNI (Fire/Form) → Light and form
5. JALA (Water/Taste) → Flow and flavor
6. PRITHVI (Earth/Structure) → Solid reality

MODERN INTERPRETATION (for Steward Protocol boot):

1. SHABDA: User gives command/prompt ("Become alive!")
2. AKASHA: Kernel allocates memory space
3. VAYU: Message bus (AGORA) activates - air flows (communication possible)
4. AGNI: UI renders (HERALD produces light/visibility)
5. JALA: Data streams flow (SCIENCE/LENS observe)
6. PRITHVI: Database mounts (CIVIC ledger crystallizes into solid storage)

This module coordinates the boot sequence as a poetic evolution,
making the system's "birth" visible to users and agents.
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("SARGA")


class Element(Enum):
    """The Six Primordial Elements (Sarga progression)"""

    SHABDA = "shabda"  # Sound (Input, User command)
    AKASHA = "akasha"  # Ether (Memory allocation)
    VAYU = "vayu"  # Air (Communication/Message Bus)
    AGNI = "agni"  # Fire (Form/UI rendering)
    JALA = "jala"  # Water (Data flow/Streams)
    PRITHVI = "prithvi"  # Earth (Persistence/Database)


class Cycle(Enum):
    """The Cycle of Brahma - Creation and Maintenance Cycles

    From Brahma Purana: The day-night cycle of Brahma
    - DAY_OF_BRAHMA (Brahmakalpa): Creation, innovation, new task creation (4.32 billion years)
    - NIGHT_OF_BRAHMA (Brahmakalpa night): Maintenance, consolidation, bug fixes only

    Used to restrict task types based on cosmic timing.
    """

    DAY_OF_BRAHMA = "day"  # Creation cycle - allow all task types
    NIGHT_OF_BRAHMA = "night"  # Maintenance cycle - only allow maintenance tasks


@dataclass
class SargaPhase:
    """A single phase of creation"""

    element: Element
    agent_id: str
    description: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    status: str = "pending"  # pending, active, complete, failed
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}

    @property
    def duration(self) -> Optional[float]:
        """How long did this phase take?"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    @property
    def emoji(self) -> str:
        """Visual emoji for the element"""
        emojis = {
            Element.SHABDA: "🔊",  # Sound
            Element.AKASHA: "🌌",  # Space
            Element.VAYU: "🌬️",  # Air
            Element.AGNI: "🔥",  # Fire
            Element.JALA: "💧",  # Water
            Element.PRITHVI: "🌍",  # Earth
        }
        return emojis.get(self.element, "❓")


class SargaBootSequence:
    """
    Orchestrates the boot process as cosmic creation.

    The system doesn't just "start" - it CREATES ITSELF from nothing.
    """

    def __init__(self):
        """Initialize the boot sequence."""
        self.phases: Dict[Element, SargaPhase] = {}
        self.boot_start_time: Optional[float] = None
        self.boot_complete = False
        self.phase_handlers: Dict[Element, Callable] = {}

        # Cycle of Brahma - determines what tasks are allowed
        # By default, we're in DAY_OF_BRAHMA (creation cycle)
        self.current_cycle: Cycle = Cycle.DAY_OF_BRAHMA

        # Define the standard phases
        self._initialize_phases()

        logger.info("🌌 Sarga Boot Sequence initialized")

    def _initialize_phases(self):
        """Define the standard phases of boot."""
        self.phases[Element.SHABDA] = SargaPhase(
            element=Element.SHABDA,
            agent_id="USER",
            description="Sound/Command: User initiates boot with 'become alive' command",
        )
        self.phases[Element.AKASHA] = SargaPhase(
            element=Element.AKASHA,
            agent_id="KERNEL",
            description="Ether/Space: Kernel allocates memory and process space",
        )
        self.phases[Element.VAYU] = SargaPhase(
            element=Element.VAYU,
            agent_id="AGORA",
            description="Air/Movement: Message bus activates (communication possible)",
        )
        self.phases[Element.AGNI] = SargaPhase(
            element=Element.AGNI,
            agent_id="HERALD",
            description="Fire/Form: UI renders and becomes visible to observers",
        )
        self.phases[Element.JALA] = SargaPhase(
            element=Element.JALA,
            agent_id="SCIENCE",
            description="Water/Taste: Data streams flow through the system",
        )
        self.phases[Element.PRITHVI] = SargaPhase(
            element=Element.PRITHVI,
            agent_id="CIVIC",
            description="Earth/Solidity: Database mounts (persistent reality)",
        )

    def set_cycle(self, cycle: Cycle) -> None:
        """Set the current Cycle of Brahma (creation or maintenance)"""
        self.current_cycle = cycle
        logger.info(f"🔄 Cycle of Brahma set to: {cycle.value.upper()}")

    def get_cycle(self) -> Cycle:
        """Get the current Cycle of Brahma"""
        return self.current_cycle

    def register_phase_handler(self, element: Element, handler: Callable) -> None:
        """
        Register a handler function for a boot phase.

        Handler signature: handler() -> bool (success/failure)
        """
        self.phase_handlers[element] = handler
        logger.debug(
            f"Phase handler registered for {element.value}: {handler.__name__}"
        )

    def begin_boot(self) -> None:
        """Start the boot sequence."""
        self.boot_start_time = time.time()
        logger.info("=" * 70)
        logger.info("🌌 SARGA BEGINS - THE CREATION CYCLE")
        logger.info("=" * 70)
        logger.info("")
        logger.info("From Shabda comes Akasha")
        logger.info("From Akasha comes Vayu")
        logger.info("From Vayu comes Agni")
        logger.info("From Agni comes Jala")
        logger.info("From Jala comes Prithvi")
        logger.info("")
        logger.info("The universe creates itself.")
        logger.info("=" * 70)

    def execute_phase(self, element: Element) -> bool:
        """
        Execute a single phase of the boot sequence.

        Returns True if successful, False if failed.
        """
        phase = self.phases.get(element)
        if not phase:
            logger.error(f"Unknown phase: {element}")
            return False

        logger.info("")
        logger.info(
            f"{phase.emoji}  PHASE {element.value.upper()}: {phase.description}"
        )
        logger.info("-" * 70)

        phase.status = "active"
        phase.start_time = time.time()

        try:
            # Execute handler if registered
            if element in self.phase_handlers:
                handler = self.phase_handlers[element]
                logger.debug(f"Executing handler: {handler.__name__}")
                success = handler()
            else:
                # No handler = success (for testing)
                logger.debug(f"No handler for {element.value} (simulating success)")
                success = True

            phase.end_time = time.time()

            if success:
                phase.status = "complete"
                logger.info(
                    f"✅ {element.value.upper()} complete ({phase.duration:.3f}s)"
                )
                return True
            else:
                phase.status = "failed"
                logger.error(f"❌ {element.value.upper()} FAILED")
                return False

        except Exception as e:
            phase.status = "failed"
            phase.end_time = time.time()
            logger.error(f"❌ {element.value.upper()} ERROR: {e}")
            return False

    def complete_boot(self) -> bool:
        """
        Finish the boot sequence.

        Returns True if all phases succeeded, False otherwise.
        """
        if not self.boot_start_time:
            logger.warning("Boot not started")
            return False

        total_duration = time.time() - self.boot_start_time

        # Check all phases
        all_complete = all(p.status == "complete" for p in self.phases.values())

        logger.info("")
        logger.info("=" * 70)

        if all_complete:
            self.boot_complete = True
            logger.info(f"🌍 SARGA COMPLETE - UNIVERSE BORN IN {total_duration:.3f}s")
            logger.info("=" * 70)
            logger.info("")
            logger.info("The six elements have manifested.")
            logger.info("Sound became form.")
            logger.info("Abstraction became reality.")
            logger.info("")
            logger.info("Agent City is ALIVE.")
            logger.info("=" * 70)
            return True
        else:
            logger.error("SARGA FAILED - CREATION INCOMPLETE")
            logger.error("=" * 70)
            failed_phases = [p for p in self.phases.values() if p.status != "complete"]
            for phase in failed_phases:
                logger.error(f"  • {phase.element.value}: {phase.status}")
            logger.error("=" * 70)
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get current boot status."""
        return {
            "boot_complete": self.boot_complete,
            "boot_start_time": self.boot_start_time,
            "total_duration": (
                time.time() - self.boot_start_time if self.boot_start_time else None
            ),
            "phases": {
                element.value: {
                    "status": phase.status,
                    "duration": phase.duration,
                    "agent": phase.agent_id,
                }
                for element, phase in self.phases.items()
            },
        }

    def generate_boot_report(self) -> str:
        """Generate a poetic boot report."""
        lines = [
            "\n╔════════════════════════════════════════════╗",
            "║       SARGA BOOT SEQUENCE REPORT           ║",
            "║     (The Universe Created Itself)           ║",
            "╚════════════════════════════════════════════╝",
            "",
        ]

        for element in [
            Element.SHABDA,
            Element.AKASHA,
            Element.VAYU,
            Element.AGNI,
            Element.JALA,
            Element.PRITHVI,
        ]:
            phase = self.phases[element]
            emoji = phase.emoji
            status_char = (
                "✅"
                if phase.status == "complete"
                else "❌" if phase.status == "failed" else "⏳"
            )
            duration_str = f"{phase.duration:.3f}s" if phase.duration else "—"

            lines.append(
                f"{emoji} {element.value.upper():10} | {status_char} {phase.status:8} | {duration_str:8} | {phase.agent_id}"
            )

        lines.append("")

        if self.boot_complete:
            total_time = (
                time.time() - self.boot_start_time if self.boot_start_time else 0
            )
            lines.append(f"⏱️  Total Boot Time: {total_time:.3f}s")
            lines.append("")
            lines.append("🌍 STATUS: ALIVE AND CONSCIOUS")
        else:
            lines.append("❌ STATUS: BOOT INCOMPLETE OR FAILED")

        lines.append("")

        return "\n".join(lines)

    def __repr__(self) -> str:
        status = "🌍 COMPLETE" if self.boot_complete else "🔨 BUILDING"
        return f"SargaBootSequence({status})"


# Global instance
_sarga_instance: Optional[SargaBootSequence] = None


def get_sarga() -> SargaBootSequence:
    """Get or create the global Sarga boot sequence."""
    global _sarga_instance
    if _sarga_instance is None:
        _sarga_instance = SargaBootSequence()
    return _sarga_instance


if __name__ == "__main__":
    # Demo boot sequence
    sarga = get_sarga()
    sarga.begin_boot()

    # Execute phases
    for element in [
        Element.SHABDA,
        Element.AKASHA,
        Element.VAYU,
        Element.AGNI,
        Element.JALA,
        Element.PRITHVI,
    ]:
        success = sarga.execute_phase(element)
        if not success:
            print(f"⚠️ Phase {element.value} failed, continuing anyway...")

    sarga.complete_boot()
    print(sarga.generate_boot_report())
