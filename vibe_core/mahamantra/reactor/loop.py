"""
PERSISTENT REACTOR LOOP - The Eternal Heartbeat (Arjuna Pattern)
================================================================

"na tv evāhaṁ jātu nāsaṁ na tvaṁ neme janādhipāḥ"
"Never was there a time when I did not exist, nor you, nor all these kings."
— Bhagavad Gita 2.12

This module implements the PERSISTENT lifecycle of the ShadowReactor.
It replaces the ephemeral "Zombie" model with a living, breathing loop.

COMPONENTS:
1. MahaMailbox: The bridge between Async Loop and Sync Callers.
2. ReactorLoop: The eternal thread that drives the reactor.

ARJUNA PATTERN (Self-Healing):
- The Loop MUST NOT DIE.
- If the Reactor crashes, it is reborn.
- If a tick fails, the result is still delivered (FailureResult).
"""
import logging
import threading
import queue
import time
import uuid
from typing import Dict, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from vibe_core.mahamantra.substrate.cell import MahaCellUnified
from dataclasses import dataclass, field

from vibe_core.mahamantra.reactor.shadow import ShadowReactor, ShadowState

logger = logging.getLogger(__name__)

# CONSTANTS
LOOP_INTERVAL_S = 0.01  # 10ms heartbeat in idle
MAILBOX_TIMEOUT_S = 10.0  # Max time to wait for a result


@dataclass
class LoopRequest:
    """A request to the Reactor Loop."""
    tracking_id: str
    maha_cell: "MahaCellUnified"  # Typed reference
    purpose: str
    target_position: int = -1  # For routed requests (Teleportation)


class MahaMailbox:
    """
    Thread-safe mailbox for async results.
    
    Maps tracking_id -> Result.
    Sync callers wait on a specific tracking_id.
    """
    def __init__(self):
        self._results: Dict[str, object] = {}
        self._events: Dict[str, threading.Event] = {}
        self._lock = threading.Lock()

    def create_ticket(self) -> str:
        """Generate a tracking ID and prepare a wait event."""
        tracking_id = str(uuid.uuid4())
        with self._lock:
            self._events[tracking_id] = threading.Event()
        return tracking_id

    def deposit(self, tracking_id: str, result: object) -> None:
        """Deposit a result and wake up the waiter."""
        with self._lock:
            if tracking_id in self._events:
                self._results[tracking_id] = result
                self._events[tracking_id].set()
            else:
                logger.warning(f"Mailbox: Deposited result for unknown/expired ID {tracking_id}")

    def collect(self, tracking_id: str, timeout: float = MAILBOX_TIMEOUT_S) -> object:
        """
        Wait for and retrieve a result.
        
        Returns:
            The result object/dict.
        Raises:
            TimeoutError: If no result arrives in time.
        """
        event = None
        with self._lock:
            event = self._events.get(tracking_id)
        
        if not event:
            raise ValueError(f"Invalid tracking ID: {tracking_id}")

        # Wait for the loop to process
        signaled = event.wait(timeout)

        # Cleanup immediately
        with self._lock:
            result = self._results.pop(tracking_id, None)
            del self._events[tracking_id]
        
        if not signaled:
            raise TimeoutError(f"Mailbox timed out waiting for {tracking_id}")
            
        return result


