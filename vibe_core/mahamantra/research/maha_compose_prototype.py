"""
MAHA COMPOSE PROTOTYPE — From Resonant Words to English Sentences
=================================================================

"vāṇī tasya kā" — What is the speech of that One?

THIS IS THE GAP: The system finds resonant words (rank_words, seed_to_words,
maha_llm_kernel). But a LIST of words is not a SENTENCE.

    Input: "What is devotion?"
    rank_words → ["devotion", "love", "service", "supreme", ...]
    verse_words(18, 66) → ["all varieties", "abandoning", "unto me", ...]

    MISSING: How to COMPOSE these into "Abandon all varieties and serve
             with devotion — that is supreme love."

THIS PROTOTYPE proves the composition works using:
    1. MahaLLMKernel.resonate() → resonant words (EXISTING)
    2. verse_words() → Gita verse template (EXISTING)
    3. Kapitel 18 section routing → response mode (EXISTING)
    4. compose() → ASSEMBLE English output (NEW — the missing piece)

NO NEW INFRASTRUCTURE. Only wiring of existing pieces.
"""

from __future__ import annotations

from typing import Dict, Final, List, Optional, Tuple

from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    MAHA_QUANTUM,
    PARAMPARA,
    WORDS,
)

# Section routing from verified analysis
from vibe_core.mahamantra.research.language_model_resonance import (
    CHAPTER_18_SECTIONS,
    SECTION_SIGNATURES,
)
from vibe_core.mahamantra.substrate.basin_map import BASIN_LIST, COORD_BASIN
from vibe_core.mahamantra.substrate.pancha_walk import COORD_ELEMENT, ELEMENT_NAMES
from vibe_core.mahamantra.substrate.phonetic_encoder import encode_text
from vibe_core.mahamantra.substrate.resonance_ranker import rank_words, resonate
from vibe_core.mahamantra.substrate.sanskrit_lookup import verse_words
from vibe_core.mahamantra.substrate.seed_to_words import attractor_words, seed_to_words

# =============================================================================
# SECTION ROUTER: Attractor → Kapitel 18 Sektion
# =============================================================================


