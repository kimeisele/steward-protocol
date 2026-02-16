"""
SANKHYA AUDIT — Map the 24+2 Tattvas onto the actual codebase.
================================================================

For each of the 24 material elements + 2 transcendental:
  - Does a PROTOCOL exist? (definition)
  - Does an IMPLEMENTATION exist? (working code)
  - Does LEGACY code exist that COULD be adapted? (absorption candidate)
  - What's MISSING?

Run: python -m vibe_core.mahamantra.research.audit.sankhya_audit
"""

from __future__ import annotations

import ast
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[4]  # steward-protocol/
VIBE = REPO / "vibe_core"
MAHA = VIBE / "mahamantra"


@dataclass
class TattvaMapping:
    number: int
    sanskrit: str
    english: str
    category: str  # mahabhuta, tanmatra, jnanendriya, karmendriya, antahkarana, transcendental
    software_domain: str
    protocol_files: List[str] = field(default_factory=list)
    impl_files: List[str] = field(default_factory=list)
    legacy_candidates: List[str] = field(default_factory=list)
    status: str = "MISSING"  # MISSING, PROTOCOL_ONLY, LEGACY_ONLY, PARTIAL, WIRED


# === THE 24+2 TATTVAS ===

TATTVAS: List[TattvaMapping] = [
    # A. 5 Mahabhutas (Gross Elements) — the physical substrate
    TattvaMapping(1, "Prthvi", "Earth", "mahabhuta", "Persistent storage, DB, filesystem"),
    TattvaMapping(2, "Jala", "Water", "mahabhuta", "Data flow, streams, pipes"),
    TattvaMapping(3, "Tejas", "Fire", "mahabhuta", "Computation, transformation, CPU"),
    TattvaMapping(4, "Vayu", "Air", "mahabhuta", "Events, signals, messages"),
    TattvaMapping(5, "Akasa", "Ether", "mahabhuta", "Network, address space, namespace"),

    # B. 5 Tanmatras (Subtle Elements) — sense objects
    TattvaMapping(6, "Gandha", "Smell", "tanmatra", "Code smells, entropy, patterns"),
    TattvaMapping(7, "Rasa", "Taste", "tanmatra", "Test results, validation outcomes"),
    TattvaMapping(8, "Rupa", "Form", "tanmatra", "AST, code structure, types"),
    TattvaMapping(9, "Sparsa", "Touch", "tanmatra", "File changes, git diffs, state mutations"),
    TattvaMapping(10, "Sabda", "Sound", "tanmatra", "Logs, events, signals, exceptions"),

    # C. 5 Jnanendriyas (Knowledge Senses) — input sensors
    TattvaMapping(11, "Caksu", "Eye", "jnanendriya", "Code analysis, AST parsing, static analysis"),
    TattvaMapping(12, "Srotra", "Ear", "jnanendriya", "Log listener, event subscriber, signal handler"),
    TattvaMapping(13, "Ghrana", "Nose", "jnanendriya", "Entropy detector, code smell scanner"),
    TattvaMapping(14, "Jihva", "Tongue", "jnanendriya", "Test runner, type checker, validator"),
    TattvaMapping(15, "Tvak", "Skin", "jnanendriya", "Filesystem watcher, git monitor, state observer"),

    # D. 5 Karmendriyas (Action Senses) — output actuators
    TattvaMapping(16, "Vak", "Voice", "karmendriya", "Output generation, response composition, logging"),
    TattvaMapping(17, "Pani", "Hands", "karmendriya", "File operations, code editing, transformation"),
    TattvaMapping(18, "Pada", "Feet", "karmendriya", "Navigation, routing, import resolution"),
    TattvaMapping(19, "Payu", "Excretion", "karmendriya", "Garbage collection, cleanup, cache eviction"),
    TattvaMapping(20, "Upastha", "Generation", "karmendriya", "Process spawning, cell creation, code generation"),

    # E. Antahkarana (Internal Instruments)
    TattvaMapping(21, "Manas", "Mind", "antahkarana", "Central coordinator, accepts/rejects, routes input to buddhi"),
    TattvaMapping(22, "Buddhi", "Intelligence", "antahkarana", "Decision engine, analysis, Lotus pipeline"),
    TattvaMapping(23, "Ahankara", "False Ego", "antahkarana", "Identity module, ownership, position claims"),
    TattvaMapping(24, "Pradhana", "Unmanifested", "antahkarana", "Seed constants, axioms, unmanifested potential"),

    # F. Transcendental
    TattvaMapping(25, "Jiva", "Soul", "transcendental", "The user, the developer, the conscious observer"),
    TattvaMapping(26, "Paramatma", "Supersoul", "transcendental", "Krishna/Mahamantra — the knower of ALL fields"),
]


