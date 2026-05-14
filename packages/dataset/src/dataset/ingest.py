"""Ingest raw floor plan images from a directory into the dataset format.

Expected directory layout:
    raw/
      <source>/
        <typology>/
          plan_001.png
          plan_001.meta.json   # optional metadata override
          ...
"""

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from PIL import Image

from dataset.schema import DatasetItem, Typology

SUPPORTED_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp", ".tiff"})


def _stable_id(image_path: Path) -> str:
    """Content-addressed ID: SHA1 of the file bytes, first 16 chars."""
    digest = hashlib.sha1(image_path.read_bytes()).hexdigest()
    return digest[:16]


def _read_meta(image_path: Path) -> dict[str, Any]:
    meta_path = image_path.with_suffix(image_path.suffix + ".meta.json")
    if not meta_path.exists():
        meta_path = image_path.with_suffix(".meta.json")
    if meta_path.exists():
        loaded = json.loads(meta_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError(f"Expected dict at root of {meta_path}, got {type(loaded).__name__}")
        return loaded
    return {}


class DatasetIngester:
    def __init__(self, root: Path) -> None:
        self.root = root

    def discover(self) -> Iterable[Path]:
        for path in self.root.rglob("*"):
            if path.suffix.lower() in SUPPORTED_EXTENSIONS and path.is_file():
                yield path

    def ingest_one(self, image_path: Path) -> DatasetItem:
        # Validate it's a real image
        with Image.open(image_path) as im:
            im.verify()

        meta = _read_meta(image_path)
        rel = image_path.relative_to(self.root)
        parts = rel.parts

        source = meta.get("source") or (parts[0] if len(parts) > 1 else "unknown")
        typology: Typology = meta.get("typology") or (
            parts[1] if len(parts) > 2 else "khac"  # type: ignore[assignment]
        )

        return DatasetItem(
            id=_stable_id(image_path),
            image_path=str(image_path),
            source=source,
            typology=typology,
            n_floors=meta.get("n_floors", 1),
            n_rooms=meta.get("n_rooms", 0),
            region=meta.get("region"),
        )

    def ingest_all(self) -> list[DatasetItem]:
        return [self.ingest_one(p) for p in self.discover()]


def ingest_directory(root: Path) -> list[DatasetItem]:
    return DatasetIngester(root).ingest_all()
