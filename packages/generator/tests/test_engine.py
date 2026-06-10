"""Layout engine tests — rule compliance, determinism, geometry."""

import pytest
from generator.engine import (
    generate_layout,
    load_templates,
    recommend_huong,
    sector_of_point,
)
from ontology import load_ontology

ONTO = load_ontology()
TEMPLATE_KEYS = list(load_templates())
CUNG_KEYS = list(ONTO.cung_menh)


def test_templates_load_and_are_consistent() -> None:
    templates = load_templates()
    assert len(templates) >= 3
    for t in templates.values():
        free = [s for s in t.slots if s.fixed is None]
        assert len(free) == len(t.rooms)
        for room in t.rooms:
            assert room in ONTO.room_rules


def test_sector_geometry_front_door_matches_house_direction() -> None:
    # A door centered on the front edge always sits in the house-facing sector.
    sector, _ = sector_of_point(2.5, 20, 2.5, 10, 90.0)  # facing Đông
    assert sector == "dong"
    # Back of the house is the opposite sector.
    sector, _ = sector_of_point(2.5, 0, 2.5, 10, 90.0)
    assert sector == "tay"


def test_sector_geometry_left_right() -> None:
    # Front faces South (180°): viewed from above with North at the top of the
    # plan, plan-right is East and plan-left is West.
    assert sector_of_point(10, 5, 5, 5, 180.0)[0] == "dong"
    assert sector_of_point(0, 5, 5, 5, 180.0)[0] == "tay"


def test_recommend_huong_is_sinh_khi() -> None:
    for cung in CUNG_KEYS:
        huong = recommend_huong(cung, ONTO)
        rel = next(r for r in ONTO.bat_trach if r.cung == cung and r.huong == huong)
        assert rel.quan_he == "sinh_khi"


@pytest.mark.parametrize("template_key", TEMPLATE_KEYS)
@pytest.mark.parametrize("cung", CUNG_KEYS)
def test_generate_all_cung_all_templates(cung: str, template_key: str) -> None:
    layout = generate_layout(cung, template_key)
    assert 0 <= layout.score_total <= 100
    assert layout.huong_recommended
    # Recommended direction means the door must land on an auspicious sector.
    assert layout.door.diem > 0
    # Every assigned room respects its slot's allowed list.
    template = load_templates()[template_key]
    slot_allowed = {s.id: s.allowed for s in template.slots if s.fixed is None}
    for room in layout.rooms:
        if room.slot_id in slot_allowed:
            assert room.room in slot_allowed[room.slot_id]


def test_determinism() -> None:
    a = generate_layout("cung_kham", "nha_ong_5x20", "bac")
    b = generate_layout("cung_kham", "nha_ong_5x20", "bac")
    assert a == b


def test_optimizer_beats_or_ties_every_other_assignment() -> None:
    """The chosen assignment must be the argmax over all valid permutations."""
    from generator.engine import _assignments, _relations_for_cung, room_score

    cung, template_key, huong = "cung_ly", "nha_vuon_10x10", "dong"
    layout = generate_layout(cung, template_key, huong)
    template = load_templates()[template_key]
    relations = _relations_for_cung(cung, ONTO)
    cx, cy = template.width_m / 2, template.depth_m / 2
    free = [s for s in template.slots if s.fixed is None]

    def score_of(mapping: dict[str, str]) -> float:
        total, weight = 0.0, 0.0
        for slot_id, room in mapping.items():
            slot = next(s for s in free if s.id == slot_id)
            sector, _ = sector_of_point(slot.x + slot.w / 2, slot.y + slot.h / 2, cx, cy, 90.0)
            rule = ONTO.room_rules[room]
            total += rule.weight * room_score(rule, relations[sector])
            weight += rule.weight
        return total / weight

    chosen = {r.slot_id: r.room for r in layout.rooms if r.room != "san_gieng_troi"}
    best = max(score_of(m) for m in _assignments(template.rooms, free))
    assert score_of(chosen) == pytest.approx(best)


def test_bad_inputs_raise() -> None:
    with pytest.raises(KeyError):
        generate_layout("cung_ly", "biet_thu_999")
    with pytest.raises(KeyError):
        generate_layout("cung_xyz", "nha_ong_5x20")
    with pytest.raises(KeyError):
        generate_layout("cung_ly", "nha_ong_5x20", "huong_la")
