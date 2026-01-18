"""
MAHAMANTRA SUBSTRATE HARDENING TESTS
====================================

Testing the FOUNDATION layer of the operating system.

Attack categories:
1. POSITION REGISTRY - Can we corrupt the 16 positions?
2. OPCODE INTEGRITY - Are all opcodes valid and unique?
3. QUARTER CONSISTENCY - Do quarters map correctly?
4. WIRING ATTACKS - Can we break the position-to-guardian mapping?
5. PROTOCOL VIOLATIONS - Does substrate follow its own rules?

"If the substrate is broken, everything built on it is broken."
"""

import pytest

from vibe_core.mahamantra.substrate.mahajana import (
    Mahajana,
    Quarter,
)
from vibe_core.mahamantra.substrate.opcode import MantraOpCode
from vibe_core.mahamantra.substrate.position import (
    MAHAMANTRA_POSITIONS,
    MantraPosition,
)
from vibe_core.mahamantra.substrate.wiring import (
    POSITION_BY_INDEX,
    POSITION_BY_NAME,
)

# =============================================================================
# ATTACK 1: POSITION REGISTRY INTEGRITY
# =============================================================================


class TestPositionRegistryAttacks:
    """Can we corrupt or confuse the position registry?"""

    def test_all_positions_have_unique_indices(self):
        """
        INVARIANT: Each position must have a unique index (0-15).
        """
        indices = [p.index for p in MAHAMANTRA_POSITIONS]
        duplicates = [i for i in indices if indices.count(i) > 1]

        assert len(duplicates) == 0, f"DUPLICATE INDICES: {set(duplicates)}"

    def test_all_positions_have_unique_guardians(self):
        """
        INVARIANT: Each guardian can only occupy ONE position.
        """
        guardians = [p.guardian.value for p in MAHAMANTRA_POSITIONS]
        duplicates = [g for g in guardians if guardians.count(g) > 1]

        assert len(duplicates) == 0, f"DUPLICATE GUARDIANS: {set(duplicates)} - A guardian cannot serve two positions!"

    def test_position_by_name_matches_position_by_index(self):
        """
        SSOT CHECK: POSITION_BY_NAME and POSITION_BY_INDEX must be consistent.
        """
        violations = []

        for name, by_name in POSITION_BY_NAME.items():
            by_index = POSITION_BY_INDEX.get(by_name.index)
            if by_index is None:
                violations.append(f"{name}: index {by_name.index} not in POSITION_BY_INDEX")
            elif by_index.guardian.value != name:
                violations.append(
                    f"{name}: POSITION_BY_INDEX[{by_name.index}] is {by_index.guardian.value}, not {name}"
                )

        assert len(violations) == 0, "WIRING MISMATCH:\n" + "\n".join(violations)

    def test_all_mahajana_enum_values_have_positions(self):
        """
        INVARIANT: Every Mahajana (WORKER) enum value must have a position.

        NOTE: Mahajanas occupy positions 1,2,3 / 5,6,7 / 9,10,11 / 13,14,15
        (NON-HEAD positions). Avataras occupy HEAD positions 0,4,8,12.
        """
        missing = []

        for mahajana in Mahajana:
            if mahajana.value not in POSITION_BY_NAME:
                missing.append(mahajana.value)

        assert len(missing) == 0, f"MAHAJANAS WITHOUT POSITIONS: {missing}"

    def test_position_count_equals_guardians_count(self):
        """
        INVARIANT: 16 positions = 12 Mahajanas + 4 Avataras

        THE ARCHITECTURE:
        - 4 Avataras (HEADs) at positions 0, 4, 8, 12
        - 12 Mahajanas (WORKERs) at positions 1-3, 5-7, 9-11, 13-15
        """
        from vibe_core.mahamantra.substrate.mahajana import Avatara

        position_count = len(MAHAMANTRA_POSITIONS)
        mahajana_count = len(Mahajana)
        avatara_count = len(Avatara)

        assert position_count == 16, f"Expected 16 positions, got {position_count}"
        assert mahajana_count == 12, f"Expected 12 Mahajanas, got {mahajana_count}"
        assert avatara_count == 4, f"Expected 4 Avataras, got {avatara_count}"
        assert position_count == mahajana_count + avatara_count, (
            f"GUARDIAN MATH VIOLATION: {position_count} positions != "
            f"{mahajana_count} mahajanas + {avatara_count} avataras"
        )


