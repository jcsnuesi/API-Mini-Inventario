import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_movements_stock_flow():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # crear producto
        prod = {"sku": "MOVTEST001", "name": "ProdMov", "price": 1.0, "stock": 10}
        r = await ac.post("/api/products/", json=prod)
        assert r.status_code == 200
        pid = r.json()["id"]

        # entrada
        r_in = await ac.post("/api/movements/", json={"product_id": pid, "type": "in", "qty": 5})
        assert r_in.status_code == 200
        assert r_in.json()["product"]["stock"] == 15

        # salida válida
        r_out = await ac.post("/api/movements/", json={"product_id": pid, "type": "out", "qty": 8})
        assert r_out.status_code == 200
        assert r_out.json()["product"]["stock"] == 7

        # salida insuficiente
        r_bad = await ac.post("/api/movements/", json={"product_id": pid, "type": "out", "qty": 1000})
        assert r_bad.status_code == 400