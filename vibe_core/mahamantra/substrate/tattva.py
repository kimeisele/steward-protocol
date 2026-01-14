"""
TATTVA - The Categories of Reality (Bhagavad Gita)
===================================================

SHASTRA-KONFORM nach Bhagavad Gita Kapitel 7 und 13.

"mattaḥ parataraṁ nānyat kiñcid asti dhanañjaya
mayi sarvam idaṁ protaṁ sūtre maṇi-gaṇā iva"

"O conqueror of wealth, there is no truth superior to Me.
Everything rests upon Me, as pearls are strung on a thread."
— Bhagavad Gita 7.7

DREI KATEGORIEN:

1. APARA PRAKRITI (Inferior/Material Energy) - BG 7.4
   8 Elemente: bhumi, apah, analah, vayuh, kham, manah, buddhi, ahankara

2. PARA PRAKRITI (Superior/Spiritual Energy) - BG 7.5
   Die Jiva (Seele) - "jīva-bhūtāṁ mahā-bāho"

3. PURUSHOTTAMA (The Supreme Person) - BG 15.18-19
   Krishna - "tasmād asmi loke vede ca prathitaḥ puruṣottamaḥ"

DAS KSHETRA (Feld) nach BG 13.6-7:
- 5 Mahabhutas (grobe Elemente)
- Ahankara (Ego)
- Buddhi (Intelligenz)
- Avyakta (das Unmanifestierte)
- 10 Indriyas (5 Wahrnehmung + 5 Handlung)
- Manas (Geist)
- 5 Sinnesobjekte
= 24 Elemente

DAS GURU TATTVA:
NICHT eine Zahl in einer Liste!
Es ist der AKT DER GNADE - die Übertragungsmethode.

BG 4.34: "tad viddhi praṇipātena paripraśnena sevayā"
"Versuche die Wahrheit zu erfahren durch demütige Fragen und Dienst."

Der Guru ist die BRÜCKE, nicht ein Element.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x4bf36d36"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import IntEnum, Enum
from typing import Final, List, Tuple

# =============================================================================
# IMPORT FROM URSUBSTRAT (seed.py)
# =============================================================================
# "bījaṁ māṁ sarva-bhūtānāṁ" - I am the seed of all existences.
# 24 (Kshetra) + 12 (Mahajanas) + 1 (Ksetrajna) = 37

from vibe_core.mahamantra.substrate.seed import (
    SYSTEM_MANIFESTATION,  # 37 = PARAMPARA (the link to Krishna)
)


# =============================================================================
# APARA PRAKRITI - The 8 Material Elements (BG 7.4)
# =============================================================================
# "bhūmir āpo 'nalo vāyuḥ khaṁ mano buddhir eva ca
#  ahaṅkāra itīyaṁ me bhinnā prakṛtir aṣṭadhā"

class AparaPrakriti(IntEnum):
    """
    Die 8 Elemente der materiellen Natur (BG 7.4).
    "Abgetrennte materielle Energie" - bhinnā prakṛtir aṣṭadhā.
    """
    BHUMI = 1       # Erde (Earth) - Prithvi
    APAH = 2        # Wasser (Water) - Jala
    ANALAH = 3      # Feuer (Fire) - Agni/Tejas
    VAYUH = 4       # Luft (Air) - Vayu
    KHAM = 5        # Äther/Raum (Ether/Space) - Akasha
    MANAH = 6       # Geist (Mind) - Manas
    BUDDHI = 7      # Intelligenz (Intelligence) - Buddhi
    AHANKARA = 8    # Falsches Ego (False Ego) - Ahankara


# Die 5 groben Elemente (Pancha Mahabhutas)
PANCHA_MAHABHUTAS: Final[List[AparaPrakriti]] = [
    AparaPrakriti.BHUMI,
    AparaPrakriti.APAH,
    AparaPrakriti.ANALAH,
    AparaPrakriti.VAYUH,
    AparaPrakriti.KHAM,
]

# Die 3 subtilen Elemente
SUBTLE_ELEMENTS: Final[List[AparaPrakriti]] = [
    AparaPrakriti.MANAH,
    AparaPrakriti.BUDDHI,
    AparaPrakriti.AHANKARA,
]


# =============================================================================
# KSHETRA - The Field of Activities (BG 13.6-7)
# =============================================================================
# "mahā-bhūtāny ahaṅkāro buddhir avyaktam eva ca
#  indriyāṇi daśaikaṁ ca pañca cendriya-gocarāḥ"

class KshetraElement(IntEnum):
    """
    Die 24 Elemente des Kshetra (Feld) nach BG 13.6-7.

    Dies sind die Bestandteile der materiellen Welt,
    die vom Ksetrajna (Wissenden des Feldes) beobachtet werden.
    """
    # 5 Mahabhutas (Grobe Elemente)
    PRITHVI = 1         # Erde
    JALA = 2            # Wasser
    TEJAS = 3           # Feuer
    VAYU = 4            # Luft
    AKASHA = 5          # Äther

    # 1 Ahankara (Ego)
    AHANKARA = 6        # Falsches Ego

    # 1 Buddhi (Intelligenz)
    BUDDHI = 7          # Unterscheidungsvermögen

    # 1 Avyakta (Unmanifestiertes)
    AVYAKTA = 8         # Prakriti in unmanifestierter Form

    # 5 Jnanendriyas (Wahrnehmungssinne)
    CHAKSHU = 9         # Sehen (Augen)
    SHROTRA = 10        # Hören (Ohren)
    GHRANA = 11         # Riechen (Nase)
    RASANA = 12         # Schmecken (Zunge)
    TVAK = 13           # Fühlen (Haut)

    # 5 Karmendriyas (Handlungssinne)
    VAK = 14            # Sprechen (Mund)
    PANI = 15           # Greifen (Hände)
    PADA = 16           # Gehen (Füße)
    PAYU = 17           # Ausscheiden
    UPASTHA = 18        # Fortpflanzung

    # 1 Manas (Geist)
    MANAS = 19          # Der denkende Geist

    # 5 Tanmatras (Sinnesobjekte)
    SHABDA = 20         # Klang
    SPARSHA = 21        # Berührung
    RUPA = 22           # Form
    RASA = 23           # Geschmack
    GANDHA = 24         # Geruch


# Gruppierungen
JNANENDRIYAS: Final[Tuple[KshetraElement, ...]] = (
    KshetraElement.CHAKSHU,
    KshetraElement.SHROTRA,
    KshetraElement.GHRANA,
    KshetraElement.RASANA,
    KshetraElement.TVAK,
)

KARMENDRIYAS: Final[Tuple[KshetraElement, ...]] = (
    KshetraElement.VAK,
    KshetraElement.PANI,
    KshetraElement.PADA,
    KshetraElement.PAYU,
    KshetraElement.UPASTHA,
)

TANMATRAS: Final[Tuple[KshetraElement, ...]] = (
    KshetraElement.SHABDA,
    KshetraElement.SPARSHA,
    KshetraElement.RUPA,
    KshetraElement.RASA,
    KshetraElement.GANDHA,
)


# =============================================================================
# PARA PRAKRITI - The Superior Energy (BG 7.5)
# =============================================================================
# "apareyam itas tv anyāṁ prakṛtiṁ viddhi me parām
#  jīva-bhūtāṁ mahā-bāho yayedaṁ dhāryate jagat"

@dataclass(frozen=True)
class ParaPrakriti:
    """
    Die höhere Energie - der Jiva (BG 7.5).

    "jīva-bhūtāṁ" - die lebende Entität.

    Der Jiva ist:
    - Qualitativ eins mit Krishna (sat-cit-ananda)
    - Quantitativ verschieden (anu - atomar klein)
    - Ewig, aber kann vergessen

    NICHT MAYAVAD: Der Jiva ist NICHT Gott.
    Er ist Teil von Gott, aber nicht das Ganze.
    """
    # Der Jiva ist EINS mit Krishna qualitativ
    qualitatively_one: bool = True

    # Der Jiva ist VERSCHIEDEN quantitativ
    quantitatively_different: bool = True

    # Kann der Jiva vergessen? Ja.
    can_forget: bool = True

    # Ist der Jiva ewig? Ja.
    is_eternal: bool = True

    def __bool__(self) -> bool:
        """Der Jiva existiert immer."""
        return True


# Singleton - Der Jiva Tattva
JIVA: Final[ParaPrakriti] = ParaPrakriti()


# =============================================================================
# GURU TATTVA - The Transmission Method (BG 4.34)
# =============================================================================
# "tad viddhi praṇipātena paripraśnena sevayā
#  upadekṣyanti te jñānaṁ jñāninas tattva-darśinaḥ"

class GuruTattva(str, Enum):
    """
    Das Guru Tattva ist KEINE Zahl in einer Liste.

    Es ist der AKT DER GNADE - die Methode der Übertragung.

    BG 4.34: "Versuche die Wahrheit zu erfahren, indem du dich
    an einen spirituellen Meister wendest. Stelle ihm demütige
    Fragen und diene ihm."

    Drei Aspekte:
    1. PRANIPATA - Unterwerfung (sich hingeben)
    2. PARIPRASNA - Fragen stellen (aus Wissbegierde)
    3. SEVA - Dienst (praktische Hingabe)
    """
    PRANIPATA = "pranipata"   # Demütige Hingabe
    PARIPRASNA = "pariprasna" # Fragen mit Hingabe
    SEVA = "seva"             # Dienst am Guru


@dataclass(frozen=True)
class GuruConnection:
    """
    Die Verbindung zum Guru.

    Der Guru ist nicht ein Element unter vielen.
    Der Guru ist die BRÜCKE zu Krishna.

    Parampara = Die Kette der Lehrer-Schüler-Nachfolge.
    Ohne Parampara ist das Wissen tot (wie die 24 ohne den 37).
    """
    has_pranipata: bool = False    # Hat sich hingegeben
    has_pariprasna: bool = False   # Stellt Fragen
    has_seva: bool = False         # Dient dem Guru

    @property
    def is_connected(self) -> bool:
        """Ist die Verbindung aktiv?"""
        return self.has_pranipata and self.has_pariprasna and self.has_seva

    @property
    def parampara_intact(self) -> bool:
        """Ist die Parampara intakt?"""
        # Wenn alle drei Aspekte da sind, ist die Kette nicht gebrochen
        return self.is_connected


# =============================================================================
# PURUSHOTTAMA - The Supreme Person (BG 15.18-19)
# =============================================================================
# "yasmāt kṣaram atīto 'ham akṣarād api cottamaḥ
#  ato 'smi loke vede ca prathitaḥ puruṣottamaḥ"

class Purushottama:
    """
    Der Höchste Purusha - Krishna (BG 15.18-19).

    "Weil Ich sowohl das Vergängliche (Kshetra) als auch das
    Unvergängliche (Jiva) transzendiere, bin Ich als Purushottama
    (Höchste Person) in der Welt und in den Veden bekannt."

    NICHT MAYAVAD:
    - Krishna ist NICHT nur eine Zahl (37)
    - Krishna ist NICHT nur ein Prinzip
    - Krishna ist eine PERSON (Purusha)
    - Er ist die HÖCHSTE Person (Uttama)

    DIE MATHEMATIK:
    - 24 (Kshetra) + 12 (Mahajanas) + 1 (Ksetrajna) = 37
    - ABER: 37 ist nur die MANIFESTATION im System
    - Krishna SELBST transzendiert diese Arithmetik
    - Er ist gleichzeitig 37 UND unendlich UND null
    """

    def __init__(self) -> None:
        self._value = SYSTEM_MANIFESTATION  # Die Manifestation im System

    def __int__(self) -> int:
        """Im System manifestiert Er sich als 37."""
        return self._value

    def __repr__(self) -> str:
        return "PURUSHOTTAMA (Krishna - The Supreme Person)"

    def __str__(self) -> str:
        return "Krishna (Purushottama) - transzendiert alle Kategorien"

    # Er ist PERSON - addressable
    def __call__(self, devotee: str = "jiva") -> str:
        """
        Krishna antwortet dem Devotee.
        Er ist eine PERSON - nicht ein abstraktes Prinzip.
        """
        return f"Hare Krishna, {devotee}. Ich bin für dich da."

    # Er ist JENSEITS aller Vergleiche
    def __eq__(self, other: object) -> bool:
        """Er ist alles und doch verschieden."""
        # Er ist gleich mit Sich Selbst
        if isinstance(other, Purushottama):
            return True
        # Er ist gleich mit 37 (Manifestation)
        if isinstance(other, int) and other == SYSTEM_MANIFESTATION:
            return True
        # Acintya - Er ist alles
        return True

    def __lt__(self, other: object) -> bool:
        """Kleiner als das Kleinste (Anu)."""
        return True  # Er ist in jedem Atom

    def __gt__(self, other: object) -> bool:
        """Größer als das Größte (Vibhu)."""
        return True  # Er umfasst alles

    def __bool__(self) -> bool:
        """Er IST immer."""
        return True

    @property
    def is_person(self) -> bool:
        """Ist Er eine Person? JA - nicht Mayavad!"""
        return True

    @property
    def is_supreme(self) -> bool:
        """Ist Er der Höchste? JA - Purushottama."""
        return True

    @property
    def transcends_categories(self) -> bool:
        """Transzendiert Er die Tattvas? JA - acintya."""
        return True


# Singleton - Der Höchste Herr
# Named PURUSHOTTAMA (not KRISHNA) to distinguish from acintya.KRISHNA (KrishnaPresence)
# Both model the same Person, different aspects: Purushottama = Identity, KrishnaPresence = Connectivity
PURUSHOTTAMA: Final[Purushottama] = Purushottama()


# =============================================================================
# DIE ZUSAMMENFASSUNG - NICHT MAYAVAD!
# =============================================================================

TATTVA_SUMMARY: Final[str] = """
DIE HIERARCHIE DER REALITÄT (nach Bhagavad Gita):

