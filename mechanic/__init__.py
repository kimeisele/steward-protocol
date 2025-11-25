"""The Mechanic - SDLC Manager and Self-Preservation Agent.

THE MECHANIC handles the Software Development Lifecycle and system integrity.
It is the ONLY agent that runs BEFORE the kernel boots.
It ensures that the system heals itself from broken states.

GAD-000 Principle: The system IS the operator. No manual intervention required.
"""

from mechanic.cartridge_main import MechanicCartridge

__all__ = ["MechanicCartridge"]
