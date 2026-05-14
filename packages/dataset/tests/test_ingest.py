import json
from pathlib import Path

from dataset import ingest_directory
from PIL import Image


def _make_image(
    path: Path,
    size: tuple[int, int] = (100, 100),
    color: tuple[int, int, int] = (255, 255, 255),
) -> None:
    """Make a uniquely-content image. Vary `color` for distinct hashes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color=color).save(path)


def test_ingest_directory_discovers_images(tmp_path: Path) -> None:
    _make_image(tmp_path / "vendor_a" / "nha_ong" / "plan_001.png", color=(255, 0, 0))
    _make_image(tmp_path / "vendor_a" / "chung_cu" / "plan_002.png", color=(0, 255, 0))
    _make_image(tmp_path / "vendor_b" / "biet_thu" / "plan_003.jpg", color=(0, 0, 255))

    items = ingest_directory(tmp_path)

    assert len(items) == 3
    ids = {it.id for it in items}
    assert len(ids) == 3, "IDs must be unique per file"


def test_ingest_infers_source_and_typology_from_path(tmp_path: Path) -> None:
    _make_image(tmp_path / "developer_x" / "nha_ong" / "plan.png")

    items = ingest_directory(tmp_path)
    assert items[0].source == "developer_x"
    assert items[0].typology == "nha_ong"


def test_ingest_reads_meta_override(tmp_path: Path) -> None:
    image = tmp_path / "vendor" / "nha_ong" / "plan.png"
    _make_image(image)
    (image.parent / "plan.meta.json").write_text(
        json.dumps({"source": "partnership_y", "n_floors": 3, "n_rooms": 5}),
        encoding="utf-8",
    )

    items = ingest_directory(tmp_path)
    assert items[0].source == "partnership_y"
    assert items[0].n_floors == 3
    assert items[0].n_rooms == 5


def test_ingest_id_is_content_addressed(tmp_path: Path) -> None:
    a = tmp_path / "vendor" / "nha_ong" / "a.png"
    b = tmp_path / "vendor" / "nha_ong" / "b.png"
    _make_image(a, (50, 50))
    _make_image(b, (50, 50))
    # Same content (PIL default settings) → same hash → same id
    a.write_bytes(b.read_bytes())

    items = ingest_directory(tmp_path)
    ids = [it.id for it in items]
    assert ids[0] == ids[1]
