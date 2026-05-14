# Labeling guide — VN floor plans

This document defines how annotators label floor plans for our dataset. It is the **canonical source of truth** for what counts as a wall, what counts as a room, and how to handle VN-specific cases. If you find an unclear case, propose a rule in PR, don't decide on your own.

## What we label

Every labeled plan produces one `FloorPlan` (see `packages/cv/src/cv/schema.py`):

- **Walls** — line segments with thickness, optional `load_bearing` flag
- **Doors** — point + width + swing direction
- **Rooms** — closed polygons with `RoomType` and `area_m2`
- **North angle** — degrees from image "up"
- **Scale** — metres per pixel, if known

## Wall rules

1. **Exterior walls always count.** They must form a closed polygon. If the exterior is broken in the image (e.g. cropped), reject the plan.
2. **Interior walls count if they fully separate spaces.** A half-height partition that doesn't reach the ceiling does NOT count as a wall — label it as a polygon edge instead (room boundary without a wall).
3. **Load-bearing flag (`load_bearing: true`):** only set when the drawing legend explicitly indicates it (typically thicker line weight or hatching). When unclear, leave false.
4. **Thickness:** record in metres if scale is known, else in pixels. Default 0.1 m if not visible.
5. **Furniture lines are not walls.** Bed/sofa/cabinet outlines must be ignored even when drawn with similar weight to walls.

## Door rules

1. **Position** = the hinge point (or door-mid for sliding doors).
2. **Width** = the actual opening, not the door leaf when shown open.
3. **Swing direction:**
   - `in`: door swings into the labeled room
   - `out`: door swings out of the labeled room
   - `slide`: sliding door
4. **Front door** (cửa chính) must be present; if it can't be identified, reject.
5. **Internal openings without doors** (cased openings, arches) → record as a Door with `width = opening width` and `swing_direction = "slide"` as a convention (it's a permanent opening; downstream consumers can re-interpret).

## Room rules

### Required types (must label if present)

| RoomType         | VN name           | Notes                                            |
|------------------|-------------------|--------------------------------------------------|
| `phong_khach`    | Phòng khách       | Living room                                      |
| `phong_ngu`      | Phòng ngủ         | Bedroom (label every bedroom)                    |
| `phong_bep`      | Phòng bếp         | Kitchen                                          |
| `phong_tam`      | Phòng tắm / WC    | Bathroom — include separate WC                   |
| `phong_an`       | Phòng ăn          | Dining — separate from kitchen if shown          |
| `phong_tho`      | Phòng thờ         | Altar ROOM — see below                           |
| `san_gieng_troi` | Sân giếng trời    | Light well — interior open-air space             |
| `ban_cong`       | Ban công          | Balcony — exterior, with railing                 |
| `hanh_lang`      | Hành lang         | Hallway — only label if ≥ 1 m wide               |
| `cau_thang`      | Cầu thang         | Stairs — polygon includes landing                |

### Special: phong thờ vs ban thờ

- A dedicated room labelled "phòng thờ" → `phong_tho`.
- A shelf/altar **inside another room** (commonly above a wall in phòng khách or kitchen) → not a Room. Record as a `keypoint` annotation (extension, not yet in schema — leave a note in `Annotation.notes`).

Rationale: phong thủy analysis cares about ban thờ position whether or not it has a dedicated room. Future schema versions will add a `KeyPoint` field; until then, log it in notes.

### Special: sân giếng trời

A `san_gieng_troi` is an interior open-air space (light well). It MUST be labeled even though it is "outdoor," because:

- It dictates ventilation and natural light routing
- It is a phong thủy-significant feature in nhà ống

Mark by polygon. Walls bordering a light well are interior walls.

### Special: ban công vs lô gia

- **Ban công**: cantilevered, projects beyond the exterior wall. Label as `ban_cong`.
- **Lô gia**: recessed inside the building footprint, with railing. Also label as `ban_cong` for v0.1 — we may distinguish in v0.2.

## North direction

Critical for phong thủy analysis. Without north, the plan is unusable for our purposes.

1. **Preferred source:** explicit "N" arrow / compass rose on the drawing → set `north_angle_deg` to the angle from image "up" (clockwise positive).
2. **Acceptable fallback:** architect or owner confirms verbally / in writing.
3. **Not acceptable:** guessing from "the front door usually faces…" — reject the plan rather than guess.

## Scale

1. **Preferred:** scale bar on the drawing → compute `scale_m_per_px`.
2. **Acceptable:** a labeled dimension (e.g. "4500" between two walls) → divide by pixel distance.
3. **Not acceptable:** guessing. Leave `scale_m_per_px = null`; the plan can still be used for topology training.

## Quality gates (reviewer checklist)

A plan can move from `annotation` to `reviewed_by` only after:

- [ ] Every room is a closed polygon
- [ ] Polygons do not self-intersect or overlap each other
- [ ] Every interior door connects exactly two rooms or one room + outside
- [ ] Exterior walls form a single closed polygon
- [ ] `north_angle_deg` is set (not null)
- [ ] `RoomType` follows the rules above (no `khong_xac_dinh` unless genuinely unidentifiable)

## When to reject a plan

- Image resolution < 800 px on the shorter side
- Watermark obscures > 5% of the plan area
- Drawing is a 3D render, perspective view, or marketing illustration (not a true plan view)
- Multiple unrelated plans on one image (split first)
- Floor unclear (which floor of a multi-storey is this?) — label each floor separately or reject

## Annotator credit and review

- `Annotation.annotator_id` — your internal annotator handle, stable across sessions
- `Annotation.reviewed_by` — second annotator who passed the checklist above
- `Annotation.notes` — free text for anything weird the rules don't cover; review periodically and turn recurring notes into new rules
