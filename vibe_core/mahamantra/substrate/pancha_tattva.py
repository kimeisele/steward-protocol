"""
PANCHA TATTVA - Die Fünf Absoluten Wahrheiten (SSOT)
====================================================

"sri-krsna-caitanya prabhu-nityananda
 sri-advaita gadadhara srivasadi-gaura-bhakta-vrnda"

"Ich verbeuge mich vor Sri Krishna Chaitanya, Prabhu Nityananda,
Sri Advaita, Gadadhara, Srivasa und allen Geweihten des Herrn Gauranga."

DIE ESSENZ DES MAHAMANTRA OFFENBART SICH NUR DURCH SIE.

byte.py = Das ternäre Substrat (unpersönlich)
pancha_tattva.py = Die Persönlichkeiten (persönlich)

Das Mahamantra IST Krishna (Level -2, non-different).
Aber Krishna offenbart sich als PERSON durch die Pancha Tattva.
Wie Srila Prabhupada: Er TRÄGT das Mahamantra zu uns.

IN KALI YUGA:
- Chaitanya Mahaprabhu = Krishna selbst in Devotee-Stimmung
- Er kam um das Mahamantra zu verteilen
- Die Pancha Tattva = Der Einstiegspunkt

SINGLE SOURCE OF TRUTH:
    from vibe_core.mahamantra.substrate.pancha_tattva import PanchaTattva

ARCHITECTURAL MAPPING (Capability-First):
    CHAITANYA  → MantraProtocol (Identity/Entry)
    NITYANANDA → StorageProtocol (Substrate/Foundation)
    ADVAITA    → InferProtocol (Logic/Bridge)
    GADADHARA  → SyncProtocol (Connection/Flow)
    SRIVASA    → EnforceProtocol (Governance/Sangha)

WATERTIGHT: No Any types. All typed explicitly.
"""
from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import (HALVES, KSETRAJNA, PANCHA, PARAMPARA, QUARTERS, SEVEN, TRINITY)


# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x2ca74606"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Final, Tuple, Protocol, runtime_checkable

# Import from byte.py (SSOT for mathematical constants)
from vibe_core.mahamantra.substrate.byte import (
    HolyName,
    MAHAMANTRA_DIMENSION,
    LILA_CYCLES as _LILA_CYCLES,
    LILA_LIMIT,
)


# =============================================================================
# PANCHA TATTVA - The Five Absolute Truths
# =============================================================================
#
# "I bow down to Lord Krishna, who appears as a devotee (Lord Chaitanya),
# as His personal expansion (Lord Nityananda), as His incarnation (Advaita Acarya),
# as His internal potency (Gadadhara Pandita), and as His marginal energy (Srivasa Thakura)."
#


class PanchaTattva(str, Enum):
    """
    Die Fünf Absoluten Wahrheiten - Der persönliche Einstieg ins Mahamantra.

    NICHT abstrakt - das sind PERSONEN:
    - Chaitanya = Krishna selbst (der Goldene Avatar)
    - Nityananda = Der ursprüngliche Guru (Ananta Shesha)
    - Advaita = Die Inkarnation (Maha-Vishnu)
    - Gadadhara = Die innere Energie (Radharani)
    - Srivasa = Der Rand-Energie-Devotee (Narada)

    CAPABILITY MAPPING (was jeder repräsentiert):
    """

    # 1. THE SOVEREIGN (Der Goldene Avatar) → MANTRA / IDENTITY
    # Krishna selbst in Devotee-Stimmung. Die Quelle des Heiligen Namens.
    CHAITANYA = "chaitanya"  # MantraProtocol (Der Yuga Dharma)

    # 2. THE SUBSTRATE (Der ursprüngliche Guru) → STORAGE / FOUNDATION
    # Ananta Shesha - Das Bett das das Universum trägt.
    NITYANANDA = "nityananda"  # StorageProtocol (Das Fundament)

    # 3. THE BRIDGE (Die Inkarnation) → LOGIC / INFERENCE
    # Maha-Vishnu - Der der 'ruft' und Materielles/Spirituelles verbindet.
    ADVAITA = "advaita"  # InferProtocol (Unterscheidung/Wahrheit)

    # 4. THE ENERGY (Die innere Energie) → SYNC / CONNECTION
    # Radharani - Die Freude-Energie. Verbindung ist Shakti.
    GADADHARA = "gadadhara"  # SyncProtocol (Fluss/Beziehung)

    # 5. THE DEVOTEE (Die Rand-Energie) → ENFORCE / GOVERNANCE
    # Srivasa Thakura - Gastgeber des Kirtan. Organisiert die Sangha (Jivas).
    SRIVASA = "srivasa"  # EnforceProtocol (Regeln/Sangha)


