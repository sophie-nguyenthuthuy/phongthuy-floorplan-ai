"""Floor plan parser.

The intended production pipeline:
  1. Preprocess: deskew, denoise, threshold
  2. Wall segmentation: U-Net trained on CubiCasa5K + VN dataset (packages/dataset)
  3. Room polygonization: flood-fill enclosed regions, classify by features
  4. Door detection: object detector (e.g. YOLO) on wall gaps
  5. Scale inference: OCR on legend, or user-provided

Until a model is trained, `FloorPlanParser.parse` returns a **deterministic
demo layout** so the rest of the pipeline (upload → analysis → ontology →
mobile rendering) can be wired and demoed end-to-end without a trained model.

Set `STUB_MODE=off` in the environment to disable the demo and require a real
model path, which raises `ModelNotLoadedError` if absent.
"""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image

from cv.schema import Door, FloorPlan, Point, Room, Wall


class ModelNotLoadedError(RuntimeError):
    pass


class FloorPlanParser:
    """Stateful parser — holds loaded models in production. In demo mode
    returns a canned VN nhà-ống layout proportional to the input image size."""

    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path
        self._stub_mode = os.environ.get("STUB_MODE", "on").lower() != "off"
        if not self._stub_mode and model_path is None:
            raise ModelNotLoadedError(
                "STUB_MODE=off but no model_path was provided; pass a trained "
                "torch checkpoint or re-enable STUB_MODE for demo output."
            )

    def parse(self, image_path: Path) -> FloorPlan:
        with Image.open(image_path) as im:
            width, height = im.size

        if not self._stub_mode:
            # Future: load self.model_path and run inference. Until trained,
            # treat this branch as not-implemented.
            raise ModelNotLoadedError(
                "Real CV inference not implemented yet — train a U-Net + YOLO "
                "on packages/dataset and load the checkpoint here."
            )

        return _demo_layout(width, height)


def parse_image(image_path: Path) -> FloorPlan:
    """Convenience entrypoint. For repeated calls, instantiate FloorPlanParser yourself."""
    return FloorPlanParser().parse(image_path)


def _demo_layout(width_px: int, height_px: int) -> FloorPlan:
    """Deterministic VN nhà-ống (tube house) layout, scaled to the image.

    Proportions roughly match a 4x16m lot — the modal urban Vietnamese
    residential footprint. Mặt tiền (front) at the bottom of the image
    (south by convention in many VN drawings), so north_angle_deg defaults
    to 0 (image up = compass north).
    """
    # Treat the image as a 4 m × 16 m lot at uniform pixel density.
    scale = max(width_px, height_px) / 16.0  # px per metre
    w = 4.0 * scale
    h = 16.0 * scale
    margin_x = (width_px - w) / 2
    margin_y = (height_px - h) / 2

    def pt(x_m: float, y_m: float) -> Point:
        # Convert (metres from lot bottom-left) → image pixels (origin top-left).
        return Point(x=margin_x + x_m * scale, y=height_px - margin_y - y_m * scale)

    def room(name: str, x0: float, y0: float, x1: float, y1: float, confidence: float) -> Room:
        return Room(
            type=name,  # type: ignore[arg-type]
            polygon=[pt(x0, y0), pt(x1, y0), pt(x1, y1), pt(x0, y1)],
            area_m2=round((x1 - x0) * (y1 - y0), 2),
            confidence=confidence,
        )

    # Rooms (front-to-back along the 16 m length):
    rooms = [
        room("phong_khach", 0.0, 0.0, 4.0, 3.5, 0.78),  # living room (front)
        room("phong_an", 0.0, 3.5, 4.0, 5.5, 0.72),  # dining
        room("phong_bep", 0.0, 5.5, 2.5, 7.5, 0.81),  # kitchen
        room("phong_tam", 2.5, 5.5, 4.0, 7.5, 0.74),  # bathroom (ground)
        room("san_gieng_troi", 1.5, 7.5, 3.0, 9.0, 0.69),  # light well (VN-specific)
        room("cau_thang", 0.0, 7.5, 1.5, 9.0, 0.83),  # stairs
        room("phong_ngu", 0.0, 9.0, 4.0, 12.5, 0.76),  # master bedroom
        room("phong_ngu", 0.0, 12.5, 4.0, 15.0, 0.71),  # second bedroom
        room("phong_tho", 1.0, 15.0, 3.0, 16.0, 0.65),  # altar room (back; top floor by convention)
    ]

    # Perimeter walls + room dividers (simplified — perimeter only here).
    walls = [
        Wall(start=pt(0, 0), end=pt(4, 0), thickness=0.2, load_bearing=True),
        Wall(start=pt(4, 0), end=pt(4, 16), thickness=0.2, load_bearing=True),
        Wall(start=pt(4, 16), end=pt(0, 16), thickness=0.2, load_bearing=True),
        Wall(start=pt(0, 16), end=pt(0, 0), thickness=0.2, load_bearing=True),
    ]

    doors = [
        Door(position=pt(2.0, 0.0), width=1.2, swing_direction="in"),  # front door
    ]

    return FloorPlan(
        width_px=width_px,
        height_px=height_px,
        scale_m_per_px=1.0 / scale,
        walls=walls,
        doors=doors,
        rooms=rooms,
        north_angle_deg=0.0,
    )
