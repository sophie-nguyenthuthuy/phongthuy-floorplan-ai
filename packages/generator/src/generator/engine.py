"""Bát Trạch layout engine.

Given a cung mệnh, a house template, and an (optional) house direction, assign
rooms to template slots so the layout maximizes the weighted Bát Trạch score:
cửa chính and phòng ngủ on auspicious sectors, bếp and WC pressing down on
inauspicious ones ("tọa hung hướng cát").

Geometry convention (see templates.yaml): meters, origin at the back-left
corner, the front edge (main door) at y = depth_m. If the house faces compass
bearing θ_H, a plan vector (dx, dy) from the house center points at compass
bearing (θ_H − atan2(dx, dy)) — derived from the front normal (0, +1) mapping
to θ_H in a top-down view.
"""

import math
from functools import lru_cache
from itertools import permutations
from pathlib import Path
from typing import Any

import yaml
from ontology import Ontology, load_ontology
from ontology.models import BatTrachRelation, RoomRule

from generator.labels import ELEMENT_VI, NHOM_VI, QUAN_HE_VI, TIER_VI
from generator.schema import (
    DoorPlacement,
    DoorPosition,
    GeneratedLayout,
    HouseTemplate,
    PlacedRoom,
    SectorInfo,
    Slot,
    TierKey,
)

_HUONG_ORDER = ["bac", "dong_bac", "dong", "dong_nam", "nam", "tay_nam", "tay", "tay_bac"]
_BEARING: dict[str, float] = {h: i * 45.0 for i, h in enumerate(_HUONG_ORDER)}

# Score awarded when a room lands on its i-th preferred du niên (see room_rules.yaml).
_PREFER_BONUS = (0.15, 0.10, 0.05, 0.0)


def _templates_path() -> Path:
    return Path(__file__).parent / "data" / "templates.yaml"


@lru_cache(maxsize=1)
def load_templates() -> dict[str, HouseTemplate]:
    """Load house templates, keyed by template key. Cached."""
    with _templates_path().open("r", encoding="utf-8") as f:
        raw: Any = yaml.safe_load(f)
    if not isinstance(raw, list):
        raise ValueError("templates.yaml must contain a list of templates")
    templates = [HouseTemplate(**x) for x in raw]
    for t in templates:
        free = [s for s in t.slots if s.fixed is None]
        if len(free) != len(t.rooms):
            raise ValueError(f"template {t.key}: {len(t.rooms)} rooms but {len(free)} free slots")
    return {t.key: t for t in templates}


def bearing_of(huong: str) -> float:
    """Center compass bearing of a direction key (Bắc = 0°, clockwise)."""
    return _BEARING[huong]


def sector_for_bearing(deg: float) -> str:
    """Map a compass bearing to one of the 8 direction keys (45° sectors)."""
    idx = round((deg % 360) / 45.0) % 8
    return _HUONG_ORDER[idx]


def sector_of_point(
    px: float, py: float, cx: float, cy: float, theta_house: float
) -> tuple[str, float]:
    """Sector (direction key) and bearing of plan point (px, py) seen from the center."""
    dx, dy = px - cx, py - cy
    if dx == 0 and dy == 0:
        return sector_for_bearing(theta_house), theta_house
    bearing = (theta_house - math.degrees(math.atan2(dx, dy))) % 360
    return sector_for_bearing(bearing), bearing


def _relations_for_cung(cung: str, ontology: Ontology) -> dict[str, BatTrachRelation]:
    return {r.huong: r for r in ontology.bat_trach if r.cung == cung}


def room_score(rule: RoomRule, relation: BatTrachRelation) -> float:
    """Score 0..1 of a room sitting on a sector, per its placement rule.

    Auspicious-seeking rooms scale with diem; "tọa hung" rooms (bếp, WC) score
    the inverse — pressing the worst sector is the best move. A graded bonus
    rewards landing on the rule's preferred du niên.
    """
    if rule.placement == "cat":
        base = (relation.diem + 4) / 8
    elif rule.placement == "hung":
        base = (4 - relation.diem) / 8
    else:  # "any" — mildly prefers auspicious
        base = 0.6 + (relation.diem / 4) * 0.1
    bonus = 0.0
    if relation.quan_he in rule.prefer_quan_he:
        bonus = _PREFER_BONUS[min(rule.prefer_quan_he.index(relation.quan_he), 3)]
    return min(1.0, max(0.0, base + bonus))


