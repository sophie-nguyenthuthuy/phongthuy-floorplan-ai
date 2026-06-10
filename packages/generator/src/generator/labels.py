"""Vietnamese display labels for ontology keys (presentation layer, not knowledge)."""

from ontology.models import QuanHe

QUAN_HE_VI: dict[QuanHe, str] = {
    "sinh_khi": "Sinh Khí",
    "thien_y": "Thiên Y",
    "dien_nien": "Diên Niên",
    "phuc_vi": "Phục Vị",
    "hoa_hai": "Họa Hại",
    "luc_sat": "Lục Sát",
    "ngu_quy": "Ngũ Quỷ",
    "tuyet_menh": "Tuyệt Mệnh",
}

NHOM_VI: dict[str, str] = {
    "dong_tu_menh": "Đông tứ mệnh",
    "tay_tu_menh": "Tây tứ mệnh",
}

ELEMENT_VI: dict[str, str] = {
    "kim": "Kim",
    "moc": "Mộc",
    "thuy": "Thủy",
    "hoa": "Hỏa",
    "tho": "Thổ",
}

ROOM_ICON: dict[str, str] = {
    "cua_chinh": "🚪",
    "phong_khach": "🛋",
    "phong_bep": "🔥",
    "phong_ngu": "🛏",
    "phong_tam": "🚿",
    "phong_tho": "🙏",
    "phong_an": "🍚",
    "cau_thang": "🪜",
    "san_gieng_troi": "🌿",
}

TIER_VI: dict[str, str] = {
    "dai_cat": "Đại Cát",
    "cat": "Cát",
    "binh_hoa": "Bình Hòa",
    "can_hoa_giai": "Cần Hóa Giải",
}