class ReactorLoop(threading.Thread):
    """
    The Eternal Thread.
    
    Hosts the ShadowReactor instance and keeps it alive.
    """
    def __init__(self):
        super().__init__(name="ReactorLoop-1", daemon=True)
        self._queue: queue.Queue[LoopRequest] = queue.Queue()
        self._mailbox: Optional[MahaMailbox] = None
        self._reactor: Optional[ShadowReactor] = None
        self._running = False
        self._stop_event = threading.Event()
        self._idle_ticks = 0
        self._bus: Optional[object] = None  # Narada (Initialized in run)
        self._dojo: Optional[object] = None  # Dojo (Initialized in run)
        self._ready_event = threading.Event()
        
    def attach_mailbox(self, mailbox: MahaMailbox):
        """Connect the loop to a mailbox."""
        self._mailbox = mailbox

    def submit(self, maha_cell: "MahaCellUnified", purpose: str, target_position: int = -1) -> str:
        """
        Submit work to the loop. 
        Returns tracking_id to wait on.
        """
        if not self._mailbox:
            raise RuntimeError("ReactorLoop has no mailbox attached!")
            
        ticket = self._mailbox.create_ticket()
        request = LoopRequest(ticket, maha_cell, purpose, target_position)
        self._queue.put(request)
        return ticket
        
    def wait_until_ready(self, timeout: float = 5.0) -> bool:
        """Wait for the reactor loop to fully initialize."""
        if self._running:
            return True
        return self._ready_event.wait(timeout)

    def publish(self, event_type: str, agent_id: str, message: str, details: Optional[Dict] = None, task_id: Optional[str] = None) -> str:
        """
        Broadcasting Intent (Resonance Routing).
        Delegates to Narada (EventBus).
        """
        if self._bus:
            # Import expected EventType if needed, or use string
            # For now passing string is fine as EventBus handles it
            return self._bus.emit_sync(event_type, agent_id, message, details, task_id)
        else:
            logger.warning("ReactorLoop: Attempted to publish but Narada sleeps.")
            return ""

    def run(self):
        """The Main Loop."""
        # Yield to allow main thread to complete imports (avoid import deadlock)
        time.sleep(0.1)
        
        logger.info("ReactorLoop: STARTING (Hari Bol!)")
        
        # 1. Initialize Reactor (First Birth)
        self._init_memory()  # NEW: Awaken Memory (Phase 3)
        self._init_bus()     # NEW: Wake Narada (Phase 4)
        self._init_dojo()    # NEW: Open Dojo (Phase 5)
        self._init_reactor()
        
        # 2. Wire the Cosmos (Auto-Discovery)
        # Must happen AFTER reactor exists
        self._wire_bus()
        
        self._running = True
        self._ready_event.set() # Signal readiness
        
        while not self._stop_event.is_set():
            try:
                # 2. Fetch Work
                try:
                    request = self._queue.get(timeout=LOOP_INTERVAL_S)
                except queue.Empty:
                    # Idle heartbeat
                    self._meditate()
                    continue
                
                # 3. Process Work (The Tick)
                self._process_request(request)
                
            except Exception as e:
                # ARJUNA PATTERN: Global Loop Safety
                # If the loop logic itself crashes, we catch it here.
                logger.critical(f"ReactorLoop CRITICAL FAILURE: {e}", exc_info=True)
                # We can't easily notify the mailbox here because we might not know 
                # which request caused the crash if it happened outside _process_request.
                # But _process_request has its own try/catch.
                
                # Re-init reactor if it seems dead
                pass # Continue loop

        logger.info("ReactorLoop: STOPPING")

    def _wire_bus(self):
        """
        Auto-wire Mahajanas to the EventBus.
        "Yatha Pinde Tatha Brahmande"
        """
        if not self._bus or not self._reactor:
            return

        try:
            # 1. Self-Subscription (Closing the Loop)
            self._bus.subscribe(self.on_completion, ["COMPLETED"])
            
            # 2. Iterate the Mandala (16 Positions)
            for pos in range(16):
                try:
                    module = self._reactor._route_to_position(pos)
                    
                    if not module:
                        continue
                        
                    if hasattr(module, "on_event") and hasattr(module, "__listening_for__"):
                        events = getattr(module, "__listening_for__")
                        if events and isinstance(events, list):
                            self._bus.subscribe(module.on_event, events)
                            logger.info(f"ReactorLoop: Auto-wired Pos {pos} ({module.__name__}) to {events}")
                            
                except Exception as e:
                    logger.warning(f"ReactorLoop: Failed to wire Pos {pos}: {e}")

        except Exception as e:
            logger.error(f"ReactorLoop: Failed to wire bus: {e}")

    def _init_memory(self):
        """Register the Persistent Memory (The Soul's Context)."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.memory import MemoryProtocol
            from vibe_core.mahamantra.substrate.memory import PersistentMemory
            
            # Register Global Memory for Mahamantra
            # Phase 3: "Kapila's Promotion" relies on this.
            memory = PersistentMemory()
            ServiceRegistry.register(MemoryProtocol, memory)
            logger.info("ReactorLoop: PersistentMemory registered (Akshara).")
            
        except Exception as e:
            logger.error(f"ReactorLoop: Failed to register Memory: {e}")

    def _init_reactor(self):
        """Spawn or Re-spawn the ShadowReactor."""
        try:
            logger.info("ReactorLoop: Spawning ShadowReactor...")
            # Using forced_lagna=0 for direct mapping, as established in Phase 1
            self._reactor = ShadowReactor(auto_discover=True, forced_lagna=0)
            
            # SANKIRTAN MERCY: Grant authorization
            # "api cet su-durācāro..." (Gita 9.30)
            self._reactor._sankirtan_shakti = 108.0 
            
        except Exception as e:
            logger.error(f"ReactorLoop: Failed to init reactor: {e}")
            # If we can't spawn, we are in trouble. Sleep and retry?
            time.sleep(1.0)
            
    def _init_bus(self):
        """Initialize the EventBus (Narada)."""
        try:
            from vibe_core.mahamantra.substrate.event_bus import EventBus
            self._bus = EventBus()
            logger.info("ReactorLoop: Narada (EventBus) awakened.")
        except Exception as e:
            logger.error(f"ReactorLoop: Failed to init EventBus: {e}")

    def on_completion(self, event):
        """
        Handle COMPLETED events (Resonance Return).
        Resolve Mailbox tickets if applicable.
        """
        if not self._mailbox or not event.task_id:
            return
            
        # Extract result
        # The Kapila protocol puts result in details["result"]
        # Or generally in details
        result_data = event.details
        
        # We need to structure it as the Bridge expects:
        # { "success": bool, "execution_result": ..., "error": ... }
        # If the event implies success (it's COMPLETED), we assume success unless ERROR event (which we don't catch yet).
        # Improving Protocol: catch ERROR events too?
        
        # For now, construct a success result
        final_result = {
            "success": True,
            "execution_result": result_data.get("result"),
            "error": None
        }
        
        self._mailbox.deposit(event.task_id, final_result)

    def _init_dojo(self):
        """Initialize the Dojo (Legacy Training Ground)."""
        try:
            # Import lazily to avoid heavy startup if not needed
            from vibe_core.plugins.opus_assistant.manas.dojo.runner import DojoRunner
            from pathlib import Path
            # Use default workspace or specific dojo path?
            # Assuming current working dir or derived from env
            workspace = Path(".") 
            self._dojo = DojoRunner(workspace)
            logger.info("ReactorLoop: DojoRunner initialized for Meditation.")
        except Exception as e:
            logger.error(f"ReactorLoop: Failed to init Dojo: {e}")

    def _meditate(self):
        """
        Perform background duties when the reactor is idle.
        "dhyāyen nārāyaṇaṁ devam" - Meditate on the Lord.
        
        The Reactor is ALIVE. It breathes (ticks) even when no one is asking.
        """
        self._idle_ticks += 1
        
        # MEDITATION RHYTHM:
        # Loop interval is ~10ms.
        # We don't want to spin too fast. 
        # Chant every 10 ticks = 100ms = 10Hz frequency.
        if self._idle_ticks % 10 == 0:
            if self._reactor:
                try:
                    # DRIVE THE CYCLE: Manually advance position
                    # "cakram parivartayāmi" - I turn the wheel.
                    current_pos = self._reactor.position
                    next_pos = (current_pos + 1) % 16
                    self._reactor._position = next_pos
                    
                    # Self-Chant
                    tick_state = {
                        "tick": next_pos,
                        "position": next_pos,
                        "quarter": self._reactor.get_state()["quarter"], # Carry forward
                        "guardian": self._reactor.get_state()["guardian"],
                        "word": "OM", # The sound of silence
                        "opcode": None 
                    }
                    self._reactor.tick(tick_state)
                    
                    # Periodic Log (every 108 chants = ~10s)
                    if self._idle_ticks % 1080 == 0:
                         logger.debug(f"ReactorLoop: Meditating... (Cycle: {self._reactor.cycle_count}, Pos: {self._reactor.position})")
                
                    # DOJO TICK (Legacy Mounting)
                    # "Practice even when no one is watching."
                    if self._dojo and self._idle_ticks % 5 == 0: # Every 5 ticks (~500ms)
                        self._dojo.meditate_tick()
                         
                except Exception as e:
                    logger.warning(f"ReactorLoop: Meditation stumbled: {e}")

    def _process_request(self, request: LoopRequest):
        """
        Process a single request. 
        Guarded by Arjuna Pattern to ensure Mailbox delivery.
        """
        try:
            if not self._reactor:
                self._init_reactor()
                if not self._reactor:
                     raise RuntimeError("Reactor unavailable")

            # 1. Inject Payload
            # Note: ShadowReactor interface might need set_maha_cell exposed or we use internal
            self._reactor.set_maha_cell(request.maha_cell)
            
            # 2. Teleportation (Routing)
            # If target position is specified, we force the reactor to jump there.
            if request.target_position >= 0:
                self._reactor._position = request.target_position
            
            # 3. Prepare Tick State
            # We assume position from the cell or just tick from current?
            # For Phase 1 compatibility, we mapped intent directly to position.
            # But ShadowReactor is stateful. It has its OWN position.
            # wait... sticky point:
            # Ephemeral reactor was creating NEW reactor at specific pos.
            # Persistent reactor is at `self._reactor.position`.
            # If we want to support "Random Access" (routing), we might need to 
            # FORCE the reactor to jump or just accept that it WALKS.
            #
            # FOR NOW (Bridge compatibility): We force the reactor's position 
            # to the target if it's a direct routing request.
            # This preserves the "Soul" (cycle count, history) but allows "Teleportation" (Routing).
            
            # Let's trust the Bridge's routing for the target.
            # But wait, ShadowReactor.tick OVERWRITES `state['position']` with `self._position`.
            # See shadow.py:506: `position=self._position,`
            
            # I will add `target_position` to LoopRequest.
            
            # 4. Tick
            tick_state = {
                "tick": request.target_position if request.target_position >= 0 else self._reactor.position, 
                "position": request.target_position if request.target_position >= 0 else self._reactor.position,
                "quarter": "unknown",
                "guardian": "unknown", 
                "word": "unknown",
                "opcode": None,
            }
            
            # EXECUTE
            final_state = self._reactor.tick(tick_state)
            
            # 4. Success Result
            result = {
                "success": True,
                "execution_result": final_state.get("execution_result"),
                "error": final_state.get("dissonance_report"),
                "state_snapshot": {
                    "position": final_state["position"],
                    "cycle_count": final_state["cycle_count"],
                    "phase": final_state["phase"]
                }
            }
            self._mailbox.deposit(request.tracking_id, result)

        except Exception as e:
            logger.error(f"ReactorLoop: Error processing {request.tracking_id}: {e}", exc_info=True)
            # ARJUNA FIX: Deposit failure so Bridge doesn't hang
            failure_result = {
                "success": False,
                "error": str(e),
                "execution_result": None
            }
            if self._mailbox:
                self._mailbox.deposit(request.tracking_id, failure_result)


# SINGLETON
_global_loop: Optional[ReactorLoop] = None
_global_mailbox: Optional[MahaMailbox] = None
_init_lock = threading.Lock()

def get_loop() -> Tuple[ReactorLoop, MahaMailbox]:
    """Get or create the global reactor loop."""
    global _global_loop, _global_mailbox
    with _init_lock:
        if not _global_loop:
            _global_mailbox = MahaMailbox()
            _global_loop = ReactorLoop()
            _global_loop.attach_mailbox(_global_mailbox)
            _global_loop.start()
    return _global_loop, _global_mailbox
