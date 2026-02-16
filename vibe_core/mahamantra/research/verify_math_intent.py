"""Quick verification: what does decode_samskara_intent produce vs old keywords?"""

from vibe_core.mahamantra.adapters.compression import MahaCompression
from vibe_core.mahamantra.protocols._seed import WORDS, QUARTERS

comp = MahaCompression()

tests = [
    ("ERROR: Database connection failed", "tamas"),
    ("FATAL: Application crashed with segfault", "tamas"),
    ("WARNING: Slow query detected, retry in progress", "rajas"),
    ("TODO: Fix this workaround later", "rajas"),
    ("SUCCESS: All tests passed, deployment complete", "sattva"),
    ("System healthy and stable, all services verified", "sattva"),
    ("Unified system achieved optimal harmonious state", "suddha"),
    ("Error occurred but partial success achieved", "tamas"),
    ("Error: fail", "tamas"),
    ("Warning: slow", "rajas"),
    ("Success: done", "sattva"),
    ("Everything is healthy", "sattva"),
    ("Warning: minor issue", "rajas"),
    ("Error: critical failure", "tamas"),
]

correct = 0
total = len(tests)

for text, expected in tests:
    result = comp.compress(text)
    actual = result.intent_level.guna.value
    seed = result.seed
    pos = seed % WORDS
    q = pos // QUARTERS
    ok = (actual == expected)
    if ok:
        correct += 1
    mark = "OK" if ok else "XX"
    print(f"  {mark}  pos={pos:>2} q={q} got={actual:>7} exp={expected:>6}  | {text[:45]}")

print(f"\nScore: {correct}/{total} = {100*correct/total:.0f}%")
print("\nQuarter mapping: 0-3=TAMAS, 4-7=RAJAS, 8-11=SATTVA, 12-15=SUDDHA")
