"""Renderer + caption tests — valid XML, expected content, escaping."""

import xml.etree.ElementTree as ET

from generator.caption import facebook_caption, linkedin_caption
from generator.engine import generate_layout
from generator.render import plan_svg, share_card_svg

LAYOUT = generate_layout("cung_kham", "nha_ong_5x20")


def test_plan_svg_is_valid_xml_with_rooms_and_ring() -> None:
    svg = plan_svg(LAYOUT)
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    assert "Cửa chính" in svg
    assert "Bếp" in svg
    # Sector ring labels — all 8 directions present.
    for label in ("Bắc", "Nam", "Đông", "Tây"):
        assert label in svg
    assert f"{LAYOUT.score_total}/100" in svg


def test_share_card_is_valid_xml_og_ratio() -> None:
    card = share_card_svg(LAYOUT, display_name="Nhà chị Hằng")
    root = ET.fromstring(card)
    assert 'viewBox="0 0 1200 630"' in card
    assert "Nhà chị Hằng" in card
    assert str(LAYOUT.score_total) in card
    assert root is not None


def test_share_card_escapes_user_text() -> None:
    card = share_card_svg(LAYOUT, display_name='<script>"x"&</script>')
    assert "<script>" not in card
    assert "&lt;script&gt;" in card
    ET.fromstring(card)  # still valid XML


def test_captions_mention_score_and_url() -> None:
    fb = facebook_caption(LAYOUT, "https://x.vn/g", display_name="Anh Ba")
    li = linkedin_caption(LAYOUT, "https://x.vn/g")
    for cap in (fb, li):
        assert str(LAYOUT.score_total) in cap
        assert "https://x.vn/g" in cap
        assert "#phongthuy" in cap
    assert "Anh Ba" in fb


def test_caption_only_brags_about_good_rooms() -> None:
    fb = facebook_caption(LAYOUT, "u")
    for room in LAYOUT.rooms:
        if not room.good and f"{room.label_vi}: cung" in fb:
            raise AssertionError(f"caption khoe phòng chưa đạt: {room.label_vi}")
