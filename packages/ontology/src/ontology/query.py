from typing import Literal

from ontology.loader import Ontology, load_ontology
from ontology.models import BatTrachRelation

GioiTinh = Literal["nam", "nu"]


def cung_menh_from_birth(nam_sinh: int, gioi_tinh: GioiTinh) -> str:
    """Compute cung mệnh key from year of birth + gender.

    Not implemented. The exact formula depends on the phong thủy school
    (Lạc Việt, Bát Trạch Minh Cảnh, etc.). Implement after deciding which
    school is authoritative for this product and validating with an expert.
    """
    raise NotImplementedError(
        "cung_menh_from_birth is not implemented — choose a phong thủy school "
        "(Lạc Việt vs traditional Bát Trạch) and validate the formula with an expert"
    )


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
