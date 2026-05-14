from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_cung_menh_returns_full_record() -> None:
    response = client.post(
        "/analyses/cung-menh",
        json={"nam_sinh": 1990, "thang_sinh": 6, "ngay_sinh": 15, "gioi_tinh": "nam"},
    )
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["cung_menh"] == "cung_ly"
    assert body["label_vi"] == "Ly"
    assert body["element"] == "hoa"
    assert body["nhom"] == "dong_tu_menh"
    assert body["huong_chinh"] == "nam"

    # Ly has 4 good + 4 bad directions (phuc_vi counts as good with +1).
    assert len(body["huong_tot"]) == 4
    assert len(body["huong_xau"]) == 4

    # huong_tot must be sorted by descending diem
    diems = [h["diem"] for h in body["huong_tot"]]
    assert diems == sorted(diems, reverse=True)
    assert diems[0] == 4  # sinh_khi


def test_january_birth_uses_previous_phong_thuy_year() -> None:
    # 1990 male = Ly; born Jan 15 1990 → counted as 1989 → Khảm
    response = client.post(
        "/analyses/cung-menh",
        json={"nam_sinh": 1990, "thang_sinh": 1, "ngay_sinh": 15, "gioi_tinh": "nam"},
    )
    assert response.json()["cung_menh"] == "cung_kham"


def test_invalid_date_returns_422() -> None:
    response = client.post(
        "/analyses/cung-menh",
        json={"nam_sinh": 1990, "thang_sinh": 2, "ngay_sinh": 30, "gioi_tinh": "nam"},
    )
    assert response.status_code == 422


def test_invalid_gender_returns_422() -> None:
    response = client.post(
        "/analyses/cung-menh",
        json={"nam_sinh": 1990, "thang_sinh": 6, "ngay_sinh": 15, "gioi_tinh": "other"},
    )
    assert response.status_code == 422
