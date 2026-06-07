from fastapi import APIRouter, HTTPException, Query
from app.models import MovementCreate
from app.repositories import movements as repo_movements

# ⚠️ IMPORTANTE: SIN prefix aquí
router = APIRouter()

@router.post("/")
async def create_movement(payload: MovementCreate):
    """Registrar un movimiento de stock (entrada/salida)"""
    result = await repo_movements.create_movement(payload.model_dump())
    
    if result.get("error") == "insufficient_stock":
        raise HTTPException(status_code=400, detail="Stock insuficiente")
    
    if result.get("error") == "product_not_found":
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return result

@router.get("/{product_id}")
async def get_movements_by_product(
    product_id: str,
    start_date: str = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    end_date: str = Query(None, description="Fecha fin (YYYY-MM-DD)")
):
    """Obtener movimientos de un producto (opcionalmente por rango de fechas)"""
    movements = await repo_movements.get_movements_by_product_and_date(
        product_id, start_date, end_date
    )
    return movements