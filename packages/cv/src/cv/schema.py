"""Structured floor plan output — the schema downstream consumers depend on."""

from typing import Literal

from pydantic import BaseModel, Field

RoomType = Literal[
    "phong_khach",  # living room
    "phong_ngu",  # bedroom
    "phong_bep",  # kitchen
    "phong_tam",  # bathroom
    "phong_an",  # dining
    "phong_tho",  # ban thờ / altar room — VN-specific
    "san_gieng_troi",  # light well — VN-specific
    "ban_cong",  # balcony
    "hanh_lang",  # hallway
    "cau_thang",  # stairs
    "khong_xac_dinh",  # unknown
]


class Point(BaseModel):
    x: float
    y: float


class Wall(BaseModel):
    start: Point
    end: Point
    thickness: float = 0.1
    load_bearing: bool = False


class Door(BaseModel):
    position: Point
    width: float
    swing_direction: Literal["in", "out", "slide"] = "in"


class Room(BaseModel):
    type: RoomType
    polygon: list[Point]
    area_m2: float = Field(..., ge=0)
    confidence: float = Field(..., ge=0, le=1)


class FloorPlan(BaseModel):
    """Parsed output for a single floor plan image."""

    width_px: int
    height_px: int
    scale_m_per_px: float | None = None
    """Real-world scale if known (from drawing legend or user input)."""

    walls: list[Wall] = Field(default_factory=list)
    doors: list[Door] = Field(default_factory=list)
    rooms: list[Room] = Field(default_factory=list)

    north_angle_deg: float | None = None
    """Compass bearing of the 'up' direction in the image. Required for phong thủy analysis."""
