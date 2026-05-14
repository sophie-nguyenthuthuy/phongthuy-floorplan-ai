"""Floor plan parser — currently a stub.

The intended pipeline:
  1. Preprocess: deskew, denoise, threshold
  2. Wall segmentation: U-Net trained on CubiCasa5K + VN dataset (packages/dataset)
  3. Room polygonization: flood-fill enclosed regions, classify by features
  4. Door detection: object detector (e.g. YOLO) on wall gaps
  5. Scale inference: OCR on legend, or user-provided

Until a model is trained, `parse_image` returns an empty FloorPlan with image
dimensions filled in, so the rest of the pipeline can be wired end-to-end.
"""

from pathlib import Path

from PIL import Image

from cv.schema import FloorPlan


class FloorPlanParser:
    """Stateful parser — holds loaded models in production. Currently a no-op."""

    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path
        # TODO: load torch model from model_path

    def parse(self, image_path: Path) -> FloorPlan:
        with Image.open(image_path) as im:
            width, height = im.size
        return FloorPlan(width_px=width, height_px=height)


def parse_image(image_path: Path) -> FloorPlan:
    """Convenience entrypoint. For repeated calls, instantiate FloorPlanParser yourself."""
    return FloorPlanParser().parse(image_path)
