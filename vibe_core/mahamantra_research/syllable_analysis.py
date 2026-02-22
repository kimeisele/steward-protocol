"""
SYLLABLE INTERVAL ANALYSIS - The REAL Research
===============================================

NO ASSUMPTIONS. JUST MATH.

The previous approach was wrong because:
1. We analyzed LETTERS (k-a-p-i-l-a) not SYLLABLES (KA-PI-LA)
2. We jumped to conclusions without calculating ALL 12
3. We curve-fitted instead of discovering

THIS FILE:
- Breaks names into proper SANSKRIT SYLLABLES
- Calculates intervals for ALL 12 Mahajanas
- Looks for REAL patterns without assumptions
"""

from typing import List, Tuple, Dict

# The RAMA Grid (49 positions = complete Sanskrit alphabet)
# 0-15: Vowels (Svaras)
# 16-40: Stop Consonants (Sparsha) - 5x5 grid
# 41-48: Semivowels/Sibilants

RAMA_GRID = {
    # Vowels (0-15)
    "a": 0,
    "ā": 1,
    "i": 2,
    "ī": 3,
    "u": 4,
    "ū": 5,
    "ṛ": 6,
    "ṝ": 7,
    "ḷ": 8,
    "ḹ": 9,
    "e": 10,
    "ai": 11,
    "o": 12,
    "au": 13,
    "ṁ": 14,
    "ḥ": 15,
    # Ka-varga (Guttural) 16-20
    "ka": 16,
    "kha": 17,
    "ga": 18,
    "gha": 19,
    "ṅa": 20,
    # Ca-varga (Palatal) 21-25
    "ca": 21,
    "cha": 22,
    "ja": 23,
    "jha": 24,
    "ña": 25,
    # Ṭa-varga (Retroflex) 26-30
    "ṭa": 26,
    "ṭha": 27,
    "ḍa": 28,
    "ḍha": 29,
    "ṇa": 30,
    # Ta-varga (Dental) 31-35
    "ta": 31,
    "tha": 32,
    "da": 33,
    "dha": 34,
    "na": 35,
    # Pa-varga (Labial) 36-40
    "pa": 36,
    "pha": 37,
    "ba": 38,
    "bha": 39,
    "ma": 40,
    # Antastha (Semivowels) 41-44
    "ya": 41,
    "ra": 42,
    "la": 43,
    "va": 44,
    # Ushman (Sibilants) 45-48
    "śa": 45,
    "ṣa": 46,
    "sa": 47,
    "ha": 48,
}

# Mahamantra constants (from _seed.py)
CONSTANTS = {
    1: "KSETRAJNA",
    2: "HALVES",
    3: "TRINITY",
    4: "QUARTERS",
    5: "PANCHA",
    7: "SEVEN",
    8: "HARE_COUNT",
    10: "TEN",
    12: "MAHAJANA_COUNT",
    16: "WORDS",
    17: "KRISHNA_SUM",
    24: "KSHETRA",
    25: "PRASADAM",
    37: "PARAMPARA",
    49: "RAMA",
    70: "HARE_SUM",
}


def syllabify_sanskrit(name: str) -> List[str]:
    """
    Break a Sanskrit name into proper SYLLABLES.

    Sanskrit syllable rules:
    - Consonant + vowel = one syllable (ka, pi, la)
    - Conjunct consonants belong to following syllable
    - Final consonant joins previous syllable
    """
    # Manual syllabification for accuracy
    # (Automated Sanskrit syllabification is complex)

    syllables_map = {
        # The 12 Mahajanas (SB 6.3.20 order)
        "brahma": ["brah", "ma"],  # ब्रह्मा = brah-mā
        "narada": ["nā", "ra", "da"],  # नारद = nā-ra-da
        "shambhu": ["śam", "bhu"],  # शम्भु = śam-bhu
        "kumaras": ["ku", "mā", "ra"],  # कुमार = ku-mā-ra (4 kumaras)
        "kapila": ["ka", "pi", "la"],  # कपिल = ka-pi-la
        "manu": ["ma", "nu"],  # मनु = ma-nu
        "prahlada": ["prah", "lā", "da"],  # प्रह्लाद = prah-lā-da
        "janaka": ["ja", "na", "ka"],  # जनक = ja-na-ka
        "bhishma": ["bhī", "ṣma"],  # भीष्म = bhī-ṣma
        "bali": ["ba", "li"],  # बलि = ba-li
        "shuka": ["śu", "ka"],  # शुक = śu-ka
        "yamaraja": ["ya", "ma", "rā", "ja"],  # यमराज = ya-ma-rā-ja
        # The 4 Avataras
        "vyasa": ["vyā", "sa"],  # व्यास = vyā-sa
        "prithu": ["pṛ", "thu"],  # पृथु = pṛ-thu
        "parashurama": ["pa", "ra", "śu", "rā", "ma"],
        "nrisimha": ["nṛ", "siṁ", "ha"],  # नृसिंह = nṛ-siṁ-ha
    }

    return syllables_map.get(name.lower(), list(name))


