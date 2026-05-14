"""JSONL manifest read/write.

One DatasetItem per line. Resilient to schema additions — new optional fields
on `DatasetItem` will simply be `None` for old manifest entries.
"""

import json
from collections.abc import Iterable
from pathlib import Path

from dataset.schema import DatasetItem


def write_manifest(items: Iterable[DatasetItem], path: Path) -> int:
    """Write items to `path` as JSONL. Returns the number written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(item.model_dump_json(exclude_none=True))
            f.write("\n")
            count += 1
    return count


def read_manifest(path: Path) -> list[DatasetItem]:
    """Load a JSONL manifest into a list of DatasetItem."""
    items: list[DatasetItem] = []
    with path.open("r", encoding="utf-8") as f:
        for line_number, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                items.append(DatasetItem.model_validate(json.loads(line)))
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(f"Invalid manifest entry at {path}:{line_number}: {exc}") from exc
    return items