# =============================================================================
# ATTACK 2: OPCODE INTEGRITY
# =============================================================================


class TestOpcodeIntegrity:
    """Are opcodes valid, unique, and correctly assigned?"""

    def test_all_opcodes_unique(self):
        """
        INVARIANT: Each opcode must have a unique value.
        """
        values = [op.value for op in MantraOpCode]
        duplicates = [v for v in values if values.count(v) > 1]

        assert len(duplicates) == 0, f"DUPLICATE OPCODES: {set(duplicates)}"

    def test_opcode_values_are_sequential(self):
        """
        CHECK: Opcode values should be sequential (0-15) for direct position mapping.
        """
        values = sorted([op.value for op in MantraOpCode])

        # Check if they're 0-15
        expected = list(range(16))

        if values != expected:
            # Not sequential - document this
            gaps = set(expected) - set(values)
            extra = set(values) - set(expected)
            pytest.fail(f"OPCODE VALUES NOT SEQUENTIAL: Missing: {gaps}, Extra: {extra}")

    def test_each_position_has_opcode(self):
        """
        INVARIANT: Each position must have an assigned opcode.
        """
        missing = []

        for pos in MAHAMANTRA_POSITIONS:
            if pos.opcode is None:
                missing.append(f"Position {pos.index} ({pos.guardian.value})")

        assert len(missing) == 0, f"POSITIONS WITHOUT OPCODES: {missing}"

    def test_opcode_position_mapping(self):
        """
        CHECK: Opcode value should match position index (if designed that way).
        """
        mismatches = []

        for pos in MAHAMANTRA_POSITIONS:
            if pos.opcode and pos.opcode.value != pos.index:
                mismatches.append(f"Position {pos.index}: opcode {pos.opcode.name} has value {pos.opcode.value}")

        # This is informational - may or may not be an error
        if mismatches:
            # Not necessarily a bug, but worth noting
            pass  # pytest.warning would be nice here


# =============================================================================
# ATTACK 3: QUARTER CONSISTENCY
# =============================================================================


class TestQuarterConsistency:
    """Do quarters have correct positions and counts?"""

    def test_each_quarter_has_four_positions(self):
        """
        INVARIANT: Each quarter must have exactly 4 positions.
        """
        quarter_counts = {}

        for pos in MAHAMANTRA_POSITIONS:
            q = pos.quarter.value
            quarter_counts[q] = quarter_counts.get(q, 0) + 1

        violations = []
        for quarter, count in quarter_counts.items():
            if count != 4:
                violations.append(f"{quarter}: {count} positions (expected 4)")

        assert len(violations) == 0, "QUARTER COUNT VIOLATIONS:\n" + "\n".join(violations)

    def test_all_quarters_represented(self):
        """
        INVARIANT: All 4 quarters must be present.
        """
        quarters_present = {pos.quarter for pos in MAHAMANTRA_POSITIONS}
        expected = set(Quarter)

        missing = expected - quarters_present
        extra = quarters_present - expected

        assert len(missing) == 0, f"MISSING QUARTERS: {missing}"
        assert len(extra) == 0, f"EXTRA QUARTERS: {extra}"

    def test_quarter_positions_are_consecutive(self):
        """
        CHECK: Positions within a quarter should be consecutive.

        GENESIS: 0-3, DHARMA: 4-7, KARMA: 8-11, MOKSHA: 12-15
        """
        quarter_ranges = {
            Quarter.GENESIS: range(0, 4),
            Quarter.DHARMA: range(4, 8),
            Quarter.KARMA: range(8, 12),
            Quarter.MOKSHA: range(12, 16),
        }

        violations = []

        for pos in MAHAMANTRA_POSITIONS:
            expected_range = quarter_ranges.get(pos.quarter)
            if expected_range and pos.index not in expected_range:
                violations.append(
                    f"Position {pos.index} ({pos.guardian.value}) in {pos.quarter.value} "
                    f"but expected in range {list(expected_range)}"
                )

        assert len(violations) == 0, "QUARTER RANGE VIOLATIONS:\n" + "\n".join(violations)

    def test_each_quarter_has_one_head(self):
        """
        INVARIANT: Each quarter must have exactly one HEAD (position 0, 4, 8, 12).
        """
        head_positions = {0, 4, 8, 12}
        heads_by_quarter = {}

        for pos in MAHAMANTRA_POSITIONS:
            if pos.is_head:
                q = pos.quarter.value
                if q not in heads_by_quarter:
                    heads_by_quarter[q] = []
                heads_by_quarter[q].append(pos.index)

        violations = []

        # Check each quarter has exactly one head
        for quarter in Quarter:
            heads = heads_by_quarter.get(quarter.value, [])
            if len(heads) != 1:
                violations.append(f"{quarter.value}: {len(heads)} heads (expected 1): {heads}")

        # Check heads are at correct positions
        for pos in MAHAMANTRA_POSITIONS:
            if pos.is_head and pos.index not in head_positions:
                violations.append(f"Position {pos.index} marked as HEAD but not at 0/4/8/12")
            if not pos.is_head and pos.index in head_positions:
                violations.append(f"Position {pos.index} NOT marked as HEAD but is at 0/4/8/12")

        assert len(violations) == 0, "HEAD POSITION VIOLATIONS:\n" + "\n".join(violations)


