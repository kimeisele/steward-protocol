"""
PHILOSOPHY SCRIPTS (STUBS)
==========================
Stubs for the philosophical debate circuit.
"""


def generate_argument(side: str, topic: str, context: str = None):
    if side == "pro":
        return {"argument": f"The Thesis on {topic} is that it is fundamental to the universe."}
    else:
        return {"argument": f"The Antithesis counters that {topic} is merely an illusion, given '{context}'."}


def synthesize(thesis: str, antithesis: str):
    return {"conclusion": f"Synthesis: {thesis} AND {antithesis} are both aspects of the One."}
