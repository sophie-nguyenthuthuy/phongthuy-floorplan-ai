"""Stratified train/val/test split.

Stratification keys default to (typology, source) so each typology is
represented proportionally in every split, and so the same source doesn't
bleed across splits in unbalanced ways.

Deterministic given the seed and input ordering. Idempotent: running it twice
with the same inputs produces the same assignments.
"""

import random
from collections import defaultdict
from collections.abc import Iterable, Sequence

from dataset.schema import DatasetItem, Split

DEFAULT_RATIOS: dict[Split, float] = {"train": 0.8, "val": 0.1, "test": 0.1}


def _validate_ratios(ratios: dict[Split, float]) -> None:
    total = sum(ratios.values())
    if not 0.999 <= total <= 1.001:
        raise ValueError(f"Split ratios must sum to 1.0, got {total}")
    for split, r in ratios.items():
        if r < 0:
            raise ValueError(f"Split ratio for {split} must be non-negative, got {r}")


def _stratum_key(item: DatasetItem, by: Sequence[str]) -> tuple[object, ...]:
    return tuple(getattr(item, attr) for attr in by)


def stratified_split(
    items: Iterable[DatasetItem],
    ratios: dict[Split, float] | None = None,
    by: Sequence[str] = ("typology", "source"),
    seed: int = 42,
) -> dict[Split, list[DatasetItem]]:
    """Assign each item to a split, stratified by `by` fields.

    Items are grouped by the stratification key, shuffled deterministically
    within each group, then sliced according to `ratios`. Each item keeps its
    original metadata; the returned items have their `split` field set.
    """
    ratios = ratios or DEFAULT_RATIOS
    _validate_ratios(ratios)

    rng = random.Random(seed)
    splits_order: list[Split] = ["train", "val", "test"]

    # Group by stratum
    strata: dict[tuple[object, ...], list[DatasetItem]] = defaultdict(list)
    for it in items:
        strata[_stratum_key(it, by)].append(it)

    out: dict[Split, list[DatasetItem]] = {s: [] for s in splits_order}

    for stratum_items in strata.values():
        # Sort first for determinism regardless of input order, then shuffle.
        sorted_items = sorted(stratum_items, key=lambda x: x.id)
        rng.shuffle(sorted_items)

        n = len(sorted_items)
        # Compute split sizes; remainder goes to train.
        sizes: dict[Split, int] = {s: int(n * ratios.get(s, 0.0)) for s in splits_order}
        sizes["train"] = n - sizes["val"] - sizes["test"]

        cursor = 0
        for split in splits_order:
            chunk = sorted_items[cursor : cursor + sizes[split]]
            for it in chunk:
                # Pydantic models are immutable by default — use model_copy.
                out[split].append(it.model_copy(update={"split": split}))
            cursor += sizes[split]

    return out
