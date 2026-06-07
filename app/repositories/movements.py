from app.db import get_db
from bson import ObjectId
from datetime import datetime

async def create_movement(payload: dict):
    db = get_db()
    if db is None:
        print(" Error: Base de datos no disponible")
        return {"error": "Database not available"}
    
    # Verificar stock si es movimiento de salida
    if payload["type"] == "out":
        try:
            product = await db.products.find_one({"_id": ObjectId(payload["product_id"])})
            if not product:
                return {"error": "product_not_found"}
            if product.get("stock", 0) < payload["qty"]:
                return {"error": "insufficient_stock"}
            
            # Actualizar stock del producto
            await db.products.update_one(
                {"_id": ObjectId(payload["product_id"])},
                {"$inc": {"stock": -payload["qty"]}}
            )
        except Exception as e:
            print(f" Error verificando stock: {e}")
            return {"error": str(e)}
    else:  
        try:
            # Actualizar stock 
            await db.products.update_one(
                {"_id": ObjectId(payload["product_id"])},
                {"$inc": {"stock": payload["qty"]}}
            )
        except Exception as e:
            print(f" Error actualizando stock: {e}")
            return {"error": str(e)}
    
    # Registrar movimiento
    payload["ts"] = datetime.utcnow()
    try:
        res = await db.movements.insert_one(payload)
        doc = await db.movements.find_one({"_id": res.inserted_id})
        return {
            "id": str(doc["_id"]),
            "product_id": doc["product_id"],
            "type": doc["type"],
            "qty": doc["qty"],
            "ts": doc["ts"].isoformat()
        }
    except Exception as e:
        print(f" Error registrando movimiento: {e}")
        return {"error": str(e)}

async def get_movements_by_product_and_date(product_id: str, start_date: str = None, end_date: str = None):
    db = get_db()
    if db is None:
        print(" Error: Base de datos no disponible")
        return {"items": []}
    
    query = {"product_id": product_id}
    
    # Filtrar por fechas si se proporcionan
    date_filter = {}
    if start_date:
        try:
            date_filter["$gte"] = datetime.fromisoformat(start_date)
        except ValueError:
            pass
    if end_date:
        try:
            date_filter["$lte"] = datetime.fromisoformat(end_date)
        except ValueError:
            pass
    
    if date_filter:
        query["ts"] = date_filter
    
    try:
        cursor = db.movements.find(query).sort("ts", -1)
        items = []
        async for doc in cursor:
            items.append({
                "id": str(doc["_id"]),
                "product_id": doc["product_id"],
                "type": doc["type"],
                "qty": doc["qty"],
                "ts": doc["ts"].isoformat()
            })
        return {"items": items}
    except Exception as e:
        print(f" Error obteniendo movimientos: {e}")
        return {"items": []}