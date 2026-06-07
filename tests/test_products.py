import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_and_get_product():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {"sku": "TESTSKU100", "name": "Prueba", "price": 3.5, "stock": 2}
        r = await ac.post("/api/products/", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data["sku"] == "TESTSKU100"
        pid = data["id"]

        r2 = await ac.get(f"/api/products/{pid}")
        assert r2.status_code == 200
        data2 = r2.json()
        assert data2["id"] == pid