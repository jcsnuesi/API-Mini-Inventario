from fastapi import APIRouter, HTTPException, Query, Depends
from app.models import ProductCreate, ProductUpdate
from app.repositories import products as repo_products
from app.deps import get_db

# ⚠️ IMPORTANTE: SIN prefix aquí
router = APIRouter()

@router.post("/")
async def create_product(payload: ProductCreate):
    """Crear un nuevo producto"""
    # Validar que SKU sea único
    existing = await repo_products.get_product_by_sku(payload.sku)
    if existing:
        raise HTTPException(status_code=400, detail="SKU ya existe")
    
    # Crear producto
    created = await repo_products.create_product(payload.model_dump())
    
    # Verificar error de duplicado (por si acaso)
    if created and created.get("error") == "duplicate_sku":
        raise HTTPException(status_code=400, detail="SKU ya existe")
    
    return created

@router.get("/")
async def list_products(
    name: str | None = Query(None, description="Filtrar por nombre"),
    category: str | None = Query(None, description="Filtrar por categoría"),
    skip: int = Query(0, ge=0, description="Paginación: elementos a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Paginación: límite de elementos"),
    price_min: float | None = Query(None, ge=0, description="Precio mínimo"),
    price_max: float | None = Query(None, ge=0, description="Precio máximo")
):
    """Listar productos con filtros y paginación"""
    # Construir filtros
    filters = {}
    
    if name:
        filters["name"] = {"$regex": name, "$options": "i"}  # Búsqueda case-insensitive
    
    if category:
        filters["category"] = category
    
    # Filtro por rango de precio
    if price_min is not None or price_max is not None:
        price_filter = {}
        if price_min is not None:
            price_filter["$gte"] = price_min
        if price_max is not None:
            price_filter["$lte"] = price_max
        filters["price"] = price_filter
    
    # Obtener productos
    result = await repo_products.list_products(
        filters=filters,
        skip=skip,
        limit=limit
    )
    
    return result

@router.get("/{product_id}")
async def get_product(product_id: str):
    """Obtener un producto por ID"""
    product = await repo_products.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return product

@router.patch("/{product_id}")
async def update_product(product_id: str, payload: ProductUpdate):
    """Actualizar un producto"""
    # Solo actualizar campos que no sean None
    update_data = payload.model_dump(exclude_none=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    updated = await repo_products.update_product(product_id, update_data)
    
    if not updated:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return updated

@router.delete("/{product_id}")
async def delete_product(product_id: str):
    """Eliminar un producto (solo si stock = 0)"""
    # Primero obtener el producto
    product = await repo_products.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Verificar que stock sea 0
    if product.get("stock", 0) != 0:
        raise HTTPException(
            status_code=400, 
            detail="No se puede eliminar producto con stock distinto de 0"
        )
    
    # Eliminar producto
    deleted = await repo_products.delete_product(product_id)
    
    if not deleted:
        raise HTTPException(status_code=500, detail="Error al eliminar producto")
    
    return {"deleted": True, "message": "Producto eliminado correctamente"}