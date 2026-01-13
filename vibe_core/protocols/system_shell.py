"""
System Shell Protocol
=====================
Layer: Substrate (0)
Type: Protocol (Interface)

Defines the contract for shell execution, enabling strictly verified
interactions with the Operating System (e.g. Git, Docker).

"The Shell is the body; the Protocol is the spirit."
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bali"
__position__ = 13
__genesis__ = "0x0070b98b"  # GenesisByte: parampara % 37 == 0

from typing import List, Optional, Protocol, runtime_checkable, Union
from dataclasses import dataclass
from pathlib import Path
import subprocess
import os


@dataclass
class ShellResult:
    """Standardized shell execution result."""
    stdout: str
    stderr: str
    returncode: int

    @property
    def success(self) -> bool:
        return self.returncode == 0


@runtime_checkable
class ShellProtocol(Protocol):
    """
    Protocol for executing system commands.
    
    Replaces `subprocess.run` calls to allow:
    1. Mock-free testing (using Stubs)
    2. Sandboxed execution (System Integrity)
    3. Audit logging of all shell commands
    """

    def run(
        self, 
        command: List[str], 
        cwd: Optional[Union[str, Path]] = None,
        check: bool = False,
        env: Optional[dict] = None
    ) -> ShellResult:
        """
        Execute a shell command.
        
        Args:
            command: List of arguments (e.g. ["git", "status"])
            cwd: Working directory
            check: Raise SystemError if returncode != 0
            env: Environment variables
            
        Returns:
            ShellResult object
        """
        ...


class SystemShell:
    """
    Standard implementation of ShellProtocol using subprocess.
    """
    
    def run(
        self, 
        command: List[str], 
        cwd: Optional[Union[str, Path]] = None,
        check: bool = False,
        env: Optional[dict] = None
    ) -> ShellResult:
        try:
            # Use os.environ if env not provided, or merge?
            # subprocess.run uses os.environ by default if env is None
            
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                env=env,
                check=False # We handle check manually to return ShellResult first
            )
            
            shell_result = ShellResult(
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode
            )
            
            if check and not shell_result.success:
                raise SystemError(f"Command failed: {' '.join(command)}\nStderr: {shell_result.stderr}")
                
            return shell_result
            
        except Exception as e:
            if check:
                raise SystemError(f"Execution failed: {e}")
            return ShellResult(stdout="", stderr=str(e), returncode=-1)
