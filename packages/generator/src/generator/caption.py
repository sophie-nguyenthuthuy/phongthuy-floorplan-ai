"""Social captions for generated layouts — the marketing surface.

Two voices: Facebook (warm, emoji, gia đình) and LinkedIn (proptech, dữ liệu).
Pure functions of the layout — deterministic, no model calls.
"""

from generator.schema import GeneratedLayout

HASHTAGS = "#phongthuy #battrach #nhadep #xaynha #thietkenha #proptech"


def _room_line(layout: GeneratedLayout) -> str:
    icons = {"phong_bep": "🔥", "phong_ngu": "🛏", "phong_tho": "🙏", "phong_khach": "🛋"}
    parts = [
        f"{icons[r.room]} {r.label_vi}: cung {r.quan_he_label_vi}"
        for r in layout.rooms
        if r.room in icons and r.good
    ]
    return " · ".join(parts[:3])


def facebook_caption(layout: GeneratedLayout, url: str, display_name: str | None = None) -> str:
    """Warm, shareable FB caption with the score as the hook."""
    who = display_name or f"gia chủ mệnh {layout.cung_label_vi}"
    return (
        f"🏠✨ Sơ đồ {layout.template_label_vi} chuẩn phong thủy cho {who}\n"
        f"🧭 Cung {layout.cung_label_vi} ({layout.nhom_label_vi}) — "
        f"nhà hướng {layout.huong_nha_label_vi} đón {layout.house_quan_he_label_vi}\n"
        f"📊 Điểm phong thủy: {layout.score_total}/100 — {layout.tier_label_vi}\n"
        f"{_room_line(layout)}\n"
        f"Tạo sơ đồ cho tuổi của bạn (miễn phí, 30 giây) 👉 {url}\n"
        f"{HASHTAGS}"
    )


def linkedin_caption(layout: GeneratedLayout, url: str) -> str:
    """Proptech-flavored LinkedIn caption — data angle, no doom-mongering."""
    return (
        f"Phong thủy Bát Trạch, mã hóa thành dữ liệu kiểm chứng được.\n\n"
        f"Engine của chúng tôi xếp {len(layout.rooms)} không gian của một "
        f"{layout.template_label_vi.lower()} theo bảng Bát Trạch 8×8 truyền thống: "
        f"bếp tọa hung, phòng ngủ tọa cát, cửa chính mở tại cung "
        f"{layout.door.quan_he_label_vi}.\n\n"
        f"Kết quả cho gia chủ cung {layout.cung_label_vi}: "
        f"{layout.score_total}/100 ({layout.tier_label_vi}) — "
        f"tính bằng tri thức dạng YAML có chuyên gia thẩm định, không phải LLM đoán mò.\n\n"
        f"Demo: {url}\n{HASHTAGS}"
    )
