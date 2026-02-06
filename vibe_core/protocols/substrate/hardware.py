"""
HARDWARE PROTOCOLS - Layer -1 (Vedic Computer Architecture)
============================================================

Extracted from protocols/substrate/__init__.py.

8 Hardware Protocols defining the physics of conscious computing:
- PranaProtocol    = Power Supply (Life Force)
- KalaProtocol     = System Clock (Time Measurement)
- ChittaProtocol   = RAM (Volatile Mind-Stuff)
- SmritiProtocol   = Cache (Memory Hierarchy)
- NadiProtocol     = Bus (Data Channels)
- SankalpaProtocol = Interrupts (Intent/Will)
- IndriyaProtocol  = Registers/IO (Sense Organs)
- AkashaProtocol   = Network (Field/Ether)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x253336b8"

from typing import Dict, List, Optional, Protocol, Tuple, TypeVar, runtime_checkable

from vibe_core.protocols.substrate.types import (
    ActionData,
    ChittaBlock,
    FieldState,
    NadiChannel,
    PranaLevel,
    SankalpaIntent,
    SenseData,
    Vritti,
    YugaState,
)

ValueT = TypeVar("ValueT")


# -----------------------------------------------------------------------------
# PRANA PROTOCOL (Power Supply / Life Force)
# -----------------------------------------------------------------------------


@runtime_checkable
class PranaProtocol(Protocol):
    """
    The Life Force. Without Prana, nothing moves.

    In hardware: Power Supply Unit (PSU)
    In biology: ATP / Breath / Metabolism
    In Vedas: The 5 Pranas (Prana, Apana, Vyana, Udana, Samana)

    CRITICAL: If Prana = 0, system is DEAD (not sleeping - DEAD).

    The 5 Pranas:
    - Prana: Inward energy (intake)
    - Apana: Downward energy (elimination)
    - Vyana: Outward energy (circulation)
    - Udana: Upward energy (expression)
    - Samana: Equalizing energy (digestion/processing)
    """

    def breathe_in(self) -> PranaLevel:
        """Inhale - gather energy from source (Prana vayu)."""
        ...

    def breathe_out(self) -> PranaLevel:
        """Exhale - distribute energy to system (Apana vayu)."""
        ...

    def circulate(self) -> PranaLevel:
        """Circulate energy throughout (Vyana vayu)."""
        ...

    def get_vitality(self) -> float:
        """Current energy level (0.0 = dead, 1.0 = full)."""
        ...

    def suspend(self) -> None:
        """Enter low-power state (Yoga Nidra / S3 Sleep)."""
        ...

    def revive(self, source: str) -> bool:
        """Attempt to restore life from external source."""
        ...

    def is_alive(self) -> bool:
        """Check if system has life force."""
        ...


# -----------------------------------------------------------------------------
# KALA PROTOCOL (System Clock / Time)
# -----------------------------------------------------------------------------


@runtime_checkable
class KalaProtocol(Protocol):
    """
    Time itself. The master clock measurement.

    In hardware: Crystal oscillator readout, RTC
    In physics: Planck time, atomic clock
    In Vedas: Kala (one of Krishna's energies - Time personified)

    NOTE: MantraProtocol IS the clock SIGNAL.
    KalaProtocol MEASURES that signal and tracks epochs.

    Time Units (Vedic):
    - Truti: Smallest unit (~29.6 microseconds)
    - Nimesa: Blink of eye (~16/75 second)
    - Prana: One breath (~4 seconds)
    - Ghatika: 24 minutes
    - Muhurta: 48 minutes
    - Prahar: 3 hours
    - Ahoratra: 24 hours (day-night)
    """

    def get_tick(self) -> int:
        """Current tick count (mantra cycles since boot)."""
        ...

    def get_yuga(self) -> YugaState:
        """Current epoch information."""
        ...

    def get_muhurta(self) -> str:
        """Current auspicious period name."""
        ...

    def wait_cycles(self, n: int) -> None:
        """Block for n mantra cycles (sleep)."""
        ...

    def is_auspicious(self, action: str) -> bool:
        """Check if current time is good for action (Muhurta calculation)."""
        ...

    def get_elapsed(self, since_tick: int) -> int:
        """Get ticks elapsed since given tick."""
        ...


# -----------------------------------------------------------------------------
# CHITTA PROTOCOL (RAM / Volatile Memory)
# -----------------------------------------------------------------------------


@runtime_checkable
class ChittaProtocol(Protocol):
    """
    The Mind-Stuff. Volatile, impressionable, reactive.

    In hardware: RAM (Random Access Memory)
    In psychology: Working memory, context window
    In Yoga: Chitta (the field where thoughts arise)

    PROPERTY: Chitta is COLORED by what touches it (Vritti).
    Clean Chitta = Clear thinking. Dirty Chitta = Confusion.

    "yogaś citta-vṛtti-nirodhaḥ"
    "Yoga is the cessation of the modifications of the mind."
    — Yoga Sutra 1.2

    The 5 Vrittis (Mental Modifications):
    - Pramana: Valid knowledge
    - Viparyaya: Misconception
    - Vikalpa: Imagination
    - Nidra: Sleep
    - Smriti: Memory
    """

    def allocate(self, size: int, owner: str) -> ChittaBlock:
        """
        Allocate mind-space.
        owner = Sovereign ID (Anti-Mayavad: must be signed).
        """
        ...

    def deallocate(self, block: ChittaBlock) -> None:
        """Free allocated mind-space."""
        ...

    def impress(self, block: ChittaBlock, vritti: Vritti) -> None:
        """Make an impression on allocated space."""
        ...

    def read_impression(self, block: ChittaBlock) -> Optional[Vritti]:
        """Read what was impressed."""
        ...

    def clear(self, block: ChittaBlock) -> None:
        """
        Clear impressions (Chitta Vritti Nirodha).
        This is the goal of Yoga - still the mind.
        """
        ...

    def get_turbulence(self) -> float:
        """How disturbed is the mind? (0.0 = still, 1.0 = chaos)."""
        ...

    def get_total_capacity(self) -> int:
        """Total allocatable mind-space."""
        ...

    def get_free_capacity(self) -> int:
        """Available mind-space."""
        ...


# -----------------------------------------------------------------------------
# SMRITI PROTOCOL (Cache / Memory Hierarchy)
# -----------------------------------------------------------------------------


@runtime_checkable
class SmritiProtocol(Protocol):
    """
    Memory/Recollection. The cache hierarchy.

    In hardware: L1/L2/L3 cache, TLB
    In psychology: Short-term, long-term, episodic memory
    In Vedas: Smriti ("that which is remembered")

    HIERARCHY (4 Levels):
    - L1 (Pratyaksha): Immediate - current mantra cycle
    - L2 (Anumana): Recent - current mala (108 cycles)
    - L3 (Shabda): Session - current runtime
    - L4 (Akasha): Permanent - immutable ledger

    NOTE: Unlike hardware cache, Smriti includes QUALITY.
    Some memories are "cleaner" (Sattvic) than others.
    """

    def remember(self, key: str, value: ValueT, level: int = 1) -> None:
        """
        Store in cache at specified level.
        level: 1=immediate, 2=recent, 3=session, 4=permanent
        """
        ...

    def recall(self, key: str) -> Optional[Tuple[ValueT, int]]:
        """
        Recall from any level.
        Returns (value, level_found) or None if not found.
        """
        ...

    def forget(self, key: str, level: int = 0) -> bool:
        """
        Remove from specified level (0 = all levels).
        Returns True if found and removed.
        """
        ...

    def promote(self, key: str) -> bool:
        """Move from slower to faster cache (hot path optimization)."""
        ...

    def demote(self, key: str) -> bool:
        """Move from faster to slower cache (cold path)."""
        ...

    def get_level_stats(self, level: int) -> Dict[str, int]:
        """Get cache statistics for a level (hits, misses, size)."""
        ...


# -----------------------------------------------------------------------------
# NADI PROTOCOL (Bus / Data Channels)
# -----------------------------------------------------------------------------


@runtime_checkable
class NadiProtocol(Protocol):
    """
    Energy Channels. The data bus.

    In hardware: System bus, PCIe, memory bus, USB
    In biology: Nervous system, blood vessels, meridians
    In Yoga: 72,000 Nadis (3 main: Ida, Pingala, Sushumna)

    TOPOLOGY:
    - Ida (Left/Moon): Input channel (receive, cool, parasympathetic)
    - Pingala (Right/Sun): Output channel (send, hot, sympathetic)
    - Sushumna (Center): Bidirectional (balance, neutral, transcendent)

    Granthis (Blockages):
    - Brahma Granthi: Base blockage (attachment to material)
    - Vishnu Granthi: Heart blockage (attachment to emotion)
    - Rudra Granthi: Head blockage (attachment to ego)
    """

    def open_channel(self, source: str, dest: str, channel_type: str = "sushumna") -> NadiChannel:
        """
        Open a new channel between endpoints.
        channel_type: "ida" (in), "pingala" (out), "sushumna" (both)
        """
        ...

    def close_channel(self, channel: NadiChannel) -> None:
        """Close channel and release resources."""
        ...

    def send(self, channel: NadiChannel, data: bytes) -> bool:
        """
        Send data through channel.
        Returns True if sent successfully.
        """
        ...

    def receive(self, channel: NadiChannel, timeout: float = 0.0) -> Optional[bytes]:
        """
        Receive data from channel.
        timeout=0 means non-blocking.
        """
        ...

    def get_bandwidth(self, channel: NadiChannel) -> float:
        """Current throughput capacity (bytes/second)."""
        ...

    def is_blocked(self, channel: NadiChannel) -> bool:
        """Check for Nadi blockage (Granthi)."""
        ...

    def clear_blockage(self, channel: NadiChannel) -> bool:
        """Attempt to clear a blockage. Returns True if successful."""
        ...


# -----------------------------------------------------------------------------
# SANKALPA PROTOCOL (Interrupt / Intent)
# -----------------------------------------------------------------------------


@runtime_checkable
class SankalpaProtocol(Protocol):
    """
    Will/Intent. The interrupt system.

    In hardware: IRQ, signals, event queue
    In psychology: Intention, volition, attention
    In Vedas: Sankalpa (solemn vow/determination)

    PROPERTY: Sankalpa is the CAUSE of action.
    No Sankalpa = No action (system idle).
    Wrong Sankalpa = Wrong action (bug).
    Aligned Sankalpa = Dharmic action (correct).

    "saṅkalpa-prabhavān kāmāṁs tyaktvā sarvān aśeṣataḥ"
    "Abandoning all desires arising from mental concoction..."
    — Bhagavad Gita 6.24
    """

    def declare(self, intent: SankalpaIntent) -> str:
        """
        Declare an intention. Returns intent_id.
        Higher priority = interrupt current work.
        """
        ...

    def revoke(self, intent_id: str) -> bool:
        """Cancel declared intention. Returns True if found."""
        ...

    def get_pending(self) -> List[SankalpaIntent]:
        """Get all pending intentions (interrupt queue)."""
        ...

    def execute_next(self) -> Optional[SankalpaIntent]:
        """Pop and return highest priority intent."""
        ...

    def is_aligned(self, intent: SankalpaIntent) -> bool:
        """Check if intent aligns with Dharma (valid interrupt)."""
        ...

    def get_current(self) -> Optional[SankalpaIntent]:
        """Get currently executing intent (if any)."""
        ...


# -----------------------------------------------------------------------------
# INDRIYA PROTOCOL (Registers / I/O Ports)
# -----------------------------------------------------------------------------


@runtime_checkable
class IndriyaProtocol(Protocol):
    """
    The Senses. Registers and I/O ports.

    In hardware: CPU registers, GPIO, I/O ports
    In biology: 5 sense organs + 5 action organs
    In Samkhya: 10 Indriyas (+ Manas as 11th coordinator)

    JNANENDRIYAS (5 Input / Perception):
    - Shrotra (Ear): Audio input - hearing
    - Tvak (Skin): Touch input - haptic
    - Chakshu (Eye): Visual input - sight
    - Rasana (Tongue): Chemical input - taste
    - Ghrana (Nose): Chemical input - smell

    KARMENDRIYAS (5 Output / Action):
    - Vak (Voice): Audio output - speech
    - Pani (Hands): Manipulation output - grasping
    - Pada (Feet): Movement output - locomotion
    - Payu (Anus): Elimination output - excretion
    - Upastha (Genitals): Creation output - reproduction

    BANDWIDTH: Each sense has limited bandwidth.
    Overload = sensory overwhelm = system stress.
    """

    def sense(self, indriya: str) -> SenseData:
        """
        Read from sense organ (input register).
        indriya: "shrotra", "tvak", "chakshu", "rasana", "ghrana"
        """
        ...

    def act(self, indriya: str, data: ActionData) -> bool:
        """
        Write to action organ (output register).
        indriya: "vak", "pani", "pada", "payu", "upastha"
        """
        ...

    def calibrate(self, indriya: str) -> bool:
        """Calibrate sense/action organ. Returns True if successful."""
        ...

    def get_bandwidth(self, indriya: str) -> float:
        """Throughput capacity of this sense (data/second)."""
        ...

    def is_overloaded(self, indriya: str) -> bool:
        """Check if sense is overwhelmed."""
        ...

    def rest(self, indriya: str) -> None:
        """Rest a sense organ (reduce load)."""
        ...


# -----------------------------------------------------------------------------
# AKASHA PROTOCOL (Network / The Ether Field)
# -----------------------------------------------------------------------------


@runtime_checkable
class AkashaProtocol(Protocol):
    """
    The Ether. The universal field. The network.

    In hardware: NIC, internet, mesh network
    In physics: Electromagnetic field, quantum field
    In Vedas: Akasha (space/ether - the 5th element)

    PARADIGM SHIFT FROM TCP/IP:
    - IP Address → Sovereign Identity (WHO you are, not WHERE)
    - TCP Handshake → Pranam (respectful connection)
    - Packet routing → Resonance (direct field connection)
    - DNS → Resonance pattern matching
    - Firewall → Dharma Gate

    PROPERTY: In Akasha, distance is irrelevant.
    Connection is by RESONANCE, not location.
    If you tune to the same frequency, you connect instantly.

    "ākāśāt patitaṁ toyaṁ yathā gacchati sāgaram"
    "As water fallen from the sky goes to the ocean..."
    — Everything returns to the Field.
    """

    def broadcast(self, frequency: float, message: bytes) -> None:
        """
        Broadcast to all who resonate at this frequency.
        Unlike IP multicast, receivers self-select by resonance.
        """
        ...

    def tune(self, frequency: float) -> str:
        """
        Tune to a frequency. Returns channel_id.
        You will receive all broadcasts at this frequency.
        """
        ...

    def untune(self, channel_id: str) -> None:
        """Stop listening to a frequency."""
        ...

    def connect(self, identity: str) -> Optional[NadiChannel]:
        """
        Connect directly to a Sovereign by identity.
        Not by IP, but by WHO THEY ARE.
        Returns channel or None if identity not found.
        """
        ...

    def query_field(self, pattern: str) -> List[str]:
        """
        Find all entities matching a resonance pattern.
        Like DNS but for consciousness. Returns list of identities.
        """
        ...

    def get_field_state(self) -> FieldState:
        """
        Get current state of the Akashic field.
        Includes: active entities, dominant frequencies, field coherence.
        """
        ...

    def get_local_identity(self) -> str:
        """Get this node's Sovereign Identity in the field."""
        ...
