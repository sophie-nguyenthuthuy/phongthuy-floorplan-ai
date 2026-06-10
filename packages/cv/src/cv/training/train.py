"""Train the floor-plan U-Net on the procedural synth set (+ any real
hand-labelled samples placed alongside).

Usage:
    .venv/bin/python -m cv.training.train --data data/synth --epochs 30

The output is a TorchScript checkpoint at packages/cv/models/floorplan.pt
that `FloorPlanParser` picks up automatically (bypassing STUB_MODE).

Architecture: small U-Net with 32-base channels. Trains in ~20 min on a
T4 / 30 min on M2 MPS / 4 hours on 4-core CPU.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

try:
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, Dataset
    from torchvision import transforms
except ImportError:
    print("torch + torchvision not installed. Run: uv pip install torch torchvision", file=sys.stderr)
    sys.exit(1)

from cv.training.synth import CLASSES


class FloorPlanDataset(Dataset):
    def __init__(self, root: Path, size: int = 256) -> None:
        self.rgbs = sorted(root.glob("sample_*[!_mask].png"))
        if not self.rgbs:
            # The synth glob excludes the _mask suffix; collect by pairing.
            self.rgbs = sorted(p for p in root.glob("sample_*.png") if "_mask" not in p.name)
        self.size = size
        self.tx_rgb = transforms.Compose([
            transforms.Resize((size, size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def __len__(self) -> int:
        return len(self.rgbs)

    def __getitem__(self, i: int):
        rgb_path = self.rgbs[i]
        mask_path = rgb_path.with_name(rgb_path.stem + "_mask.png")
        rgb = Image.open(rgb_path).convert("RGB")
        mask = Image.open(mask_path).resize((self.size, self.size), Image.NEAREST)
        return self.tx_rgb(rgb), torch.as_tensor(np.array(mask), dtype=torch.long)


class _Block(nn.Module):
    def __init__(self, ic: int, oc: int) -> None:
        super().__init__()
        self.body = nn.Sequential(
            nn.Conv2d(ic, oc, 3, padding=1), nn.BatchNorm2d(oc), nn.ReLU(inplace=True),
            nn.Conv2d(oc, oc, 3, padding=1), nn.BatchNorm2d(oc), nn.ReLU(inplace=True),
        )

    def forward(self, x):  # type: ignore[override]
        return self.body(x)


class SmallUNet(nn.Module):
    """32-base-channel U-Net — small enough to overfit synth but big enough
    to learn real layouts when paired with augmented real samples."""

    def __init__(self, n_classes: int) -> None:
        super().__init__()
        c1, c2, c3, c4 = 32, 64, 128, 256
        self.d1 = _Block(3, c1)
        self.d2 = _Block(c1, c2)
        self.d3 = _Block(c2, c3)
        self.bot = _Block(c3, c4)
        self.up3 = nn.ConvTranspose2d(c4, c3, 2, 2)
        self.u3 = _Block(c3 * 2, c3)
        self.up2 = nn.ConvTranspose2d(c3, c2, 2, 2)
        self.u2 = _Block(c2 * 2, c2)
        self.up1 = nn.ConvTranspose2d(c2, c1, 2, 2)
        self.u1 = _Block(c1 * 2, c1)
        self.head = nn.Conv2d(c1, n_classes, 1)
        self.pool = nn.MaxPool2d(2)

    def forward(self, x):  # type: ignore[override]
        d1 = self.d1(x)
        d2 = self.d2(self.pool(d1))
        d3 = self.d3(self.pool(d2))
        b = self.bot(self.pool(d3))
        x = self.u3(torch.cat([self.up3(b), d3], 1))
        x = self.u2(torch.cat([self.up2(x), d2], 1))
        x = self.u1(torch.cat([self.up1(x), d1], 1))
        return self.head(x)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", type=Path, default=Path("data/synth"))
    ap.add_argument("--out", type=Path, default=Path("packages/cv/models/floorplan.pt"))
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--size", type=int, default=256)
    args = ap.parse_args()

    if not args.data.exists():
        print(f"✗ data dir {args.data} missing — run `python -m cv.training.synth` first", file=sys.stderr)
        sys.exit(1)

    device = ("cuda" if torch.cuda.is_available()
              else "mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()
              else "cpu")
    print(f"▶ device={device}, classes={len(CLASSES)}, size={args.size}")

    ds = FloorPlanDataset(args.data, size=args.size)
    dl = DataLoader(ds, batch_size=args.batch, shuffle=True, num_workers=2)
    model = SmallUNet(len(CLASSES)).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    loss_fn = nn.CrossEntropyLoss()

    for epoch in range(args.epochs):
        model.train()
        running = 0.0
        for rgb, mask in dl:
            rgb, mask = rgb.to(device), mask.to(device)
            opt.zero_grad()
            logits = model(rgb)
            loss = loss_fn(logits, mask)
            loss.backward()
            opt.step()
            running += loss.item()
        print(f"  epoch {epoch + 1:02d}/{args.epochs}  loss={running / max(len(dl), 1):.4f}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    model.eval()
    # TorchScript trace so cv.parser can load without depending on this file.
    example = torch.randn(1, 3, args.size, args.size, device=device)
    scripted = torch.jit.trace(model, example)
    scripted.save(str(args.out))
    print(f"\n✓ saved {args.out}")
    print("  set STUB_MODE=off and pass model_path to FloorPlanParser to use it")


if __name__ == "__main__":
    main()
