import logging
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("RealGraftTest")


def create_dummy_lib(base_path: Path):
    """Create a dummy sentence-transformers library in a real filesystem path."""
    lib_dir = base_path / ".steward" / "lib"
    lib_dir.mkdir(parents=True, exist_ok=True)

    # Create valid python package
    pkg_dir = lib_dir / "sentence_transformers"
    pkg_dir.mkdir(exist_ok=True)

    (pkg_dir / "__init__.py").write_text(
        textwrap.dedent("""
    class SentenceTransformer:
        def __init__(self, model_name_or_path, **kwargs):
            print(f"✅ Real Loaded model: {model_name_or_path}")

        def encode(self, sentences, **kwargs):
            # Return dummy numpy-like list
            import numpy as np
            return np.array([[0.1, 0.2]])
    """)
    )

    # Also need numpy for SemanticEngine
    numpy_dir = lib_dir / "numpy"
    numpy_dir.mkdir(exist_ok=True)
    (numpy_dir / "__init__.py").write_text("""
class ndarray:
    pass
def array(x): return [0.1]
def dot(a, b): return 0.5
def linalg(): pass
class linalg:
    @staticmethod
    def norm(x): return 1.0
""")

    logger.info(f"📁 Created dummy libs at {lib_dir}")
    return lib_dir


def run_subprocess_test(home_dir: Path):
    """Run a child process with modified HOME to simulate container."""
    env = os.environ.copy()
    env["HOME"] = str(home_dir)
    pass_pythonpath = os.getcwd()
    if "PYTHONPATH" in env:
        pass_pythonpath = f"{pass_pythonpath}:{env['PYTHONPATH']}"
    env["PYTHONPATH"] = pass_pythonpath

    # Script to run inside the "container"
    # It must:
    # 1. Boot CognitiveKernel
    # 2. Assert it found the dummy lib
    script = textwrap.dedent("""
    import sys
    import logging
    from pathlib import Path

    # Configure logging to see internal messages
    logging.basicConfig(level=logging.INFO)

    print(f"🏠 CONTAINER HOME: {Path.home()}")

    try:
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import CognitiveKernel, ManasConfig

        # Workspace for kernel
        k_workspace = Path(Path.home()) / "workspace"
        k_workspace.mkdir(parents=True, exist_ok=True)

        print("🚀 Booting Kernel...")
        kernel = CognitiveKernel(workspace=k_workspace, config=ManasConfig())

        print(f"🧠 Intelligence State: {kernel.has_intelligence}")

        if kernel.has_intelligence:
            print("✅ SUCCESS: Kernel grafted intelligence from custom HOME")
            sys.exit(0)
        else:
            print("❌ FAILURE: Kernel failed to graft intelligence")
            sys.exit(1)

    except Exception as e:
        print(f"❌ CRASH: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    """)

    logger.info("🚀 Launching subprocess...")
    result = subprocess.run([sys.executable, "-c", script], env=env, capture_output=True, text=True)

    print("\n--- Subprocess Output ---")
    print(result.stdout)
    print("-------------------------")
    print(result.stderr)
    print("-------------------------\n")

    if result.returncode == 0:
        logger.info("✅ TEST PASSED: Real subprocess grafted successfully.")
    else:
        logger.error("❌ TEST FAILED: Subprocess error.")
        sys.exit(1)


def main():
    # 1. Setup real temp dir
    test_root = Path("/tmp/opus_real_test")
    if test_root.exists():
        shutil.rmtree(test_root)
    test_root.mkdir()

    try:
        # 2. Plant the 'Garden' (Libraries)
        create_dummy_lib(test_root)

        # 3. Enter the 'Container' (Subprocess)
        run_subprocess_test(test_root)

    finally:
        # Cleanup
        if test_root.exists():
            shutil.rmtree(test_root)
            logger.info("🧹 Cleaned up /tmp/opus_real_test")


if __name__ == "__main__":
    main()
