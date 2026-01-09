"""
DWARAPALA PROTOCOL - The Gatekeepers (Pre-Commit Hook).

"Not even a blade of grass moves into the Repo without Sanction."

This protocol iterates over all 'Testable' components.
It runs their 'fast' tests.
If ANY fail, the Commit is rejected.
"""

from typing import List, Protocol, Tuple
from vibe_core.protocols.testable import Testable, TestableType
# Assuming YamarajaPhysics/Judgment exist in governance.yamaraja
from vibe_core.protocols.governance.yamaraja import YamarajaPhysics, Judgment, Verdict

class CommitIntent(Protocol):
    author: str
    changes: List[Testable]
    message: str

class DwarapalaGatekeeper:
    """
    The Pre-Commit Hook Implementation.
    """
    
    def inspect_commit(self, intent: CommitIntent) -> Tuple[bool, str]:
        """
        Runs before any state is persisted to the Immutable Ledger.
        """
        print(f"🛑 DWARAPALA: Halting {intent.author} at the Gate...")
        
        total_tests = 0
        passed_tests = 0
        
        for component in intent.changes:
            print(f"   🔍 Scanning {component.get_testable_id()}...") # Assuming method accessor if property not guaranteed
            
            # 1. Fetch Tests (Fractal Discovery)
            cases = component.get_test_cases()
            
            for case in cases:
                # Pre-Commit only runs 'fast' or 'basic' tags
                if "fast" in case.tags or "basic" in case.tags:
                    total_tests += 1
                    try:
                        # 2. EXECUTE TEST
                        # We pass 'None' as Kernel because Pre-Commit is often static/isolated
                        # Ideally type hint kernel as Optional[KernelProtocol] in definition
                        success = case.test_func(None, component)
                        
                        if not success:
                            return False, f"⛔ BLOCK: {component.get_testable_id()} failed test '{case.name}'"
                        
                        passed_tests += 1
                    except Exception as e:
                        return False, f"🔥 CRASH: {component.get_testable_id()} exploded during '{case.name}': {e}"

        # 3. Yamaraja Check on the Test Suite itself
        # Did we actually run enough tests?
        if total_tests == 0:
            return False, "⛔ BLOCK: Cowardice. No tests provided for changes."

        print(f"✅ DWARAPALA: {passed_tests}/{total_tests} Gates passed. Open Vaikuntha.")
        return True, "Access Granted"
