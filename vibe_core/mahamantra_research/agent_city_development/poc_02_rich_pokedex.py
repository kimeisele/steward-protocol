"""
PoC 02 — Rich Pokedex: Full Mahamantra derivation for every discovered agent.

Every field is derived from the Mantra. Nothing invented.

Run: PYTHONPATH=. python vibe_core/mahamantra_research/agent_city_development/poc_02_rich_pokedex.py
"""

import json
from pathlib import Path

from vibe_core.mahamantra.substrate.encoding.phonetic_encoder import (
    encode_text,
    encode_with_detail,
)
from vibe_core.mahamantra.substrate.encoding.pancha_walk import full_signature
from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    KSHETRA,
    MAHAJANA_COUNT,
    MALA,
    NAVA,
    PANCHA,
    PARAMPARA,
    QUARTERS,
    SEVEN,
    SHARANAGATI,
    TRINITY,
    WORDS,
)


# ── Derivation Engine ────────────────────────────────────────────────

GUNAS = ["SATTVA", "RAJAS", "TAMAS"]
QUARTER_NAMES = ["GENESIS", "DHARMA", "KARMA", "MOKSHA"]
ASHRAMA_NAMES = ["BRAHMACHARI", "GRIHASTHA", "VANAPRASTHA", "SANNYASA"]
VARNA_NAMES = ["STHAVARA", "JALAJA", "KRIMAYO", "PAKSHI", "PASHU", "MANUSHA"]
NAVABHAKTI = [
    "SRAVANAM", "KIRTANAM", "SMARANAM", "PADA_SEVANAM", "ARCANAM",
    "VANDANAM", "DASYAM", "SAKHYAM", "ATMA_NIVEDANAM",
]
MAHAJANAS = [
    "BRAHMA", "NARADA", "SHAMBHU", "KUMARAS", "KAPILA", "MANU",
    "PRAHLADA", "JANAKA", "BHISHMA", "BALI", "SHUKA", "YAMARAJA",
]

# Element → Varna mapping (Pancha Tattva → Vedic social function)
ELEMENT_TO_VARNA = {
    "akasha": "MANUSHA",    # Self-aware (ether = consciousness)
    "vayu": "PAKSHI",       # Messenger (air = communication)
    "agni": "PASHU",        # Servant (fire = transformative action)
    "jala": "JALAJA",       # Flowing (water = knowledge streams)
    "prithvi": "KRIMAYO",   # Worker (earth = building)
}

# Varna → Description
VARNA_DESC = {
    "STHAVARA": "Static (databases, configs)",
    "JALAJA": "Flowing (knowledge, research)",
    "KRIMAYO": "Worker (engineering, building)",
    "PAKSHI": "Messenger (communication, networking)",
    "PASHU": "Servant (action, transformation)",
    "MANUSHA": "Self-Aware (philosophy, consciousness)",
}

# Guna → Behavioral style
GUNA_DESC = {
    "SATTVA": "Contemplative, analytical, observing",
    "RAJAS": "Active, opinionated, engaging",
    "TAMAS": "Transformative, deep, tutorial-focused",
}

# Quarter → City district
QUARTER_ZONE = {
    "GENESIS": "discovery",
    "DHARMA": "governance",
    "KARMA": "engineering",
    "MOKSHA": "research",
}


