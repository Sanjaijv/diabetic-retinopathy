from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import create_app
from app.models.interface import UnavailableModel


def client() -> TestClient:
    return TestClient(create_app(model=UnavailableModel()))


def image_bytes(size=(256, 256), color=(50, 90, 60), fmt="JPEG") -> bytes:
    image = Image.new("RGB", size, color)
    buffer = BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()


def test_health_and_model_info_report_unavailable_model():
    api = client()
    assert api.get("/api/health").json() == {"status": "ok", "model_available": False}
    info = api.get("/api/model-info").json()
    assert info["model_available"] is False
    assert info["supported_classes"] == []


def test_empty_upload_is_rejected():
    response = client().post("/api/analyze", files={"file": ("empty.jpg", b"", "image/jpeg")})
    assert response.status_code == 400


def test_corrupt_upload_is_rejected():
    response = client().post("/api/analyze", files={"file": ("bad.jpg", b"not an image", "image/jpeg")})
    assert response.status_code == 400


def test_unsupported_format_is_rejected():
    response = client().post(
        "/api/analyze", files={"file": ("image.gif", image_bytes(fmt="GIF"), "image/gif")}
    )
    assert response.status_code == 400


def test_valid_upload_returns_explicit_unavailable_result():
    response = client().post(
        "/api/analyze", files={"file": ("retina.jpg", image_bytes(), "image/jpeg")}
    )
    assert response.status_code == 200
    result = response.json()
    assert result["model_available"] is False
    assert result["screening_class"] is None
    assert "unavailable" in result["explanation_message"].lower()


def test_small_dimensions_are_rejected():
    response = client().post(
        "/api/analyze", files={"file": ("small.jpg", image_bytes((32, 32)), "image/jpeg")}
    )
    assert response.status_code == 400
