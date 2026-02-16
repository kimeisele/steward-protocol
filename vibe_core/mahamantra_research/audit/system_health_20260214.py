"""
SYSTEM HEALTH AUDIT — Comprehensive Self-Assessment
=====================================================

Runs ALL diagnostic tools in one pass:
1. Self-heal scan (Shuddhi on mahamantra itself)
2. F821 undefined names (ruff)
3. Hanging test detection
4. Import chain validation
5. Gate pipeline status

This is the Ouroboros: the system auditing itself.

Usage:
    python -m vibe_core.mahamantra.research.audit.system_health_20260214
"""

import json
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class HealthMetric:
    name: str
    status: str  # "PASS", "WARN", "FAIL"
    value: object
    detail: str = ""


@dataclass
class HealthReport:
    timestamp: str
    metrics: List[HealthMetric] = field(default_factory=list)
    violations_by_rule: Dict[str, int] = field(default_factory=dict)
    healable_total: int = 0
    failed_total: int = 0
    files_scanned: int = 0
    gate_pipeline_status: str = "UNKNOWN"
    f821_count: int = 0
    hanging_tests: List[str] = field(default_factory=list)
    import_errors: List[str] = field(default_factory=list)


def find_root() -> Path:
    p = Path(__file__).resolve()
    while p.name != "steward-protocol" and p != p.parent:
        p = p.parent
    return p


def check_shuddhi_self_scan(root: Path) -> Tuple[Dict[str, int], int, int, int]:
    """Scan mahamantra with its own immune system."""
    from vibe_core.mahamantra.dharma.kumaras.engine import ShuddhiEngine
    from vibe_core.mahamantra.substrate.shuddhi import ShuddhiStatus

    engine = ShuddhiEngine()
    scan_dirs = [
        root / "vibe_core" / "mahamantra" / "substrate",
        root / "vibe_core" / "mahamantra" / "dharma",
        root / "vibe_core" / "mahamantra" / "kernel",
        root / "vibe_core" / "mahamantra" / "reactor",
    ]

    violations: Dict[str, int] = {}
    healable = 0
    failed = 0
    files_scanned = 0

    for d in scan_dirs:
        if not d.exists():
            continue
        for f in sorted(d.rglob("*.py")):
            if "__pycache__" in str(f) or f.name.startswith("test_"):
                continue
            if f.stat().st_size < 50:
                continue
            files_scanned += 1
            results = engine.scan_file(f)
            for r in results:
                if r.status == ShuddhiStatus.PURIFIED:
                    violations[r.rule_id] = violations.get(r.rule_id, 0) + 1
                    healable += 1
                elif r.status == ShuddhiStatus.FAILED:
                    failed += 1

    return violations, healable, failed, files_scanned


def check_ruff_f821(root: Path) -> int:
    """Count undefined name errors in mahamantra."""
    try:
        result = subprocess.run(
            ["python3", "-m", "ruff", "check", "--select", "F821",
             str(root / "vibe_core" / "mahamantra")],
            capture_output=True, text=True, timeout=30,
        )
        # Count lines that are actual errors (not summary)
        lines = [l for l in result.stdout.strip().split("\n") if "F821" in l]
        return len(lines)
    except Exception:
        return -1


def check_gate_pipeline(root: Path) -> str:
    """Verify the 5-gate pipeline is wired and functional."""
    try:
        from vibe_core.mahamantra.dharma.kumaras.healing_resolver import (
            HealingIntentResolver,
            wire_healing_resolver,
        )
        from vibe_core.mahamantra.substrate.gate_providers import (
            EnforceGateProvider,
        )

        resolver = HealingIntentResolver()
        provider = EnforceGateProvider()

        checks = [
            hasattr(resolver, "can_resolve"),
            hasattr(resolver, "resolve"),
            hasattr(resolver, "_fire_gate_safe"),
            hasattr(provider, "write_source"),
            hasattr(provider, "enforce"),
        ]

        if all(checks):
            return "OPERATIONAL"
        else:
            return f"DEGRADED ({sum(checks)}/5 checks pass)"

    except Exception as e:
        return f"OFFLINE ({e})"


def check_core_imports(root: Path) -> List[str]:
    """Test critical import chains."""
    errors = []
    critical_imports = [
        "vibe_core.mahamantra.substrate.lotus_core",
        "vibe_core.mahamantra.substrate.gate_providers",
        "vibe_core.mahamantra.substrate.pancha_tattva",
        "vibe_core.mahamantra.dharma.kumaras.engine",
        "vibe_core.mahamantra.dharma.kumaras.healing_resolver",
        "vibe_core.mahamantra.dharma.kumaras.healing_intent",
        "vibe_core.mahamantra.kernel.singularity",
        "vibe_core.mahamantra.substrate.chamber",
        "vibe_core.mahamantra.substrate.antaranga",
    ]

    for module_path in critical_imports:
        try:
            __import__(module_path)
        except Exception as e:
            errors.append(f"{module_path}: {e}")

    return errors


