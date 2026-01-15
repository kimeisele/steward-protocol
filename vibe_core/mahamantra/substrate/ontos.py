"""
ONTOS - Das Sein der Architektur (Level -1)
===========================================

"mayādhyakṣeṇa prakṛtiḥ sūyate sa-carācaram"
"This material nature is working under My direction." (BG 9.10)

DIE ONTOLOGISCHE WAHRHEITSTABELLE.
Zentralisiert. Deklarativ. Passiv.

Struktur:
1. 5 TATTVA GRUPPEN (The Dance / Pairs)
2. 16 MANIFESTATIONEN (Varna x Ashrama)
"""

from __future__ import annotations
from enum import Enum, IntEnum
from typing import Final, List, Tuple, Dict, NamedTuple

# =============================================================================
# THE 5 TATTVAS (The Personal Rulers of the Pairs)
# =============================================================================

class Tattva(str, Enum):
    CHAITANYA = "chaitanya"   # Pair: HARE KRISHNA (0-1, 2-3)
    ADVAITA = "advaita"       # Pair: KRISHNA KRISHNA (4-5)
    GADADHARA = "gadadhara"   # Pair: HARE HARE (6-7, 14-15)
    NITYANANDA = "nityananda" # Pair: HARE RAMA (8-9, 10-11)
    SRIVASA = "srivasa"       # Pair: RAMA RAMA (12-13)

# =============================================================================
# THE VARNA & ASHRAMA (Passive Signatures)
# =============================================================================

class Varna(IntEnum):
    BRAHMANA = 0
    KSHATRIYA = 1
    VAISHYA = 2
    SHUDRA = 3

class Ashrama(IntEnum):
    BRAHMACHARYA = 0
    GRIHASTHA = 1
    VANAPRASTHA = 2
    SANNYASA = 3

# =============================================================================
# THE 16 MANIFESTATIONS (The Dance Steps)
# =============================================================================

class Manifestation(NamedTuple):
    index: int
    guardian: str
    tattva: Tattva
    varna: Varna
    ashrama: Ashrama
    is_head: bool
    word: str

ONTOLOGY: Final[Tuple[Manifestation, ...]] = (
    # Pair 0-1 (HARE KRISHNA) -> CHAITANYA
    Manifestation(0, "prithu", Tattva.CHAITANYA, Varna.BRAHMANA, Ashrama.BRAHMACHARYA, True, "HARE"),
    Manifestation(1, "brahma", Tattva.CHAITANYA, Varna.BRAHMANA, Ashrama.GRIHASTHA, False, "KRISHNA"),
    # Pair 2-3 (HARE KRISHNA) -> CHAITANYA
    Manifestation(2, "narada", Tattva.CHAITANYA, Varna.BRAHMANA, Ashrama.VANAPRASTHA, False, "HARE"),
    Manifestation(3, "shambhu", Tattva.CHAITANYA, Varna.BRAHMANA, Ashrama.SANNYASA, False, "KRISHNA"),
    
    # Pair 4-5 (KRISHNA KRISHNA) -> ADVAITA
    Manifestation(4, "vyasa", Tattva.ADVAITA, Varna.KSHATRIYA, Ashrama.BRAHMACHARYA, True, "KRISHNA"),
    Manifestation(5, "kumaras", Tattva.ADVAITA, Varna.KSHATRIYA, Ashrama.GRIHASTHA, False, "KRISHNA"),
    # Pair 6-7 (HARE HARE) -> GADADHARA
    Manifestation(6, "kapila", Tattva.GADADHARA, Varna.KSHATRIYA, Ashrama.VANAPRASTHA, False, "HARE"),
    Manifestation(7, "manu", Tattva.GADADHARA, Varna.KSHATRIYA, Ashrama.SANNYASA, False, "HARE"),
    
    # Pair 8-9 (HARE RAMA) -> NITYANANDA
    Manifestation(8, "parashurama", Tattva.NITYANANDA, Varna.VAISHYA, Ashrama.BRAHMACHARYA, True, "HARE"),
    Manifestation(9, "prahlada", Tattva.NITYANANDA, Varna.VAISHYA, Ashrama.GRIHASTHA, False, "RAMA"),
    # Pair 10-11 (HARE RAMA) -> NITYANANDA
    Manifestation(10, "janaka", Tattva.NITYANANDA, Varna.VAISHYA, Ashrama.VANAPRASTHA, False, "HARE"),
    Manifestation(11, "bhishma", Tattva.NITYANANDA, Varna.VAISHYA, Ashrama.SANNYASA, False, "RAMA"),
    
    # Pair 12-13 (RAMA RAMA) -> SRIVASA
    Manifestation(12, "nrisimha", Tattva.SRIVASA, Varna.SHUDRA, Ashrama.BRAHMACHARYA, True, "RAMA"),
    Manifestation(13, "bali", Tattva.SRIVASA, Varna.SHUDRA, Ashrama.GRIHASTHA, False, "RAMA"),
    # Pair 14-15 (HARE HARE) -> GADADHARA
    Manifestation(14, "shuka", Tattva.GADADHARA, Varna.SHUDRA, Ashrama.VANAPRASTHA, False, "HARE"),
    Manifestation(15, "yamaraja", Tattva.GADADHARA, Varna.SHUDRA, Ashrama.SANNYASA, False, "HARE"),
)

# =============================================================================
# LOOKUP (O(1) Access)
# =============================================================================

BY_INDEX: Final[Dict[int, Manifestation]] = {m.index: m for m in ONTOLOGY}
BY_GUARDIAN: Final[Dict[str, Manifestation]] = {m.guardian: m for m in ONTOLOGY}
BY_TATTVA: Final[Dict[Tattva, List[Manifestation]]] = {}

for m in ONTOLOGY:
    if m.tattva not in BY_TATTVA:
        BY_TATTVA[m.tattva] = []
    BY_TATTVA[m.tattva].append(m)

def get_manifestation(key: int | str) -> Manifestation:
    if isinstance(key, int): return BY_INDEX[key]
    return BY_GUARDIAN[key.lower()]

def get_tattva_members(tattva: Tattva) -> List[Manifestation]:
    return BY_TATTVA.get(tattva, [])

__all__ = ["Tattva", "Varna", "Ashrama", "Manifestation", "ONTOLOGY", "get_manifestation", "get_tattva_members"]