"""
Sanskrit Seed Lexicon Extraction
================================

Extracts Sanskrit word-for-word data from vedabase.db and transforms it
into architecture-native seed format.

Research findings:
- vedabase.db contains 700 BG verses (Prabhupada's Bhagavad Gita As It Is, 1972)
- 698 verses have synonyms (word-for-word), 699 have Sanskrit, 700 have translation
- 4161 unique Sanskrit words, 6203 unique (word, meaning) pairs
- 0 seed collisions on SHA256[:4] for all unique Sanskrit words
- Average 16.0 word-meaning pairs per verse (= WORDS constant)

Copyright layers:
  Layer 0: Sanskrit verses        - Public domain (3000+ years old)
  Layer 1: Sanskrit word forms    - Public domain (grammatical facts)
  Layer 2: Word-for-word meanings - Dictionary entries (functional, not creative)
  Layer 3: Translation sentences  - Prabhupada's creative expression (BBT copyright)
  Layer 4: Purports               - BBT copyright, do not extract

Approach: Extract Layers 0-2 as seed-indexed lexicon.
Layer 3+4 are NOT stored. The DB is destroyed after extraction.

Architecture fit:
  - Each Sanskrit word → deterministic phonetic_seed (SHA256[:4])
  - Seeds are 32-bit, addressing 4 billion values for 4161 words (no collisions)
  - 13 bits sufficient to index all 6203 unique pairs
  - DIW is 19 bits → can address the entire lexicon natively
  - Each verse averages 16.0 pairs = WORDS = Mahamantra word count
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from typing import Final

# Paths
DB_PATH: Final = Path(__file__).resolve().parents[3] / "docs" / "vedabase.db"
OUTPUT_DIR: Final = Path(__file__).resolve().parent / "gita"
LEXICON_PATH: Final = OUTPUT_DIR / "sanskrit_seed_lexicon.json"
VERSE_SEEDS_PATH: Final = OUTPUT_DIR / "verse_seed_map.json"


def phonetic_seed(word: str) -> int:
    """Deterministic 32-bit seed from Sanskrit word. No collisions for 4161 words."""
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
    """
    Extract Sanskrit seed lexicon from vedabase.db.

    Returns dict with:
      - vocabulary: {seed_hex: {word, meanings[]}}
      - verses: [{chapter, verse, sanskrit_text, word_seeds[]}]
      - stats: extraction statistics
    """
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()

    # Build vocabulary
    vocabulary: dict[str, dict] = {}  # seed_hex -> {word, meanings}
    verses: list[dict] = []

    c.execute("SELECT chapter, verse, sanskrit, synonyms FROM verses ORDER BY chapter, CAST(verse AS INTEGER)")

    total_pairs = 0
    collision_check: dict[int, str] = {}  # seed -> word (detect collisions)

    for chapter, verse_num, sanskrit_text, synonyms_text in c.fetchall():
        word_seeds = []

        if synonyms_text:
            pairs = parse_synonyms(synonyms_text)
            for sanskrit, meaning in pairs:
                seed = phonetic_seed(sanskrit)
                seed_hex = f"{seed:08x}"

                # Collision detection
                if seed in collision_check:
                    if collision_check[seed] != sanskrit.lower():
                        raise ValueError(f"COLLISION: {sanskrit} and {collision_check[seed]} share seed {seed_hex}")
                collision_check[seed] = sanskrit.lower()

                if seed_hex not in vocabulary:
                    vocabulary[seed_hex] = {
                        "word": sanskrit,
                        "meanings": [],
                    }

                # Add meaning if not already present
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

        # Sanskrit text is public domain - store the phonetic seed
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

    return {
        "vocabulary": vocabulary,
        "verses": verses,
        "stats": stats,
    }


def build_reverse_index(lexicon: dict) -> dict:
    """Build attractor-space index for the vocabulary.

    Maps each word's seed modulo key architectural constants
    to enable resonance-based lookup.
    """
    QUANTUM = 137  # MAHA_QUANTUM = POSITION_SUM_TOTAL + KSETRAJNA
    PARAMPARA = 37
    WORDS = 16

    attractor_index: dict[int, list[str]] = {}
    parampara_index: dict[int, list[str]] = {}
    position_index: dict[int, list[str]] = {}

    for seed_hex, entry in lexicon["vocabulary"].items():
        seed = int(seed_hex, 16)
        attractor = seed % QUANTUM
        parampara_slot = seed % PARAMPARA
        position = seed % WORDS

        attractor_index.setdefault(attractor, []).append(seed_hex)
        parampara_index.setdefault(parampara_slot, []).append(seed_hex)
        position_index.setdefault(position, []).append(seed_hex)

    return {
        "by_attractor": {str(k): v for k, v in sorted(attractor_index.items())},
        "by_parampara": {str(k): v for k, v in sorted(parampara_index.items())},
        "by_position": {str(k): v for k, v in sorted(position_index.items())},
        "distribution": {
            "attractors_used": len(attractor_index),
            "attractor_space": QUANTUM,
            "avg_per_attractor": round(len(lexicon["vocabulary"]) / max(len(attractor_index), 1), 1),
            "parampara_slots_used": len(parampara_index),
            "positions_used": len(position_index),
        },
    }


def extract_and_save(db_path: Path = DB_PATH) -> dict:
    """Full extraction pipeline. Saves results to research/gita/."""
    if not db_path.exists():
        print(f"ERROR: {db_path} not found")
        sys.exit(1)

    print(f"Extracting from {db_path}...")
    lexicon = extract_lexicon(db_path)
    reverse_idx = build_reverse_index(lexicon)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save lexicon (vocabulary + verse seed map)
    lexicon_out = {
        "meta": {
            "source": "Bhagavad Gita As It Is (1972)",
            "layers_extracted": ["sanskrit_words", "word_meanings"],
            "layers_excluded": ["translations", "purports"],
            "note": "Sanskrit is public domain. Word-for-word meanings are dictionary-level functional entries.",
        },
        "stats": lexicon["stats"],
        "vocabulary": lexicon["vocabulary"],
    }

    with open(LEXICON_PATH, "w", encoding="utf-8") as f:
        json.dump(lexicon_out, f, ensure_ascii=False, indent=2)
    print(f"Lexicon: {LEXICON_PATH} ({LEXICON_PATH.stat().st_size // 1024}KB)")

    # Save verse seed map (no copyrighted text, only seeds)
    verse_map_out = {
        "meta": {
            "description": "Each verse mapped to its word seeds. No copyrighted text stored.",
        },
        "verses": lexicon["verses"],
        "reverse_index": reverse_idx,
    }

    with open(VERSE_SEEDS_PATH, "w", encoding="utf-8") as f:
        json.dump(verse_map_out, f, ensure_ascii=False, indent=2)
    print(f"Verse map: {VERSE_SEEDS_PATH} ({VERSE_SEEDS_PATH.stat().st_size // 1024}KB)")

    # Print summary
    s = lexicon["stats"]
    print(f"\n{'=' * 50}")
    print("EXTRACTION COMPLETE")
    print(f"{'=' * 50}")
    print(f"Verses:       {s['total_verses']}")
    print(f"Word pairs:   {s['total_pairs']}")
    print(f"Unique words: {s['unique_words']}")
    print(f"Unique pairs: {s['unique_pairs']}")
    print(f"Avg/verse:    {s['avg_pairs_per_verse']} (WORDS = 16)")
    print(f"Collisions:   {s['collisions']}")
    print(f"Bits needed:  {s['bits_for_vocabulary']} (DIW = 19)")
    print("\nAttractor distribution:")
    d = reverse_idx["distribution"]
    print(f"  {d['attractors_used']}/{d['attractor_space']} attractors used")
    print(f"  {d['avg_per_attractor']} words per attractor (avg)")
    print(f"  {d['positions_used']}/16 positions used")

    return lexicon


def demonstrate_lookup(lexicon: dict) -> None:
    """Show how seed-based lookup works at runtime."""
    vocab = lexicon["vocabulary"]
    verses = lexicon["verses"]

    # Find BG 18.66
    fixed_point = next((v for v in verses if v["ref"] == "BG.18.66"), None)
    if not fixed_point:
        print("BG 18.66 not found")
        return

    print(f"\n{'=' * 50}")
    print(f"RUNTIME LOOKUP DEMO: {fixed_point['ref']}")
    print(f"{'=' * 50}")

    for seed_hex in fixed_point["word_seeds"]:
        entry = vocab.get(seed_hex, {})
        word = entry.get("word", "?")
        meanings = entry.get("meanings", [])
        print(f"  0x{seed_hex} → {word} → {meanings[0] if meanings else '?'}")

    print("\nTo reconstruct word-for-word from seeds:")
    print("  1. Load lexicon (seed → word + meaning)")
    print("  2. For each verse, iterate word_seeds[]")
    print("  3. Lookup each seed → get Sanskrit word + meaning")
    print("  4. No copyrighted text stored as plaintext")


if __name__ == "__main__":
    lexicon = extract_and_save()
    demonstrate_lookup(lexicon)
