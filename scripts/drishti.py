#!/usr/bin/env python3
"""
🔭 DRISHTI - The Dead Man's Switch (OPUS-063)

Sanskrit: Drishti = Gaze, Vision, Focus

PURPOSE:
    The dashboard OPUS.md must NEVER lie.
    If the kernel dies, OPUS.md must scream "DEAD".
    Since a dead kernel can't mark itself as dead, we need an EXTERNAL observer.

LOGIC:
    1. Read .boot_pid (kernel PID file)
    2. Check: Does process exist?
    3. Check: Is OPUS.md older than threshold?
    4. ACTION: If process gone OR file stale -> Write WARNING to OPUS.md

USAGE:
    python scripts/drishti.py           # Check and warn if needed
    python scripts/drishti.py --force   # Force write warning (for testing)
    python scripts/drishti.py --status  # Just report status, don't modify

INTEGRATION:
    - Called by heartbeat.yml workflow
    - Called by session-start hook
    - Can be run manually anytime
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x8bfee8a5"  # GenesisByte: parampara % 37 == 0

import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Thresholds
STALE_THRESHOLD_SECONDS = 120  # 2 minutes - if OPUS.md older than this, kernel is likely dead
PID_FILE = Path("/tmp/vibe_os/kernel/boot.pid")
OPUS_FILE = Path("OPUS.md")


def get_kernel_pid() -> int | None:
    """Read kernel PID from file."""
    if not PID_FILE.exists():
        return None
    try:
        return int(PID_FILE.read_text().strip())
    except (ValueError, IOError):
        return None


def is_process_running(pid: int) -> bool:
    """Check if a process with given PID is running."""
    try:
        os.kill(pid, 0)  # Signal 0 = check existence
        return True
    except OSError:
        return False


def get_opus_last_modified() -> datetime | None:
    """Get last modification time of OPUS.md."""
    if not OPUS_FILE.exists():
        return None
    try:
        mtime = OPUS_FILE.stat().st_mtime
        return datetime.fromtimestamp(mtime)
    except OSError:
        return None


def extract_opus_timestamp() -> datetime | None:
    """Extract timestamp from OPUS.md content."""
    if not OPUS_FILE.exists():
        return None
    try:
        content = OPUS_FILE.read_text()
        # Look for: Last Updated: 2025-12-14 17:44 UTC
        match = re.search(r"Last Updated: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}(?::\d{2})?) UTC", content)
        if match:
            ts_str = match.group(1)
            if len(ts_str) == 16:  # No seconds
                ts_str += ":00"
            return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        return None
    except Exception:
        return None


def diagnose() -> dict:
    """
    Diagnose kernel health.

    Returns dict with:
        - kernel_alive: bool
        - opus_stale: bool
        - opus_age_seconds: int or None
        - pid: int or None
        - status: "HEALTHY" | "KERNEL_DEAD" | "STALE_DASHBOARD" | "UNKNOWN"
    """
    result = {
        "kernel_alive": False,
        "opus_stale": False,
        "opus_age_seconds": None,
        "pid": None,
        "status": "UNKNOWN",
    }

    # Check PID
    pid = get_kernel_pid()
    result["pid"] = pid

    if pid:
        result["kernel_alive"] = is_process_running(pid)

    # Check OPUS.md staleness
    opus_ts = extract_opus_timestamp()
    if opus_ts:
        age = datetime.utcnow() - opus_ts
        result["opus_age_seconds"] = int(age.total_seconds())
        result["opus_stale"] = age > timedelta(seconds=STALE_THRESHOLD_SECONDS)

    # Determine status
    if result["kernel_alive"] and not result["opus_stale"]:
        result["status"] = "HEALTHY"
    elif not result["kernel_alive"]:
        result["status"] = "KERNEL_DEAD"
    elif result["opus_stale"]:
        result["status"] = "STALE_DASHBOARD"

    return result


def inject_warning(reason: str) -> None:
    """
    Inject a warning banner into OPUS.md.

    This writes DIRECTLY to the file, bypassing the kernel.
    Emergency mode only.
    """
    if not OPUS_FILE.exists():
        print(f"❌ OPUS.md not found at {OPUS_FILE}")
        return

    content = OPUS_FILE.read_text()

    # Check if warning already present
    if "🔴 SYSTEM FAILURE" in content or "⚠️ KERNEL OFFLINE" in content:
        print("⚠️ Warning already present in OPUS.md")
        return

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    warning_banner = f"""
<!--
⚠️ DRISHTI WATCHDOG ALERT ⚠️
Injected: {timestamp}
Reason: {reason}
-->

