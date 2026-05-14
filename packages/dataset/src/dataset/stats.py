"""Summary statistics for a dataset manifest.

Use this to keep an eye on class imbalance, source concentration, and
annotation completeness as the corpus grows.
"""

from collections import Counter
from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel, Field

from dataset.schema import DatasetItem


class DatasetStats(BaseModel):
    total: int
    by_typology: dict[str, int] = Field(default_factory=dict)
    by_source: dict[str, int] = Field(default_factory=dict)
    by_region: dict[str, int] = Field(default_factory=dict)
    by_split: dict[str, int] = Field(default_factory=dict)
    annotated: int = 0
    reviewed: int = 0
    source_concentration_top1: float = 0.0
    """Fraction of the corpus from its single largest source. >0.5 is a red flag."""


def compute_stats(items: Iterable[DatasetItem]) -> DatasetStats:
    items_list = list(items)
    n = len(items_list)
    if n == 0:
        return DatasetStats(total=0)

    by_typology = Counter(it.typology for it in items_list)
    by_source = Counter(it.source for it in items_list)
    by_region = Counter(it.region or "unknown" for it in items_list)
    by_split = Counter(it.split or "unassigned" for it in items_list)

    annotated = sum(1 for it in items_list if it.annotation is not None)
    reviewed = sum(
        1
        for it in items_list
        if it.annotation is not None and it.annotation.reviewed_by is not None
    )

    top1_count = by_source.most_common(1)[0][1] if by_source else 0

    return DatasetStats(
        total=n,
        by_typology={str(k): v for k, v in by_typology.items()},
        by_source=dict(by_source),
        by_region={str(k): v for k, v in by_region.items()},
        by_split={str(k): v for k, v in by_split.items()},
        annotated=annotated,
        reviewed=reviewed,
        source_concentration_top1=top1_count / n,
    )


def stats_to_text(stats: DatasetStats) -> str:
    """Render stats as a human-readable string for CLI output."""
    lines: list[str] = [f"Total: {stats.total}"]

    def _section(title: str, data: dict[str, Any]) -> None:
        lines.append(f"\n{title}:")
        for k, v in sorted(data.items(), key=lambda kv: -kv[1]):
            pct = (v / stats.total * 100) if stats.total else 0
            lines.append(f"  {k:<20} {v:>5}  ({pct:>5.1f}%)")

    _section("By typology", stats.by_typology)
    _section("By source", stats.by_source)
    _section("By region", stats.by_region)
    _section("By split", stats.by_split)

    lines.append(f"\nAnnotated: {stats.annotated} ({stats.annotated / stats.total * 100:.1f}%)")
    lines.append(f"Reviewed:  {stats.reviewed} ({stats.reviewed / stats.total * 100:.1f}%)")
    lines.append(f"Top-1 source concentration: {stats.source_concentration_top1 * 100:.1f}%")
    if stats.source_concentration_top1 > 0.5:
        lines.append("  ⚠️  >50% from one source — corpus is source-imbalanced.")
    return "\n".join(lines)