def syllable_to_rama_index(syllable: str) -> int:
    """
    Map a syllable to its RAMA grid index.

    For consonant+vowel syllables (like 'ka'), use the consonant position.
    For pure vowels, use vowel position.
    """
    # Check if it's a known syllable
    if syllable in RAMA_GRID:
        return RAMA_GRID[syllable]

    # Handle conjuncts and special cases
    first_char = syllable[0] if syllable else ""

    # Map first sound to RAMA
    consonant_map = {
        "b": 38,  # ba
        "k": 16,  # ka
        "g": 18,  # ga
        "c": 21,  # ca
        "j": 23,  # ja
        "t": 31,  # ta
        "d": 33,  # da
        "n": 35,  # na
        "p": 36,  # pa
        "m": 40,  # ma
        "y": 41,  # ya
        "r": 42,  # ra
        "l": 43,  # la
        "v": 44,  # va
        "ś": 45,
        "s": 47,
        "h": 48,
    }

    vowel_map = {
        "a": 0,
        "ā": 1,
        "i": 2,
        "ī": 3,
        "u": 4,
        "ū": 5,
        "ṛ": 6,
        "ṝ": 7,
        "ḷ": 8,
        "e": 10,
        "o": 12,
    }

    # Special syllables
    special = {
        "brah": 38,  # bra- starts with ba
        "śam": 45,  # śa-
        "prah": 36,  # pra- starts with pa
        "bhī": 39,  # bhī = bha + ī
        "ṣma": 46,  # ṣma = ṣa
        "vyā": 44,  # vyā = va
        "pṛ": 36,  # pṛ = pa
        "thu": 32,  # thu = tha
        "nṛ": 35,  # nṛ = na
        "siṁ": 47,  # siṁ = sa
        "nā": 35,  # nā = na
        "mā": 40,  # mā = ma
        "rā": 42,  # rā = ra
        "lā": 43,  # lā = la
    }

    if syllable in special:
        return special[syllable]

    if first_char in consonant_map:
        return consonant_map[first_char]
    if first_char in vowel_map:
        return vowel_map[first_char]

    return -1  # Unknown


def analyze_mahajana(name: str) -> Dict:
    """
    Analyze a single Mahajana's syllable structure.
    """
    syllables = syllabify_sanskrit(name)
    indices = [syllable_to_rama_index(s) for s in syllables]

    # Calculate intervals between consecutive syllables
    intervals = []
    for i in range(len(indices) - 1):
        if indices[i] >= 0 and indices[i + 1] >= 0:
            interval = (indices[i + 1] - indices[i]) % 49
            intervals.append(
                {
                    "from": syllables[i],
                    "to": syllables[i + 1],
                    "from_idx": indices[i],
                    "to_idx": indices[i + 1],
                    "interval": interval,
                    "constant": CONSTANTS.get(interval, None),
                }
            )

    return {
        "name": name,
        "syllables": syllables,
        "indices": indices,
        "intervals": intervals,
    }


def run_full_analysis():
    """
    Analyze ALL 12 Mahajanas and look for patterns.
    """
    print("=" * 70)
    print("SYLLABLE INTERVAL ANALYSIS - ALL 12 MAHAJANAS")
    print("=" * 70)
    print()
    print("NO ASSUMPTIONS. JUST MATH.")
    print()

    mahajanas = [
        "brahma",
        "narada",
        "shambhu",
        "kumaras",
        "kapila",
        "manu",
        "prahlada",
        "janaka",
        "bhishma",
        "bali",
        "shuka",
        "yamaraja",
    ]

    all_intervals = []
    const_count = {}

    for name in mahajanas:
        result = analyze_mahajana(name)

        print(f"\n{name.upper()}:")
        print(f"  Syllables: {' - '.join(result['syllables'])}")
        print(f"  RAMA indices: {result['indices']}")

        for iv in result["intervals"]:
            const = iv.get("constant", "")
            mark = f" = {const}" if const else ""
            print(f"  {iv['from']}({iv['from_idx']}) → {iv['to']}({iv['to_idx']}): +{iv['interval']}{mark}")

            all_intervals.append(iv["interval"])
            if const:
                const_count[const] = const_count.get(const, 0) + 1

    # Summary
    print()
    print("=" * 70)
    print("INTERVAL FREQUENCY ANALYSIS")
    print("=" * 70)
    print()

    from collections import Counter

    interval_freq = Counter(all_intervals)

    print("All intervals found (sorted by frequency):")
    for interval, count in interval_freq.most_common():
        const = CONSTANTS.get(interval, "?")
        print(f"  +{interval:2} appears {count}x = {const}")

    print()
    print("Mahamantra constants found:")
    for const, count in sorted(const_count.items(), key=lambda x: -x[1]):
        print(f"  {const}: {count}x")

    print()
    print("=" * 70)
    print("RAW DATA FOR PATTERN ANALYSIS")
    print("=" * 70)
    print()
    print("(interval_sequence per mahajana)")
    print()

    for name in mahajanas:
        result = analyze_mahajana(name)
        ivs = [iv["interval"] for iv in result["intervals"]]
        print(f"  {name:12}: {ivs}")


if __name__ == "__main__":
    run_full_analysis()
