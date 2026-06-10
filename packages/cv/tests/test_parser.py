from pathlib import Path

from cv import parse_image
from cv.schema import FloorPlan
from PIL import Image


def test_parser_returns_image_dimensions(tmp_path: Path) -> None:
    image_path = tmp_path / "plan.png"
    Image.new("RGB", (640, 480), color="white").save(image_path)

    plan = parse_image(image_path)

    assert isinstance(plan, FloorPlan)
    assert plan.width_px == 640
    assert plan.height_px == 480


def test_demo_parser_returns_vn_nha_ong_layout(tmp_path: Path) -> None:
    """In STUB_MODE (the default), the parser returns a deterministic VN
    nhà-ống layout so the upload → analyze → render flow can be demoed
    end-to-end without a trained CV model."""
    image_path = tmp_path / "plan.png"
    Image.new("RGB", (640, 480)).save(image_path)

    plan = parse_image(image_path)

    # Demo layout always includes core VN-specific rooms.
    room_types = {r.type for r in plan.rooms}
    assert "phong_khach" in room_types
    assert "phong_bep" in room_types
    assert "phong_ngu" in room_types
    assert "phong_tho" in room_types  # altar room — VN-specific
    # Perimeter walls + at least the front door.
    assert len(plan.walls) >= 4
    assert len(plan.doors) >= 1
    # Scale is inferred from image dimensions.
    assert plan.scale_m_per_px is not None and plan.scale_m_per_px > 0
