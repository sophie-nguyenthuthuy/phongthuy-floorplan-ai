"""Generator endpoint tests."""

from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

PAYLOAD = {
    "nam_sinh": 1990,
    "thang_sinh": 6,
    "ngay_sinh": 15,
    "gioi_tinh": "nam",
    "template": "nha_ong_5x20",
}


def test_list_templates() -> None:
    r = client.get("/generator/templates")
    assert r.status_code == 200
    keys = {t["key"] for t in r.json()}
    assert {"nha_ong_5x20", "can_ho_65", "nha_vuon_10x10"} <= keys


def test_create_layout_recommends_huong() -> None:
    r = client.post("/generator/layouts", json=PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    layout = body["layout"]
    assert layout["huong_recommended"] is True
    assert layout["cung_menh"] == "cung_ly"  # nam 1990 (sau Lập Xuân) → Ly
    assert 0 <= layout["score_total"] <= 100
    assert "plan.svg" in body["plan_svg_url"]
    assert "share-card.svg" in body["share_card_svg_url"]
    assert str(layout["score_total"]) in body["caption_facebook"]


def test_svg_urls_roundtrip() -> None:
    body = client.post("/generator/layouts", json={**PAYLOAD, "display_name": "Anh Tuấn"}).json()
    for url in (body["plan_svg_url"], body["share_card_svg_url"]):
        r = client.get(url)
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("image/svg+xml")
        assert r.text.startswith("<svg")


def test_explicit_huong_respected() -> None:
    r = client.post("/generator/layouts", json={**PAYLOAD, "huong_nha": "tay"})
    layout = r.json()["layout"]
    assert layout["huong_nha"] == "tay"
    assert layout["huong_recommended"] is False


def test_invalid_inputs_rejected() -> None:
    bad = [
        {**PAYLOAD, "ngay_sinh": 31, "thang_sinh": 2},
        {**PAYLOAD, "template": "nope"},
        {**PAYLOAD, "huong_nha": "nope"},
    ]
    for payload in bad:
        assert client.post("/generator/layouts", json=payload).status_code == 422
