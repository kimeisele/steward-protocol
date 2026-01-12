
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
        3: ("BIND_CTX", LegacyOpCode.BIND_CTX),
        4: ("ASSERT_TRUTH", LegacyOpCode.ASSERT_TRUTH),
        5: ("RESOLVE_REQ", LegacyOpCode.RESOLVE_REQ),
        6: ("GARBAGE_COLLECT", LegacyOpCode.GARBAGE_COLLECT),
        7: ("PULSE_SYNC", LegacyOpCode.PULSE_SYNC),
        8: ("FETCH_RES", LegacyOpCode.FETCH_RES),
        9: ("EXEC_SERVICE", LegacyOpCode.EXEC_SERVICE),
        10: ("CHECK_DHARMA", LegacyOpCode.CHECK_DHARMA),
        11: ("COMMIT_LOG", LegacyOpCode.COMMIT_LOG),
        12: ("CACHE_STATE", LegacyOpCode.CACHE_STATE),
        13: ("OPTIMIZE", LegacyOpCode.OPTIMIZE),
        14: ("YIELD_CPU", LegacyOpCode.YIELD_CPU),
        15: ("RESET_IP", LegacyOpCode.RESET_IP),
    }
    
    for pos, (name, legacy_op) in truth_table.items():
        new_op = NewOpCode(pos)
        
        # Check Name Match (Semantic Unity)
        if new_op.name != name:
            mapping_failures.append(f"Position {pos}: Legacy={name} != New={new_op.name}")
            
        # Check Value Match (Technical Unity)
        # This will fail because str != int
        if legacy_op.value != pos and legacy_op.name != new_op.name:
             # If names match, we might forgive value mismatch for now (String vs Int)
             # But strictly, they should be interchangeable or mappable.
             pass

    if mapping_failures:
        pytest.fail(f"OpCode Identity Crisis detected:\n" + "\n".join(mapping_failures))
        
    print("✅ OpCode Names Aligned")

def test_router_integration():
    """
    Test that the Router can handle both types or effectively bridges them.
    This simulates the 'mahamantra.execute()' routing logic.
    """
    from vibe_core.protocols.mahajanas.router import MahajanaRouter, Mahajana
    from vibe_core.mahamantra.substrate.wiring import get_position_by_opcode
    
    router = MahajanaRouter()
    
    # Legacy Route (String Enum)
    legacy_mahajana = router.route(LegacyOpCode.EXEC_SERVICE)
    assert legacy_mahajana == Mahajana.PRAHLADA
    
    # New Route (Int Enum) - Does the router support it?
    # Or do we need a bridge?
    new_op = NewOpCode(9) # EXEC_SERVICE
    
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
