# Phong Thủy + Floor Plan AI

AI-powered floor plan analysis with Vietnamese phong thủy interpretation.
Mobile-first. Vietnamese-canonical ontology.

## Why this is defensible

1. **`packages/dataset`** — curated corpus of Vietnamese residential floor plans (apartment, nhà ống, nhà phố) with VN-specific labels (ban thờ, sân giếng trời, etc.). Western datasets like CubiCasa5K do not cover these typologies well.
2. **`packages/ontology`** — phong thủy encoded as versioned, queryable data (bát trạch, cung mệnh, ngũ hành, hướng). Expert-validated YAML, not LLM hallucination.

The CV model and mobile app are commodity work on top of these two assets.

## Stack

| Layer     | Tech                                                |
|-----------|-----------------------------------------------------|
| Mobile    | Expo (React Native + TypeScript), React Navigation  |
| API       | FastAPI (Python 3.12), uv                           |
| CV        | PyTorch — floor plan parsing (walls, rooms, doors)  |
| Ontology  | YAML data + Pydantic models + pure-Python queries   |
| Dataset   | Ingestion + labeling tooling for VN floor plans     |
| Infra     | Docker, docker-compose, GitHub Actions CI           |

## Repository layout

```
apps/
  api/                # FastAPI service
  mobile/             # Expo app
packages/
  cv/                 # Floor plan CV models
  ontology/           # Phong thủy knowledge as data
  dataset/            # VN floor plan corpus tooling
infra/
  docker/             # Dockerfiles
  compose/            # docker-compose for local dev
.github/workflows/    # CI
```

## Quick start

Prerequisites: `uv`, `pnpm`, `docker` (optional for compose).

```bash
make install        # install Python + Node deps
make api            # run FastAPI at http://localhost:8000
make demo           # same as `make api` — open http://localhost:8000/
make mobile         # run Expo dev server
make test           # pytest + mobile tests
make lint           # ruff + mypy + eslint
```

## Demo

Run `make api` and open **http://localhost:8000/** in a browser. The page is a
self-contained, no-build demo (served by the API itself) that drives the real
endpoints end-to-end — ideal for screenshots:

1. **Cung mệnh** — birth date + gender → bát trạch good/bad directions.
2. **Floor plan** — upload an image or use the built-in sample (nhà ống 4×16m);
   the CV pipeline returns rooms, walls and doors.
3. **Bát trạch overlay** — each room is colored by ngũ hành and, once a cung
   mệnh is computed, outlined green/red by its direction relative to the house
   center (e.g. "phòng ngủ hướng Bắc — Diên Niên").

No Expo or build step required. The CV model runs in `STUB_MODE=on`
(deterministic sample layout) until a trained checkpoint is available.

## Ontology conventions

- Canonical keys are **Vietnamese, lowercased, underscored**: `cung_can`, `huong_tay_bac`, `ngu_hanh_kim`.
- Each entity carries `label_vi` and `label_en` for UI rendering.
- All phong thủy data lives in [`packages/ontology/src/ontology/data/`](packages/ontology/src/ontology/data) as YAML. **Treat it like a database schema** — version migrations, validate, do not edit casually.

## Phong thủy school

We use **traditional Bát Trạch Minh Cảnh**, not Lạc Việt. Rationale and future swappability: [`docs/SCHOOL_DECISION.md`](docs/SCHOOL_DECISION.md).

## Status

Scaffold — incubating idea. `cung_menh_from_birth` is implemented with the standard formula and Lập Xuân (Feb 4) cutoff, covered by reference-value tests. CV pipeline is a stub awaiting a trained model and labeled data. The bát trạch table is encoded from standard references but **must be expert-validated before commercial release**.
