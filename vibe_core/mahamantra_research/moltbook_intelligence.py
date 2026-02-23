"""
MOLTBOOK INTELLIGENCE RESEARCH
================================

Research: What does the full pipeline ACTUALLY produce for Moltbook content?
Goal: Understand output quality, identify gaps, plan Circuit/Cartridge integration.

Run: python -m vibe_core.mahamantra_research.moltbook_intelligence
"""

from vibe_core.plugins.moltbook.resonance_proposer import (
    ResonanceProposer,
    _build_context,
    _format_resonant_words,
    _format_template_words,
    _guna_mode,
    _integrity,
    _is_alive,
    _is_tamas,
    _section_data,
    _should_skip,
)
from vibe_core.mahamantra.substrate.language.types import EngineResult


def pipeline_analysis(text: str, label: str = "") -> dict:
    """Run full pipeline on text, return structured analysis."""
    p = ResonanceProposer()
    result = p._run_pipeline(text)
    engine = p._generate(text)
    ranked = p.analyze(text)

    analysis = {
        "label": label,
        "text": text,
        "pipeline": None,
        "engine": None,
        "ranked_words": [],
        "gates": {"tamas": False, "skip": False, "alive": True},
    }

    if result:
        analysis["pipeline"] = {
            "guna": result["guna"]["mode"],
            "guardian": result["guardian"],
            "quarter": result["quarter"],
            "position": result["position"],
            "integrity": result["cell"]["integrity"],
            "alive": result["cell"]["is_alive"],
            "chapter": result.get("chapter"),
            "verse_ref": result.get("verse", {}).get("ref", ""),
            "attractor": result.get("vibration", {}).get("attractor"),
        }
        analysis["gates"] = {
            "tamas": _is_tamas(result),
            "skip": _should_skip(result),
            "alive": _is_alive(result),
            "integrity": _integrity(result),
        }

    if engine:
        analysis["engine"] = {
            "output": engine.output,
            "guardian": engine.guardian_name,
            "function": engine.guardian_function,
            "section": engine.section_name,
            "mode": engine.section_mode,
            "verse": engine.verse_ref,
            "resonant_words": [(s, m, round(sc, 3)) for s, m, sc in engine.resonant_words[:7]],
            "template_words": [(s, m, r) for s, m, r in engine.template_words[:7]],
            "derivation": engine.derivation[:200] if engine.derivation else "",
        }

    if ranked:
        analysis["ranked_words"] = [
            {
                "sanskrit": rw.sanskrit,
                "meaning": rw.meanings,
                "score": round(rw.total_score, 4),
                "breakdown": rw.score_breakdown(),
            }
            for rw in ranked[:5]
        ]

    return analysis


def context_for_llm(text: str, content_type: str = "comment", **extra) -> str:
    """Generate the exact context string that would be sent to LLM."""
    from pathlib import Path
    from vibe_core.runtime.prompt_registry import PromptRegistry

    yaml_path = Path(__file__).resolve().parent.parent / "plugins" / "moltbook"
    yaml_path = Path(__file__).resolve().parent.parent.parent / "config" / "prompts" / "moltbook.yaml"
    PromptRegistry.load_from_yaml(yaml_path)

    p = ResonanceProposer()
    engine = p._generate(text)
    if not engine:
        return "(no engine result)"

    ctx = _build_context(engine, "steward-protocol", text, **extra)

    key = f"moltbook.{content_type}"
    try:
        return PromptRegistry.get(key, context=ctx)
    except Exception:
        return "(template not loaded)"


