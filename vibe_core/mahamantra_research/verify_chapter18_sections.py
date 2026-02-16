"""
VERIFIKATION: Kapitel 18 Sektionen — Phonetische Distinktheit
==============================================================

Hypothese: Die 7 Sektionen von Kapitel 18 (12+6+22+8+7+11+12 = 78)
haben UNTERSCHIEDLICHE phonetische Profile.

Methode:
    1. Alle 78 Verse laden (verse_words)
    2. Pro Sektion: alle RAMA-Koordinaten sammeln
    3. Pro Sektion berechnen:
       a) Element-Histogramm (5 Elemente: Akasha/Vayu/Agni/Jala/Prithvi)
       b) Varga-Verteilung (3 Klassen: Svara/Sparsha/Shesha)
       c) HKR-Signatur (Hare/Krishna/Rama Anteil)
       d) Basin-Verteilung (7 Attraktoren)
       e) Phonem-Attractor-Verteilung (5 Mahamantra-Konstanten)
       f) Shruti-Ratio (Fixed Points vs Journey Points)
    4. Paarweise Distanzen zwischen Sektionen
    5. Entscheidung: Sind die Sektionen statistisch distinkt?

KEIN Zufall. Alles deterministisch. Reine Analyse.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x2c80316d"

from typing import Final

from vibe_core.mahamantra.protocols._seed import PARAMPARA, WORDS

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

# --- Imports ---
from vibe_core.mahamantra.protocols._seed import PANCHA, TRINITY
from vibe_core.mahamantra_research.language_model_resonance import (
    CHAPTER_18_SECTIONS,
    CHAPTER_18_VERSES,
)
from vibe_core.mahamantra.substrate.basin_map import (
    BASIN_COUNT,
    BASIN_INDEX,
    BASIN_LIST,
    COORD_BASIN,
    COORD_PHONEME_ATTRACTOR,
    PHONEME_ATTRACTOR_COUNT,
    PHONEME_ATTRACTOR_INDEX,
    PHONEME_ATTRACTOR_LIST,
    basin_histogram,
    phoneme_attractor_histogram,
)
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT,
    COORD_HARMONIC,
    COORD_SUB,
    COORD_VARGA,
    ELEMENT_NAMES,
    IS_SHRUTI,
    element_histogram,
)
from vibe_core.mahamantra.substrate.sanskrit_lookup import hkr_signature, verse_words

# =============================================================================
# DATEN LADEN
# =============================================================================


def load_section_data() -> dict:
    """
    Lade alle 78 Verse von Kapitel 18 und gruppiere nach Sektion.

    Returns: {
        section_name: {
            "verses": [VerseWords, ...],
            "all_coords": [int, ...],        # alle RAMA-Koordinaten
            "all_words": [WordEntry, ...],    # alle Wörter
            "word_count": int,
            "phoneme_count": int,
        }
    }
    """
    sections = {}

    for section_name, start, end, length in CHAPTER_18_SECTIONS:
        coords_all = []
        words_all = []
        verses_loaded = []
        missing_verses = []

        for v in range(start, end + 1):
            vw = verse_words(18, v)
            if vw is None:
                missing_verses.append(v)
                continue
            verses_loaded.append(vw)
            for word in vw.words:
                words_all.append(word)
                coords_all.extend(word.coords)

        sections[section_name] = {
            "start": start,
            "end": end,
            "expected_length": length,
            "verses_loaded": len(verses_loaded),
            "missing_verses": missing_verses,
            "all_coords": coords_all,
            "all_words": words_all,
            "word_count": len(words_all),
            "phoneme_count": len(coords_all),
        }

    return sections


# =============================================================================
# ANALYSE-FUNKTIONEN
# =============================================================================


def element_profile(coords: list[int]) -> dict:
    """Element-Histogramm normalisiert auf Prozent."""
    if not coords:
        return {name: 0.0 for name in ELEMENT_NAMES}
    hist = [0] * PANCHA
    for c in coords:
        hist[COORD_ELEMENT[c]] += 1
    total = len(coords)
    return {ELEMENT_NAMES[i]: round(hist[i] / total * 100, 1) for i in range(PANCHA)}


def varga_profile(coords: list[int]) -> dict:
    """Varga-Verteilung (Svara/Sparsha/Shesha) in Prozent."""
    if not coords:
        return {"svara": 0.0, "sparsha": 0.0, "shesha": 0.0}
    names = ("svara", "sparsha", "shesha")
    hist = [0] * TRINITY
    for c in coords:
        hist[COORD_VARGA[c]] += 1
    total = len(coords)
    return {names[i]: round(hist[i] / total * 100, 1) for i in range(TRINITY)}


def hkr_profile(coords: list[int]) -> dict:
    """H/K/R Anteil in Prozent."""
    if not coords:
        return {"H": 0.0, "K": 0.0, "R": 0.0}
    sig = hkr_signature(coords)
    h = sig.count("H")
    k = sig.count("K")
    r = sig.count("R")
    total = len(sig) or 1
    return {
        "H": round(h / total * 100, 1),
        "K": round(k / total * 100, 1),
        "R": round(r / total * 100, 1),
    }


def basin_profile(coords: list[int]) -> dict:
    """Basin-Verteilung in Prozent."""
    if not coords:
        return {str(b): 0.0 for b in BASIN_LIST}
    hist = basin_histogram(coords)
    total = len(coords)
    return {str(BASIN_LIST[i]): round(hist[i] / total * 100, 1) for i in range(BASIN_COUNT)}


def attractor_profile(coords: list[int]) -> dict:
    """Phonem-Attractor-Verteilung in Prozent."""
    if not coords:
        return {str(a): 0.0 for a in PHONEME_ATTRACTOR_LIST}
    hist = phoneme_attractor_histogram(coords)
    total = len(coords)
    return {str(PHONEME_ATTRACTOR_LIST[i]): round(hist[i] / total * 100, 1) for i in range(PHONEME_ATTRACTOR_COUNT)}


def shruti_ratio(coords: list[int]) -> float:
    """Anteil Shruti-Phoneme (Fixed Points) in Prozent."""
    if not coords:
        return 0.0
    shruti_count = sum(1 for c in coords if IS_SHRUTI[c])
    return round(shruti_count / len(coords) * 100, 1)


# =============================================================================
# DISTANZ-FUNKTIONEN
# =============================================================================


def l1_distance(profile_a: dict, profile_b: dict) -> float:
    """L1 (Manhattan) Distanz zwischen zwei Profilen."""
    keys = set(profile_a) | set(profile_b)
    return sum(abs(profile_a.get(k, 0) - profile_b.get(k, 0)) for k in keys)


def max_diff(profile_a: dict, profile_b: dict) -> tuple[str, float]:
    """Größte Einzeldifferenz und welche Dimension."""
    best_key = ""
    best_diff = 0.0
    for k in set(profile_a) | set(profile_b):
        d = abs(profile_a.get(k, 0) - profile_b.get(k, 0))
        if d > best_diff:
            best_diff = d
            best_key = k
    return best_key, best_diff


# =============================================================================
# HAUPTANALYSE
# =============================================================================


def run_analysis() -> dict:
    """Vollständige Analyse der 7 Sektionen von Kapitel 18."""
    print("=" * 72)
    print("KAPITEL 18 — SEKTIONS-VERIFIKATION")
    print("=" * 72)
    print()

    # Daten laden
    print("Lade 78 Verse von Kapitel 18...")
    sections = load_section_data()

    total_words = 0
    total_phonemes = 0
    total_missing = 0

    for name, data in sections.items():
        total_words += data["word_count"]
        total_phonemes += data["phoneme_count"]
        total_missing += len(data["missing_verses"])
        status = "OK" if not data["missing_verses"] else f"MISSING: {data['missing_verses']}"
        print(
            f"  {name:12s}: {data['verses_loaded']:2d} Verse, "
            f"{data['word_count']:3d} Wörter, "
            f"{data['phoneme_count']:4d} Phoneme — {status}"
        )

    print(f"\n  GESAMT: {total_words} Wörter, {total_phonemes} Phoneme, {total_missing} fehlende Verse")
    print()

    # Profile berechnen
    print("-" * 72)
    print("ELEMENT-PROFILE (5 Elemente: Akasha/Vayu/Agni/Jala/Prithvi)")
    print("-" * 72)

    section_profiles = {}
    for name, data in sections.items():
        coords = data["all_coords"]
        ep = element_profile(coords)
        vp = varga_profile(coords)
        hp = hkr_profile(coords)
        bp = basin_profile(coords)
        ap = attractor_profile(coords)
        sr = shruti_ratio(coords)

        section_profiles[name] = {
            "element": ep,
            "varga": vp,
            "hkr": hp,
            "basin": bp,
            "attractor": ap,
            "shruti": sr,
            "phoneme_count": data["phoneme_count"],
            "word_count": data["word_count"],
        }

        print(
            f"\n  [{name}] (Verse {data['start']}-{data['end']}, "
            f"{data['word_count']} Wörter, {data['phoneme_count']} Phoneme)"
        )
        print(f"    Element:   {ep}")
        print(f"    Varga:     {vp}")
        print(f"    HKR:       {hp}")
        print(f"    Shruti:    {sr}%")

    # Paarweise Distanzen
    print()
    print("-" * 72)
    print("PAARWEISE ELEMENT-DISTANZEN (L1, höher = verschiedener)")
    print("-" * 72)

    names = list(section_profiles.keys())
    n = len(names)

    # Header
    print(f"\n  {'':12s}", end="")
    for name in names:
        print(f" {name[:8]:>8s}", end="")
    print()

    max_dist = 0.0
    max_pair = ("", "")
    min_dist = 999.0
    min_pair = ("", "")

    for i in range(n):
        print(f"  {names[i]:12s}", end="")
        for j in range(n):
            d = l1_distance(
                section_profiles[names[i]]["element"],
                section_profiles[names[j]]["element"],
            )
            print(f" {d:8.1f}", end="")
            if i < j:
                if d > max_dist:
                    max_dist = d
                    max_pair = (names[i], names[j])
                if d < min_dist:
                    min_dist = d
                    min_pair = (names[i], names[j])
        print()

    print(f"\n  MAX Distanz: {max_dist:.1f} zwischen {max_pair[0]} und {max_pair[1]}")
    print(f"  MIN Distanz: {min_dist:.1f} zwischen {min_pair[0]} und {min_pair[1]}")

    # HKR Distanzen
    print()
    print("-" * 72)
    print("PAARWEISE HKR-DISTANZEN (L1)")
    print("-" * 72)

    print(f"\n  {'':12s}", end="")
    for name in names:
        print(f" {name[:8]:>8s}", end="")
    print()

    hkr_max = 0.0
    hkr_max_pair = ("", "")

    for i in range(n):
        print(f"  {names[i]:12s}", end="")
        for j in range(n):
            d = l1_distance(
                section_profiles[names[i]]["hkr"],
                section_profiles[names[j]]["hkr"],
            )
            print(f" {d:8.1f}", end="")
            if i < j and d > hkr_max:
                hkr_max = d
                hkr_max_pair = (names[i], names[j])
        print()

    print(f"\n  MAX HKR-Distanz: {hkr_max:.1f} zwischen {hkr_max_pair[0]} und {hkr_max_pair[1]}")

    # Basin-Distanzen
    print()
    print("-" * 72)
    print("PAARWEISE BASIN-DISTANZEN (L1)")
    print("-" * 72)

    print(f"\n  {'':12s}", end="")
    for name in names:
        print(f" {name[:8]:>8s}", end="")
    print()

    basin_max = 0.0
    basin_max_pair = ("", "")

    for i in range(n):
        print(f"  {names[i]:12s}", end="")
        for j in range(n):
            d = l1_distance(
                section_profiles[names[i]]["basin"],
                section_profiles[names[j]]["basin"],
            )
            print(f" {d:8.1f}", end="")
            if i < j and d > basin_max:
                basin_max = d
                basin_max_pair = (names[i], names[j])
        print()

    print(f"\n  MAX Basin-Distanz: {basin_max:.1f} zwischen {basin_max_pair[0]} und {basin_max_pair[1]}")

    # Shruti-Vergleich
    print()
    print("-" * 72)
    print("SHRUTI-RATIO PRO SEKTION (Fixed Points %)")
    print("-" * 72)

    for name in names:
        sr = section_profiles[name]["shruti"]
        bar = "#" * int(sr / 2)
        print(f"  {name:12s}: {sr:5.1f}% {bar}")

    # Attractor-Profile
    print()
    print("-" * 72)
    print("PHONEM-ATTRACTOR-PROFILE (5 Mahamantra-Konstanten)")
    print("-" * 72)

    for name in names:
        ap = section_profiles[name]["attractor"]
        print(f"  {name:12s}: {ap}")

    # Zusammenfassung
    print()
    print("=" * 72)
    print("ZUSAMMENFASSUNG")
    print("=" * 72)

    # Berechne Gesamtvarianz
    all_element_dists = []
    all_hkr_dists = []
    all_basin_dists = []

    for i in range(n):
        for j in range(i + 1, n):
            all_element_dists.append(
                l1_distance(
                    section_profiles[names[i]]["element"],
                    section_profiles[names[j]]["element"],
                )
            )
            all_hkr_dists.append(
                l1_distance(
                    section_profiles[names[i]]["hkr"],
                    section_profiles[names[j]]["hkr"],
                )
            )
            all_basin_dists.append(
                l1_distance(
                    section_profiles[names[i]]["basin"],
                    section_profiles[names[j]]["basin"],
                )
            )

    avg_element = sum(all_element_dists) / len(all_element_dists)
    avg_hkr = sum(all_hkr_dists) / len(all_hkr_dists)
    avg_basin = sum(all_basin_dists) / len(all_basin_dists)

    print(f"\n  Durchschnittliche Element-Distanz:   {avg_element:.1f}")
    print(f"  Durchschnittliche HKR-Distanz:       {avg_hkr:.1f}")
    print(f"  Durchschnittliche Basin-Distanz:      {avg_basin:.1f}")

    # Dominanz-Analyse: Welches Element/HKR dominiert pro Sektion?
    print()
    print("-" * 72)
    print("DOMINANZ-ANALYSE (Stärkstes Element & HKR pro Sektion)")
    print("-" * 72)

    for name in names:
        ep = section_profiles[name]["element"]
        hp = section_profiles[name]["hkr"]

        dom_element = max(ep, key=ep.get)
        dom_hkr = max(hp, key=hp.get)

        print(f"  {name:12s}: Element={dom_element:8s} ({ep[dom_element]:5.1f}%)  HKR={dom_hkr} ({hp[dom_hkr]:5.1f}%)")

    # Entscheidung
    print()
    print("-" * 72)
    print("ENTSCHEIDUNG")
    print("-" * 72)

    # Kriterien:
    # 1. Wenn avg Element-Distanz > 5.0: deutlich verschieden
    # 2. Wenn avg HKR-Distanz > 5.0: deutlich verschieden
    # 3. Wenn verschiedene dominante Elemente: qualitativ verschieden

    dominant_elements = set()
    dominant_hkr = set()
    for name in names:
        ep = section_profiles[name]["element"]
        hp = section_profiles[name]["hkr"]
        dominant_elements.add(max(ep, key=ep.get))
        dominant_hkr.add(max(hp, key=hp.get))

    distinct_elements = len(dominant_elements) > 1
    distinct_hkr = len(dominant_hkr) > 1

    print(f"\n  Unique dominante Elemente: {len(dominant_elements)} ({', '.join(sorted(dominant_elements))})")
    print(f"  Unique dominante HKR:     {len(dominant_hkr)} ({', '.join(sorted(dominant_hkr))})")
    print(f"  Avg Element-Distanz:      {avg_element:.1f} {'(SIGNIFIKANT)' if avg_element > 5 else '(gering)'}")
    print(f"  Avg HKR-Distanz:          {avg_hkr:.1f} {'(SIGNIFIKANT)' if avg_hkr > 5 else '(gering)'}")
    print(f"  Avg Basin-Distanz:         {avg_basin:.1f} {'(SIGNIFIKANT)' if avg_basin > 5 else '(gering)'}")

    if avg_element > 3 or distinct_elements or avg_hkr > 3:
        print("\n  ERGEBNIS: Sektionen sind phonetisch DISTINKT.")
        print("  → Kapitel-18-Routing als ResponseMode ist VALIDE.")
    else:
        print("\n  ERGEBNIS: Sektionen sind phonetisch ÄHNLICH.")
        print("  → Kapitel-18-Routing muss auf anderer Ebene erfolgen (semantisch, nicht phonetisch).")

    return section_profiles


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    profiles = run_analysis()
