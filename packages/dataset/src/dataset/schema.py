from typing import Literal

from cv.schema import FloorPlan
from pydantic import BaseModel, Field

Split = Literal["train", "val", "test"]
"""Stratified split. Stratification keys: typology, source, n_rooms."""

Typology = Literal[
    "nha_ong",  # tube house — narrow + deep
    "nha_pho",  # townhouse — multi-story, mixed-use ground floor
    "biet_thu",  # villa
    "chung_cu",  # apartment in a high-rise
    "nha_cap_4",  # single-story house
    "khac",
]


class Annotation(BaseModel):
    """Expert-provided ground truth for a single floor plan."""

    floor_plan: FloorPlan
    annotator_id: str
    reviewed_by: str | None = None
    notes: str | None = None


class DatasetItem(BaseModel):
    id: str
    image_path: str
    source: str
    """Where this plan came from: developer name, scraping source, partnership, etc."""

    typology: Typology
    n_floors: int = Field(..., ge=1)
    n_rooms: int = Field(..., ge=0)
    region: Literal["mien_bac", "mien_trung", "mien_nam"] | None = None
    annotation: Annotation | None = None
    split: Split | None = None