def recommend_huong(cung: str, ontology: Ontology) -> str:
    """Best house direction for a cung mệnh — its Sinh Khí direction."""
    relations = _relations_for_cung(cung, ontology)
    best = max(relations.values(), key=lambda r: r.diem)
    return best.huong


def _tier(score: int) -> tuple[TierKey, str]:
    key: TierKey
    if score >= 85:
        key = "dai_cat"
    elif score >= 70:
        key = "cat"
    elif score >= 55:
        key = "binh_hoa"
    else:
        key = "can_hoa_giai"
    return key, TIER_VI[key]


def _door_options(template: HouseTemplate) -> list[tuple[DoorPosition, float]]:
    """Door midpoint x for left/center/right thirds of the front edge."""
    w = template.width_m
    return [("trai", w / 6), ("giua", w / 2), ("phai", 5 * w / 6)]


def _assignments(rooms: list[str], slots: list[Slot]) -> list[dict[str, str]]:
    """All valid injective room→slot assignments honoring slot.allowed.

    Templates keep free-slot counts ≤ 6, so brute force (≤ 720 permutations)
    is instant. Duplicate room keys produce equivalent assignments; dedupe by
    the (slot → room) mapping.
    """
    seen: set[tuple[tuple[str, str], ...]] = set()
    valid: list[dict[str, str]] = []
    for perm in permutations(range(len(rooms))):
        mapping = {slots[i].id: rooms[perm[i]] for i in range(len(rooms))}
        key = tuple(sorted(mapping.items()))
        if key in seen:
            continue
        seen.add(key)
        if all(mapping[s.id] in s.allowed for s in slots):
            valid.append(mapping)
    return valid


def _sector_infos(relations: dict[str, BatTrachRelation], onto: Ontology) -> list[SectorInfo]:
    return [
        SectorInfo(
            huong=h,
            label_vi=onto.huong[h].label_vi,
            quan_he=relations[h].quan_he,
            quan_he_label_vi=QUAN_HE_VI[relations[h].quan_he],
            diem=relations[h].diem,
            bearing_deg=_BEARING[h],
        )
        for h in _HUONG_ORDER
    ]


def _highlights(
    placed: list[PlacedRoom],
    door_score: float,
    door_rel: BatTrachRelation,
    door_sector: str,
    onto: Ontology,
) -> list[str]:
    highlights = [
        f"{r.label_vi} tọa cung {r.quan_he_label_vi} ({r.huong_label_vi})"
        for r in placed
        if r.score >= 0.8 and r.room != "san_gieng_troi"
    ]
    if door_score >= 0.8:
        highlights.insert(
            0,
            f"Cửa chính mở tại cung {QUAN_HE_VI[door_rel.quan_he]}"
            f" ({onto.huong[door_sector].label_vi})",
        )
    return highlights


def _pick_door(
    template: HouseTemplate,
    relations: dict[str, BatTrachRelation],
    theta: float,
    door_rule: RoomRule,
) -> tuple[float, DoorPosition, float, str]:
    """Best (score, position, midpoint_x, sector) among the front-edge thirds."""
    cx, cy = template.width_m / 2, template.depth_m / 2
    best: tuple[float, DoorPosition, float, str] | None = None
    for position, dx in _door_options(template):
        sector, _ = sector_of_point(dx, template.depth_m, cx, cy, theta)
        score = room_score(door_rule, relations[sector])
        if best is None or score > best[0]:
            best = (score, position, dx, sector)
    assert best is not None
    return best


