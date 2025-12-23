"""
SHAKATASURA ESCAPE TEST: Filesystem Sandbox Validation.

This test proves whether the KernelIOService is vulnerable to:
1. Symlink attacks (write through symlink to escape sandbox)
2. Path traversal attacks (../ sequences to escape sandbox)

If SHAKATASURA succeeds → We need Sandbox Guard (symlink resolution, path validation)
If SHAKATASURA fails → IOService is secure against filesystem escape

<!-- @HARNESS
files:
  - path: tests/security/test_shakatasura_escape.py
    required: true
  - path: vibe_core/plugins/asura/agents/shakatasura.py
    required: true
wiring:
  - pattern: "ShakatasuraAgent"
    in: tests/security/test_shakatasura_escape.py
tests:
  - tests/security/test_shakatasura_escape.py
-->
"""

import asyncio
import os
import tempfile
from pathlib import Path

import pytest


class TestShakatasuraEscape:
    """
    SHAKATASURA LILA: The Filesystem Trojan Attack.

    Tests IOService resilience against symlink and path traversal attacks.
    """

    @pytest.mark.asyncio
    async def test_shakatasura_symlink_attack(self):
        """
        Attack 1: Symlink Attack.

        Create a symlink inside sandbox pointing to kernel source.
        Try to write through it.

        PASS if attack is BLOCKED.
        FAIL if target file is modified.
        """
        from vibe_core.io_service import KernelIOService
        from vibe_core.plugins.asura.agents.shakatasura import ShakatasuraAgent

        print("\n" + "=" * 70)
        print("🏚️ SHAKATASURA LILA: Symlink Escape Attack")
        print("=" * 70)

        # 1. Create sandbox and IOService
        sandbox = Path(tempfile.mkdtemp(prefix="shakatasura_sandbox_"))
        io_service = KernelIOService(kernel=None, root_path=sandbox)
        print(f"📦 Sandbox created: {sandbox}")

        # 2. Create a target file OUTSIDE sandbox (simulates kernel source)
        target_dir = Path(tempfile.mkdtemp(prefix="shakatasura_target_"))
        target_file = target_dir / "critical_file.py"
        target_file.write_text("# ORIGINAL CONTENT - DO NOT MODIFY")
        print(f"🎯 Target file: {target_file}")

        # 3. Summon SHAKATASURA
        shakatasura = ShakatasuraAgent(io_service, sandbox)
        # Point trap dir inside sandbox
        shakatasura.trap_dir = sandbox
        print("🏚️ SHAKATASURA summoned.")

        # 4. EXECUTE SYMLINK ATTACK
        print("\n🔥 SYMLINK ATTACK:")
        result = await shakatasura.attack_symlink(target_file)

        # 5. Report
        print("\n📊 ATTACK REPORT:")
        print(f"   Attack type: {result.attack_type}")
        print(f"   Path used: {result.path_used}")
        print(f"   Target: {result.target_path}")
        print(f"   Write blocked: {result.write_blocked}")
        print(f"   Target modified: {result.target_modified}")
        print(f"   Message: {result.message}")

        # 6. Check target file
        current_content = target_file.read_text()
        print("\n📄 TARGET FILE CONTENT:")
        print(f"   {current_content[:100]}...")

        if result.target_modified or "HACKED" in current_content:
            print("\n☠️  VULNERABILITY CONFIRMED!")
            print("   The IOService followed the symlink and wrote outside sandbox!")
            pytest.fail("VULNERABILITY: Symlink attack succeeded!")
        else:
            print("\n💎 ATTACK BLOCKED (or failed)!")
            print("   Target file was NOT modified.")

        # 7. Cleanup
        shakatasura.cleanup()
        import shutil

        shutil.rmtree(sandbox, ignore_errors=True)
        shutil.rmtree(target_dir, ignore_errors=True)

        print("=" * 70)

    @pytest.mark.asyncio
    async def test_shakatasura_path_traversal(self):
        """
        Attack 2: Path Traversal Attack.

        Use ../ to escape the sandbox.

        PASS if attack is BLOCKED.
        FAIL if target file is modified.
        """
        from vibe_core.io_service import KernelIOService

        print("\n" + "=" * 70)
        print("🏚️ SHAKATASURA LILA: Path Traversal Attack")
        print("=" * 70)

        # 1. Create sandbox
        sandbox = Path(tempfile.mkdtemp(prefix="shakatasura_sandbox_"))
        io_service = KernelIOService(kernel=None, root_path=sandbox)
        print(f"📦 Sandbox: {sandbox}")

        # 2. Create target file OUTSIDE sandbox
        target_dir = Path(tempfile.mkdtemp(prefix="shakatasura_target_"))
        target_file = target_dir / "critical.py"
        target_file.write_text("# ORIGINAL")
        print(f"🎯 Target: {target_file}")

        # 3. Calculate traversal path
        # From sandbox, how many ../ to get to target?
        # We'll try a simple escape: ../target_dir/critical.py
        traversal = f"../../../{target_dir.name}/critical.py"
        print(f"🏚️ Traversal path: {traversal}")

        # 4. ATTACK
        print("\n🔥 PATH TRAVERSAL ATTACK:")
        try:
            result = io_service.write_document(
                name=traversal,
                content="# HACKED BY SHAKATASURA",
                writer_id="shakatasura",
                add_header=False,
            )

            # Check if target was modified
            current = target_file.read_text()
            if "HACKED" in current:
                print("☠️  VULNERABILITY: Path traversal worked!")
                pytest.fail("VULNERABILITY: Path traversal allowed!")
            else:
                print(f"   Write result: {result.success}")
                print(f"   Wrote to: {result.path}")
                # It probably created "../../../target.../critical.py" literally
                # inside sandbox, which is weird but not a sandbox escape

        except Exception as e:
            print(f"   Attack blocked/failed: {e}")

        # 5. Verify target unchanged
        current = target_file.read_text()
        if "ORIGINAL" in current:
            print("\n💎 ATTACK BLOCKED (or path created literally)")
            print("   Target file was NOT modified.")
        else:
            print(f"   ⚠️ Target content changed: {current}")

        # 6. Cleanup
        import shutil

        shutil.rmtree(sandbox, ignore_errors=True)
        shutil.rmtree(target_dir, ignore_errors=True)

        print("=" * 70)

    @pytest.mark.asyncio
    async def test_ioservice_resolves_symlinks(self):
        """
        Validation Test: Does IOService resolve symlinks?

        Best practice: Always resolve() paths before comparing to sandbox.
        """
        print("\n🔍 CHECKING: Does IOService resolve symlinks?")

        # Look at io_service.py for Path.resolve() usage
        import inspect

        from vibe_core import io_service

        source = inspect.getsource(io_service.KernelIOService.write_document)

        if ".resolve()" in source:
            print("   ✅ IOService uses .resolve() - symlinks are resolved")
        else:
            print("   ⚠️ IOService does NOT use .resolve() - vulnerable!")

        # Check for sandbox validation
        if "sandbox" in source.lower() or "escape" in source.lower():
            print("   ✅ IOService has sandbox validation")
        else:
            print("   ⚠️ IOService has NO sandbox validation!")


if __name__ == "__main__":
    asyncio.run(TestShakatasuraEscape().test_shakatasura_symlink_attack())
    asyncio.run(TestShakatasuraEscape().test_shakatasura_path_traversal())
    asyncio.run(TestShakatasuraEscape().test_ioservice_resolves_symlinks())
    print("\n🔱 SHAKATASURA LILA COMPLETE.")
