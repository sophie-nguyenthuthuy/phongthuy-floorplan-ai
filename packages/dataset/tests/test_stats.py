from cv.schema import FloorPlan
from dataset.schema import Annotation, DatasetItem
from dataset.stats import compute_stats, stats_to_text


def _item(
    id_: str,
    typology: str = "nha_ong",
    source: str = "vendor_a",
    region: str | None = None,
    annotated: bool = False,
    reviewed: bool = False,
) -> DatasetItem:
    annotation = None
    if annotated:
        annotation = Annotation(
            floor_plan=FloorPlan(width_px=100, height_px=100),
            annotator_id="ann_001",
            reviewed_by="ann_002" if reviewed else None,
        )
    return DatasetItem(
        id=id_,
        image_path=f"/data/{id_}.png",
        source=source,
        typology=typology,  # type: ignore[arg-type]
        n_floors=1,
        n_rooms=3,
        region=region,  # type: ignore[arg-type]
        annotation=annotation,
    )


def test_empty_stats_returns_zeros() -> None:
    stats = compute_stats([])
    assert stats.total == 0
    assert stats.by_typology == {}


def test_stats_count_by_typology_and_source() -> None:
    items = [
        _item("a", typology="nha_ong", source="x"),
        _item("b", typology="nha_ong", source="y"),
        _item("c", typology="chung_cu", source="x"),
    ]
    stats = compute_stats(items)
    assert stats.total == 3
    assert stats.by_typology == {"nha_ong": 2, "chung_cu": 1}
    assert stats.by_source == {"x": 2, "y": 1}


def test_stats_count_annotations_and_reviews() -> None:
    items = [
        _item("a", annotated=False),
        _item("b", annotated=True, reviewed=False),
        _item("c", annotated=True, reviewed=True),
    ]
    stats = compute_stats(items)
    assert stats.annotated == 2
    assert stats.reviewed == 1


def test_stats_source_concentration() -> None:
    items = [_item(f"i{i}", source="dominant") for i in range(8)] + [
        _item(f"j{i}", source="other") for i in range(2)
    ]
    stats = compute_stats(items)
    assert stats.source_concentration_top1 == 0.8


def test_stats_to_text_includes_warning_when_imbalanced() -> None:
    items = [_item(f"i{i}", source="single") for i in range(10)]
    stats = compute_stats(items)
    text = stats_to_text(stats)
    assert "source-imbalanced" in text
