"""
Analyze the meaning token coverage of the Gita lexicon.
What English concepts does it cover? Where are the gaps?
Can we bridge the gaps with synonym expansion?
"""

from vibe_core.mahamantra.substrate.semantic_index import get_index

idx = get_index()
idx._ensure_loaded()

tokens = sorted(idx._by_meaning_word.keys())
print(f"Total unique English meaning tokens: {len(tokens)}")
print()

# Group by semantic category
categories = {
    "negative": ["destroy", "death", "kill", "fear", "anger", "sin", "evil",
                 "fall", "fail", "failure", "loss", "suffering", "pain", "grief",
                 "illusion", "ignorance", "bondage", "enemy", "fault", "wrong",
                 "bewildered", "confusion", "distress", "misery", "lamentation"],
    "positive": ["success", "victory", "peace", "happiness", "joy", "bliss",
                 "knowledge", "wisdom", "liberation", "freedom", "pure", "divine",
                 "transcendental", "supreme", "perfect", "good", "auspicious",
                 "devotion", "love", "mercy", "grace", "harmony"],
    "action": ["create", "destroy", "fight", "act", "work", "perform", "give",
               "take", "see", "hear", "speak", "think", "know", "understand",
               "control", "surrender", "worship", "meditate", "serve"],
    "state": ["stable", "fixed", "steady", "eternal", "temporary", "changing",
              "living", "dead", "born", "unborn", "manifest", "unmanifest",
              "conscious", "unconscious", "awake", "sleeping"],
    "tech_missing": ["error", "warning", "database", "system", "healthy",
                     "slow", "fast", "crash", "bug", "fix", "deploy", "test",
                     "build", "run", "start", "stop", "connect", "disconnect",
                     "timeout", "retry", "queue", "process", "thread", "memory"],
}

for cat, words in categories.items():
    found = []
    missing = []
    for w in words:
        matches = idx._by_meaning_word.get(w, [])
        if matches:
            found.append(f"{w}({len(matches)})")
        else:
            missing.append(w)
    total = len(words)
    pct = len(found) / total * 100 if total else 0
    print(f"\n{cat.upper()} ({len(found)}/{total} = {pct:.0f}%):")
    print(f"  Found:   {', '.join(found)}")
    print(f"  Missing: {', '.join(missing)}")

# Now: what are the MOST COMMON meaning tokens?
print("\n" + "=" * 80)
print("TOP 50 MEANING TOKENS (by number of Sanskrit words)")
print("=" * 80)
by_count = sorted(idx._by_meaning_word.items(), key=lambda x: -len(x[1]))
for tok, words in by_count[:50]:
    print(f"  {tok:<25} {len(words):>4} words")

print(f"\n\nTotal tokens: {len(tokens)}")
print(f"Tokens with 1 word: {sum(1 for t,w in idx._by_meaning_word.items() if len(w)==1)}")
print(f"Tokens with 2+ words: {sum(1 for t,w in idx._by_meaning_word.items() if len(w)>=2)}")
print(f"Tokens with 5+ words: {sum(1 for t,w in idx._by_meaning_word.items() if len(w)>=5)}")
print(f"Tokens with 10+ words: {sum(1 for t,w in idx._by_meaning_word.items() if len(w)>=10)}")
