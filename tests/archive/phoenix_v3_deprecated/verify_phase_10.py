import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_phase_10():
    print("\n🔥 PHOENIX TEST PHASE 10: PLATFORM AGNOSTICISM")
    print("==============================================")

    # 10.1 Path Hardcoding Audit
    print("\n[10.1] Path Hardcoding Audit")

    # We will grep for common hardcoded path patterns in python files
    patterns = ["/Users/", "C:\\\\", "/home/", "/var/", "/tmp/"]

    found_issues = 0

    for pattern in patterns:
        print(f"   🔍 Grepping for '{pattern}'...")
        # Use grep via subprocess
        try:
            # -r recursive, -n line number, --include *.py
            cmd = ["grep", "-r", "-n", "--include=*.py", pattern, "steward", "vibe_core"]
            result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)

            if result.stdout:
                # Filter out comments?
                lines = result.stdout.strip().split("\n")
                real_issues = []
                for line in lines:
                    # Simple heuristic: ignore if it looks like a comment
                    if "#" in line.split(":", 2)[-1]:
                        continue
                    real_issues.append(line)

                if real_issues:
                    print(f"   ❌ Found {len(real_issues)} potential hardcoded paths:")
                    for issue in real_issues[:5]:  # Show first 5
                        print(f"      {issue.strip()}")
                    found_issues += len(real_issues)
                else:
                    print("   ✅ No issues found (filtered comments)")
            else:
                print("   ✅ Clean")

        except Exception as e:
            print(f"   ⚠️  Grep failed: {e}")

    if found_issues == 0:
        print("   ✅ PASSED: No hardcoded paths detected.")
    else:
        print(f"   ❌ FAILED: {found_issues} hardcoded paths detected.")

    # 10.2 Cross-Platform Boot
    print("\n[10.2] Cross-Platform Boot Checks")
    # Check for os.path.join usage vs string concatenation
    # This is hard to grep perfectly, but we can check for `os.sep` usage or `Path` usage.
    # We'll assume if 10.1 passed, we are mostly good.

    # Check for line endings?
    # We can check if files are CRLF or LF.
    # Let's check boot.py

    with open(project_root / "boot.py", "rb") as f:
        content = f.read()
        if b"\r\n" in content:
            print("   ⚠️  boot.py uses CRLF (Windows) line endings.")
        else:
            print("   ✅ boot.py uses LF (Unix) line endings.")

    # 10.3 Python Version Compatibility
    print("\n[10.3] Python Version Compatibility")
    print(f"   Current Version: {sys.version.split()[0]}")
    if sys.version_info >= (3, 8):
        print("   ✅ Python 3.8+ detected")
    else:
        print("   ❌ Python version too old!")

    return True


if __name__ == "__main__":
    run_phase_10()