def generate_layout(
    cung: str,
    template_key: str,
    huong_nha: str | None = None,
    ontology: Ontology | None = None,
) -> GeneratedLayout:
    """Generate the optimal layout for a cung mệnh on a template.

    If huong_nha is None the engine recommends the cung's Sinh Khí direction.
    Deterministic: same inputs always produce the same layout.
    """
    onto = ontology or load_ontology()
    templates = load_templates()
    if template_key not in templates:
        raise KeyError(f"unknown template: {template_key}")
    template = templates[template_key]
    if cung not in onto.cung_menh:
        raise KeyError(f"unknown cung mệnh: {cung}")
    cung_info = onto.cung_menh[cung]

    huong_recommended = huong_nha is None
    huong = huong_nha or recommend_huong(cung, onto)
    if huong not in onto.huong:
        raise KeyError(f"unknown hướng: {huong}")
    theta = bearing_of(huong)

    relations = _relations_for_cung(cung, onto)

    # Door: pick the front-edge third with the best cua_chinh score.
    door_rule = onto.room_rules["cua_chinh"]
    door_w = min(1.4, template.width_m / 4)
    door_score, door_pos, door_x, door_sector = _pick_door(template, relations, theta, door_rule)
    door_rel = relations[door_sector]

    # Rooms: brute-force the best assignment of rooms to free slots.
    free_slots = [s for s in template.slots if s.fixed is None]
    fixed_slots = [s for s in template.slots if s.fixed is not None]
    slot_sector = {
        s.id: sector_of_point(
            s.x + s.w / 2, s.y + s.h / 2, template.width_m / 2, template.depth_m / 2, theta
        )[0]
        for s in template.slots
    }

    def assignment_score(mapping: dict[str, str]) -> float:
        total, weight = 0.0, 0.0
        for slot_id, room in mapping.items():
            rule = onto.room_rules[room]
            total += rule.weight * room_score(rule, relations[slot_sector[slot_id]])
            weight += rule.weight
        return total / weight if weight else 0.0

    candidates = _assignments(template.rooms, free_slots)
    if not candidates:
        raise ValueError(f"template {template_key} has no valid room assignment")
    best_mapping = max(candidates, key=assignment_score)

    # Build placed rooms (assigned + fixed), score, and advice.
    slot_by_id = {s.id: s for s in template.slots}
    placed: list[PlacedRoom] = []
    total_w, total_s = float(door_rule.weight), door_score * door_rule.weight
    for slot_id, room in list(best_mapping.items()) + [
        (s.id, s.fixed) for s in fixed_slots if s.fixed is not None
    ]:
        slot = slot_by_id[slot_id]
        rule = onto.room_rules[room]
        rel = relations[slot_sector[slot_id]]
        score = room_score(rule, rel)
        good = score >= 0.6
        if slot.fixed is None:
            total_w += rule.weight
            total_s += score * rule.weight
        placed.append(
            PlacedRoom(
                room=room,
                label_vi=rule.label_vi,
                slot_id=slot_id,
                x=slot.x,
                y=slot.y,
                w=slot.w,
                h=slot.h,
                huong=rel.huong,
                huong_label_vi=onto.huong[rel.huong].label_vi,
                quan_he=rel.quan_he,
                quan_he_label_vi=QUAN_HE_VI[rel.quan_he],
                diem=rel.diem,
                score=round(score, 3),
                good=good,
                advice_vi=rule.note_vi if good else rule.fix_vi,
            )
        )
    placed.sort(key=lambda r: -r.score)

    score_total = round(100 * total_s / total_w)
    tier_key, tier_label = _tier(score_total)

    house_rel = relations[huong]
    sectors = _sector_infos(relations, onto)
    highlights = _highlights(placed, door_score, door_rel, door_sector, onto)
    warnings = [r.advice_vi for r in placed if r.score < 0.5]

    return GeneratedLayout(
        template_key=template.key,
        template_label_vi=template.label_vi,
        width_m=template.width_m,
        depth_m=template.depth_m,
        cung_menh=cung,
        cung_label_vi=cung_info.label_vi,
        nhom=cung_info.nhom,
        nhom_label_vi=NHOM_VI[cung_info.nhom],
        element=cung_info.element,
        element_label_vi=ELEMENT_VI[cung_info.element],
        huong_nha=huong,
        huong_nha_label_vi=onto.huong[huong].label_vi,
        huong_recommended=huong_recommended,
        house_quan_he=house_rel.quan_he,
        house_quan_he_label_vi=QUAN_HE_VI[house_rel.quan_he],
        house_diem=house_rel.diem,
        door=DoorPlacement(
            x=door_x - door_w / 2,
            y=template.depth_m,
            width_m=door_w,
            position=door_pos,
            huong=door_sector,
            huong_label_vi=onto.huong[door_sector].label_vi,
            quan_he=door_rel.quan_he,
            quan_he_label_vi=QUAN_HE_VI[door_rel.quan_he],
            diem=door_rel.diem,
            score=round(door_score, 3),
        ),
        rooms=placed,
        sectors=sectors,
        score_total=score_total,
        tier=tier_key,
        tier_label_vi=tier_label,
        highlights_vi=highlights[:4],
        warnings_vi=warnings,
        extra_advice_vi=template.extra_advice_vi,
    )
