import os
import sys

sys.path.append(os.getcwd())

import hashlib

from vibe_core.security import SecurityIntentManager


def calculate_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    manager = SecurityIntentManager()

    target_file = "vibe_core/kernel_impl.py"
    new_hash = calculate_hash(target_file)

    intent = manager.propose_intent(
        author="System (Antigravity)",
        description="Update kernel hash for Sudarshana Singularity (Vishnu Clock Attributes)",
        changes={target_file: new_hash},
    )

    print(f"INTENT_ID={intent.id}")
    print(f"INTENT_DESC={intent.description}")
    print(f"NEW_HASH={new_hash}")


if __name__ == "__main__":
    main()
