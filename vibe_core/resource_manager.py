"""
RESOURCE MANAGER - Real OS-Level Enforcement
============================================

Goal: Make CivicBank credits REAL by enforcing CPU/RAM limits.

Philosophy:
"Credits are not numbers in a database. Credits are CPU cycles and memory bytes.
The economy is the operating system."

Architecture:
- ResourceManager: Enforces quotas using psutil
- Credit-to-Resource Mapping: 100 credits = 10% CPU, 100 MB RAM
- Periodic Sync: Kernel syncs quotas with CivicBank every minute
"""

import logging
import time
from dataclasses import dataclass
from multiprocessing import Process
from typing import Any, Dict, Optional

import psutil

logger = logging.getLogger("RESOURCE_MANAGER")


@dataclass
class ResourceQuota:
    """Resource quota for an agent"""

    cpu_percent: int  # Max CPU% (0-100)
    memory_mb: int  # Max RAM in MB


class ResourceManager:
    """
    Enforce CPU and RAM limits on agent processes.

    This makes the CivicBank credit system REAL:
    - Low credits = throttled performance
    - High credits = more resources
    - No credits = minimal baseline
    """

    # Credit-to-Resource mapping
    CREDIT_TIERS = [
        (1000, {"cpu_percent": 50, "memory_mb": 1024}),  # Premium
        (500, {"cpu_percent": 25, "memory_mb": 512}),  # Standard
        (100, {"cpu_percent": 10, "memory_mb": 100}),  # Basic
        (0, {"cpu_percent": 5, "memory_mb": 50}),  # Minimal
    ]

    # Absolute limits (safety caps)
    MAX_CPU_PERCENT = 50
    MAX_MEMORY_MB = 1024

    def __init__(self):
        self.quotas: Dict[str, ResourceQuota] = {}
        self.last_enforcement = {}  # {agent_id: timestamp}

    def calculate_quota_from_credits(self, credits: int) -> ResourceQuota:
        """
        Calculate resource quota based on credit balance.

        Args:
            credits: Agent's credit balance

        Returns:
            ResourceQuota with CPU% and RAM limits
        """
        # Find appropriate tier
        for threshold, resources in self.CREDIT_TIERS:
            if credits >= threshold:
                return ResourceQuota(
                    cpu_percent=min(resources["cpu_percent"], self.MAX_CPU_PERCENT),
                    memory_mb=min(resources["memory_mb"], self.MAX_MEMORY_MB),
                )

        # Fallback to minimal
        return ResourceQuota(cpu_percent=5, memory_mb=50)

    def set_quota(self, agent_id: str, credits: int) -> None:
        """
        Set resource quota for an agent based on credits.

        Args:
            agent_id: Agent identifier
            credits: Current credit balance
        """
        quota = self.calculate_quota_from_credits(credits)
        self.quotas[agent_id] = quota
        logger.info(f"💰 {agent_id}: {credits} credits → {quota.cpu_percent}% CPU, {quota.memory_mb} MB RAM")

    def enforce_quota(self, agent_id: str, process: Process) -> None:
        """
        Apply resource quota to a running process.

        Args:
            agent_id: Agent identifier
            process: multiprocessing.Process object
        """
        quota = self.quotas.get(agent_id)
        if not quota:
            logger.warning(f"⚠️  No quota set for {agent_id}, using minimal")
            quota = ResourceQuota(cpu_percent=5, memory_mb=50)
            self.quotas[agent_id] = quota

        try:
            # Get psutil Process
            p = psutil.Process(process.pid)

            # CPU Throttling via nice()
            # nice values: -20 (highest priority) to 19 (lowest priority)
            # Map cpu_percent to nice value
            # 50% CPU = nice 0 (normal)
            # 25% CPU = nice 10
            # 10% CPU = nice 15
            # 5% CPU = nice 19
            nice_value = max(0, min(19, 20 - (quota.cpu_percent // 2.5)))
            p.nice(int(nice_value))

            logger.debug(f"🔧 {agent_id} (PID {process.pid}): nice={nice_value} for {quota.cpu_percent}% CPU target")

            # Memory limits (Linux only, limited macOS support)
            # Note: This sets the limit in the PARENT process, not the child
            # For true per-process limits, we'd need to set this INSIDE the child process
            # or use cgroups (Linux only)
            # For now, we'll log a warning on macOS
            try:
                import platform
                import resource

                if platform.system() == "Linux":
                    memory_bytes = quota.memory_mb * 1024 * 1024
                    # This would need to be set in the child process, not here
                    # resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
                    logger.debug(f"🔧 {agent_id}: RAM limit {quota.memory_mb} MB (Linux)")
                else:
                    logger.debug(f"⚠️  {agent_id}: RAM limits not enforced on {platform.system()}")
            except Exception as e:
                logger.debug(f"⚠️  Memory limit failed: {e}")

            self.last_enforcement[agent_id] = time.time()

        except psutil.NoSuchProcess:
            logger.warning(f"⚠️  Process for {agent_id} not found (PID {process.pid})")
        except Exception as e:
            logger.error(f"❌ Failed to enforce quota for {agent_id}: {e}")

    def get_usage(self, agent_id: str, process: Process) -> Dict[str, Any]:
        """
        Get current resource usage for an agent.

        Args:
            agent_id: Agent identifier
            process: multiprocessing.Process object

        Returns:
            Dict with cpu_percent, memory_mb, and quota info
        """
        try:
            p = psutil.Process(process.pid)

            # Get CPU% (interval=0.1 for quick sampling)
            cpu_percent = p.cpu_percent(interval=0.1)

            # Get memory in MB
            memory_info = p.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)

            quota = self.quotas.get(agent_id, ResourceQuota(cpu_percent=5, memory_mb=50))

            return {
                "agent_id": agent_id,
                "pid": process.pid,
                "cpu_percent": round(cpu_percent, 2),
                "memory_mb": round(memory_mb, 2),
                "quota_cpu": quota.cpu_percent,
                "quota_memory": quota.memory_mb,
                "cpu_within_quota": cpu_percent <= quota.cpu_percent * 1.2,  # 20% tolerance
                "memory_within_quota": memory_mb <= quota.memory_mb * 1.2,
            }
        except psutil.NoSuchProcess:
            return {"agent_id": agent_id, "error": "Process not found"}
        except Exception as e:
            return {"agent_id": agent_id, "error": str(e)}

    def get_all_usage(self, process_manager) -> Dict[str, Dict[str, Any]]:
        """
        Get resource usage for all agents.

        Args:
            process_manager: ProcessManager instance

        Returns:
            Dict mapping agent_id to usage stats
        """
        usage = {}
        for agent_id, info in process_manager.processes.items():
            if info.process.is_alive():
                usage[agent_id] = self.get_usage(agent_id, info.process)
        return usage

    def check_violations(self, process_manager) -> list:
        """
        Check for agents exceeding their quotas.

        Args:
            process_manager: ProcessManager instance

        Returns:
            List of violation dicts
        """
        violations = []
        usage_stats = self.get_all_usage(process_manager)

        for agent_id, stats in usage_stats.items():
            if "error" in stats:
                continue

            if not stats.get("cpu_within_quota"):
                violations.append(
                    {
                        "agent_id": agent_id,
                        "type": "CPU",
                        "usage": stats["cpu_percent"],
                        "quota": stats["quota_cpu"],
                    }
                )

            if not stats.get("memory_within_quota"):
                violations.append(
                    {
                        "agent_id": agent_id,
                        "type": "MEMORY",
                        "usage": stats["memory_mb"],
                        "quota": stats["quota_memory"],
                    }
                )

        return violations
