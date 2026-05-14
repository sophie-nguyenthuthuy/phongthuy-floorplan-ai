from pathlib import Path

from PIL import Image

from cv import parse_image
from cv.schema import FloorPlan


def test_parser_returns_image_dimensions(tmp_path: Path) -> None:
    image_path = tmp_path / "plan.png"
    Image.new("RGB", (640, 480), color="white").save(image_path)

    plan = parse_image(image_path)

    assert isinstance(plan, FloorPlan)
    assert plan.width_px == 640
    assert plan.height_px == 480


def test_stub_parser_returns_empty_rooms(tmp_path: Path) -> None:
    image_path = tmp_path / "plan.png"
    Image.new("RGB", (100, 100)).save(image_path)

    plan = parse_image(image_path)

    assert plan.rooms == []
    assert plan.walls == []
    assert plan.doors == []
