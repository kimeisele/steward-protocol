"""
MAHAPROMPT PROTOCOL - Das Gesetz des Lotus
==========================================

"sri-krsna-caitanya prabhu-nityananda
 sri-advaita gadadhara srivasadi-gaura-bhakta-vrnda"

DIES IST GESETZ, NICHT DOKUMENTATION.

DER LOTUS SPRIESST:
==================
__init__.py = Chaitanya (0) = HARE = Ursprung
    |
    +-- genesis/   = Nityananda = Foundation (0-3)
    +-- dharma/    = Advaita = Bridge (4-7)
    +-- karma/     = Gadadhara = Flow (8-11)
    +-- moksha/    = Srivasa = Governance (12-15)

5 FRAGEN BEANTWORTEN ALLES:
===========================
1. chaitanya  - Was IST es? (Identity)
2. nityananda - Worauf RUHT es? (Foundation)
3. advaita    - Was VERBINDET es? (Bridge)
4. gadadhara  - Wie FLIESST es? (Flow)
5. srivasa    - Wer REGIERT es? (Governance)

FOLDER IS WIRING - DER LOTUS IST DIE STRUKTUR.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Final, Protocol, runtime_checkable, Dict, Tuple
from pathlib import Path


# =============================================================================
# PANCHA TATTVA - Die 5 Absoluten Wahrheiten ALS GESETZ
# =============================================================================

class PanchaTattva(IntEnum):
    """Die 5 - alles andere deriviert von hier."""
    CHAITANYA = 0   # Was IST es? (HARE - ruft)
    NITYANANDA = 1  # Worauf RUHT es? (Foundation)
    ADVAITA = 2     # Was VERBINDET es? (Bridge)
    GADADHARA = 3   # Wie FLIESST es? (Flow)
    SRIVASA = 4     # Wer REGIERT es? (Governance)


# =============================================================================
# DIE 5 FRAGEN - Jedes File muss diese beantworten
# =============================================================================

@dataclass(frozen=True)
class TattvaDeclaration:
    """
    Jedes File deklariert sich durch 5 Antworten.

    Paramatma (die Uberseele) kann diese lesen und eingreifen.
    """
    chaitanya: str    # Was IST es?
    nityananda: str   # Worauf RUHT es?
    advaita: str      # Was VERBINDET es?
    gadadhara: str    # Wie FLIESST es?
    srivasa: str      # Wer REGIERT es?

    def as_dict(self) -> Dict[str, str]:
        return {
            "chaitanya": self.chaitanya,
            "nityananda": self.nityananda,
            "advaita": self.advaita,
            "gadadhara": self.gadadhara,
            "srivasa": self.srivasa,
        }


# =============================================================================
# QUARTER MAPPING - 5 auf 4 Takte
# =============================================================================
#
# Chaitanya + Nityananda = GENESIS (1 + 3 = 4)
# Advaita = DHARMA (4)
# Gadadhara = KARMA (4)
# Srivasa = MOKSHA (4)
#
# 5 Tattvas verteilen 16 Positionen auf 4 Quarters.

class Quarter(IntEnum):
    """Die 4 Takte - 5 Tattvas verteilen sie."""
    GENESIS = 0   # Chaitanya (0) + Nityananda (1-3)
    DHARMA = 1    # Advaita (4-7)
    KARMA = 2     # Gadadhara (8-11)
    MOKSHA = 3    # Srivasa (12-15)


QUARTER_NAMES: Final[Tuple[str, ...]] = ("genesis", "dharma", "karma", "moksha")

TATTVA_TO_QUARTER: Final[Dict[PanchaTattva, Quarter]] = {
    PanchaTattva.CHAITANYA: Quarter.GENESIS,
    PanchaTattva.NITYANANDA: Quarter.GENESIS,
    PanchaTattva.ADVAITA: Quarter.DHARMA,
    PanchaTattva.GADADHARA: Quarter.KARMA,
    PanchaTattva.SRIVASA: Quarter.MOKSHA,
}

# Positionen pro Tattva
TATTVA_POSITIONS: Final[Dict[PanchaTattva, Tuple[int, ...]]] = {
    PanchaTattva.CHAITANYA: (0,),           # Der Ursprung - Position 0
    PanchaTattva.NITYANANDA: (1, 2, 3),     # Foundation - Positionen 1-3
    PanchaTattva.ADVAITA: (4, 5, 6, 7),     # Bridge - Positionen 4-7
    PanchaTattva.GADADHARA: (8, 9, 10, 11), # Flow - Positionen 8-11
    PanchaTattva.SRIVASA: (12, 13, 14, 15), # Governance - Positionen 12-15
}


def get_tattva_for_position(position: int) -> PanchaTattva:
    """Welche Tattva regiert diese Position?"""
    if position == 0:
        return PanchaTattva.CHAITANYA
    elif position <= 3:
        return PanchaTattva.NITYANANDA
    elif position <= 7:
        return PanchaTattva.ADVAITA
    elif position <= 11:
        return PanchaTattva.GADADHARA
    else:
        return PanchaTattva.SRIVASA


def get_quarter_for_position(position: int) -> Quarter:
    """Welches Quarter fur diese Position?"""
    return Quarter(position // 4)


# =============================================================================
# FOLDER IS WIRING - Der Lotus als Struktur
# =============================================================================

LOTUS_STRUCTURE: Final[Dict[str, PanchaTattva]] = {
    "__init__.py": PanchaTattva.CHAITANYA,  # Ursprung
    "genesis": PanchaTattva.NITYANANDA,      # Foundation
    "dharma": PanchaTattva.ADVAITA,          # Bridge
    "karma": PanchaTattva.GADADHARA,         # Flow
    "moksha": PanchaTattva.SRIVASA,          # Governance
    "substrate": PanchaTattva.NITYANANDA,    # Foundation (SSOT)
}


def get_tattva_for_path(path: Path) -> PanchaTattva:
    """Welche Tattva regiert diesen Pfad?"""
    parts = path.parts

    # Check folder names
    for part in parts:
        if part in LOTUS_STRUCTURE:
            return LOTUS_STRUCTURE[part]

    # Default: alles spriesst aus Chaitanya
    return PanchaTattva.CHAITANYA


# =============================================================================
# PROTOCOL - Watertight Interface
# =============================================================================

@runtime_checkable
class MahapromptAware(Protocol):
    """
    Jedes System das dem Lotus folgt implementiert dies.

    Die 5 Fragen mussen beantwortet werden.
    """

    @property
    def tattva(self) -> TattvaDeclaration:
        """Die 5 Antworten dieses Systems."""
        ...

    @property
    def position(self) -> int:
        """Position im Mahamantra (0-15)."""
        ...

    @property
    def quarter(self) -> Quarter:
        """Quarter (genesis/dharma/karma/moksha)."""
        ...


# =============================================================================
# PARAMATMA - Die Uberseele die alles sieht
# =============================================================================

class Paramatma:
    """
    Der Observer der uberall Zugriff hat.

    Kann die 5 Fragen jedes Files lesen.
    Kann eingreifen wo notig.
    """

    @staticmethod
    def read_declaration(file_path: Path) -> TattvaDeclaration | None:
        """Liest __tattva__ aus einem File."""
        try:
            import ast
            content = file_path.read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__tattva__":
                            if isinstance(node.value, ast.Dict):
                                d = {}
                                for k, v in zip(node.value.keys, node.value.values):
                                    if isinstance(k, ast.Constant) and isinstance(v, ast.Constant):
                                        d[k.value] = v.value
                                if all(k in d for k in ["chaitanya", "nityananda", "advaita", "gadadhara", "srivasa"]):
                                    return TattvaDeclaration(**d)
        except Exception:
            pass
        return None

    @staticmethod
    def get_tattva(file_path: Path) -> PanchaTattva:
        """Welche Tattva regiert dieses File?"""
        return get_tattva_for_path(file_path)

    @staticmethod
    def verify_lotus(root: Path) -> Dict[str, bool]:
        """Verifiziert die Lotus-Struktur."""
        results = {}
        for folder in ["genesis", "dharma", "karma", "moksha", "substrate"]:
            folder_path = root / folder
            results[folder] = folder_path.exists() and folder_path.is_dir()
        return results


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Pancha Tattva
    "PanchaTattva",
    "TattvaDeclaration",
    # Quarter
    "Quarter",
    "QUARTER_NAMES",
    "TATTVA_TO_QUARTER",
    "TATTVA_POSITIONS",
    # Functions
    "get_tattva_for_position",
    "get_quarter_for_position",
    "get_tattva_for_path",
    # Lotus Structure
    "LOTUS_STRUCTURE",
    # Protocol
    "MahapromptAware",
    # Paramatma
    "Paramatma",
]
