"""Command-line interface for dataset operations.

Usage:
    python -m dataset ingest <raw_dir> -o <manifest.jsonl>
    python -m dataset stats <manifest.jsonl>
    python -m dataset split <manifest.jsonl> -o <out_dir> [--seed 42]
"""

import argparse
import sys
from pathlib import Path

from dataset.ingest import ingest_directory
from dataset.manifest import read_manifest, write_manifest
from dataset.split import stratified_split
from dataset.stats import compute_stats, stats_to_text


def _cmd_ingest(args: argparse.Namespace) -> int:
    raw = Path(args.raw_dir)
    if not raw.is_dir():
        print(f"error: not a directory: {raw}", file=sys.stderr)
        return 2

    items = ingest_directory(raw)
    out = Path(args.output)
    n = write_manifest(items, out)
    print(f"Wrote {n} items to {out}")
    return 0


def _cmd_stats(args: argparse.Namespace) -> int:
    manifest = Path(args.manifest)
    items = read_manifest(manifest)
    stats = compute_stats(items)
    print(stats_to_text(stats))
    return 0


def _cmd_split(args: argparse.Namespace) -> int:
    manifest = Path(args.manifest)
    items = read_manifest(manifest)
    splits = stratified_split(items, seed=args.seed)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for split_name, split_items in splits.items():
        path = out_dir / f"{split_name}.jsonl"
        n = write_manifest(split_items, path)
        print(f"  {split_name:<6} {n:>5}  → {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m dataset", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ingest = sub.add_parser("ingest", help="Ingest a raw/ directory into a manifest")
    p_ingest.add_argument("raw_dir", help="Directory containing raw images")
    p_ingest.add_argument("-o", "--output", required=True, help="Output manifest path (JSONL)")
    p_ingest.set_defaults(func=_cmd_ingest)

    p_stats = sub.add_parser("stats", help="Print summary statistics for a manifest")
    p_stats.add_argument("manifest", help="Path to manifest.jsonl")
    p_stats.set_defaults(func=_cmd_stats)

    p_split = sub.add_parser("split", help="Produce train/val/test splits from a manifest")
    p_split.add_argument("manifest", help="Path to manifest.jsonl")
    p_split.add_argument("-o", "--output-dir", required=True, help="Output directory for splits")
    p_split.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    p_split.set_defaults(func=_cmd_split)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
