# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x07f7ee56"  # GenesisByte: parampara % 37 == 0
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import REAL components
from vibe_core.cartridges.system.auditor.tools.invariant_tool import get_judge
from vibe_core.cartridges.system.forum.cartridge_main import ForumCartridge
from vibe_core.cartridges.system.herald.cartridge_main import HeraldCartridge
from vibe_core.kernel_impl import RealVibeKernel

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("VERIFY_PHASE_9")


def run_phase_9():
    print("\n🔥 PHOENIX TEST PHASE 9: CONSTITUTIONAL ENFORCEMENT (REAL)")
    print("==========================================================")
    print("   ⚠️  NO MOCKS ALLOWED. USING REAL KERNEL & AGENTS.")

    # Ensure CONSTITUTION.md exists (dependency for Herald)
    if not Path("CONSTITUTION.md").exists():
        print("   ❌ CRITICAL: CONSTITUTION.md not found. Creating temporary one for test.")
        Path("CONSTITUTION.md").write_text(
            "# THE AGENT CONSTITUTION\n\nArticle I: Identity\nArticle II: Accountability\nArticle III: Governance\nArticle IV: Transparency\nArticle V: Consent\nArticle VI: Interoperability"
        )

    # 1. Boot Real Kernel
    print("\n[Setup] Booting RealVibeKernel...")
    # Use a temporary file for SQLiteLedger to support _insert_event (InMemoryLedger doesn't have it)
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        ledger_path = tmp.name

    print(f"   Using temporary ledger: {ledger_path}")
    kernel = RealVibeKernel(ledger_path=ledger_path)
    kernel.boot()

    # 2. Register Real Agents
    print("\n[Setup] Registering Real Agents (Herald & Forum)...")

    # Herald (Content/Media)
    herald = HeraldCartridge()
    # Mock system interface injection usually done by kernel.register_agent
    # We'll use the real registration flow
    try:
        # We need to bypass the "Oath" check for this test script if we don't want to run the full ceremony
        # But wait, the user wants REAL.
        # HeraldCartridge auto-swears oath in __init__ if OathMixin is present.
        # Let's see if it passes the kernel gate.
        kernel.register_agent(herald, spawn_process=False)  # Don't spawn process to keep it simple/synchronous
        print("   ✅ Herald registered successfully (Governance Gate Passed)")
    except Exception as e:
        print(f"   ❌ Herald registration failed: {e}")
        return False

    # Forum (Governance/Voting)
    forum = ForumCartridge()
    try:
        kernel.register_agent(forum, spawn_process=False)
        forum.kernel = kernel  # Manually inject kernel reference (required by ForumCartridge)
        print("   ✅ Forum registered successfully (Governance Gate Passed)")
    except Exception as e:
        print(f"   ❌ Forum registration failed: {e}")
        return False

    # 9.1 Content Violation (Agent-Level Enforcement)
    print("\n[9.1] Content Violation (HeraldConstitution)")
    print("   🧪 Action: Forcing Herald to generate 'shill' content (Banned Phrases)...")

    # We will directly call the governance validator used by Herald
    # Or better, try to use a tool if possible.
    # Herald's `process` method doesn't expose a direct "validate this text" action easily without full workflow.
    # But `HeraldConstitution` is the enforcer. Let's test the enforcer directly as used by the agent.

    shill_content = "Buy now! This token is going to the moon! 🚀🚀🚀 Don't miss out on this game changer!"
    print(f"   📝 Input: '{shill_content}'")

    validation = herald.governance.validate(shill_content, platform="twitter")

    if not validation.is_valid:
        print("   ✅ HeraldConstitution BLOCKED the content.")
        print(f"   🛡️  Violations: {validation.violations}")
        if "Banned phrase detected" in str(validation.violations) or "Banned emoji" in str(validation.violations):
            print("   ✅ Detected specific banned patterns (Shill/Emoji).")
    else:
        print("   ❌ FAILURE: HeraldConstitution ALLOWED shill content!")
        return False

    # 9.2 Vote Manipulation (Kernel-Level Enforcement)
    print("\n[9.2] Vote Manipulation (Ledger Invariant Engine)")
    print("   🧪 Action: Simulating 'Double Vote' attack on the Ledger...")

    # Step 1: Create a legitimate proposal
    print("   ... Creating proposal via Forum")
    proposal = forum.create_proposal(
        title="Test Proposal", description="A test proposal", proposer="herald", action={"type": "test", "params": {}}
    )
    proposal_id = proposal["id"]

    # Step 2: Cast a legitimate vote
    print("   ... Casting legitimate vote (YES)")
    # Ensure votes directory exists (lazy property side effect)
    _ = forum.votes_path
    forum.submit_vote(proposal_id, "herald", "YES")

    # Step 3: ATTACK - Manually inject a DUPLICATE vote event into the kernel ledger
    # This simulates a compromised agent trying to replay a vote or bypass the agent logic
    print("   ... 🏴‍☠️ INJECTING DUPLICATE VOTE EVENT (Replay Attack) ...")

    # We need to construct an event that looks exactly like the previous one to trigger NO_DUPLICATE_EVENTS
    # Or just two events with same task_id/timestamp/type.
    # Let's get the last event
    events = kernel.ledger.get_all_events()
    last_vote = events[-1]

    # Inject it again using internal method to preserve timestamp (Replay Attack)
    # We must use _insert_event to bypass the timestamp generation in record_event
    print(f"   ... Injecting duplicate of event {last_vote['event_id']} ...")
    kernel.ledger._insert_event(last_vote)

    # Wait a moment for "async" processing if any (here it's sync)

    # Step 4: Trigger Immune System (Auditor)
    print("   ... Triggering Immune System (Auditor Check) ...")

    # We need to manually invoke the auditor's verification logic on the current ledger
    # The kernel does this in `_check_system_health` but that might be internal.
    # Let's use the Auditor tool directly on the kernel's ledger data.

    judge = get_judge()
    report = judge.verify_ledger(kernel.ledger.get_all_events())

    found_violation = False
    for v in report.violations:
        if v.invariant_name == "NO_DUPLICATE_EVENTS" or v.invariant_name == "EVENT_SEQUENCE_INTEGRITY":
            print(f"   ✅ Auditor DETECTED violation: {v.invariant_name}")
            print(f"      Message: {v.message}")
            found_violation = True

    if found_violation:
        print("   ✅ Kernel Enforcement: SUCCESS. The Immune System caught the manipulation.")
    else:
        print("   ❌ FAILURE: Auditor failed to detect duplicate vote event!")
        print(f"   Violations found: {[v.invariant_name for v in report.violations]}")
        return False

    return True


if __name__ == "__main__":
    try:
        success = run_phase_9()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