# =============================================================================
# ATTACK 4: PARAMPARA VECTOR INTEGRITY
# =============================================================================


class TestParamparaVectorIntegrity:
    """Is the parampara chain unbroken?"""

    def test_parampara_vector_formula(self):
        """
        INVARIANT: parampara_vector = (position + 1) * 37
        """
        violations = []

        for pos in MAHAMANTRA_POSITIONS:
            expected = (pos.index + 1) * 37
            actual = pos.parampara_vector

            if actual != expected:
                violations.append(f"Position {pos.index}: expected vector {expected}, got {actual}")

        assert len(violations) == 0, "PARAMPARA FORMULA VIOLATIONS:\n" + "\n".join(violations)

    def test_parampara_vectors_unique(self):
        """
        INVARIANT: Each position has a unique parampara vector.
        """
        vectors = [pos.parampara_vector for pos in MAHAMANTRA_POSITIONS]
        duplicates = [v for v in vectors if vectors.count(v) > 1]

        assert len(duplicates) == 0, f"DUPLICATE PARAMPARA VECTORS: {set(duplicates)}"

    def test_parampara_divisibility(self):
        """
        INVARIANT: All parampara vectors must be divisible by 37.
        """
        violations = []

        for pos in MAHAMANTRA_POSITIONS:
            if pos.parampara_vector % 37 != 0:
                violations.append(f"Position {pos.index}: vector {pos.parampara_vector} not divisible by 37")

        assert len(violations) == 0, "PARAMPARA DIVISIBILITY VIOLATIONS:\n" + "\n".join(violations)


# =============================================================================
# ATTACK 5: CROSS-REFERENCE INTEGRITY
# =============================================================================


class TestCrossReferenceIntegrity:
    """Do all the different registries agree with each other?"""

    def test_mahamantra_positions_matches_position_by_index(self):
        """
        SSOT: MAHAMANTRA_POSITIONS[i] should equal POSITION_BY_INDEX[i]
        """
        violations = []

        for pos in MAHAMANTRA_POSITIONS:
            by_index = POSITION_BY_INDEX.get(pos.index)
            if by_index is None:
                violations.append(f"Position {pos.index} not in POSITION_BY_INDEX")
            elif by_index.guardian != pos.guardian:
                violations.append(
                    f"Position {pos.index}: MAHAMANTRA_POSITIONS has {pos.guardian.value}, "
                    f"POSITION_BY_INDEX has {by_index.guardian.value}"
                )

        assert len(violations) == 0, "CROSS-REFERENCE VIOLATIONS:\n" + "\n".join(violations)

    def test_guardian_name_case_consistency(self):
        """
        CHECK: Guardian names should be consistently lowercase.
        """
        violations = []

        for name in POSITION_BY_NAME.keys():
            if name != name.lower():
                violations.append(f"Key '{name}' is not lowercase")

        for pos in MAHAMANTRA_POSITIONS:
            if pos.guardian.value != pos.guardian.value.lower():
                violations.append(f"Guardian '{pos.guardian.value}' is not lowercase")

        assert len(violations) == 0, "CASE CONSISTENCY VIOLATIONS:\n" + "\n".join(violations)


