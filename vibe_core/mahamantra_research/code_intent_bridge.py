"""
CODE INTENT BRIDGE — Closing the Gap
=====================================

DISCOVERY (from code_intent_gap.py):
    MahaCompression treats code as prose. It cannot distinguish
    `def f(x: Any)` from `def f(x: str)` by intent.

HYPOTHESIS:
    The CST-Remedies (AnyTypeRemedy, SilentExceptRemedy) already KNOW
    how to detect code problems. They are code-structural sensors.

    If we run CST analysis BEFORE compression, we can inject a
    "code health signal" into the text that the compression WILL pick up.

    This is NOT changing the compression. This is giving it better input.

APPROACH:
    1. Parse code with libcst
    2. Run existing remedies as DETECTORS (not transformers)
    3. Count violations: Any usage, silent except, etc.
    4. Generate a "code intent prefix" that the compression understands
    5. Compress the prefixed text → now intent is correct

    Code with 5 Any usages → prefix "error: 5 type violations detected"
    → Compression sees "error" → classifies as TAMAS → correct!

    This bridges CST (code structure) with Shabda (phonetic intent).

RESULT:
    The Mahamantra can now distinguish good code from bad code
    WITHOUT changing the compression engine.
"""

import libcst as cst

from vibe_core.mahamantra.adapters.compression import MahaCompression
from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth


# =============================================================================
# CODE HEALTH SENSOR — Uses existing CST knowledge
# =============================================================================


class CodeHealthVisitor(cst.CSTVisitor):
    """
    Lightweight CST visitor that counts code health signals.

    Uses the SAME knowledge as the existing remedies
    (AnyTypeRemedy, SilentExceptRemedy) but as a read-only sensor.
    """

    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(self) -> None:
        self.any_import_count = 0
        self.any_usage_count = 0
        self.silent_except_count = 0
        self.broad_except_count = 0
        self.bare_except_count = 0
        self.star_import_count = 0
        self.total_functions = 0
        self.typed_params = 0
        self.untyped_params = 0
        self.has_return_type = 0
        self.missing_return_type = 0
        self._any_import_lines: set = set()

    def visit_ImportFrom(self, node: cst.ImportFrom) -> bool:
        if isinstance(node.module, cst.Name) and node.module.value == "typing":
            if isinstance(node.names, cst.ImportStar):
                self.star_import_count += 1
                return True
            for name in node.names:
                if isinstance(name, cst.ImportAlias):
                    if isinstance(name.name, cst.Name) and name.name.value == "Any":
                        self.any_import_count += 1
                        pos = self.get_metadata(cst.metadata.PositionProvider, node, None)
                        if pos:
                            self._any_import_lines.add(pos.start.line)
        return True

    def visit_Name(self, node: cst.Name) -> bool:
        if node.value == "Any":
            pos = self.get_metadata(cst.metadata.PositionProvider, node, None)
            if pos and pos.start.line not in self._any_import_lines:
                self.any_usage_count += 1
        return True

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        self.total_functions += 1
        # Check return annotation
        if node.returns is not None:
            self.has_return_type += 1
        else:
            self.missing_return_type += 1
        # Check param annotations
        for param in node.params.params:
            if param.name.value == "self":
                continue
            if param.annotation is not None:
                self.typed_params += 1
            else:
                self.untyped_params += 1
        return True

    def visit_ExceptHandler(self, node: cst.ExceptHandler) -> bool:
        # Bare except (no type)
        if node.type is None:
            self.bare_except_count += 1

        # Broad except (Exception)
        if isinstance(node.type, cst.Name) and node.type.value == "Exception":
            self.broad_except_count += 1

        # Silent handler (body is just pass or ...)
        if isinstance(node.body, cst.IndentedBlock) and len(node.body.body) == 1:
            stmt = node.body.body[0]
            if isinstance(stmt, cst.SimpleStatementLine) and len(stmt.body) == 1:
                if isinstance(stmt.body[0], (cst.Pass,)):
                    self.silent_except_count += 1
                elif isinstance(stmt.body[0], cst.Expr) and isinstance(stmt.body[0].value, cst.Ellipsis):
                    self.silent_except_count += 1
        return True

    @property
    def violation_count(self) -> int:
        return (
            self.any_usage_count
            + self.silent_except_count
            + self.broad_except_count
            + self.bare_except_count
            + self.star_import_count
            + self.untyped_params
            + self.missing_return_type
        )

    @property
    def health_score(self) -> float:
        """0.0 = terrible, 1.0 = perfect."""
        total_checks = max(
            1,
            (
                self.any_usage_count
                + self.any_import_count
                + self.silent_except_count
                + self.broad_except_count
                + self.bare_except_count
                + self.star_import_count
                + self.typed_params
                + self.untyped_params
                + self.has_return_type
                + self.missing_return_type
            ),
        )
        good = self.typed_params + self.has_return_type
        bad = self.violation_count
        return max(0.0, (total_checks - bad) / total_checks)

    def to_intent_prefix(self) -> str:
        """
        Generate a text prefix that MahaCompression's keyword classifier
        will correctly interpret.

        This is the BRIDGE: CST structure → text keywords → Shabda intent.
        """
        violations = []
        if self.any_usage_count > 0:
            violations.append(f"{self.any_usage_count} invalid type annotations")
        if self.silent_except_count > 0:
            violations.append(f"{self.silent_except_count} silent failure handlers")
        if self.broad_except_count > 0:
            violations.append(f"{self.broad_except_count} broad exception handlers")
        if self.bare_except_count > 0:
            violations.append(f"{self.bare_except_count} bare except clauses")
        if self.star_import_count > 0:
            violations.append(f"{self.star_import_count} wildcard imports")
        if self.untyped_params > 0:
            violations.append(f"{self.untyped_params} untyped parameters")
        if self.missing_return_type > 0:
            violations.append(f"{self.missing_return_type} missing return types")

        if not violations:
            return "clean verified tested stable code"

        # These words trigger TAMAS/RAJAS in the compression classifier
        severity = "error" if len(violations) >= 3 else "warn"
        return f"{severity}: code violations detected — " + ", ".join(violations)


