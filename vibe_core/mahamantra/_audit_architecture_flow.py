#!/usr/bin/env python3
"""
ARCHITECTURE FLOW AUDIT - The REAL System Understanding
========================================================

CRITICAL INSIGHT: LLM DOES NOT EXIST IN BASE VERSION!
=====================================================
- MahaLLM ≠ LLM (completely different concept!)
- The Mahamantra ITSELF is the real "LLM" - the ultimate servant
- LLM is just an INTERPRETER layer (optional, external)
- The Substrate is the BRAIN

THE FLOW (Sravanam Principle - Everyone listens to Guru above):
===============================================================

Intent (Chat Input - Call & Response Kirtan)
    ↓
PRABHUPADA (Shakti - ALWAYS FIRST! The mercy that enables everything)
    ↓
MAHAMANTRA (The ultimate "servant" - meditates on intent, uses senses/tools)
    ↓
4 AVATARS (Receive delegation from Mahamantra)
    ↓
12 MAHAJANAS (Receive delegation from Avatars)
    ↓
Services (Naga, etc.) + Shadow Jivas (for detailed work)

GITA INTEGRATION:
=================
- Gita structures EVERYTHING
- Mahajanas and Guardians submit to Gita's structure
- Resonance-based Gita answers can happen MID-FLOW (not just at end!)
- Mahamantra can query Gita itself
- Semantic translation layers (Shabda, tensors) translate Gita wisdom
  to domain-specific language based on codebase context

RUNTIME ARCHITECTURE:
=====================
- Universal Maha Cell = The space where everything happens
- Sankirtan Chamber = The process inside the cell
- Everything holographic - comes together and plays together
- ALL happens in RAM at runtime - no messy filesystem!

BUILD (24) + RUNTIME (24) = LILA (48):
======================================
- BUILD: Phonetic encoding, tensor transformation, position calculation
- RUNTIME: Guardian execution, Gita consultation, response generation
- Currently we have BUILD but RUNTIME is incomplete

RUN: python -m vibe_core.mahamantra._audit_architecture_flow
"""

from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field

# Add project root to path
# __file__ = vibe_core/mahamantra/_audit_architecture_flow.py
# parent = vibe_core/mahamantra
# parent.parent = vibe_core
# parent.parent.parent = steward-protocol (PROJECT_ROOT)
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class ArchitectureComponent:
    """A component in the architecture."""
    name: str
    layer: str  # "prabhupada", "mahamantra", "avatar", "mahajana", "service"
    files: List[str] = field(default_factory=list)
    delegates_to: List[str] = field(default_factory=list)
    listens_to: Optional[str] = None  # Sravanam - who does this listen to?


def find_prabhupada_references() -> List[str]:
    """Find all files that reference Prabhupada (the Shakti layer)."""
    results = []
    mahamantra_dir = PROJECT_ROOT / "vibe_core" / "mahamantra"

    for py_file in mahamantra_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "prabhupada" in content.lower() or "shakti" in content.lower():
                results.append(str(py_file.relative_to(PROJECT_ROOT)))
        except Exception:
            pass
    return results


def find_avatar_references() -> Dict[str, List[str]]:
    """Find files referencing the 4 Avatars."""
    avatars = ["nrisimha", "bali", "shuka", "yamaraja"]  # Positions 12-15
    results = {a: [] for a in avatars}
    mahamantra_dir = PROJECT_ROOT / "vibe_core" / "mahamantra"

    for py_file in mahamantra_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore").lower()
            for avatar in avatars:
                if avatar in content:
                    results[avatar].append(str(py_file.relative_to(PROJECT_ROOT)))
        except Exception:
            pass
    return results


def find_gita_integration() -> List[str]:
    """Find all Gita-related files and integrations."""
    results = []
    mahamantra_dir = PROJECT_ROOT / "vibe_core" / "mahamantra"

    for py_file in mahamantra_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "gita" in content.lower():
                results.append(str(py_file.relative_to(PROJECT_ROOT)))
        except Exception:
            pass
    return results


def find_sankirtan_chamber() -> List[str]:
    """Find Sankirtan Chamber related files."""
    results = []
    mahamantra_dir = PROJECT_ROOT / "vibe_core" / "mahamantra"

    for py_file in mahamantra_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "sankirtan" in content.lower() or "chamber" in content.lower():
                results.append(str(py_file.relative_to(PROJECT_ROOT)))
        except Exception:
            pass
    return results


def find_maha_cell() -> List[str]:
    """Find Universal Maha Cell related files."""
    results = []
    vibe_core_dir = PROJECT_ROOT / "vibe_core"

    for py_file in vibe_core_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "maha_cell" in content.lower() or "mahacell" in content.lower() or "cell" in py_file.name.lower():
                results.append(str(py_file.relative_to(PROJECT_ROOT)))
        except Exception:
            pass
    return results


def find_shadow_jivas() -> List[str]:
    """Find Shadow Jiva related files (for detailed work delegation)."""
    results = []
    vibe_core_dir = PROJECT_ROOT / "vibe_core"

    for py_file in vibe_core_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "shadow" in content.lower() or "jiva" in content.lower():
                results.append(str(py_file.relative_to(PROJECT_ROOT)))
        except Exception:
            pass
    return results