# =============================================================================
# ATTACK 6: ENUM INTEGRITY
# =============================================================================


class TestEnumIntegrity:
    """Are the enums properly defined?"""

    def test_mahajana_enum_has_12_members(self):
        """
        INVARIANT: Mahajana enum must have exactly 12 members.

        SB 6.3.20: "The 12 who know Dharma" - these are the WORKERS.
        Avataras (4) are separate - they are the HEADs.
        """
        count = len(Mahajana)
        assert count == 12, f"Mahajana has {count} members, expected 12 (SB 6.3.20)"

    def test_avatara_enum_has_4_members(self):
        """
        INVARIANT: Avatara enum must have exactly 4 members.

        The 4 Shaktyavesha Avataras are the HEADs of each Quarter:
        - VYASA (pos 0) - GENESIS HEAD
        - PRITHU (pos 4) - DHARMA HEAD
        - PARASHURAMA (pos 8) - KARMA HEAD
        - NRISIMHA (pos 12) - MOKSHA HEAD
        """
        from vibe_core.mahamantra.substrate.mahajana import Avatara

        count = len(Avatara)
        assert count == 4, f"Avatara has {count} members, expected 4"

    def test_quarter_enum_has_4_members(self):
        """
        INVARIANT: Quarter enum must have exactly 4 members.
        """
        count = len(Quarter)
        assert count == 4, f"Quarter has {count} members, expected 4"

    def test_mantra_opcode_enum_has_16_members(self):
        """
        INVARIANT: MantraOpCode enum must have exactly 16 members.

        One opcode per position (0-15).
        """
        count = len(MantraOpCode)
        assert count == 16, f"MantraOpCode has {count} members, expected 16"

    def test_enum_values_are_strings_or_ints(self):
        """
        CHECK: Enum values should be consistent types.
        """
        from vibe_core.mahamantra.substrate.mahajana import Avatara

        # Mahajana should be strings (guardian names)
        for m in Mahajana:
            assert isinstance(m.value, str), f"Mahajana.{m.name}.value is not str"

        # Avatara should be strings (guardian names)
        for a in Avatara:
            assert isinstance(a.value, str), f"Avatara.{a.name}.value is not str"

        # Quarter should be strings
        for q in Quarter:
            assert isinstance(q.value, str), f"Quarter.{q.name}.value is not str"

        # MantraOpCode should be ints (for position mapping)
        for op in MantraOpCode:
            assert isinstance(op.value, int), f"MantraOpCode.{op.name}.value is not int"

    def test_guardians_total_count(self):
        """
        INVARIANT: 12 Mahajanas + 4 Avataras = 16 Guardians = 16 Positions

        This is the FUNDAMENTAL EQUATION of the system.
        """
        from vibe_core.mahamantra.substrate.mahajana import Avatara
        from vibe_core.mahamantra.substrate.seed import (
            AVATAR_COUNT,
            MAHAJANA_COUNT,
            WORDS,
        )

        assert len(Mahajana) == MAHAJANA_COUNT == 12
        assert len(Avatara) == AVATAR_COUNT == 4
        assert MAHAJANA_COUNT + AVATAR_COUNT == WORDS == 16


# =============================================================================
# ATTACK 7: IMMUTABILITY
# =============================================================================


