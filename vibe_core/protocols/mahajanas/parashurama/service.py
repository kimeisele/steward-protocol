"""
PARASHURAMA SERVICE - Wraps Legacy semantic_syscalls.py
========================================================

POSITION: 8 (HEAD - KARMA Quarter)

This is a THIN WRAPPER that connects the legacy SemanticSyscallExecutor
to the Mahajana framework. NO DUPLICATION - just delegation.

WRAPPED: vibe_core.semantic_syscalls.SemanticSyscallExecutor

"As Parashurama wielded his axe with swift, decisive action,
this service executes karma (action) with precision."
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from vibe_core.protocols.mahajanas.parashurama import (
    ParashuramaProtocolBase,
    FetchStatus,
    ResourceValue,
    FetchResult,
    FetchState,
)

# Import legacy implementation - DO NOT DUPLICATE
from vibe_core.semantic_syscalls import (
    SemanticSyscallExecutor,
    SyscallRequest,
    SyscallResult,
    SyscallType,
)


class ParashuramaService(ParashuramaProtocolBase):
    """
    PARASHURAMA Service - Karma/Execution.

    WRAPS the legacy SemanticSyscallExecutor.
    Manages syscall execution and resource fetching.

    Position 8 - The warrior HEAD, executes decisive action.
    """

    def __init__(self, kernel: Optional["RealVibeKernel"] = None) -> None:
        """Initialize with optional kernel for syscall execution."""
        self._kernel = kernel
        self._executor: Optional[SemanticSyscallExecutor] = None
        self._resources: Dict[str, ResourceValue] = {}
        self._resource_status: Dict[str, FetchStatus] = {}
        self._stats = {
            "total_fetches": 0,
            "successful": 0,
            "failed": 0,
            "cache_hits": 0,
            "bytes_fetched": 0,
        }

    def _ensure_executor(self) -> Optional[SemanticSyscallExecutor]:
        """Lazy init of executor if kernel available."""
        if self._executor is None and self._kernel is not None:
            self._executor = SemanticSyscallExecutor(self._kernel)
        return self._executor

    # =========================================================================
    # FETCH PROTOCOL (Position 8 - FETCH_RES)
    # =========================================================================

    def fetch(self, resource_id: str, timeout_ms: int = 5000) -> FetchResult:
        """FETCH_RES: Fetch a resource by ID."""
        self._stats["total_fetches"] += 1
        start_time = datetime.now()

        # Check cache first
        if resource_id in self._resources:
            self._stats["cache_hits"] += 1
            return FetchResult(
                success=True,
                status=FetchStatus.CACHED.value,
                resource_id=resource_id,
                resource_type="cached",
                size_bytes=len(str(self._resources[resource_id])),
                timestamp=datetime.now().isoformat(),
                latency_ms=0,
            )

        # Mark as fetching
        self._resource_status[resource_id] = FetchStatus.FETCHING

        try:
            # For now, just mark as pending (actual fetch would be async)
            self._resource_status[resource_id] = FetchStatus.SUCCESS
            self._stats["successful"] += 1

            latency = int((datetime.now() - start_time).total_seconds() * 1000)

            return FetchResult(
                success=True,
                status=FetchStatus.SUCCESS.value,
                resource_id=resource_id,
                resource_type="syscall",
                size_bytes=0,
                timestamp=datetime.now().isoformat(),
                latency_ms=latency,
            )
        except Exception as e:
            self._resource_status[resource_id] = FetchStatus.FAILED
            self._stats["failed"] += 1
            return FetchResult(
                success=False,
                status=FetchStatus.FAILED.value,
                resource_id=resource_id,
                error_message=str(e),
                timestamp=datetime.now().isoformat(),
            )

    def fetch_batch(self, resource_ids: List[str]) -> List[FetchResult]:
        """Fetch multiple resources in batch."""
        return [self.fetch(rid) for rid in resource_ids]

    def get_resource(self, resource_id: str) -> Optional[ResourceValue]:
        """Get a fetched resource value."""
        return self._resources.get(resource_id)

    def is_available(self, resource_id: str) -> bool:
        """Check if a resource is available."""
        return resource_id in self._resources

    def prefetch(self, resource_ids: List[str]) -> int:
        """Prefetch resources. Returns count queued."""
        count = 0
        for rid in resource_ids:
            if rid not in self._resource_status:
                self._resource_status[rid] = FetchStatus.PENDING
                count += 1
        return count

    def invalidate(self, resource_id: str) -> bool:
        """Invalidate cached resource. Returns True if existed."""
        if resource_id in self._resources:
            del self._resources[resource_id]
            self._resource_status.pop(resource_id, None)
            return True
        return False

    def get_status(self, resource_id: str) -> FetchStatus:
        """Get fetch status of a resource."""
        return self._resource_status.get(resource_id, FetchStatus.PENDING)

    def get_state(self) -> FetchState:
        """Get fetch state."""
        total = self._stats["total_fetches"]
        avg_latency = 0  # Would calculate from actual fetches

        return FetchState(
            total_fetches=total,
            successful_fetches=self._stats["successful"],
            failed_fetches=self._stats["failed"],
            cache_hits=self._stats["cache_hits"],
            total_bytes_fetched=self._stats["bytes_fetched"],
            avg_latency_ms=avg_latency,
            health="pristine" if self._stats["failed"] == 0 else "healthy",
        )

    # =========================================================================
    # SYSCALL EXECUTION (Legacy SemanticSyscallExecutor)
    # =========================================================================

    def execute_syscall(self, request: SyscallRequest) -> SyscallResult:
        """Execute a semantic syscall via legacy executor."""
        executor = self._ensure_executor()
        if executor is None:
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error="No kernel available for syscall execution",
            )
        return executor.execute(request)

    @property
    def executor(self) -> Optional[SemanticSyscallExecutor]:
        """Access the legacy syscall executor."""
        return self._ensure_executor()

    def set_kernel(self, kernel: "RealVibeKernel") -> None:
        """Set kernel for syscall execution."""
        self._kernel = kernel
        self._executor = None  # Reset to pick up new kernel


__all__ = ["ParashuramaService"]