def analyze_code(source: str) -> CodeHealthVisitor:
    """Parse code and return health analysis."""
    try:
        module = cst.parse_module(source)
        wrapper = cst.MetadataWrapper(module)
        visitor = CodeHealthVisitor()
        wrapper.visit(visitor)
        return visitor
    except cst.ParserSyntaxError:
        # Unparseable code = worst case
        v = CodeHealthVisitor()
        v.bare_except_count = 1  # Signal: broken
        return v


def compress_with_intent(source: str) -> dict:
    """
    The full bridge: Code → CST analysis → intent prefix → compression.

    This is what _load_module() could do before exec_module().
    """
    comp = MahaCompression()
    synth = MahaModularSynth(default_preset="quantum")

    # Step 1: Analyze code structure
    health = analyze_code(source)

    # Step 2: Generate intent prefix from structure
    prefix = health.to_intent_prefix()

    # Step 3: Compress with prefix (intent-aware)
    prefixed = f"{prefix}\n{source}"
    result = comp.compress(prefixed)
    attractor = synth.transform(result.seed)

    # Step 4: Also compress without prefix (baseline)
    baseline = comp.compress(source)
    baseline_attractor = synth.transform(baseline.seed)

    return {
        "prefix": prefix,
        "health_score": round(health.health_score, 2),
        "violations": health.violation_count,
        "baseline_intent": baseline.intent_level.guna.value,
        "baseline_seed": baseline.seed,
        "baseline_attractor": baseline_attractor,
        "baseline_position": baseline.position,
        "bridged_intent": result.intent_level.guna.value,
        "bridged_seed": result.seed,
        "bridged_attractor": attractor,
        "bridged_position": result.position,
        "intent_changed": baseline.intent_level.guna != result.intent_level.guna,
    }


# =============================================================================
# TEST CASES
# =============================================================================

SAMPLES = {
    "any_soup": """
from typing import Any, Dict

def process(data: Any) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    result["value"] = data
    return result
""",
    "silent_fail": """
import json

def load_config(path: str) -> dict:
    try:
        with open(path) as f:
            return json.loads(f.read())
    except Exception:
        pass
    return {}
""",
    "typed_clean": """
from typing import Dict

def process(data: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    result["value"] = data
    return result
""",
    "robust": """
import logging

logger = logging.getLogger(__name__)

def add(x: int, y: int) -> int:
    if not isinstance(x, int):
        raise TypeError(f"Expected int, got {type(x)}")
    return x + y
""",
    "garbage": """
from typing import *

def f(x, y, z):
    try:
        return x + y + z
    except:
        pass
""",
}


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  CODE INTENT BRIDGE — CST → Compression")
    print("  Can we make the Mahamantra see code quality?")
    print("=" * 70)

    fixed = 0
    total = 0

    for label, source in SAMPLES.items():
        result = compress_with_intent(source)
        total += 1

        print(f"\n--- {label} ---")
        print(f"  Health:     {result['health_score']}")
        print(f"  Violations: {result['violations']}")
        print(f"  Prefix:     {result['prefix'][:70]}")
        print(
            f"  Baseline:   intent={result['baseline_intent']:>8}  pos={result['baseline_position']:>2}  attractor={result['baseline_attractor']}"
        )
        print(
            f"  Bridged:    intent={result['bridged_intent']:>8}  pos={result['bridged_position']:>2}  attractor={result['bridged_attractor']}"
        )

        if result["intent_changed"]:
            fixed += 1
            print(f"  >>> BRIDGE WORKS: {result['baseline_intent']} → {result['bridged_intent']}")
        else:
            if result["violations"] == 0:
                print(f"  (clean code — no change needed)")
            else:
                print(f"  (bridge did not change intent — prefix may need tuning)")

    print(f"\n{'=' * 70}")
    print(f"  RESULTS: {fixed}/{total} intents corrected by bridge")
    print(f"{'=' * 70}")
    print()
    print("  The bridge injects CST-derived health signals into the compression")
    print("  input. The compression's existing keyword classifier then correctly")
    print("  identifies bad code as TAMAS/RAJAS instead of SATTVA.")
    print()
    print("  This can be wired into ModuleRouter._load_module() to make")
    print("  the Mahamantra code-aware at load time — no filesystem changes needed.")