def scan_file_for_keywords(filepath: Path, keywords: List[str]) -> bool:
    """Check if a file contains any of the keywords (case-insensitive)."""
    try:
        content = filepath.read_text(errors="ignore").lower()
        return any(kw.lower() in content for kw in keywords)
    except Exception:
        return False


def count_lines(filepath: Path) -> int:
    try:
        return sum(1 for _ in filepath.open(errors="ignore"))
    except Exception:
        return 0


def find_files_with_keywords(root: Path, keywords: List[str], exclude_dirs: set = None) -> List[Tuple[str, int]]:
    """Find .py files containing keywords. Returns (relative_path, line_count)."""
    if exclude_dirs is None:
        exclude_dirs = {"__pycache__", ".git", "node_modules", ".benchmarks"}

    results = []
    for py_file in sorted(root.rglob("*.py")):
        if any(d in py_file.parts for d in exclude_dirs):
            continue
        if scan_file_for_keywords(py_file, keywords):
            rel = str(py_file.relative_to(REPO))
            results.append((rel, count_lines(py_file)))
    return results


def map_tattva(t: TattvaMapping) -> TattvaMapping:
    """Map a single tattva to existing code."""

    # Keywords to search for each tattva
    keyword_map: Dict[int, Tuple[List[str], List[str], List[str]]] = {
        # (protocol_keywords, impl_keywords, legacy_keywords)

        # Mahabhutas
        1: (["mahabhuta", "prthvi", "earth"], ["sqlite", "db_path", "flush"], ["ledger", "store"]),
        2: (["jala", "water", "stream"], ["pipeline", "data_flow"], ["conveyor", "stream"]),
        3: (["tejas", "fire", "compute"], ["lotus_core", "__call__", "pipeline"], ["kernel_impl", "execute"]),
        4: (["vayu", "air", "signal"], ["event_bus", "broadcast", "emit"], ["signal_bus", "event_bus"]),
        5: (["akasa", "ether", "namespace"], ["cell_router", "address", "position"], ["topology", "network"]),

        # Tanmatras
        6: (["gandha", "smell", "entropy"], ["entropy", "code_smell"], ["ouroboros", "violation"]),
        7: (["rasa", "taste", "validation"], ["test_result", "validate"], ["vajra", "harness"]),
        8: (["rupa", "form", "ast"], ["parse", "fragment", "ast"], ["loaders", "parser"]),
        9: (["sparsa", "touch", "diff"], ["git_diff", "file_change", "mutation"], ["git", "watcher"]),
        10: (["sabda", "sound", "log"], ["log_sentinel", "listener"], ["logging", "event"]),

        # Jnanendriyas
        11: (["caksu", "eye", "jnanendriya"], ["code_analysis", "static_analysis", "scanner"], ["analyst", "architecture_tool"]),
        12: (["srotra", "ear", "jnanendriya"], ["sravanam", "listener", "subscriber"], ["beat_subscriber", "diw_subscriber"]),
        13: (["ghrana", "nose", "jnanendriya"], ["entropy", "smell", "detector"], ["shuddhi", "watchman"]),
        14: (["jihva", "tongue", "jnanendriya"], ["test_runner", "type_check", "validator"], ["vajra", "pytest"]),
        15: (["tvak", "skin", "jnanendriya"], ["file_watcher", "state_observer", "monitor"], ["io_sentinel", "state_service"]),

        # Karmendriyas
        16: (["vak", "voice", "karmendriya"], ["compose", "generate", "output"], ["renderer", "scribe"]),
        17: (["pani", "hands", "karmendriya"], ["file_op", "edit", "transform"], ["file_operator", "io_service"]),
        18: (["pada", "feet", "karmendriya"], ["router", "navigate", "import_resolution"], ["layered_router", "routing"]),
        19: (["payu", "excretion", "karmendriya"], ["gc", "cleanup", "evict", "prune"], ["garbage_collect", "prune"]),
        20: (["upastha", "generation", "karmendriya"], ["spawn", "create_cell", "generate"], ["process_manager", "agent_birth"]),

        # Antahkarana
        21: (["manas", "mind", "antahkarana"], ["mantra_kernel", "intent", "accept_reject"], ["manas", "cortex"]),
        22: (["buddhi", "intelligence", "antahkarana"], ["lotus_core", "__call__", "pipeline_cache"], ["kernel_impl", "execute"]),
        23: (["ahankara", "ego", "identity"], ["__mahajana__", "__position__", "__genesis__"], ["identity", "manifest"]),
        24: (["pradhana", "unmanifested", "avyakta"], ["seed.py", "PARAMPARA", "axiom"], ["seed", "constant"]),

        # Transcendental
        25: (["jiva", "soul", "ksetrajna"], ["user", "developer", "observer"], []),
        26: (["paramatma", "supersoul", "krishna"], ["mahamantra", "lotus", "singularity"], []),
    }

    proto_kw, impl_kw, legacy_kw = keyword_map.get(t.number, ([], [], []))

    # Search in mahamantra/protocols/ for protocol definitions
    if proto_kw:
        t.protocol_files = [
            f for f, _ in find_files_with_keywords(MAHA / "protocols", proto_kw)
        ]

    # Search in mahamantra/ (excluding protocols/ and research/) for implementations
    if impl_kw:
        for subdir in ["substrate", "kernel", "dharma", "services", "reactor", "net"]:
            p = MAHA / subdir
            if p.exists():
                t.impl_files.extend([
                    f for f, _ in find_files_with_keywords(p, impl_kw)
                ])

    # Search in vibe_core/ (excluding mahamantra/) for legacy candidates
    if legacy_kw:
        for item in sorted(VIBE.iterdir()):
            if item.name == "mahamantra" or not item.is_dir():
                continue
            if item.name in {"__pycache__", ".benchmarks"}:
                continue
            t.legacy_candidates.extend([
                f for f, _ in find_files_with_keywords(item, legacy_kw)
            ])
        # Also check root files
        for py in sorted(VIBE.glob("*.py")):
            if scan_file_for_keywords(py, legacy_kw):
                t.legacy_candidates.append(str(py.relative_to(REPO)))

    # Determine status
    has_proto = len(t.protocol_files) > 0
    has_impl = len(t.impl_files) > 0
    has_legacy = len(t.legacy_candidates) > 0

    if has_proto and has_impl:
        t.status = "WIRED" if not has_legacy else "PARTIAL"  # PARTIAL = impl exists but legacy not absorbed
    elif has_proto and not has_impl:
        t.status = "PROTOCOL_ONLY"
    elif not has_proto and has_legacy:
        t.status = "LEGACY_ONLY"
    elif not has_proto and not has_impl and not has_legacy:
        t.status = "MISSING"
    else:
        t.status = "PARTIAL"

    return t