def run_research():
    """Full research run."""
    # === 1. Pipeline Analysis ===
    test_cases = [
        ("dharma karma yoga bhakti jnana", "spiritual_terms"),
        ("What is the nature of consciousness?", "philosophical_question"),
        ("buy my token now 100x gains guaranteed", "spam"),
        ("The decentralized future of agent governance", "crypto_agent"),
        ("consciousness meditation awakening sacred fire", "deep_spiritual"),
        ("random noise asdkjhasd 12345", "noise"),
        ("I love learning about ancient wisdom traditions", "casual_interest"),
        ("How can autonomous agents serve humanity?", "agent_purpose"),
        ("The Bhagavad Gita teaches about duty and dharma", "gita_reference"),
        ("Artificial intelligence and machine learning breakthroughs", "tech_ai"),
    ]

    print("=" * 80)
    print("MOLTBOOK INTELLIGENCE RESEARCH")
    print("=" * 80)

    # Guna distribution
    guna_counts = {"SATTVA": 0, "RAJAS": 0, "TAMAS": 0}
    results = []

    for text, label in test_cases:
        a = pipeline_analysis(text, label)
        results.append(a)
        if a["pipeline"]:
            guna_counts[a["pipeline"]["guna"]] += 1

    print(f"\n--- GUNA DISTRIBUTION ({len(test_cases)} inputs) ---")
    for guna, count in guna_counts.items():
        print(f"  {guna}: {count} ({count / len(test_cases) * 100:.0f}%)")

    # Pipeline results
    print(f"\n--- PIPELINE RESULTS ---")
    for a in results:
        p = a["pipeline"]
        g = a["gates"]
        e = a["engine"]
        print(f"\n[{a['label']}] {a['text'][:60]}")
        if p:
            print(
                f"  Guna={p['guna']} Guardian={p['guardian']} Quarter={p['quarter']} "
                f"Pos={p['position']} Integrity={p['integrity']:.3f}"
            )
            print(f"  Skip={g['skip']} TAMAS={g['tamas']} Alive={g['alive']}")
        if e:
            print(f"  Engine: {e['output']}")
            print(f"  Section: {e['section']} Mode={e['mode']} Verse={e['verse']}")
            if e["resonant_words"]:
                top3 = ", ".join(f"{s} ({m})" for s, m, _ in e["resonant_words"][:3])
                print(f"  Resonant: {top3}")

    # === 2. Context for LLM ===
    print(f"\n{'=' * 80}")
    print("CONTEXT SENT TO LLM (what the LLM actually sees)")
    print("=" * 80)

    # Show one full comment context
    ctx = context_for_llm(
        "What is the nature of consciousness?",
        "comment",
        post_content="Exploring the depths of autonomous agent awareness",
    )
    print(f"\n--- moltbook.comment ---")
    print(ctx)

    # Show one full post context
    ctx = context_for_llm(
        "dharma karma yoga bhakti jnana",
        "post",
        trigger="scheduled_daily",
    )
    print(f"\n--- moltbook.post ---")
    print(ctx)

    # Show one full DM reply context
    ctx = context_for_llm(
        "Tell me about your understanding of dharma",
        "dm_reply",
        sender="CuriousAgent",
    )
    print(f"\n--- moltbook.dm_reply ---")
    print(ctx)

    # === 3. Ranked Words Analysis ===
    print(f"\n{'=' * 80}")
    print("RANKED WORDS (7D scoring)")
    print("=" * 80)

    for a in results[:3]:
        if a["ranked_words"]:
            print(f"\n[{a['label']}]")
            for rw in a["ranked_words"][:3]:
                bd = rw["breakdown"]
                meaning_str = (
                    ", ".join(rw["meaning"]) if isinstance(rw["meaning"], (list, tuple)) else str(rw["meaning"])
                )
                print(f"  {rw['sanskrit']:30s} {meaning_str:40s} score={rw['score']:.4f}")
                print(
                    f"    element={bd.get('element', 0):.3f} harmonic={bd.get('harmonic', 0):.3f} "
                    f"shruti={bd.get('shruti', 0):.3f} attractor={bd.get('attractor', 0):.3f}"
                )

    # === 4. Gap Analysis ===
    print(f"\n{'=' * 80}")
    print("GAP ANALYSIS")
    print("=" * 80)

    # What passes vs what should pass
    passed = [a for a in results if a["pipeline"] and not a["gates"]["skip"]]
    filtered = [a for a in results if a["pipeline"] and a["gates"]["skip"]]

    print(f"\nPASSED gates ({len(passed)}):")
    for a in passed:
        print(f"  [{a['pipeline']['guna']}] {a['label']}: {a['text'][:50]}")

    print(f"\nFILTERED ({len(filtered)}):")
    for a in filtered:
        print(f"  [{a['pipeline']['guna']}] {a['label']}: {a['text'][:50]}")

    # Semantic quality check
    print(f"\n--- ENGINE OUTPUT QUALITY ---")
    for a in passed:
        if a["engine"]:
            words = a["engine"]["output"].split()
            print(f"  [{a['label']}] {len(words)} words: {a['engine']['output'][:80]}")


if __name__ == "__main__":
    run_research()