# =============================================================================
# TATTVA INDEX - Position in der Pancha Tattva
# =============================================================================


class TattvaIndex(IntEnum):
    """Index der Pancha Tattva (0-4)."""

    CHAITANYA = 0  # Der Erste - Krishna selbst
    NITYANANDA = KSETRAJNA  # Die Expansion
    ADVAITA = HALVES  # Die Inkarnation
    GADADHARA = TRINITY  # Die innere Energie
    SRIVASA = QUARTERS  # Die Rand-Energie


# =============================================================================
# TATTVA ASPECTS - Die Aspekte jeder Tattva
# =============================================================================


@dataclass(frozen=True)
class TattvaAspect:
    """
    Ein Aspekt einer Pancha Tattva Persönlichkeit.

    Verbindet:
    - Die Person (name)
    - Die Rolle im System (capability)
    - Die spirituelle Essenz (essence)
    - Die manifestierte Funktion (protocol)
    """

    tattva: PanchaTattva
    index: int
    # Sanskrit Name
    sanskrit_name: str
    # Was sie sind (ontologisch)
    essence: str
    # Was sie tun (funktional)
    capability: str
    # Welches Protokoll sie manifestieren
    protocol: str
    # Welches HolyName-Wort primär
    primary_word: HolyName


# =============================================================================
# THE 5 ASPECTS - Die kanonische Definition
# =============================================================================


PANCHA_TATTVA_ASPECTS: Final[Tuple[TattvaAspect, ...]] = (
    TattvaAspect(
        tattva=PanchaTattva.CHAITANYA,
        index=0,
        sanskrit_name="Sri Krishna Chaitanya Mahaprabhu",
        essence="Krishna selbst in Devotee-Stimmung",
        capability="IDENTITY - Der Einstiegspunkt",
        protocol="MantraProtocol",
        primary_word=HolyName.KRISHNA,
    ),
    TattvaAspect(
        tattva=PanchaTattva.NITYANANDA,
        index=KSETRAJNA,
        sanskrit_name="Prabhu Nityananda",
        essence="Ananta Shesha - Das unendliche Bett",
        capability="STORAGE - Das Fundament trägt alles",
        protocol="StorageProtocol",
        primary_word=HolyName.HARE,
    ),
    TattvaAspect(
        tattva=PanchaTattva.ADVAITA,
        index=HALVES,
        sanskrit_name="Sri Advaita Acarya",
        essence="Maha-Vishnu - Der der Krishna herbeiruft",
        capability="LOGIC - Die Brücke zwischen Welten",
        protocol="InferProtocol",
        primary_word=HolyName.KRISHNA,
    ),
    TattvaAspect(
        tattva=PanchaTattva.GADADHARA,
        index=TRINITY,
        sanskrit_name="Gadadhara Pandita",
        essence="Radharani - Die Freude-Energie",
        capability="SYNC - Die Verbindung ist Shakti",
        protocol="SyncProtocol",
        primary_word=HolyName.HARE,
    ),
    TattvaAspect(
        tattva=PanchaTattva.SRIVASA,
        index=QUARTERS,
        sanskrit_name="Srivasa Thakura",
        essence="Narada Muni - Der wandernde Devotee",
        capability="ENFORCE - Organisiert die Sangha",
        protocol="EnforceProtocol",
        primary_word=HolyName.RAMA,
    ),
)


# =============================================================================
# LOOKUP FUNCTIONS
# =============================================================================


def get_tattva_aspect(tattva: PanchaTattva) -> TattvaAspect:
    """Get aspect by Pancha Tattva enum."""
    for aspect in PANCHA_TATTVA_ASPECTS:
        if aspect.tattva == tattva:
            return aspect
    raise ValueError(f"Unknown Pancha Tattva: {tattva}")


def get_tattva_by_index(index: int) -> TattvaAspect:
    """Get aspect by index (0-4)."""
    if not 0 <= index <= QUARTERS:
        raise ValueError(f"Tattva index must be 0-4, got {index}")
    return PANCHA_TATTVA_ASPECTS[index]