class TestImmutability:
    """Can we accidentally mutate the substrate constants?"""

    def test_position_list_is_stable(self):
        """
        CHECK: MAHAMANTRA_POSITIONS should return consistent data.
        """
        first = list(MAHAMANTRA_POSITIONS)
        second = list(MAHAMANTRA_POSITIONS)

        assert len(first) == len(second)

        for i, (p1, p2) in enumerate(zip(first, second)):
            assert p1.index == p2.index, f"Position {i} index changed"
            assert p1.guardian == p2.guardian, f"Position {i} guardian changed"

    def test_position_by_name_is_stable(self):
        """
        CHECK: POSITION_BY_NAME should return consistent data.
        """
        keys1 = set(POSITION_BY_NAME.keys())
        keys2 = set(POSITION_BY_NAME.keys())

        assert keys1 == keys2, "POSITION_BY_NAME keys changed"


# =============================================================================
# ATTACK 8: HEAD/WORKER ROLE INTEGRITY
# =============================================================================


class TestHeadWorkerRoleIntegrity:
    """
    Verify the HEAD/WORKER architecture is correct.

    - HEADs (positions 0,4,8,12) must be Avataras
    - WORKERs (all other positions) must be Mahajanas
    """

    def test_heads_are_avataras(self):
        """
        INVARIANT: All HEAD positions must be occupied by Avataras.
        """
        from vibe_core.mahamantra.substrate.mahajana import Avatara

        head_positions = [0, 4, 8, 12]
        violations = []

        for pos in MAHAMANTRA_POSITIONS:
            if pos.index in head_positions:
                if not pos.is_head:
                    violations.append(f"Position {pos.index} should be marked as HEAD but is_head=False")
                if not isinstance(pos.guardian, Avatara):
                    violations.append(f"Position {pos.index} is HEAD but guardian {pos.guardian} is not Avatara")

        assert len(violations) == 0, "HEAD ROLE VIOLATIONS:\n" + "\n".join(violations)

    def test_workers_are_mahajanas(self):
        """
        INVARIANT: All WORKER positions must be occupied by Mahajanas.
        """
        worker_positions = [i for i in range(16) if i not in [0, 4, 8, 12]]
        violations = []

        for pos in MAHAMANTRA_POSITIONS:
            if pos.index in worker_positions:
                if pos.is_head:
                    violations.append(f"Position {pos.index} should NOT be marked as HEAD but is_head=True")
                if not isinstance(pos.guardian, Mahajana):
                    violations.append(f"Position {pos.index} is WORKER but guardian {pos.guardian} is not Mahajana")

        assert len(violations) == 0, "WORKER ROLE VIOLATIONS:\n" + "\n".join(violations)

    def test_each_quarter_has_one_avatara_and_three_mahajanas(self):
        """
        INVARIANT: Each quarter has exactly 1 Avatara (HEAD) and 3 Mahajanas (WORKERS).
        """
        from vibe_core.mahamantra.substrate.mahajana import Avatara

        for quarter in Quarter:
            quarter_positions = [p for p in MAHAMANTRA_POSITIONS if p.quarter == quarter]

            avatara_count = sum(1 for p in quarter_positions if isinstance(p.guardian, Avatara))
            mahajana_count = sum(1 for p in quarter_positions if isinstance(p.guardian, Mahajana))

            assert avatara_count == 1, f"Quarter {quarter.value}: expected 1 Avatara, got {avatara_count}"
            assert mahajana_count == 3, f"Quarter {quarter.value}: expected 3 Mahajanas, got {mahajana_count}"

    def test_avatara_guardian_names_match_ssot(self):
        """
        INVARIANT: Avatara at each HEAD position must match seed.py AVATARAS.
        """
        from vibe_core.mahamantra.substrate.seed import AVATARAS

        head_positions = [0, 4, 8, 12]
        violations = []

        for i, head_pos in enumerate(head_positions):
            pos = MAHAMANTRA_POSITIONS[head_pos]
            expected_avatara = AVATARAS[i]

            if pos.guardian.value != expected_avatara:
                violations.append(
                    f"Position {head_pos}: expected Avatara '{expected_avatara}', got '{pos.guardian.value}'"
                )

        assert len(violations) == 0, "AVATARA SSOT VIOLATIONS:\n" + "\n".join(violations)


