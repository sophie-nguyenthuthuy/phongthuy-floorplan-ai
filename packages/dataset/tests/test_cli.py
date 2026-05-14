"""End-to-end CLI test: ingest → stats → split."""

import io
from contextlib import redirect_stdout
from pathlib import Path

from dataset.cli import main
from dataset.manifest import read_manifest
from PIL import Image


def _make_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (100, 100), color="white").save(path)


def _make_raw_dir(root: Path, n_per_typology: int = 5) -> None:
    for source in ("vendor_a", "vendor_b"):
        for typology in ("nha_ong", "chung_cu"):
            for i in range(n_per_typology):
                _make_image(root / source / typology / f"plan_{i:03d}.png")


def test_cli_ingest_then_stats_then_split(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    _make_raw_dir(raw, n_per_typology=5)
    manifest = tmp_path / "manifest.jsonl"

    # Ingest
    rc = main(["ingest", str(raw), "-o", str(manifest)])
    assert rc == 0
    items = read_manifest(manifest)
    assert len(items) == 20  # 2 sources × 2 typologies × 5

    # Stats
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(["stats", str(manifest)])
    assert rc == 0
    output = buf.getvalue()
    assert "Total: 20" in output
    assert "nha_ong" in output

    # Split
    out_dir = tmp_path / "splits"
    rc = main(["split", str(manifest), "-o", str(out_dir), "--seed", "7"])
    assert rc == 0
    train = read_manifest(out_dir / "train.jsonl")
    val = read_manifest(out_dir / "val.jsonl")
    test = read_manifest(out_dir / "test.jsonl")
    assert len(train) + len(val) + len(test) == 20
    # Default ratios are 80/10/10 → with 20 items per stratum size 5,
    # most strata get train=4, val=0, test=1 (or similar). Check majority is train.
    assert len(train) >= 10


def test_cli_ingest_missing_dir_returns_nonzero(tmp_path: Path) -> None:
    rc = main(["ingest", str(tmp_path / "does_not_exist"), "-o", str(tmp_path / "m.jsonl")])
    assert rc == 2
