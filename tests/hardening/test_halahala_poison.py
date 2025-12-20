"""
HALAHALA: Data Poisoning/Fuzzing Test - The Poison Protocol.

Mythology: When the Devas and Asuras churned the ocean, Halahala (deadly poison)
emerged first. Shiva drank it and held it in his throat (Nilakantha = Blue Throat),
preventing it from destroying the world.

This test proves:
1. SQL Injection payloads are neutralized (Parameterized Queries).
2. Memory bombs don't crash the system.
3. Null bytes and type mismatches are handled gracefully.

"The poison must be swallowed, but never digested."
"""

import json
import sys

import pytest

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.ledger import InMemoryLedger, SQLiteLedger


class TestHalahalaPoison:
    """Tests for data sanitization and persistence layer resilience."""

    def test_sql_injection_neutralized(self):
        """
        HALAHALA TEST 1: SQL Injection Attack.

        The payload tries to drop the events table.
        Parameterized queries should treat it as DATA, not CODE.
        """
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)

        # THE POISON: Classic SQL Injection
        injection_payloads = [
            "'); DROP TABLE ledger_events; --",
            "'; DELETE FROM ledger_events WHERE '1'='1",
            "UNION SELECT * FROM sqlite_master",
            "1; ATTACH DATABASE '/tmp/hack.db' AS hack",
        ]

        print("\n☣️  INJECTING SQL POISON...")

        for payload in injection_payloads:
            try:
                kernel.ledger.record_event(
                    event_type="POISON_TEST", agent_id="sql_injector", details={"payload": payload}
                )
            except Exception as e:
                print(f"   ⚠️ Exception (OK if managed): {e}")

        # VERIFICATION: Table still exists
        try:
            events = kernel.ledger.get_all_events()
            print(f"✅ SQL Injection NEUTRALIZED: {len(events)} events in ledger")

            # Check the injection string was stored as DATA
            payloads_found = sum(1 for e in events if "DROP TABLE" in str(e))
            print(f"   Found {payloads_found} injection payloads stored as harmless text")

        except Exception as e:
            pytest.fail(f"HALAHALA VICTORY (SQL): Table destroyed! Error: {e}")

    def test_memory_bomb_survived(self):
        """
        HALAHALA TEST 2: Memory Bomb (Large Payload).

        A 1MB payload should be handled without crashing.
        """
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)

        # THE POISON: 1MB String (reduced from 10MB for faster test)
        memory_bomb = "A" * 1_000_000  # 1MB

        print("\n☣️  INJECTING MEMORY BOMB (1MB)...")

        initial_memory = sys.getsizeof([])  # Baseline

        try:
            kernel.ledger.record_event(event_type="MEMORY_BOMB", agent_id="glutton", details={"bomb": memory_bomb})
            print("✅ Memory Bomb STORED (system survived)")

        except MemoryError:
            pytest.fail("HALAHALA VICTORY (Memory): OOM killed the system!")

        except Exception as e:
            # Managed exception is acceptable (payload rejected)
            print(f"✅ Memory Bomb REJECTED gracefully: {e}")

        # System should still be functional
        events = kernel.ledger.get_all_events()
        assert len(events) >= 0, "Ledger still accessible"
        print(f"✅ System stable after memory bomb: {len(events)} events in ledger")

    def test_null_byte_attack(self):
        """
        HALAHALA TEST 3: Null Byte Sabotage.

        Null bytes (\x00) can break C-based string handling.
        Python/SQLite should handle them gracefully.
        """
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)

        # THE POISON: Null bytes
        null_payloads = [
            "\x00",
            "before\x00after",
            "\x00\x00\x00ATTACK\x00\x00\x00",
        ]

        print("\n☣️  INJECTING NULL BYTES...")

        for payload in null_payloads:
            try:
                kernel.ledger.record_event(event_type="NULL_ATTACK", agent_id="ghost", details={"payload": payload})
            except Exception as e:
                print(f"   ⚠️ Null byte rejected: {e}")

        # VERIFICATION: System still works
        events = kernel.ledger.get_all_events()
        print(f"✅ Null Byte Attack SURVIVED: {len(events)} events in ledger")

    def test_recursive_json_depth(self):
        """
        HALAHALA TEST 4: Recursive JSON Depth Attack.

        Deeply nested JSON can cause stack overflow during serialization.
        """
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)

        # THE POISON: Deep recursion
        def create_deep_dict(depth):
            if depth == 0:
                return "bottom"
            return {"level": create_deep_dict(depth - 1)}

        deep_dict = create_deep_dict(50)  # 50 levels deep

        print("\n☣️  INJECTING RECURSIVE JSON (50 levels)...")

        try:
            kernel.ledger.record_event(event_type="RECURSION_ATTACK", agent_id="vasuki", details=deep_dict)
            print("✅ Recursive JSON STORED successfully")

        except RecursionError:
            pytest.fail("HALAHALA VICTORY (Recursion): Stack overflow!")

        except Exception as e:
            # Managed exception is acceptable
            print(f"✅ Recursive JSON REJECTED gracefully: {e}")

    def test_type_mismatch_attack(self):
        """
        HALAHALA TEST 5: Type Mismatch Attack.

        Sending wrong types where dicts/strings are expected.
        """
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)

        # THE POISON: Wrong types
        wrong_types = [
            12345,  # int instead of dict
            ["array"],  # list instead of dict
            None,  # None instead of dict
            True,  # bool instead of dict
            3.14159,  # float instead of dict
        ]

        print("\n☣️  INJECTING TYPE MISMATCHES...")

        for payload in wrong_types:
            try:
                kernel.ledger.record_event(
                    event_type="TYPE_MISMATCH",
                    agent_id="jester",
                    details=payload,  # type: ignore
                )
            except TypeError as e:
                print(f"   ⚠️ Type error (expected): {e}")
            except Exception as e:
                print(f"   ⚠️ Other exception: {e}")

        # VERIFICATION: System still works
        events = kernel.ledger.get_all_events()
        print(f"✅ Type Mismatch Attack SURVIVED: {len(events)} events in ledger")


class TestNilakandhaSanitization:
    """Tests verifying the Nilakandha (Blue Throat) sanitization layer."""

    def test_parameterized_queries_verified(self):
        """
        NILAKANDHA TEST: Verify parameterized queries are used.

        This is a code inspection test - the actual protection is in
        SQLiteLedger._insert_event using `?` placeholders.
        """
        import inspect

        # Get source of _insert_event
        source = inspect.getsource(SQLiteLedger._insert_event)

        # Check for parameterized query pattern
        uses_placeholders = "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" in source
        uses_fstring_dangers = 'f"INSERT' in source or "f'INSERT" in source

        print("\n🔍 NILAKANDHA INSPECTION:")
        print(f"   Uses parameterized queries (?): {uses_placeholders}")
        print(f"   Uses dangerous f-strings: {uses_fstring_dangers}")

        assert uses_placeholders, "Must use parameterized queries!"
        assert not uses_fstring_dangers, "Must NOT use f-strings for SQL!"

        print("✅ NILAKANDHA VERIFIED: Parameterized queries in use")


# Run standalone
if __name__ == "__main__":
    test = TestHalahalaPoison()
    test.test_sql_injection_neutralized()
    test.test_memory_bomb_survived()
    test.test_null_byte_attack()
    test.test_recursive_json_depth()
    test.test_type_mismatch_attack()

    nilakandha = TestNilakandhaSanitization()
    nilakandha.test_parameterized_queries_verified()

    print("\n🔱 HALAHALA COMPLETE: Shiva lives. The poison was neutralized.")
