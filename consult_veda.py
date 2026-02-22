import sys
from vibe_core.mahamantra.cli.veda_explorer import process, ExplorerMode


def consult():
    print("Consulting Veda Explorer for structural audit guidance...")
    result = process(
        "Give me guidance on the structural audit of the 304 files in Mahamantra. Show me resonance-based hints and Gita verses for architectural engineering.",
        mode=ExplorerMode.CREATIVE,
    )
    print(f"\nResponse from {result.get('data', {}).get('guardian', 'unknown').upper()}:")
    print("-" * 40)
    print(result["response"])
    print("-" * 40)


if __name__ == "__main__":
    consult()
