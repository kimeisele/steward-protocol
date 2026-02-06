"""
Sanskrit Seed Lexicon Extraction
================================

Extracts Sanskrit word-for-word data from vedabase.db and transforms it
into architecture-native RAMA coordinate format.

Two encoding modes:
  1. SHA256 phonetic seeds (legacy, for backward compat)
  2. RAMA coordinates (native, architecture-aligned)

The RAMA encoding uses the Varnamala Codec:
  - Each Sanskrit letter → RAMA Grid coordinate (0-48)
  - Each coordinate = 6 bits = VENU field of DIW
  - Entire Gita word-for-word = 54,423 phonemes = 39KB packed
  - Fits in 65K lotus address space (83% utilization)

Copyright layers:
  Layer 0: Sanskrit verses        - Public domain (3000+ years old)
  Layer 1: Sanskrit word forms    - Public domain (grammatical facts)
  Layer 2: Word-for-word meanings - Dictionary entries (functional, not creative)
  Layer 3: Translation sentences  - BBT copyright (NOT extracted)
  Layer 4: Purports               - BBT copyright (NOT extracted)
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from typing import Final

# Paths
DB_PATH: Final = Path(__file__).resolve().parents[3] / "docs" / "vedabase.db"
OUTPUT_DIR: Final = Path(__file__).resolve().parent / "gita"
LEXICON_PATH: Final = OUTPUT_DIR / "sanskrit_seed_lexicon.json"
VERSE_SEEDS_PATH: Final = OUTPUT_DIR / "verse_seed_map.json"
RAMA_LEXICON_PATH: Final = OUTPUT_DIR / "rama_lexicon.json"


def phonetic_seed(word: str) -> int:
    """Deterministic 32-bit seed from Sanskrit word."""
    h = hashlib.sha256(word.lower().encode("utf-8")).digest()
    return int.from_bytes(h[:4], "big")


def parse_synonyms(text: str) -> list[tuple[str, str]]:
    """Parse vedabase synonym format: 'word—meaning;word—meaning;...'"""
    pairs = []
    for entry in text.split(";"):
        entry = entry.strip()
        if "—" not in entry:
            continue
        parts = entry.split("—", 1)
        sanskrit = parts[0].strip()
        meaning = parts[1].strip()
        if sanskrit and meaning:
            pairs.append((sanskrit, meaning))
    return pairs


def extract_lexicon(db_path: Path = DB_PATH) -> dict:
    """Extract Sanskrit seed lexicon from vedabase.db."""
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()

    vocabulary: dict[str, dict] = {}
    verses: list[dict] = []

    c.execute("SELECT chapter, verse, sanskrit, synonyms FROM verses ORDER BY chapter, CAST(verse AS INTEGER)")

    total_pairs = 0
    collision_check: dict[int, str] = {}

    for chapter, verse_num, sanskrit_text, synonyms_text in c.fetchall():
        word_seeds = []

        if synonyms_text:
            pairs = parse_synonyms(synonyms_text)
            for sanskrit, meaning in pairs:
                seed = phonetic_seed(sanskrit)
                seed_hex = f"{seed:08x}"

                if seed in collision_check:
                    if collision_check[seed] != sanskrit.lower():
                        raise ValueError(f"COLLISION: {sanskrit} and {collision_check[seed]} share seed {seed_hex}")
                collision_check[seed] = sanskrit.lower()

                if seed_hex not in vocabulary:
                    vocabulary[seed_hex] = {"word": sanskrit, "meanings": []}

                if meaning not in vocabulary[seed_hex]["meanings"]:
                    vocabulary[seed_hex]["meanings"].append(meaning)

                word_seeds.append(seed_hex)
                total_pairs += 1

        verse_entry = {
            "ref": f"BG.{chapter}.{verse_num}",
            "chapter": chapter,
            "verse": verse_num,
            "word_seeds": word_seeds,
        }

        if sanskrit_text:
            verse_entry["sanskrit_seed"] = f"{phonetic_seed(sanskrit_text):08x}"

        verses.append(verse_entry)

    conn.close()

    stats = {
        "total_verses": len(verses),
        "total_pairs": total_pairs,
        "unique_words": len(vocabulary),
        "unique_pairs": sum(len(v["meanings"]) for v in vocabulary.values()),
        "avg_pairs_per_verse": round(total_pairs / max(len(verses), 1), 1),
        "collisions": 0,
        "bits_for_vocabulary": len(vocabulary).bit_length(),
    }

    return {"vocabulary": vocabulary, "verses": verses, "stats": stats}


def _clean_meaning(meaning: str) -> str:
    """Clean parsing artifacts from a word-for-word meaning.

    Vedabase synonyms have several recurring extraction problems:
    - Em-dash leakage: "also,madhusūdana—O killer of Madhu" → "also"
    - Missing spaces: "theVedas" → "the Vedas"
    - Trailing periods: "also." → "also"
    """
    import re

    # 1. Em-dash leakage: truncate at comma+word—meaning pattern
    if "—" in meaning:
        meaning = meaning.split("—")[0]
    # Also catch comma followed by Sanskrit word (lowercase diacritics)
    if "," in meaning:
        parts = meaning.split(",")
        meaning = parts[0]

    # 2. Missing spaces before capital letters mid-word: "theVedas" → "the Vedas"
    meaning = re.sub(r"([a-z])([A-Z])", r"\1 \2", meaning)
    # Missing spaces: "ofsomajuice" → harder, but "of" prefix is common
    meaning = re.sub(r"\bof([a-z])", r"of \1", meaning)

    # 3. Trailing periods (inconsistent in source)
    meaning = meaning.rstrip(".")

    return meaning.strip()


def extract_rama_lexicon(db_path: Path = DB_PATH) -> dict:
    """
    Extract Sanskrit word-for-word as RAMA coordinate sequences.

    This is the architecture-native encoding. No SHA256 hashes.
    Each word = sequence of RAMA Grid coordinates (0-48).
    Each coordinate = 6 bits = VENU field.

    DEDUPLICATION: Vedabase groups consecutive verses (e.g. "Texts 16-18")
    with a single combined word-for-word section. The DB stores the same
    synonyms string for every verse in the group. We detect this and assign
    the words only to the FIRST verse in each group, marking the others
    with a "grouped_with" reference.
    """
    from vibe_core.mahamantra.substrate.varnamala_codec import (
        BITS_PER_COORD,
        encode,
        encode_verse_words,
        pack_word,
    )

    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()

    # First pass: detect duplicate synonym groups
    c.execute("SELECT chapter, verse, synonyms FROM verses ORDER BY chapter, CAST(verse AS INTEGER)")
    rows = c.fetchall()

    # Group consecutive verses with identical synonyms
    seen_synonyms: dict[str, str] = {}  # synonyms_hash → first verse ref
    verse_group_map: dict[str, str] = {}  # ref → grouped_with ref (if secondary)

    for chapter, verse_num, synonyms_text in rows:
        ref = f"BG.{chapter}.{verse_num}"
        if not synonyms_text or not synonyms_text.strip():
            continue
        syn_hash = hashlib.md5(synonyms_text.encode()).hexdigest()
        if syn_hash in seen_synonyms:
            verse_group_map[ref] = seen_synonyms[syn_hash]
        else:
            seen_synonyms[syn_hash] = ref

    # Second pass: build vocabulary and verse data
    vocabulary: dict[str, dict] = {}
    verses: list[dict] = []
    total_phonemes = 0
    total_words = 0
    grouped_count = 0

    c.execute("SELECT chapter, verse, sanskrit, synonyms FROM verses ORDER BY chapter, CAST(verse AS INTEGER)")

    for chapter, verse_num, sanskrit_text, synonyms_text in c.fetchall():
        ref = f"BG.{chapter}.{verse_num}"
        word_entries = []

        if ref in verse_group_map:
            # Secondary verse in a group — words belong to the first verse
            grouped_count += 1
            verse_data = {
                "ref": ref,
                "chapter": chapter,
                "verse": verse_num,
                "words": [],
                "grouped_with": verse_group_map[ref],
            }
        elif synonyms_text and synonyms_text.strip():
            entries = encode_verse_words(synonyms_text)
            for entry in entries:
                packed_hex = f"{entry['packed']:x}"
                coords = list(entry["rama_coords"])
                meaning = _clean_meaning(entry["meaning"])

                if packed_hex not in vocabulary:
                    vocabulary[packed_hex] = {
                        "word": entry["sanskrit"],
                        "coords": coords,
                        "length": entry["length"],
                        "meanings": [],
                    }

                if meaning and meaning not in vocabulary[packed_hex]["meanings"]:
                    vocabulary[packed_hex]["meanings"].append(meaning)

                word_entries.append(
                    {
                        "packed": packed_hex,
                        "length": entry["length"],
                    }
                )
                total_phonemes += entry["length"]
                total_words += 1

            verse_data = {
                "ref": ref,
                "chapter": chapter,
                "verse": verse_num,
                "words": word_entries,
            }
        else:
            # Empty verse
            verse_data = {
                "ref": ref,
                "chapter": chapter,
                "verse": verse_num,
                "words": [],
            }

        if sanskrit_text:
            sanskrit_coords = encode(sanskrit_text)
            verse_data["sanskrit_phonemes"] = len(sanskrit_coords)

        verses.append(verse_data)

    conn.close()

    total_bits = total_phonemes * BITS_PER_COORD

    stats = {
        "total_verses": len(verses),
        "total_words": total_words,
        "unique_words": len(vocabulary),
        "total_phonemes": total_phonemes,
        "total_bits": total_bits,
        "total_bytes": total_bits // 8,
        "avg_phonemes_per_word": round(total_phonemes / max(total_words, 1), 1),
        "avg_phonemes_per_verse": round(total_phonemes / max(len(verses), 1), 1),
        "grouped_verses": grouped_count,
        "empty_verses": sum(1 for v in verses if not v["words"] and "grouped_with" not in v),
        "fits_in_65k": total_phonemes <= 65536,
        "utilization_65k_pct": round(total_phonemes / 65536 * 100, 1),
    }

    return {"vocabulary": vocabulary, "verses": verses, "stats": stats}


def extract_and_save(db_path: Path = DB_PATH) -> dict:
    """Full extraction pipeline."""
    if not db_path.exists():
        print(f"ERROR: {db_path} not found")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Legacy SHA256 lexicon
    print(f"Extracting SHA256 lexicon from {db_path}...")
    lexicon = extract_lexicon(db_path)

    lexicon_out = {
        "meta": {
            "source": "Bhagavad Gita As It Is (1972)",
            "layers_extracted": ["sanskrit_words", "word_meanings"],
            "layers_excluded": ["translations", "purports"],
            "note": ("Sanskrit is public domain. Word-for-word meanings are dictionary-level functional entries."),
        },
        "stats": lexicon["stats"],
        "vocabulary": lexicon["vocabulary"],
    }

    with open(LEXICON_PATH, "w", encoding="utf-8") as f:
        json.dump(lexicon_out, f, ensure_ascii=False, indent=2)
    print(f"  → {LEXICON_PATH} ({LEXICON_PATH.stat().st_size // 1024}KB)")

    verse_map_out = {
        "meta": {"description": "Verse → word seeds. No copyrighted text."},
        "verses": lexicon["verses"],
    }

    with open(VERSE_SEEDS_PATH, "w", encoding="utf-8") as f:
        json.dump(verse_map_out, f, ensure_ascii=False, indent=2)
    print(f"  → {VERSE_SEEDS_PATH} ({VERSE_SEEDS_PATH.stat().st_size // 1024}KB)")

    # RAMA coordinate lexicon (architecture-native)
    print("\nExtracting RAMA lexicon...")
    rama = extract_rama_lexicon(db_path)

    rama_out = {
        "meta": {
            "source": "Bhagavad Gita As It Is (1972)",
            "encoding": "RAMA Grid coordinates (0-48), 6 bits each",
            "note": (
                "Architecture-native encoding. Each coordinate = one Sanskrit "
                "letter in the 49-space (VARNAMALA = POSITION_SUM_RAMA)."
            ),
        },
        "stats": rama["stats"],
        "vocabulary": rama["vocabulary"],
        "verses": rama["verses"],
    }

    with open(RAMA_LEXICON_PATH, "w", encoding="utf-8") as f:
        json.dump(rama_out, f, ensure_ascii=False, indent=2)
    print(f"  → {RAMA_LEXICON_PATH} ({RAMA_LEXICON_PATH.stat().st_size // 1024}KB)")

    # Summary
    s = rama["stats"]
    print(f"\n{'=' * 50}")
    print("EXTRACTION COMPLETE")
    print(f"{'=' * 50}")
    print(f"Verses:            {s['total_verses']}")
    print(f"Words:             {s['total_words']}")
    print(f"Unique words:      {s['unique_words']}")
    print(f"Total phonemes:    {s['total_phonemes']}")
    print(f"Total size:        {s['total_bytes']} bytes ({s['total_bytes'] // 1024}KB)")
    print(f"Avg phon/word:     {s['avg_phonemes_per_word']}")
    print(f"Avg phon/verse:    {s['avg_phonemes_per_verse']}")
    print(f"Fits in 65K:       {s['fits_in_65k']} ({s['utilization_65k_pct']}%)")

    return rama


def demonstrate_rama_lookup(rama: dict) -> None:
    """Show RAMA-based lookup for BG 18.66."""
    from vibe_core.mahamantra.substrate.varnamala_codec import decode, unpack_word

    vocab = rama["vocabulary"]
    verse = next((v for v in rama["verses"] if v["ref"] == "BG.18.66"), None)
    if not verse:
        return

    print(f"\n{'=' * 50}")
    print(f"RAMA SPELLING: {verse['ref']}")
    print(f"{'=' * 50}")

    for word_entry in verse["words"]:
        packed_hex = word_entry["packed"]
        length = word_entry["length"]
        entry = vocab.get(packed_hex, {})
        word = entry.get("word", "?")
        coords = entry.get("coords", [])
        meanings = entry.get("meanings", [])

        # Decode from coordinates
        decoded = decode(coords)
        print(f"  {word:20} → RAMA{str(coords):35} → {decoded}")
        if meanings:
            print(f"  {'':20}   meaning: {meanings[0]}")


if __name__ == "__main__":
    rama = extract_and_save()
    demonstrate_rama_lookup(rama)
