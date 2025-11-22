"""
StewardClient: The Runtime Interface for Autonomous Agents
Allows agents to sign their work and prove their identity.
"""

from pathlib import Path
from steward import crypto


class StewardClient:
    """
    The Runtime Interface for Autonomous Agents.
    Allows an agent to sign its work and prove its identity.
    """

    def __init__(self, identity_file="STEWARD.md"):
        """
        Initialize the Steward client.

        Args:
            identity_file (str): Path to the STEWARD.md identity file
        """
        self.identity_path = Path(identity_file)
        if not self.identity_path.exists():
            print(f"⚠️  [Steward] Identity file {identity_file} not found. Running in anonymous mode.")
            self.authenticated = False
        else:
            self.authenticated = True
            self._load_identity()

    def _load_identity(self):
        """Load and parse identity from STEWARD.md"""
        try:
            content = self.identity_path.read_text()
            # Simple check: does it contain public key reference?
            self.has_key_reference = "public_key" in content.lower() or "publickey" in content.lower()
        except Exception as e:
            self.has_key_reference = False

    def sign_artifact(self, content: str) -> str:
        """
        Cryptographically signs a text artifact (post, log, decision).
        Returns the signature string.

        Args:
            content (str): The content to sign

        Returns:
            str: Base64-encoded signature, or error string if not authenticated
        """
        if not self.authenticated:
            return "UNSIGNED_ANONYMOUS_ARTIFACT"

        try:
            return crypto.sign_content(content)
        except Exception as e:
            return f"SIGNING_ERROR: {str(e)}"

    def assert_identity(self) -> bool:
        """
        Verifies that the runtime has access to the private keys matching the identity.

        Returns:
            bool: True if keys are accessible, False otherwise
        """
        if not self.authenticated:
            return False
        try:
            # Simple check: Can we load and use the key?
            test_sig = crypto.sign_content("identity_check")
            return len(test_sig) > 0
        except Exception:
            return False

    def get_identity_file(self) -> Path:
        """Returns the path to the identity file."""
        return self.identity_path
