"""Schemas for the layout generator — templates in, generated layouts out."""

from typing import Literal

from ontology.models import Nhom, QuanHe
from pydantic import BaseModel, Field


class Slot(BaseModel):
    """A rectangular placement slot inside a house template (meters)."""

    id: str
    x: float
    y: float
    w: float = Field(..., gt=0)
    h: float = Field(..., gt=0)
    allowed: list[str] = Field(default_factory=list)
    fixed: str | None = None


class HouseTemplate(BaseModel):
    """A parameterized VN house typology the engine can lay out."""

    key: str
    label_vi: str
    description_vi: str
    width_m: float = Field(..., gt=0)
    depth_m: float = Field(..., gt=0)
    rooms: list[str]
    slots: list[Slot]
    extra_advice_vi: list[str] = Field(default_factory=list)


class SectorInfo(BaseModel):
    """One of the 8 Bát Trạch sectors around the house center, for overlays."""

    huong: str
    label_vi: str
    quan_he: QuanHe
    quan_he_label_vi: str
    diem: int
    bearing_deg: float


class PlacedRoom(BaseModel):
    """A room assigned to a slot, with its Bát Trạch verdict."""

    room: str
    label_vi: str
    slot_id: str
    x: float
    y: float
    w: float
    h: float
    huong: str
    huong_label_vi: str
    quan_he: QuanHe
    quan_he_label_vi: str
    diem: int
    score: float = Field(..., ge=0, le=1)
    good: bool
    advice_vi: str


DoorPosition = Literal["trai", "giua", "phai"]


class DoorPlacement(BaseModel):
    """Main door on the front edge — the highest-weight placement in Bát Trạch."""

    x: float
    y: float
    width_m: float
    position: DoorPosition
    huong: str
    huong_label_vi: str
    quan_he: QuanHe
    quan_he_label_vi: str
    diem: int
    score: float = Field(..., ge=0, le=1)


TierKey = Literal["dai_cat", "cat", "binh_hoa", "can_hoa_giai"]


class GeneratedLayout(BaseModel):
    """Full generator output — everything renderers and the API need."""

    template_key: str
    template_label_vi: str
    width_m: float
    depth_m: float

    cung_menh: str
    cung_label_vi: str
    nhom: Nhom
    nhom_label_vi: str
    element: str
    element_label_vi: str

    huong_nha: str
    huong_nha_label_vi: str
    huong_recommended: bool
    house_quan_he: QuanHe
    house_quan_he_label_vi: str
    house_diem: int

    door: DoorPlacement
    rooms: list[PlacedRoom]
    sectors: list[SectorInfo]

    score_total: int = Field(..., ge=0, le=100)
    tier: TierKey
    tier_label_vi: str

    highlights_vi: list[str]
    warnings_vi: list[str]
    extra_advice_vi: list[str]
