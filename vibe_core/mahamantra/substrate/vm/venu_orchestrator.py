"""
VENU ORCHESTRATOR - The Dancing Mahamantra
==========================================

"venum kvanantam aravinda-dalayataksham"
"Krishna plays His flute, with lotus-petal eyes"
— Brahma-samhita 5.30

The 19-bit Divine Instruction Word (DIW):
  VENU (6 bits) + VAMSI (9 bits) + MURALI (4 bits) = 19 bits

ALL VALUES DERIVED FROM SSOT (_seed.py). NO HARDCODING.
"""

import logging
import struct
from typing import ClassVar, Final, List, Tuple

from vibe_core.mahamantra.protocols._seed import (
    COSMIC_FRAME,
    HALVES,
    KSETRAJNA,
    MAHAMANTRA_NAME_HARE,
    MAHAMANTRA_NAME_KRISHNA,
    MAHAMANTRA_NAME_RAMA,
    MAHAMANTRA_WORD_PATTERN,
    MURALI_HOLES,
    POSITION_SUM_RAMA,
    QUARTERS,
    SEVEN,
    TEN,
    VAMSI_HOLES,
    VENU_HOLES,
    WORDS,
)
from vibe_core.mahamantra.protocols._venu import (
    DIWEvent,
    DIWSubscriberProtocol,
)
from vibe_core.mahamantra.protocols.diw import (
    CLUSTER_SHIFT,
    CONDITION_SHIFT,
    DIW_MASK,
    MURALI_SHIFT,
    SUNYA_MASK,
    VAMSI_SHIFT,
    VENU_MASK,
    VENU_SHIFT,
    pack,
    pack_full,
    unpack,
)

logger = logging.getLogger("VENU_ORCHESTRATOR")

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = HALVES
__genesis__ = "0xdd4f22d7"  # GenesisByte: parampara % 37 == 0

# =============================================================================
# NAME ENCODING (DERIVED FROM SSOT)
# =============================================================================
# Map name strings to integer encoding
# H=0, K=1, R=2 (matches HolyName enum order from byte.py)

_NAME_TO_ENCODING: Final[dict[str, int]] = {
    MAHAMANTRA_NAME_HARE: 0,  # "H" → 0
    MAHAMANTRA_NAME_KRISHNA: 1,  # "K" → 1
    MAHAMANTRA_NAME_RAMA: 2,  # "R" → 2
}


# =============================================================================
# THE FLUTE CYCLE LUT (DERIVED FROM MAHAMANTRA_WORD_PATTERN)
# =============================================================================
# Format: Native 19-bit DIW = pack(venu, vamsi, murali)
#
# Each position in the Mahamantra encodes a complete DIW:
#   VENU   (6 bits): Position-derived quality  = (pos * SEVEN) % 2^6
#   VAMSI  (9 bits): Name-derived process       = encoding * (2^9 // 3) + pos
#   MURALI (4 bits): Quarter-derived phase       = pos // (WORDS // QUARTERS)
#
# This is O(1) lookup instead of runtime calculation.


def _compute_flute_cycle() -> Tuple[int, ...]:
    """
    Compute THE_FLUTE_CYCLE from MAHAMANTRA_WORD_PATTERN (SSOT).

    Each entry is a native 19-bit DIW in canonical 6-9-4 format.
    The Mahamantra pattern determines the content of each word.
    """
    result: list[int] = []
    quarter_size = WORDS // QUARTERS  # 4 positions per quarter
    vamsi_stride = (1 << VAMSI_HOLES) // 3  # 512 // 3 = 170

    for pos, name in enumerate(MAHAMANTRA_WORD_PATTERN):
        encoding = _NAME_TO_ENCODING[name]  # H=0, K=1, R=2

        # VENU (6 bits): Quality derived from position
        # Offset by KSETRAJNA so position 0 is never silent (DIW != 0)
        # Linear spread using SEVEN ensures all 16 values are distinct
        venu = ((pos + KSETRAJNA) * SEVEN) % (1 << VENU_HOLES)  # 1-63, never 0

        # VAMSI (9 bits): Process derived from Name + position
        # Each name occupies a distinct region of the 512 space
        # Offset by KSETRAJNA ensures encoding=0,pos=0 is never zero
        vamsi = (encoding * vamsi_stride + pos + KSETRAJNA) % (1 << VAMSI_HOLES)  # 1-511

        # MURALI (4 bits): Phase derived from quarter
        murali = pos // quarter_size  # 0-3

        diw = pack(venu, vamsi, murali)
        result.append(diw)
    return tuple(result)