> # 🔴 SYSTEM FAILURE
>
> **Kernel Status:** ❌ OFFLINE / CRASHED
>
> **Detected by:** DRISHTI Watchdog
>
> **Reason:** {reason}
>
> **Action Required:** Run `python -m vibe_core.cli boot`
>
> **Timestamp:** {timestamp}

---

"""

    # Inject after the HTML comment header
    if content.startswith("<!--"):
        # Find end of first comment
        end_comment = content.find("-->")
        if end_comment != -1:
            insert_pos = end_comment + 3
            new_content = content[:insert_pos] + "\n" + warning_banner + content[insert_pos:]
        else:
            new_content = warning_banner + content
    else:
        new_content = warning_banner + content

    OPUS_FILE.write_text(new_content)
    print("🔴 DRISHTI: Warning injected into OPUS.md")
    print(f"   Reason: {reason}")


def clear_warning() -> None:
    """Remove DRISHTI warning from OPUS.md if kernel is healthy."""
    if not OPUS_FILE.exists():
        return

    content = OPUS_FILE.read_text()

    # Remove DRISHTI warning block
    pattern = r"<!--\s*⚠️ DRISHTI WATCHDOG ALERT.*?---\s*"
    new_content = re.sub(pattern, "", content, flags=re.DOTALL)

    # Also remove the visible warning
    pattern2 = r"> # 🔴 SYSTEM FAILURE.*?---\s*"
    new_content = re.sub(pattern2, "", new_content, flags=re.DOTALL)

    if new_content != content:
        OPUS_FILE.write_text(new_content)
        print("✅ DRISHTI: Warning cleared from OPUS.md")


def main():
    parser = argparse.ArgumentParser(description="DRISHTI - Kernel Liveness Watchdog")
    parser.add_argument("--force", action="store_true", help="Force inject warning (for testing)")
    parser.add_argument("--status", action="store_true", help="Just report status, don't modify")
    parser.add_argument("--clear", action="store_true", help="Clear warning if kernel is healthy")
    args = parser.parse_args()

    print("🔭 DRISHTI - The Dead Man's Switch")
    print("=" * 40)

    diag = diagnose()

    print(f"PID:           {diag['pid'] or 'N/A'}")
    print(f"Kernel Alive:  {'✅ YES' if diag['kernel_alive'] else '❌ NO'}")
    print(f"OPUS.md Age:   {diag['opus_age_seconds']}s" if diag["opus_age_seconds"] else "OPUS.md Age:   N/A")
    print(f"OPUS Stale:    {'⚠️ YES' if diag['opus_stale'] else '✅ NO'}")
    print(f"Status:        {diag['status']}")
    print()

    if args.status:
        # Just report, don't modify
        sys.exit(0 if diag["status"] == "HEALTHY" else 1)

    if args.force:
        inject_warning("FORCED TEST by operator")
        sys.exit(0)

    if args.clear:
        if diag["status"] == "HEALTHY":
            clear_warning()
        else:
            print("⚠️ Cannot clear warning - system not healthy")
        sys.exit(0)

    # Auto-action based on status
    if diag["status"] == "KERNEL_DEAD":
        inject_warning(f"Kernel process (PID {diag['pid']}) not running")
    elif diag["status"] == "STALE_DASHBOARD":
        inject_warning(f"OPUS.md not updated for {diag['opus_age_seconds']}s (threshold: {STALE_THRESHOLD_SECONDS}s)")
    elif diag["status"] == "HEALTHY":
        # Check if we need to clear old warnings
        clear_warning()
        print("✅ System healthy - no action needed")
    else:
        print("⚠️ Unknown status - manual inspection recommended")


if __name__ == "__main__":
    main()
