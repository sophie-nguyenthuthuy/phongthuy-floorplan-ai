#!/usr/bin/env bash
# Train the floor-plan U-Net on synthetic + (optionally) real data.
#
# Real-data placement: drop labelled (rgb + mask) pairs into
#   packages/cv/data/real/sample_NNNN.png + _mask.png
# alongside the generated synth/ — pass --data <combined-dir> if you keep
# them separate and pre-link with `ln -s`.
#
# Usage:
#   ./scripts/train_floorplan.sh             # 2000 synth + 30 epochs
#   N=10000 EPOCHS=60 ./scripts/train_floorplan.sh
#   PYTHON=python3.11 ./scripts/train_floorplan.sh    # force interpreter
set -euo pipefail

cd "$(dirname "$0")/.."

N="${N:-2000}"
EPOCHS="${EPOCHS:-30}"
DATA="${DATA:-packages/cv/data/synth}"
OUT="${OUT:-packages/cv/models/floorplan.pt}"
VENV="${VENV:-.train-venv}"

# ─── Locate a usable Python ────────────────────────────────────────────────
# Prefer 3.11/3.12 for the widest torch-wheel compatibility, but 3.13 also
# works as of mid-2026. Fall back to `python3` so anaconda installs work.
if [[ -n "${PYTHON:-}" ]]; then
    :  # honour explicit override
elif command -v python3.12 >/dev/null 2>&1; then PYTHON=python3.12
elif command -v python3.11 >/dev/null 2>&1; then PYTHON=python3.11
elif command -v python3.13 >/dev/null 2>&1; then PYTHON=python3.13
elif command -v python3.10 >/dev/null 2>&1; then PYTHON=python3.10
elif command -v python3       >/dev/null 2>&1; then PYTHON=python3
else echo "✗ no python3 found on PATH" >&2; exit 1; fi
echo "▶ using $PYTHON ($($PYTHON --version))"

# ─── Build / refresh a dedicated training venv ─────────────────────────────
# We intentionally use a separate venv (`.train-venv`) rather than the
# project's main `.venv` so torch (~2 GB) doesn't bloat the runtime image.
if [[ ! -x "$VENV/bin/python" ]]; then
    echo "▶ creating $VENV"
    "$PYTHON" -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install --quiet --upgrade pip

echo "▶ installing torch + torchvision (this can take 3–10 min on first run)"
"$VENV/bin/python" -m pip install --quiet \
    torch torchvision pillow numpy

# ─── Synth ─────────────────────────────────────────────────────────────────
echo "▶ generating $N synthetic samples → $DATA"
PYTHONPATH="packages/cv/src" \
    "$VENV/bin/python" -m cv.training.synth --out "$DATA" --n "$N"

# ─── Train ─────────────────────────────────────────────────────────────────
echo "▶ training $EPOCHS epochs"
PYTHONPATH="packages/cv/src" \
    "$VENV/bin/python" -m cv.training.train --data "$DATA" --out "$OUT" --epochs "$EPOCHS"

echo ""
echo "✓ Checkpoint: $OUT"
echo "  Test with:"
echo "    STUB_MODE=off PYTHONPATH=packages/cv/src $VENV/bin/python -c \\"
echo "      'from pathlib import Path; from cv.parser import FloorPlanParser;\\"
echo "       p=FloorPlanParser(Path(\"$OUT\"));\\"
echo "       print(p.parse(next(Path(\"storage\").glob(\"*.png\"))))'"
