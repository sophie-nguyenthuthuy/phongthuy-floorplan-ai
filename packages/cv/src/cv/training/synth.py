"""Procedural VN nhà-ống floor plan generator.

Until real labelled data lands, this generates an arbitrary number of plausible
Vietnamese tube-house floor plans + their semantic masks for U-Net training.

Output per sample (under `out_dir`):
    sample_NNNN.png       — RGB rendering of the plan (input)
    sample_NNNN_mask.png  — palette PNG, room-class labels per pixel

Room classes match `cv.schema.RoomType` (0 = background, 1.. = each VN room).

Run:
    .venv/bin/python -m cv.training.synth --out data/synth --n 5000

This is NOT production-grade data — it teaches the model basic VN tube-house
priors (long aspect ratio, ban thờ at the back/top, light well mid-depth).
Real photos / hand-drawings + this synthetic set together produce a usable
pilot model. Synth-only training will overfit to the generator's biases.
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from PIL import Image, ImageDraw

# Class indices — keep aligned with cv.schema.RoomType ordering.
CLASSES = (
    "background",      # 0
    "phong_khach",     # 1
    "phong_ngu",       # 2
    "phong_bep",       # 3
    "phong_tam",       # 4
    "phong_an",        # 5
    "phong_tho",       # 6
    "san_gieng_troi",  # 7
    "ban_cong",        # 8
    "hanh_lang",       # 9
    "cau_thang",       # 10
)
CLASS_INDEX: dict[str, int] = {name: i for i, name in enumerate(CLASSES)}

# Display colours for the RGB rendering (visual sanity, not for training).
COLOURS: dict[str, tuple[int, int, int]] = {
    "background": (245, 245, 245),
    "phong_khach": (255, 218, 185),
    "phong_ngu": (176, 196, 222),
    "phong_bep": (255, 200, 124),
    "phong_tam": (173, 216, 230),
    "phong_an": (255, 228, 181),
    "phong_tho": (255, 182, 193),
    "san_gieng_troi": (255, 255, 224),
    "ban_cong": (211, 211, 211),
    "hanh_lang": (220, 220, 220),
    "cau_thang": (190, 190, 190),
}


def _gen_one(rng: random.Random, size: int = 640) -> tuple[Image.Image, Image.Image]:
    """Generate a single (rgb, mask_palette) pair, both `size`×`size`.

    Layout: vertical strip representing a tube house ~4 m wide × 16 m deep.
    Mặt tiền at the bottom of the image (south by convention).
    """
    rgb = Image.new("RGB", (size, size), COLOURS["background"])
    mask = Image.new("P", (size, size), CLASS_INDEX["background"])
    rdraw = ImageDraw.Draw(rgb)
    mdraw = ImageDraw.Draw(mask)

    # Lot proportions with jitter.
    width_m = rng.uniform(3.5, 5.0)
    depth_m = rng.uniform(12.0, 18.0)
    px_per_m = (size * 0.85) / max(width_m, depth_m)
    lot_w = int(width_m * px_per_m)
    lot_h = int(depth_m * px_per_m)
    x0 = (size - lot_w) // 2
    y0 = (size - lot_h) // 2

    # Walk back-to-front laying out rooms. Front = highest y (bottom of img).
    front_y = y0 + lot_h
    cursor_m = 0.0  # metres from front

    # Living room (front, ~3.5 m deep)
    living_depth = rng.uniform(3.0, 4.2)
    _box(rdraw, mdraw, "phong_khach", x0, front_y - int(living_depth * px_per_m),
         x0 + lot_w, front_y, px_per_m)
    cursor_m += living_depth

    # Dining (~2 m)
    dining_depth = rng.uniform(1.6, 2.4)
    y_top = front_y - int((cursor_m + dining_depth) * px_per_m)
    y_bot = front_y - int(cursor_m * px_per_m)
    _box(rdraw, mdraw, "phong_an", x0, y_top, x0 + lot_w, y_bot, px_per_m)
    cursor_m += dining_depth

    # Kitchen + bathroom side-by-side (~2 m)
    kb_depth = rng.uniform(1.8, 2.4)
    mid_x = x0 + lot_w // 2 + rng.randint(-int(0.3 * px_per_m), int(0.3 * px_per_m))
    y_top = front_y - int((cursor_m + kb_depth) * px_per_m)
    y_bot = front_y - int(cursor_m * px_per_m)
    if rng.random() < 0.5:
        _box(rdraw, mdraw, "phong_bep", x0, y_top, mid_x, y_bot, px_per_m)
        _box(rdraw, mdraw, "phong_tam", mid_x, y_top, x0 + lot_w, y_bot, px_per_m)
    else:
        _box(rdraw, mdraw, "phong_tam", x0, y_top, mid_x, y_bot, px_per_m)
        _box(rdraw, mdraw, "phong_bep", mid_x, y_top, x0 + lot_w, y_bot, px_per_m)
    cursor_m += kb_depth

    # Light well + stairs (~1.5 m) — VN specific
    well_depth = rng.uniform(1.2, 1.8)
    mid_x = x0 + lot_w // 3
    y_top = front_y - int((cursor_m + well_depth) * px_per_m)
    y_bot = front_y - int(cursor_m * px_per_m)
    _box(rdraw, mdraw, "cau_thang", x0, y_top, mid_x, y_bot, px_per_m)
    _box(rdraw, mdraw, "san_gieng_troi", mid_x, y_top, x0 + lot_w, y_bot, px_per_m)
    cursor_m += well_depth

    # 1–2 bedrooms (back)
    n_bedrooms = rng.randint(1, 2)
    remaining = max(0.0, depth_m - cursor_m - 1.0)  # leave ~1 m for ban thờ
    bedroom_depth = remaining / n_bedrooms
    for _ in range(n_bedrooms):
        y_top = front_y - int((cursor_m + bedroom_depth) * px_per_m)
        y_bot = front_y - int(cursor_m * px_per_m)
        _box(rdraw, mdraw, "phong_ngu", x0, y_top, x0 + lot_w, y_bot, px_per_m)
        cursor_m += bedroom_depth

    # Ban thờ (back, slim)
    if rng.random() < 0.85:  # not every plan has it on this floor
        altar_depth = rng.uniform(0.8, 1.2)
        y_top = front_y - int((cursor_m + altar_depth) * px_per_m)
        y_bot = front_y - int(cursor_m * px_per_m)
        if y_top >= y0:
            _box(rdraw, mdraw, "phong_tho",
                 x0 + lot_w // 4, y_top, x0 + 3 * lot_w // 4, y_bot, px_per_m)

    return rgb, mask


def _box(rdraw, mdraw, klass: str, x0: int, y0: int, x1: int, y1: int, px_per_m: float) -> None:
    rdraw.rectangle((x0, y0, x1, y1), fill=COLOURS[klass], outline=(40, 40, 40), width=max(1, int(px_per_m * 0.12)))
    mdraw.rectangle((x0, y0, x1, y1), fill=CLASS_INDEX[klass])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=Path("data/synth"))
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--size", type=int, default=640)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    for i in range(args.n):
        rgb, mask = _gen_one(rng, size=args.size)
        rgb.save(args.out / f"sample_{i:05d}.png")
        mask.save(args.out / f"sample_{i:05d}_mask.png")
        if i % 200 == 0:
            print(f"  generated {i + 1}/{args.n}")

    print(f"\n✓ {args.n} samples + masks under {args.out}")
    print(f"  classes: {CLASSES}")


if __name__ == "__main__":
    main()
