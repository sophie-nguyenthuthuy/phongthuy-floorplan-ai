"""Layout generator endpoints — stateless, deterministic, shareable.

The SVG endpoints take the same parameters as the JSON endpoint via query
string, so a share-card URL is permanent without any storage: same inputs,
same Bát Trạch verdict, same pixels.
"""

from datetime import date
from typing import Literal
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import Response
from generator import (
    GeneratedLayout,
    facebook_caption,
    generate_layout,
    linkedin_caption,
    load_templates,
    plan_svg,
    share_card_svg,
)
from ontology import load_ontology
from ontology.query import cung_menh_from_birth
from pydantic import BaseModel, Field

router = APIRouter(prefix="/generator", tags=["generator"])

_ONTOLOGY = load_ontology()

HuongKey = Literal["bac", "dong_bac", "dong", "dong_nam", "nam", "tay_nam", "tay", "tay_bac"]
GioiTinh = Literal["nam", "nu"]


class TemplateSummary(BaseModel):
    key: str
    label_vi: str
    description_vi: str
    width_m: float
    depth_m: float
    rooms_vi: list[str]


@router.get("/templates", response_model=list[TemplateSummary])
def list_templates() -> list[TemplateSummary]:
    return [
        TemplateSummary(
            key=t.key,
            label_vi=t.label_vi,
            description_vi=t.description_vi,
            width_m=t.width_m,
            depth_m=t.depth_m,
            rooms_vi=[_ONTOLOGY.room_rules[r].label_vi for r in t.rooms],
        )
        for t in load_templates().values()
    ]


class GenerateInput(BaseModel):
    """Birth date matters (not just year): the phong thủy year follows Lập Xuân."""

    nam_sinh: int = Field(..., ge=1900, le=2100)
    thang_sinh: int = Field(..., ge=1, le=12)
    ngay_sinh: int = Field(..., ge=1, le=31)
    gioi_tinh: GioiTinh
    template: str
    huong_nha: HuongKey | None = None
    display_name: str | None = Field(None, max_length=40)


class GenerateResponse(BaseModel):
    layout: GeneratedLayout
    caption_facebook: str
    caption_linkedin: str
    plan_svg_url: str
    share_card_svg_url: str


def _layout_for(
    nam_sinh: int,
    thang_sinh: int,
    ngay_sinh: int,
    gioi_tinh: GioiTinh,
    template: str,
    huong_nha: str | None,
) -> GeneratedLayout:
    try:
        birth = date(nam_sinh, thang_sinh, ngay_sinh)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Ngày sinh không hợp lệ: {exc}",
        ) from exc
    cung = cung_menh_from_birth(birth, gioi_tinh)
    try:
        return generate_layout(cung, template, huong_nha, _ONTOLOGY)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc


@router.post("/layouts", response_model=GenerateResponse)
def create_layout(payload: GenerateInput) -> GenerateResponse:
    layout = _layout_for(
        payload.nam_sinh,
        payload.thang_sinh,
        payload.ngay_sinh,
        payload.gioi_tinh,
        payload.template,
        payload.huong_nha,
    )
    params = {
        "nam_sinh": payload.nam_sinh,
        "thang_sinh": payload.thang_sinh,
        "ngay_sinh": payload.ngay_sinh,
        "gioi_tinh": payload.gioi_tinh,
        "template": payload.template,
        # Pin the direction the engine actually used, so shared SVG links stay
        # stable even if the recommendation logic evolves.
        "huong_nha": layout.huong_nha,
    }
    if payload.display_name:
        params["display_name"] = payload.display_name
    qs = urlencode(params)
    url = "/generator"
    return GenerateResponse(
        layout=layout,
        caption_facebook=facebook_caption(layout, url, payload.display_name),
        caption_linkedin=linkedin_caption(layout, url),
        plan_svg_url=f"/generator/plan.svg?{qs}",
        share_card_svg_url=f"/generator/share-card.svg?{qs}",
    )


@router.get("/plan.svg", response_class=Response)
def plan_image(
    nam_sinh: int = Query(..., ge=1900, le=2100),
    thang_sinh: int = Query(..., ge=1, le=12),
    ngay_sinh: int = Query(..., ge=1, le=31),
    gioi_tinh: GioiTinh = Query(...),
    template: str = Query(...),
    huong_nha: HuongKey | None = Query(None),
) -> Response:
    layout = _layout_for(nam_sinh, thang_sinh, ngay_sinh, gioi_tinh, template, huong_nha)
    return Response(content=plan_svg(layout), media_type="image/svg+xml")


@router.get("/share-card.svg", response_class=Response)
def share_card_image(
    nam_sinh: int = Query(..., ge=1900, le=2100),
    thang_sinh: int = Query(..., ge=1, le=12),
    ngay_sinh: int = Query(..., ge=1, le=31),
    gioi_tinh: GioiTinh = Query(...),
    template: str = Query(...),
    huong_nha: HuongKey | None = Query(None),
    display_name: str | None = Query(None, max_length=40),
) -> Response:
    layout = _layout_for(nam_sinh, thang_sinh, ngay_sinh, gioi_tinh, template, huong_nha)
    svg = share_card_svg(layout, url="phongthuy-floorplan.ai", display_name=display_name)
    return Response(content=svg, media_type="image/svg+xml")
