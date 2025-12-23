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


async def cmd_approve(plugin: Any, intent_id: Optional[str] = None, all: bool = False, **kwargs) -> Dict[str, Any]:
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
            result = await router.approve_intent(intent["id"])
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

    result = await router.approve_intent(intent_id)

    if result.success:
        print(f"✅ Intent approved and executed: {intent_id}")
        return {"success": True, "result": result.result, "handler": result.executed_by}
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


# =============================================================================
# CLI OUTPUT FORMATTERS (Used by plugin_main.py)
# =============================================================================


def format_status_output(context: Optional[Dict[str, Any]], json_mode: bool = False) -> Dict[str, Any]:
    """
    Format status output for CLI display.

    Args:
        context: Current context dict from OpusContextService
        json_mode: If True, return raw data without printing

    Returns:
        Status dict with formatted output
    """
    import json as json_lib

    if context is None:
        if not json_mode:
            print("🧠 MANAS STATUS: Context not available")
        return {"status": "unavailable", "message": "No context synthesized"}

    # Extract key metrics
    health = context.get("health", {})
    awareness = context.get("awareness", {})
    system = context.get("system", {})

    result = {
        "status": health.get("status", "unknown"),
        "consciousness_level": awareness.get("consciousness_level", 0),
        "state": awareness.get("state", "unknown"),
        "tick": awareness.get("tick", 0),
        "pending_intents": awareness.get("pending_intents", 0),
        "karma_score": system.get("karma_score", 0),
        "context_hash": context.get("context_hash", "")[:16],
    }

    if json_mode:
        print(json_lib.dumps(result, indent=2))
        return result

    # Human-readable output
    print("\n🧠 MANAS STATE OF MIND")
    print("=" * 50)
    print(f"   Status:       {result['status']}")
    print(f"   Consciousness: {result['consciousness_level']:.1%}")
    print(f"   State:        {result['state']}")
    print(f"   Tick:         {result['tick']}")
    print(f"   Pending:      {result['pending_intents']} intents")
    print(f"   Karma:        {result['karma_score']}")
    print("=" * 50)

    return result


def format_log_output(observations: list, limit: int = 20, json_mode: bool = False) -> Dict[str, Any]:
    """
    Format observation log output for CLI display.

    Args:
        observations: List of observation dicts
        limit: Max entries to display
        json_mode: If True, return raw data without printing

    Returns:
        Log dict with entries
    """
    import json as json_lib

    limited = observations[:limit] if limit else observations

    result = {"count": len(observations), "showing": len(limited), "entries": limited}

    if json_mode:
        print(json_lib.dumps(result, indent=2))
        return result

    if not limited:
        print("📓 No observations logged yet")
        return result

    print(f"\n📓 OPUS OBSERVATION LOG (showing {len(limited)}/{len(observations)})")
    print("=" * 60)
    for obs in limited:
        timestamp = obs.get("timestamp", "unknown")
        severity = obs.get("severity", "INFO")
        message = obs.get("message", "")
        print(f"[{timestamp}] {severity}: {message}")

    return result


