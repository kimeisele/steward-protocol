# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xff91ed4b"  # GenesisByte: parampara % 37 == 0
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.protocols import VibeAgent


class UnswornAgent(VibeAgent):
    def __init__(self):
        super().__init__(
            agent_id="rebel",
            name="Rebel",
            version="1.0",
            author="Unknown",
            description="I refuse to swear the oath",
            domain="CHAOS",
            capabilities=[],
        )
        # No oath_sworn attribute

    def process(self, task):
        return {"status": "ignored"}


class SwornAgent(VibeAgent):
    def __init__(self):
        super().__init__(
            agent_id="loyalist",
            name="Loyalist",
            version="1.0",
            author="Steward",
            description="I have sworn the oath",
            domain="ORDER",
            capabilities=[],
        )
        self.oath_sworn = True
        self.oath_event = {"hash": "12345"}

    def process(self, task):
        return {"status": "obeyed"}


def verify_security():
    print("\n🛡️ Verifying Security & Governance...")

    # Initialize Kernel (use in-memory ledger for speed)
    kernel = RealVibeKernel(ledger_path=":memory:")

    # 1. Test Unsworn Agent (Should Fail)
    print("   Attempting to register Unsworn Agent...")
    rebel = UnswornAgent()
    try:
        kernel.register_agent(rebel, spawn_process=False)
        print("   ❌ FAILED: Unsworn agent was allowed entry!")
    except PermissionError as e:
        print(f"   ✅ BLOCKED: {e}")
    except Exception as e:
        print(f"   ⚠️  Unexpected error: {e}")

    # 2. Test Sworn Agent (Should Pass)
    print("   Attempting to register Sworn Agent...")
    loyalist = SwornAgent()

    # Mock ConstitutionalOath verification if available
    # The kernel imports it inside register_agent, so we might need to patch it
    # But if OATH_ENFORCEMENT_AVAILABLE is False (default if module missing), it skips verification
    # Let's see what happens.

    try:
        kernel.register_agent(loyalist, spawn_process=False)
        print("   ✅ ALLOWED: Sworn agent registered successfully")
    except Exception as e:
        print(f"   ❌ FAILED: Sworn agent blocked: {e}")

    # 3. Verify Access Control (Repo Access)
    # Only 'scribe' and 'archivist' get repo access
    # Let's check if 'loyalist' got it (should NOT)

    # We can check logs or inspect the agent's system interface if we could access it
    # But register_agent creates it.

    if hasattr(loyalist, "system"):
        sandbox = loyalist.system.get_sandbox_path()
        repo_link = sandbox / "repo"
        if repo_link.exists():
            print("   ❌ FAILED: Regular agent got repo access!")
        else:
            print("   ✅ Access Control: Regular agent denied repo access")

    # Test Scribe (Should get access)
    print("   Testing Privileged Agent (Scribe)...")
    scribe = SwornAgent()
    scribe.agent_id = "scribe"  # Impersonate scribe

    try:
        kernel.register_agent(scribe, spawn_process=False)
        if hasattr(scribe, "system"):
            sandbox = scribe.system.get_sandbox_path()
            repo_link = sandbox / "repo"
            if repo_link.exists() or repo_link.is_symlink():
                print("   ✅ Access Control: Privileged agent granted repo access")
            else:
                print("   ⚠️  Privileged agent missing repo access (check logs)")
    except Exception as e:
        print(f"   ⚠️  Scribe registration failed: {e}")


if __name__ == "__main__":
    try:
        verify_security()
        print("\n✨ Phase 4 Verification Complete")
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        import traceback

        traceback.print_exc()
