"""
ANTARANGA REGISTRY — The Inner Chamber (Contiguous RAM)
========================================================

"ceto-darpaṇa-mārjanaṁ" — Cleansing the mirror of the heart.

The Antaranga is the INTIMATE space where resonance happens at
hardware speed. No Python objects. No garbage collector. No pointers.
Just contiguous bytes reacting to voltage — like silicon.

Architecture:
    Bahiranga (Outer Chamber) = SankirtanChamber (Python objects, API)
    Antaranga (Inner Chamber) = THIS (contiguous bytearray, O(1) ops)

    The outer wraps the inner. Srivas Angan: the door is closed,
    but the kirtan inside is the heart.

Memory Layout (per slot):
    ┌──────────────────────────────────────────────────────────────┐
    │  HEADER (24 bytes)              │  LIFECYCLE (8 bytes)       │
    │  source(4) target(4) op(4)      │  prana(4) integ(2) cyc(2)  │
    │  arcanam(4) atma(4) flags(4)    │                            │
    └──────────────────────────────────────────────────────────────┘
    Total: 32 bytes per slot × 512 slots = 16,384 bytes (16 KB)

    This is the MINIMUM viable cell for collision/resonance:
    - source/target/op: identity (who, where, what)
    - arcanam: signature (parampara check)
    - atma_nivedanam: checksum (integrity)
    - flags: is_active(1 bit) + reserved(31 bits)
    - prana: energy (uint32, max ~4.2B)
    - integrity: membrane health (uint16, 0-65535 = 0.0-1.0)
    - cycle: age (uint16, max 65535)

Collision Logic (pure byte arithmetic):
    if resident.prana == 0:  → SILENCE: visitor takes slot
    else:                    → RESONANCE: prana += visitor.prana, integrity = avg

ALL VALUES DERIVED FROM SSOT (_seed.py). NO HARDCODING.
"""

import ctypes
import struct
from typing import Final, NamedTuple, Optional

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    KSETRAJNA,
    MAHA_QUANTUM,
    MALA,
    VAMSI_HOLES,
    WORDS,
)

# === MAHAJANA DECLARATION ===
__mahajana__ = "gauranga"
__position__ = 0

# =============================================================================
# CONSTANTS (DERIVED FROM SSOT)
# =============================================================================

# Slot count: 2^VAMSI_HOLES = 2^9 = 512
ANTARANGA_SLOTS: Final[int] = KSETRAJNA << VAMSI_HOLES  # 512

# Bytes per slot: 32 (24 header + 8 lifecycle)
SLOT_BYTES: Final[int] = 32

# Total chamber size: 512 × 32 = 16,384 bytes
CHAMBER_BYTES: Final[int] = ANTARANGA_SLOTS * SLOT_BYTES

# Max prana in uint32: GENESIS_PRANA × MALA = 13700 × 108 = 1,479,600
MAX_PRANA_U32: Final[int] = MAHA_QUANTUM * 100 * MALA

# Genesis prana: MAHA_QUANTUM × 100 = 13,700
GENESIS_PRANA_U32: Final[int] = MAHA_QUANTUM * 100

# Integrity full: 65535 (uint16 max, represents 1.0)
INTEGRITY_FULL: Final[int] = (KSETRAJNA << 16) - KSETRAJNA  # 65535

# Flag: is_active
FLAG_ACTIVE: Final[int] = KSETRAJNA  # bit 0

# Struct format for one slot (little-endian):
#   Header:    source(I) target(I) op(I) arcanam(I) atma(I) flags(I) = 24 bytes
#   Lifecycle: prana(I) integrity(H) cycle(H) = 8 bytes
#   Total: 32 bytes
_SLOT_FMT: Final[str] = "<IIIIII IHH"
_SLOT_SIZE: Final[int] = struct.calcsize(_SLOT_FMT)

# Verify slot size matches
assert _SLOT_SIZE == SLOT_BYTES, f"Slot size mismatch: {_SLOT_SIZE} != {SLOT_BYTES}"


# =============================================================================
# SHABDA SALT — Prabhupada's full acoustic fingerprint per Mahamantra position
# =============================================================================

_SHABDA_SALT: Optional[tuple] = None

# Neutral: rms=128(1.0×), varga=2(mid), f0=1200(~1.0×), cent=128(1.0×)
_NEUTRAL_SALT = (128, 2, 1200, 128)