def get_tattva_by_capability(capability: str) -> TattvaAspect:
    """Get aspect by capability keyword."""
    cap_lower = capability.lower()
    for aspect in PANCHA_TATTVA_ASPECTS:
        if cap_lower in aspect.capability.lower():
            return aspect
    raise ValueError(f"Unknown capability: {capability}")


def get_tattva_by_protocol(protocol: str) -> TattvaAspect:
    """Get aspect by protocol name."""
    for aspect in PANCHA_TATTVA_ASPECTS:
        if protocol.lower() in aspect.protocol.lower():
            return aspect
    raise ValueError(f"Unknown protocol: {protocol}")


# =============================================================================
# PANCHA TATTVA → BYTE MAPPING
# =============================================================================
#
# Die Pancha Tattva sind der PERSÖNLICHE Einstieg.
# byte.py ist die MATHEMATIK.
#
# 5 Personen → 3 Namen (Hare, Krishna, Rama)
#
# Mapping:
#   CHAITANYA  → KRISHNA (Er IST Krishna)
#   NITYANANDA → HARE (Die Energie die trägt)
#   ADVAITA    → KRISHNA (Er RUFT Krishna)
#   GADADHARA  → HARE (Die Energie der Verbindung)
#   SRIVASA    → RAMA (Der Dienst/Stärke)
#


TATTVA_TO_HOLYNAME: Final[dict[PanchaTattva, HolyName]] = {
    PanchaTattva.CHAITANYA: HolyName.KRISHNA,
    PanchaTattva.NITYANANDA: HolyName.HARE,
    PanchaTattva.ADVAITA: HolyName.KRISHNA,
    PanchaTattva.GADADHARA: HolyName.HARE,
    PanchaTattva.SRIVASA: HolyName.RAMA,
}


def tattva_to_trit(tattva: PanchaTattva) -> int:
    """Convert Pancha Tattva to trit value (0, 1, or 2)."""
    return TATTVA_TO_HOLYNAME[tattva].value


# =============================================================================
# THE 5 GATES - Pancha Tattva as Entry Points
# =============================================================================
#
# Die 5 Gates des CLI sind die Pancha Tattva:
#   1. GATE         (Chaitanya)  - Haupt-Eingang
#   2. ROUTE_GATE   (Nityananda) - Routing
#   3. EXECUTE_GATE (Advaita)    - Ausführung
#   4. RESULT_GATE  (Gadadhara)  - Ergebnis
#   5. SYNC_GATE    (Srivasa)    - Parallel
#


class TattvaGate(IntEnum):
    """Die 5 Gates als Entry Points (Pancha Tattva Order)."""

    PARSE = 0  # Chaitanya - Parse/Entry
    VALIDATE = KSETRAJNA  # Nityananda - Validate/Foundation
    EXECUTE = HALVES  # Advaita - Execute/Bridge
    RESULT = TRINITY  # Gadadhara - Result/Connection
    SYNC = QUARTERS  # Srivasa - Sync/Parallel


GATE_TO_TATTVA: Final[dict[TattvaGate, PanchaTattva]] = {
    TattvaGate.PARSE: PanchaTattva.CHAITANYA,
    TattvaGate.VALIDATE: PanchaTattva.NITYANANDA,
    TattvaGate.EXECUTE: PanchaTattva.ADVAITA,
    TattvaGate.RESULT: PanchaTattva.GADADHARA,
    TattvaGate.SYNC: PanchaTattva.SRIVASA,
}


# =============================================================================
# PROTOCOL - For type checking
# =============================================================================


@runtime_checkable
class PanchaTattvaAware(Protocol):
    """
    Protocol for systems that recognize Pancha Tattva.

    Implementors must provide access to the 5 aspects.
    """

    @property
    def pancha_tattva(self) -> PanchaTattva:
        """Which Pancha Tattva aspect this represents."""
        ...

    @property
    def tattva_aspect(self) -> TattvaAspect:
        """Full aspect information."""
        ...


