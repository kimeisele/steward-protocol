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

import multiprocessing
import logging
import time
import traceback
from multiprocessing import Process, Pipe, Queue
from typing import Dict, Any, Optional, Type, List, Tuple
from dataclasses import dataclass
from enum import Enum

from vibe_core.protocols import VibeAgent

logger = logging.getLogger("PROCESS_MANAGER")

class ProcessStatus(Enum):
    INIT = "init"
    RUNNING = "running"
    STOPPED = "stopped"
    CRASHED = "crashed"
    QUARANTINED = "quarantined"

@dataclass
class AgentProcessInfo:
    process: Process
    parent_pipe: Any  # Connection object
    agent_id: str
    status: ProcessStatus
    restarts: int = 0
    last_heartbeat: float = 0.0

class AgentProcess:
    """
    Sandboxed Agent Process.
    
    This runs in a SEPARATE process from the kernel.
    It instantiates the agent and runs its event loop.
    """
    
    def __init__(self, agent_id: str, agent_class: Type[VibeAgent], child_pipe: Any, config: Any = None):
        self.agent_id = agent_id
        self.agent_class = agent_class
        self.pipe = child_pipe
        self.config = config
        
    def run(self):
        """
        The entry point for the child process.
        """
        # Re-configure logging for child process
        logging.basicConfig(level=logging.INFO, format=f'%(asctime)s [{self.agent_id.upper()}] %(message)s')
        child_logger = logging.getLogger(f"AGENT_{self.agent_id.upper()}")
        
        try:
            child_logger.info(f"🚀 Process started for {self.agent_id}")
            
            # Instantiate Agent
            agent = self.agent_class(config=self.config)
            
            # Inject Pipe (this replaces direct kernel reference)
            agent.set_kernel_pipe(self.pipe)
            
            child_logger.info(f"✅ Agent instantiated. Entering event loop.")
            
            # Event Loop
            while True:
                # 1. Check for messages from Kernel
                if self.pipe.poll(0.1):  # Non-blocking check
                    msg = self.pipe.recv()
                    
                    if msg.get("type") == "STOP":
                        child_logger.info("🛑 Received STOP command")
                        break
                        
                    elif msg.get("type") == "TASK":
                        # Execute Task
                        task = msg.get("payload")
                        child_logger.info(f"⚡ Processing task {task.task_id}")
                        try:
                            result = agent.process(task)
                            self.pipe.send({
                                "type": "TASK_RESULT",
                                "task_id": task.task_id,
                                "result": result,
                                "status": "success"
                            })
                        except Exception as e:
                            child_logger.error(f"❌ Task failed: {e}")
                            self.pipe.send({
                                "type": "TASK_RESULT",
                                "task_id": task.task_id,
                                "error": str(e),
                                "status": "failed"
                            })
                            
                    elif msg.get("type") == "PING":
                        self.pipe.send({"type": "PONG", "status": agent.report_status()})
                
                # 2. Agent autonomous loop (if any)
                # agent.tick() 
                
        except Exception as e:
            child_logger.critical(f"💥 CRITICAL CRASH: {e}")
            child_logger.critical(traceback.format_exc())
            # Send crash report before dying
            try:
                self.pipe.send({
                    "type": "CRASH",
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })
            except:
                pass
            raise  # Die and let OS clean up

def _run_agent_process(agent_id, agent_class, pipe, config):
    """Static wrapper for multiprocessing target"""
    proc = AgentProcess(agent_id, agent_class, pipe, config)
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
    
    MAX_RESTARTS = 3
    
    def __init__(self):
        self.processes: Dict[str, AgentProcessInfo] = {}
        multiprocessing.set_start_method('spawn', force=True) # Safer for macOS/Linux
        
    def spawn_agent(self, agent_id: str, agent_class: Type[VibeAgent], config: Any = None):
        """Spawn a new agent process."""
        logger.info(f"🌱 Spawning process for {agent_id}...")
        
        parent_conn, child_conn = Pipe()
        
        process = Process(
            target=_run_agent_process,
            args=(agent_id, agent_class, child_conn, config),
            name=f"vibe-agent-{agent_id}",
            daemon=True # Die if kernel dies
        )
        
        process.start()
        
        self.processes[agent_id] = AgentProcessInfo(
            process=process,
            parent_pipe=parent_conn,
            agent_id=agent_id,
            status=ProcessStatus.RUNNING,
            last_heartbeat=time.time()
        )
        
        logger.info(f"✅ Spawned {agent_id} (PID: {process.pid})")
        
    def send_task(self, agent_id: str, task: Any):
        """Send a task to an agent."""
        if agent_id not in self.processes:
            raise ValueError(f"Agent {agent_id} not running")
            
        info = self.processes[agent_id]
        if info.status != ProcessStatus.RUNNING:
             raise ValueError(f"Agent {agent_id} is {info.status.value}")
             
        info.parent_pipe.send({
            "type": "TASK",
            "payload": task
        })
        
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
        """Restart logic."""
        info = self.processes[agent_id]
        
        if info.restarts >= self.MAX_RESTARTS:
            logger.critical(f"⛔ {agent_id} exceeded max restarts ({self.MAX_RESTARTS}). QUARANTINED.")
            info.status = ProcessStatus.QUARANTINED
            return
            
        logger.info(f"♻️  Restarting {agent_id} (Attempt {info.restarts + 1}/{self.MAX_RESTARTS})...")
        
        # We need the class and config to restart. 
        # In a real implementation, we'd store these in a registry or the info object.
        # For now, we assume the caller handles re-spawning or we store the class in info.
        # (Updating AgentProcessInfo to store class/config would be better)
        
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
