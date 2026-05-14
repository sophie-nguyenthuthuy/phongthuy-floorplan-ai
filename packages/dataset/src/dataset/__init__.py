"""Vietnamese floor plan dataset tooling.

The defensible moat. Western datasets (CubiCasa5K, R-FP, Rent3D) underrepresent:
  - nhà ống (tube houses) — narrow, deep, multi-floor
  - nhà phố (townhouses) with mixed commercial ground floor
  - apartment layouts common in HCMC/Hanoi developers
  - VN-specific rooms: phòng thờ (altar room), sân giếng trời (light well)

This package handles ingestion of raw plans, annotation schema, train/val/test
splits, and quality checks.
"""

from dataset.ingest import DatasetIngester, ingest_directory
from dataset.schema import Annotation, DatasetItem, Split

__all__ = ["Annotation", "DatasetIngester", "DatasetItem", "Split", "ingest_directory"]
