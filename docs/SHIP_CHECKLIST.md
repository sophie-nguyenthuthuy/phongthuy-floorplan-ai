# Ship checklist — phongthuy-floorplan-ai

## 1. CV model

- [ ] **Train the floor-plan parser** (currently a deterministic VN
      nhà-ống stub):
  - Acquire labelled dataset — see `packages/dataset/LABELING_GUIDE.md`.
    Public starter: CubiCasa5K. Vietnamese typologies: collect your own.
  - Run `scripts/train_floorplan.sh` (see this repo's `scripts/`).
  - Output: a TorchScript checkpoint at `packages/cv/models/floorplan.pt`.
  - Flip `STUB_MODE=off` and load via `FloorPlanParser(model_path=...)`.

## 2. Phong thủy ontology

- [ ] **Expert validation** — the bát trạch table at
      `packages/ontology/src/ontology/data/bat_trach.yaml` is encoded
      from standard references but must be reviewed by a practising
      expert before any commercial use. Tag a version once signed off.
- [ ] **School selection** — defaults to Bát Trạch Minh Cảnh. To swap to
      Lạc Việt, see `docs/SCHOOL_DECISION.md`.

## 3. Mobile distribution

- [ ] **Apple Developer Program** ($99/year) for iOS TestFlight + App Store.
- [ ] **Google Play Console** ($25 one-time) for Android.
- [ ] **EAS build profile** configured in `apps/mobile`.
- [ ] **Privacy policy URL** required for both stores.

## 4. Smoke before release

```
make smoke PROJECT=phongthuy-floorplan-ai
.venv/bin/pytest -q
```