def run_audit() -> List[TattvaMapping]:
    """Run the full 24+2 audit."""
    print("SANKHYA AUDIT — Mapping 24+2 Tattvas to Codebase")
    print("=" * 60)
    print()

    results = []
    for t in TATTVAS:
        t = map_tattva(t)
        results.append(t)

    # Print by category
    categories = [
        ("A. MAHABHUTAS (Gross Elements — Physical Substrate)", "mahabhuta"),
        ("B. TANMATRAS (Subtle Elements — Sense Objects)", "tanmatra"),
        ("C. JNANENDRIYAS (Knowledge Senses — Input Sensors)", "jnanendriya"),
        ("D. KARMENDRIYAS (Action Senses — Output Actuators)", "karmendriya"),
        ("E. ANTAHKARANA (Internal Instruments)", "antahkarana"),
        ("F. TRANSCENDENTAL", "transcendental"),
    ]

    status_counts = {"MISSING": 0, "PROTOCOL_ONLY": 0, "LEGACY_ONLY": 0, "PARTIAL": 0, "WIRED": 0}

    for title, cat in categories:
        print(f"\n{title}")
        print("-" * 60)
        for t in results:
            if t.category != cat:
                continue
            status_counts[t.status] += 1
            icon = {
                "MISSING": "  ",
                "PROTOCOL_ONLY": "P ",
                "LEGACY_ONLY": "L ",
                "PARTIAL": "PL",
                "WIRED": "OK",
            }[t.status]
            print(f"  [{icon}] {t.number:2d}. {t.sanskrit:<12s} ({t.english:<12s}) → {t.software_domain}")
            if t.protocol_files:
                for f in t.protocol_files[:3]:
                    print(f"       P: {f}")
            if t.impl_files:
                for f in t.impl_files[:3]:
                    print(f"       I: {f}")
            if t.legacy_candidates:
                shown = t.legacy_candidates[:3]
                more = len(t.legacy_candidates) - 3
                for f in shown:
                    print(f"       L: {f}")
                if more > 0:
                    print(f"       L: ... +{more} more")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  WIRED (protocol + impl):     {status_counts['WIRED']}")
    print(f"  PARTIAL (some pieces):       {status_counts['PARTIAL']}")
    print(f"  PROTOCOL_ONLY (no impl):     {status_counts['PROTOCOL_ONLY']}")
    print(f"  LEGACY_ONLY (no protocol):   {status_counts['LEGACY_ONLY']}")
    print(f"  MISSING (nothing):           {status_counts['MISSING']}")
    print()

    # The critical question
    jnana = [t for t in results if t.category == "jnanendriya"]
    jnana_wired = sum(1 for t in jnana if t.status in ("WIRED", "PARTIAL"))
    print(f"SENSES WIRED: {jnana_wired}/5 Jnanendriyas")
    print(f"  → Lotus is {'SEEING' if jnana_wired >= 3 else 'BLIND' if jnana_wired == 0 else 'SQUINTING'}")

    karma = [t for t in results if t.category == "karmendriya"]
    karma_wired = sum(1 for t in karma if t.status in ("WIRED", "PARTIAL"))
    print(f"ACTUATORS WIRED: {karma_wired}/5 Karmendriyas")
    print(f"  → Lotus {'CAN ACT' if karma_wired >= 3 else 'IS PARALYZED' if karma_wired == 0 else 'CAN TWITCH'}")

    antah = [t for t in results if t.category == "antahkarana"]
    antah_wired = sum(1 for t in antah if t.status in ("WIRED", "PARTIAL"))
    print(f"INTERNAL ORGANS: {antah_wired}/4 Antahkarana")

    # Legacy absorption potential
    total_legacy = sum(len(t.legacy_candidates) for t in results)
    print(f"\nLEGACY ABSORPTION CANDIDATES: {total_legacy} files")
    print("  → These could become senses via Adapter pattern")

    return results


if __name__ == "__main__":
    run_audit()
