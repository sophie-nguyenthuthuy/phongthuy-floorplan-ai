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
make mobile         # run Expo dev server
make test           # pytest + mobile tests
make lint           # ruff + mypy + eslint
```

## Ontology conventions

- Canonical keys are **Vietnamese, lowercased, underscored**: `cung_can`, `huong_tay_bac`, `ngu_hanh_kim`.
- Each entity carries `label_vi` and `label_en` for UI rendering.
- All phong thủy data lives in [`packages/ontology/src/ontology/data/`](packages/ontology/src/ontology/data) as YAML. **Treat it like a database schema** — version migrations, validate, do not edit casually.

## Status

Scaffold — incubating idea. Ontology data and CV models are stubs awaiting expert input and labeled data. Algorithm for `cung_menh_from_birth` is not implemented and must be validated against the user's chosen phong thủy school (Lạc Việt vs traditional) before any production use.