def _get_shabda_salt() -> tuple:
    """Prabhupada's full acoustic salt per word position (0-15).

    Returns tuple of 16 entries, each (rms, varga, f0_x10, centroid_100).
    Lazy init. After first call: pure tuple lookup, O(1).
    """
    global _SHABDA_SALT
    if _SHABDA_SALT is not None:
        return _SHABDA_SALT
    try:
        from vibe_core.mahamantra.substrate.encoding.shabda_bridge import (
            prabhupada_salt,
            unpack_frame,
        )

        entries = []
        for p in range(WORDS):
            r0, v0, f0, c0 = unpack_frame(prabhupada_salt(p * 2))
            r1, v1, f1, c1 = unpack_frame(prabhupada_salt(p * 2 + 1))
            entries.append(
                (
                    (r0 + r1) // 2,
                    (v0 + v1) // 2,
                    (f0 + f1) // 2,
                    (c0 + c1) // 2,
                )
            )
        _SHABDA_SALT = tuple(entries)
    except Exception:
        _SHABDA_SALT = (_NEUTRAL_SALT,) * WORDS
    return _SHABDA_SALT


# =============================================================================
# CTYPES ZERO-COPY OVERLAY
# =============================================================================
# A C-struct mapped directly onto the bytearray. No unpack, no alloc.
# Reading slot.prana is a single pointer dereference into contiguous RAM.


class _CSlot(ctypes.LittleEndianStructure):
    """32-byte C-struct overlay. Same layout as _SLOT_FMT."""

    _fields_ = [
        ("source", ctypes.c_uint32),
        ("target", ctypes.c_uint32),
        ("operation", ctypes.c_uint32),
        ("arcanam", ctypes.c_uint32),
        ("atma", ctypes.c_uint32),
        ("flags", ctypes.c_uint32),
        ("prana", ctypes.c_uint32),
        ("integrity", ctypes.c_uint16),
        ("cycle", ctypes.c_uint16),
    ]


assert ctypes.sizeof(_CSlot) == SLOT_BYTES, f"CSlot size mismatch: {ctypes.sizeof(_CSlot)} != {SLOT_BYTES}"

_CSlotArray = _CSlot * ANTARANGA_SLOTS


# =============================================================================
# SLOT VIEW (Read-only snapshot, no allocation on hot path)
# =============================================================================


class SlotView(NamedTuple):
    """Lightweight read-only view of a slot. No Python object overhead on write path."""

    source: int
    target: int
    operation: int
    arcanam: int
    atma_nivedanam: int
    flags: int
    prana: int
    integrity: int  # uint16: 0-65535
    cycle: int


# =============================================================================
# ANTARANGA REGISTRY
# =============================================================================