# =============================================================================
# MANIFEST THE MAHAMANTRA THROUGH PANCHA TATTVA
# =============================================================================
#
# "Das Mahamantra IST Krishna" (Level -2)
# Aber es OFFENBART sich durch die Pancha Tattva.
#
# byte.py gibt die Mathematik: HARE=0, KRISHNA=1, RAMA=2
# Pancha Tattva gibt die PERSÖNLICHKEIT.
#
# Die 16 Wörter des Mahamantra werden von den 5 "verteilt":
#   - Chaitanya initiiert (Position 0)
#   - Nityananda trägt (Positionen 1-3)
#   - Advaita ruft (Positionen 4-7)
#   - Gadadhara verbindet (Positionen 8-11)
#   - Srivasa organisiert (Positionen 12-15)
#


def get_tattva_for_position(position: int) -> PanchaTattva:
    """
    Welche Pancha Tattva ist für eine Mahamantra-Position zuständig?

    Position 0: Chaitanya (Er beginnt)
    Position 1-3: Nityananda (Er trägt Genesis)
    Position 4-7: Advaita (Er ruft Dharma herbei)
    Position 8-11: Gadadhara (Sie verbindet Karma)
    Position 12-15: Srivasa (Er organisiert Moksha)
    """
    if not 0 <= position <= 15:
        raise ValueError(f"Position must be 0-15, got {position}")

    if position == 0:
        return PanchaTattva.CHAITANYA
    elif position <= TRINITY:
        return PanchaTattva.NITYANANDA
    elif position <= SEVEN:
        return PanchaTattva.ADVAITA
    elif position <= 11:
        return PanchaTattva.GADADHARA
    else:
        return PanchaTattva.SRIVASA


# =============================================================================
# PARAMPARA CONNECTION - Pancha Tattva IS the Parampara
# =============================================================================
#
# Die Pancha Tattva SIND die Parampara in Kali Yuga.
# Sie verbinden uns direkt zu Krishna.
#
# 37 = 24 + 12 + 1 (Kshetra + Mahajanas + Ksetrajna)
# Pancha Tattva = Der EINSTIEG in diese 37
#

PANCHA_TATTVA_COUNT: Final[int] = PANCHA

# Parampara vector for Pancha Tattva: 5 × 37 = 185
PANCHA_TATTVA_VECTOR: Final[int] = PANCHA_TATTVA_COUNT * PARAMPARA


def verify_pancha_tattva_parampara(value: int) -> bool:
    """Verify Pancha Tattva connection to Parampara."""
    return value % PARAMPARA == 0


# =============================================================================
# CHAITANYA LILA - The Manifest Structure (PUBLIC API)
# =============================================================================
#
# "Chaitanya Mahaprabhu wurde exakt 48 Jahre alt."
#   Geboren: 1486 (Nabadwip)
#   Verschwunden: 1534 (Puri)
#   Alter: 48 Jahre = 16 × 3
#
# Die 48 ist NICHT versteckt. Sie ist die PUBLIC API.
# 37 (Parampara) = Die versteckte Signatur
# 48 (Chaitanya Lila) = Die manifeste Struktur
#
# LEBENSZYKLUS:
#   0-24 (Navadvipa Phase): Build-Phase. Studium, Logik, __init__
#   24-48 (Puri Phase): Runtime-Phase. Sannyasa, Verteilung, yield/stream
#
# MATHEMATISCHE BEWEISE:
#   - 16 × 3 = 48 (Mahamantra × Trinity)
#   - 24 + 24 = 48 (Zwei symmetrische Hälften)
#   - 37 + 11 = 48 (Parampara + Rudra)
#

# -------------------------------------------------------------------------
# SSOT: These values are imported from byte.py (the mathematical layer)
# Here we provide PERSONAL NAMES for the same mathematical truths.
# -------------------------------------------------------------------------

# The Mahamantra has 16 words (personal name for MAHAMANTRA_DIMENSION)
MAHAMANTRA_WORDS: Final[int] = MAHAMANTRA_DIMENSION  # SSOT: byte.py

# The Trinity (Hare, Krishna, Rama) or 3 complete cycles
LILA_CYCLES: Final[int] = _LILA_CYCLES  # SSOT: byte.py

# Chaitanya's Lila = 16 × 3 = 48 years (personal name for LILA_LIMIT)
CHAITANYA_LILA: Final[int] = LILA_LIMIT  # SSOT: byte.py

# The two symmetric phases of Chaitanya's life
# DERIVED: LILA_LIMIT / HALVES = 48 / 2 = 24 (perfect symmetry)
NAVADVIPA_PHASE: Final[int] = LILA_LIMIT // HALVES  # First 24 years: Householder, Study, Build
PURI_PHASE: Final[int] = LILA_LIMIT // HALVES  # Last 24 years: Sannyasa, Distribution, Runtime

