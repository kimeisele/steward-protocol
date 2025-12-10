import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))


class MockKernel:
    project_root = PROJECT_ROOT


from vibe_core.plugins.interface.renderers.opus.panels.verification import VerificationPanel


def run():
    print("DEBUG: Initializing VerificationPanel")
    kernel = MockKernel()

    # Manually inject BasePanel dependency since we aren't using the full plugin loader
    # VerificationPanel inherits BasePanel, which needs kernel.
    # But wait, BasePanel is in .panels.__init__? No, it's imported from .base
    # Let's just try instantiation.

    # Monkeypatch to debug
    original_verify_tests = VerificationPanel._verify_tests

    def debug_verify_tests(self, tests):
        print(f"DEBUG: Verifying tests: {tests}")
        for t in tests:
            print(f"DEBUG: Checking test pattern: {t!r} (type: {type(t)})")
            try:
                list(self._root.glob(t))
            except Exception as e:
                print(f"DEBUG: CRASH on pattern {t!r}: {e}")
                # Don't re-raise, let original run to crash if it must, or just continue
        return original_verify_tests(self, tests)

    VerificationPanel._verify_tests = debug_verify_tests

    panel = VerificationPanel(kernel)
    print("DEBUG: Calling render()")
    try:
        content = panel.render()
        print("DEBUG: Render result length:", len(content) if content else "None")
        print("--- CONTENT START ---")
        print(content)
        print("--- CONTENT END ---")
    except Exception as e:
        print(f"DEBUG: Render failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run()
