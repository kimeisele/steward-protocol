# MAHAPROMPT - DAS GESETZ

**DIES IST GESETZ. SIEHE: `vibe_core/mahamantra/substrate/pancha_tattva.py`**

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

Krishna ist acintya - immer präsent, muss nichts "lesen".

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
from vibe_core.mahamantra.substrate.pancha_tattva import get_tattva_for_position

# Position IST die Zuordnung
tattva = get_tattva_for_position(1)  # Position 1 (Brahma)
# -> PanchaTattva.NITYANANDA
```

---

## PROTOCOL IMPORT

```python
from vibe_core.mahamantra.substrate.pancha_tattva import (
    PanchaTattva,
    TattvaAspect,
    get_tattva_for_position,
    PANCHA_TATTVA_ASPECTS,
)
```

---

## VERBOTEN

- Hardcoded Positionen ohne Tattva-Mapping
- Folders ausserhalb der Lotus-Struktur
- Any types
- Duplicate SSOT (alle Konstanten kommen aus substrate/)

---

**HARE KRISHNA. DER LOTUS SPRIESST. 5 FRAGEN.**
