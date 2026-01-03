"""
System Doctor Plugin.
Implements 'steward doctor' for GAD-000 Introspection.
"""

from typing import Any, Dict

from vibe_core.plugin_protocol import KernelPlugin


class DoctorPlugin(KernelPlugin):
    """
    The Doctor: System Introspection Agent.
    """

    @property
    def plugin_id(self) -> str:
        return "doctor"

    def cmd_doctor(self, deep: bool = False) -> Dict[str, Any]:
        """
        Diagnose system health.

        Args:
            deep: If True, run deep diagnostics (e.g. check DB integrity)

        Returns:
            Structured health report (GAD-000 compliant).
        """
        # We can use SystemInspector here
        # Since we are in OFFLINE mode, 'self._kernel' might be minimal or None depending on loader
        # But 'steward doctor' implies we check the persisted state.

        # NOTE: In offline execution mode, we might not have a full kernel.
        # But SystemInspector works on what it's given.

        from pathlib import Path

        report = {"status": "HEALTHY", "checks": [], "issues": []}

        # 1. File System Check
        required_paths = ["data/vibe_ledger.db", "config/phoenix.yaml", "vibe_core/kernel.py"]

        for path_str in required_paths:
            path = Path(path_str)
            exists = path.exists()
            report["checks"].append({"check": "file_exists", "target": path_str, "passed": exists})
            if not exists and path_str != "data/vibe_ledger.db":  # DB might not exist yet
                report["status"] = "DEGRADED"
                report["issues"].append(f"Missing critical file: {path_str}")

        # 2. Python Environment
        import sys

        report["checks"].append({"check": "python_version", "value": sys.version.split(" ")[0], "passed": True})

        # 3. Legacy Rot Scan (Deep Diagnostic)
        if deep:
            deprecated_count = 0
            scanned_count = 0
            base_path = Path("vibe_core")
            if base_path.exists():
                for py_file in base_path.rglob("*.py"):
                    scanned_count += 1
                    try:
                        content = py_file.read_text(errors="ignore")
                        if "@deprecated" in content or "DeprecationWarning" in content:
                            deprecated_count += 1
                            report["issues"].append(f"Legacy code detected in: {py_file}")
                    except Exception as e:
                        # OPUS-312: Log file read failures at debug
                        import logging

                        logging.getLogger("DOCTOR").debug(f"Could not read {py_file}: {e}")

            report["checks"].append(
                {
                    "check": "legacy_rot",
                    "scanned": scanned_count,
                    "deprecated_files": deprecated_count,
                    "passed": deprecated_count == 0,
                }
            )
            if deprecated_count > 0:
                report["status"] = "ADVISORY"

        # 3. Kernel Introspection (if we can)
        # If execution_mode is offline, we don't have a running kernel passed in usually?
        # TODO: Clarify offline mode dependency injection.

        return report