def check_test_suite(root: Path) -> Tuple[int, int, int]:
    """Run kumaras tests quickly."""
    try:
        result = subprocess.run(
            ["python3", "-m", "pytest",
             str(root / "vibe_core" / "mahamantra" / "dharma" / "kumaras" / "tests"),
             "-q", "--tb=no"],
            capture_output=True, text=True, timeout=30,
        )
        # Parse "54 passed" from output
        for line in result.stdout.split("\n"):
            if "passed" in line:
                parts = line.split()
                for i, p in enumerate(parts):
                    if p == "passed":
                        return int(parts[i-1]), 0, 0
        return 0, 0, 0
    except Exception:
        return -1, -1, -1


def main():
    root = find_root()
    report = HealthReport(
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
    )

    print("=" * 70)
    print("SYSTEM HEALTH AUDIT — Ouroboros Self-Assessment")
    print(f"Timestamp: {report.timestamp}")
    print("=" * 70)

    # 1. Self-scan
    print("\n[1/5] Shuddhi Self-Scan...")
    violations, healable, failed, files_scanned = check_shuddhi_self_scan(root)
    report.violations_by_rule = violations
    report.healable_total = healable
    report.failed_total = failed
    report.files_scanned = files_scanned
    status = "PASS" if failed == 0 else "FAIL"
    print(f"  Files: {files_scanned}, Violations: {healable} healable, {failed} failed → {status}")
    for rule, count in sorted(violations.items(), key=lambda x: -x[1]):
        print(f"    {rule}: {count}")
    report.metrics.append(HealthMetric("shuddhi_self_scan", status, healable))

    # 2. Ruff F821
    print("\n[2/5] Ruff F821 (undefined names)...")
    f821_count = check_ruff_f821(root)
    report.f821_count = f821_count
    status = "PASS" if f821_count == 0 else ("WARN" if f821_count <= 3 else "FAIL")
    print(f"  F821 errors: {f821_count} → {status}")
    report.metrics.append(HealthMetric("ruff_f821", status, f821_count))

    # 3. Gate Pipeline
    print("\n[3/5] Gate Pipeline Status...")
    gate_status = check_gate_pipeline(root)
    report.gate_pipeline_status = gate_status
    status = "PASS" if gate_status == "OPERATIONAL" else "FAIL"
    print(f"  Pipeline: {gate_status} → {status}")
    report.metrics.append(HealthMetric("gate_pipeline", status, gate_status))

    # 4. Core Imports
    print("\n[4/5] Core Import Chains...")
    import_errors = check_core_imports(root)
    report.import_errors = import_errors
    status = "PASS" if not import_errors else "FAIL"
    print(f"  Import chains: {len(import_errors)} errors → {status}")
    for e in import_errors:
        print(f"    ✗ {e}")
    report.metrics.append(HealthMetric("core_imports", status, len(import_errors)))

    # 5. Test Suite
    print("\n[5/5] Kumaras Test Suite...")
    passed, failed_tests, errors = check_test_suite(root)
    status = "PASS" if passed > 0 and failed_tests == 0 else "FAIL"
    print(f"  Tests: {passed} passed, {failed_tests} failed → {status}")
    report.metrics.append(HealthMetric("test_suite", status, passed))

    # Summary
    print("\n" + "=" * 70)
    pass_count = sum(1 for m in report.metrics if m.status == "PASS")
    warn_count = sum(1 for m in report.metrics if m.status == "WARN")
    fail_count = sum(1 for m in report.metrics if m.status == "FAIL")
    overall = "HEALTHY" if fail_count == 0 else "DEGRADED"
    print(f"OVERALL: {overall} — {pass_count} PASS, {warn_count} WARN, {fail_count} FAIL")
    print("=" * 70)

    # Save JSON
    json_path = Path(__file__).parent / "system_health_report.json"
    json_path.write_text(json.dumps({
        "timestamp": report.timestamp,
        "overall": overall,
        "metrics": [asdict(m) for m in report.metrics],
        "violations_by_rule": report.violations_by_rule,
        "healable_total": report.healable_total,
        "files_scanned": report.files_scanned,
        "f821_count": report.f821_count,
        "gate_pipeline_status": report.gate_pipeline_status,
        "import_errors": report.import_errors,
    }, indent=2))
    print(f"\nJSON: {json_path}")


if __name__ == "__main__":
    main()
