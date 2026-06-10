"""SVG renderers — annotated floor plan + 1200×630 share card (FB/LinkedIn OG ratio).

Pure string generation, no drawing libraries. Sector arcs are sampled as
polylines to avoid SVG sweep-flag pitfalls. All user-provided text is escaped.
"""

import math
from xml.sax.saxutils import escape

from generator.labels import ROOM_ICON
from generator.schema import GeneratedLayout

# Palette — dark, gold-accented, consistent with the demo UI.
BG = "#0b0f14"
PANEL = "#11161d"
GOLD = "#d4af37"
TEXT = "#ece5d3"
MUTED = "#8b8676"
GOOD_FILL = "rgba(52,211,153,0.14)"
GOOD_STROKE = "#34d399"
BAD_FILL = "rgba(239,68,68,0.14)"
BAD_STROKE = "#ef4444"

QUAN_HE_COLOR: dict[str, str] = {
    "sinh_khi": "#34d399",
    "thien_y": "#6ee7b7",
    "dien_nien": "#a3e635",
    "phuc_vi": "#fbbf24",
    "hoa_hai": "#fb923c",
    "luc_sat": "#f87171",
    "ngu_quy": "#ef4444",
    "tuyet_menh": "#b91c1c",
}


def _dir(theta_deg: float, bearing_deg: float) -> tuple[float, float]:
    """Unit screen vector (x right, y down) toward a compass bearing.

    The plan renders with the front edge at the bottom; the front normal
    (0, +1 on screen) points at house bearing θ_H.
    """
    d = math.radians(theta_deg - bearing_deg)
    return math.sin(d), math.cos(d)


def _annular_sector(
    cx: float, cy: float, r_in: float, r_out: float, theta: float, b1: float, b2: float
) -> str:
    """Polygon points for an annular sector between bearings b1..b2 (sampled)."""
    steps = 12
    pts: list[str] = []
    for i in range(steps + 1):
        b = b1 + (b2 - b1) * i / steps
        x, y = _dir(theta, b)
        pts.append(f"{cx + r_out * x:.1f},{cy + r_out * y:.1f}")
    for i in range(steps, -1, -1):
        b = b1 + (b2 - b1) * i / steps
        x, y = _dir(theta, b)
        pts.append(f"{cx + r_in * x:.1f},{cy + r_in * y:.1f}")
    return " ".join(pts)


