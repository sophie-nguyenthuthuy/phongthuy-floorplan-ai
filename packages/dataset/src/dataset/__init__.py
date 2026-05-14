"""Vietnamese floor plan dataset tooling.

The defensible moat. Western datasets (CubiCasa5K, R-FP, Rent3D) underrepresent:
  - nhà ống (tube houses) — narrow, deep, multi-floor
  - nhà phố (townhouses) with mixed commercial ground floor
  - apartment layouts common in HCMC/Hanoi developers
  - VN-specific rooms: phòng thờ (altar room), sân giếng trời (light well)

This package handles ingestion, manifest format, stratified splits, and stats.
"""

from dataset.ingest import DatasetIngester, ingest_directory
from dataset.manifest import read_manifest, write_manifest
from dataset.schema import Annotation, DatasetItem, Split, Typology
from dataset.split import stratified_split
from dataset.stats import DatasetStats, compute_stats

__all__ = [
    "Annotation",
    "DatasetIngester",
    "DatasetItem",
    "DatasetStats",
    "Split",
    "Typology",
    "compute_stats",
    "ingest_directory",
    "read_manifest",
    "stratified_split",
    "write_manifest",
]
