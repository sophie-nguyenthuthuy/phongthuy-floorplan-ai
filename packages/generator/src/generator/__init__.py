"""Phong thủy floor-plan generator — Bát Trạch layout engine, SVG renderer, captions."""

from generator.caption import facebook_caption, linkedin_caption
from generator.engine import generate_layout, load_templates, recommend_huong
from generator.render import plan_svg, share_card_svg
from generator.schema import GeneratedLayout, HouseTemplate

__all__ = [
    "GeneratedLayout",
    "HouseTemplate",
    "facebook_caption",
    "generate_layout",
    "linkedin_caption",
    "load_templates",
    "plan_svg",
    "recommend_huong",
    "share_card_svg",
]
