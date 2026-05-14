import io

from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_upload_returns_id_and_size() -> None:
    payload = b"fake png bytes"
    response = client.post(
        "/floor-plans",
        files={"file": ("plan.png", io.BytesIO(payload), "image/png")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "plan.png"
    assert body["size_bytes"] == len(payload)
    assert len(body["id"]) == 32
