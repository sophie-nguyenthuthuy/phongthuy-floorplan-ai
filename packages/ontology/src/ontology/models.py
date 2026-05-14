from typing import Literal

from pydantic import BaseModel, Field

Nhom = Literal["dong_tu_menh", "tay_tu_menh"]
"""Group: East-four-trigrams (Khảm, Ly, Chấn, Tốn) or West-four (Càn, Khôn, Cấn, Đoài)."""

QuanHe = Literal[
    "sinh_khi",     # +4  most auspicious
    "thien_y",      # +3
    "dien_nien",    # +2
    "phuc_vi",      # +1
    "hoa_hai",      # -1
    "luc_sat",      # -2
    "ngu_quy",      # -3
    "tuyet_menh",   # -4  most inauspicious
]

NguHanhKey = Literal["kim", "moc", "thuy", "hoa", "tho"]


class NguHanh(BaseModel):
    """Ngũ hành — five elements with sinh (generates) and khắc (overcomes) relations."""

    key: NguHanhKey
    label_vi: str
    label_en: str
    sinh: NguHanhKey
    khac: NguHanhKey


class Huong(BaseModel):
    """Hướng — one of 8 cardinal/intercardinal directions."""

    key: str
    label_vi: str
    label_en: str
    degrees_from: float = Field(..., ge=0, lt=360)
    degrees_to: float = Field(..., ge=0, le=360)
    trigram: str


class CungMenh(BaseModel):
    """Cung mệnh — personal trigram derived from birth year + gender."""

    key: str
    label_vi: str
    label_en: str
    element: NguHanhKey
    nhom: Nhom
    huong_chinh: str


class BatTrachRelation(BaseModel):
    """One cell of the 8x8 Bát Trạch table: a (cung, huong) → (quan_he, diem)."""

    cung: str
    huong: str
    quan_he: QuanHe
    diem: int = Field(..., ge=-4, le=4)