def _plan_group(
    layout: GeneratedLayout, max_px: float, with_ring: bool = True
) -> tuple[str, float]:
    """Floor plan as a <g> centered on (0,0). Returns (markup, half-extent px)."""
    theta = {s.huong: s.bearing_deg for s in layout.sectors}[layout.huong_nha]
    w_m, d_m = layout.width_m, layout.depth_m
    ring_pad = 40.0 if with_ring else 0.0
    label_pad = 58.0 if with_ring else 8.0  # room for side-anchored two-line labels
    half_diag = math.hypot(w_m / 2, d_m / 2)

    # Fit house + ring + labels inside max_px.
    scale = (max_px / 2 - ring_pad - label_pad) / half_diag
    hw, hd = w_m * scale, d_m * scale
    ox, oy = -hw / 2, -hd / 2  # house top-left in group coords
    r_in = half_diag * scale + 10
    r_out = r_in + 26
    half_extent = r_out + label_pad if with_ring else max(hw, hd) / 2 + label_pad

    parts: list[str] = []

    if with_ring:
        for s in layout.sectors:
            color = QUAN_HE_COLOR[s.quan_he]
            pts = _annular_sector(
                0, 0, r_in, r_out, theta, s.bearing_deg - 22.5, s.bearing_deg + 22.5
            )
            parts.append(f'<polygon points="{pts}" fill="{color}" opacity="0.22"/>')
            # Two-line label outside the ring (direction + du niên), anchored
            # away from the ring so horizontal-extreme labels never collide.
            x, y = _dir(theta, s.bearing_deg)
            lx, ly = x * (r_out + 8), y * (r_out + 8)
            anchor = "start" if x > 0.35 else ("end" if x < -0.35 else "middle")
            base = ly - 12 if y < -0.35 else ly + 4
            parts.append(
                f'<text x="{lx:.1f}" y="{base:.1f}" font-size="11" font-weight="700"'
                f' fill="{color}" text-anchor="{anchor}">{s.label_vi}</text>'
            )
            parts.append(
                f'<text x="{lx:.1f}" y="{base + 11:.1f}" font-size="8" fill="{TEXT}"'
                f' opacity="0.75" text-anchor="{anchor}">{s.quan_he_label_vi}</text>'
            )

    # House shell.
    parts.append(
        f'<rect x="{ox:.1f}" y="{oy:.1f}" width="{hw:.1f}" height="{hd:.1f}"'
        f' fill="{PANEL}" stroke="{GOLD}" stroke-width="2.5" rx="3"/>'
    )

    # Rooms.
    for r in layout.rooms:
        fill, stroke = (GOOD_FILL, GOOD_STROKE) if r.good else (BAD_FILL, BAD_STROKE)
        if r.room == "san_gieng_troi":
            fill, stroke = "rgba(212,175,55,0.10)", GOLD
        x, y = ox + r.x * scale, oy + r.y * scale
        rw, rh = r.w * scale, r.h * scale
        cx, cy = x + rw / 2, y + rh / 2
        parts.append(
            f'<rect x="{x + 1.5:.1f}" y="{y + 1.5:.1f}" width="{rw - 3:.1f}" height="{rh - 3:.1f}"'
            f' fill="{fill}" stroke="{stroke}" stroke-width="1.2" stroke-dasharray="0" rx="2"/>'
        )
        icon = ROOM_ICON.get(r.room, "")
        big = rh >= 46 and rw >= 70
        name_fs = 11 if big else 8.5
        parts.append(
            f'<text x="{cx:.1f}" y="{cy - (5 if big else 3):.1f}" font-size="{name_fs}"'
            f' font-weight="700" fill="{TEXT}" text-anchor="middle">{icon} {r.label_vi}</text>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{cy + (10 if big else 7):.1f}" font-size="{8 if big else 6.5}"'
            f' fill="{QUAN_HE_COLOR[r.quan_he]}" text-anchor="middle">'
            f"{r.huong_label_vi} · {r.quan_he_label_vi}</text>"
        )

    # Main door on the front edge (bottom).
    door = layout.door
    dx1, dx2 = ox + door.x * scale, ox + (door.x + door.width_m) * scale
    fy = oy + hd
    parts.append(
        f'<line x1="{dx1:.1f}" y1="{fy:.1f}" x2="{dx2:.1f}" y2="{fy:.1f}"'
        f' stroke="{GOLD}" stroke-width="6" stroke-linecap="round"/>'
    )
    mx = (dx1 + dx2) / 2
    parts.append(
        f'<path d="M {mx:.1f} {fy + 4:.1f} l -4 7 h 8 z" fill="{GOLD}"'
        f' transform="rotate(180 {mx:.1f} {fy + 7.5:.1f})"/>'
    )
    parts.append(
        f'<text x="{mx:.1f}" y="{fy + 21:.1f}" font-size="9" font-weight="700" fill="{GOLD}"'
        f' text-anchor="middle">Cửa chính · {door.huong_label_vi} ({door.quan_he_label_vi})</text>'
    )

    return "".join(parts), half_extent


def plan_svg(layout: GeneratedLayout, size_px: int = 720) -> str:
    """Standalone annotated floor plan with the Bát Trạch sector ring."""
    group, half = _plan_group(layout, max_px=size_px - 24, with_ring=True)
    side = (half + 12) * 2
    c = side / 2
    header = (
        f'<text x="{c:.0f}" y="24" font-size="15" font-weight="800" fill="{TEXT}"'
        f' text-anchor="middle">{layout.template_label_vi} · Cung {layout.cung_label_vi}'
        f" · Hướng {layout.huong_nha_label_vi}</text>"
    )
    footer = (
        f'<text x="{c:.0f}" y="{side + 32:.0f}" font-size="12" fill="{MUTED}" text-anchor="middle">'
        f"Điểm phong thủy {layout.score_total}/100 · {layout.tier_label_vi}"
        f" · Bát Trạch Minh Cảnh</text>"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {side:.0f} {side + 44:.0f}"'
        f' font-family="-apple-system, Segoe UI, Roboto, sans-serif">'
        f'<rect width="100%" height="100%" fill="{BG}"/>'
        f"{header}"
        f'<g transform="translate({c:.1f},{c + 22:.1f})">{group}</g>'
        f"{footer}</svg>"
    )


