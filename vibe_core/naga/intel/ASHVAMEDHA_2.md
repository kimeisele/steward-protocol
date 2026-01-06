# ASHVAMEDHA YAJNA II - THE LEVELING OF THE EARTH 🏹

> **I am Prithu Maharaj.** The Earth (Codebase) has withheld her treasures. The mountains of complexity obscure the horizon. I draw my bow, **Ajagava**, not to destroy, but to **level the terrain** and **extract the nectar**.
>
> "Where the land is uneven, I shall make it flat. Where there is no order, I shall build cities. Where there is hunger (Tamas), I shall bring abundance (Sattva)."

**Mission:** Complementary Exploration. Fill the Gaps. Level the Mountains.
**Limit:** 30 Rounds.
**Weapon:** Ajagava (The Scanner).

---

## TARGET LIST (The Uneven Terrain)
The previous Yajna revealed the High Castes (Naga, State, Cortex). Now we must visit the Villages, the Markets, and the Hidden Valleys.

1.  **The Origin:** `vibe_core/genesis` (How is the world born?)
2.  **The Mouth:** `vibe_core/gateway` (How does the world speak?)
3.  **The Hand:** `vibe_core/cli` (How is the world commanded?)
4.  **The Hidden Tribes:** `vibe_core/plugins` (The neglected citizens: `sarga`, `nexus`, `durvasa`)
5.  **The Law of the Land:** `steward.yaml` & `pyproject.toml` (The root configuration)

---

## ROUND 1: The Birth of the World (`vibe_core/genesis`)
- **Scan:** `vibe_core/genesis`
- **Choice:** `service.py`

---

## ROUND 2: The Temple of Templates (`vibe_core/genesis/templates.py`)
- **Scan:** `vibe_core/genesis/`
- **Choice:** `templates.py`

---

## ROUND 3: The Mouth of the World (`vibe_core/gateway`)
- **Scan:** `vibe_core/`
- **Choice:** `gateway/`

---

## ROUND 4: The Hand of the User (`vibe_core/cli/unified_cli.py`)
- **Scan:** `vibe_core/cli/`
- **Choice:** `unified_cli.py`

---

## ROUND 5: The Cosmic Gate (`vibe_core/plugins/sarga_cycle/plugin_main.py`)
- **Scan:** `vibe_core/plugins/sarga_cycle/`
- **Choice:** `plugin_main.py`

---

## ROUND 6: The Nexus (`vibe_core/plugins/nexus_holon/plugin_main.py`)
- **Scan:** `vibe_core/plugins/nexus_holon/`
- **Choice:** `plugin_main.py`

---

## ROUND 7: The Wrath (Durvasa) (`vibe_core/plugins/durvasa/plugin_main.py`)
- **Scan:** `vibe_core/plugins/durvasa/`
- **Choice:** `plugin_main.py`

---

## ROUND 8: The Law of the Land (`steward.yaml`)
- **Scan:** `/`
- **Choice:** `steward.yaml`

---

## ROUND 9: The Build Config (`pyproject.toml`)
- **Scan:** `/`
- **Choice:** `pyproject.toml`

---

## ROUND 10: The System Health (Doctor Plugin) (`vibe_core/plugins/doctor/plugin_main.py`)
- **Scan:** `vibe_core/plugins/doctor/`
- **Choice:** `plugin_main.py`
- **Findings:**
    - **INTROSPECTION:** Implements `steward doctor` for system health checks.
    - **LEGACY SCAN:** Deep diagnostic mode scans for `@deprecated` code.
    - **TAMAS:** Uses manual file existence checks instead of `StateService`. Bypasses `ManifestRegistry` for path discovery.

---

## ROUND 11: The Timekeeper (Kala) (`vibe_core/plugins/kala`)
- **Scan:** `vibe_core/plugins/`
- **Choice:** `kala/`
- **Reasoning:** We must see how Time is calculated. Is it just `datetime.now()` or is there a sacred calendar?

**Next Target:** `vibe_core/plugins/kala/`