def find_maha_attention() -> List[str]:
    """Find MahaAttention related files."""
    results = []
    vibe_core_dir = PROJECT_ROOT / "vibe_core"

    for py_file in vibe_core_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "attention" in content.lower() or "mahaattention" in content.lower():
                results.append(str(py_file.relative_to(PROJECT_ROOT)))
        except Exception:
            pass
    return results


def analyze_delegation_chain() -> Dict[str, Set[str]]:
    """Analyze who delegates to whom based on imports and references."""
    delegation = {}
    mahamantra_dir = PROJECT_ROOT / "vibe_core" / "mahamantra"

    for py_file in mahamantra_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            file_key = str(py_file.relative_to(PROJECT_ROOT))

            # Look for delegation patterns
            delegates_to = set()
            if "delegate" in content.lower():
                # Find what it delegates to
                if "mahajana" in content.lower():
                    delegates_to.add("mahajana")
                if "avatar" in content.lower():
                    delegates_to.add("avatar")
                if "naga" in content.lower():
                    delegates_to.add("naga")
                if "shadow" in content.lower():
                    delegates_to.add("shadow")

            if delegates_to:
                delegation[file_key] = delegates_to
        except Exception:
            pass

    return delegation


def main():
    """Run the architecture flow audit."""
    print("=" * 80)
    print("ARCHITECTURE FLOW AUDIT - Understanding the REAL System")
    print("=" * 80)
    print()

    print("CRITICAL: LLM DOES NOT EXIST IN BASE VERSION!")
    print("MahaLLM ≠ LLM - The Mahamantra ITSELF is the real 'LLM'")
    print()

    # 1. Prabhupada Layer (Shakti - ALWAYS FIRST)
    print("-" * 60)
    print("1. PRABHUPADA LAYER (Shakti - The mercy that enables all)")
    print("-" * 60)
    prabhupada_files = find_prabhupada_references()
    print(f"   Files referencing Prabhupada/Shakti: {len(prabhupada_files)}")
    for f in prabhupada_files[:10]:
        print(f"     - {f}")
    if len(prabhupada_files) > 10:
        print(f"     ... and {len(prabhupada_files) - 10} more")
    print()

    # 2. Avatar Layer
    print("-" * 60)
    print("2. AVATAR LAYER (4 Avatars - Positions 12-15)")
    print("-" * 60)
    avatar_refs = find_avatar_references()
    for avatar, files in avatar_refs.items():
        print(f"   {avatar.upper()}: {len(files)} files")
    print()

    # 3. Gita Integration
    print("-" * 60)
    print("3. GITA INTEGRATION (Structures EVERYTHING)")
    print("-" * 60)
    gita_files = find_gita_integration()
    print(f"   Files with Gita integration: {len(gita_files)}")
    for f in gita_files[:10]:
        print(f"     - {f}")
    if len(gita_files) > 10:
        print(f"     ... and {len(gita_files) - 10} more")
    print()

    # 4. Sankirtan Chamber
    print("-" * 60)
    print("4. SANKIRTAN CHAMBER (The process inside Maha Cell)")
    print("-" * 60)
    sankirtan_files = find_sankirtan_chamber()
    print(f"   Sankirtan/Chamber files: {len(sankirtan_files)}")
    for f in sankirtan_files[:10]:
        print(f"     - {f}")
    print()

    # 5. Maha Cell
    print("-" * 60)
    print("5. UNIVERSAL MAHA CELL (The space where everything happens)")
    print("-" * 60)
    cell_files = find_maha_cell()
    print(f"   Cell-related files: {len(cell_files)}")
    for f in cell_files[:10]:
        print(f"     - {f}")
    print()

    # 6. Shadow Jivas
    print("-" * 60)
    print("6. SHADOW JIVAS (For detailed work delegation)")
    print("-" * 60)
    shadow_files = find_shadow_jivas()
    print(f"   Shadow/Jiva files: {len(shadow_files)}")
    for f in shadow_files[:10]:
        print(f"     - {f}")
    if len(shadow_files) > 10:
        print(f"     ... and {len(shadow_files) - 10} more")
    print()

    # 7. MahaAttention
    print("-" * 60)
    print("7. MAHA ATTENTION (Attention mechanism)")
    print("-" * 60)
    attention_files = find_maha_attention()
    print(f"   Attention-related files: {len(attention_files)}")
    for f in attention_files[:10]:
        print(f"     - {f}")
    print()

    # 8. Delegation Chain Analysis
    print("-" * 60)
    print("8. DELEGATION CHAIN (Sravanam - who listens to whom)")
    print("-" * 60)
    delegation = analyze_delegation_chain()
    print(f"   Files with delegation patterns: {len(delegation)}")
    for file_path, delegates in list(delegation.items())[:10]:
        print(f"     {Path(file_path).name} → {', '.join(delegates)}")
    print()

    print("=" * 80)
    print("SUMMARY: The system is MUCH more complex than folder-based routing!")
    print("BUILD (24) exists, RUNTIME (24) is incomplete → LILA (48) not achieved")
    print("=" * 80)


if __name__ == "__main__":
    main()

