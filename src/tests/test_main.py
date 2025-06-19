import pytest
from fastapi.testclient import TestClient

from webapp.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_app():
    app.dependency_overrides = {}

def test_root():
    """Test root endpoint returns 200 and expected content type."""
    response = client.get("/")
    assert response.status_code == 200, "Root endpoint should return 200"
    assert "text/html" in response.headers["content-type"], "Root should return HTML"