class AntarangaRegistry:
    """
    The Inner Chamber — 512 slots × 32 bytes = 16 KB contiguous RAM.

    No Python objects in the hot path. No GC. No pointer indirection.
    Pure byte arithmetic. Like silicon reacting to voltage.

    Operations:
        get(slot) → SlotView          O(1) struct.unpack_from
        set(slot, ...)                O(1) struct.pack_into
        collide(slot, visitor_*)      O(1) in-place merge or presence
        apply_diw(slot, diw)          O(1) in-place transformation

    The outer SankirtanChamber wraps this for Python API compatibility.
    """

    __slots__ = ("_mem", "_slots")

    def __init__(self) -> None:
        """Allocate the chamber: one contiguous block of silence."""
        self._mem = bytearray(CHAMBER_BYTES)
        self._slots = _CSlotArray.from_buffer(self._mem)

    # =========================================================================
    # CORE: O(1) READ / WRITE
    # =========================================================================

    def get(self, slot: int) -> SlotView:
        """Read slot as SlotView. O(1). Zero-copy via ctypes overlay."""
        s = self._slots[slot]
        return SlotView(
            s.source,
            s.target,
            s.operation,
            s.arcanam,
            s.atma,
            s.flags,
            s.prana,
            s.integrity,
            s.cycle,
        )

    def set_slot(
        self,
        slot: int,
        source: int,
        target: int,
        operation: int,
        arcanam: int,
        atma_nivedanam: int,
        flags: int,
        prana: int,
        integrity: int,
        cycle: int,
    ) -> None:
        """Write full slot. O(1)."""
        offset = slot * SLOT_BYTES
        struct.pack_into(
            _SLOT_FMT,
            self._mem,
            offset,
            source,
            target,
            operation,
            arcanam,
            atma_nivedanam,
            flags,
            prana,
            integrity,
            cycle,
        )

    # =========================================================================
    # CORE: COLLISION (The Heart of Resonance)
    # =========================================================================

    def collide(
        self,
        slot: int,
        v_source: int,
        v_target: int,
        v_operation: int,
        v_arcanam: int,
        v_atma: int,
        v_prana: int,
        v_integrity: int,
        v_cycle: int,
    ) -> bool:
        """
        Visitor collides with resident at slot. In-place. O(1).

        Returns True if RESONANCE (merge), False if PRESENCE (new).

        Logic (mirrors MahaCellUnified.interact()):
            Resident prana == 0 → SILENCE → visitor takes slot (Presence)
            Resident prana > 0  → RESONANCE → merge (prana add, integrity avg)
        """
        s = self._slots[slot]

        # Read resident prana via ctypes (zero-copy)
        if s.prana == 0:
            # SILENCE → PRESENCE: visitor takes the slot (bulk write)
            offset = slot * SLOT_BYTES
            struct.pack_into(
                _SLOT_FMT,
                self._mem,
                offset,
                v_source,
                v_target,
                v_operation,
                v_arcanam,
                v_atma,
                FLAG_ACTIVE,
                v_prana,
                v_integrity,
                v_cycle,
            )
            return False

        # RESONANCE → MERGE: accumulate prana, average integrity
        new_prana = min(s.prana + v_prana, MAX_PRANA_U32)
        new_integrity = (s.integrity + v_integrity) // HALVES

        # Write back only the mutable lifecycle fields
        struct.pack_into("<IHH", self._mem, slot * SLOT_BYTES + 24, new_prana, new_integrity, s.cycle)
        return True

    # =========================================================================
    # CORE: APPLY DIW (The Reactor)
    # =========================================================================

    def apply_diw(self, slot: int, diw: int) -> None:
        """
        Apply Divine Instruction Word to slot. In-place. O(1).

        Mirrors SankirtanChamber._apply_diw() but operates on raw bytes.

        DIW format: 6-bit VENU | 9-bit VAMSI | 4-bit MURALI
        """
        from vibe_core.mahamantra.protocols._seed import (
            QUALITIES,
            SEVEN,
        )
        from vibe_core.mahamantra.protocols.diw import (
            CLUSTER_SHIFT,
            CONDITION_MASK,
            CONDITION_SHIFT,
            MURALI_MASK,
            MURALI_SHIFT,
            VAMSI_MASK,
            VAMSI_SHIFT,
            VENU_MASK,
            VENU_SHIFT,
        )

        s = self._slots[slot]

        # Read current lifecycle via ctypes (zero-copy)
        prana = s.prana
        if prana == 0:
            return  # Dead slot, nothing to transform

        integrity_u16 = s.integrity
        cycle = s.cycle

        # Decode DIW
        venu = (diw >> VENU_SHIFT) & VENU_MASK
        vamsi = (diw >> VAMSI_SHIFT) & VAMSI_MASK
        murali = (diw >> MURALI_SHIFT) & MURALI_MASK
        mode = (diw >> CLUSTER_SHIFT) & 0xF

        # Intensity from VENU (0.0 to 1.0 as fixed-point)
        intensity_fp = venu  # 0-63, we use integer arithmetic
        max_intensity = QUALITIES - KSETRAJNA  # 63

        # Name region from VAMSI
        vamsi_stride = (KSETRAJNA << VAMSI_HOLES) // 3  # 170
        name_region = min(vamsi // vamsi_stride, HALVES)  # 0=H, 1=K, 2=R

        # Phase from MURALI
        phase = murali % 4  # 0-3: GENESIS, DHARMA, KARMA, MOKSHA

        # Base delta (integer arithmetic, no floats)
        # base_delta = (7 + intensity * 7) * (mode + 1)
        # Using integer: (SEVEN + venu * SEVEN // 63) * (mode + 1)
        base_delta = (SEVEN + (intensity_fp * SEVEN) // max_intensity) * (mode + KSETRAJNA)

        # Shabda salt: Prabhupada's full acoustic fingerprint modulates resonance
        condition = (diw >> CONDITION_SHIFT) & CONDITION_MASK
        salt_rms, salt_varga, salt_f0, salt_cent = _get_shabda_salt()[condition]

        # RMS → base_delta (prana strength)
        base_delta = base_delta * (128 + salt_rms) // 256

        # F0 → intensity (integrity sensitivity): pitch modulates membrane response
        f0_norm = min(255, salt_f0 * 255 // 2400)
        intensity_fp = intensity_fp * (128 + f0_norm) // 256

        # Centroid → intensity (second factor): spectral brightness amplifies integrity
        cent_norm = min(255, salt_cent)
        intensity_fp = intensity_fp * (128 + cent_norm) // 256

        # Save cycle before phase block for varga modulation
        cycle_before = cycle

        # Phase-specific transformation (mirrors _apply_diw exactly)
        if phase == 0:  # GENESIS
            if name_region == 0:  # HARE
                prana += base_delta * HALVES
            elif name_region == 1:  # KRISHNA
                prana += base_delta
                integrity_u16 = min(
                    INTEGRITY_FULL, integrity_u16 + (intensity_fp * INTEGRITY_FULL) // (max_intensity * 100)
                )
            else:  # RAMA
                prana += base_delta
                cycle += KSETRAJNA

        elif phase == 1:  # DHARMA
            if name_region == 0:  # HARE
                prana = max(0, prana - base_delta)
            elif name_region == 1:  # KRISHNA
                integrity_u16 = min(
                    INTEGRITY_FULL, integrity_u16 + (intensity_fp * INTEGRITY_FULL) // (max_intensity * 50)
                )
            else:  # RAMA
                cycle += KSETRAJNA
                integrity_u16 = min(
                    INTEGRITY_FULL, integrity_u16 + (intensity_fp * INTEGRITY_FULL) // (max_intensity * 100)
                )

        elif phase == HALVES:  # KARMA
            prana = max(0, prana - base_delta)
            if name_region == 0:  # HARE
                cycle += KSETRAJNA
            elif name_region == 1:  # KRISHNA
                integrity_u16 = min(
                    INTEGRITY_FULL, integrity_u16 + (intensity_fp * INTEGRITY_FULL) // (max_intensity * 100)
                )
                cycle += KSETRAJNA
            else:  # RAMA
                cycle += HALVES

        else:  # MOKSHA
            prana = max(0, prana - base_delta)
            if name_region == 0:  # HARE
                integrity_u16 = max(0, integrity_u16 - (intensity_fp * INTEGRITY_FULL) // (max_intensity * 200))
            elif name_region == 1:  # KRISHNA
                integrity_u16 = min(
                    INTEGRITY_FULL, integrity_u16 + (intensity_fp * INTEGRITY_FULL) // (max_intensity * 100)
                )
            else:  # RAMA
                cycle += HALVES

        # Varga → cycle: articulation depth modulates progression
        # Throat (0) → 1.3×, mid (2) → 1.0×, lips (4) → 0.7×
        cycle_added = cycle - cycle_before
        if cycle_added > 0:
            varga_factor = 128 + (HALVES - salt_varga) * 20  # 0→168, 2→128, 4→88
            cycle = cycle_before + max(KSETRAJNA, cycle_added * varga_factor // 128)

        # Clamp prana
        prana = min(prana, MAX_PRANA_U32)

        # Write back lifecycle
        struct.pack_into("<IHH", self._mem, slot * SLOT_BYTES + 24, prana, integrity_u16, cycle)

    # =========================================================================
    # QUERY METHODS
    # =========================================================================

    def is_alive(self, slot: int) -> bool:
        """Check if slot has active cell. O(1). Zero-copy."""
        return self._slots[slot].prana > 0

    def prana_at(self, slot: int) -> int:
        """Read prana at slot. O(1). Zero-copy."""
        return self._slots[slot].prana

    def active_count(self) -> int:
        """Count active slots. O(N) but N=512 is small. Zero-copy."""
        slots = self._slots
        count = 0
        for i in range(ANTARANGA_SLOTS):
            if slots[i].prana > 0:
                count += KSETRAJNA
        return count

    def total_prana(self) -> int:
        """Sum of all prana in chamber. O(N). Zero-copy."""
        slots = self._slots
        total = 0
        for i in range(ANTARANGA_SLOTS):
            total += slots[i].prana
        return total

    def clear(self) -> None:
        """Wipe the chamber clean. O(1) — memset equivalent."""
        ctypes.memset(ctypes.addressof(self._slots), 0, CHAMBER_BYTES)

    @property
    def raw(self) -> memoryview:
        """Direct access to the contiguous memory. For advanced use."""
        return memoryview(self._mem)

    @property
    def size_bytes(self) -> int:
        """Total chamber size in bytes."""
        return CHAMBER_BYTES

    def __repr__(self) -> str:
        active = self.active_count()
        return f"<AntarangaRegistry: {active}/{ANTARANGA_SLOTS} slots, {CHAMBER_BYTES} bytes>"