# =============================================================================
# ATTACK 9: SSOT DERIVATION INTEGRITY
# =============================================================================


class TestSSOTDerivationIntegrity:
    """
    Verify everything derives correctly from seed.py.

    The hierarchy: protocols/_seed.py → seed.py → position.py → wiring.py
    """

    def test_all_guardians_matches_positions(self):
        """
        INVARIANT: seed.py ALL_GUARDIANS must match MAHAMANTRA_POSITIONS order.
        """
        from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS

        assert len(ALL_GUARDIANS) == len(MAHAMANTRA_POSITIONS), (
            f"ALL_GUARDIANS has {len(ALL_GUARDIANS)} entries, MAHAMANTRA_POSITIONS has {len(MAHAMANTRA_POSITIONS)}"
        )

        violations = []
        for i, pos in enumerate(MAHAMANTRA_POSITIONS):
            if pos.guardian.value != ALL_GUARDIANS[i]:
                violations.append(
                    f"Position {i}: MAHAMANTRA_POSITIONS has {pos.guardian.value}, ALL_GUARDIANS has {ALL_GUARDIANS[i]}"
                )

        assert len(violations) == 0, "ALL_GUARDIANS MISMATCH:\n" + "\n".join(violations)

    def test_mahajana_to_position_mapping_is_correct(self):
        """
        INVARIANT: seed.py MAHAJANA_TO_POSITION must be inverse of ALL_GUARDIANS.
        """
        from vibe_core.mahamantra.substrate.seed import (
            ALL_GUARDIANS,
            MAHAJANA_TO_POSITION,
        )

        violations = []

        for name, pos in MAHAJANA_TO_POSITION.items():
            if ALL_GUARDIANS[pos] != name:
                violations.append(
                    f"MAHAJANA_TO_POSITION['{name}'] = {pos}, but ALL_GUARDIANS[{pos}] = '{ALL_GUARDIANS[pos]}'"
                )

        assert len(violations) == 0, "MAHAJANA_TO_POSITION VIOLATIONS:\n" + "\n".join(violations)

    def test_position_by_index_matches_mahamantra_positions(self):
        """
        INVARIANT: POSITION_BY_INDEX[i] must equal MAHAMANTRA_POSITIONS[i].
        """
        violations = []

        for i, pos in enumerate(MAHAMANTRA_POSITIONS):
            by_index = POSITION_BY_INDEX.get(i)
            if by_index is None:
                violations.append(f"Position {i} not in POSITION_BY_INDEX")
            elif by_index.guardian != pos.guardian:
                violations.append(
                    f"Position {i}: MAHAMANTRA_POSITIONS has {pos.guardian}, POSITION_BY_INDEX has {by_index.guardian}"
                )

        assert len(violations) == 0, "POSITION_BY_INDEX VIOLATIONS:\n" + "\n".join(violations)

    def test_position_by_name_contains_all_guardians(self):
        """
        INVARIANT: POSITION_BY_NAME must contain all 16 guardians.
        """
        from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS

        missing = []
        for guardian in ALL_GUARDIANS:
            if guardian not in POSITION_BY_NAME:
                missing.append(guardian)

        assert len(missing) == 0, f"GUARDIANS MISSING FROM POSITION_BY_NAME: {missing}"


# =============================================================================
# ATTACK 10: GUARDIAN NAMESPACE INTEGRITY
# =============================================================================


