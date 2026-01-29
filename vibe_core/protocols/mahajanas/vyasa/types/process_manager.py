"""
PROCESS MANAGER - The "Airbag" System
=====================================

Goal: Isolate agents in separate processes so one crash doesn't kill the kernel.

Architecture:
- AgentProcess: A wrapper around multiprocessing.Process
- ProcessManager: The kernel's interface to manage these processes
- IPC: Pipes/Queues for communication between Kernel and Agents

Philosophy:
"The Kernel is the Temple. Agents are the visitors.
If a visitor collapses, the Temple stands."
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x70acde90"  # GenesisByte: parampara % 37 == 0

import logging
import multiprocessing
import time
import traceback
from dataclasses import dataclass
from enum import Enum
from multiprocessing import Pipe, Process
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("PROCESS_MANAGER")


def _get_runtime_config():
    """Get runtime config with fallback for standalone usage."""
    try:
        from vibe_core.phoenix.config import get_config

        return get_config().runtime
    except Exception:
        # Fallback for standalone/testing
        from vibe_core.phoenix.sections.runtime.section_main import RuntimeConfig

        return RuntimeConfig()


class ProcessStatus(Enum):
    INIT = "init"
    RUNNING = "running"
    STOPPED = "stopped"
    CRASHED = "crashed"
    QUARANTINED = "quarantined"


# SECURITY: Max message size to prevent pipe deadlock (from config)
# LAZY: Don't call get_config() at import time (Siksastakam Effect #1: no stale/eager load)
_MAX_MESSAGE_SIZE: int | None = None


def get_max_message_size() -> int:
    """Get max message size from config (lazy loaded)."""
    global _MAX_MESSAGE_SIZE
    if _MAX_MESSAGE_SIZE is None:
        runtime_config = _get_runtime_config()
        _MAX_MESSAGE_SIZE = runtime_config.limits.max_message_size
    return _MAX_MESSAGE_SIZE


# DEPRECATED: Use get_max_message_size() instead - kept for backwards compat
MAX_MESSAGE_SIZE = 1024 * 1024  # 1MB default, actual value loaded lazily


@dataclass
class AgentProcessInfo:
    process: Process
    parent_pipe: Any  # Connection object
    agent_id: str
    status: ProcessStatus
    cartridge_path: str  # LATE BINDING: Path to cartridge_main.py (for restart)
    cartridge_class_name: str  # LATE BINDING: Class name (for restart)
    config: Any = None  # STORED for restart
    restarts: int = 0
    last_heartbeat: float = 0.0


class AgentProcess:
    """
    Sandboxed Agent Process.

    This runs in a SEPARATE process from the kernel.
    It instantiates the agent and runs its event loop.

    LATE BINDING: Receives cartridge_path and class_name instead of agent_class.
    This avoids pickle errors with dynamically loaded modules.
    """

    def __init__(
        self,
        agent_id: str,
        cartridge_path: str,
        cartridge_class_name: str,
        child_pipe: Any,
        config: Any = None,
    ):
        self.agent_id = agent_id
        self.cartridge_path = cartridge_path
        self.cartridge_class_name = cartridge_class_name
        self.pipe = child_pipe
        self.config = config

    def run(self):
        """
        The entry point for the child process.
        """
        import importlib.util
        import sys
        from pathlib import Path

        # Re-configure logging for child process
        logging.basicConfig(
            level=logging.INFO,
            format=f"%(asctime)s [{self.agent_id.upper()}] %(message)s",
        )
        child_logger = logging.getLogger(f"AGENT_{self.agent_id.upper()}")

        try:
            child_logger.info(f"🚀 Process started for {self.agent_id}")

            # LATE BINDING: Load the cartridge module in the child process
            # This is the key fix - we don't pickle the class, we pickle the path
            cartridge_path = Path(self.cartridge_path)
            if not cartridge_path.exists():
                raise FileNotFoundError(f"Cartridge not found: {self.cartridge_path}")

            module_name = f"cartridge_{self.agent_id}"
            spec = importlib.util.spec_from_file_location(module_name, cartridge_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot create module spec for {cartridge_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module  # Register for subsequent imports
            spec.loader.exec_module(module)

            # Get the cartridge class
            agent_class = getattr(module, self.cartridge_class_name, None)
            if agent_class is None:
                raise AttributeError(f"Class {self.cartridge_class_name} not found in {cartridge_path}")

            child_logger.info(f"📦 Loaded cartridge: {self.cartridge_class_name}")

            # Instantiate Agent
            try:
                agent = agent_class(config=self.config)
            except TypeError:
                # Cartridge doesn't accept config parameter
                agent = agent_class()

            # Inject Pipe (this replaces direct kernel reference)
            agent.set_kernel_pipe(self.pipe)

            child_logger.info("✅ Agent instantiated. Entering event loop.")

            # Event Loop
            while True:
                # 1. Check for messages from Kernel
                if self.pipe.poll(0.1):  # Non-blocking check
                    msg = self.pipe.recv()

                    if msg.get("type") == "STOP":
                        child_logger.info("🛑 Received STOP command")
                        break

                    elif msg.get("type") == "TASK":
                        # SECURITY FIX: Send ACK immediately (no more fire-and-forget)
                        task = msg.get("payload")
                        self.pipe.send({"type": "TASK_ACK", "task_id": getattr(task, "task_id", None)})

                        # Execute Task
                        child_logger.info(f"⚡ Processing task {task.task_id}")
                        try:
                            import asyncio

                            # Handle both async and sync process() methods
                            if asyncio.iscoroutinefunction(agent.process):
                                result = asyncio.run(agent.process(task))
                            else:
                                result = agent.process(task)
                            self.pipe.send(
                                {
                                    "type": "TASK_RESULT",
                                    "task_id": task.task_id,
                                    "result": result,
                                    "status": "success",
                                }
                            )
                        except Exception as e:
                            child_logger.error(f"❌ Task failed: {e}")
                            self.pipe.send(
                                {
                                    "type": "TASK_RESULT",
                                    "task_id": task.task_id,
                                    "error": str(e),
                                    "status": "failed",
                                }
                            )

                    elif msg.get("type") == "PING":
                        self.pipe.send({"type": "PONG", "status": agent.report_status()})

                # 2. Agent autonomous loop (if any)
                # agent.tick()

        except Exception as e:
            child_logger.critical(f"💥 CRITICAL CRASH: {e}")
            child_logger.critical(traceback.format_exc())
            # Send crash report before dying
            try:
                self.pipe.send(
                    {
                        "type": "CRASH",
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                )
            except Exception:
                pass
            raise  # Die and let OS clean up


def _run_agent_process(agent_id, cartridge_path, cartridge_class_name, pipe, config):
    """
    Static wrapper for multiprocessing target.

    LATE BINDING: Receives path/classname instead of class object.
    The AgentProcess will load the module itself in the child process.
    """
    proc = AgentProcess(agent_id, cartridge_path, cartridge_class_name, pipe, config)
    proc.run()


class ProcessManager:
    """
    Kernel Component: Manages the lifecycle of agent processes.

    Responsibilities:
    - Spawn agent processes
    - Route messages (Kernel <-> Agent)
    - Monitor health (Narasimha)
    - Restart crashed agents
    """

    def __init__(self):
        self.processes: Dict[str, AgentProcessInfo] = {}
        # Get max restarts from config
        runtime_config = _get_runtime_config()
        self.MAX_RESTARTS = runtime_config.limits.max_agent_restarts
        multiprocessing.set_start_method("spawn", force=True)  # Safer for macOS/Linux

    def spawn_agent(
        self,
        agent_id: str,
        cartridge_path: str,
        cartridge_class_name: str,
        config: Any = None,
    ):
        """
        Spawn a new agent process.

        LATE BINDING: Receives cartridge_path and class_name instead of agent_class.
        The child process loads the module itself - no pickle required for classes.
        """
        logger.info(f"🌱 Spawning process for {agent_id}...")

        parent_conn, child_conn = Pipe()

        process = Process(
            target=_run_agent_process,
            args=(agent_id, cartridge_path, cartridge_class_name, child_conn, config),
            name=f"vibe-agent-{agent_id}",
            daemon=True,  # Die if kernel dies
        )

        process.start()

        self.processes[agent_id] = AgentProcessInfo(
            process=process,
            parent_pipe=parent_conn,
            agent_id=agent_id,
            status=ProcessStatus.RUNNING,
            cartridge_path=cartridge_path,  # LATE BINDING: Stored for restart
            cartridge_class_name=cartridge_class_name,  # LATE BINDING: Stored for restart
            config=config,  # STORED for restart
            last_heartbeat=time.time(),
        )

        logger.info(f"✅ Spawned {agent_id} (PID: {process.pid})")

    def send_task(self, agent_id: str, task: Any) -> bool:
        """
        Send a task to an agent.

        Returns:
            True if task was sent and ACK received, False otherwise.

        SECURITY FIX: Message size limits prevent pipe deadlock.
        """
        import pickle

        if agent_id not in self.processes:
            raise ValueError(f"Agent {agent_id} not running")

        info = self.processes[agent_id]
        if info.status != ProcessStatus.RUNNING:
            raise ValueError(f"Agent {agent_id} is {info.status.value}")

        # SECURITY: Check message size to prevent pipe deadlock
        msg = {"type": "TASK", "payload": task}
        try:
            msg_size = len(pickle.dumps(msg))
            if msg_size > MAX_MESSAGE_SIZE:
                logger.error(f"⛔ Message too large ({msg_size} bytes > {MAX_MESSAGE_SIZE}). Rejected.")
                return False
        except Exception as e:
            logger.error(f"⛔ Cannot serialize message: {e}")
            return False

        info.parent_pipe.send(msg)

        # SECURITY FIX: Wait for ACK (no more fire-and-forget)
        try:
            if info.parent_pipe.poll(timeout=5.0):  # 5 second timeout
                ack = info.parent_pipe.recv()
                if ack.get("type") == "TASK_ACK":
                    return True
            logger.warning(f"⚠️ No ACK from {agent_id} within timeout")
            return False
        except Exception as e:
            logger.error(f"⛔ ACK failed from {agent_id}: {e}")
            return False

    def check_health(self):
        """
        NARASIMHA: The Watchdog.
        Checks if processes are alive. Restarts them if they crashed.
        """
        for agent_id, info in list(self.processes.items()):
            # Check if process is alive
            if not info.process.is_alive():
                exit_code = info.process.exitcode
                logger.warning(f"⚠️  Agent {agent_id} died (Exit Code: {exit_code})")

                info.status = ProcessStatus.CRASHED
                self._handle_crash(agent_id)

    def get_pending_messages(self) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Get all pending messages from all agents.
        Returns list of (agent_id, message) tuples.
        """
        messages = []
        for agent_id, info in self.processes.items():
            if info.status == ProcessStatus.RUNNING:
                while info.parent_pipe.poll():
                    try:
                        msg = info.parent_pipe.recv()
                        messages.append((agent_id, msg))
                    except EOFError:
                        break
        return messages

    def _handle_crash(self, agent_id: str):
        """
        Restart a crashed agent.

        SECURITY FIX: Actually restarts the agent (not just a stub).
        LATE BINDING: Uses stored cartridge_path and class_name from AgentProcessInfo.
        """
        info = self.processes[agent_id]

        if info.restarts >= self.MAX_RESTARTS:
            logger.critical(f"⛔ {agent_id} exceeded max restarts ({self.MAX_RESTARTS}). QUARANTINED.")
            info.status = ProcessStatus.QUARANTINED
            return

        logger.info(f"♻️  Restarting {agent_id} (Attempt {info.restarts + 1}/{self.MAX_RESTARTS})...")

        # Clean up old process
        try:
            if info.process.is_alive():
                info.process.terminate()
                info.process.join(timeout=2)
            info.parent_pipe.close()
        except Exception as e:
            logger.warning(f"Cleanup error for {agent_id}: {e}")

        # REAL RESTART: Create new pipe and process (LATE BINDING)
        parent_conn, child_conn = Pipe()

        new_process = Process(
            target=_run_agent_process,
            args=(agent_id, info.cartridge_path, info.cartridge_class_name, child_conn, info.config),
            name=f"vibe-agent-{agent_id}",
            daemon=True,
        )
        new_process.start()

        # Update info
        info.process = new_process
        info.parent_pipe = parent_conn
        info.status = ProcessStatus.RUNNING
        info.restarts += 1
        info.last_heartbeat = time.time()

        logger.info(f"✅ Restarted {agent_id} (PID: {new_process.pid}, restarts: {info.restarts})")

    def shutdown(self):
        """Kill all agents."""
        logger.info("🛑 Shutting down all agent processes...")
        for agent_id, info in self.processes.items():
            if info.process.is_alive():
                info.parent_pipe.send({"type": "STOP"})
                info.process.join(timeout=2)
                if info.process.is_alive():
                    info.process.terminate()
        logger.info("✅ All agents stopped.")
