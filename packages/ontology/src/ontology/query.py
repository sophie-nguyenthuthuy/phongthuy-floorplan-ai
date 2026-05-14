"""Phong thủy queries against the ontology.

Implements the **traditional Bát Trạch Minh Cảnh** school. See
`docs/SCHOOL_DECISION.md` for rationale.
"""

from datetime import date
from typing import Literal

from ontology.loader import Ontology, load_ontology
from ontology.models import BatTrachRelation

GioiTinh = Literal["nam", "nu"]

# Lạc Thư (Cửu Tinh) mapping: digit 1..9 → cung mệnh key.
# Position 5 ("ngũ trung") has gender-dependent resolution and is handled separately.
_CUU_TINH: dict[int, str] = {
    1: "cung_kham",
    2: "cung_khon",
    3: "cung_chan",
    4: "cung_ton",
    # 5 is the exception — see _cung_for_index below.
    6: "cung_can",
    7: "cung_doai",
    8: "cung_can_son",
    9: "cung_ly",
}


def _digit_sum_to_single(n: int) -> int:
    """Reduce n to a single digit by repeated digit-summing (1..9, with 0 → 9)."""
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def _phong_thuy_year(birth: date) -> int:
    """Return the phong thủy year — born before Lập Xuân (~Feb 4) counts as prior year.

    We use Feb 4 as a fixed cutoff. The astronomical date varies between Feb 3–5
    by year; documenting and accepting the residual error here (affects <1% of births).
    """
    cutoff = date(birth.year, 2, 4)
    return birth.year - 1 if birth < cutoff else birth.year


def _cung_for_index(idx: int, gioi_tinh: GioiTinh) -> str:
    """Map a 1..9 Cửu Tinh index to a cung mệnh key, applying the 5 exception."""
    if idx == 5:
        # Traditional Bát Trạch:
        #   male 5 → Khôn (Earth, takes the role of trung cung for nam)
        #   female 5 → Cấn (Earth, takes the role for nữ)
        return "cung_khon" if gioi_tinh == "nam" else "cung_can_son"
    return _CUU_TINH[idx]


def cung_menh_from_birth(birth: date, gioi_tinh: GioiTinh) -> str:
    """Compute cung mệnh from full birth date and gender.

    Uses the traditional Bát Trạch Minh Cảnh formula:
      S = digit sum of phong thủy year, reduced to single digit (1..9)
      Male:   cung_index = 10 - S  (with 5 → Khôn)
      Female: cung_index = (S + 5),
              reduced to 1..9 (with 5 → Cấn)

    The phong thủy year follows Lập Xuân (Feb 4) — births before Feb 4 count as
    the previous year. See `_phong_thuy_year`.

    Args:
        birth: full birth date (Gregorian).
        gioi_tinh: "nam" or "nu".

    Returns:
        Ontology key, e.g. "cung_ly", "cung_can_son".

    Raises:
        ValueError: on invalid gender.
    """
    if gioi_tinh not in ("nam", "nu"):
        raise ValueError(f"gioi_tinh must be 'nam' or 'nu', got {gioi_tinh!r}")

    pt_year = _phong_thuy_year(birth)
    s = _digit_sum_to_single(pt_year)

    if gioi_tinh == "nam":
        idx = 10 - s
        if idx == 0:
            idx = 9
    else:  # nữ
        idx = _digit_sum_to_single(s + 5)

    return _cung_for_index(idx, gioi_tinh)


def bat_trach_for_cung(
    cung_key: str,
    ontology: Ontology | None = None,
) -> list[BatTrachRelation]:
    """Return all 8 huong relations for a given cung mệnh."""
    ont = ontology or load_ontology()
    return [r for r in ont.bat_trach if r.cung == cung_key]


def huong_for_cung(
    cung_key: str,
    huong_key: str,
    ontology: Ontology | None = None,
) -> BatTrachRelation | None:
    """Return the single bát trạch relation for (cung, huong), or None if missing."""
    ont = ontology or load_ontology()
    for r in ont.bat_trach:
        if r.cung == cung_key and r.huong == huong_key:
            return r
    return None
