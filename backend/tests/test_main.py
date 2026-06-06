import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

def test_health_check(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_lifespan():
    from app.main import lifespan
    from fastapi import FastAPI
    app_mock = MagicMock(spec=FastAPI)
    
    with patch("app.main.Base.metadata.create_all") as mock_create_all:
        async with lifespan(app_mock):
            pass
        mock_create_all.assert_called_once()
