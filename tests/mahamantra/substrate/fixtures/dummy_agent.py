"""
DUMMY AGENT CARTRIDGE
=====================

Used for testing ProcessManager.
Contains a simple agent that responds to IPC and can commit suicide.
"""
import time
import sys

class DummyAgent:
    def __init__(self, config=None):
        self.config = config
        self.kernel_pipe = None
        
    def set_kernel_pipe(self, pipe):
        self.kernel_pipe = pipe
        
    def report_status(self):
        return {"status": "alive", "config_echo": self.config}
        
    def process(self, task):
        # Simulate processing
        command = task.get("command")
        
        if command == "suicide":
            # Simulate a crash
            sys.exit(1)
            
        return f"Processed: {command}"
