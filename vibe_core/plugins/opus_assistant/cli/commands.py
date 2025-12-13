"""
OPUS CLI Commands - The "Remote Control" for OPUS Assistant.

Phase 3: Command-Line Interface

Commands:
    steward opus:status  → Live "State of Mind" (context)
    steward opus:log     → Journal entries from OPUS.md
    steward opus:verify  → Manual verification trigger

Architecture (GAD-000 Compliant):
    ┌─────────────────────────────────┐
    │         CLI Layer               │  ← NO LOGIC! Thin wrapper.
    │  (Format output, --json flag)   │
    └──────────────┬──────────────────┘
                   │ calls
                   ▼
    ┌─────────────────────────────────┐
    │      plugin_main.py APIs        │  ← ALL logic lives here
    │  verify(), get_current_context()│
    └─────────────────────────────────┘

The CLI is a "remote control" - it NEVER does its own thinking.
Every icon must represent a REAL system state.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# =============================================================================
# Output Formatters (Human-Readable with Visual Anchors)
# =============================================================================


def format_status_output(context: Optional[Dict[str, Any]], json_mode: bool = False) -> Dict[str, Any]:
    """
    Format context for human-readable output.

    Uses Visual Anchors (GAD-000 approved):
    - 🟢 HEALTHY / NOMINAL
    - 🟡 WARNING / DEGRADED
    - 🔴 CRITICAL / DRIFTED

    Args:
        context: OpusContext dict from get_current_context()
        json_mode: If True, return raw dict for JSON output

    Returns:
        Dict with formatted output
    """
    if context is None:
        return {
            "success": False,
            "error": "No context available. Is OPUS Assistant active?",
            "status_icon": "🔴",
        }

    if json_mode:
        return {"success": True, "data": context}

    # Extract key info
    health = context.get("health", {})
    health_status = health.get("status", "UNKNOWN")
    health_score = health.get("overall", 0.0)
    drift = context.get("drift", {})
    has_drift = drift.get("has_drift", False)
    context_hash = context.get("context_hash", "")[:12]

    # Determine status icon based on REAL state
    if health_status in ("HEALTHY", "NOMINAL") and not has_drift:
        status_icon = "🟢"
    elif health_status in ("DEGRADED", "WARNING") or has_drift:
        status_icon = "🟡"
    else:
        status_icon = "🔴"

    # Format human-readable output
    formatted = {
        "success": True,
        "status_icon": status_icon,
        "status": health_status,
        "health_score": f"{health_score:.0%}",
        "drift_detected": has_drift,
        "context_hash": context_hash,
        "summary": f"{status_icon} System Status: {health_status} ({health_score:.0%} health)",
    }

    # Add details
    if has_drift:
        drift_files = drift.get("files", [])
        formatted["drift_summary"] = f"⚠️ Drift detected in {len(drift_files)} file(s)"
        formatted["drift_files"] = drift_files[:5]  # Limit to 5

    # Add health breakdown
    formatted["health_breakdown"] = {
        "opus_exists": "🟢" if health.get("opus_exists", False) else "🔴",
        "harness_valid": "🟢" if health.get("harness_valid", False) else "🔴",
        "no_drift": "🟢" if not has_drift else "🟡",
        "kernel_active": "🟢" if health.get("kernel_active", False) else "⚪",
    }

    return formatted


def format_log_output(
    observations: List[Dict[str, Any]],
    limit: int = 20,
    json_mode: bool = False,
) -> Dict[str, Any]:
    """
    Format journal observations for output.

    Args:
        observations: List of observation dicts
        limit: Max observations to show
        json_mode: If True, return raw dict

    Returns:
        Dict with formatted output
    """
    if json_mode:
        return {"success": True, "data": observations[:limit], "total": len(observations)}

    if not observations:
        return {
            "success": True,
            "message": "_No observations recorded yet._",
            "observations": [],
        }

    # Format observations with visual severity anchors
    formatted_obs = []
    for obs in observations[:limit]:
        severity = obs.get("severity", "INFO")
        icon = {
            "INFO": "ℹ️",
            "WARN": "⚠️",
            "ALERT": "🚨",
            "INSIGHT": "💡",
        }.get(severity, "📝")

        formatted_obs.append(
            {
                "icon": icon,
                "timestamp": obs.get("timestamp", "")[:19],  # Trim to seconds
                "source": obs.get("source", "unknown"),
                "message": obs.get("message", ""),
                "severity": severity,
            }
        )

    return {
        "success": True,
        "observations": formatted_obs,
        "total": len(observations),
        "showing": min(limit, len(observations)),
    }


def format_verify_output(
    verification: Dict[str, Any],
    json_mode: bool = False,
) -> Dict[str, Any]:
    """
    Format verification results for output.

    Args:
        verification: Verification report dict from verify()
        json_mode: If True, return raw dict

    Returns:
        Dict with formatted output
    """
    if json_mode:
        return {"success": True, "data": verification}

    passed = verification.get("passed", False)
    checks = verification.get("checks", [])
    harness = verification.get("harness", {})

    # Overall status icon
    status_icon = "🟢" if passed else "🔴"

    # Count results
    passed_count = sum(1 for c in checks if c.get("passed", False))
    failed_count = len(checks) - passed_count

    formatted = {
        "success": True,
        "status_icon": status_icon,
        "passed": passed,
        "summary": f"{status_icon} Verification {'PASSED' if passed else 'FAILED'}",
        "stats": {
            "passed": passed_count,
            "failed": failed_count,
            "total": len(checks),
        },
    }

    # Add harness info
    if harness:
        formatted["harness"] = {
            "files_tracked": len(harness.get("files", [])),
            "rules": len(harness.get("rules", [])),
        }

    # Add failed checks (if any)
    if failed_count > 0:
        failed_checks = [c for c in checks if not c.get("passed", False)]
        formatted["failures"] = [
            {"check": c.get("name", "unknown"), "reason": c.get("reason", "No details")} for c in failed_checks[:10]
        ]

    return formatted


# =============================================================================
# Journal Parser (Extracts observations from OPUS.md)
# =============================================================================


def parse_journal_from_opus(opus_path: Path) -> List[Dict[str, Any]]:
    """
    Parse observations from OPUS.md journal section.

    Looks for content between @JOURNAL START and @JOURNAL END markers.

    Args:
        opus_path: Path to OPUS.md

    Returns:
        List of observation dicts
    """
    if not opus_path.exists():
        return []

    content = opus_path.read_text()

    # Find journal section
    pattern = re.compile(
        r"<!-- @JOURNAL START -->\s*(.*?)\s*<!-- @JOURNAL END -->",
        re.DOTALL,
    )

    match = pattern.search(content)
    if not match:
        return []

    journal_content = match.group(1).strip()
    if journal_content == "_No observations yet._":
        return []

    # Icon to severity mapping (Unicode-safe)
    icon_to_severity = {
        "ℹ️": "INFO",
        "⚠️": "WARN",
        "🚨": "ALERT",
        "💡": "INSIGHT",
    }

    # Parse observations line by line for better Unicode handling
    # Format: - `timestamp` ICON **[source]** message
    observations = []

    for line in journal_content.split("\n"):
        line = line.strip()
        if not line.startswith("- `"):
            continue

        # Extract timestamp
        ts_match = re.match(r"^- `(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})`\s+", line)
        if not ts_match:
            continue

        timestamp = ts_match.group(1)
        rest = line[ts_match.end() :]

        # Find severity icon at start of rest
        severity = "INFO"
        for icon, sev in icon_to_severity.items():
            if rest.startswith(icon):
                severity = sev
                rest = rest[len(icon) :].lstrip()
                break

        # Extract source: **[source]**
        source_match = re.match(r"\*\*\[([^\]]+)\]\*\*\s*", rest)
        if source_match:
            source = source_match.group(1)
            message = rest[source_match.end() :].strip()
        else:
            source = "unknown"
            message = rest.strip()

        observations.append(
            {
                "timestamp": timestamp,
                "severity": severity,
                "source": source,
                "message": message,
            }
        )

    return observations


# =============================================================================
# CLI Response Builder
# =============================================================================


def build_cli_response(
    data: Dict[str, Any],
    json_mode: bool = False,
) -> str:
    """
    Build final CLI response string.

    Args:
        data: Formatted data dict
        json_mode: If True, return JSON string

    Returns:
        Formatted string for terminal output
    """
    if json_mode:
        import json

        return json.dumps(data, indent=2, default=str)

    # Build human-readable output
    lines = []

    # Header with status
    if "summary" in data:
        lines.append(data["summary"])
        lines.append("")

    # Status details
    if "health_breakdown" in data:
        lines.append("Health Breakdown:")
        for key, icon in data["health_breakdown"].items():
            label = key.replace("_", " ").title()
            lines.append(f"  {icon} {label}")
        lines.append("")

    # Drift info
    if "drift_summary" in data:
        lines.append(data["drift_summary"])
        if data.get("drift_files"):
            for f in data["drift_files"]:
                lines.append(f"    - {f}")
        lines.append("")

    # Observations (for log command)
    if "observations" in data and data["observations"]:
        lines.append(f"Journal ({data.get('showing', 0)}/{data.get('total', 0)} entries):")
        for obs in data["observations"]:
            lines.append(f"  {obs['icon']} [{obs['timestamp']}] {obs['message']}")
        lines.append("")

    # Verification results
    if "stats" in data:
        stats = data["stats"]
        lines.append(f"Checks: {stats['passed']}/{stats['total']} passed")
        if data.get("failures"):
            lines.append("Failures:")
            for f in data["failures"]:
                lines.append(f"  🔴 {f['check']}: {f['reason']}")

    # Context hash footer
    if "context_hash" in data:
        lines.append(f"Context: {data['context_hash']}")

    return "\n".join(lines)


# =============================================================================
# EXPLORE Command - Token-Efficient Codebase Navigation
# =============================================================================


def explore_codebase(
    query: str,
    workspace: Path,
    limit: int = 10,
    json_mode: bool = False,
) -> Dict[str, Any]:
    """
    Explore the codebase for files matching a concept.

    Instead of RAG (which pulls random chunks), this does:
    1. Keyword matching in file names
    2. Docstring/comment search
    3. Import graph analysis
    4. Hot path prioritization

    Args:
        query: What to explore (e.g., "authentication", "kernel", "plugins")
        workspace: Project root
        limit: Max files to return
        json_mode: If True, return raw data

    Returns:
        Dict with relevant files and context
    """
    import subprocess

    results = []
    query_lower = query.lower()
    query_parts = query_lower.split()

    vibe_core = workspace / "vibe_core"
    if not vibe_core.exists():
        return {"success": False, "error": "vibe_core/ not found"}

    # Strategy 1: File name matching (most relevant)
    for py_file in vibe_core.glob("**/*.py"):
        if "__pycache__" in str(py_file):
            continue

        file_name = py_file.stem.lower()
        path_str = str(py_file.relative_to(workspace)).lower()

        # Score based on query match
        score = 0

        # Exact name match
        if query_lower in file_name:
            score += 100

        # Path contains query
        if query_lower in path_str:
            score += 50

        # Partial matches
        for part in query_parts:
            if part in file_name:
                score += 30
            if part in path_str:
                score += 15

        if score > 0:
            results.append(
                {
                    "path": str(py_file.relative_to(workspace)),
                    "score": score,
                    "reason": "name_match",
                }
            )

    # Strategy 2: Content search (docstrings, comments)
    try:
        grep_result = subprocess.run(
            ["grep", "-r", "-l", "-i", query, str(vibe_core)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if grep_result.returncode == 0:
            for line in grep_result.stdout.strip().split("\n"):
                if line and ".py" in line and "__pycache__" not in line:
                    try:
                        rel_path = str(Path(line).relative_to(workspace))
                        # Check if already in results
                        existing = next((r for r in results if r["path"] == rel_path), None)
                        if existing:
                            existing["score"] += 20
                            existing["reason"] = "name+content"
                        else:
                            results.append(
                                {
                                    "path": rel_path,
                                    "score": 20,
                                    "reason": "content_match",
                                }
                            )
                    except ValueError:
                        pass
    except Exception:
        pass

    # Strategy 3: Hot path bonus (files that are frequently changed are more important)
    try:
        git_result = subprocess.run(
            ["git", "log", "--pretty=format:", "--name-only", "-50"],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if git_result.returncode == 0:
            hot_files = set()
            for line in git_result.stdout.split("\n"):
                line = line.strip()
                if line and line.endswith(".py"):
                    hot_files.add(line)

            for result in results:
                if result["path"] in hot_files:
                    result["score"] += 25
                    result["hot"] = True
    except Exception:
        pass

    # Sort by score, take top N
    results.sort(key=lambda x: -x["score"])
    top_results = results[:limit]

    # Get one-liner descriptions for top results
    for result in top_results:
        try:
            file_path = workspace / result["path"]
            content = file_path.read_text()

            # Extract first docstring
            if '"""' in content:
                start = content.find('"""') + 3
                end = content.find('"""', start)
                if end > start:
                    doc = content[start:end].strip()
                    result["description"] = doc.split("\n")[0][:60]
        except Exception:
            pass

    if json_mode:
        return {
            "success": True,
            "query": query,
            "results": top_results,
            "total_matches": len(results),
        }

    return {
        "success": True,
        "query": query,
        "results": top_results,
        "total_matches": len(results),
        "summary": f"Found {len(results)} files matching '{query}', showing top {len(top_results)}",
    }


def format_explore_output(data: Dict[str, Any], json_mode: bool = False) -> str:
    """Format explore results for terminal output."""
    if json_mode:
        import json

        return json.dumps(data, indent=2, default=str)

    if not data.get("success"):
        return f"❌ {data.get('error', 'Unknown error')}"

    lines = [
        f"🔍 Exploring: '{data['query']}'",
        f"   Found {data['total_matches']} matches, showing top {len(data['results'])}",
        "",
    ]

    for i, result in enumerate(data["results"], 1):
        hot_marker = "🔥" if result.get("hot") else "  "
        score = result["score"]
        path = result["path"]
        desc = result.get("description", "")

        lines.append(f"{hot_marker} {i:2}. [{score:3}] {path}")
        if desc:
            lines.append(f"        └── {desc}")

    lines.append("")
    lines.append("💡 Use: Read the top files to understand this area of the codebase")

    return "\n".join(lines)
