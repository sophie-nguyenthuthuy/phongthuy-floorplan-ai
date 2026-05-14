import pytest
from dataset.schema import DatasetItem
from dataset.split import stratified_split


def _item(id_: str, typology: str = "nha_ong", source: str = "vendor_a") -> DatasetItem:
    return DatasetItem(
        id=id_,
        image_path=f"/data/{id_}.png",
        source=source,
        typology=typology,  # type: ignore[arg-type]
        n_floors=1,
        n_rooms=3,
    )


def test_split_assigns_every_item_exactly_once() -> None:
    items = [_item(f"i{i}") for i in range(100)]
    splits = stratified_split(items)

    total = sum(len(v) for v in splits.values())
    assert total == len(items)

    seen_ids = {it.id for split_items in splits.values() for it in split_items}
    assert seen_ids == {it.id for it in items}


def test_split_is_deterministic_with_seed() -> None:
    items = [_item(f"i{i}") for i in range(100)]
    a = stratified_split(items, seed=42)
    b = stratified_split(items, seed=42)
    assert [it.id for it in a["train"]] == [it.id for it in b["train"]]
    assert [it.id for it in a["val"]] == [it.id for it in b["val"]]


def test_split_is_order_independent() -> None:
    """Same items in different order should produce the same assignments."""
    items_a = [_item(f"i{i}") for i in range(100)]
    items_b = list(reversed(items_a))
    a = stratified_split(items_a, seed=42)
    b = stratified_split(items_b, seed=42)
    assert {it.id for it in a["train"]} == {it.id for it in b["train"]}


def test_split_stratifies_by_typology() -> None:
    items = [_item(f"a{i}", typology="nha_ong") for i in range(50)] + [
        _item(f"b{i}", typology="chung_cu") for i in range(50)
    ]
    splits = stratified_split(items, ratios={"train": 0.6, "val": 0.2, "test": 0.2})

    # Each typology should be represented in every split close to its overall share
    for split_items in splits.values():
        nha_ong_count = sum(1 for it in split_items if it.typology == "nha_ong")
        chung_cu_count = sum(1 for it in split_items if it.typology == "chung_cu")
        if split_items:
            ratio = nha_ong_count / len(split_items)
            assert 0.4 <= ratio <= 0.6, f"typology imbalance in split: {ratio}"
            assert nha_ong_count + chung_cu_count == len(split_items)


def test_split_sets_split_field() -> None:
    items = [_item(f"i{i}") for i in range(20)]
    splits = stratified_split(items)
    for split_name, split_items in splits.items():
        for it in split_items:
            assert it.split == split_name


def test_invalid_ratios_raise() -> None:
    items = [_item("a")]
    with pytest.raises(ValueError, match="sum to 1"):
        stratified_split(items, ratios={"train": 0.5, "val": 0.1, "test": 0.1})
