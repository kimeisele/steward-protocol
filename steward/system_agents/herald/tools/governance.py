"""
Herald Governance Module - Minimal governance class for compatibility.

Governance is handled at the kernel level by Narasimha and Constitutional Oath.
This is a compatibility shim for legacy code.
"""


class HeraldConstitution:
    """Minimal HeraldConstitution class for boot compatibility."""

    def __init__(self):
        """Initialize with minimal governance state."""
        self.rules = []
        self.enforced = True

    @staticmethod
    def get_constitution_text() -> str:
        """Get the constitution as text."""
        return "Governance is enforced at the kernel level by Narasimha protocol."

    def check_governance(self, content: str) -> bool:
        """Always return True - kernel governs, not Herald."""
        return True
