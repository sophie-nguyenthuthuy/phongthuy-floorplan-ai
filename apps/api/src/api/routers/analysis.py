from typing import Literal

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ontology import load_ontology
from ontology.query import bat_trach_for_cung, cung_menh_from_birth

router = APIRouter(prefix="/analyses", tags=["analyses"])

_ONTOLOGY = load_ontology()


class CungMenhInput(BaseModel):
    nam_sinh: int = Field(..., ge=1900, le=2100, description="Năm sinh dương lịch")
    gioi_tinh: Literal["nam", "nu"]


class HuongRelation(BaseModel):
    huong: str
    quan_he: str
    diem: int


class CungMenhResponse(BaseModel):
    cung_menh: str
    label_vi: str
    nhom: str
    huong_tot: list[HuongRelation]
    huong_xau: list[HuongRelation]


@router.post("/cung-menh", response_model=CungMenhResponse)
def analyze_cung_menh(payload: CungMenhInput) -> CungMenhResponse:
    try:
        cung_key = cung_menh_from_birth(payload.nam_sinh, payload.gioi_tinh)
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(exc),
        ) from exc

    cung = _ONTOLOGY.cung_menh.get(cung_key)
    if cung is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unknown cung mệnh key: {cung_key}",
        )

    relations = bat_trach_for_cung(cung_key, _ONTOLOGY)
    huong_tot = [
        HuongRelation(huong=r.huong, quan_he=r.quan_he, diem=r.diem)
        for r in relations
        if r.diem > 0
    ]
    huong_xau = [
        HuongRelation(huong=r.huong, quan_he=r.quan_he, diem=r.diem)
        for r in relations
        if r.diem < 0
    ]

    return CungMenhResponse(
        cung_menh=cung.key,
        label_vi=cung.label_vi,
        nhom=cung.nhom,
        huong_tot=sorted(huong_tot, key=lambda r: -r.diem),
        huong_xau=sorted(huong_xau, key=lambda r: r.diem),
    )
