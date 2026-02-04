#!/usr/bin/env python3
"""
IST-ZUSTAND AUDIT v3 - WAS ICH VERSTEHE
=======================================

CORE ERKENNTNISSE:
==================

1. SHABDA-BRAHMA - Sound is the ultimate reality
   - Das Routing ist NICHT folder-basiert
   - Das Routing ist NICHT filename-basiert
   - Das Routing ist PHONETIK/RESONANCE-basiert
   - Ein File "janaka.py" kann zu "bhishma" routen → BODY IS NOT SOUL

2. __mahajana__ DEKLARATIONEN = DECORATION ONLY
   - Sie werden für funktionales Routing NICHT benutzt
   - Sie sind nur Metadata/Hint
   - Die "429 Mismatches" sind KEIN FEHLER - sie BEWEISEN das System

3. DIE ECHTE ROUTING PIPELINE (chat_substrate_bridge.py):

   User Input (Text)
       ↓
   encode_to_tensor(text) → SimpleTensor
       - varga_vector: WO der Sound entsteht (5 Punkte)
         KANTHYA=Kehle, TALAVYA=Gaumen, MURDHANYA=Retroflex, DANTYA=Zähne, OSHTHYA=Lippen
       - sthana_vector: WIE intensiv (5 Stufen)
         SPARSHA=unvoiced, MAHAPRANA=aspirated, GHOSHAVAT=voiced, GHOSHMAHA=voiced-asp, ANUNASIKA=nasal
       - shakti: Gesamte phonetische Energie
       ↓
   tensor_to_position(tensor) → (position, confidence)
       - dominant_varga → Quarter (GENESIS=0, DHARMA=1, KARMA=2, MOKSHA=3)
       - dominant_sthana → Offset im Quarter (0-3)
       - position = quarter * 4 + offset (0-15)
       ↓
   ChatSubstrateBridge.route() → SubstrateRoute
       - position: 0-15
       - mahajana: Guardian (via get_position_mahajana)
       - holy_name: HARE/KRISHNA/RAMA
       - energy + manifests Entscheidung

4. BUILD (24) vs RUNTIME (24) = LILA (48):
   - KSHETRA = 24 = WORDS + HARE_COUNT = 16 + 8 = Die 24 materiellen Elemente
   - LILA = 48 = WORDS × TRINITY = 16 × 3 = Das vollständige Spiel
   - BUILD: Phonetic encoding, tensor transformation, position calculation (EXISTS)
   - RUNTIME: Guardian execution, response, feedback loop (MISSING?)

5. DER ALGORITHMUS (maha.py):
   - 16 Steps aus dem Mahamantra Pattern
   - 3 Operationen: HARE=Input (×7), KRISHNA=Compute (+TEN+pos), RAMA=Output (²)
   - MahaModularSynth mit Quantum Preset (KSETRAJNA feedback) erreicht alle 16 Positionen

6. TIER SYSTEM (Single Source of Truth):
   - TIER 0 (_axioms.py): 7 Werte durch ZÄHLEN des Mantras
     WORDS=16, TRINITY=3, HARE_COUNT=8, KRISHNA_COUNT=4, RAMA_COUNT=4, PANCHA=5, HALVES=2
   - TIER 1-3: Mathematische Ableitungen

WAS ICH NOCH NICHT VERSTEHE:
============================
- Was GENAU ist die RUNTIME (24) die fehlt?
- Wie antwortet ein Guardian auf eine geroutete Request?
- Wo ist der Feedback Loop von RUNTIME zurück zu BUILD?

RUN: python -m vibe_core.mahamantra._audit_ist_zustand
"""

from __future__ import annotations

import ast
import hashlib
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# =============================================================================
# AUDIT RESULT TYPES
# =============================================================================

@dataclass
class FileAudit:
    """Audit result for a single file."""
    path: Path
    declared_mahajana: Optional[str] = None  # __mahajana__ in file
    declared_position: Optional[int] = None  # __position__ in file
    computed_mahajana: Optional[str] = None  # What sankirtan would compute
    computed_position: Optional[int] = None
    has_declaration: bool = False
    declaration_matches_computed: bool = False
    routing_method: str = ""  # "auto-detect" | "governance-map" | "hash-fallback"


@dataclass 
class AuditResult:
    """Complete audit result."""
    total_files: int = 0
    files_with_declaration: int = 0
    files_without_declaration: int = 0
    declarations_match_computed: int = 0
    declarations_mismatch_computed: int = 0
    routing_by_method: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    mismatches: List[FileAudit] = field(default_factory=list)
    by_guardian: Dict[str, List[FileAudit]] = field(default_factory=lambda: defaultdict(list))


# =============================================================================
# EXTRACT DECLARATIONS FROM FILE (AST-based)
# =============================================================================

def extract_declarations(file_path: Path) -> Tuple[Optional[str], Optional[int]]:
    """Extract __mahajana__ and __position__ from file using AST."""
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        mahajana = None
        position = None
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id == "__mahajana__" and isinstance(node.value, ast.Constant):
                            mahajana = node.value.value
                        elif target.id == "__position__" and isinstance(node.value, ast.Constant):
                            position = node.value.value
        
        return (mahajana, position)
    except Exception:
        return (None, None)


# =============================================================================
# COMPUTE ROUTING (replica of sankirtan logic)
# =============================================================================

