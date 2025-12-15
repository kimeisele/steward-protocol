"""
OPUS Assistant CLI Commands.

Clean Architecture:
- Dispatched by UnifiedCLI (Layer 1) via manifest.json
- Executed here (Layer 2)
- Delegates to IntentRouter (Manas/Brain)
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

# Lazy import to avoid circular dependencies if possible,
# but IntentRouter is a relatively standalone logic component.
from vibe_core.plugins.opus_assistant.manas.intent_router import IntentRouter

logger = logging.getLogger("OPUS_CLI")


def cmd_approve(plugin: Any, intent_id: Optional[str] = None, all: bool = False, **kwargs) -> Dict[str, Any]:
    """
    Approve and execute a pending intent.

    Args:
        plugin: The OpusAssistantPlugin instance (injected by adapter)
        intent_id: ID of the intent to approve
        all: Whether to approve all pending intents
    """
    router = IntentRouter(workspace=plugin._kernel.workspace_path if plugin._kernel else Path.cwd())
    if plugin._kernel:
        router.inject_kernel(plugin._kernel)

    if all:
        pending = router.list_pending_intents()
        if not pending:
            return {"success": True, "message": "📭 No pending intents to approve"}

        print(f"⚡ Approving {len(pending)} intents...")
        successes = 0
        details = []
        for intent in pending:
            result = router.approve_intent(intent["id"])
            details.append({"id": intent["id"], "success": result.success, "error": result.error})
            if result.success:
                print(f"  ✅ {intent['id']}: {intent['title']}")
                successes += 1
            else:
                print(f"  ❌ {intent['id']}: {result.error}")

        return {
            "success": successes == len(pending),
            "approved_count": successes,
            "total_count": len(pending),
            "details": details,
        }

    if not intent_id:
        return {"success": False, "error": "Usage: steward approve <intent_id>"}

    result = router.approve_intent(intent_id)

    if result.success:
        print(f"✅ Intent approved and executed: {intent_id}")
        return {"success": True, "result": result.result, "handler": result.handler}
    else:
        print(f"❌ Failed to approve: {result.error}")
        return {"success": False, "error": result.error}


def cmd_reject(plugin: Any, intent_id: Optional[str] = None, reason: str = "", **kwargs) -> Dict[str, Any]:
    """Reject a pending intent."""
    if not intent_id:
        return {"success": False, "error": "Usage: steward reject <intent_id>"}

    router = IntentRouter(workspace=plugin._kernel.workspace_path if plugin._kernel else Path.cwd())
    if plugin._kernel:
        router.inject_kernel(plugin._kernel)

    success = router.reject_intent(intent_id, reason)

    if success:
        print(f"❌ Intent rejected: {intent_id}")
        return {"success": True, "rejected_id": intent_id}
    else:
        return {"success": False, "error": f"Intent not found: {intent_id}"}


def cmd_pending(plugin: Any, json_output: bool = False, **kwargs) -> Dict[str, Any]:
    """List pending intents."""
    router = IntentRouter(workspace=plugin._kernel.workspace_path if plugin._kernel else Path.cwd())
    pending = router.list_pending_intents()

    # If CLIExecutor handles return values by printing JSON, we just return dict.
    # But for 'human' output, we might want to print here or rely on renderer.
    # The clean CLI pattern suggests returning data and letting Layer 1 render,
    # OR rendering logic here if it's specific.
    # UnifiedCLI `_dispatch_plugin` prints `response.data`.

    if not pending and not json_output:
        print("📭 No pending intents")
        return {"count": 0, "intents": []}

    if not json_output:
        print("📬 PENDING INTENTS (awaiting approval)")
        print("=" * 60)
        for intent in pending:
            print(f"\n🆔 {intent['id']}")
            print(f"   Type:       {intent['intent_type']}")
            print(f"   Title:      {intent['title']}")
            print(f"   Confidence: {intent.get('confidence', 0.5):.2f}")

    return {"count": len(pending), "intents": pending}


def cmd_karma(plugin: Any, **kwargs) -> Dict[str, Any]:
    """Show MANAS karma."""
    router = IntentRouter(workspace=plugin._kernel.workspace_path if plugin._kernel else Path.cwd())
    summary = router.get_karma_summary()

    print("🔮 MANAS KARMA SUMMARY")
    print("=" * 40)
    print(f"   Total Karma:  {summary['total_karma']:.1f}")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")

    return summary
