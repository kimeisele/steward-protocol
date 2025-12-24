"""
💓 PRANA - The Life Force

Config-driven kernel lifecycle management.
Reads from config/prana.yaml (NOT VISNU-protected) to control behavior.

ARCHITECTURE:
    - config/prana.yaml = editable without VISNU bypass
    - .github/workflows/*.yml = PROTECTED, immutable
    - Scripts call prana.load_config() to get current settings

Usage:
    from vibe_core.prana import load_config, ensure_kernel_running

    config = load_config()
    if config.heartbeat.boot_kernel_first:
        ensure_kernel_running()
"""

import logging
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger("PRANA")

# Default config path
CONFIG_PATH = Path("config/prana.yaml")


@dataclass
class SessionStartConfig:
    auto_boot_kernel: bool = True
    background_boot: bool = True
    boot_timeout: int = 10


@dataclass
class HeartbeatConfig:
    enabled: bool = True
    min_interval_minutes: int = 10
    boot_kernel_first: bool = True
    execute_tasks: bool = True
    max_tasks_per_pulse: int = 3


@dataclass
class KernelConfig:
    ready_timeout: int = 30
    log_level: str = "INFO"
    auto_restart: bool = True


@dataclass
class OpusConfig:
    refresh_interval: int = 60
    force_refresh_on_heartbeat: bool = False


@dataclass
class LimitsConfig:
    max_agents: int = 5
    budget_per_pulse: float = 1.00
    failure_threshold: int = 3


@dataclass
class PranaConfig:
    """Full PRANA configuration."""

    session_start: SessionStartConfig = field(default_factory=SessionStartConfig)
    heartbeat: HeartbeatConfig = field(default_factory=HeartbeatConfig)
    kernel: KernelConfig = field(default_factory=KernelConfig)
    opus: OpusConfig = field(default_factory=OpusConfig)
    limits: LimitsConfig = field(default_factory=LimitsConfig)


def load_config(config_path: Optional[Path] = None) -> PranaConfig:
    """
    Load PRANA configuration from YAML file.

    Falls back to defaults if file doesn't exist or can't be parsed.
    """
    path = config_path or CONFIG_PATH

    if not path.exists():
        logger.warning(f"PRANA config not found at {path}, using defaults")
        return PranaConfig()

    try:
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        return _parse_config(data)

    except ImportError:
        # No PyYAML - try simple parsing
        logger.debug("PyYAML not available, using simple parser")
        return _parse_simple(path)

    except Exception as e:
        logger.error(f"Failed to load PRANA config: {e}")
        return PranaConfig()


def _parse_config(data: Dict[str, object]) -> PranaConfig:
    """Parse YAML data into PranaConfig."""

    def get_section(name: str, cls):
        section_data = data.get(name, {})
        if not section_data:
            return cls()
        return cls(**{k: v for k, v in section_data.items() if hasattr(cls, k) or k in cls.__dataclass_fields__})

    return PranaConfig(
        session_start=get_section("session_start", SessionStartConfig),
        heartbeat=get_section("heartbeat", HeartbeatConfig),
        kernel=get_section("kernel", KernelConfig),
        opus=get_section("opus", OpusConfig),
        limits=get_section("limits", LimitsConfig),
    )


def _parse_simple(path: Path) -> PranaConfig:
    """Simple YAML parser without PyYAML dependency."""
    config = PranaConfig()
    content = path.read_text()

    # Very basic parsing for boolean values
    if "auto_boot_kernel: true" in content:
        config.session_start.auto_boot_kernel = True
    elif "auto_boot_kernel: false" in content:
        config.session_start.auto_boot_kernel = False

    if "boot_kernel_first: true" in content:
        config.heartbeat.boot_kernel_first = True
    elif "boot_kernel_first: false" in content:
        config.heartbeat.boot_kernel_first = False

    if "enabled: false" in content:
        config.heartbeat.enabled = False

    return config


def is_kernel_running() -> bool:
    """Check if the kernel is currently running."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "boot_kernel.py"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def ensure_kernel_running(config: Optional[PranaConfig] = None, background: bool = True) -> bool:
    """
    Ensure the kernel is running. Start it if not.

    Returns True if kernel is running after this call.
    """
    if is_kernel_running():
        logger.debug("Kernel already running")
        return True

    cfg = config or load_config()
    timeout = cfg.kernel.ready_timeout

    logger.info("💓 PRANA: Starting kernel...")

    try:
        if background:
            subprocess.Popen(
                ["python", "-m", "vibe_core.cli", "boot", "--background"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            subprocess.run(
                ["python", "-m", "vibe_core.cli", "boot", "--background"],
                check=True,
                capture_output=True,
            )

        # Wait for kernel to be ready
        start = time.time()
        while time.time() - start < timeout:
            if is_kernel_running():
                logger.info("✅ Kernel started successfully")
                return True
            time.sleep(0.5)

        logger.warning("⚠️ Kernel start timed out")
        return False

    except Exception as e:
        logger.error(f"❌ Failed to start kernel: {e}")
        return False


def get_last_heartbeat() -> Optional[str]:
    """Get timestamp of last heartbeat from state file."""
    state_file = Path(".opus_state/prana_heartbeat.json")
    if not state_file.exists():
        return None

    try:
        import json

        with open(state_file) as f:
            data = json.load(f)
        return data.get("last_pulse")
    except Exception:
        return None


def record_heartbeat() -> None:
    """Record current heartbeat timestamp (Atomic)."""
    import json
    import os
    import tempfile
    from datetime import datetime

    state_file = Path(".opus_state/prana_heartbeat.json")
    state_file.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "last_pulse": datetime.utcnow().isoformat(),
        "kernel_running": is_kernel_running(),
    }

    content = json.dumps(data, indent=2)

    # Atomic write pattern to prevent corruption
    fd, tmp_path = tempfile.mkstemp(
        dir=state_file.parent,
        prefix=f".{state_file.stem}_",
        suffix=state_file.suffix,
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        # Atomic rename
        os.replace(tmp_path, state_file)
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        logger.error(f"Failed to record heartbeat: {e}")
        raise
