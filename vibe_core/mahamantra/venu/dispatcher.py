"""
VENU DISPATCHER - Guardian Execution Router
===========================================

"Krishna arranges, Halbgötter execute."

Clean separation:
- Mahamantra determines WHAT (position → guardian)
- VenuDispatcher executes WHO (guardian → service)

NO spaghetti. NO inline imports. SATTVIC.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION ===
__mahajana__ = "prithu"
__position__ = 4
__genesis__ = "0x9a8f7e6d"

from typing import Dict, Any, Optional
import importlib
import asyncio


class VenuDispatcher:
    """
    Guardian execution dispatcher.
    
    Routes cells to guardian services based on position.
    Handles polymorphic execution (execute() vs process_intent()).
    """
    
    __slots__ = ('_service_cache',)
    
    def __init__(self) -> None:
        """Initialize with empty service cache."""
        self._service_cache: Dict[str, Any] = {}
    
    def dispatch(
        self,
        quarter: str,
        guardian: str,
        input_text: str,
        cell: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Dispatch to guardian service.
        
        Args:
            quarter: Quarter name (genesis/dharma/karma/moksha)
            guardian: Guardian name (e.g. prithu, kapila)
            input_text: User input
            cell: Optional MahaCellUnified
            
        Returns:
            Dict with success, output, execution result
        """
        # Get guardian handler - EXPLICIT error handling
        try:
            service = self._get_service(quarter, guardian)
        except ImportError as e:
            return {
                'success': False,
                'output': f'Guardian {guardian} not implemented: {e}',
                'execution': None,
                'exit_code': 127  # Command not found
            }
        
        # Polymorphic execution
        try:
            if hasattr(service, 'execute'):
                # Worker interface (Prithu, Vyasa, etc.)
                result = service.execute(input_text)
                return {
                    'success': True,
                    'output': str(result),
                    'execution': result,
                    'exit_code': 0
                }
            
            elif hasattr(service, 'process_intent'):
                # Cognitive interface (Kapila-style)
                if asyncio.iscoroutinefunction(service.process_intent):
                    result = self._run_async(service.process_intent(input_text, None))
                else:
                    result = service.process_intent(input_text, None)
                
                return {
                    'success': True,
                    'output': str(result),
                    'execution': result,
                    'exit_code': 0
                }
            
            else:
                # Service exists but no execution method
                return {
                    'success': False,
                    'output': f'{guardian.capitalize()}Service has no execute() or process_intent()',
                    'execution': None,
                    'exit_code': 1
                }
        
        except Exception as e:
            return {
                'success': False,
                'output': f'Execution failed: {e}',
                'execution': None,
                'exit_code': 1
            }
    
    def _get_service(self, quarter: str, guardian: str) -> Optional[Any]:
        """
        Get guardian handler - EXPLICIT, NO SILENT FAILURES.
        
        Returns: Guardian module OR raises ImportError
        Caller MUST handle missing guardians explicitly!
        """
        cache_key = f"{quarter}.{guardian}"
        
        # Check cache
        if cache_key in self._service_cache:
            return self._service_cache[cache_key]
        
        # Import guardian module - let ImportError propagate!
        module_path = f"vibe_core.mahamantra.{quarter}.{guardian}"
        guardian_module = importlib.import_module(module_path)
        
        # Cache and return
        self._service_cache[cache_key] = guardian_module
        return guardian_module
    
    @staticmethod
    def _run_async(coro):
        """Run async coroutine in sync context."""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(coro)
        except RuntimeError:
            # Event loop already running
            return asyncio.run(coro)


# Singleton instance
_dispatcher: Optional[VenuDispatcher] = None

def get_dispatcher() -> VenuDispatcher:
    """Get singleton dispatcher instance."""
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = VenuDispatcher()
    return _dispatcher
