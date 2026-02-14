"""
E2E HEALING TEST — Proves the cellular healing pipeline works on real codebase files.

Scans real project files for violations, heals them (dry-run), and reports results.
This is the proof that Phase 1 (Fragment → CSTRemedy → Verify → Maya-Sync) is alive.

Usage:
    python -m vibe_core.mahamantra.research.audit.e2e_healing_test
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple


def find_project_root() -> Path:
    """Walk up from this script to find steward-protocol root."""
    p = Path(__file__).resolve()
    while p.name != "steward-protocol" and p != p.parent:
        p = p.parent
    if not (p / "vibe_core").exists():
        print("ERROR: Cannot find vibe_core/", file=sys.stderr)
        sys.exit(1)
    return p


def scan_for_violations(root: Path) -> Dict[str, List[Tuple[Path, str]]]:
    """Scan real project files and find violations that have remedies."""
    from vibe_core.mahamantra.dharma.kumaras.engine import ShuddhiEngine
    from vibe_core.mahamantra.substrate.shuddhi import ShuddhiStatus

    engine = ShuddhiEngine()
    remedies = engine.list_remedies()
    print(f"Available remedies ({len(remedies)}): {', '.join(sorted(remedies))}")

    # Scan a selection of real files
    scan_dirs = [
        root / "vibe_core" / "naga",
        root / "vibe_core" / "ouroboros",
        root / "vibe_core" / "services",
    ]

    violations: Dict[str, List[Tuple[Path, str]]] = {}
    files_scanned = 0

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for py_file in sorted(scan_dir.rglob("*.py")):
            if py_file.name.startswith("test_") or "__pycache__" in str(py_file):
                continue
            if py_file.stat().st_size < 100:
                continue

            files_scanned += 1
            results = engine.scan_file(py_file)
            for r in results:
                if r.status == ShuddhiStatus.PURIFIED:
                    violations.setdefault(r.rule_id, []).append((py_file, r.rule_id))

    print(f"Files scanned: {files_scanned}")
    print(f"Violations found: {sum(len(v) for v in violations.values())}")
    for rule_id, vlist in sorted(violations.items(), key=lambda x: -len(x[1])):
        print(f"  {rule_id}: {len(vlist)} violations")

    return violations


def run_cellular_healing(root: Path, violations: Dict[str, List[Tuple[Path, str]]]) -> None:
    """Run the cellular healing pipeline on found violations (dry-run)."""
    from vibe_core.mahamantra.dharma.kumaras.fragment_parser import parse_file_to_fragments
    from vibe_core.mahamantra.dharma.kumaras.healing_intent import get_cellular_healer
    from vibe_core.mahamantra.substrate.shuddhi import ShuddhiStatus

    healer = get_cellular_healer()

    # Pick silent_failure as the test rule (simplest, most reliable)
    test_rule = "silent_failure"
    targets = violations.get(test_rule, [])

    if not targets:
        print(f"\nNo {test_rule} violations found. Trying other rules...")
        for rule_id, vlist in violations.items():
            if vlist:
                test_rule = rule_id
                targets = vlist
                break

    if not targets:
        print("No violations with remedies found. Nothing to heal.")
        return

    print(f"\n{'='*70}")
    print(f"CELLULAR HEALING E2E TEST — rule: {test_rule}")
    print(f"{'='*70}")

    # Test on first target file
    target_file = targets[0][0]
    print(f"Target: {target_file.relative_to(root)}")

    # Step 1: Parse into fragments
    frags = parse_file_to_fragments(target_file)
    print(f"Fragments extracted: {frags.count}")
    for f in frags.fragments:
        print(f"  [{f.fragment_type.name:8s}] {f.display_name} (L{f.line_start}-{f.line_end})")

    # Step 2: Heal (dry-run)
    print(f"\nHealing with rule '{test_rule}' (dry-run)...")
    results = healer.heal_file(target_file, test_rule, dry_run=True)

    purified = [r for r in results if r.shuddhi_result.status == ShuddhiStatus.PURIFIED]
    skipped = [r for r in results if r.shuddhi_result.status == ShuddhiStatus.SKIPPED]
    failed = [r for r in results if r.shuddhi_result.status == ShuddhiStatus.FAILED]

    print(f"\nResults:")
    print(f"  PURIFIED: {len(purified)}")
    print(f"  SKIPPED:  {len(skipped)}")
    print(f"  FAILED:   {len(failed)}")

    for f in failed:
        name = f.fragment.display_name if f.fragment else "?"
        print(f"  FAILED DETAIL: {name} — {f.shuddhi_result.message[:120]}")

    for p in purified:
        name = p.fragment.display_name if p.fragment else "?"
        print(f"\n  HEALED: {name}")
        if p.shuddhi_result.diff:
            # Show first 400 chars of diff
            print(f"  DIFF:")
            for line in p.shuddhi_result.diff.splitlines()[:15]:
                print(f"    {line}")

    # Verdict
    print(f"\n{'='*70}")
    if purified and not failed:
        print("VERDICT: PASS — Cellular healing pipeline works end-to-end.")
    elif purified and failed:
        print(f"VERDICT: PARTIAL — {len(purified)} healed, {len(failed)} failed.")
    elif failed:
        print(f"VERDICT: FAIL — {len(failed)} failures, 0 healed.")
    else:
        print("VERDICT: NO-OP — No violations found in fragments (all skipped).")
    print(f"{'='*70}")


def main():
    root = find_project_root()
    print(f"Project root: {root}")
    print()

    violations = scan_for_violations(root)
    run_cellular_healing(root, violations)


if __name__ == "__main__":
    main()
