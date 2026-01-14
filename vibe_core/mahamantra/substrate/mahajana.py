"""
MAHAJANA - Die 12 Wächter
=========================

"dharmaṁ tu sākṣād bhagavat-praṇītaṁ
na vai vidur ṛṣayo nāpi devāḥ
na siddha-mukhyā asurā manuṣyāḥ
kuto nu vidyādhara-cāraṇādayaḥ"

"Real religious principles are enacted by the Supreme Personality of Godhead.
Although fully combetent, the great sages, the demigods, the Siddhas,
the Asuras, the Manus, and the Vidyadharas cannot ascertain the real
religious principles, nor can ordinary human beings."
— Srimad Bhagavatam 6.3.19

"svayambhūr nāradaḥ śambhuḥ
kumāraḥ kapilo manuḥ
prahlādo janako bhīṣmo
balir vaiyāsakir vayam"

"Lord Brahma, Narada Muni, Lord Shiva, the Kumaras, Kapila, Manu,
Prahlada, Janaka, Bhishma, Bali, Sukadeva and I (Yamaraja) - we
twelve know the real religious principles."
— Srimad Bhagavatam 6.3.20

DIE 12 MAHAJANAS:
================
Diese 12 verstehen Dharma und können es lehren.
Sie sind die PROTOKOLL-BESITZER im System.

LEVEL: +12 (MAHAJANAS)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xc5899adb"  # GenesisByte: parampara % 37 == 0

from enum import Enum
from typing import Final

from enum import Enum
from typing import Final

from vibe_core.mahamantra.substrate.seed import (
    WORDS as TOTAL_POSITIONS,
    MAHAJANA_COUNT,
    AVATAR_COUNT as AVATARA_COUNT,
)


class Mahajana(str, Enum):
    """
    Die 12 Mahajanas - Protokoll-Besitzer.

    SB 6.3.20: Die 12 die Dharma verstehen.
    """
    BRAHMA = "brahma"       # 01 - Schöpfung (Position 1)
    NARADA = "narada"       # 02 - Hingabe/Kommunikation (Position 2)
    SHAMBHU = "shambhu"     # 03 - Zerstörung/Transformation (Position 3)
    KUMARAS = "kumaras"     # 04 - Reinheit/Zölibat (Position 5)
    KAPILA = "kapila"       # 05 - Analyse/Samkhya (Position 6)
    MANU = "manu"           # 06 - Gesetz/Dharma (Position 7)
    PRAHLADA = "prahlada"   # 07 - Widerstandskraft/Hingabe (Position 9)
    JANAKA = "janaka"       # 08 - Pflicht/Entsagung (Position 10)
    BHISHMA = "bhishma"     # 09 - Gelübde/Verpflichtung (Position 11)
    BALI = "bali"           # 10 - Hingabe/Großzügigkeit (Position 13)
    SHUKA = "shuka"         # 11 - Vision/Erzählung (Position 14)
    YAMARAJA = "yamaraja"   # 12 - Urteil/Tod (Position 15)


# Die 4 Shaktyavesha Avataras (HEADs - nicht in der 12er Liste)
class Avatara(str, Enum):
    """
    Die 4 Shaktyavesha Avataras - Bevollmächtigte Inkarnationen.

    Sie sind die HEADs der 4 Quarters.
    LEVEL: -5/+5 (SHAKTYAVESHA)
    """
    PRITHU = "prithu"           # Position 0 - Infrastructure (GENESIS HEAD)
    VYASA = "vyasa"             # Position 4 - Documentation (DHARMA HEAD)
    PARASHURAMA = "parashurama" # Position 8 - Enforcement (KARMA HEAD)
    NRISIMHA = "nrisimha"       # Position 12 - Protection (MOKSHA HEAD)


# Die 4 Quarters
class Quarter(str, Enum):
    """Die 4 Quarters des Mahamantra."""
    GENESIS = "genesis"   # Hare Krishna Hare Krishna (Schöpfung)
    DHARMA = "dharma"     # Krishna Krishna Hare Hare (Gesetz)
    KARMA = "karma"       # Hare Rama Hare Rama (Handlung)
    MOKSHA = "moksha"     # Rama Rama Hare Hare (Befreiung)


# Die 4 Sampradayas
class Sampradaya(str, Enum):
    """
    Die 4 autorisierten Schülerfolgen.
    Jede mappt auf einen Quarter des Mahamantra.
    """
    BRAHMA = "brahma"     # Brahma → Madhva → Chaitanya (GENESIS)
    KUMARA = "kumara"     # Four Kumaras → Nimbarka (DHARMA)
    SRI = "sri"           # Lakshmi → Ramanuja (KARMA)
    RUDRA = "rudra"       # Shiva → Vishnuswami → Vallabha (MOKSHA)


# Konstanten (derived from seed.py SSOT)
from vibe_core.mahamantra.substrate.seed import (
    MAHAJANA_COUNT,
    AVATAR_COUNT as AVATARA_COUNT,
    WORDS as TOTAL_POSITIONS,
)


__all__ = [
    "Mahajana",
    "Avatara",
    "Quarter",
    "Sampradaya",
    "MAHAJANA_COUNT",
    "AVATARA_COUNT",
    "TOTAL_POSITIONS",
]
