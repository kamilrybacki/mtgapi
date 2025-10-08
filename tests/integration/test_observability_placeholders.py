import pytest
from httpx import AsyncClient, ASGITransport

from mtgapi.entrypoint import API


@pytest.mark.asyncio
async def test_metrics_placeholder_returns_501() -> None:
    transport = ASGITransport(app=API)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/metrics")
    assert response.status_code == 501
    assert response.json()["detail"].startswith("metrics not implemented")


@pytest.mark.asyncio
async def test_tracing_placeholder_returns_501() -> None:
    transport = ASGITransport(app=API)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/_trace/test")
    assert response.status_code == 501
    assert response.json()["detail"].startswith("tracing not implemented")


@pytest.mark.asyncio
async def test_feature_flags_placeholder_returns_501_with_flags_key() -> None:
    transport = ASGITransport(app=API)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/feature-flags")
    assert response.status_code == 501
    body = response.json()
    assert body["detail"].startswith("feature flags not implemented")
    assert body["flags"] == {}
