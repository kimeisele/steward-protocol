"""
MISSING MAHAJANA REMEDY - Brings Orphans Into the Fold.

"yānti deva-vratā devān pitṝn yānti pitṛ-vratāḥ
bhūtāni yānti bhūtejyā yānti mad-yājino 'pi mām"

"Those who worship the demigods will go to the demigods;
those who worship the ancestors go to the ancestors;
those who worship ghosts go to the ghosts;
and those who worship Me will come to Me."
— Bhagavad Gita 9.25

DETECTION: Files without __mahajana__ declaration (orphans)
SURGERY: Inject Mahajana DNA via Sankirtan pattern

THE PANCHA TATTVA OF ADOPTION:
    CHAITANYA:  The orphan file receives its identity
    NITYANANDA: Sankirtan carries the injection logic
    ADVAITA:    analyze_source() bridges content → Mahajana
    GADADHARA:  CST Module transformation flows the DNA
    SRIVASA:    Path-based governance determines position

ADOPTION ALGORITHM (Lila Migration):
    1. ANALYZE: Scan file content for keywords/patterns
    2. INFER: Map patterns to Mahajana position
    3. COMPUTE: Generate valid genesis byte
    4. INJECT: Insert DNA block after docstring/future imports

MAHAJANA INFERENCE (from lila/adoption.py):
    - "test_", "assert" → yamaraja (Position 15, judgment)
    - "create", "init", "new" → brahma (Position 1, creation)
    - "log", "emit", "send" → narada (Position 2, communication)
    - "delete", "clean", "remove" → shambhu (Position 3, destruction)
    - "compile", "parse", "scan" → prithu (Position 4, compilation)
    - "execute", "run", "action" → parashurama (Position 8, execution)
    - etc.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"  # Position 1 - Creation (We CREATE identity)
__position__ = 1
__genesis__ = "0x2297685d"  # GenesisByte: parampara % 37 == 0

# === PANCHA TATTVA DECLARATION ===
__tattva__ = {
    "chaitanya": "Missing Mahajana Remedy - Adoption Service",
    "nityananda": "Sankirtan Protocol (injection logic)",
    "advaita": "analyze_source() from lila/adoption.py",
    "gadadhara": "LibCST Module header transformation",
    "srivasa": "Path + content governance determines identity",
}

from typing import List, Optional, Sequence, Tuple

import libcst as cst

from vibe_core.mahamantra.dharma.kapila.remedies.base import CSTRemedy
from vibe_core.mahamantra.protocols._seed import PARAMPARA, WORDS


class MissingMahajanaRemedy(CSTRemedy):
    """
    Adopts orphan files by injecting Mahajana DNA.

    THE LILA (Divine Play):
        1. DETECTION: Check if __mahajana__ exists
        2. INFERENCE: Analyze content to determine best Mahajana
        3. COMPUTATION: Generate valid genesis hash
        4. INJECTION: Insert DNA block at proper location

    SAFETY:
        - Only injects if NO existing __mahajana__
        - Uses deterministic inference (same content = same Mahajana)
        - Preserves all existing code structure
    """

    @property
    def rule_id(self) -> str:
        return "missing_mahajana"

    @property
    def requirements(self) -> List[str]:
        return ["vibe_core.mahamantra.lila.adoption"]

    def __init__(self, file_path: str = ""):
        super().__init__()
        self._file_path = file_path
        self._has_mahajana = False
        self._has_position = False
        self._has_genesis = False
        self._inferred_mahajana: Optional[str] = None
        self._inferred_position: Optional[int] = None
        self._source_code: str = ""
        # NOTE: Cognitive awareness is in ShuddhiEngine, not here!
        # Remedies are DUMB transformers. Engine vibrates to Akash.

    def set_file_path(self, path: str) -> None:
        """Set the file path for inference."""
        self._file_path = path

    def visit_Module(self, node: cst.Module) -> bool:
        """Capture source for analysis."""
        self._source_code = node.code
        return True

    def visit_Assign(self, node: cst.Assign) -> None:
        """Check if declaration already exists."""
        if len(node.targets) != 1:
            return

        target = node.targets[0].target
        if not isinstance(target, cst.Name):
            return

        name = target.value
        if name == "__mahajana__":
            self._has_mahajana = True
        elif name == "__position__":
            self._has_position = True
        elif name == "__genesis__":
            self._has_genesis = True

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        """
        LILA PHASES: INFERENCE → COMPUTATION → INJECTION.

        If no __mahajana__ exists, inject the full DNA block.
        Engine handles vibration to Akash - remedy stays DUMB.
        """
        # Already has declaration - no healing needed
        if self._has_mahajana:
            return updated_node

        # INFERENCE: Determine Mahajana from content
        self._infer_mahajana()

        if self._inferred_mahajana is None:
            # Could not infer - skip
            return updated_node

        self.violation_found = True
        self.applied = True

        # COMPUTATION: Generate valid genesis
        genesis = self._compute_genesis()

        # INJECTION: Build DNA block
        dna_statements = self._build_dna_block(genesis)

        # Find insertion point (after docstring and __future__ imports)
        insert_idx = self._find_insert_index(updated_node.body)

        # Create new body with DNA injected
        new_body = list(updated_node.body[:insert_idx]) + dna_statements + list(updated_node.body[insert_idx:])

        return updated_node.with_changes(body=new_body)

    def _infer_mahajana(self) -> None:
        """
        ADVAITA BRIDGE: Infer Mahajana from file content and path.

        Uses lila/adoption.py analyze_source() if available,
        falls back to inline inference.
        """
        try:
            from vibe_core.mahamantra.lila.adoption import analyze_source

            result = analyze_source(self._source_code)
            if result.get("score", 0.0) >= 0.3:
                self._inferred_mahajana = result.get("mahajana")
                self._inferred_position = result.get("position")
                return
        except ImportError:
            pass

        # Fallback: inline inference from path and content
        self._infer_inline()

    def _infer_inline(self) -> None:
        """
        Inline Mahajana inference from path patterns.

        QUARTER-BASED ROUTING:
            genesis/   → Position 0-3 (vyasa, brahma, narada, shambhu)
            dharma/    → Position 4-7 (prithu, kumaras, kapila, manu)
            karma/     → Position 8-11 (parashurama, prahlada, janaka, bhishma)
            moksha/    → Position 12-15 (nrisimha, bali, shuka, yamaraja)
        """
        path_lower = self._file_path.lower()
        content_lower = self._source_code.lower()

        # Path-based inference (most reliable)
        path_mappings = [
            # Quarter folders
            ("genesis/vyasa", "vyasa", 0),
            ("genesis/brahma", "brahma", 1),
            ("genesis/narada", "narada", 2),
            ("genesis/shambhu", "shambhu", 3),
            ("dharma/prithu", "prithu", 4),
            ("dharma/kumaras", "kumaras", 5),
            ("dharma/kapila", "kapila", 6),
            ("dharma/manu", "manu", 7),
            ("karma/parashurama", "parashurama", 8),
            ("karma/prahlada", "prahlada", 9),
            ("karma/janaka", "janaka", 10),
            ("karma/bhishma", "bhishma", 11),
            ("moksha/nrisimha", "nrisimha", 12),
            ("moksha/bali", "bali", 13),
            ("moksha/shuka", "shuka", 14),
            ("moksha/yamaraja", "yamaraja", 15),
            # General folders
            ("/test", "yamaraja", 15),
            ("/cli/", "narada", 2),
            ("/services/", "prahlada", 9),
            ("/adapters/", "vyasa", 0),
            ("/protocols/", "manu", 7),
            ("/research/", "kapila", 6),
        ]

        for pattern, mahajana, position in path_mappings:
            if pattern in path_lower:
                self._inferred_mahajana = mahajana
                self._inferred_position = position
                return

        # Content-based inference (fallback)
        content_mappings = [
            (["test_", "assert", "pytest", "unittest"], "yamaraja", 15),
            (["create", "init", "new", "allocate"], "brahma", 1),
            (["log", "emit", "send", "message", "notify"], "narada", 2),
            (["delete", "clean", "remove", "destroy", "gc"], "shambhu", 3),
            (["compile", "parse", "scan", "analyze"], "prithu", 4),
            (["execute", "run", "action", "do"], "parashurama", 8),
            (["serve", "service", "handle", "process"], "prahlada", 9),
            (["duty", "responsibility", "manage"], "janaka", 10),
            (["commit", "immutable", "final", "vow"], "bhishma", 11),
            (["protect", "guard", "security", "auth"], "nrisimha", 12),
            (["yield", "resource", "give", "donate"], "bali", 13),
            (["audit", "judge", "review", "check"], "yamaraja", 15),
        ]

        for keywords, mahajana, position in content_mappings:
            for keyword in keywords:
                if keyword in content_lower:
                    self._inferred_mahajana = mahajana
                    self._inferred_position = position
                    return

        # Ultimate fallback: prahlada (service/devotion - most generic)
        self._inferred_mahajana = "prahlada"
        self._inferred_position = 9

    def _compute_genesis(self) -> str:
        """
        Compute valid genesis byte for this file.

        YOGA MAYA: Uses only mahajana + position (NO file_path!)
        This makes Genesis HOLOGRAPHIC - same archetype → same hash ALWAYS.
        """
        import hashlib

        mahajana = self._inferred_mahajana or "prahlada"
        position = self._inferred_position or 9

        # YOGA MAYA: Pure archetype identity (NO FILE PATH!)
        identity = f"{mahajana}:{position}"
        raw_hash = hashlib.sha256(identity.encode()).hexdigest()[:8]

        # Adjust to be divisible by 37
        base_value = int(raw_hash, 16)
        adjusted = base_value - (base_value % PARAMPARA)

        return f"0x{adjusted:08x}"

    def _build_dna_block(self, genesis: str) -> List[cst.BaseStatement]:
        """Build the DNA declaration block as CST nodes."""
        mahajana = self._inferred_mahajana or "prahlada"
        position = self._inferred_position or 9

        # Create the three assignment statements
        statements: List[cst.BaseStatement] = []

        # __mahajana__ = "name"
        statements.append(
            cst.SimpleStatementLine(
                body=[
                    cst.Assign(
                        targets=[cst.AssignTarget(target=cst.Name("__mahajana__"))],
                        value=cst.SimpleString(f'"{mahajana}"'),
                    )
                ],
                leading_lines=[
                    cst.EmptyLine(whitespace=cst.SimpleWhitespace("")),
                    cst.EmptyLine(comment=cst.Comment("# === MAHAJANA DECLARATION (machine-readable) ===")),
                ],
            )
        )

        # __position__ = N
        statements.append(
            cst.SimpleStatementLine(
                body=[
                    cst.Assign(
                        targets=[cst.AssignTarget(target=cst.Name("__position__"))],
                        value=cst.Integer(str(position)),
                    )
                ]
            )
        )

        # __genesis__ = "0x..."
        statements.append(
            cst.SimpleStatementLine(
                body=[
                    cst.Assign(
                        targets=[cst.AssignTarget(target=cst.Name("__genesis__"))],
                        value=cst.SimpleString(f'"{genesis}"'),
                    )
                ],
                trailing_whitespace=cst.TrailingWhitespace(
                    whitespace=cst.SimpleWhitespace("  "),
                    comment=cst.Comment(f"# GenesisByte: parampara % {PARAMPARA} == 0"),
                ),
            )
        )

        return statements

    def _find_insert_index(self, body: Sequence[cst.BaseStatement]) -> int:
        """
        Find the correct insertion point for DNA block.

        PYTHON REQUIREMENT: `from __future__` must be FIRST (after docstring).

        ORDER:
            1. Shebang (optional)
            2. Module docstring (optional)
            3. from __future__ imports (MUST be here if present)
            4. === DNA BLOCK GOES HERE ===
            5. Other imports
            6. Code
        """
        insert_idx = 0

        for i, stmt in enumerate(body):
            # Skip docstrings (first string expression)
            if i == 0 and isinstance(stmt, cst.SimpleStatementLine):
                if len(stmt.body) == 1 and isinstance(stmt.body[0], cst.Expr):
                    if isinstance(stmt.body[0].value, (cst.SimpleString, cst.ConcatenatedString)):
                        insert_idx = i + 1
                        continue

            # Skip __future__ imports
            if isinstance(stmt, cst.SimpleStatementLine):
                for item in stmt.body:
                    if isinstance(item, cst.ImportFrom):
                        if isinstance(item.module, cst.Name) and item.module.value == "__future__":
                            insert_idx = i + 1
                            continue
                        if isinstance(item.module, cst.Attribute):
                            # from __future__.xyz (rare but possible)
                            pass

            # Also skip regular "from __future__" in ImportFrom statements
            if isinstance(stmt, cst.ImportFrom):
                if isinstance(stmt.module, cst.Name) and stmt.module.value == "__future__":
                    insert_idx = i + 1
                    continue

            # Found non-docstring, non-future content - insert before it
            break

        return insert_idx


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MissingMahajanaRemedy",
]