def route_to_section(attractor: int, seed: int = 0) -> Tuple[str, int, int]:
    """
    Route an attractor + seed to a Kapitel 18 section.

    Two-stage routing:
        1. Attractor determines the BROAD section (via element dominance)
        2. Seed determines the EXACT verse within that section

    The element of the attractor mod 49 maps to sections:
        vayu    → TYAGA or RAHASYA (renunciation / devotion)
        jala    → SANKHYA or TRAIGUNYA or BRAHMAN (analysis / qualities / liberation)
        prithvi → VARNASHRAMA or SANJAYA (duty / conclusion)
        akasha  → RAHASYA (the hidden, the highest)
        agni    → TRAIGUNYA (transformation through gunas)

    Returns: (section_name, verse_number, section_index)
    """
    from vibe_core.mahamantra.substrate.rama_grid import VARNAMALA_TOTAL

    # Stage 1: Attractor element → section pool
    rama_coord = attractor % VARNAMALA_TOTAL
    element = int(COORD_ELEMENT[rama_coord])
    elem_name = ELEMENT_NAMES[element]

    # Map element to section candidates (verified from section profiles)
    section_pools = {
        "akasha": [("RAHASYA", 5), ("TYAGA", 0)],
        "vayu": [("TYAGA", 0), ("RAHASYA", 5)],
        "agni": [("TRAIGUNYA", 2), ("SANKHYA", 1)],
        "jala": [("SANKHYA", 1), ("BRAHMAN", 4), ("TRAIGUNYA", 2)],
        "prithvi": [("VARNASHRAMA", 3), ("SANJAYA", 6)],
    }

    pool = section_pools.get(elem_name, [("RAHASYA", 5)])

    # Stage 2: Seed selects from pool + verse within section
    pool_idx = seed % len(pool)
    section_name, section_idx = pool[pool_idx]

    # Get verse range for this section
    _, start, end, _ = CHAPTER_18_SECTIONS[section_idx]

    # Seed selects verse within section
    verse_range = end - start + 1
    verse_offset = (seed // len(pool)) % verse_range
    verse_num = start + verse_offset

    return section_name, verse_num, section_idx


# =============================================================================
# VERSE TEMPLATE: Extract grammatical skeleton from Gita verse
# =============================================================================


def extract_template(chapter: int, verse: int) -> List[Dict]:
    """
    Extract a grammatical template from a Gita verse.

    Each word position in the verse becomes a SLOT:
    - slot["sanskrit"] = original Sanskrit word
    - slot["meaning"] = English meaning (from lexicon)
    - slot["role"] = grammatical role (inferred from position + meaning)

    The template provides STRUCTURE. Resonant words provide CONTENT.
    """
    vw = verse_words(chapter, verse)
    if vw is None:
        return []

    slots = []
    for i, w in enumerate(vw.words):
        meaning = w.meaning if w.meaning else ""

        # Infer grammatical role from meaning patterns
        role = _infer_role(meaning, i, len(vw.words))

        slots.append(
            {
                "position": i,
                "sanskrit": w.sanskrit,
                "meaning": meaning,
                "role": role,
                "coords": w.coords,
            }
        )

    return slots


def _infer_role(meaning: str, position: int, total: int) -> str:
    """
    Infer grammatical role from English meaning.

    Not a parser — just pattern matching on the existing glosses.
    """
    ml = meaning.lower()

    # Verb indicators
    verb_markers = (
        "to ",
        "should ",
        "does ",
        "can ",
        "must ",
        "is ",
        "are ",
        "was ",
        "has ",
        "having ",
        "being ",
        "doing ",
        "said",
        "know",
        "give",
        "take",
        "abandon",
        "perform",
        "attain",
        "think",
        "see",
        "go",
        "come",
        "fight",
        "worship",
    )
    for v in verb_markers:
        if ml.startswith(v) or ml == v.rstrip():
            return "VERB"

    # Pronoun/reference
    if ml in (
        "i",
        "me",
        "my",
        "unto me",
        "of me",
        "him",
        "his",
        "you",
        "your",
        "unto you",
        "this",
        "that",
        "these",
        "who",
        "which",
        "what",
        "all",
        "every",
        "each",
    ):
        return "REF"

    # Conjunction/particle
    if ml in (
        "and",
        "or",
        "but",
        "also",
        "indeed",
        "certainly",
        "not",
        "nor",
        "neither",
        "never",
        "always",
        "therefore",
        "thus",
        "so",
        "even",
        "only",
    ):
        return "PARTICLE"

    # Qualifier
    qual_markers = (
        "very ",
        "great ",
        "supreme ",
        "divine ",
        "eternal ",
        "best ",
        "highest ",
        "most ",
        "pure ",
        "full ",
        "true ",
        "all ",
        "complete ",
    )
    for q in qual_markers:
        if ml.startswith(q):
            return "QUALITY"

    # Preposition-like
    if ml.startswith(("in ", "of ", "by ", "from ", "to ", "for ", "with ", "without ", "after ", "before ")):
        return "PREP"

    # Default: NOUN (content word)
    return "NOUN"


# =============================================================================
# COMPOSER: Resonant Words + Template → English Output
# =============================================================================


def compose(
    resonant_words: List[Dict],
    template: List[Dict],
    section: str,
) -> str:
    """
    Compose an English response from resonant words + verse template.

    Strategy per section (from SECTION_SIGNATURES):
        TYAGA       (FILTER):  Filter resonant meanings through template nouns
        SANKHYA     (VERB):    Emphasize verbs/actions from template
        TRAIGUNYA   (QUALITY): Emphasize qualities/adjectives
        VARNASHRAMA (CONTEXT): Emphasize context/duty words
        BRAHMAN     (TARGET):  Emphasize destination/goal words
        RAHASYA     (CORE):    Emphasize intimate/devotional core
        SANJAYA     (CLOSURE): Wrap up, conclude

    The template provides word ORDER. The resonant words provide CONTENT.
    Section determines which parts get emphasized.
    """
    if not template or not resonant_words:
        return ""

    sig = SECTION_SIGNATURES.get(section, {})
    mode = sig.get("mode", "CORE")

    # Step 1: Collect all resonant meanings (ordered by score)
    resonant_meanings = []
    for rw in resonant_words:
        meanings = rw.get("meanings", ())
        if isinstance(meanings, str):
            meanings = (meanings,)
        for m in meanings:
            if m and m not in resonant_meanings:
                resonant_meanings.append(m)

    # Step 2: Collect template meanings by role
    template_verbs = [s["meaning"] for s in template if s["role"] == "VERB"]
    template_nouns = [s["meaning"] for s in template if s["role"] == "NOUN"]
    template_quals = [s["meaning"] for s in template if s["role"] == "QUALITY"]
    template_refs = [s["meaning"] for s in template if s["role"] == "REF"]
    template_parts = [s["meaning"] for s in template if s["role"] == "PARTICLE"]
    template_preps = [s["meaning"] for s in template if s["role"] == "PREP"]

    # Step 3: Build sentence fragments based on mode
    fragments = []

    if mode == "FILTER":
        # TYAGA: "X through Y" pattern — resonant + template nouns
        if template_refs:
            fragments.append(template_refs[0].capitalize())
        for m in resonant_meanings[:3]:
            fragments.append(m)
        if template_verbs:
            fragments.append(template_verbs[0])
        if template_preps:
            fragments.append(template_preps[0])
        for m in template_nouns[:2]:
            fragments.append(m)

    elif mode == "VERB":
        # SANKHYA: Action-centered — verb + resonant objects
        if template_verbs:
            fragments.append(template_verbs[0].capitalize())
        for m in resonant_meanings[:3]:
            fragments.append(m)
        if template_parts:
            fragments.append(template_parts[0])
        if template_nouns:
            fragments.append(template_nouns[0])

    elif mode == "QUALITY":
        # TRAIGUNYA: Quality-centered — adjective + resonant nouns
        if template_quals:
            fragments.append(template_quals[0].capitalize())
        elif resonant_meanings:
            fragments.append(resonant_meanings[0].capitalize())
        for m in resonant_meanings[1:4]:
            fragments.append(m)
        if template_verbs:
            fragments.append(template_verbs[0])
        if template_refs:
            fragments.append(template_refs[0])

    elif mode == "CONTEXT":
        # VARNASHRAMA: Duty-centered — context + action + resonant
        if template_preps:
            fragments.append(template_preps[0].capitalize())
        for m in template_nouns[:2]:
            fragments.append(m)
        if template_verbs:
            fragments.append(template_verbs[0])
        for m in resonant_meanings[:3]:
            fragments.append(m)

    elif mode == "TARGET":
        # BRAHMAN: Goal-centered — resonant destination + template path
        for m in resonant_meanings[:2]:
            fragments.append(m.capitalize())
        if template_verbs:
            fragments.append(template_verbs[0])
        if template_preps:
            fragments.append(template_preps[0])
        for m in template_nouns[:2]:
            fragments.append(m)
        if template_quals:
            fragments.append(template_quals[0])

    elif mode == "CORE":
        # RAHASYA: Intimate — direct resonant words + template core
        for m in resonant_meanings[:2]:
            fragments.append(m.capitalize())
        if template_refs:
            fragments.append(template_refs[0])
        if template_verbs:
            fragments.append(template_verbs[0])
        for m in resonant_meanings[2:5]:
            fragments.append(m)

    elif mode == "CLOSURE":
        # SANJAYA: Conclusion — summary of resonant + closing template
        if template_parts:
            fragments.append(template_parts[0].capitalize())
        for m in resonant_meanings[:4]:
            fragments.append(m)
        if template_verbs:
            fragments.append(template_verbs[0])

    else:
        # Fallback: interleave resonant and template
        for m in resonant_meanings[:5]:
            fragments.append(m)

    # Step 4: Clean and join
    # Remove duplicates while preserving order
    seen = set()
    clean = []
    for f in fragments:
        fl = f.lower().strip()
        if fl and fl not in seen:
            seen.add(fl)
            clean.append(f.strip())

    if not clean:
        return " ".join(resonant_meanings[:5])

    return " ".join(clean)


# =============================================================================
# FULL PIPELINE: Input → Composed English
# =============================================================================


def maha_compose(text: str, top_n: int = 7, verbose: bool = False) -> Dict:
    """
    The complete pipeline: Input text → composed English response.

    Uses ONLY existing infrastructure:
        1. encode_text()     → RAMA coordinates
        2. resonate()        → ranked words with English meanings
        3. seed_to_words()   → attractor → verse routing
        4. verse_words()     → grammatical template
        5. route_to_section() → response mode
        6. compose()         → English output

    Returns full trace for analysis.
    """
    from vibe_core.mahamantra.adapters.compression import MahaCompression

    # Step 1: Encode
    coords = encode_text(text)
    if not coords:
        return {"input": text, "error": "no phonemes", "output": ""}

    # Step 2: Compress to seed (same as lotus_core)
    compressor = MahaCompression()
    compression = compressor.compress(text)
    seed = compression.seed

    # Step 3: Get resonant words (7D ranking)
    # resonate() returns List[RankedWord], not a response object
    ranked_words = resonate(text, top_n=top_n)

    resonant_dicts = [
        {
            "sanskrit": rw.word.sanskrit,
            "meanings": rw.word.meanings,
            "score": rw.total_score,
            "element": ELEMENT_NAMES[rw.word.first_element] if rw.word.first_element >= 0 else "?",
        }
        for rw in ranked_words
    ]

    # Step 4: Get attractor for verse routing
    from vibe_core.mahamantra.adapters.synth import create_synth

    synth = create_synth(preset="quantum")
    resonance_result = synth.resonate(seed)
    attractor = resonance_result.attractor

    # Step 5: Route to Kapitel 18 section (attractor + seed = two-stage)
    section_name, verse_num, section_idx = route_to_section(attractor, seed)

    # Step 6: Get verse template
    template = extract_template(GITA_CHAPTERS, verse_num)

    # Step 7: Compose
    output = compose(resonant_dicts, template, section_name)

    result = {
        "input": text,
        "seed": seed,
        "attractor": attractor,
        "section": section_name,
        "section_mode": SECTION_SIGNATURES.get(section_name, {}).get("mode", "?"),
        "verse": f"BG 18.{verse_num}",
        "guardian": "—",
        "resonant_words": [
            f"{rw.word.sanskrit}={rw.word.meanings[0] if rw.word.meanings else '?'} ({rw.total_score:.2f})"
            for rw in ranked_words
        ],
        "template_words": [f"{s['meaning']} [{s['role']}]" for s in template[:10]],
        "output": output,
    }

    if verbose:
        result["coords"] = coords[:16]
        result["template_full"] = template

    return result


# =============================================================================
# DEMO
# =============================================================================


def demo() -> None:
    """Run the prototype on diverse inputs."""
    inputs = [
        "What is devotion?",
        "fire and wisdom",
        "Krishna",
        "tell me about dharma",
        "love",
        "the meaning of sacrifice",
        "who am I?",
        "anger and peace",
        "Hare Krishna",
        "surrender everything",
    ]

    print("=" * 80)
    print("MAHA COMPOSE PROTOTYPE — Input → English Output")
    print("=" * 80)

    for text in inputs:
        r = maha_compose(text, verbose=False)
        print(f"\n{'─' * 80}")
        print(f"  INPUT:    {r['input']}")
        print(f"  SEED:     {r['seed']}  ATTRACTOR: {r['attractor']}")
        print(f"  SECTION:  {r['section']} ({r['section_mode']})  VERSE: {r['verse']}")
        print(f"  GUARDIAN: {r['guardian']}")
        print(f"  WORDS:    {', '.join(r['resonant_words'][:5])}")
        print(f"  TEMPLATE: {', '.join(r['template_words'][:5])}")
        print(f"  OUTPUT:   {r['output']}")

    print(f"\n{'=' * 80}")
    print("DONE — All outputs are DETERMINISTIC. Same input → always same output.")
    print("=" * 80)


if __name__ == "__main__":
    demo()