def parse_journal_from_opus(opus_path: Path) -> list:
    """
    Parse OPUS.md journal section to extract observations.

    Args:
        opus_path: Path to OPUS.md file

    Returns:
        List of observation dicts
    """
    import re

    if not opus_path.exists():
        return []

    try:
        content = opus_path.read_text()

        # Look for journal section
        journal_match = re.search(r"## 📓 Journal\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
        if not journal_match:
            return []

        journal_content = journal_match.group(1)
        observations = []

        # Parse entries like: - [2024-01-01 12:00] INFO: Message
        entry_pattern = re.compile(r"-\s*\[([^\]]+)\]\s*(\w+):\s*(.+?)(?=\n-|\Z)", re.DOTALL)
        for match in entry_pattern.finditer(journal_content):
            observations.append(
                {
                    "timestamp": match.group(1).strip(),
                    "severity": match.group(2).strip(),
                    "message": match.group(3).strip(),
                }
            )

        return observations

    except Exception as e:
        logger.warning(f"Failed to parse journal: {e}")
        return []


def format_verify_output(verification: Dict[str, Any], json_mode: bool = False) -> Dict[str, Any]:
    """
    Format verification output for CLI display.

    Args:
        verification: Verification report dict
        json_mode: If True, return raw data without printing

    Returns:
        Formatted verification dict
    """
    import json as json_lib

    if json_mode:
        print(json_lib.dumps(verification, indent=2))
        return verification

    status = verification.get("status", "unknown")
    issues = verification.get("issues", [])
    checks = verification.get("checks", {})

    print("\n🔍 OPUS VERIFICATION REPORT")
    print("=" * 50)
    print(f"   Status: {status}")
    print(f"   Issues: {len(issues)}")

    if checks:
        print("\n   Checks:")
        for check_name, check_result in checks.items():
            icon = "✅" if check_result.get("passed") else "❌"
            print(f"     {icon} {check_name}")

    if issues:
        print("\n   Issues Found:")
        for issue in issues[:5]:  # Limit to 5
            print(f"     ⚠️  {issue.get('message', issue)}")
        if len(issues) > 5:
            print(f"     ... and {len(issues) - 5} more")

    return verification


def explore_codebase(query: str, workspace: Path, limit: int = 10, json_mode: bool = False) -> Dict[str, Any]:
    """
    Token-efficient codebase exploration.

    Uses deterministic search (no LLM) to find relevant files.

    Args:
        query: Search query
        workspace: Workspace root
        limit: Max files to return
        json_mode: If True, return raw data

    Returns:
        Exploration results dict
    """
    import subprocess

    results = {"query": query, "files": [], "total_matches": 0}

    # 1. Name-based search
    try:
        proc = subprocess.run(
            ["find", str(workspace), "-name", f"*{query}*", "-type", "f"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        name_matches = [p for p in proc.stdout.strip().split("\n") if p and ".git" not in p][:limit]
        results["files"].extend(name_matches)
    except Exception:
        pass

    # 2. Content-based search (grep)
    try:
        proc = subprocess.run(
            ["grep", "-rl", query, str(workspace), "--include=*.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        content_matches = [p for p in proc.stdout.strip().split("\n") if p and ".git" not in p]
        for match in content_matches:
            if match not in results["files"] and len(results["files"]) < limit:
                results["files"].append(match)
    except Exception:
        pass

    results["total_matches"] = len(results["files"])

    if not json_mode and results["files"]:
        print(f"\n🔍 EXPLORE: '{query}' ({len(results['files'])} files)")
        print("=" * 50)
        for f in results["files"]:
            rel = Path(f).relative_to(workspace) if f.startswith(str(workspace)) else f
            print(f"   📄 {rel}")

    return results


def deep_explore(query: str, workspace: Path, limit: int = 5) -> Dict[str, Any]:
    """
    Deep exploration mode - reads file contents for synthesis.

    Args:
        query: Search query
        workspace: Workspace root
        limit: Max files to read

    Returns:
        Deep exploration results with file contents
    """
    # First get files via normal explore
    basic = explore_codebase(query, workspace, limit=limit, json_mode=True)

    results = {
        "query": query,
        "files": [],
        "synthesis_prompt": "",
    }

    # Read file contents
    for file_path in basic.get("files", [])[:limit]:
        try:
            path = Path(file_path)
            if path.exists() and path.stat().st_size < 50000:  # Max 50KB
                content = path.read_text()
                results["files"].append(
                    {
                        "path": str(path.relative_to(workspace)),
                        "size": len(content),
                        "content": content[:5000],  # First 5KB
                    }
                )
        except Exception:
            pass

    # Generate synthesis prompt
    if results["files"]:
        file_list = "\n".join([f"- {f['path']}" for f in results["files"]])
        results["synthesis_prompt"] = f"""Analyze these files related to '{query}':

{file_list}

Provide a concise summary of:
1. What this code does
2. Key patterns and dependencies
3. Potential issues or improvements
"""

    return results


def build_cli_response(success: bool, data: Any = None, error: Optional[str] = None) -> Dict[str, Any]:
    """
    Build a standard CLI response dict.

    Args:
        success: Whether the operation succeeded
        data: Response data
        error: Error message if failed

    Returns:
        Standard CLI response dict
    """
    response = {"success": success}
    if data is not None:
        response["data"] = data
    if error:
        response["error"] = error
    return response
