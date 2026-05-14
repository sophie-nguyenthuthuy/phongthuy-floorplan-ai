from datetime import date
from typing import Literal

from fastapi import APIRouter, HTTPException, status
from ontology import load_ontology
from ontology.models import BatTrachRelation
from ontology.query import bat_trach_for_cung, cung_menh_from_birth
from pydantic import BaseModel, Field

router = APIRouter(prefix="/analyses", tags=["analyses"])

_ONTOLOGY = load_ontology()


class CungMenhInput(BaseModel):
    """Full birth date is required because the phong thủy year follows Lập Xuân
    (~Feb 4), not Jan 1. A January birthday counts as the previous lunar year."""

    nam_sinh: int = Field(..., ge=1900, le=2100)
    thang_sinh: int = Field(..., ge=1, le=12)
    ngay_sinh: int = Field(..., ge=1, le=31)
    gioi_tinh: Literal["nam", "nu"]

    def to_date(self) -> date:
        return date(self.nam_sinh, self.thang_sinh, self.ngay_sinh)


class HuongRelation(BaseModel):
    huong: str
    huong_label_vi: str
    quan_he: str
    diem: int


class CungMenhResponse(BaseModel):
    cung_menh: str
    label_vi: str
    label_en: str
    element: str
    nhom: str
    huong_chinh: str
    huong_tot: list[HuongRelation]
    huong_xau: list[HuongRelation]


@router.post("/cung-menh", response_model=CungMenhResponse)
def analyze_cung_menh(payload: CungMenhInput) -> CungMenhResponse:
    try:
        birth = payload.to_date()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid birth date: {exc}",
        ) from exc

    cung_key = cung_menh_from_birth(birth, payload.gioi_tinh)
    cung = _ONTOLOGY.cung_menh.get(cung_key)
    if cung is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unknown cung mệnh key: {cung_key}",
        )

    relations = bat_trach_for_cung(cung_key, _ONTOLOGY)
    huong_index = _ONTOLOGY.huong

    def to_relation(r: BatTrachRelation) -> HuongRelation:
        return HuongRelation(
            huong=r.huong,
            huong_label_vi=huong_index[r.huong].label_vi,
            quan_he=r.quan_he,
            diem=r.diem,
        )

    huong_tot = sorted(
        (to_relation(r) for r in relations if r.diem > 0),
        key=lambda h: -h.diem,
    )
    huong_xau = sorted(
        (to_relation(r) for r in relations if r.diem < 0),
        key=lambda h: h.diem,
    )

    return CungMenhResponse(
        cung_menh=cung.key,
        label_vi=cung.label_vi,
        label_en=cung.label_en,
        element=cung.element,
        nhom=cung.nhom,
        huong_chinh=cung.huong_chinh,
        huong_tot=huong_tot,
        huong_xau=huong_xau,
    )
