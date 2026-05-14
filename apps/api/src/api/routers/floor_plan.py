import uuid
from pathlib import Path

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
    target: Path = settings.storage_path / f"{floor_plan_id}-{file.filename or 'plan'}"
    target.write_bytes(content)

    return FloorPlanUploadResponse(
        id=floor_plan_id,
        filename=file.filename or "plan",
        size_bytes=len(content),
    )
