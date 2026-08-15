"""Real FastAPI-to-PostgreSQL health endpoint integration verification."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from flowlens.api.app import create_app
from flowlens.config import Settings

pytestmark = pytest.mark.integration


def test_health_endpoint_uses_real_postgresql() -> None:
    try:
        settings = Settings()
    except ValidationError:
        pytest.skip("FLOWLENS_DATABASE_URL is required for API integration tests")

    with TestClient(create_app(settings)) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "flowlens-api",
        "database": "ok",
    }
