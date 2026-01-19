"""
OPERATION SUDARSHANA - The Fractal Hull
=======================================
"The Wheel that keeps the Rhythm."

Dieser Decorator wickelt 'Tote Materie' (Funktionen) in 'Lebendigen Klang' (Mantra).
Er verbindet Phase 16 (The 37th) mit Phase 1 (Atomic Verbs).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x66f4e2ed"  # GenesisByte: parampara % 37 == 0

import functools
import multiprocessing
import uuid
import logging
import traceback
from typing import Callable, Any, TypeVar, ParamSpec, Optional, Dict, Generic
from enum import Enum, auto
from dataclasses import dataclass
from multiprocessing.pool import AsyncResult

from vibe_core.mahamantra.substrate.opcode import MantraOpCode
from vibe_core.protocols.universal.types import SovereignContext, AccessDeniedError
from vibe_core.protocols.universal.the_37th import The37th

P = ParamSpec("P")
R = TypeVar("R")

# --- 1. The Protocol Definition ---


class SysState(Enum):
    DORMANT = 0
    AWAKE = 1
    ENTROPY_HIGH = 99  # Panic state


@dataclass
class PranaTask(Generic[R]):
    """The atom of work. The 'Fractal' unit."""

    id: str
    target: Callable[..., R]
    args: tuple
    kwargs: dict
    mantra_signature: str


@dataclass
class PranaFailure:
    """
    Represents a failed manifestation.
    Carries the trace of the entropy (Exception) back to the source.
    """

    error: Exception
    traceback: str
    task_id: str


class MantraCrash(Exception):
    """
    Raised in the main thread when a worker dies.
    """

    pass


class PranaFuture(Generic[R]):
    """
    The Nervous System (Nadi).
    Connects the separated Limb (Worker) back to the Brain (Main Thread).
    """

    def __init__(self, task_id: str, async_result: AsyncResult):
        self.task_id = task_id
        self._val = async_result

    def get(self, timeout: Optional[float] = None) -> R:
        """
        Synchronous waiting for the result.
        Unwraps PranaFailure -> Excetion (Immune Response).
        """
        try:
            result = self._val.get(timeout=timeout)

            # The Immune Check: Is it a Failure?
            if isinstance(result, PranaFailure):
                # Re-raise it locally so logic can handle it
                # We could log here, but the Kernel logs errors too.
                # Just bridging the gap.
                raise result.error

            return result  # type: ignore

        except multiprocessing.TimeoutError:
            raise TimeoutError(f"Task {self.task_id} timed out.")

    def wait(self, timeout: Optional[float] = None) -> None:
        self._val.wait(timeout)

    def ready(self) -> bool:
        return self._val.ready()

    def successful(self) -> bool:
        return self._val.successful()

    def __repr__(self) -> str:
        state = "READY" if self.ready() else "PENDING"
        return f"<PranaFuture {self.task_id} [{state}]>"


# --- 2. The Task Kernel (The State Organ) ---
# MantraKernel: The Governor of Prana (Compute).
# Distinct from 'TaskKernel' (Logical Sandbox).


def _guarded_execution(task: PranaTask[R]) -> Any:
    """
    The Immune Wrapper. Runs on the 'Real Core'.
    It catches exceptions and converts them into PranaFailure data.
    Note: Returns Any because it returns either R or PranaFailure.
    """
    try:
        # 1. Execute the Legacy Code
        # Note: task.target might require unpacking args/kwargs or similar
        # Based on how we constructed it: target=func, args=args, kwargs=kwargs
        return task.target(*task.args, **task.kwargs)
    except Exception as e:
        # 2. Catch the Entropy
        return PranaFailure(error=e, traceback=traceback.format_exc(), task_id=task.id)


class MantraKernel:
    """
    The Governor of Prana (Compute).
    This Kernel manages the Sudarshana Chakra (The Process Pool).
    """

    def __init__(self, core_count: Optional[int] = None):
        self.state = SysState.DORMANT
        self.core_count = core_count or multiprocessing.cpu_count()
        # LAZY INIT POOL? No, User wants it ready.
        self.pool = multiprocessing.Pool(processes=self.core_count)
        self.active_manifestations: Dict[str, AsyncResult] = {}  # Tracking running tasks
        self.logger = logging.getLogger("MantraKernel")

        # Configure logging if not running under pytest capture issues
        # logging.basicConfig(level=logging.INFO)
        self.logger.info(f"🌀 MantraKernel Initialized. Cores aligned: {self.core_count}")

    def inject_prana(self, task: PranaTask[R]) -> PranaFuture[R]:
        """
        Takes a task and assigns it to a physical core.
        Returns a PranaFuture (Nervous System Link).
        """
        if self.state == SysState.ENTROPY_HIGH:
            self.logger.error("⚠️ ENTROPY TOO HIGH. Rejecting Task.")
            raise MantraCrash("MantraKernel Rejected Task: Entropy High")

        self.logger.info(f"⚡ Injecting Prana into Task {task.id} [{task.mantra_signature}]")

        # Async execution on a real core
        # We wrap the call in _guarded_execution
        # Note: apply_async(func, args, kwds) arguments must be pickleable.
        # _guarded_execution is top level, so it is pickleable.

        async_result = self.pool.apply_async(
            _guarded_execution,
            args=(task,),  # Pass the task object as the argument
            callback=self._on_complete,
            error_callback=self._on_error,
        )
        self.active_manifestations[task.id] = async_result

        # Return the Nadi (Link)
        return PranaFuture(task.id, async_result)

    def _on_complete(self, result: object) -> None:
        """The Echo returns."""
        # This callback runs in the result thread (helper).
        if isinstance(result, PranaFailure):
            self.logger.warning(f"💀 Task Failed (Caught by Immune System): {result.error}")
        else:
            self.logger.info(f"✨ Karma Resolved: {str(result)[:50]}")

    def _on_error(self, error: BaseException) -> None:
        # This caches POOL level mechanism errors, or unchecked errors
        self.logger.error(f"💀 Task Failed (Orphan died/Unchecked): {error}")

    def purge_orphans(self) -> None:
        """
        Garbage Collection: Reclaims resources from stuck tasks.
        """
        self.logger.info("🧹 Sweeping the temple. Removing orphan contexts.")

    def shutdown(self) -> None:
        self.pool.close()
        self.pool.join()
        self.logger.info("🛑 Kali Yuga containment. System Halt.")


# --- 3. The Sudarshana Chakra (Updated) ---


class SudarshanaChakra:
    """
    Das drehende Rad. Es schneidet Karma (Latenz) und schützt Dharma (Integrität).
    """

    @staticmethod
    def spin(opcode: MantraOpCode, context: Optional[SovereignContext]) -> bool:
        """
        Führt einen Takt-Zyklus aus.
        """
        # 1. 37th OVERRIDE (Venu-Gita Check)
        if context and context.identity_id == "did:vibe:37:bija-akshara":  # From purusha.py
            return True

        # 2. STANDARD MANTRA CHECK
        # print(f"🌀 SUDARSHANA SPIN: {opcode.name}")
        return True


# GLOBAL KERNEL (The Living Spirit)
# Warning: This spawns processes on import!
KERNEL = MantraKernel()


def mantra_governed(opcode: MantraOpCode):
    """
    The updated decorator. instead of running immediately,
    it submits to the Kernel for 'Real Core' processing.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> PranaFuture[R]:  # Returns Future now!
            # 1. Context Extraktion (Suche nach SovereignContext in Args)
            context = None
            for arg in args:
                if isinstance(arg, SovereignContext):
                    context = arg
                    break

            if context is None:
                for val in kwargs.values():
                    if isinstance(val, SovereignContext):
                        context = val
                        break

            # 2. Sudarshana Spin (Der Schnitt)
            SudarshanaChakra.spin(opcode, context)

            # 3. Packaging the Dead Matter into Living Task
            task_id = str(uuid.uuid4())[:8]

            task = PranaTask(
                id=task_id,
                target=func,
                args=args,  # type: ignore
                kwargs=kwargs,  # type: ignore
                mantra_signature=opcode.name,
            )

            # 4. Offload to the Kernel
            return KERNEL.inject_prana(task)

        return wrapper

    return decorator
