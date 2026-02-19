"""
MANTRA VM — DIW-Dispatched Execution Engine
=============================================

"nava-vidha bhakti" — Nine forms of devotional service (SB 7.5.23).

9-instruction dispatch loop. Each instruction reads from / writes to
a shared ctx dict.

ARCHITECTURE:
    execute_cycle(lotus, input_data, opcode) -> result dict
    - Builds ctx dict
    - Iterates CYCLE (9 instructions) via DISPATCH table
    - PURE COMPUTATION — no gates (gates fire at execute() boundary)
    - Returns the 27-key result dict
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, Optional, Union

from vibe_core.mahamantra.protocols._navabhakti import (
    CYCLE,
    NavaBhaktiOp,
)

if TYPE_CHECKING:
    from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

logger = logging.getLogger("MAHAMANTRA.VM")


# =============================================================================
# 9 WRAPPER FUNCTIONS — The true NavaBhakti (SB 7.5.23)
# =============================================================================

def _w_sravanam(lotus: "MahamantraLotus", ctx: dict) -> None:
    """1. SRAVANAM — Hearing. Parse input AND encode phonetic coords."""
    text, cell, seed = lotus.sravanam(ctx["input_data"])
    ctx["input_text"] = text
    ctx["cell"] = cell
    ctx["seed"] = seed
    # Phonetic encoding (was split out as fake 'NAMA' step)
    ctx["input_coords"] = lotus.nama(ctx["input_text"])


def _w_kirtanam(lotus: "MahamantraLotus", ctx: dict) -> None:
    """2. KIRTANAM — Chanting. Compression + chamber transformation."""
    ctx["seed"] = lotus.kirtanam(ctx["input_text"], ctx["seed"])


def _w_pada_sevanam(lotus: "MahamantraLotus", ctx: dict) -> None:
    a, v, r = lotus.pada_sevanam(ctx["seed"])
    ctx["attractor"] = a
    ctx["variance"] = v
    ctx["raw_address"] = r


def _w_arcanam(lotus: "MahamantraLotus", ctx: dict) -> None:
    ov = lotus.arcanam(ctx["seed"])
    ctx["parampara_verified"] = ov["parampara_validated"]
    ctx["parampara_channel"] = ov["parampara_channel"]
    ctx["parampara_coherence"] = ov["coherence"]


def _w_smaranam(lotus: "MahamantraLotus", ctx: dict) -> None:
    ctx["resonant_words"] = lotus.smaranam(ctx["input_coords"], ctx["attractor"])


def _w_vandanam(lotus: "MahamantraLotus", ctx: dict) -> None:
    v = lotus.vandanam(ctx["attractor"], ctx["seed"])
    ctx["verse_result"] = v["verse_result"]
    ctx["verse_info"] = v["verse_info"]
    ctx["chapter"] = v["chapter"]
    ctx["chapter_significance"] = v["chapter_significance"]
    ctx["gita_phase"] = v["gita_phase"]
    ctx["is_complete"] = v["is_complete"]


def _w_dasyam(lotus: "MahamantraLotus", ctx: dict) -> None:
    d = lotus.dasyam(ctx["attractor"], ctx.get("opcode"))
    ctx["position"] = d["position"]
    ctx["diw"] = d["diw"]
    ctx["diw_comp"] = d["diw_comp"]
    ctx["quarter"] = d["quarter"]
    ctx["guardian"] = d["guardian"]
    ctx["role"] = d["role"]
    ctx["quarter_head_name"] = d["quarter_head_name"]
    ctx["holy_name"] = d["holy_name"]
    ctx["trinity_function"] = d["trinity_function"]
    ctx["rama_coord"] = d["rama_coord"]
    ctx["phoneme"] = d["phoneme"]
    ctx["phoneme_element"] = d["phoneme_element"]
    ctx["phoneme_varga"] = d["phoneme_varga"]
    ctx["phoneme_sub"] = d["phoneme_sub"]
    ctx["phoneme_harmonic"] = d["phoneme_harmonic"]
    ctx["phoneme_shruti"] = d["phoneme_shruti"]
    ctx["pipeline_opcode"] = d["pipeline_opcode"]
    ctx["pipeline_guna"] = d["pipeline_guna"]


def _w_sakhyam(lotus: "MahamantraLotus", ctx: dict) -> None:
    """8. SAKHYAM — Friendship. Cell creation + chamber transformation."""
    ctx["result_cell"] = lotus.sakhyam(
        ctx["seed"], ctx["raw_address"], ctx["position"], ctx["input_text"],
    )
    # Chamber work (was split out as fake 'KIRTAN' step)
    from vibe_core.mahamantra.substrate.lotus_core import _get_pipeline
    P = _get_pipeline()
    chamber = P.get_chamber()
    rw = ctx["resonant_words"]
    ctx["antaranga_collisions"] = chamber.resonate_words(rw, ctx["attractor"]) if rw else 0
    ctx["kirtan_cycles"] = min(
        P.KSETRAJNA + lotus._akash["total_rounds"] // P.WORDS,
        P.MAX_CYCLES,
    )
    ctx["result_cell"] = chamber.kirtan(ctx["result_cell"], cycles=ctx["kirtan_cycles"])
    if ctx["input_coords"]:
        ctx["result_cell"] = chamber.spell_kirtan(ctx["result_cell"], ctx["input_coords"])


def _w_atma_nivedanam(lotus: "MahamantraLotus", ctx: dict) -> None:
    """9. ATMA_NIVEDANAM — Self-surrender. Reactor + akash update + result."""
    from vibe_core.mahamantra.substrate.lotus_core import _get_pipeline
    from vibe_core.mahamantra.protocols._header import MahaCell, MahaHeader, HEADER_DAILY_CYCLES
    P = _get_pipeline()

    # Yajna/reactor work (was split out as fake 'YAJNA' step)
    reactor = P.get_shadow_reactor_factory().spawn(
        auto_discover=False, initial_position=ctx["position"], forced_lagna=0,
    )
    import vibe_core.mahamantra.substrate.mantra_vm as _this_module
    reactor.chant(_this_module)
    reactor.set_maha_cell(
        MahaCell(
            header=MahaHeader.create(
                source=ctx["seed"], target=ctx["raw_address"],
                operation=ctx["position"], link=0, intent=0,
                ttl=HEADER_DAILY_CYCLES, state=0,
            ),
            payload=ctx["input_text"].encode("utf-8"),
        )
    )
    shadow_state = None
    guardian_result = None
    base_tick = lotus._akash["total_beats"]
    for i in range(P.WORDS):
        tp = (ctx["position"] + i) % P.WORDS
        tw, to = P.MAHAMANTRA_SEQUENCE[tp]
        tick_input = {
            "tick": base_tick + i, "position": tp,
            "quarter": P.quarter_names[tp], "guardian": P.ALL_GUARDIANS[tp],
            "word": tw, "opcode": to.value,
        }
        shadow_state = reactor.tick(tick_input)
        tr = shadow_state.get("execution_result")
        if tr is not None:
            guardian_result = tr
    ctx["shadow_state"] = shadow_state
    ctx["guardian_result"] = guardian_result

    # Akash update
    WORDS = P.WORDS
    lotus._akash["total_beats"] += WORDS
    lotus._akash["total_rounds"] += 1
    lotus._akash["accumulated_value"] = (
        lotus._akash["accumulated_value"] + ctx["attractor"]
    ) % P.MAHA_QUANTUM
    lotus._akash["attractor_counts"][ctx["attractor"]] = (
        lotus._akash["attractor_counts"].get(ctx["attractor"], 0) + 1
    )
    lotus._akash["last_seed"] = ctx["seed"]
    lotus._akash["last_position"] = ctx["position"]
    lotus._akash["last_attractor"] = ctx["attractor"]
    ctx["_result"] = _build_result(ctx, lotus, P)


# =============================================================================
# DISPATCH TABLE — NavaBhaktiOp → Wrapper
# =============================================================================

DISPATCH = {
    NavaBhaktiOp.SRAVANAM: _w_sravanam,
    NavaBhaktiOp.KIRTANAM: _w_kirtanam,
    NavaBhaktiOp.SMARANAM: _w_smaranam,
    NavaBhaktiOp.PADA_SEVANAM: _w_pada_sevanam,
    NavaBhaktiOp.ARCANAM: _w_arcanam,
    NavaBhaktiOp.VANDANAM: _w_vandanam,
    NavaBhaktiOp.DASYAM: _w_dasyam,
    NavaBhaktiOp.SAKHYAM: _w_sakhyam,
    NavaBhaktiOp.ATMA_NIVEDANAM: _w_atma_nivedanam,
}


# =============================================================================
# RESULT BUILDER — 27-key output dict (identical to lotus_core.py:838-939)
# =============================================================================

def _build_result(ctx: dict, lotus: "MahamantraLotus", P: object) -> dict:
    from vibe_core.mahamantra.protocols._header import HEADER_SIZE_BYTES
    from vibe_core.mahamantra.substrate.pancha_tattva import TattvaGate
    chamber = P.get_chamber()
    return {
        "input": ctx["input_text"],
        "tattva_gate": "SRIVASA",
        "guna": {
            "mode": ctx["pipeline_guna"].name,
            "opcode": ctx["pipeline_opcode"].name,
            "opcode_value": ctx["pipeline_opcode"].value,
            "source": "caller" if ctx.get("opcode") is not None else "position",
        },
        "vibration": {
            "seed": ctx["seed"],
            "attractor": ctx["attractor"],
            "rama_index": ctx["rama_coord"],
            "phoneme": ctx["phoneme"],
            "signature": {
                "element": P.ELEMENT_NAMES[ctx["phoneme_element"]],
                "varga": ctx["phoneme_varga"],
                "sub": ctx["phoneme_sub"],
                "harmonic": ctx["phoneme_harmonic"],
                "shruti": ctx["phoneme_shruti"],
                "frequency": ctx["phoneme_harmonic"] * 3 + ctx["phoneme_element"] * 15,
            },
        },
        "parampara": {
            "verified": ctx["parampara_verified"],
            "channel": ctx["parampara_channel"],
            "coherence": ctx["parampara_coherence"],
        },
        "chapter": ctx["chapter"],
        "chapter_significance": ctx["chapter_significance"],
        "verse": ctx["verse_info"],
        "matches": len(ctx["verse_result"].matches),
        "gita_phase": ctx["gita_phase"],
        "is_complete": ctx["is_complete"],
        "position": ctx["position"],
        "guardian": ctx["guardian"],
        "quarter": ctx["quarter"],
        "role": ctx["role"],
        "quarter_head": ctx["quarter_head_name"],
        "holy_name": ctx["holy_name"],
        "trinity_function": ctx["trinity_function"],
        "diw": {
            "raw": ctx["diw"],
            "venu": ctx["diw_comp"].venu,
            "vamsi": ctx["diw_comp"].vamsi,
            "murali": ctx["diw_comp"].murali,
        },
        "cell": {
            "header_size": HEADER_SIZE_BYTES,
            "payload_size": len(ctx["input_text"].encode("utf-8")),
            "total_size": HEADER_SIZE_BYTES + len(ctx["input_text"].encode("utf-8")),
            "valid": True,
            "parampara_verified": ctx["parampara_verified"],
            "prana": ctx["result_cell"].prana,
            "integrity": ctx["result_cell"].membrane_integrity / P.COSMIC_FRAME,
            "is_alive": ctx["result_cell"].is_alive,
            "cycle": ctx["result_cell"].age,
        },
        "nama": {
            "coords": ctx["input_coords"],
            "phoneme_count": len(ctx["input_coords"]),
        },
        "smaranam": tuple(
            {
                "sanskrit": rw.word.sanskrit,
                "meaning": rw.word.first_meaning,
                "score": rw.total_score,
            }
            for rw in ctx["resonant_words"]
        ),
        "antaranga": {
            "active_slots": chamber.antaranga.active_count(),
            "total_prana": chamber.antaranga.total_prana(),
            "collisions": ctx["antaranga_collisions"],
            "size_bytes": chamber.antaranga.size_bytes,
        },
        "akash": lotus._akash,
        "execution": {
            "success": ctx["result_cell"].is_alive,
            "prana": ctx["result_cell"].prana,
            "integrity": ctx["result_cell"].membrane_integrity / P.COSMIC_FRAME,
            "kirtan_cycles": ctx["kirtan_cycles"],
            "transformations": ctx["kirtan_cycles"] * P.WORDS,
            "yajna_ticks": P.WORDS,
            "cycles": ctx["result_cell"].age,
            "guardian_acted": ctx["guardian_result"] is not None,
            "guardian_result": ctx["guardian_result"],
        },
        "yajna": {
            "phase": ctx["shadow_state"].get("phase"),
            "cycle_count": ctx["shadow_state"].get("cycle_count", 0),
            "switch_count": ctx["shadow_state"].get("switch_count", 0),
            "return_count": ctx["shadow_state"].get("return_count", 0),
            "dissonance": ctx["shadow_state"].get("dissonance_report"),
        },
        "gate_trace": (
            TattvaGate.PARSE.name,
            TattvaGate.VALIDATE.name,
            TattvaGate.EXECUTE.name,
            TattvaGate.RESULT.name,
            TattvaGate.SYNC.name,
        ),
    }


# =============================================================================
# ENGINE — The dispatch loop
# =============================================================================

def execute_cycle(
    lotus: "MahamantraLotus",
    input_data: Union[str, object],
    opcode: Optional[int] = None,
) -> Dict[str, object]:
    """
    Execute the 9-step NavaBhakti pipeline via VAMSI dispatch.

    If CycleCompiler has custom ops registered, uses the compiled cycle.
    Otherwise, zero-overhead static CYCLE dispatch (the common case).

    PURE COMPUTATION — no gates. Gates fire at the boundary (execute()).
    """
    # VM registers: persistent state across cycles, stored on lotus instance
    if not hasattr(lotus, "_vm_registers"):
        lotus._vm_registers = {}

    ctx: Dict[str, object] = {
        "input_data": input_data,
        "opcode": opcode,
        "vm_registers": lotus._vm_registers,
    }

    # Fast path: no custom ops → static dispatch (zero overhead)
    from vibe_core.mahamantra.substrate.cycle_compiler import get_compiler
    compiler = get_compiler()
    if compiler.custom_count == 0:
        for op in CYCLE:
            DISPATCH[op](lotus, ctx)
    else:
        # Compiled path: core + custom ops with condition evaluation
        compiled = compiler.compile()
        dispatch = compiler.dispatch
        for cop in compiled:
            if cop.condition is not None and not cop.condition(ctx):
                continue  # Condition bits: skip this op
            dispatch[cop.op_id](lotus, ctx)

    return ctx["_result"]
