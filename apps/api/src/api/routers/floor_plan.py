import uuid
from pathlib import Path

from cv.parser import parse_image
from cv.schema import FloorPlan
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from api.settings import settings

router = APIRouter(prefix="/floor-plans", tags=["floor-plans"])


class FloorPlanUploadResponse(BaseModel):
    id: str
    filename: str
    size_bytes: int


@router.post("", response_model=FloorPlanUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload(file: UploadFile = File(...)) -> FloorPlanUploadResponse:
    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Upload exceeds {settings.max_upload_bytes} bytes",
        )

    floor_plan_id = uuid.uuid4().hex
    settings.storage_path.mkdir(parents=True, exist_ok=True)
    target: Path = settings.storage_path / f"{floor_plan_id}-{file.filename or 'plan'}"
    target.write_bytes(content)

    return FloorPlanUploadResponse(
        id=floor_plan_id,
        filename=file.filename or "plan",
        size_bytes=len(content),
    )


class FloorPlanAnalyzeResponse(BaseModel):
    id: str
    floor_plan: FloorPlan
    notes: list[str]


@router.get("/{plan_id}/analyze", response_model=FloorPlanAnalyzeResponse)
def analyze(plan_id: str) -> FloorPlanAnalyzeResponse:
    """Parse an uploaded floor plan and return room layout + walls + doors.

    Until the trained CV model lands, this returns a deterministic VN nhà-ống
    layout (see `cv.parser._demo_layout`) — the rest of the flow
    (mobile app rendering + ontology overlay) works end-to-end without
    needing a real model.
    """
    matches = sorted(settings.storage_path.glob(f"{plan_id}-*"))
    if not matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"floor plan {plan_id} not found",
        )

    floor_plan = parse_image(matches[0])
    notes: list[str] = []
    if floor_plan.scale_m_per_px is None:
        notes.append("Tỉ lệ chưa xác định — không quy ra m² thực tế được.")
    if not any(r.type == "phong_tho" for r in floor_plan.rooms):
        notes.append(
            "Chưa phát hiện phòng thờ — phong thủy nhà VN thường yêu cầu bố trí phòng thờ trên cao."
        )
    altar = next((r for r in floor_plan.rooms if r.type == "phong_tho"), None)
    if altar and altar.confidence < 0.7:
        notes.append("Phòng thờ được nhận diện với độ tin cậy thấp; lương y nên kiểm tra lại.")

    return FloorPlanAnalyzeResponse(id=plan_id, floor_plan=floor_plan, notes=notes)