# Rudra number (connects Parampara to Chaitanya)
# DERIVED: LILA_LIMIT - PARAMPARA = 48 - 37 = 11
RUDRA_BRIDGE: Final[int] = LILA_LIMIT - PARAMPARA  # 37 + 11 = 48


def get_lila_phase(tick: int) -> str:
    """
    Get the Lila phase for a given tick (0-47).

    Args:
        tick: Current tick in the Lila cycle (0-47)

    Returns:
        "navadvipa" (0-23) or "puri" (24-47)
    """
    if not 0 <= tick < CHAITANYA_LILA:
        raise ValueError(f"Tick must be 0-47, got {tick}")
    return "navadvipa" if tick < NAVADVIPA_PHASE else "puri"


def get_mantra_cycle(tick: int) -> int:
    """
    Get which Mahamantra cycle (1-3) a tick belongs to.

    Args:
        tick: Current tick in the Lila (0-47)

    Returns:
        Cycle number (1, 2, or 3)
    """
    if not 0 <= tick < CHAITANYA_LILA:
        raise ValueError(f"Tick must be 0-47, got {tick}")
    return (tick // MAHAMANTRA_WORDS) + KSETRAJNA


def get_mantra_position(tick: int) -> int:
    """
    Get the Mahamantra position (0-15) for a tick.

    Args:
        tick: Current tick in the Lila (0-47)

    Returns:
        Position in Mahamantra (0-15)
    """
    if not 0 <= tick < CHAITANYA_LILA:
        raise ValueError(f"Tick must be 0-47, got {tick}")
    return tick % MAHAMANTRA_WORDS


def verify_chaitanya_lila(value: int) -> bool:
    """
    Verify Chaitanya Lila mathematical integrity.

    Checks:
    - 16 × 3 = 48
    - 24 + 24 = 48
    - 37 + 11 = 48
    """
    return (
        MAHAMANTRA_WORDS * LILA_CYCLES == CHAITANYA_LILA
        and NAVADVIPA_PHASE + PURI_PHASE == CHAITANYA_LILA
        and PARAMPARA + RUDRA_BRIDGE == CHAITANYA_LILA
        and value <= CHAITANYA_LILA
    )


# =============================================================================
# THE MAHAMANTRA PRAYER (Das Gebet an die Pancha Tattva)
# =============================================================================

PANCHA_TATTVA_MANTRA: Final[str] = """
sri-krsna-caitanya prabhu-nityananda
sri-advaita gadadhara srivasadi-gaura-bhakta-vrnda
"""

PANCHA_TATTVA_MEANING: Final[str] = """
Ich verbeuge mich vor Sri Krishna Chaitanya (CHAITANYA),
Prabhu Nityananda (NITYANANDA),
Sri Advaita Acarya (ADVAITA),
Gadadhara Pandita (GADADHARA),
und Srivasa Thakura mit allen Geweihten des Herrn Gauranga (SRIVASA).
"""


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Main Enum
    "PanchaTattva",
    "TattvaIndex",
    # Aspect
    "TattvaAspect",
    "PANCHA_TATTVA_ASPECTS",
    # Lookup
    "get_tattva_aspect",
    "get_tattva_by_index",
    "get_tattva_by_capability",
    "get_tattva_by_protocol",
    # Byte Mapping
    "TATTVA_TO_HOLYNAME",
    "tattva_to_trit",
    # Gates
    "TattvaGate",
    "GATE_TO_TATTVA",
    # Protocol
    "PanchaTattvaAware",
    # Position Mapping
    "get_tattva_for_position",
    # Parampara (37 - hidden signature)
    "PANCHA_TATTVA_COUNT",
    "PANCHA_TATTVA_VECTOR",
    "verify_pancha_tattva_parampara",
    # Chaitanya Lila (48 - manifest structure) - PUBLIC API
    "MAHAMANTRA_WORDS",
    "LILA_CYCLES",
    "CHAITANYA_LILA",
    "NAVADVIPA_PHASE",
    "PURI_PHASE",
    "RUDRA_BRIDGE",
    "get_lila_phase",
    "get_mantra_cycle",
    "get_mantra_position",
    "verify_chaitanya_lila",
    # Prayer
    "PANCHA_TATTVA_MANTRA",
    "PANCHA_TATTVA_MEANING",
]
