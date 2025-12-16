"""
RUNTIME EXTENSIONS - OS-level Library Loading

Allows the thin binary to load optional dependencies from:
1. ~/.steward/lib/  (user-installed extensions)
2. System site-packages (if available)

This is the OS philosophy: Binary ships thin, user extends at runtime.
No rebuild required - just `steward install-semantic`.

Usage (in boot.py, BEFORE any heavy imports):
    from vibe_core.runtime_extensions import extend_runtime
    extend_runtime()
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger("RUNTIME_EXT")

# Standard extension directory
STEWARD_HOME = Path.home() / ".steward"
STEWARD_LIB = STEWARD_HOME / "lib"
STEWARD_MODELS = STEWARD_HOME / "models"

# Packages that can be loaded from extensions
OPTIONAL_PACKAGES = [
    "numpy",
    "sentence_transformers",
    "torch",
    "scipy",
    "huggingface_hub",
]


def ensure_extension_dirs() -> None:
    """Create extension directories if they don't exist."""
    STEWARD_LIB.mkdir(parents=True, exist_ok=True)
    STEWARD_MODELS.mkdir(parents=True, exist_ok=True)

    # Create README for discoverability
    readme = STEWARD_LIB / "README.md"
    if not readme.exists():
        readme.write_text("""# Steward Runtime Extensions

This directory contains optional Python packages for Steward.

## Install Semantic Intelligence

```bash
pip install --target ~/.steward/lib numpy sentence-transformers
```

Or use the built-in command:
```bash
steward install-semantic
```

## What gets installed:
- numpy: Vector operations
- sentence-transformers: Neural embeddings (includes torch)

The thin kernel loads these at runtime if available.
""")


def extend_runtime() -> List[str]:
    """
    Extend sys.path to include user extensions.

    Call this BEFORE importing optional packages like numpy.
    Returns list of paths that were added.
    """
    added_paths = []

    # Add user extension directory
    if STEWARD_LIB.exists():
        lib_path = str(STEWARD_LIB)
        if lib_path not in sys.path:
            sys.path.insert(0, lib_path)
            added_paths.append(lib_path)
            logger.debug(f"Extended runtime: {lib_path}")

    return added_paths


def check_extension(package: str) -> bool:
    """Check if an optional package is available (either system or extension)."""
    try:
        __import__(package)
        return True
    except ImportError:
        return False


def get_extension_status() -> dict:
    """Get status of all optional extensions."""
    # First extend runtime to check extensions
    extend_runtime()

    status = {
        "steward_home": str(STEWARD_HOME),
        "steward_lib": str(STEWARD_LIB),
        "lib_exists": STEWARD_LIB.exists(),
        "packages": {},
    }

    for pkg in OPTIONAL_PACKAGES:
        try:
            mod = __import__(pkg)
            version = getattr(mod, "__version__", "unknown")
            location = getattr(mod, "__file__", "unknown")
            status["packages"][pkg] = {
                "available": True,
                "version": version,
                "location": location,
            }
        except ImportError:
            status["packages"][pkg] = {
                "available": False,
                "version": None,
                "location": None,
            }

    return status


def install_semantic_extensions(target_dir: Optional[Path] = None) -> bool:
    """
    Install semantic intelligence packages to extension directory.

    Uses pip to install numpy and sentence-transformers to ~/.steward/lib/
    Returns True on success.
    """
    import subprocess

    target = target_dir or STEWARD_LIB
    target.mkdir(parents=True, exist_ok=True)

    packages = ["numpy", "sentence-transformers"]

    logger.info(f"Installing semantic extensions to {target}...")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--target", str(target), "--upgrade", *packages],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            logger.info("Semantic extensions installed successfully")
            return True
        else:
            logger.error(f"Installation failed: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Installation error: {e}")
        return False