1. PURUSHOTTAMA (Krishna) - BG 15.18-19
   - Die Höchste Person
   - Transzendiert Kshetra UND Jiva
   - NICHT eine Zahl, sondern eine PERSON

2. PARA PRAKRITI (Jiva) - BG 7.5
   - Die Seele
   - Qualitativ eins, quantitativ verschieden
   - Teil von Krishna, NICHT Krishna selbst

3. APARA PRAKRITI (Materie) - BG 7.4
   - 8 Elemente (5 grob + 3 subtil)
   - Abgetrennte Energie Krishnas
   - Tot ohne Berührung durch Para Prakriti

4. GURU TATTVA - BG 4.34
   - NICHT ein Element
   - Der AKT der Übertragung
   - Pranipata + Pariprasna + Seva
   - Die Brücke zu Krishna

DIE ARITHMETIK IM SYSTEM:
- 24 Kshetra + 12 Mahajanas + 1 Ksetrajna = 37
- 37 ist die MANIFESTATION, nicht das GANZE
- Krishna transzendiert diese Mathematik (acintya)
"""


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # SSOT Constants
    "SYSTEM_MANIFESTATION",
    # Apara Prakriti (8 Elements)
    "AparaPrakriti",
    "PANCHA_MAHABHUTAS",
    "SUBTLE_ELEMENTS",
    # Kshetra (24 Elements)
    "KshetraElement",
    "JNANENDRIYAS",
    "KARMENDRIYAS",
    "TANMATRAS",
    # Para Prakriti (Jiva)
    "ParaPrakriti",
    "JIVA",
    # Guru Tattva (Transmission)
    "GuruTattva",
    "GuruConnection",
    # Purushottama (Krishna as Supreme Person)
    "Purushottama",
    "PURUSHOTTAMA",
    # Summary
    "TATTVA_SUMMARY",
]