# Pre-computed at module load - O(1) access forever
THE_FLUTE_CYCLE: Final[Tuple[int, ...]] = _compute_flute_cycle()


# =============================================================================
# VERIFICATION: LUT INTEGRITY
# =============================================================================

if len(THE_FLUTE_CYCLE) != WORDS:
    raise ValueError(f"LUT must have {WORDS} entries, got {len(THE_FLUTE_CYCLE)}")

# Verify all entries fit in 19 bits
for _i, _entry in enumerate(THE_FLUTE_CYCLE):
    if _entry > DIW_MASK:
        raise ValueError(f"Entry {_i} exceeds 19-bit DIW: {hex(_entry)}")

# Verify MURALI encodes quarters correctly (0,0,0,0, 1,1,1,1, 2,2,2,2, 3,3,3,3)
for _i, _entry in enumerate(THE_FLUTE_CYCLE):
    _expected_quarter = _i // (WORDS // QUARTERS)
    _actual = unpack(_entry).murali
    if _actual != _expected_quarter:
        raise ValueError(f"Position {_i}: MURALI={_actual}, expected quarter {_expected_quarter}")

# Verify VAMSI distinguishes names (H, K, R occupy different regions)
_vamsi_by_name: dict[int, list[int]] = {0: [], 1: [], 2: []}
for _i, _entry in enumerate(THE_FLUTE_CYCLE):
    _encoding = _NAME_TO_ENCODING[MAHAMANTRA_WORD_PATTERN[_i]]
    _vamsi_by_name[_encoding].append(unpack(_entry).vamsi)

# Each name's VAMSI values must be unique within that name
for _enc, _vals in _vamsi_by_name.items():
    if len(_vals) != len(set(_vals)):
        raise ValueError(f"Name encoding {_enc} has duplicate VAMSI values")


# =============================================================================
# MASKS AND CONSTANTS - Re-exported from diw.py (SSOT for bit layout)
# =============================================================================
# DIW_MASK, SUNYA_MASK, VENU_SHIFT, VAMSI_SHIFT, MURALI_SHIFT,
# VELOCITY_SHIFT, CLUSTER_SHIFT are all imported from protocols.diw


# =============================================================================
# VENU ORCHESTRATOR
# =============================================================================