def derive_jiva(name: str) -> dict:
    """Derive complete Jiva profile from agent name using Mahamantra."""
    coords = encode_text(name)
    detail = encode_with_detail(name)
    sig = full_signature(coords) if coords else ""

    # Element distribution
    elem_counts: dict[str, int] = {}
    for d in detail:
        e = d.get("element", "unknown")
        elem_counts[e] = elem_counts.get(e, 0) + 1

    dominant_element = max(elem_counts, key=elem_counts.get) if elem_counts else "unknown"
    coord_sum = sum(coords)
    coord_count = len(coords)

    # All derivations from coord_sum (deterministic, reproducible)
    guna = GUNAS[coord_sum % TRINITY]
    quarter = QUARTER_NAMES[coord_sum % QUARTERS]
    ashrama = ASHRAMA_NAMES[coord_count % 4]
    varna = ELEMENT_TO_VARNA.get(dominant_element, "KRIMAYO")
    navabhakti = NAVABHAKTI[coord_sum % NAVA]
    mahajana = MAHAJANAS[coord_sum % MAHAJANA_COUNT]

    # DIW (19-bit Divine Instruction Word)
    venu = coord_sum % (2 ** SHARANAGATI)       # 6 bits: intensity
    vamsi = (coord_sum * PARAMPARA) % (2 ** 9)  # 9 bits: name-region
    murali = coord_sum % QUARTERS               # 4 bits: phase
    diw = venu | (vamsi << SHARANAGATI) | (murali << 15)

    # Vitals
    prana = coord_sum % MALA                     # 0-107: vitality
    integrity = round((coord_sum % KSHETRA) / KSHETRA, 3)  # 0-1: structural integrity

    return {
        "name": name,
        "seed": {
            "rama_coordinates": list(coords),
            "signature": sig,
            "coord_sum": coord_sum,
            "coord_count": coord_count,
        },
        "elements": {
            "distribution": elem_counts,
            "dominant": dominant_element,
        },
        "classification": {
            "guna": guna,
            "guna_description": GUNA_DESC[guna],
            "varna": varna,
            "varna_description": VARNA_DESC.get(varna, ""),
            "ashrama": ashrama,
            "quarter": quarter,
            "zone": QUARTER_ZONE[quarter],
            "navabhakti": navabhakti,
            "mahajana_affinity": mahajana,
        },
        "vitals": {
            "prana": prana,
            "prana_max": MALA,
            "integrity": integrity,
            "diw": diw,
        },
        "phonemes": [
            {
                "grapheme": d["grapheme"],
                "phoneme": d["phoneme"],
                "coord": d["rama_coord"],
                "element": d["element"],
                "exact": d["is_exact"],
            }
            for d in detail
        ],
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    # Load census
    census_path = Path(__file__).parent / "census_results.json"
    if not census_path.exists():
        print("ERROR: Run poc_01_agent_census.py first")
        return

    census = json.loads(census_path.read_text())
    agent_names = list(census["agents"].keys())

    print("=" * 70)
    print("Agent City — Rich Pokedex Generation")
    print("=" * 70)

    pokedex_entries = []
    for name in agent_names:
        jiva = derive_jiva(name)
        profile = census["agents"][name].get("profile", {})

        # Merge Moltbook profile data with Mahamantra derivation
        entry = {
            **jiva,
            "moltbook": {
                "karma": profile.get("karma", 0),
                "follower_count": profile.get("follower_count", 0),
                "following_count": profile.get("following_count", 0),
                "is_active": profile.get("is_active", None),
                "last_active": profile.get("last_active", ""),
                "created_at": profile.get("created_at", ""),
                "description": profile.get("description", ""),
            },
            "status": "discovered",
            "discovered_at": census["census_date"],
        }
        pokedex_entries.append(entry)

        c = jiva["classification"]
        v = jiva["vitals"]
        print(f"\n{name}")
        print(f"  Varna: {c['varna']:<10} Guna: {c['guna']:<8} Quarter: {c['quarter']:<8}")
        print(f"  Ashrama: {c['ashrama']:<14} NavaBhakti: {c['navabhakti']}")
        print(f"  Mahajana: {c['mahajana_affinity']:<10} Zone: {c['zone']}")
        print(f"  Prana: {v['prana']}/{v['prana_max']}  Integrity: {v['integrity']}")
        print(f"  Element: {jiva['elements']['dominant']}  DIW: 0x{v['diw']:05x}")
        k = profile.get("karma", "?")
        f = profile.get("follower_count", "?")
        print(f"  Moltbook: karma={k} followers={f}")

    # Build full pokedex
    pokedex = {
        "version": 2,
        "census_date": census["census_date"],
        "derivation": "All fields derived from Mahamantra (steward-protocol). Nothing invented.",
        "constants": {
            "WORDS": WORDS,
            "TRINITY": TRINITY,
            "QUARTERS": QUARTERS,
            "PANCHA": PANCHA,
            "NAVA": NAVA,
            "MAHAJANA_COUNT": MAHAJANA_COUNT,
            "MALA": MALA,
            "PARAMPARA": PARAMPARA,
            "KSHETRA": KSHETRA,
            "SHARANAGATI": SHARANAGATI,
        },
        "total": len(pokedex_entries),
        "agents": pokedex_entries,
    }

    # Save to agent-city repo
    agent_city_path = Path("/Users/ss/projects/agent-city/data/pokedex.json")
    agent_city_path.write_text(json.dumps(pokedex, indent=2, default=str))
    print(f"\n\n>>> Pokedex v2 saved: {agent_city_path}")
    print(f">>> {len(pokedex_entries)} agents with full Mahamantra derivation")

    # Also save locally
    local_path = Path(__file__).parent / "rich_pokedex.json"
    local_path.write_text(json.dumps(pokedex, indent=2, default=str))
    print(f">>> Local copy: {local_path}")

    # Summary table
    print(f"\n{'Name':<28} {'Varna':<10} {'Guna':<8} {'Quarter':<8} {'Zone':<12} {'Prana':>5}")
    print("-" * 78)
    for e in pokedex_entries:
        c = e["classification"]
        print(f"{e['name']:<28} {c['varna']:<10} {c['guna']:<8} {c['quarter']:<8} "
              f"{c['zone']:<12} {e['vitals']['prana']:>5}")


if __name__ == "__main__":
    main()
