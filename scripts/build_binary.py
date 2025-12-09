import shutil
import sys

import PyInstaller.__main__


def build_binary():
    """
    Build VibeOS Binary (The Singularity)
    """
    print("🌌 STARTING PHASE 11: THE SINGULARITY BUILD 🌌")

    # Clean previous builds
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("dist", ignore_errors=True)

    # Define build arguments
    args = [
        "boot.py",  # Entry point
        "--name=vibe",  # Output name
        "--onedir",  # Portable folder (no decompression delay)
        "--clean",  # Clean cache
        # Hidden Imports (Plugins & Dependencies)
        "--hidden-import=vibe_core.plugins",
        "--hidden-import=vibe_core.plugins.sys_interface",
        "--hidden-import=vibe_core.plugins.sys_interface.plugin_main",
        "--hidden-import=vibe_core.plugins.vedic_governance",
        "--hidden-import=vibe_core.plugins.vedic_governance.plugin_main",
        "--hidden-import=vibe_core.plugins.monitor",
        "--hidden-import=vibe_core.plugins.monitor.plugin_main",
        "--hidden-import=sqlite3",
        "--hidden-import=yaml",
        # Exclude Source Code (Thin Kernel Philosophy)
        "--exclude-module=vibe_core.cartridges",
        "--exclude-module=knowledge",
        # === LEAN BUILD: Exclude ML Bloat ===
        "--exclude-module=torch",
        "--exclude-module=transformers",
        "--exclude-module=scipy",
        "--exclude-module=pandas",
        "--exclude-module=sklearn",
        "--exclude-module=numpy",
        "--exclude-module=tensorflow",
        "--exclude-module=keras",
        "--exclude-module=matplotlib",
        "--exclude-module=PIL",
        "--exclude-module=cv2",
        "--exclude-module=onnxruntime",
        "--exclude-module=nltk",
        "--exclude-module=spacy",
        # Hooks path (if needed)
        # "--additional-hooks-dir=hooks",
    ]

    print(f"📦 PyInstaller Args: {args}")

    # Run PyInstaller
    try:
        PyInstaller.__main__.run(args)
        print("\n✅ BUILD SUCCESSFUL: dist/vibe")
    except Exception as e:
        print(f"\n❌ BUILD FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build_binary()