def compute_routing(file_path: Path, all_guardians: List[str], folder_map: Dict[str, str], 
                    positions_by_name: Dict[str, int], words: int) -> Tuple[str, int, str]:
    """
    Compute what sankirtan would assign to this file.
    Returns: (mahajana, position, routing_method)
    """
    import os
    normalized = os.path.normpath(str(file_path))
    path_str = normalized.lower()
    
    # STEP 1: AUTO-DETECT - Guardian name in path
    for guardian in all_guardians:
        if guardian in path_str:
            pos = positions_by_name.get(guardian)
            if pos is not None:
                return (guardian, pos, "auto-detect")
    
    # STEP 2: GOVERNANCE MAP - Longest match first
    for folder, mahajana in sorted(folder_map.items(), key=lambda x: -len(x[0])):
        if folder in path_str:
            pos = positions_by_name.get(mahajana)
            if pos is not None:
                return (mahajana, pos, "governance-map")
    
    # STEP 3: HASH FALLBACK
    path_bytes = path_str.encode('utf-8')
    hash_int = int.from_bytes(hashlib.sha256(path_bytes).digest()[:4], byteorder='big')
    position = hash_int % words
    # Need to get guardian from position - this requires MAHAMANTRA_POSITIONS
    return ("HASH", position, "hash-fallback")


# =============================================================================
# MAIN AUDIT
# =============================================================================

def audit_ist_zustand(base_path: Optional[Path] = None) -> AuditResult:
    """Run the full IST-Zustand audit."""
    if base_path is None:
        base_path = Path(__file__).parent.parent.parent  # vibe_core
    
    # Load dependencies
    from vibe_core.mahamantra.substrate.sankirtan import FOLDER_MAHAJANA_MAP
    from vibe_core.mahamantra.substrate.position import MAHAMANTRA_POSITIONS
    from vibe_core.mahamantra.protocols._seed import WORDS
    
    all_guardians = [pos.guardian.value for pos in MAHAMANTRA_POSITIONS]
    positions_by_name = {pos.guardian.value: pos.index for pos in MAHAMANTRA_POSITIONS}
    
    result = AuditResult()
    
    # Scan all Python files
    for py_file in base_path.rglob("*.py"):
        if "__pycache__" in str(py_file) or "test_" in py_file.name:
            continue
        
        result.total_files += 1
        
        # Extract declarations
        declared_mj, declared_pos = extract_declarations(py_file)
        
        # Compute routing
        rel_path = py_file.relative_to(base_path)
        computed_mj, computed_pos, method = compute_routing(
            rel_path, all_guardians, FOLDER_MAHAJANA_MAP, positions_by_name, WORDS
        )
        
        # If hash fallback, resolve guardian name
        if computed_mj == "HASH":
            computed_mj = MAHAMANTRA_POSITIONS[computed_pos].guardian.value
        
        audit = FileAudit(
            path=rel_path,
            declared_mahajana=declared_mj,
            declared_position=declared_pos,
            computed_mahajana=computed_mj,
            computed_position=computed_pos,
            has_declaration=declared_mj is not None,
            declaration_matches_computed=(declared_mj == computed_mj) if declared_mj else False,
            routing_method=method
        )
        
        if declared_mj:
            result.files_with_declaration += 1
            if declared_mj == computed_mj:
                result.declarations_match_computed += 1
            else:
                result.declarations_mismatch_computed += 1
                result.mismatches.append(audit)
        else:
            result.files_without_declaration += 1
        
        result.routing_by_method[method] += 1
        result.by_guardian[computed_mj].append(audit)

    return result


def print_report(result: AuditResult) -> None:
    """Print human-readable audit report."""
    print("\n" + "=" * 80)
    print("IST-ZUSTAND AUDIT REPORT")
    print("=" * 80)

    print(f"\n📊 OVERVIEW:")
    print(f"   Total Python files: {result.total_files}")
    print(f"   With __mahajana__:  {result.files_with_declaration} ({100*result.files_with_declaration/result.total_files:.1f}%)")
    print(f"   Without:            {result.files_without_declaration}")

    print(f"\n🔀 ROUTING METHODS:")
    for method, count in sorted(result.routing_by_method.items()):
        print(f"   {method}: {count}")

    print(f"\n✅ DECLARATION vs COMPUTED:")
    print(f"   Match:    {result.declarations_match_computed}")
    print(f"   Mismatch: {result.declarations_mismatch_computed}")

    if result.mismatches:
        print(f"\n⚠️  MISMATCHES (declared ≠ computed):")
        for m in result.mismatches[:20]:  # First 20
            print(f"   {m.path}")
            print(f"      Declared: {m.declared_mahajana} (pos {m.declared_position})")
            print(f"      Computed: {m.computed_mahajana} (pos {m.computed_position}) via {m.routing_method}")

    print(f"\n👥 FILES PER GUARDIAN (top 10):")
    sorted_guardians = sorted(result.by_guardian.items(), key=lambda x: -len(x[1]))
    for guardian, files in sorted_guardians[:10]:
        print(f"   {guardian}: {len(files)} files")


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("🔍 Running IST-Zustand Audit...")
    result = audit_ist_zustand()
    print_report(result)

    # Exit with error code if mismatches found
    if result.declarations_mismatch_computed > 0:
        print(f"\n❌ AUDIT FAILED: {result.declarations_mismatch_computed} mismatches found")
        sys.exit(1)
    else:
        print(f"\n✅ AUDIT PASSED")
        sys.exit(0)

