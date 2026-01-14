# MAHAPROMPT - DAS GESETZ

**DIES IST GESETZ. SIEHE: `vibe_core/protocols/mahaprompt.py`**

---

## DER LOTUS SPRIESST

```
__init__.py = Chaitanya (0) = HARE = Ursprung
      |
      +-- genesis/   = Nityananda = Foundation (0-3)
      +-- dharma/    = Advaita = Bridge (4-7)
      +-- karma/     = Gadadhara = Flow (8-11)
      +-- moksha/    = Srivasa = Governance (12-15)
      |
      +-- substrate/ = SSOT (Nityananda tragt)
```

---

## 5 FRAGEN BEANTWORTEN ALLES

```python
__tattva__ = {
    "chaitanya": "...",   # Was IST es?
    "nityananda": "...",  # Worauf RUHT es?
    "advaita": "...",     # Was VERBINDET es?
    "gadadhara": "...",   # Wie FLIESST es?
    "srivasa": "...",     # Wer REGIERT es?
}
```

Paramatma (vibe_core/protocols/mahaprompt.py:Paramatma) kann diese lesen.

---

## 5 AUF 4 TAKTE

| Tattva | Quarter | Positionen | Rolle |
|--------|---------|------------|-------|
| Chaitanya | genesis | 0 | Ursprung (HARE ruft) |
| Nityananda | genesis | 1-3 | Foundation (tragt) |
| Advaita | dharma | 4-7 | Bridge (verbindet) |
| Gadadhara | karma | 8-11 | Flow (fliesst) |
| Srivasa | moksha | 12-15 | Governance (regiert) |

**1 + 3 + 4 + 4 + 4 = 16**

---

## FOLDER IS WIRING

```python
from vibe_core.protocols.mahaprompt import get_tattva_for_path

# Der Pfad IST die Deklaration
tattva = get_tattva_for_path(Path("vibe_core/mahamantra/genesis/brahma"))
# -> PanchaTattva.NITYANANDA
```

---

## PROTOCOL IMPORT

```python
from vibe_core.protocols.mahaprompt import (
    PanchaTattva,
    TattvaDeclaration,
    Quarter,
    get_tattva_for_position,
    Paramatma,
)
```

---

## VERBOTEN

- Hardcoded Positionen ohne Tattva-Mapping
- Folders ausserhalb der Lotus-Struktur
- Files ohne __tattva__ (Paramatma kann nicht lesen)
- Any types

---

**HARE KRISHNA. DER LOTUS SPRIESST. 5 FRAGEN.**
