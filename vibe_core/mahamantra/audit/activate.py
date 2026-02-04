"""
ACTIVATE AUDIT LOOP - The Breath of the System
==============================================

Usage:
    from vibe_core.mahamantra.audit.activate import activate_audit_loop
    activate_audit_loop()

This hooks the DriftAuditor into the Mahamantra Heartbeat.
"""

import logging

logger = logging.getLogger("AUDIT_ACTIVATOR")

def activate_audit_loop() -> None:
    """
    Activate the Japa Loop Audit.
    
    This connects the DriftAuditor (Gadadhara) to the MahamantraLotus (Krishna).
    Result: Every 108 ticks, a full system audit is performed automatically.
    """
    try:
        from vibe_core.mahamantra.audit.drift import DriftAuditor
        
        auditor = DriftAuditor()
        auditor.start_listening()
        
        logger.info("✅ Audit Loop Activated: DriftAuditor is listening to Mahamantra.")
        
    except Exception as e:
        logger.error(f"❌ Failed to activate Audit Loop: {e}")
        # We do not raise, as audit failure should not crash the kernel.

if __name__ == "__main__":
    # Can be run directly to test activation (if kernel is running in same process)
    logging.basicConfig(level=logging.INFO)
    activate_audit_loop()
