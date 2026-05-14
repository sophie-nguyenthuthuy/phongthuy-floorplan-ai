from pathlib import Path

from dataset.manifest import read_manifest, write_manifest
from dataset.schema import DatasetItem


def _item(id_: str, **overrides: object) -> DatasetItem:
    base: dict[str, object] = {
        "id": id_,
        "image_path": f"/data/raw/{id_}.png",
        "source": "vendor_a",
        "typology": "nha_ong",
        "n_floors": 3,
        "n_rooms": 5,
    }
    base.update(overrides)
    return DatasetItem(**base)  # type: ignore[arg-type]


def test_write_and_read_roundtrip(tmp_path: Path) -> None:
    items = [_item("a"), _item("b", source="vendor_b"), _item("c", typology="chung_cu")]
    path = tmp_path / "manifest.jsonl"

    written = write_manifest(items, path)
    assert written == 3

    loaded = read_manifest(path)
    assert len(loaded) == 3
    assert [it.id for it in loaded] == ["a", "b", "c"]
    assert loaded[1].source == "vendor_b"
    assert loaded[2].typology == "chung_cu"


def test_empty_lines_are_skipped(tmp_path: Path) -> None:
    path = tmp_path / "manifest.jsonl"
    write_manifest([_item("a")], path)
    # Append blank lines
    with path.open("a", encoding="utf-8") as f:
        f.write("\n\n")
    loaded = read_manifest(path)
    assert len(loaded) == 1


def test_invalid_line_raises_with_line_number(tmp_path: Path) -> None:
    import pytest

    path = tmp_path / "bad.jsonl"
    path.write_text('{"valid": false}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="line"):
        read_manifest(path)
