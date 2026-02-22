#!/usr/bin/env python3
"""
CLEAN ROOM EXTRACTION - Vibration Signatures from Scripture
============================================================

"nāma cintāmaṇiḥ kṛṣṇaś caitanya-rasa-vigrahaḥ"
"The Holy Name is a transcendental touchstone."

PURPOSE:
========
Extract VIBRATION SIGNATURES from scripture, NOT TEXT.
The result is mathematically unangreifbar (legally safe).

WHAT WE EXTRACT:
================
- verse_id: "BG.18.66" (reference, not content)
- phonetic_key: tuple of PhoneticClass (vibration pattern)
- resonance_vector: (HARE, KRISHNA, RAMA) resonance values
- guna_seed: Intent classification (TAMAS/RAJAS/SATTVA/SUDDHA)
- attractor: MahaAlgorithm attractor value

WHAT WE DO NOT STORE:
=====================
- Sanskrit text (copyright)
- Translation text (copyright)
- Purport text (copyright)

AFTER EXTRACTION:
=================
1. Save resonance_index.json (only signatures)
2. DELETE source database
3. System can route by resonance, return POINTER not content

This is the "Radio Model" - we transmit frequencies, not text.

Usage:
    python clean_room_extraction.py /path/to/vedabase.db /output/resonance_index.json
"""

# === MAHAJANA DECLARATION ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x4f35578d"  # GenesisByte: parampara % 37 == 0

import json
import sqlite3
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Final, List, Optional, Tuple
import sys

# Use existing infrastructure - NO REIMPLEMENTATION!
from vibe_core.protocols.substrate.resonance import (
    PhoneticClass,
    to_phonetic_key,
    calculate_resonance,
    HolyName,
)
from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    MAHA_QUANTUM,
    WORDS,
)
from vibe_core.mahamantra_research.dharma import MahaResonator

# Global resonator instance (reuse, don't recreate)
_RESONATOR = MahaResonator(mod_space=MAHA_QUANTUM)


# =============================================================================
# DATA TYPES (What we extract - NO TEXT)
# =============================================================================


@dataclass
class VerseSignature:
    """
    Vibration signature of a verse.

    Contains ONLY mathematical/phonetic data.
    NO copyrighted text content.
    """

    # Reference (not content)
    verse_id: str  # e.g., "BG.18.66"
    chapter: int
    verse: str

    # Vibration signature
    phonetic_hash: str  # Hash of phonetic key (not the text!)
    phonetic_length: int  # Number of phonetic units

    # Resonance vector (3D)
    resonance_hare: float
    resonance_krishna: float
    resonance_rama: float
    dominant_name: str  # Which Holy Name resonates most

    # Guna classification
    guna: str  # "tamas", "rajas", "sattva", "suddha"
    guna_seed: int  # 32-bit seed

    # MahaAlgorithm attractor
    attractor: int  # Attractor in mod 137 space
    position: int  # Position in 16-word Mahamantra (0-15)


@dataclass
class ResonanceIndex:
    """
    Complete resonance index for scripture.

    This is the ONLY artifact we keep.
    Source database is DELETED after extraction.
    """

    book_code: str  # e.g., "BG"
    total_verses: int
    total_chapters: int

    # Statistics
    avg_resonance_hare: float
    avg_resonance_krishna: float
    avg_resonance_rama: float

    # Chapter-level signatures
    chapter_signatures: Dict[int, dict]

    # Verse-level signatures
    verses: List[dict]

    # Metadata
    extraction_version: str
    extraction_method: str


# =============================================================================
# EXTRACTION FUNCTIONS
# =============================================================================


def compute_guna(text: str) -> Tuple[str, int]:
    """
    Classify text into guna (mode) and compute seed.

    Uses keyword detection (simplified MahaCompression).
    Returns (guna_name, seed).
    """
    text_lower = text.lower()

    # Keywords for each guna
    tamas_keywords = ["error", "fail", "crash", "death", "fear", "ignorance", "darkness"]
    rajas_keywords = ["desire", "passion", "action", "work", "attachment", "fruit"]
    sattva_keywords = ["knowledge", "wisdom", "peace", "truth", "good", "pure"]
    suddha_keywords = ["surrender", "devotion", "love", "krishna", "transcendental"]

    scores = {
        "tamas": sum(1 for kw in tamas_keywords if kw in text_lower),
        "rajas": sum(1 for kw in rajas_keywords if kw in text_lower),
        "sattva": sum(1 for kw in sattva_keywords if kw in text_lower),
        "suddha": sum(1 for kw in suddha_keywords if kw in text_lower),
    }

    # Compute seed (hash-based)
    seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)

    # Find dominant guna (priority: suddha > sattva > rajas > tamas)
    if scores["suddha"] > 0:
        return "suddha", seed
    if scores["sattva"] > 0:
        return "sattva", seed
    if scores["rajas"] > 0:
        return "rajas", seed
    if scores["tamas"] > 0:
        return "tamas", seed

    return "sattva", seed  # Default to sattva


def compute_attractor(seed: int) -> int:
    """
    Find attractor in mod 137 space using MahaResonator.

    USES EXISTING INFRASTRUCTURE - no reimplementation!
    """
    result = _RESONATOR.find_attractor(seed)
    return result.attractor


