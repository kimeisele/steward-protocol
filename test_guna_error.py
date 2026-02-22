from vibe_core.mahamantra import mahamantra

try:
    print("Testing mahamantra('hare krishna')...")
    result = mahamantra("hare krishna")
    print("Success!")
    print(f"Result keys: {result.keys()}")
    if "verse" in result:
        print(f"Verse info: {result['verse']}")
except Exception as e:
    print(f"Caught error: {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()
