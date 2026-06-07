from app.db import get_db
from bson import ObjectId
from datetime import datetime
from pymongo.errors import DuplicateKeyError

def _doc_to_out(doc):
    if not doc:
        return None
    return {
        "id": str(doc.get("_id")),
        "sku": doc.get("sku"),
        "name": doc.get("name"),
        "category": doc.get("category"),
        "price": float(doc.get("price")),
        "stock": int(doc.get("stock", 0)),
        "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
        "updated_at": doc.get("updated_at").isoformat() if doc.get("updated_at") else None,
    }

async def create_product(payload: dict):
    db = get_db()  # Obtener instancia actual de DB
    if db is None:
        print(" Error: Base de datos no disponible")
        return {"error": "Database not available"}
    
    payload["created_at"] = datetime.utcnow()
    payload["updated_at"] = datetime.utcnow()
    try:
        res = await db.products.insert_one(payload)
    except DuplicateKeyError:
        return {"error": "duplicate_sku"}
    except Exception as e:
        print(f" Error al insertar producto: {e}")
        return {"error": str(e)}
    
    doc = await db.products.find_one({"_id": res.inserted_id})
    return _doc_to_out(doc)

async def get_product_by_id(pid: str):
    db = get_db()
    if db is None:
        print(" Error: Base de datos no disponible")
        return None
    
    try:
        doc = await db.products.find_one({"_id": ObjectId(pid)})
        return _doc_to_out(doc)
    except Exception as e:
        print(f" Error al obtener producto por ID: {e}")
        return None

async def get_product_by_sku(sku: str):
    db = get_db()
    if db is None:
        print(" Error: Base de datos no disponible")
        return None
    
    try:
        doc = await db.products.find_one({"sku": sku})
        return _doc_to_out(doc)
    except Exception as e:
        print(f" Error al obtener producto por SKU: {e}")
        return None

async def list_products(filters: dict = None, skip: int = 0, limit: int = 10):
    db = get_db()
    if db is None:
        print(" Error: Base de datos no disponible")
        return {"total": 0, "items": []}
    
    q = filters or {}
    try:
        cursor = db.products.find(q).skip(skip).limit(limit)
        items = []
        async for d in cursor:
            items.append(_doc_to_out(d))
        total = await db.products.count_documents(q)
        return {"total": total, "items": items}
    except Exception as e:
        print(f" Error al listar productos: {e}")
        return {"total": 0, "items": []}

async def update_product(pid: str, patch: dict):
    db = get_db()
    if db is None:
        print(" Error: Base de datos no disponible")
        return None
    
    patch["updated_at"] = datetime.utcnow()
    try:
        await db.products.update_one({"_id": ObjectId(pid)}, {"$set": patch})
        doc = await db.products.find_one({"_id": ObjectId(pid)})
        return _doc_to_out(doc)
    except Exception as e:
        print(f" Error al actualizar producto: {e}")
        return None

async def delete_product(pid: str):
    db = get_db()
    if db is None:
        print(" Error: Base de datos no disponible")
        return False
    
    try:
        res = await db.products.delete_one({"_id": ObjectId(pid)})
        return res.deleted_count == 1
    except Exception as e:
        print(f" Error al eliminar producto: {e}")
        return False