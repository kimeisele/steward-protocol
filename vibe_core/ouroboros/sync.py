"""
CI/CD Sync Service - Bridge between remote CI and local Knowledge Graph.

This service fetches CI/CD results from GitHub Actions and ingests them
into the local Knowledge Graph, enabling the Ouroboros loop to learn
from remote failures.
"""

import json
import logging
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ingestion import ViolationIngester, ViolationRecord, ViolationSource

logger = logging.getLogger("OUROBOROS")


class CISyncService:
    """
    Syncs CI/CD violations from GitHub Actions to local Knowledge Graph.

    Usage:
        sync = CISyncService()
        sync.sync_latest()  # Fetch and ingest latest CI results
    """

    def __init__(
        self,
        repo: Optional[str] = None,
        ingester: Optional[ViolationIngester] = None,
    ):
        """
        Initialize CI sync service.

        Args:
            repo: GitHub repo in "owner/repo" format (auto-detected if None)
            ingester: ViolationIngester instance (created if None)
        """
        self.repo = repo or self._detect_repo()
        self.ingester = ingester or ViolationIngester()
        self._last_sync: Optional[datetime] = None

    def _detect_repo(self) -> str:
        """Detect GitHub repo from git remote."""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            url = result.stdout.strip()

            # Parse GitHub URL (ssh or https)
            if "github.com" in url:
                # git@github.com:owner/repo.git or https://github.com/owner/repo.git
                if url.startswith("git@"):
                    repo = url.split(":")[1].replace(".git", "")
                else:
                    repo = url.split("github.com/")[1].replace(".git", "")
                return repo
        except Exception as e:
            logger.warning(f"[OUROBOROS] Failed to detect repo: {e}")

        return "unknown/unknown"

    def sync_latest(self, workflow: str = "steward-ci.yml") -> Dict[str, Any]:
        """
        Sync the latest CI run results.

        Args:
            workflow: Workflow file name to sync

        Returns:
            Sync result summary
        """
        result = {
            "synced_at": datetime.now().isoformat(),
            "workflow": workflow,
            "runs_checked": 0,
            "violations_ingested": 0,
            "errors": [],
        }

        try:
            # Get latest run ID
            run_info = self._get_latest_run(workflow)
            if not run_info:
                result["errors"].append("No recent CI runs found")
                return result

            result["run_id"] = run_info.get("databaseId")
            result["run_status"] = run_info.get("status")
            result["run_conclusion"] = run_info.get("conclusion")
            result["runs_checked"] = 1

            # Only sync failed runs
            if run_info.get("conclusion") == "failure":
                violations = self._extract_violations_from_run(run_info)
                if violations:
                    count = self.ingester.ingest(violations)
                    result["violations_ingested"] = count

            self._last_sync = datetime.now()
            logger.info(f"[OUROBOROS] CI sync complete: {result['violations_ingested']} violations ingested")

        except Exception as e:
            logger.error(f"[OUROBOROS] CI sync failed: {e}")
            result["errors"].append(str(e))

        return result

    def _get_latest_run(self, workflow: str) -> Optional[Dict[str, Any]]:
        """Get latest workflow run info using gh CLI."""
        try:
            result = subprocess.run(
                [
                    "gh",
                    "run",
                    "list",
                    "--workflow",
                    workflow,
                    "--limit",
                    "1",
                    "--json",
                    "databaseId,status,conclusion,name,createdAt,headBranch",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                runs = json.loads(result.stdout)
                return runs[0] if runs else None

        except FileNotFoundError:
            logger.warning("[OUROBOROS] gh CLI not found. Install with: brew install gh")
        except Exception as e:
            logger.warning(f"[OUROBOROS] Failed to get CI run: {e}")

        return None

    def _extract_violations_from_run(self, run_info: Dict[str, Any]) -> List[ViolationRecord]:
        """
        Extract violations from a failed CI run.

        This downloads the run logs and parses them for error patterns.
        """
        violations = []
        run_id = run_info.get("databaseId")

        if not run_id:
            return violations

        try:
            # Get failed jobs
            result = subprocess.run(
                [
                    "gh",
                    "run",
                    "view",
                    str(run_id),
                    "--json",
                    "jobs",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return violations

            data = json.loads(result.stdout)
            jobs = data.get("jobs", [])

            for job in jobs:
                if job.get("conclusion") == "failure":
                    job_violations = self._extract_violations_from_job(run_id, job)
                    violations.extend(job_violations)

        except Exception as e:
            logger.warning(f"[OUROBOROS] Failed to extract violations: {e}")

        return violations

    def _extract_violations_from_job(
        self,
        run_id: int,
        job: Dict[str, Any],
    ) -> List[ViolationRecord]:
        """Extract violations from a failed job's logs."""
        violations = []
        job_name = job.get("name", "unknown")

        # Determine source based on job name
        source = ViolationSource.CI_BUILD
        if "lint" in job_name.lower():
            source = ViolationSource.CI_LINT
        elif "test" in job_name.lower():
            source = ViolationSource.CI_TEST
        elif "security" in job_name.lower():
            source = ViolationSource.CI_SECURITY

        try:
            # Download job logs
            with tempfile.TemporaryDirectory() as tmpdir:
                log_path = Path(tmpdir) / "job.log"

                result = subprocess.run(
                    [
                        "gh",
                        "run",
                        "view",
                        str(run_id),
                        "--job",
                        str(job.get("databaseId")),
                        "--log",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode == 0:
                    log_content = result.stdout
                    violations.extend(self._parse_log_for_violations(log_content, source))

        except Exception as e:
            logger.warning(f"[OUROBOROS] Failed to get job logs: {e}")

        # If no specific violations found, create a generic failure record
        if not violations:
            violations.append(
                ViolationRecord(
                    source=source,
                    rule_id=f"CI_FAILURE:{job_name}",
                    file_path=None,
                    line=None,
                    message=f"CI job '{job_name}' failed",
                    severity="HIGH",
                    has_remedy=False,
                    context={"job_name": job_name, "run_id": run_id},
                )
            )

        return violations

    def _parse_log_for_violations(
        self,
        log_content: str,
        source: ViolationSource,
    ) -> List[ViolationRecord]:
        """
        Parse CI log content for violation patterns.

        Recognizes common error formats from ruff, pytest, mypy, etc.
        """
        violations = []

        for line in log_content.split("\n"):
            # Ruff pattern: filename:line:col: CODE message
            if "::" in line and any(c in line for c in ["E", "F", "W"]):
                parts = line.split(":")
                if len(parts) >= 4:
                    file_path = parts[0].strip()
                    try:
                        line_no = int(parts[1])
                        # Extract code (e.g., F401)
                        rest = ":".join(parts[3:])
                        code = rest.split()[0] if rest else "UNKNOWN"

                        violations.append(
                            ViolationRecord(
                                source=ViolationSource.CI_LINT,
                                rule_id=code,
                                file_path=file_path,
                                line=line_no,
                                message=rest.strip(),
                                severity="MEDIUM",
                                has_remedy=True,
                            )
                        )
                    except (ValueError, IndexError) as e:
                        # OPUS-312: Log parse failures at debug (not critical)
                        import logging

                        logging.getLogger("OUROBOROS").debug(f"Lint line parse failed: {e}")

            # Pytest pattern: FAILED test_file.py::test_name
            elif "FAILED" in line and "::" in line:
                parts = line.split()
                for part in parts:
                    if "::" in part:
                        nodeid = part.strip()
                        file_path = nodeid.split("::")[0]

                        violations.append(
                            ViolationRecord(
                                source=ViolationSource.CI_TEST,
                                rule_id=f"TEST_FAILURE:{nodeid}",
                                file_path=file_path,
                                line=None,
                                message=f"Test failed: {nodeid}",
                                severity="HIGH",
                                has_remedy=False,
                            )
                        )
                        break

            # Error pattern: error: message
            elif line.strip().lower().startswith("error:"):
                violations.append(
                    ViolationRecord(
                        source=source,
                        rule_id="GENERIC_ERROR",
                        message=line.strip(),
                        severity="HIGH",
                        has_remedy=False,
                    )
                )

        return violations

    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status."""
        return {
            "repo": self.repo,
            "last_sync": self._last_sync.isoformat() if self._last_sync else None,
            "gh_cli_available": self._check_gh_cli(),
        }

    def _check_gh_cli(self) -> bool:
        """Check if gh CLI is available and authenticated."""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False