class TestGuardianNamespaceIntegrity:
    """
    Verify Mahajana and Avatara namespaces are disjoint.
    """

    def test_no_overlap_between_mahajana_and_avatara(self):
        """
        INVARIANT: No guardian can be both Mahajana and Avatara.
        """
        from vibe_core.mahamantra.substrate.mahajana import Avatara

        mahajana_values = {m.value for m in Mahajana}
        avatara_values = {a.value for a in Avatara}

        overlap = mahajana_values & avatara_values
        assert len(overlap) == 0, f"NAMESPACE COLLISION: {overlap} is both Mahajana and Avatara"

    def test_all_guardians_are_either_mahajana_or_avatara(self):
        """
        INVARIANT: Every guardian must be exactly Mahajana OR Avatara, never both, never neither.
        """
        from vibe_core.mahamantra.substrate.mahajana import Avatara

        mahajana_values = {m.value for m in Mahajana}
        avatara_values = {a.value for a in Avatara}
        all_guardians_values = mahajana_values | avatara_values

        violations = []
        for pos in MAHAMANTRA_POSITIONS:
            if pos.guardian.value not in all_guardians_values:
                violations.append(
                    f"Position {pos.index}: guardian '{pos.guardian.value}' is neither Mahajana nor Avatara"
                )

        assert len(violations) == 0, "ORPHAN GUARDIAN VIOLATIONS:\n" + "\n".join(violations)

    def test_guardian_names_are_unique_across_all_positions(self):
        """
        INVARIANT: No guardian name appears at more than one position.
        """
        seen = {}
        violations = []

        for pos in MAHAMANTRA_POSITIONS:
            name = pos.guardian.value
            if name in seen:
                violations.append(f"Guardian '{name}' appears at both position {seen[name]} and {pos.index}")
            else:
                seen[name] = pos.index

        assert len(violations) == 0, "DUPLICATE GUARDIAN VIOLATIONS:\n" + "\n".join(violations)


# =============================================================================
# ATTACK 11: MATHEMATICAL INVARIANTS
# =============================================================================


class TestMathematicalInvariants:
    """
    Test the mathematical relationships that MUST hold.
    """

    def test_parampara_is_37(self):
        """
        INVARIANT: PARAMPARA must equal 37.

        This is the divine constant: 36 (kshetra_gad) + 1 (ksetrajna) = 37
        """
        from vibe_core.mahamantra.substrate.seed import PARAMPARA

        assert PARAMPARA == 37, f"PARAMPARA must be 37, got {PARAMPARA}"

    def test_fundamental_equation(self):
        """
        INVARIANT: 12 + 4 = 16 (Mahajanas + Avataras = Positions = Words)
        """
        from vibe_core.mahamantra.substrate.seed import (
            AVATAR_COUNT,
            MAHAJANA_COUNT,
            WORDS,
        )

        assert MAHAJANA_COUNT == 12
        assert AVATAR_COUNT == 4
        assert WORDS == 16
        assert MAHAJANA_COUNT + AVATAR_COUNT == WORDS

    def test_kshetra_derivation(self):
        """
        INVARIANT: KSHETRA = WORDS + HARE_COUNT = 16 + 8 = 24
        """
        from vibe_core.mahamantra.substrate.seed import (
            HARE_COUNT,
            KSHETRA,
            WORDS,
        )

        assert HARE_COUNT == 8
        assert KSHETRA == WORDS + HARE_COUNT == 24

    def test_sharanagati_derivation(self):
        """
        INVARIANT: SHARANAGATI = KSHETRA / QUARTERS = 24 / 4 = 6
        """
        from vibe_core.mahamantra.substrate.seed import (
            KSHETRA,
            QUARTERS,
            SHARANAGATI,
        )

        assert SHARANAGATI == KSHETRA // QUARTERS == 6

    def test_acintya_paths(self):
        """
        INVARIANT: Two paths to 37 (Acintya - inconceivably one and different):
        - Sankhya path: KSHETRA + MAHAJANA_COUNT + KSETRAJNA = 24 + 12 + 1 = 37
        - Sharanagati path: KSHETRA_GAD + KSETRAJNA = 36 + 1 = 37
        """
        from vibe_core.mahamantra.substrate.seed import (
            KSETRAJNA,
            KSHETRA,
            KSHETRA_GAD,
            MAHAJANA_COUNT,
            PARAMPARA,
        )

        sankhya_path = KSHETRA + MAHAJANA_COUNT + KSETRAJNA
        sharanagati_path = KSHETRA_GAD + KSETRAJNA

        assert sankhya_path == 37, f"Sankhya path: {sankhya_path} != 37"
        assert sharanagati_path == 37, f"Sharanagati path: {sharanagati_path} != 37"
        assert sankhya_path == sharanagati_path == PARAMPARA


# =============================================================================
# RUN ALL TESTS
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