def _donut(cx: float, cy: float, r: float, score: int) -> str:
    circ = 2 * math.pi * r
    on = circ * score / 100
    color = GOOD_STROKE if score >= 70 else (GOLD if score >= 55 else BAD_STROKE)
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#222a35" stroke-width="14"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="14"'
        f' stroke-linecap="round" stroke-dasharray="{on:.1f} {circ - on:.1f}"'
        f' transform="rotate(-90 {cx} {cy})"/>'
        f'<text x="{cx}" y="{cy + 2}" font-size="56" font-weight="900" fill="{TEXT}"'
        f' text-anchor="middle" dominant-baseline="middle">{score}</text>'
        f'<text x="{cx}" y="{cy + 38}" font-size="15" fill="{MUTED}"'
        ' text-anchor="middle">/100</text>'
    )


def share_card_svg(
    layout: GeneratedLayout,
    url: str = "phongthuy-floorplan.ai",
    display_name: str | None = None,
) -> str:
    """1200×630 OG-ratio share card — the asset that travels on FB/LinkedIn."""
    name = escape(display_name) if display_name else f"Gia chủ cung {layout.cung_label_vi}"
    plan_group, _ = _plan_group(layout, max_px=470, with_ring=True)

    hl: list[str] = []
    for i, h in enumerate(layout.highlights_vi[:3]):
        hl.append(
            f'<text x="620" y="{356 + i * 34}" font-size="17" fill="{TEXT}">'
            f'<tspan fill="{GOOD_STROKE}" font-weight="800">✓</tspan>  {escape(h)}</text>'
        )

    tier_color = (
        GOOD_STROKE
        if layout.score_total >= 70
        else (GOLD if layout.score_total >= 55 else BAD_STROKE)
    )

    tier_w = 34 + 17 * len(layout.tier_label_vi)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630"',
        ' font-family="-apple-system, Segoe UI, Roboto, sans-serif">',
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">',
        f'<stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="#161007"/>',
        "</linearGradient></defs>",
        '<rect width="1200" height="630" fill="url(#bg)"/>',
        f'<circle cx="1130" cy="80" r="180" fill="none" stroke="{GOLD}"'
        ' stroke-width="1" opacity="0.15"/>',
        f'<circle cx="1130" cy="80" r="140" fill="none" stroke="{GOLD}"'
        ' stroke-width="1" opacity="0.12"/>',
        # Left: plan.
        f'<g transform="translate(300,318)">{plan_group}</g>',
        # Right: headline + score.
        f'<text x="620" y="78" font-size="30" font-weight="900" fill="{TEXT}">'
        "Sơ đồ phong thủy của bạn</text>",
        f'<text x="620" y="112" font-size="19" fill="{MUTED}">{name} · {layout.nhom_label_vi}'
        f" · Mệnh {layout.element_label_vi}</text>",
        _donut(700, 220, 70, layout.score_total),
        f'<rect x="800" y="178" rx="17" width="{tier_w}" height="34" fill="none"'
        f' stroke="{tier_color}" stroke-width="2"/>',
        f'<text x="{800 + tier_w / 2}" y="200" font-size="19" font-weight="800"'
        f' fill="{tier_color}" text-anchor="middle">{layout.tier_label_vi}</text>',
        f'<text x="800" y="244" font-size="17" fill="{TEXT}">Nhà hướng'
        f' <tspan font-weight="800" fill="{GOLD}">{layout.huong_nha_label_vi}</tspan>'
        f' đón <tspan font-weight="800">{layout.house_quan_he_label_vi}</tspan></text>',
        f'<text x="620" y="318" font-size="20" font-weight="800" fill="{GOLD}">'
        "Điểm sáng Bát Trạch</text>",
        "".join(hl),
        # Footer brand bar.
        '<rect x="0" y="555" width="1200" height="75" fill="#0a0d11"/>',
        f'<text x="60" y="600" font-size="22" font-weight="900" fill="{GOLD}">'
        "🧭 Phong Thủy AI</text>",
        f'<text x="1140" y="600" font-size="18" fill="{TEXT}" text-anchor="end">'
        f'Tạo sơ đồ cho tuổi của bạn — miễn phí 30 giây · <tspan fill="{GOLD}"'
        f' font-weight="800">{escape(url)}</tspan></text>',
        "</svg>",
    ]
    return "".join(parts)
