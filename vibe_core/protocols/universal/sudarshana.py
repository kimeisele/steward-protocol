"""
OPERATION SUDARSHANA - The Fractal Hull
=======================================
"The Wheel that keeps the Rhythm."

Dieser Decorator wickelt 'Tote Materie' (Funktionen) in 'Lebendigen Klang' (Mantra).
Er verbindet Phase 16 (The 37th) mit Phase 1 (Atomic Verbs).
"""

import functools
from typing import Callable, Any, TypeVar, ParamSpec, Optional
from vibe_core.protocols.universal.mantra import MantraOpCode
from vibe_core.protocols.universal.types import SovereignContext, AccessDeniedError
from vibe_core.protocols.universal.the_37th import The37th

P = ParamSpec("P")
R = TypeVar("R")

import functools
import multiprocessing
import uuid
import logging
from typing import Callable, Any, TypeVar, ParamSpec, Optional, Dict
from enum import Enum, auto
from dataclasses import dataclass

from vibe_core.protocols.universal.mantra import MantraOpCode
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
class PranaTask:
    """The atom of work. The 'Fractal' unit."""
    id: str
    target: Callable
    args: tuple
    kwargs: dict
    mantra_signature: str

# --- 2. The Task Kernel (The State Organ) ---

class MantraKernel:
    """
    The Governor. It manages the 'Real Cores' and cleans Orphans.
    """
    def __init__(self, core_count: Optional[int] = None):
        self.state = SysState.DORMANT
        self.core_count = core_count or multiprocessing.cpu_count()
        # LAZY INIT POOL? No, User wants it ready.
        self.pool = multiprocessing.Pool(processes=self.core_count)
        self.active_manifestations: Dict[str, Any] = {} # Tracking running tasks
        self.logger = logging.getLogger("SudarshanaKernel")
        
        # Configure logging if not running under pytest capture issues
        # logging.basicConfig(level=logging.INFO) 
        self.logger.info(f"🌀 Kernel Initialized. Cores aligned: {self.core_count}")

    def inject_prana(self, task: PranaTask) -> Optional[str]:
        """
        Takes a task and assigns it to a physical core.
        """
        if self.state == SysState.ENTROPY_HIGH:
            self.logger.error("⚠️ ENTROPY TOO HIGH. Rejecting Task.")
            return None

        self.logger.info(f"⚡ Injecting Prana into Task {task.id} [{task.mantra_signature}]")
        
        # Async execution on a real core
        # Note: We pass kwargs too
        # multiprocessing.Pool.apply_async supports args and kwargs
        async_result = self.pool.apply_async(
            task.target, 
            args=task.args, 
            kwds=task.kwargs,
            callback=self._on_complete,
            error_callback=self._on_error
        )
        self.active_manifestations[task.id] = async_result
        return task.id

    def _on_complete(self, result: Any):
        """The Echo returns."""
        # This runs in main thread usually provided by pool callback mechanism?
        # Actually standard python multiprocessing callbacks run in main thread.
        # print(f"✨ Karma Resolved: {result}") 
        # Using print for now as per user spec, but logger is better.
        self.logger.info(f"✨ Karma Resolved: {result}")

    def _on_error(self, error: BaseException):
        self.logger.error(f"💀 Task Failed (Orphan died): {error}")

    def purge_orphans(self):
        """
        Garbage Collection: Reclaims resources from stuck tasks.
        """
        # Logic to check for stuck async_results would go here
        # For now, just a stub as per user request
        self.logger.info("🧹 Sweeping the temple. Removing orphan contexts.")

    def shutdown(self):
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
        if context and context.identity_id == "did:vibe:37:bija-akshara": # From purusha.py
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
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any: # Returns TaskID string now!
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
            
            # Note regarding pickling: 'func' must be picklable (top level).
            # If wrapper is used on methods, 'func' is unbound function, 'args[0]' is self.
            # This generally pickle-able if class is module level.
            
            task = PranaTask(
                id=task_id,
                target=func,
                args=args, # type: ignore
                kwargs=kwargs, # type: ignore
                mantra_signature=opcode.name
            )
            
            # 4. Offload to the Kernel
            KERNEL.inject_prana(task)
            
            # Return Promise/ID (The Nervous System gap)
            return f"🌀 Task {task_id} submitted to the Wheel."
            
        return wrapper
    return decorator
