# Dataset — VN floor plans

This is the moat. The model is the easy part.

## Why it has to exist

Public floor-plan datasets are predominantly Western:

| Dataset       | Plans   | Typology coverage                          |
|---------------|---------|--------------------------------------------|
| CubiCasa5K    | 5,000   | Finnish apartments, single-floor           |
| Rent3D        | 215     | US apartments                              |
| R-FP (R3D)    | 500+    | Western residential                        |
| ZInD (Zillow) | ~71k    | US single-family homes                     |

Vietnamese residential plans differ structurally:

- **Nhà ống** — 4–5 m wide × 15–25 m deep, 3–5 floors, narrow staircase
- **Nhà phố** — ground-floor commercial + upper residential
- **Chung cư** (apartment) — VN developer floor plate conventions
- **Biệt thự** — villa, varied
- **Nhà cấp 4** — single-story rural/peri-urban

And VN-specific rooms that Western models don't predict:

- **Phòng thờ** — altar room (sometimes a dedicated room, sometimes a corner shelf)
- **Sân giếng trời** — light well (interior open-air courtyard, common in nhà ống)
- **Ban thờ ông Táo** — kitchen altar position (relevant for phong thủy)

A model trained on CubiCasa5K will systematically misread these. Fine-tuning needs our own corpus.

## Target corpus

| Stage           | Plans  | Use                                       |
|-----------------|--------|-------------------------------------------|
| MVP             | 500    | Sanity-check fine-tune, internal demo     |
| Beta            | 2,000  | First credible model                      |
| GA              | 5,000  | Production model, stratified by typology  |

Distribution targets (% of corpus):

| Typology     | Target % |
|--------------|----------|
| chung_cu     | 35       |
| nha_ong      | 25       |
| nha_pho      | 15       |
| biet_thu     | 10       |
| nha_cap_4    | 10       |
| khac         | 5        |

Region split target: 40% miền Nam, 40% miền Bắc, 20% miền Trung.

## Sources — legal status matrix

| Source                                              | Legal?         | Effort | Quality |
|-----------------------------------------------------|----------------|--------|---------|
| Developer brochures shared with permission          | ✅              | M      | High    |
| Architect partnerships (signed agreement)           | ✅              | H      | High    |
| Original drawings purchased / commissioned          | ✅              | H      | High    |
| Public MOC documents, building code samples         | ✅              | L      | Medium  |
| Scraping batdongsan.com.vn / mogi.vn                | ❌ — copyright  | L      | Medium  |
| Reusing CubiCasa5K-style public corpora (research)  | ✅ research only | L      | N/A     |

**Default policy:** no scraping. Plans enter the corpus only via explicit source permission, recorded in the `source` field on `DatasetItem`.

## Directory layout

```
data/
  raw/                  # original images, organized by source/typology
    <source>/
      <typology>/
        plan_001.png
        plan_001.meta.json    # optional override metadata
  manifest.jsonl        # generated; one DatasetItem per line
  splits/
    train.jsonl
    val.jsonl
    test.jsonl
```

`data/` is gitignored — see [`data/README.md`](../../data/README.md) for how to provision it.

## CLI

```bash
# 1. Ingest raw images into a manifest
uv run python -m dataset ingest data/raw -o data/manifest.jsonl

# 2. Inspect counts and balance
uv run python -m dataset stats data/manifest.jsonl

# 3. Produce train/val/test splits (deterministic, stratified by typology+source)
uv run python -m dataset split data/manifest.jsonl -o data/splits
```

## Annotation

Labeling rules and quality bar: [`docs/LABELING_GUIDE.md`](../../docs/LABELING_GUIDE.md).

For tooling we recommend Label Studio — its polygon and keypoint tools are sufficient for walls / rooms / doors / north arrow.

## Quality bar

A plan enters the labeled split only if:

1. Image resolution ≥ 800 px on the shorter side.
2. North direction is determinable (legend arrow visible, OR architect confirmed).
3. Scale is determinable (legend bar OR a known reference dimension).
4. All exterior walls form a closed polygon.
5. Reviewed by a second annotator (`Annotation.reviewed_by` populated).

Items below this bar can stay in the manifest as `annotation: null` for unsupervised pretraining, but must not enter labeled training splits.