def extract_verse_signature(
    verse_id: str,
    chapter: int,
    verse: str,
    sanskrit: str,
    translation: str,
) -> VerseSignature:
    """
    Extract vibration signature from a verse.

    Uses EXISTING infrastructure (resonance.py).
    Does NOT store any text content.
    """
    # Combine texts for phonetic analysis
    combined = f"{sanskrit} {translation}"

    # Compute phonetic key using existing infrastructure
    try:
        phonetic_key = to_phonetic_key(combined)
        phonetic_hash = hashlib.sha256(str(phonetic_key).encode()).hexdigest()[:16]
        phonetic_length = len(phonetic_key)
    except Exception:
        phonetic_hash = "unknown"
        phonetic_length = 0

    # Compute resonance with Holy Names
    try:
        res_hare = calculate_resonance(combined, HolyName.HARE)
        res_krishna = calculate_resonance(combined, HolyName.KRISHNA)
        res_rama = calculate_resonance(combined, HolyName.RAMA)
    except Exception:
        res_hare = res_krishna = res_rama = 0.0

    # Find dominant name
    resonances = {"HARE": res_hare, "KRISHNA": res_krishna, "RAMA": res_rama}
    dominant = max(resonances, key=resonances.get)

    # Compute guna and seed
    guna, guna_seed = compute_guna(translation)

    # Compute attractor
    attractor = compute_attractor(guna_seed)
    position = guna_seed % WORDS

    return VerseSignature(
        verse_id=verse_id,
        chapter=chapter,
        verse=verse,
        phonetic_hash=phonetic_hash,
        phonetic_length=phonetic_length,
        resonance_hare=res_hare,
        resonance_krishna=res_krishna,
        resonance_rama=res_rama,
        dominant_name=dominant,
        guna=guna,
        guna_seed=guna_seed,
        attractor=attractor,
        position=position,
    )


def extract_from_database(db_path: str) -> ResonanceIndex:
    """
    Extract resonance index from Vedabase.

    CLEAN ROOM: Only mathematical signatures are kept.
    No text content is stored.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all BG verses
    cursor.execute("""
        SELECT chapter, verse, sanskrit, translation
        FROM verses
        WHERE book_code = 'BG'
        ORDER BY chapter, CAST(verse AS INTEGER)
    """)

    verses = []
    chapter_data: Dict[int, List[VerseSignature]] = {}

    for row in cursor.fetchall():
        chapter, verse, sanskrit, translation = row
        verse_id = f"BG.{chapter}.{verse}"

        sig = extract_verse_signature(
            verse_id=verse_id,
            chapter=chapter,
            verse=str(verse),
            sanskrit=sanskrit or "",
            translation=translation or "",
        )

        verses.append(sig)
        chapter_data.setdefault(chapter, []).append(sig)

    conn.close()

    # Compute chapter-level signatures
    chapter_signatures = {}
    for ch, sigs in chapter_data.items():
        chapter_signatures[ch] = {
            "verse_count": len(sigs),
            "avg_resonance_hare": sum(s.resonance_hare for s in sigs) / len(sigs),
            "avg_resonance_krishna": sum(s.resonance_krishna for s in sigs) / len(sigs),
            "avg_resonance_rama": sum(s.resonance_rama for s in sigs) / len(sigs),
            "dominant_guna": max(
                ["tamas", "rajas", "sattva", "suddha"], key=lambda g: sum(1 for s in sigs if s.guna == g)
            ),
        }

    # Compute totals
    total_hare = sum(s.resonance_hare for s in verses) / len(verses)
    total_krishna = sum(s.resonance_krishna for s in verses) / len(verses)
    total_rama = sum(s.resonance_rama for s in verses) / len(verses)

    return ResonanceIndex(
        book_code="BG",
        total_verses=len(verses),
        total_chapters=len(chapter_data),
        avg_resonance_hare=total_hare,
        avg_resonance_krishna=total_krishna,
        avg_resonance_rama=total_rama,
        chapter_signatures=chapter_signatures,
        verses=[asdict(v) for v in verses],
        extraction_version="1.0.0",
        extraction_method="clean_room_phonetic_resonance",
    )


def save_index(index: ResonanceIndex, output_path: str) -> None:
    """Save resonance index to JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(asdict(index), f, indent=2, ensure_ascii=False)


# =============================================================================
# MAIN
# =============================================================================


def main():
    """
    CLEAN ROOM EXTRACTION

    1. Extract vibration signatures
    2. Save to JSON
    3. (Manual step) Delete source database
    """
    if len(sys.argv) < 3:
        print("Usage: python clean_room_extraction.py <vedabase.db> <output.json>")
        print()
        print("Example:")
        print("  python clean_room_extraction.py temp/vedabase.db data/resonance_index.json")
        sys.exit(1)

    db_path = sys.argv[1]
    output_path = sys.argv[2]

    print("=" * 60)
    print("CLEAN ROOM EXTRACTION")
    print("=" * 60)
    print()
    print(f"Source: {db_path}")
    print(f"Output: {output_path}")
    print()

    # Extract
    print("Extracting vibration signatures...")
    index = extract_from_database(db_path)

    print(f"  Verses: {index.total_verses}")
    print(f"  Chapters: {index.total_chapters}")
    print(f"  Avg HARE resonance: {index.avg_resonance_hare:.4f}")
    print(f"  Avg KRISHNA resonance: {index.avg_resonance_krishna:.4f}")
    print(f"  Avg RAMA resonance: {index.avg_resonance_rama:.4f}")
    print()

    # Save
    print(f"Saving to {output_path}...")
    save_index(index, output_path)
    print("Done.")
    print()

    # Reminder
    print("=" * 60)
    print("IMPORTANT: Now DELETE the source database!")
    print(f"  rm {db_path}")
    print()
    print("The resonance_index.json contains ONLY mathematical signatures.")
    print("NO copyrighted text content.")
    print("=" * 60)


if __name__ == "__main__":
    main()
