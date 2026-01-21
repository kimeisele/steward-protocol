import pytest
from vibe_core.protocols.substrate import MantraOpCode as LegacyOpCode
from vibe_core.mahamantra.substrate.opcode import MantraOpCode as NewOpCode


def test_opcode_unity_parampara():
    """
    THE UNITY TEST: One Mantra, One Truth.

    Verifies that the legacy string-based OpCodes and the new int-based OpCodes
    are synchronized and represent the same 16-step sequence.
    """

    print("\n=== MAHAMANTRA UNITY AUDIT ===")

    # 1. Count Check
    assert len(LegacyOpCode) == 16, f"Legacy has {len(LegacyOpCode)} opcodes, expected 16"
    assert len(NewOpCode) == 16, f"New has {len(NewOpCode)} opcodes, expected 16"

    # 2. Position Mapping Check
    # This is where the Split-Brain manifests.
    # Legacy uses string keys ("sys_wake"), New uses int positions (0).
    # We need a deterministic map.

    mapping_failures = []

    # Expected Mapping (The 16 Positions)
    truth_table = {
        0: ("SYS_WAKE", LegacyOpCode.SYS_WAKE),
        1: ("LOAD_ROOT", LegacyOpCode.LOAD_ROOT),
        2: ("ALLOC_MEM", LegacyOpCode.ALLOC_MEM),
        3: ("INIT_THREAD", LegacyOpCode.INIT_THREAD),
        4: ("COMPILE_AST", LegacyOpCode.COMPILE_AST),
        5: ("BIND_SYMBOL", LegacyOpCode.BIND_SYMBOL),
        6: ("TYPE_CHECK", LegacyOpCode.TYPE_CHECK),
        7: ("DHARMA_TEST", LegacyOpCode.DHARMA_TEST),
        8: ("EXEC_OP", LegacyOpCode.EXEC_OP),
        9: ("EXTEND_CAP", LegacyOpCode.EXTEND_CAP),
        10: ("STATE_SYNC", LegacyOpCode.STATE_SYNC),
        11: ("LEDGER_SIGN", LegacyOpCode.LEDGER_SIGN),
        12: ("YIELD_CPU", LegacyOpCode.YIELD_CPU),
        13: ("IO_FLUSH", LegacyOpCode.IO_FLUSH),
        14: ("LOG_EMIT", LegacyOpCode.LOG_EMIT),
        15: ("AUDIT_SEAL", LegacyOpCode.AUDIT_SEAL),
    }

    for pos, (name, legacy_op) in truth_table.items():
        new_op = NewOpCode(pos)

        # Check Name Match (Semantic Unity)
        if new_op.name != name:
            mapping_failures.append(f"Position {pos}: Legacy={name} != New={new_op.name}")

        # Check Value Match (Technical Unity)
        # Note: Values might differ (str vs int), but they should represent the same logical step.

    if mapping_failures:
        pytest.fail(f"OpCode Identity Crisis detected:\n" + "\n".join(mapping_failures))

    print("✅ OpCode Names Aligned")


def test_router_integration():
    """
    Test that the Router can handle both types or effectively bridges them.
    This simulates the 'mahamantra.execute()' routing logic.
    """
    from vibe_core.protocols.mahajanas.router import MahajanaRouter, Mahajana
    from vibe_core.mahamantra.substrate.position import get_position_by_opcode

    router = MahajanaRouter()

    # Legacy Route (String Enum)
    legacy_mahajana = router.route(LegacyOpCode.EXTEND_CAP)
    # With legacy=False default (or updated table), this should be PRAHLADA.
    # If legacy=True is still active or table is old, it might be JANAKA.
    # Let's align with the NEW truth: EXTEND_CAP -> PRAHLADA
    assert legacy_mahajana == Mahajana.PRAHLADA

    # New Route (Int Enum) - Does the router support it?
    # Or do we need a bridge?
    new_op = NewOpCode(9)  # EXTEND_CAP

    try:
        # The router expects MantraOpCode (Legacy) which is str-based.
        # Passing Int-based NewOpCode might fail or route incorrectly.
        # Ideally, we want unity.
        router.route(new_op)
    except (ValueError, KeyError, TypeError) as e:
        print(f"⚠️ Router rejected NewOpCode: {e}")
        # This confirms the incompatibility
        pytest.fail(f"Router cannot handle NewOpCode: {e}")


if __name__ == "__main__":
    test_opcode_unity_parampara()
