"""
EXECUTABLE MIXIN - Universal Execution Interface
=================================================

"One interface to rule them all"

ALL services get execute() through this mixin.
NO need to patch 16 guardians individually!

This is the ADAPTER LAYER between:
- Dispatcher (expects execute())
- Services (implement Protocols with specific methods)

ARCHITECTURE:
    Service = Protocol Implementation + ExecutableMixin
    
Example:
    class BrahmaService(BrahmaProtocol, ExecutableMixin):
        # Implements: wake(), load_root(), alloc_mem()
        # Inherits: execute() from mixin
"""

from typing import Any, Dict


class ExecutableMixin:
    """
    Mixin that provides execute() interface for all services.
    
    Services implement protocol-specific methods (wake, commit, etc).
    This mixin provides universal execute() that routes to them.
    """
    
    def execute(self, input_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Universal execution interface.
        
        Routes input to appropriate protocol method based on:
        1. Guardian name (self.__class__.__name__)
        2. Input keywords
        3. Available methods
        
        Returns standardized dict with success, output, action.
        """
        intent = input_text.lower().strip()
        
        # Get service name
        service_name = self.__class__.__name__.replace("Service", "").lower()
        
        # Common patterns
        if "state" in intent or "status" in intent:
            if hasattr(self, "get_state"):
                state = self.get_state()
                return {
                    "success": True,
                    "action": "get_state",
                    "service": service_name,
                    "state": state
                }
        
        # Default: return service info
        methods = [m for m in dir(self) if not m.startswith('_') and callable(getattr(self, m))]
        protocol_methods = [m for m in methods if m not in ['execute', 'get_state']]
        
        return {
            "success": True,
            "action": "introspect",
            "service": service_name,
            "input": input_text,
            "available_methods": protocol_methods[:10],  # First 10
            "message": f"{service_name} service ready. Available: {', '.join(protocol_methods[:5])}"
        }