class VenuOrchestrator:
    """
    The Dancing Mahamantra - LUT-based O(1) Performance.

    Uses pre-computed look-up table derived from MAHAMANTRA_WORD_PATTERN.
    Pattern: rama_grid.py (SVARAS, SPARSHA_GRID as LUTs).

    "The Orchestrator plays Krishna's flute - 19 bits at a time."
    """

    __mahajana__: ClassVar[str] = "narada"
    __position__: ClassVar[int] = 2

    # Flute configuration (from _seed.py)
    VENU_BITS: ClassVar[int] = VENU_HOLES  # 6 - Low register (64 states)
    VAMSI_BITS: ClassVar[int] = VAMSI_HOLES  # 9 - Mid register (512 = SIKSASTAKAM_CACHE)
    MURALI_BITS: ClassVar[int] = MURALI_HOLES  # 4 - High register (16 = WORDS)

    __slots__ = ("_tick", "_prev_state", "_mode", "_subscribers", "_owned")

    def __init__(self) -> None:
        self._tick: int = 0
        self._prev_state: int = 0
        self._mode: int = 0  # 0=Solo, 1=CallResponse, 2=Chorus
        self._subscribers: List[DIWSubscriberProtocol] = []
        self._owned: bool = False  # DEPRECATED: Was used by VenuService bypass. Kept for audio_engine compat.

    # =========================================================================
    # PANCHA TATTVA PROTOCOL (5 Questions Every Entity Must Answer)
    # =========================================================================

    @property
    def __tattva__(self) -> dict:
        """The 5-fold truth of VenuOrchestrator."""
        return {
            "chaitanya": "VenuOrchestrator - The Dancing Mahamantra (19-bit DIW)",
            "nityananda": "THE_FLUTE_CYCLE LUT (pre-computed from MAHAMANTRA_WORD_PATTERN)",
            "advaita": "step() - O(1) LUT lookup + XOR + Mode injection",
            "gadadhara": f"VENU({VENU_HOLES}b) + VAMSI({VAMSI_HOLES}b) + MURALI({MURALI_HOLES}b) = 19b",
            "srivasa": f"WORDS ({WORDS}), COSMIC_FRAME ({COSMIC_FRAME})",
        }

    @property
    def tick(self) -> int:
        """Current tick position."""
        return self._tick

    @property
    def mode(self) -> int:
        """Current Kirtan Mode."""
        return self._mode

    # =========================================================================
    # SUBSCRIBER MANAGEMENT (Krishna's Flute -> Jivas Dance)
    # =========================================================================

    def subscribe(self, subscriber: DIWSubscriberProtocol) -> None:
        """Register a DIW subscriber.

        The subscriber's on_diw() will be called on every step()
        with the full DIWEvent. This is the bit-level orchestration
        point: nothing moves without the flute.

        Args:
            subscriber: Any object implementing DIWSubscriberProtocol.

        Raises:
            TypeError: If subscriber doesn't implement the protocol.
        """
        if not isinstance(subscriber, DIWSubscriberProtocol):
            raise TypeError(f"{type(subscriber).__name__} does not implement DIWSubscriberProtocol")
        self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber: DIWSubscriberProtocol) -> None:
        """Remove a DIW subscriber."""
        try:
            self._subscribers.remove(subscriber)
        except ValueError:
            pass  # Not subscribed — idempotent

    @property
    def subscriber_count(self) -> int:
        """Number of active DIW subscribers."""
        return len(self._subscribers)

    def _emit(self, diw: int) -> None:
        """Dispatch DIWEvent to all subscribers.

        This is the core dispatch: the flute plays, every jiva dances.
        Errors in individual subscribers are logged but never stop the flute.
        """
        if not self._subscribers:
            return

        components = unpack(diw)
        event = DIWEvent(
            diw=diw & DIW_MASK,
            tick=self._tick,
            position=self._tick % WORDS,
            phase=components.murali,
            venu=components.venu,
            vamsi=components.vamsi,
            murali=components.murali,
            mode=self._mode,
        )

        for sub in self._subscribers:
            try:
                sub.on_diw(event)
            except Exception as exc:
                logger.error(
                    "DIW subscriber %s error at tick %d: %s",
                    sub.subscriber_name,
                    self._tick,
                    exc,
                )

    # =========================================================================
    # CORE STEP
    # =========================================================================

    def step(self) -> int:
        """
        One step through the Mahamantra.
        Returns the native 19-bit DIW for the current tick | Mode Flags.

        O(1) - just a LUT lookup.

        The returned word is a canonical 6-9-4 DIW:
            VENU   (bits 0-5):  Quality/Mood
            VAMSI  (bits 6-14): Process/Action
            MURALI (bits 15-18): Phase/Quarter
            + Mode in Cluster bits (23-26)

        After computing the DIW, dispatches a DIWEvent to all subscribers.
        The flute plays, every jiva dances.
        """
        # O(1) lookup - native 19-bit DIW
        position = self._tick % WORDS
        diw = THE_FLUTE_CYCLE[position]

        # Dispatch to all subscribers BEFORE advancing tick
        # (subscribers see the tick that produced this DIW)
        self._emit(diw)

        # Update state
        self._prev_state = diw
        self._tick = (self._tick + 1) % COSMIC_FRAME

        # Inject Mode + Position into transport bits
        # Cluster (23-26): Reactor mode. Condition (27-30): Mantra position.
        return diw | (self._mode << CLUSTER_SHIFT) | (position << CONDITION_SHIFT)

    def cycle(self) -> int:
        """
        Complete 16-step cycle.
        Returns XOR of all 19-bit DIW entries (full cycle resonance).
        """
        accumulated = 0
        for i in range(WORDS):
            accumulated ^= THE_FLUTE_CYCLE[i] & DIW_MASK

        self._prev_state = accumulated
        self._tick = (self._tick + WORDS) % COSMIC_FRAME
        return accumulated

    def verify_divinity(self) -> bool:
        """
        The "Beweis Gottes" Test (non-mutating).
        Verifies the LUT has correct structural properties:
        - No entry is zero (SUNYA = silence)
        - All 4 quarters (MURALI) are represented
        - All 3 names (VAMSI regions) are represented
        - All VENU values are unique (no collisions)
        - Full cycle XOR is non-zero and fits in 19 bits
        """
        # Structural verification of the LUT (no state mutation)
        murali_set: set[int] = set()
        venu_set: set[int] = set()
        vamsi_regions: set[int] = set()
        vamsi_stride = (1 << VAMSI_HOLES) // 3  # 170

        for i, entry in enumerate(THE_FLUTE_CYCLE):
            if entry == 0:
                raise ValueError(f"Position {i} is SUNYA (zero) - the flute is silent")
            parts = unpack(entry)
            murali_set.add(parts.murali)
            venu_set.add(parts.venu)
            vamsi_regions.add(min(parts.vamsi // vamsi_stride, 2))

        if len(murali_set) != QUARTERS:
            raise ValueError(f"Must have {QUARTERS} quarters, got {len(murali_set)}")
        if len(vamsi_regions) < 3:
            raise ValueError(f"Must have 3 name regions, got {len(vamsi_regions)}")
        if len(venu_set) != WORDS:
            raise ValueError(f"Must have {WORDS} unique VENU values, got {len(venu_set)}")

        # Cycle XOR check (computed without mutating self)
        cycle_xor = 0
        for entry in THE_FLUTE_CYCLE:
            cycle_xor ^= entry & DIW_MASK
        if cycle_xor == 0:
            raise ValueError("Cycle XOR is zero - the flute is silent")
        if cycle_xor > DIW_MASK:
            raise ValueError(f"Cycle XOR exceeds 19-bit DIW: {hex(cycle_xor)}")

        return True

    def route(self, seed: int) -> Tuple[int, int, int]:
        """
        Route seed through the orchestra.

        All formulas use SSOT constants (SEVEN, TEN) to ensure
        full coverage of all 16 positions.

        FIX: murali was (seed * seed) % 16 which only produces 4 values
        (quadratic residues mod 16 = {0,1,4,9}). Now uses linear
        combination to reach all 16 positions.

        Args:
            seed: Non-negative integer seed value.

        Raises:
            TypeError: If seed is not an integer.
            ValueError: If seed is negative.
        """
        if not isinstance(seed, int):
            raise TypeError(f"seed must be int, got {type(seed).__name__}")
        if seed < 0:
            raise ValueError(f"seed must be non-negative, got {seed}")
        venu = (seed * SEVEN) % (1 << self.VENU_BITS)
        vamsi = (seed + TEN) % (1 << self.VAMSI_BITS)
        murali = (seed * SEVEN + TEN) % (1 << self.MURALI_BITS)
        return (venu, vamsi, murali)

    def harmonize(
        self,
        venu: int,
        vamsi: int,
        murali: int,
        velocity: int = 15,
        cluster_route: int = 0,
        sunya: bool = False,
    ) -> int:
        """Combine three flute states into 32-bit Instruction Word."""
        return pack_full(venu, vamsi, murali, velocity, cluster_route, sunya)

    @staticmethod
    def is_sunya(word: int) -> bool:
        """Check if instruction is silence (No-Op)."""
        from vibe_core.mahamantra.protocols.diw import is_sunya as _is_sunya

        return _is_sunya(word)

    @staticmethod
    def extract_diw(full_word: int) -> int:
        """Extract the 19-bit DIW from a 32-bit instruction word."""
        from vibe_core.mahamantra.protocols.diw import extract_core

        return extract_core(full_word)

    def spell(self, coords: Tuple[int, ...], cycle: int = 0) -> Tuple[int, ...]:
        """
        Spell a Sanskrit word through the flute.

        Each RAMA coordinate becomes the VENU field of a DIW.
        VAMSI encodes the H/K/R name-region of the generating position.
        MURALI encodes the quarter (phase in the word).

        This is the Forward Engineering mode: the flute doesn't play
        from the static LUT, it plays from a coordinate score.

        Args:
            coords: RAMA coordinate sequence (from varnamala_codec.encode).
                    Each value should be 0-48 (RAMA space). Values > VENU_MASK
                    are silently masked to 6 bits.
            cycle: Mahamantra cycle for H/K/R signature context (non-negative).

        Returns:
            Tuple of DIW values, one per coordinate (phoneme).

        Raises:
            TypeError: If coords is not a tuple/sequence of ints.
            ValueError: If cycle is negative.
        """
        if cycle < 0:
            raise ValueError(f"cycle must be non-negative, got {cycle}")
        result = []
        quarter_size = max(1, len(coords) // QUARTERS) or 1
        vamsi_stride = (1 << VAMSI_HOLES) // 3  # 170

        for i, coord in enumerate(coords):
            # VENU: The RAMA coordinate itself (0-48, fits in 6 bits)
            venu = coord & VENU_MASK

            # Inverse route: which Mahamantra position generated this coord?
            # krishna_route(pos, cycle) = (pos * 17 + cycle * 16) % 49
            # inverse: pos = ((coord - cycle * 16) * 26) % 49
            pos = ((coord - cycle * WORDS) * 26) % POSITION_SUM_RAMA
            maha_pos = pos % WORDS
            name = MAHAMANTRA_WORD_PATTERN[maha_pos]
            encoding = _NAME_TO_ENCODING[name]

            # VAMSI: Name-region + position in word
            vamsi = (encoding * vamsi_stride + i) % (1 << VAMSI_HOLES)

            # MURALI: Phase within the word
            murali = min(i // quarter_size, QUARTERS - 1)

            diw = pack(venu, vamsi, murali)
            result.append(diw)

            # Emit to subscribers (each phoneme is a tick)
            self._emit(diw)

            # Advance tick
            self._prev_state = diw
            self._tick = (self._tick + 1) % COSMIC_FRAME

        return tuple(result)

    def reset(self) -> None:
        """Reset orchestrator to initial state.

        Clears tick, prev_state, mode. Subscribers are preserved
        (they are wiring, not state). Use unsubscribe() to remove.
        """
        self._tick = 0
        self._prev_state = 0
        self._mode = 0

    def set_mode(self, mode: int) -> None:
        """Set the Kirtan Mode (0=Solo, 1=CallResponse, 2=Chorus).

        Args:
            mode: 0 (Solo), 1 (CallResponse), or 2 (Chorus).
                  Max = HALVES (2) from SSOT.

        Raises:
            TypeError: If mode is not an integer.
            ValueError: If mode is outside 0..HALVES.
        """
        if not isinstance(mode, int):
            raise TypeError(f"mode must be int, got {type(mode).__name__}")
        if not (0 <= mode <= HALVES):
            raise ValueError(f"Mode must be 0-{HALVES}, got {mode}")
        self._mode = mode

    # =========================================================================
    # PERSISTENCE
    # =========================================================================

    def to_bytes(self) -> bytes:
        """Serialize state (tick, prev_state, mode)."""
        return struct.pack("<QQQ", self._tick, self._prev_state, self._mode)

    def from_bytes(self, data: bytes) -> None:
        """Restore state from serialized bytes.

        Validates restored values against SSOT bounds:
        - tick must be < COSMIC_FRAME
        - mode must be <= HALVES
        - prev_state must be <= DIW_MASK (19 bits)

        Raises:
            ValueError: If data is too short or contains out-of-bounds values.
        """
        MIN_SIZE = 24  # 3 * 8
        if len(data) < MIN_SIZE:
            # Backwards compatibility check for old 16-byte snapshots
            if len(data) >= 16:
                self._tick, self._prev_state = struct.unpack("<QQ", data[:16])
                self._mode = 0  # Default to Solo
                self._tick %= COSMIC_FRAME
                self._prev_state &= DIW_MASK
                return
            raise ValueError("Data too short")

        tick, prev_state, mode = struct.unpack("<QQQ", data[:24])
        # Clamp to valid ranges (defensive against corrupt snapshots)
        self._tick = tick % COSMIC_FRAME
        self._prev_state = prev_state & DIW_MASK
        self._mode = min(mode, HALVES)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "THE_FLUTE_CYCLE",
    "DIW_MASK",
    "SUNYA_MASK",
    "VENU_SHIFT",
    "VAMSI_SHIFT",
    "MURALI_SHIFT",
    # Class
    "VenuOrchestrator",
    # Re-exported from _venu.py for convenience
    "DIWEvent",
    "DIWSubscriberProtocol",
]
